"""Small DSP toolkit for the generators: everything is NumPy, deterministic for a given seed.

All signals are float64 arrays, mono shape (n,) or stereo shape (n, 2), in the range [-1, 1].
"""
from __future__ import annotations

import numpy as np

SR = 48000


def t_axis(dur: float, sr: int = SR) -> np.ndarray:
    return np.arange(int(round(dur * sr))) / sr


def rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def adsr(n: int, sr: int, attack: float, decay: float = 0.0, sustain: float = 1.0, release: float = 0.0,
         curve: float = 3.0) -> np.ndarray:
    """Piecewise envelope. `curve` > 1 makes the decay/release segments exponential-looking."""
    env = np.zeros(n)
    a, d, r = (int(x * sr) for x in (attack, decay, release))
    a = min(a, n)
    if a: env[:a] = np.linspace(0, 1, a, endpoint=False) ** 1.5
    i = a
    if d and i < n:
        k = min(d, n - i); x = np.linspace(0, 1, k, endpoint=False)
        env[i:i + k] = sustain + (1 - sustain) * (1 - x) ** curve; i += k
    s_end = max(i, n - r)
    env[i:s_end] = sustain
    if r and s_end < n:
        k = n - s_end; x = np.linspace(0, 1, k)
        env[s_end:] = sustain * (1 - x) ** curve
    return env


def exp_decay(n: int, sr: int, tau: float) -> np.ndarray:
    return np.exp(-np.arange(n) / sr / tau)


def chirp(f: np.ndarray, sr: int = SR, phase0: float = 0.0) -> np.ndarray:
    """Sine whose instantaneous frequency follows the array `f` (Hz, one value per sample)."""
    return np.sin(phase0 + 2 * np.pi * np.cumsum(f) / sr)


def shaped_noise(n: int, sr: int, gen: np.random.Generator, lo: float, hi: float, tilt_db_oct: float = 0.0) -> np.ndarray:
    """White noise band-limited to [lo, hi] Hz with a spectral tilt (dB per octave), via one FFT."""
    x = gen.standard_normal(n)
    X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / sr)
    g = ((f >= lo) & (f <= hi)).astype(float)
    # soft band edges (1/3 octave raised-cosine)
    for edge, rising in ((lo, True), (hi, False)):
        if edge <= 0: continue
        band = (f > edge / 2 ** (1 / 6)) & (f < edge * 2 ** (1 / 6))
        x_ = np.log2(f[band] / edge) * 3 + 0.5
        g[band] = 0.5 - 0.5 * np.cos(np.pi * np.clip(x_ if rising else 1 - x_, 0, 1))
    with np.errstate(divide='ignore'):
        tilt = np.where(f > 0, 10 ** (tilt_db_oct * np.log2(np.maximum(f, 1) / 1000) / 20), 0)
    y = np.fft.irfft(X * g * tilt, n)
    return y / (np.abs(y).max() + 1e-12)


def sweep_filter_noise(n: int, sr: int, gen: np.random.Generator, f_center: np.ndarray, q: float = 2.0,
                       block: int = 1024) -> np.ndarray:
    """Noise through a band-pass whose centre follows `f_center` (Hz per sample): overlap-add of FFT blocks,
    each filtered with a Gaussian bump (on a log-frequency axis) centred on that block's frequency."""
    hop = block // 2; win = np.hanning(block); out = np.zeros(n + block)
    x = gen.standard_normal(n + block)
    f = np.fft.rfftfreq(block, 1 / sr); lf = np.log2(np.maximum(f, 1))
    width = 1.0 / q
    for i in range(0, n, hop):
        fc = f_center[min(i + hop, n - 1)]
        g = np.exp(-0.5 * ((lf - np.log2(fc)) / width) ** 2)
        seg = np.fft.irfft(np.fft.rfft(x[i:i + block] * win) * g, block)
        out[i:i + block] += seg
    y = out[:n]
    return y / (np.abs(y).max() + 1e-12)


def lowpass(x: np.ndarray, sr: int, fc: float) -> np.ndarray:
    """Zero-phase FFT low-pass with a smooth (1/2 octave) roll-off."""
    n = x.shape[0]; X = np.fft.rfft(x, axis=0); f = np.fft.rfftfreq(n, 1 / sr)
    g = 1 / (1 + (f / fc) ** 4)
    return np.fft.irfft(X * (g[:, None] if x.ndim == 2 else g), n, axis=0)


def stereo(mono: np.ndarray, width: float = 0.0, gen: np.random.Generator | None = None, delay_ms: float = 0.0,
           pan: float = 0.0) -> np.ndarray:
    """Mono → stereo. `width` 0..1 mixes in a decorrelated copy (random-phase all-pass), always mono-compatible
    (L+R keeps the mono signal); `delay_ms` adds a small Haas offset; `pan` -1..1 (constant power)."""
    L = R = mono
    if width > 0:
        gen = gen or rng(0)
        X = np.fft.rfft(mono); ph = np.exp(1j * gen.uniform(-np.pi, np.pi, X.shape)); ph[0] = 1
        side = np.fft.irfft(X * ph, len(mono)) * width
        L, R = mono + side, mono - side
    if delay_ms:
        d = int(delay_ms * SR / 1000); R = np.r_[np.zeros(d), R[:-d]] if d else R
    th = (pan + 1) * np.pi / 4
    return np.stack([L * np.cos(th) * np.sqrt(2), R * np.sin(th) * np.sqrt(2)], 1)


def fade(x: np.ndarray, sr: int, fin: float = 0.0, fout: float = 0.0) -> np.ndarray:
    x = x.copy(); n = x.shape[0]
    if fin: k = min(n, int(fin * sr)); x[:k] *= (np.linspace(0, 1, k) ** 2)[:, None] if x.ndim == 2 else np.linspace(0, 1, k) ** 2
    if fout: k = min(n, int(fout * sr)); r = np.cos(np.linspace(0, np.pi / 2, k)) ** 2; x[-k:] *= r[:, None] if x.ndim == 2 else r
    return x


def soft_clip(x: np.ndarray, drive: float = 1.0) -> np.ndarray:
    return np.tanh(x * drive) / np.tanh(drive)


def normalize(x: np.ndarray, peak_db: float = -1.0) -> np.ndarray:
    return x * (10 ** (peak_db / 20) / (np.abs(x).max() + 1e-12))
