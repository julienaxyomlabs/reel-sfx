"""Regenerate docs/SOUNDS.md from src/reel_sfx/sounds/sounds.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
m = json.loads((ROOT / 'src/reel_sfx/sounds/sounds.json').read_text(encoding='utf-8'))
L = ['# Sounds', '', f'{len(m["sounds"])} sounds, all 48 kHz / 24-bit stereo WAV, peak −1 dBFS (the bleep −3 dBFS), CC0-1.0.', '',
     '**Anchor**: the instant that should land on the visual event (`onset` = start of the sound, `peak` = loudest point of a sweep, '
     '`end` = the end of a riser). `reel_sfx.place()` aligns it for you.', '',
     '**Suggested gain**: a starting level for the cue under a voice normalised to about −16 LUFS. It is not a rule.', '',
     '| id | category | length | anchor | suggested gain | use |', '|---|---|---|---|---|---|']
for s in m['sounds']:
    L.append(f"| `{s['id']}` | {s['category']} | {s['duration_s']:.2f} s | {s['anchor']['type']} @ {s['anchor']['seconds']:.3f} s "
             f"| {s['suggested_gain_db']} dB | {s['use']} |")
L += ['', 'Regenerate this table after changing a recipe: see CONTRIBUTING.md.', '']
(ROOT / 'docs/SOUNDS.md').write_text('\n'.join(L), encoding='utf-8')
print('docs/SOUNDS.md:', len(m['sounds']), 'sounds')
