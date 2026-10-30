"""reel-sfx: original procedural sound effects for short-form video editing.

    >>> import reel_sfx
    >>> [s['id'] for s in reel_sfx.list_sounds('whoosh')]
    ['whoosh.air', 'whoosh.soft', 'whoosh.swipe']
    >>> reel_sfx.path('impact.sub')            # bundled 48 kHz / 24-bit stereo WAV
    >>> stem = reel_sfx.place([{'t': 1.0, 'id': 'whoosh.soft'}], duration=3.0)
"""
from .library import anchor, info, list_sounds, load, path, render
from .mix import duck, mix, place
from .wavio import read_wav, write_wav

__version__ = '0.1.0'
__all__ = ['anchor', 'info', 'list_sounds', 'load', 'path', 'render', 'place', 'duck', 'mix', 'read_wav', 'write_wav',
           '__version__']
