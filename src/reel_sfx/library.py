"""The bundled sounds: metadata, file paths, loading and fresh renders."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from .generators import RECIPES
from .wavio import read_wav

SOUNDS_DIR = Path(__file__).parent / 'sounds'


@lru_cache(maxsize=1)
def _catalog() -> Dict[str, dict]:
    data = json.loads((SOUNDS_DIR / 'sounds.json').read_text(encoding='utf-8'))
    return {s['id']: s for s in data['sounds']}


def list_sounds(category: Optional[str] = None) -> List[dict]:
    """Metadata of every bundled sound (optionally one category), sorted by id."""
    return [s for _, s in sorted(_catalog().items()) if category in (None, s['category'])]


def info(sound_id: str) -> dict:
    try:
        return _catalog()[sound_id]
    except KeyError:
        raise KeyError(f'unknown sound {sound_id!r}; run `reel-sfx list` for the ids') from None


def path(sound_id: str) -> Path:
    """Absolute path of the bundled 48 kHz / 24-bit stereo WAV."""
    return SOUNDS_DIR / info(sound_id)['file']


def load(sound_id: str) -> Tuple[np.ndarray, int]:
    """→ (float32 array (n, 2), sample rate) of the bundled file."""
    return read_wav(path(sound_id))


def anchor(sound_id: str) -> float:
    """Seconds from the start of the file to the instant that should land on the visual event."""
    return float(info(sound_id)['anchor']['seconds'])


def render(sound_id: str, seed: Optional[int] = None, sr: int = 48000, **kwargs) -> Tuple[np.ndarray, float]:
    """Synthesize a sound afresh → (float array (n, 2), anchor seconds). A different `seed` gives a variation
    of the noise-based sounds; extra keyword arguments go to the recipe (e.g. `dur=` for bleep.censor)."""
    if sound_id not in RECIPES:
        raise KeyError(f'unknown sound {sound_id!r}')
    r = RECIPES[sound_id]
    return r.fn(r.seed if seed is None else seed, sr, **kwargs)
