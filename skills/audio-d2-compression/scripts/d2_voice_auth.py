#!/usr/bin/env python3
"""
D2 Voice Authentication
=======================
Voice biometric authentication built on the D2 audio representation.
Original D2 research by Adrian Mallett (2021).

Each person's voice produces a statistically unique pattern of peak
amplitudes and inter-peak timing in the D2 format. This module builds
a compact statistical fingerprint from a voice sample and matches it
against stored profiles.

Workflow
--------
  Enrolment   : record passphrase → compress to D2 → build + save profile
  Authenticate : record passphrase → compress to D2 → compare to profile → score
"""

import json
import numpy as np
from pathlib import Path
from typing import Optional

# local import
import sys
sys.path.insert(0, str(Path(__file__).parent))
from d2_audio import audio_to_d2


# ---------------------------------------------------------------------------
# Statistical fingerprinting
# ---------------------------------------------------------------------------

def _d2_fingerprint(peaks: np.ndarray, tbs: np.ndarray) -> dict:
    """
    Derive a compact statistical fingerprint from D2 arrays.

    Features captured
    -----------------
    - peaks : mean, std, median, p10, p90  (amplitude envelope shape)
    - tbs   : mean, std, median, p10, p90  (rhythm / cadence)
    - ratio : mean(|peaks|) / mean(tbs)    (energy-rate fingerprint)
    - peak_sign_ratio : fraction of positive peaks (voice register)
    """
    p = peaks.astype(np.float64)
    t = tbs.astype(np.float64)

    def stats(arr: np.ndarray) -> dict:
        return {
            "mean":   float(np.mean(arr)),
            "std":    float(np.std(arr)),
            "median": float(np.median(arr)),
            "p10":    float(np.percentile(arr, 10)),
            "p90":    float(np.percentile(arr, 90)),
        }

    fp = {
        "peaks":           stats(p),
        "tbs":             stats(t),
        "ratio":           float(np.mean(np.abs(p)) / (np.mean(t) + 1e-9)),
        "peak_sign_ratio": float(np.mean(p > 0)),
        "n_peaks":         int(len(p)),
    }
    return fp


def _fingerprint_distance(fp_a: dict, fp_b: dict) -> float:
    """
    Compute a normalised distance score (0 = identical, higher = more different)
    between two fingerprints by comparing each statistical feature.
    """
    feature_keys = [
        ("peaks", "mean"),
        ("peaks", "std"),
        ("peaks", "median"),
        ("peaks", "p10"),
        ("peaks", "p90"),
        ("tbs",   "mean"),
        ("tbs",   "std"),
        ("tbs",   "median"),
        ("tbs",   "p10"),
        ("tbs",   "p90"),
    ]
    scalar_keys = ["ratio", "peak_sign_ratio"]

    distances = []

    for group, key in feature_keys:
        a = fp_a[group][key]
        b = fp_b[group][key]
        denom = (abs(a) + abs(b)) / 2.0 + 1e-9
        distances.append(abs(a - b) / denom)

    for key in scalar_keys:
        a = fp_a[key]
        b = fp_b[key]
        denom = (abs(a) + abs(b)) / 2.0 + 1e-9
        distances.append(abs(a - b) / denom)

    return float(np.mean(distances))


# ---------------------------------------------------------------------------
# Profile storage
# ---------------------------------------------------------------------------

def _profile_path(profile_name: str, profile_dir: str) -> Path:
    Path(profile_dir).mkdir(parents=True, exist_ok=True)
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in profile_name)
    return Path(profile_dir) / f"{safe_name}.voice.json"


def save_profile(profile_name: str, fingerprint: dict, profile_dir: str,
                 notes: str = "") -> str:
    """Persist a voice fingerprint to disk as a JSON file."""
    path = _profile_path(profile_name, profile_dir)
    record = {
        "name":        profile_name,
        "notes":       notes,
        "fingerprint": fingerprint,
    }
    with open(path, "w") as f:
        json.dump(record, f, indent=2)
    return str(path)


def load_profile(profile_name: str, profile_dir: str) -> dict:
    """Load a stored voice fingerprint. Raises FileNotFoundError if missing."""
    path = _profile_path(profile_name, profile_dir)
    if not path.exists():
        raise FileNotFoundError(
            f"No voice profile found for '{profile_name}' in {profile_dir}")
    with open(path) as f:
        return json.load(f)


def list_profiles(profile_dir: str) -> list[str]:
    """Return names of all stored voice profiles in a directory."""
    p = Path(profile_dir)
    if not p.exists():
        return []
    return [f.stem.replace(".voice", "")
            for f in sorted(p.glob("*.voice.json"))]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def enrol_voice(
    audio_path: str,
    profile_name: str,
    profile_dir: str = "/a0/usr/voice_profiles",
    sample_rate: int = 16000,
    notes: str = "",
) -> str:
    """
    Enrol a speaker from an audio file.

    Parameters
    ----------
    audio_path   : path to any pydub-readable audio file (WAV, MP3, …)
    profile_name : unique name for this speaker (e.g. "adrian")
    profile_dir  : directory to store voice profiles
    sample_rate  : sample rate for D2 conversion (16 kHz is fine for voice)
    notes        : optional metadata string stored alongside the profile

    Returns
    -------
    str – path of the saved profile JSON file
    """
    from pydub import AudioSegment

    audio = (AudioSegment.from_file(audio_path)
             .set_channels(1)
             .set_frame_rate(sample_rate))
    samples = np.array(audio.get_array_of_samples(), dtype=np.int32)

    peaks, tbs = audio_to_d2(samples)
    fp = _d2_fingerprint(peaks, tbs)

    path = save_profile(profile_name, fp, profile_dir, notes)

    print(f"✓ Enrolled : '{profile_name}'")
    print(f"  Profile  : {path}")
    print(f"  Peaks    : {fp['n_peaks']:,}")
    print(f"  Peak mean: {fp['peaks']['mean']:.1f}  std: {fp['peaks']['std']:.1f}")
    print(f"  TBS mean : {fp['tbs']['mean']:.1f}  std: {fp['tbs']['std']:.1f}")
    return path


