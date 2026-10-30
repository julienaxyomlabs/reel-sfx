"""Every bundled sound: valid file, format, level, metadata, licence, provenance, integrity."""
import hashlib
import json
import wave
from pathlib import Path

import numpy as np
import pytest

import reel_sfx
from reel_sfx.generators import RECIPES
from reel_sfx.library import SOUNDS_DIR

META = json.loads((SOUNDS_DIR / 'sounds.json').read_text(encoding='utf-8'))
SOUNDS = META['sounds']
IDS = [s['id'] for s in SOUNDS]


def test_catalog_matches_recipes():
    assert sorted(IDS) == sorted(RECIPES), 'sounds.json and generators.RECIPES disagree: run python -m reel_sfx.build'
    assert len(IDS) == len(set(IDS))


def test_no_stray_files():
    on_disk = sorted(str(p.relative_to(SOUNDS_DIR)).replace('\\', '/') for p in SOUNDS_DIR.rglob('*') if p.is_file())
    assert on_disk == sorted(['sounds.json'] + [s['file'] for s in SOUNDS])


@pytest.mark.parametrize('s', SOUNDS, ids=IDS)
def test_wav_format(s):
    with wave.open(str(SOUNDS_DIR / s['file']), 'rb') as w:
        assert (w.getframerate(), w.getnchannels(), w.getsampwidth() * 8) == (48000, 2, 24)
        assert w.getnframes() / 48000 == pytest.approx(s['duration_s'], abs=1e-4)


@pytest.mark.parametrize('s', SOUNDS, ids=IDS)
def test_levels(s):
    x, sr = reel_sfx.load(s['id'])
    peak = 20 * np.log10(np.abs(x).max()); rms = 20 * np.log10(np.sqrt((x ** 2).mean()))
    assert peak <= -0.9, 'too hot: leave headroom'
    assert peak >= -6.0 and rms > -45, 'silent or nearly silent'
    assert (np.abs(x) >= 0.999).sum() == 0, 'clipped samples'
    assert abs(x.mean()) < 0.01, 'DC offset'
    assert np.isfinite(x).all()
    mono_loss = 20 * np.log10(np.sqrt((x.mean(1) ** 2).mean()) / np.sqrt((x ** 2).mean()))
    assert mono_loss > -3.0, 'not mono-compatible'


@pytest.mark.parametrize('s', SOUNDS, ids=IDS)
def test_metadata(s):
    assert s['license'] == 'CC0-1.0'
    assert 'No recording, sample, or analysis of any existing sound' in s['provenance']
    assert s['generator'].startswith('reel_sfx.generators:')
    assert s['anchor']['type'] in ('onset', 'peak', 'end')
    assert 0 <= s['anchor']['seconds'] <= s['duration_s'] + 1e-6
    assert hashlib.sha256((SOUNDS_DIR / s['file']).read_bytes()).hexdigest() == s['sha256']
