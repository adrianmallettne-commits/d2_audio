---
name: "audio-d2-compression"
description: "Compress audio files to the D2 format (peak + timing arrays) and restore them back to WAV. Use when asked to compress, encode, or restore audio files using the D2 method. Original research by Adrian Mallett (2021)."
version: "1.0.0"
author: "Adrian Mallett (research) / Agent Zero (implementation)"
tags: ["audio", "compression", "codec", "D2", "music", "wav", "numpy"]
trigger_patterns:
  - "compress audio"
  - "D2 audio"
  - "audio compression"
  - "compress music"
  - "decompress audio"
  - "restore audio"
  - "D2 format"
  - "d2 compress"
  - "d2 decompress"
  - "audio codec"
  - "voice authentication"
  - "voice recognition"
  - "enrol voice"
  - "enroll voice"
  - "authenticate voice"
  - "voice profile"
  - "voice biometric"
  - "voice login"
  - "speaker recognition"
  - "voice fingerprint"
---

# D2 Audio Compression Skill

This skill compresses audio files using the **D2 format** — a custom codec that represents
audio as two compact arrays (peak amplitudes + time between peaks) and reconstructs the
waveform via Cubic Bézier interpolation.

> *Original research by Adrian Mallett (2021). The method independently parallels
> professional sinusoidal modelling codecs, arriving at the concept through a geometric,
> intuitive route.*

---

## How It Works

1. **Compression** — scan audio samples, record each local peak amplitude and the number of
   samples since the previous peak. Store as a compact `.d2.npz` file.
2. **Decompression** — read peaks and timing arrays; interpolate between each pair of peaks
   using a smooth Cubic Bézier curve; write the result as a 16-bit mono WAV.

---

## Script Location

```
/a0/usr/skills/audio-d2-compression/scripts/d2_audio.py
```

---

## Usage Instructions

### 1. Compress an audio file

Use `code_execution_tool` with `runtime=python`:

```python
import sys
sys.path.insert(0, "/a0/usr/skills/audio-d2-compression/scripts")
from d2_audio import compress_file

output = compress_file(
    input_path="/path/to/input.wav",   # any pydub-readable format
    output_path="/path/to/output.d2.npz",  # optional, auto-named if omitted
    sample_rate=44100                   # optional, default 44100 Hz
)
print("Saved to:", output)
```

### 2. Decompress a D2 file back to WAV

```python
import sys
sys.path.insert(0, "/a0/usr/skills/audio-d2-compression/scripts")
from d2_audio import decompress_file

output = decompress_file(
    d2_path="/path/to/file.d2.npz",
    output_path="/path/to/restored.wav"  # optional, auto-named if omitted
)
print("Restored to:", output)
```

### 3. Command-line (terminal)

```bash
# Compress
python /a0/usr/skills/audio-d2-compression/scripts/d2_audio.py compress input.wav

# Decompress
python /a0/usr/skills/audio-d2-compression/scripts/d2_audio.py decompress input.d2.npz
```

---

## Dependencies

Ensure these are installed before running:

```bash
pip install pydub numpy
apt-get install -y ffmpeg   # needed by pydub for MP3/AAC etc.
```

---

## Output Format

| File | Description |
|---|---|
| `*.d2.npz` | Compressed D2 archive (peaks, tbs, sample_rate, original_length) |
| `*_restored.wav` | Reconstructed mono 16-bit WAV |

---

## Notes

- The codec currently operates on **mono audio**. Stereo files are auto-converted to mono.
- Reconstruction is **near-lossless in length** but Bézier smoothing alters dynamics.
- This is a research-grade codec, not optimised for production throughput on very large files.
- For best fidelity use `sample_rate=44100`; lower rates compress faster.

---

## Voice Authentication

The `d2_voice_auth.py` script uses D2 fingerprinting for speaker recognition.
Each person's voice produces a unique statistical pattern of peak amplitudes and
timing — stored as a compact JSON profile file.

**Script:** `/a0/usr/skills/audio-d2-compression/scripts/d2_voice_auth.py`

**Default profile directory:** `/a0/usr/voice_profiles/`

### 1. Enrol a speaker

```python
import sys
sys.path.insert(0, "/a0/usr/skills/audio-d2-compression/scripts")
from d2_voice_auth import enrol_voice

enrol_voice(
    audio_path="/path/to/voice_sample.wav",
    profile_name="adrian",
    profile_dir="/a0/usr/voice_profiles",
    notes="Enrolled 2026"
)
```

### 2. Authenticate a speaker

```python
from d2_voice_auth import authenticate_voice

result = authenticate_voice(
    audio_path="/path/to/test_sample.wav",
    profile_name="adrian",
    threshold=0.35
)
print(result)
# {'authenticated': True, 'confidence': 82.5, 'distance': 0.1225, ...}
```

### 3. Compare two voices directly

```python
from d2_voice_auth import compare_voices

result = compare_voices("/path/to/voice_a.wav", "/path/to/voice_b.wav")
print(result)  # {'distance': 0.08, 'similarity': 92.0}
```

### 4. List enrolled profiles

```python
from d2_voice_auth import list_profiles
print(list_profiles("/a0/usr/voice_profiles"))
```

### Voice Fingerprint Features

| Feature | What it encodes |
|---|---|
| Peak mean / std | Overall vocal energy and variability |
| Peak p10 / p90 | Quiet and loud range of the voice |
| TBS mean / std | Speech rhythm and cadence |
| TBS p10 / p90 | Fastest and slowest speaking intervals |
| Ratio | Energy-to-rate fingerprint |
| Peak sign ratio | Voice register (proportion positive/negative peaks) |

### Threshold Guide

| Threshold | Behaviour |
|---|---|
| `0.20` | Very strict — may reject same speaker across sessions |
| `0.35` | Balanced default — recommended starting point |
| `0.50` | Lenient — better for noisy environments |

### CLI Usage

```bash
# Enrol
python d2_voice_auth.py enrol   voice.wav adrian
# Authenticate
python d2_voice_auth.py auth    voice.wav adrian
# Compare two recordings
python d2_voice_auth.py compare voice_a.wav voice_b.wav
# List profiles
python d2_voice_auth.py list
```
