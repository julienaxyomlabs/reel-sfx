# Contributing

Issues and pull requests are welcome: new sounds, better recipes, API ideas and docs.

## The one rule for sounds

**A sound is code.** Add a recipe to `src/reel_sfx/generators.py` that builds the sound from oscillators, noise
and envelopes. Do **not** add or derive from:

- recordings, samples, sample packs or presets, whatever their licence;
- spectra, envelopes or parameters measured from an existing sound;
- recipes tuned by A/B comparison against a specific third-party effect.

This is what lets every WAV in the repo be dedicated to the public domain (CC0). By opening a pull request, you
agree that your code is MIT-licensed and that the audio your recipe renders is dedicated under CC0 1.0.

## Adding a sound

1. Write a function decorated with `@recipe(...)`: an id like `category.name`, a title, a category, an anchor
   (`onset`, `peak` or `end`), tags, a one-line use, a suggested gain and a seed. It returns
   `(stereo_array, anchor_seconds)`. Keep the peak at −1 dBFS with `normalize()`, and keep it mono-compatible:
   `stereo()` does that.
2. Rebuild the files and the table:
   ```bash
   python -m reel_sfx.build            # (from src/, or after pip install -e .)
   python tools/make_sounds_table.py
   ```
3. Run the tests: `pip install -e ".[test]" && pytest`.

## Development

```bash
git clone https://github.com/julienaxyomlabs/reel-sfx && cd reel-sfx
python -m venv .venv && . .venv/bin/activate
pip install -e ".[test]"
pytest -q
```

CI runs the tests on Linux, macOS and Windows with Python 3.9 and 3.12, then builds the wheel and checks its
contents.