def authenticate_voice(
    audio_path: str,
    profile_name: str,
    profile_dir: str = "/a0/usr/voice_profiles",
    sample_rate: int = 16000,
    threshold: float = 0.35,
) -> dict:
    """
    Authenticate a voice sample against a stored profile.

    Parameters
    ----------
    audio_path   : path to the voice sample to test
    profile_name : name of the stored profile to match against
    profile_dir  : directory containing voice profiles
    sample_rate  : must match the rate used during enrolment
    threshold    : distance below which the speaker is accepted (default 0.35)
                   lower = stricter.  Tune based on your environment.

    Returns
    -------
    dict with keys:
        authenticated : bool   – True if distance < threshold
        confidence    : float  – 0–100 %, higher = more confident match
        distance      : float  – raw normalised distance (lower = closer)
        threshold     : float  – threshold used
        profile       : str    – profile name tested against
    """
    from pydub import AudioSegment

    record = load_profile(profile_name, profile_dir)
    stored_fp = record["fingerprint"]

    audio = (AudioSegment.from_file(audio_path)
             .set_channels(1)
             .set_frame_rate(sample_rate))
    samples = np.array(audio.get_array_of_samples(), dtype=np.int32)

    peaks, tbs = audio_to_d2(samples)
    live_fp = _d2_fingerprint(peaks, tbs)

    dist = _fingerprint_distance(stored_fp, live_fp)

    # Map distance to a 0-100 confidence score
    # distance=0 → 100%, distance=threshold → 50%, beyond threshold → <50%
    confidence = max(0.0, 100.0 * (1.0 - dist / (threshold * 2)))

    authenticated = dist < threshold

    result = {
        "authenticated": authenticated,
        "confidence":    round(confidence, 1),
        "distance":      round(dist, 4),
        "threshold":     threshold,
        "profile":       profile_name,
    }

    status = "✓ AUTHENTICATED" if authenticated else "✗ REJECTED"
    print(f"{status} — profile: '{profile_name}'")
    print(f"  Distance   : {dist:.4f}  (threshold: {threshold})")
    print(f"  Confidence : {confidence:.1f}%")
    return result


def compare_voices(
    audio_path_a: str,
    audio_path_b: str,
    sample_rate: int = 16000,
) -> dict:
    """
    Compare two voice recordings directly (no stored profile needed).
    Useful for testing or building a verification pipeline.

    Returns
    -------
    dict with distance and a rough similarity percentage
    """
    from pydub import AudioSegment

    def load(path):
        audio = (AudioSegment.from_file(path)
                 .set_channels(1)
                 .set_frame_rate(sample_rate))
        samples = np.array(audio.get_array_of_samples(), dtype=np.int32)
        peaks, tbs = audio_to_d2(samples)
        return _d2_fingerprint(peaks, tbs)

    fp_a = load(audio_path_a)
    fp_b = load(audio_path_b)
    dist = _fingerprint_distance(fp_a, fp_b)
    similarity = max(0.0, 100.0 * (1.0 - dist))

    print(f"Distance   : {dist:.4f}")
    print(f"Similarity : {similarity:.1f}%")
    return {"distance": round(dist, 4), "similarity": round(similarity, 1)}


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    def usage():
        print("Usage:")
        print("  enrol        : python d2_voice_auth.py enrol    <audio> <name> [profile_dir]")
        print("  authenticate : python d2_voice_auth.py auth     <audio> <name> [profile_dir] [threshold]")
        print("  compare      : python d2_voice_auth.py compare  <audio_a> <audio_b>")
        print("  list         : python d2_voice_auth.py list     [profile_dir]")
        sys.exit(1)

    if len(sys.argv) < 2:
        usage()

    mode = sys.argv[1].lower()
    DEFAULT_DIR = "/a0/usr/voice_profiles"

    if mode == "enrol" and len(sys.argv) >= 4:
        enrol_voice(sys.argv[2], sys.argv[3],
                    sys.argv[4] if len(sys.argv) > 4 else DEFAULT_DIR)

    elif mode == "auth" and len(sys.argv) >= 4:
        thresh = float(sys.argv[5]) if len(sys.argv) > 5 else 0.35
        result = authenticate_voice(
            sys.argv[2], sys.argv[3],
            sys.argv[4] if len(sys.argv) > 4 else DEFAULT_DIR,
            threshold=thresh)
        sys.exit(0 if result["authenticated"] else 1)

    elif mode == "compare" and len(sys.argv) >= 4:
        compare_voices(sys.argv[2], sys.argv[3])

    elif mode == "list":
        d = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DIR
        profiles = list_profiles(d)
        if profiles:
            print(f"Voice profiles in {d}:")
            for name in profiles:
                print(f"  - {name}")
        else:
            print(f"No profiles found in {d}")
    else:
        usage()
