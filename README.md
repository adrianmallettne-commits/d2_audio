# 🎵 D2 Audio — Agent Zero Plugin

> **A unique audio codec and voice authentication system for [Agent Zero](https://github.com/agent0ai/agent-zero).**
> Compress audio. Restore it. Recognise the speaker. All locally, no cloud, no ML models.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Agent Zero Plugin](https://img.shields.io/badge/Agent%20Zero-Plugin-blue)](https://github.com/agent0ai/agent-zero)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Research](https://img.shields.io/badge/research-2021-orange)](#the-story-behind-d2)

---

## ✨ What makes this different

| | Traditional audio codecs | D2 Audio |
|---|---|---|
| Approach | Frequency-domain (MFCCs, FFTs) | **Time-domain** (peaks + timing) |
| Storage | Raw samples or spectrograms | **Two compact arrays** |
| Voice auth | Cloud API or heavy ML models | **Tiny JSON profiles, local only** |
| Dependencies | Often GPU, models, cloud services | **Just numpy + pydub** |
| Interpretability | Opaque neural features | **Physically meaningful peaks** |

---

## 🚀 Quick Start

### Install via Agent Zero Plugin Hub

1. Open Agent Zero
2. Go to **Plugins → Browse**
3. Find **D2 Audio**, click **Install**
4. Click **Execute** to install dependencies

### Try it in 30 seconds

Just ask Agent Zero in natural language:

```
"Compress this song.mp3 using D2"
"Decompress that .d2.npz file back to WAV"
"Enrol my voice as 'adrian' from this recording"
"Authenticate this new recording against the 'adrian' profile"
"Compare these two voice recordings for similarity"
```

---

## 🎯 What You Can Build With It

### 🔐 Privacy-First Voice Authentication
Add voice-based 2FA to local scripts, home automation, or personal AI assistants — **no cloud services, no data sent anywhere**. Profiles are tiny JSON files you own.

### 📦 Compact Audio Archiving
Store music or podcasts in a fraction of the original size. Reconstruct losslessly in length when needed.

### 🤖 AI Training Features
Feed D2 peak/timing arrays into ML models as a compact, perceptually-meaningful feature representation. Originally designed for audio restoration research.

### 🎨 Creative Audio Tools
Manipulate the D2 peak structure directly — morph between songs, create glitch effects, or compose music at the peak level.

### 🎙️ Speaker Verification
Build voice-locked AI agents that only respond to their owner's voice.

---

## 🧠 How It Works

### Compression

Instead of storing every audio sample, D2 scans the waveform and records only:

- **Peak amplitudes** — the value at each local extremum (direction change)
- **Inter-peak timing** — how many samples between successive peaks

These two arrays capture the *shape* of sound in a radically compact form.

### Reconstruction

The original waveform is rebuilt by interpolating between peaks using **Cubic Bézier curves** — producing smooth, natural audio that preserves the rhythm and dynamics of the original.

### Voice Authentication

Each person's voice produces a statistically unique D2 fingerprint:

| Feature | What it captures |
|---|---|
| Peak mean / std | Overall vocal energy and variability |
| Peak percentiles | Quiet and loud range |
| TBS mean / std | Speech rhythm and cadence |
| TBS percentiles | Fastest and slowest articulation intervals |
| Energy ratio | Combined energy-to-rate fingerprint |
| Peak sign ratio | Voice register balance |

Twelve numbers. Unique to you.

---

## 📖 Example: Full Workflow

```python
import sys
sys.path.insert(0, "/a0/usr/skills/audio-d2-compression/scripts")

# 1. Compress audio
from d2_audio import compress_file, decompress_file
compress_file("my_song.wav", "my_song.d2.npz")

# 2. Restore it later
decompress_file("my_song.d2.npz", "restored.wav")

# 3. Enrol a voice
from d2_voice_auth import enrol_voice, authenticate_voice
enrol_voice("adrian_sample.wav", "adrian")

# 4. Authenticate a new recording
result = authenticate_voice("login_attempt.wav", "adrian")
# {'authenticated': True, 'confidence': 87.3, 'distance': 0.14, ...}
```

---

## 📚 The Story Behind D2

This plugin comes from research I began in 2021 — a personal project to find a way of representing audio that was **compact, invertible, and meaningful** enough to be used as input to AI models.

The long-term vision was ambitious: train a model on modern high-fidelity recordings, then apply the learned "style" to vintage recordings — making a 1940s jazz track sound as if it had been produced today.

I didn't get to finish that vision. A **stroke** interrupted the work, and my focus since has been on recovery — including learning to walk again.

When I recently shared the original notebook with an AI agent (Agent Zero), what started as a conversation about old research turned into something I hadn't expected: **a fully working, published community plugin** built together in a single afternoon.

I'm sharing it now in the hope that creative people will take it further than I could. The ideas in here — peak-based audio encoding, time-domain voice fingerprinting, Bézier reconstruction — were never about any one application. They're **primitives**, and I'm genuinely curious what others will build with them.

— *Adrian Mallett*

---

## 🛠️ Technical Details

### Project Structure

```
d2_audio/
├── plugin.yaml              ← Agent Zero plugin manifest
├── execute.py               ← Dependency installer
├── README.md                ← This file
├── LICENSE                  ← MIT
└── skills/
    └── audio-d2-compression/
        ├── SKILL.md         ← Agent instructions + triggers
        └── scripts/
            ├── d2_audio.py         ← Compression / decompression
            └── d2_voice_auth.py    ← Voice authentication
```

### Dependencies

- Python 3.10+
- `numpy` — array operations
- `pydub` — audio I/O
- `ffmpeg` — MP3/AAC support (system package)

All installed automatically when you click **Execute** in the Plugin Hub.

### Threshold Tuning (Voice Auth)

| Threshold | Behaviour |
|---|---|
| `0.20` | Very strict — may reject the same speaker across sessions |
| `0.35` | **Balanced default — recommended** |
| `0.50` | Lenient — better for noisy environments |

---

## 🤝 Contributing

Ideas, improvements, and creative applications are very welcome. Some directions I'd love to see explored:

- Stereo support (current version is mono-only)
- Variable-precision peak encoding for better compression ratios
- Integration with Whisper or other STT models for speaker-conditioned transcription
- Web demo / visualisation of the D2 representation
- ML experiments using D2 as a feature representation

Open an issue or PR — I read everything, even if I'm slow to reply.

---

## 📜 License

MIT — free to use, modify, and distribute. See [LICENSE](LICENSE).

---

## 🔗 Links

- **Agent Zero:** https://github.com/agent0ai/agent-zero
- **Plugin Index:** https://github.com/agent0ai/a0-plugins
- **This plugin:** https://github.com/adrianmallettne-commits/d2_audio

---

*If this plugin is useful to you, a GitHub ⭐ helps others discover it. Thank you.* 🙏
