# D2 Audio — Agent Zero Plugin

> **Original research by Adrian Mallett (2021)**

A unique audio codec and voice authentication plugin for [Agent Zero](https://github.com/agent0ai/agent-zero), based on peak extraction and Cubic Bézier reconstruction.

---

## What is D2 Audio?

Instead of storing every audio sample, the D2 format stores only the **peaks** (amplitude at each local extremum) and **timing** (samples between peaks). The original waveform is reconstructed by interpolating between peaks using smooth Cubic Bézier curves.

This representation is:
- **Compact** — far fewer data points than raw audio
- **Invertible** — reconstruct audio near-losslessly
- **Meaningful** — peaks and timing map directly to perceptually relevant features

---

## Features

### 🎵 Audio Compression
- Compress any audio file (WAV, MP3, AAC, …) to a compact `.d2.npz` archive
- Reconstruct back to WAV with near-original length fidelity
- Compression ratio reporting on every encode

### 🎤 Voice Authentication
- Enrol speakers from audio samples
- Authenticate speakers via compact statistical fingerprinting
- Compare two voice recordings directly for similarity scoring
- Adjustable sensitivity threshold
- Profiles stored as human-readable JSON

---

## Installation

1. Install the plugin via the Agent Zero Plugin Hub
2. Click **Execute** in the Plugins UI to install dependencies (`pydub`, `numpy`, `ffmpeg`)

---

## Usage (via Agent Zero)

Simply ask the agent using natural language:

- _"Compress this audio file using D2"_
- _"Decompress this D2 file back to WAV"_
- _"Enrol my voice as 'adrian'"_
- _"Authenticate this voice recording against the 'adrian' profile"_
- _"Compare these two voice recordings"_

---

## Technical Background

The D2 method was originally developed as part of research into a compact audio representation suitable for training AI models to perform audio upscaling and restoration — making vintage recordings (e.g. from the 1940s) sound as if they were produced with modern technology.

The research independently parallels sinusoidal modelling techniques used in professional audio codecs, but arrives at the concept through a more geometric, intuitive route using Bézier curves for reconstruction.

The voice authentication component extends the D2 representation into biometrics: every person's voice produces a statistically unique peak/timing pattern that serves as a compact voiceprint.

---

## Files

```
d2_audio/
├── plugin.yaml
├── execute.py               ← install dependencies
├── README.md
├── LICENSE
└── skills/
    └── audio-d2-compression/
        ├── SKILL.md         ← agent instructions + triggers
        └── scripts/
            ├── d2_audio.py         ← compression / decompression
            └── d2_voice_auth.py    ← voice authentication
```

---

## License

MIT — see [LICENSE](LICENSE)

---

## Author

**Adrian Mallett** — original D2 research (2021)
