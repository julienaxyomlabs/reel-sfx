"""The bundled WAVs are exactly what the recipes produce (within 24-bit rounding)."""
import numpy as np
import pytest

import reel_sfx

IDS = [s['id'] for s in reel_sfx.list_sounds()]


@pytest.mark.parametrize('sid', IDS)
def test_render_matches_bundled_file(sid):
    y, anc = reel_sfx.render(sid)
    x, sr = reel_sfx.load(sid)
    assert y.shape == x.shape
    assert np.abs(y - x).max() < 1e-4            # 24-bit step is 1.2e-7; allows cross-platform FFT rounding
    assert anc == pytest.approx(reel_sfx.anchor(sid), abs=1e-6)


def test_seed_gives_a_variation():
    a, _ = reel_sfx.render('whoosh.soft'); b, _ = reel_sfx.render('whoosh.soft', seed=99)
    assert a.shape == b.shape and np.abs(a - b).max() > 0.05


def test_other_sample_rate():
    y, _ = reel_sfx.render('pop.short', sr=44100)
    assert abs(len(y) - round(0.14 * 44100)) <= 1
