# Changelog

## 0.1.0 (first release)

- 19 original procedural sounds (CC0), 48 kHz / 24-bit stereo:
  - whoosh: soft, air, swipe
  - riser: noise, tonal, reverse swell
  - impact: sub, boom, sub drop, heartbeat
  - pop: short pop, blip, bloop
  - click: UI click, clock tick, wooden tock
  - bell ding, 1 kHz censor bleep, pulsing sub drone
- Python API:
  - `list_sounds`, `info`, `path`, `load`, `anchor`;
  - `render` (seeded variations and parameters);
  - `place` (anchor- and frame-accurate cue placement), `duck`, `mix`;
  - `read_wav` / `write_wav` (standard library).
- CLI `reel-sfx`: `list`, `info`, `path`, `export`, `render`, `place`.
- Tests:
  - format, levels, clipping, DC, mono-compatibility;
  - metadata, licence and provenance, SHA-256;
  - bit-reproducibility of every WAV from its recipe;
  - API and CLI.
- CI on Linux, macOS and Windows (Python 3.9 / 3.12), plus a wheel-content check.
