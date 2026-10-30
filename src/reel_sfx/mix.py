"""Place sounds on a timeline (sample-accurate, anchor-aware) and mix them under a dialogue track."""
from __future__ import annotations

from typing import Iterable, Mapping, Optional

import numpy as np

from .library import anchor as _anchor, load


def _resample(x: np.ndarray, sr_in: int, sr_out: int) -> np.ndarray:
    if sr_in == sr_out: return x
    n = int(round(len(x) * sr_out / sr_in)); t = np.arange(n) * sr_in / sr_out
    return np.stack([np.interp(t, np.arange(len(x)), x[:, c]) for c in range(x.shape[1])], 1)


def place(cues: Iterable[Mapping], duration: float, sr: int = 48000, fps: Optional[float] = None) -> np.ndarray:
    """Render an SFX stem of `duration` seconds.

    Each cue: {"t": seconds, "id": sound id, "gain_db": 0, "pan": 0 (−1..1), "frame": optional int}.
    The sound's anchor (onset / peak / end) lands exactly on `t` (or on frame/fps when `frame` is given).
    Sounds that would start before 0 are trimmed; anything past `duration` is cut with a 10 ms fade.
    """
    out = np.zeros((int(round(duration * sr)), 2))
    for c in cues:
        x, sr0 = load(c['id']); x = _resample(x.astype(np.float64), sr0, sr)
        t = c['frame'] / fps if ('frame' in c and fps) else float(c['t'])
        pan = float(c.get('pan', 0.0))
        if pan:
            th = (pan + 1) * np.pi / 4; x = x * np.array([np.cos(th), np.sin(th)]) * np.sqrt(2)
        i = int(round((t - _anchor(c['id'])) * sr)); g = 10 ** (float(c.get('gain_db', 0.0)) / 20)
        if i < 0: x, i = x[-i:], 0
        j = min(len(out), i + len(x))
        if j > i: out[i:j] += x[:j - i] * g
    f = min(len(out), int(0.01 * sr))
    if f: out[-f:] *= np.linspace(1, 0, f)[:, None]
    return out


def duck(dialogue: np.ndarray, sfx: np.ndarray, sr: int, depth_db: float = 6.0, threshold_db: float = -40.0,
         attack: float = 0.01, release: float = 0.25) -> np.ndarray:
    """Lower `sfx` by up to `depth_db` while `dialogue` is above `threshold_db` (RMS, 10 ms frames)."""
    d = dialogue if dialogue.ndim == 1 else dialogue.mean(1)
    n = min(len(d), len(sfx)); hop = max(1, int(0.01 * sr))
    fr = np.sqrt(np.add.reduceat(d[:n] ** 2, np.arange(0, n, hop)) / hop + 1e-12)
    on = (20 * np.log10(fr) > threshold_db).astype(float)
    g = np.empty_like(on); s = 0.0
    a_c, r_c = np.exp(-0.01 / attack), np.exp(-0.01 / release)
    for k, v in enumerate(on):
        s = (a_c if v > s else r_c) * s + (1 - (a_c if v > s else r_c)) * v; g[k] = s
    gain = 10 ** (-depth_db * np.repeat(g, hop)[:n] / 20)
    out = sfx.copy(); out[:n] *= gain[:, None]
    return out


def mix(dialogue: Optional[np.ndarray], sfx: np.ndarray, sr: int, duck_db: float = 6.0, peak_db: float = -1.0) -> np.ndarray:
    """Dialogue + ducked SFX, peak-normalised only if it would clip above `peak_db`."""
    if dialogue is None:
        y = sfx
    else:
        d = dialogue if dialogue.ndim == 2 else np.stack([dialogue, dialogue], 1)
        n = max(len(d), len(sfx)); y = np.zeros((n, 2))
        y[:len(d)] += d; y[:len(sfx)] += duck(d, sfx, sr, duck_db)[:len(sfx)]
    lim = 10 ** (peak_db / 20); pk = np.abs(y).max()
    return y * (lim / pk) if pk > lim else y
