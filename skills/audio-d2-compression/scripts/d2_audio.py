#!/usr/bin/env python3
"""
D2 Audio Compression
====================
A custom audio codec based on peak extraction and Cubic Bézier reconstruction.
Original research by Adrian Mallett (2021).

The D2 format represents audio as two compact arrays:
  - peaks: amplitude at each local peak
  - tbs  : number of samples between successive peaks ("time between samples")

Reconstruction interpolates between peaks using Cubic Bézier curves,
producing a smooth waveform close to the original.
"""

import numpy as np
import os
from pathlib import Path


# ---------------------------------------------------------------------------
# Compression
# ---------------------------------------------------------------------------

def audio_to_d2(samples: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Convert a 1-D array of audio samples to D2 peak + timing arrays.

    Parameters
    ----------
    samples : np.ndarray  (int16 or float)
        Mono audio samples.

    Returns
    -------
    peaks : np.ndarray  (int32)   – amplitude at each local extremum
    tbs   : np.ndarray  (uint16)  – samples between successive peaks
    """
    peaks, tbs = [], []
    last_val = 0
    cur_val  = 0
    rising   = False
    falling  = False
    last_peak_pos = 0
    pos = 0

    for sample in samples:
        last_val = cur_val
        cur_val  = int(sample)
        pos     += 1

        if cur_val > last_val:
            rising  = True
        elif cur_val < last_val:
            falling = True

        if rising and falling:           # direction change → peak detected
            peaks.append(last_val)
            tbs.append(pos - last_peak_pos)
            last_peak_pos = pos
            rising  = False
            falling = False

    return np.array(peaks, dtype=np.int32), np.array(tbs, dtype=np.uint16)


# ---------------------------------------------------------------------------
# Decompression
# ---------------------------------------------------------------------------

def _bezier(p0: float, p3: float, n: int) -> np.ndarray:
    """
    Interpolate n points between p0 and p3 using a Cubic Bézier curve.
    Control points are placed to produce a smooth S-curve.
    """
    if n <= 0:
        return np.array([], dtype=np.float32)
    mid = (p0 + p3) / 2.0
    P0 = np.array([0.0, p0])
    P1 = np.array([mid, p0])
    P2 = np.array([mid, p3])
    P3 = np.array([1.0, p3])
    t  = np.linspace(0.0, 1.0, n)
    curve = (
        ((1 - t) ** 3)[:, None] * P0 +
        (3 * (1 - t) ** 2 * t)[:, None] * P1 +
        (3 * (1 - t) * t ** 2)[:, None] * P2 +
        (t ** 3)[:, None] * P3
    )
    return curve[:, 1].astype(np.float32)


def d2_to_audio(peaks: np.ndarray, tbs: np.ndarray) -> np.ndarray:
    """
    Reconstruct audio samples from D2 peak + timing arrays.

    Parameters
    ----------
    peaks : np.ndarray  – peak amplitudes
    tbs   : np.ndarray  – samples between peaks

    Returns
    -------
    np.ndarray (float32) – reconstructed audio samples
    """
    segments = []
    prev = 0.0
    for peak, n in zip(peaks, tbs):
        segments.append(_bezier(prev, float(peak), int(n)))
        prev = float(peak)
    return np.concatenate(segments) if segments else np.array([], dtype=np.float32)


# ---------------------------------------------------------------------------
# File-level helpers
# ---------------------------------------------------------------------------

def compress_file(input_path: str, output_path: str | None = None,
                  sample_rate: int = 44100) -> str:
    """
    Compress an audio file to D2 format (.d2.npz).

    Parameters
    ----------
    input_path  : path to any pydub-readable audio file
    output_path : destination .d2.npz file (default: same dir, same stem)
    sample_rate : target sample rate (default 44 100 Hz)

    Returns
    -------
    str – path of the written .d2.npz file
    """
    from pydub import AudioSegment

    audio = (AudioSegment.from_file(input_path)
             .set_channels(1)
             .set_frame_rate(sample_rate))
    samples = np.array(audio.get_array_of_samples(), dtype=np.int32)

    peaks, tbs = audio_to_d2(samples)

    if output_path is None:
        stem = Path(input_path).stem
        output_path = str(Path(input_path).parent / f"{stem}.d2.npz")

    np.savez_compressed(output_path, peaks=peaks, tbs=tbs,
                        sample_rate=np.array(sample_rate),
                        original_length=np.array(len(samples)))

    ratio = os.path.getsize(output_path) / os.path.getsize(input_path) * 100
    print(f"Compressed  : {input_path}")
    print(f"Output      : {output_path}")
    print(f"Peaks stored: {len(peaks):,}")
    print(f"Size ratio  : {ratio:.1f}% of original")
    return output_path


def decompress_file(d2_path: str, output_path: str | None = None) -> str:
    """
    Reconstruct a WAV file from a .d2.npz file.

    Parameters
    ----------
    d2_path     : path to a .d2.npz file produced by compress_file()
    output_path : destination WAV file (default: same dir, stem without .d2)

    Returns
    -------
    str – path of the written WAV file
    """
    import wave, struct

    data = np.load(d2_path)
    peaks       = data["peaks"]
    tbs         = data["tbs"]
    sample_rate = int(data["sample_rate"])

    audio = d2_to_audio(peaks, tbs)

    # Normalise to int16 range
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = (audio / max_val * 32767).astype(np.int16)
    else:
        audio = audio.astype(np.int16)

    if output_path is None:
        stem = Path(d2_path).stem
        if stem.endswith(".d2"):
            stem = stem[:-3]
        output_path = str(Path(d2_path).parent / f"{stem}_restored.wav")

    with wave.open(output_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)          # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())

    print(f"Decompressed: {d2_path}")
    print(f"Output      : {output_path}")
    print(f"Samples     : {len(audio):,}")
    return output_path


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage:")
        print("  compress   : python d2_audio.py compress  <input_audio> [output.d2.npz]")
        print("  decompress : python d2_audio.py decompress <input.d2.npz> [output.wav]")
        sys.exit(1)

    mode = sys.argv[1].lower()
    src  = sys.argv[2]
    dst  = sys.argv[3] if len(sys.argv) > 3 else None

    if mode == "compress":
        compress_file(src, dst)
    elif mode == "decompress":
        decompress_file(src, dst)
    else:
        print(f"Unknown mode '{mode}'. Use 'compress' or 'decompress'.")
        sys.exit(1)
