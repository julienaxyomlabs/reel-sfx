"""Render five variations of a noise-based sound (different seeds) so repeated cues don't sound identical.

    python examples/variations.py whoosh.soft examples/out
"""
import sys
from pathlib import Path

import reel_sfx

sid, out = (sys.argv[1], Path(sys.argv[2])) if len(sys.argv) == 3 else ('whoosh.soft', Path('examples/out'))
for seed in range(1, 6):
    y, anchor = reel_sfx.render(sid, seed=seed)
    reel_sfx.write_wav(out / f'{sid}_seed{seed}.wav', y, 48000)
print(f'5 variations of {sid} -> {out}  (anchor {anchor:.3f} s)')
