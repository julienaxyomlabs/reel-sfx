# Sounds

19 sounds, all 48 kHz / 24-bit stereo WAV, peak −1 dBFS (the bleep −3 dBFS), CC0-1.0.

**Anchor**: the instant that should land on the visual event (`onset` = start of the sound, `peak` = loudest point of a sweep, `end` = the end of a riser). `reel_sfx.place()` aligns it for you.

**Suggested gain**: a starting level for the cue under a voice normalised to about −16 LUFS. It is not a rule.

| id | category | length | anchor | suggested gain | use |
|---|---|---|---|---|---|
| `bell.ding` | bell | 2.40 s | onset @ 0.001 s | -16 dB | Notifications, a correct answer, a clean "done". |
| `bleep.censor` | tone | 0.60 s | onset @ 0.000 s | -18 dB | Covering a word; stretch it with render(..., dur=). |
| `blip.tone` | pop | 0.10 s | onset @ 0.000 s | -18 dB | Counters, small UI confirmations, list items appearing. |
| `bloop.up` | pop | 0.24 s | onset @ 0.004 s | -17 dB | Something growing or popping up; lighter than an impact. |
| `click.ui` | click | 0.06 s | onset @ 0.000 s | -18 dB | Cursor clicks, taps and button presses. |
| `drone.pulse` | drone | 4.00 s | onset @ 0.000 s | -16 dB | A low tension bed under a long moment; fade it in and out. |
| `drop.sub` | impact | 1.30 s | onset @ 0.000 s | -10 dB | Bass drop under a beat change or a punchline. |
| `heartbeat` | impact | 0.90 s | onset @ 0.000 s | -12 dB | Tension under a decision; loop it or place it once per beat. |
| `impact.boom` | impact | 3.00 s | onset @ 0.120 s | -10 dB | A wide, distant low boom for big moments. |
| `impact.sub` | impact | 1.60 s | onset @ 0.001 s | -10 dB | A heavy hit on a reveal, a title slam or a punch-in. |
| `pop.short` | pop | 0.14 s | onset @ 0.000 s | -16 dB | A sticker, emoji or icon appearing. |
| `riser.noise` | riser | 2.00 s | end @ 2.000 s | -14 dB | Build-up into a reveal; place the end on the reveal frame. |
| `riser.tonal` | riser | 1.60 s | end @ 1.600 s | -15 dB | Musical build-up into a hit or a title. |
| `swell.reverse` | riser | 1.10 s | end @ 1.100 s | -14 dB | Short reversed bloom that pulls into a cut. |
| `tick.clock` | click | 0.05 s | onset @ 0.000 s | -20 dB | A ticking clock; repeat it and speed it up for tension. |
| `tock.wood` | click | 0.16 s | onset @ 0.000 s | -16 dB | A wooden piece set down on a board; small knocks. |
| `whoosh.air` | whoosh | 0.70 s | peak @ 0.385 s | -16 dB | Lighter transitions, text or sticker reveals. |
| `whoosh.soft` | whoosh | 0.90 s | peak @ 0.432 s | -14 dB | Cuts, slides and camera moves; the loudest instant lands on the cut. |
| `whoosh.swipe` | whoosh | 0.32 s | peak @ 0.192 s | -15 dB | Quick UI slides, card flicks, short wipes. |

Regenerate this table after changing a recipe: see CONTRIBUTING.md.
