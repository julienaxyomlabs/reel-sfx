import numpy as np
import pytest

import reel_sfx


def test_list_and_filter():
    assert len(reel_sfx.list_sounds()) >= 15
    assert {s['category'] for s in reel_sfx.list_sounds('whoosh')} == {'whoosh'}


def test_unknown_id():
    with pytest.raises(KeyError):
        reel_sfx.info('nope')


@pytest.mark.parametrize('sid,t', [('tick.clock', 1.0), ('click.ui', 0.5), ('blip.tone', 2.25)])
def test_onset_lands_on_the_sample(sid, t):
    y = reel_sfx.place([{'t': t, 'id': sid}], duration=3.0)
    first = np.argmax(np.abs(y).max(1) > 1e-4)
    assert abs(first - round((t - reel_sfx.anchor(sid)) * 48000)) <= 2


def test_end_anchor_and_frames():
    # a riser placed on frame 60 at 30 fps ends exactly at 2.0 s
    y = reel_sfx.place([{'frame': 60, 'id': 'riser.noise'}], duration=3.0, fps=30)
    e = np.abs(y).max(1)
    assert e[: int(1.99 * 48000)].max() > 0.1 and e[int(2.001 * 48000):].max() < 1e-6


def test_cue_before_zero_is_trimmed_and_gain():
    y = reel_sfx.place([{'t': 0.1, 'id': 'whoosh.soft', 'gain_db': -6}], duration=1.0)
    assert y.shape == (48000, 2) and np.abs(y).max() < 0.5


def test_duck_and_mix():
    sr = 48000; t = np.arange(sr * 2) / sr
    voice = np.where(t < 1, 0.3 * np.sin(2 * np.pi * 200 * t), 0.0)
    sfx = np.full((sr * 2, 2), 0.1)
    d = reel_sfx.duck(voice, sfx, sr, depth_db=6)
    assert d[int(0.5 * sr), 0] == pytest.approx(0.1 * 10 ** (-6 / 20), rel=0.05)
    assert d[int(1.9 * sr), 0] == pytest.approx(0.1, rel=0.05)
    m = reel_sfx.mix(voice, sfx * 20, sr)
    assert np.abs(m).max() <= 10 ** (-1 / 20) + 1e-9


def test_wav_roundtrip(tmp_path):
    x = np.sin(np.linspace(0, 100, 4800))[:, None] * np.array([0.5, -0.5])
    for bits in (16, 24):
        reel_sfx.write_wav(tmp_path / f'a{bits}.wav', x, 48000, bits)
        y, sr = reel_sfx.read_wav(tmp_path / f'a{bits}.wav')
        assert sr == 48000 and np.abs(y - x).max() < (1e-4 if bits == 16 else 1e-6)
