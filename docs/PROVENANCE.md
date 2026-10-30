# Provenance

Every audio file in this package is the deterministic output of a recipe in `src/reel_sfx/generators.py`, run with
the seed recorded in `sounds.json`. A recipe uses only:

- oscillators (sines, glides, harmonic stacks, textbook bell partial ratios),
- random noise shaped with FFT filters,
- envelopes, fades, soft clipping and stereo decorrelation written in `src/reel_sfx/synth.py`.

**No recording, sample, preset, impulse response or analysis of any existing sound** went into a recipe. This
covers spectra, envelopes and fitted parameters taken from a reference. The recipes were not tuned by A/B-ing
against third-party sound effects either.

How this is enforced:

- `tests/test_reproducible.py` re-renders every sound and compares it with the bundled WAV, so the files in the
  repo are exactly what the code makes.
- `tests/test_sounds.py` checks that every entry carries `license: CC0-1.0`, the provenance statement, its
  generator and seed, and the file's SHA-256, and that no other file sits in the sounds folder.
- CONTRIBUTING.md sets the same rule for new sounds.

## What is deliberately *not* in this repository

This package was split out of a private video-editing project. That project also holds a separate sound library
whose sounds were made by **analysis-resynthesis of third-party reference recordings**: envelopes, modal fits and
spectral surfaces measured from the reference audio. Those sounds, the reference material and the comparison
files are **excluded**. Being synthesised in code does not make a sound free of the rights of the recording it was
modelled on, so none of that material, and none of the parameters derived from it, is used here.

The sounds that share names with common effects ("whoosh", "riser", "sub drop", "censor bleep", "heartbeat")
are generic categories. Their recipes were written fresh for this package.
