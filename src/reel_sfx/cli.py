"""reel-sfx command line:  list · info · path · export · render · place"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from . import __version__
from .library import info, list_sounds, path, render
from .mix import mix, place
from .wavio import read_wav, write_wav


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog='reel-sfx', description='Original procedural sound effects for video editing.')
    p.add_argument('--version', action='version', version=f'reel-sfx {__version__}')
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('list', help='list the sounds'); s.add_argument('--category'); s.add_argument('--json', action='store_true')
    s = sub.add_parser('info', help='metadata of one sound'); s.add_argument('id')
    s = sub.add_parser('path', help='path of a bundled WAV'); s.add_argument('id')
    s = sub.add_parser('export', help='copy the bundled WAVs (+ sounds.json) to a folder'); s.add_argument('dir')
    s = sub.add_parser('render', help='synthesize a sound afresh (another seed = a variation)')
    s.add_argument('id'); s.add_argument('--out', required=True); s.add_argument('--seed', type=int); s.add_argument('--sr', type=int, default=48000)
    s = sub.add_parser('place', help='render an SFX stem (or a mix under dialogue) from a cue file')
    s.add_argument('cues', help='JSON list of {"t": seconds, "id": sound id, "gain_db": 0, "pan": 0}')
    s.add_argument('--duration', type=float, help='seconds (default: the dialogue length, else last cue + 3 s)')
    s.add_argument('--dialogue', help='a voice WAV: the SFX are ducked under it and mixed with it')
    s.add_argument('--duck-db', type=float, default=6.0); s.add_argument('--sr', type=int, default=48000)
    s.add_argument('--out', required=True)
    a = p.parse_args(argv)

    if a.cmd == 'list':
        rows = list_sounds(a.category)
        if a.json: print(json.dumps(rows, indent=1)); return 0
        for r in rows:
            print(f"{r['id']:<16} {r['category']:<8} {r['duration_s']:>5.2f} s  anchor {r['anchor']['type']:<5} {r['anchor']['seconds']:.3f} s  {r['title']}")
        return 0
    if a.cmd == 'info':
        print(json.dumps(info(a.id), indent=1)); return 0
    if a.cmd == 'path':
        print(path(a.id)); return 0
    if a.cmd == 'export':
        out = Path(a.dir); out.mkdir(parents=True, exist_ok=True)
        for r in list_sounds():
            dst = out / r['file']; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(path(r['id']), dst)
        shutil.copyfile(path(list_sounds()[0]['id']).parents[1] / 'sounds.json', out / 'sounds.json')
        print(f'{len(list_sounds())} sounds → {out}'); return 0
    if a.cmd == 'render':
        y, anc = render(a.id, a.seed, a.sr); write_wav(a.out, y, a.sr)
        print(f'{a.out}  ({len(y) / a.sr:.3f} s, anchor {anc:.4f} s)'); return 0
    if a.cmd == 'place':
        cues = json.loads(Path(a.cues).read_text(encoding='utf-8'))
        dia = None
        if a.dialogue:
            dia, sr_d = read_wav(a.dialogue)
            if sr_d != a.sr: print(f'error: dialogue is {sr_d} Hz; pass --sr {sr_d}', file=sys.stderr); return 2
        dur = a.duration or (len(dia) / a.sr if dia is not None else max(float(c['t']) for c in cues) + 3.0)
        y = mix(dia, place(cues, dur, a.sr), a.sr, a.duck_db)
        write_wav(a.out, y, a.sr); print(f'{a.out}  ({len(y) / a.sr:.2f} s, {len(cues)} cues)'); return 0
    return 1


if __name__ == '__main__':
    sys.exit(main())
