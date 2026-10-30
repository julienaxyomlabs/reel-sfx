"""Minimal WAV I/O with the standard library (PCM 16/24/32-bit integer), no extra dependencies."""
from __future__ import annotations

import wave
from pathlib import Path
from typing import Tuple, Union

import numpy as np

PathLike = Union[str, Path]


def read_wav(path: PathLike) -> Tuple[np.ndarray, int]:
    """→ (float32 array of shape (n, channels) in [-1, 1], sample rate)."""
    with wave.open(str(path), 'rb') as w:
        ch, sw, sr, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        raw = w.readframes(n)
    if sw == 2:
        x = np.frombuffer(raw, '<i2').astype(np.float32) / 32768.0
    elif sw == 3:
        b = np.frombuffer(raw, np.uint8).reshape(-1, 3).astype(np.int32)
        v = b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16)
        x = (np.where(v >= 1 << 23, v - (1 << 24), v)).astype(np.float32) / float(1 << 23)
    elif sw == 4:
        x = np.frombuffer(raw, '<i4').astype(np.float32) / float(1 << 31)
    else:
        raise ValueError(f'{path}: unsupported sample width {sw * 8} bit')
    return x.reshape(-1, ch), sr


def write_wav(path: PathLike, x: np.ndarray, sr: int, bits: int = 24) -> None:
    """Write float audio (n,) or (n, channels) as PCM. Values are clipped to [-1, 1]."""
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1: x = x[:, None]
    x = np.clip(x, -1.0, 1.0)
    if bits == 16:
        data = np.round(x * 32767).astype('<i2').tobytes()
    elif bits == 24:
        v = np.round(x * ((1 << 23) - 1)).astype(np.int32).reshape(-1)
        data = np.stack([v & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF], 1).astype(np.uint8).tobytes()
    else:
        raise ValueError('bits must be 16 or 24')
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(x.shape[1]); w.setsampwidth(bits // 8); w.setframerate(sr); w.writeframes(data)
