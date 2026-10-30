"""Sound recipes. Each one is designed from first principles (oscillators, shaped noise, envelopes):
no recording, sample or analysis of any existing sound is used anywhere in this package.

A recipe takes (seed, sr) and returns a stereo float array (n, 2) plus its sync anchor in seconds:
the instant that should land on the visual event (an onset, the peak of a sweep, or the end of a riser).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Tuple

import numpy as np

from .synth import (SR, adsr, chirp, exp_decay, fade, lowpass, normalize, rng, shaped_noise, soft_clip, stereo,
                    sweep_filter_noise, t_axis)

Stereo = np.ndarray


@dataclass(frozen=True)
class Recipe:
    id: str
    title: str
    category: str
    anchor: str                 # 'onset' | 'peak' | 'end'
    tags: Tuple[str, ...]
    use: str
    level_db: float             # suggested gain under a −16 LUFS voice (starting point, not a rule)
    fn: Callable[[int, int], Tuple[Stereo, float]] = field(repr=False, compare=False)
    seed: int = 1


RECIPES: Dict[str, Recipe] = {}


def recipe(id, title, category, anchor, tags, use, level_db, seed=1):
    def deco(fn):
        RECIPES[id] = Recipe(id, title, category, anchor, tuple(tags), use, level_db, fn, seed)
        return fn
    return deco


def _moving_pan(x: np.ndarray, start: float, end: float) -> Stereo:
    """Mono → stereo with the pan travelling from `start` to `end` (−1..1), constant power."""
    p = np.linspace(start, end, len(x)); th = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(th), x * np.sin(th)], 1) * np.sqrt(2)


def _bump(n: int, peak_at: float, rise_pow: float = 2.0, fall_pow: float = 2.5) -> np.ndarray:
    """0 → 1 → 0 envelope peaking at fraction `peak_at` of the length."""
    k = max(1, int(n * peak_at)); a = np.linspace(0, 1, k) ** rise_pow; b = np.linspace(1, 0, n - k) ** fall_pow
    return np.r_[a, b]


# ── whooshes ────────────────────────────────────────────────────────────────────────────────────────

@recipe('whoosh.soft', 'Soft low whoosh', 'whoosh', 'peak', ['whoosh', 'transition', 'swipe', 'soft', 'dark'],
        'Cuts, slides and camera moves; the loudest instant lands on the cut.', -14, seed=11)
def whoosh_soft(seed, sr):
    n = int(0.9 * sr); g = rng(seed); peak = 0.48
    fc = 350 * (1400 / 350) ** _bump(n, peak, 1.2, 1.4)
    x = sweep_filter_noise(n, sr, g, fc, q=1.6) * _bump(n, peak, 2.2, 2.8)
    y = _moving_pan(lowpass(x, sr, 3000), -0.5, 0.5)
    return normalize(fade(y, sr, 0.01, 0.05)), peak * 0.9


@recipe('whoosh.air', 'Airy bright whoosh', 'whoosh', 'peak', ['whoosh', 'air', 'bright', 'transition', 'reveal'],
        'Lighter transitions, text or sticker reveals.', -16, seed=12)
def whoosh_air(seed, sr):
    n = int(0.7 * sr); g = rng(seed); peak = 0.55
    fc = 1500 * (6500 / 1500) ** _bump(n, peak, 1.0, 1.6)
    x = sweep_filter_noise(n, sr, g, fc, q=1.2) * _bump(n, peak, 2.5, 3.0)
    y = _moving_pan(x, 0.4, -0.4)
    return normalize(fade(y, sr, 0.005, 0.04)), peak * 0.7


@recipe('whoosh.swipe', 'Fast swipe', 'whoosh', 'peak', ['whoosh', 'swipe', 'fast', 'ui', 'slide'],
        'Quick UI slides, card flicks, short wipes.', -15, seed=13)
def whoosh_swipe(seed, sr):
    n = int(0.32 * sr); g = rng(seed); peak = 0.6
    fc = 900 * (4200 / 900) ** np.linspace(0, 1, n) ** 0.7
    x = sweep_filter_noise(n, sr, g, fc, q=1.4, block=512) * _bump(n, peak, 1.8, 2.2)
    y = _moving_pan(x, -0.3, 0.3)
    return normalize(fade(y, sr, 0.003, 0.02)), peak * 0.32


# ── risers and swells (anchor = end) ────────────────────────────────────────────────────────────────

@recipe('riser.noise', 'Noise riser', 'riser', 'end', ['riser', 'build', 'tension', 'transition'],
        'Build-up into a reveal; place the end on the reveal frame.', -14, seed=21)
def riser_noise(seed, sr):
    dur = 2.0; n = int(dur * sr); g = rng(seed); t = t_axis(dur, sr)
    fc = 300 * (9000 / 300) ** (t / dur) ** 1.6
    env = (t / dur) ** 2.4
    air = sweep_filter_noise(n, sr, g, fc, q=1.3) * env
    tone = chirp(110 * 4 ** (t / dur) ** 1.4, sr) * env ** 1.5 * 0.25
    y = stereo(air + tone, width=0.5, gen=g)
    return normalize(fade(y, sr, 0.05, 0.004)), dur


@recipe('riser.tonal', 'Tonal riser', 'riser', 'end', ['riser', 'synth', 'build', 'pitch'],
        'Musical build-up into a hit or a title.', -15, seed=22)
def riser_tonal(seed, sr):
    dur = 1.6; t = t_axis(dur, sr); g = rng(seed)
    f0 = 220 * 4 ** (t / dur) ** 1.3
    y = np.zeros_like(t)
    for k, det in zip(range(1, 7), (0, 0.3, -0.2, 0.15, -0.35, 0.25)):
        y += chirp(f0 * k * (1 + det / 100), sr, g.uniform(0, 6.28)) / k ** 1.1
    y *= (t / dur) ** 1.8
    return normalize(fade(stereo(y, width=0.35, gen=g), sr, 0.05, 0.004)), dur


@recipe('swell.reverse', 'Reverse swell', 'riser', 'end', ['swell', 'reverse', 'suck', 'transition'],
        'Short reversed bloom that pulls into a cut.', -14, seed=23)
def swell_reverse(seed, sr):
    dur = 1.1; n = int(dur * sr); g = rng(seed); t = t_axis(dur, sr)
    ring = sum(np.sin(2 * np.pi * f * t + g.uniform(0, 6.28)) * np.exp(-t / tau) * a
               for f, tau, a in ((392, 0.5, 1.0), (587, 0.35, 0.6), (784, 0.25, 0.4), (1175, 0.18, 0.25)))
    noise = shaped_noise(n, sr, g, 200, 6000, -3) * np.exp(-t / 0.3) * 0.5
    y = (ring + noise)[::-1]
    return normalize(fade(stereo(y, width=0.6, gen=g), sr, 0.02, 0.006)), dur


# ── impacts ─────────────────────────────────────────────────────────────────────────────────────────

@recipe('impact.sub', 'Sub impact', 'impact', 'onset', ['impact', 'hit', 'sub', 'punch', 'reveal'],
        'A heavy hit on a reveal, a title slam or a punch-in.', -10, seed=31)
def impact_sub(seed, sr):
    dur = 1.6; n = int(dur * sr); g = rng(seed); t = t_axis(dur, sr)
    sub = chirp(38 + 34 * np.exp(-t / 0.08), sr) * exp_decay(n, sr, 0.45)
    thump = np.sin(2 * np.pi * 150 * t) * exp_decay(n, sr, 0.05) * 0.5
    crack = shaped_noise(n, sr, g, 1500, 9000) * exp_decay(n, sr, 0.004) * 0.7
    y = soft_clip(sub + thump + crack, 1.6)
    return normalize(fade(stereo(y, width=0.15, gen=g), sr, 0.0005, 0.2)), 0.0005


@recipe('impact.boom', 'Distant boom', 'impact', 'onset', ['boom', 'impact', 'rumble', 'cinematic', 'low'],
        'A wide, distant low boom for big moments.', -10, seed=32)
def impact_boom(seed, sr):
    dur = 3.0; n = int(dur * sr); g = rng(seed); t = t_axis(dur, sr); hit = 0.12
    after = np.clip(t - hit, 0, None)
    env = np.where(t < hit, (t / hit) ** 3 * 0.25, np.exp(-after / 0.7))
    rumble = lowpass(shaped_noise(n, sr, g, 20, 900, -4), sr, 300) * env
    sub = np.sin(2 * np.pi * 44 * after) * np.exp(-after / 0.9) * (t >= hit)
    y = soft_clip(0.8 * rumble / (np.abs(rumble).max() + 1e-12) + 0.8 * sub, 1.3)
    return normalize(fade(stereo(y, width=0.55, gen=g), sr, 0.01, 0.4)), hit


@recipe('drop.sub', 'Sub drop', 'impact', 'onset', ['808', 'sub', 'drop', 'bass', 'slide'],
        'Bass drop under a beat change or a punchline.', -10, seed=33)
def drop_sub(seed, sr):
    dur = 1.3; n = int(dur * sr); t = t_axis(dur, sr); g = rng(seed)
    f = 45 + 65 * np.exp(-t / 0.22)
    body = chirp(f, sr) * adsr(n, sr, 0.003, 0.0, 1.0, 1.0, 2.2)
    click = np.sin(2 * np.pi * 1800 * t) * exp_decay(n, sr, 0.002) * 0.3
    y = soft_clip(body + click, 1.8)
    return normalize(fade(np.stack([y, y], 1), sr, 0.0, 0.15)), 0.0


@recipe('heartbeat', 'Heartbeat', 'impact', 'onset', ['heartbeat', 'tension', 'pulse', 'low'],
        'Tension under a decision; loop it or place it once per beat.', -12, seed=34)
def heartbeat(seed, sr):
    dur = 0.9; n = int(dur * sr); t = t_axis(dur, sr); g = rng(seed)
    def thump(t0, a):
        tt = np.clip(t - t0, 0, None); on = t >= t0
        return on * a * (np.sin(2 * np.pi * (52 + 30 * np.exp(-tt / 0.03)) * tt) * np.exp(-tt / 0.07))
    y = thump(0.0, 1.0) + thump(0.24, 0.7)
    y = lowpass(y + shaped_noise(n, sr, g, 30, 200) * 0.03 * np.exp(-t / 0.2), sr, 220)
    return normalize(fade(np.stack([y, y], 1), sr, 0.001, 0.1)), 0.0


# ── pops, blips, clicks ─────────────────────────────────────────────────────────────────────────────

@recipe('pop.short', 'Short pop', 'pop', 'onset', ['pop', 'sticker', 'appear', 'bubble'],
        'A sticker, emoji or icon appearing.', -16, seed=41)
def pop_short(seed, sr):
    dur = 0.14; n = int(dur * sr); t = t_axis(dur, sr); g = rng(seed)
    y = chirp(330 + 700 * np.exp(-t / 0.012), sr) * exp_decay(n, sr, 0.028)
    y += shaped_noise(n, sr, g, 2000, 8000) * exp_decay(n, sr, 0.0015) * 0.25
    return normalize(fade(stereo(y, width=0.1, gen=g), sr, 0.0004, 0.02)), 0.0004


@recipe('blip.tone', 'Tonal blip', 'pop', 'onset', ['blip', 'tone', 'ui', 'notification', 'counter'],
        'Counters, small UI confirmations, list items appearing.', -18, seed=42)
def blip_tone(seed, sr):
    dur = 0.1; n = int(dur * sr); t = t_axis(dur, sr)
    y = (np.sin(2 * np.pi * 1320 * t) + 0.18 * np.sin(2 * np.pi * 2640 * t)) * adsr(n, sr, 0.002, 0.0, 1.0, 0.08, 2.0)
    return normalize(np.stack([y, y], 1)), 0.0


@recipe('bloop.up', 'Rising bloop', 'pop', 'onset', ['bloop', 'glide', 'up', 'playful', 'appear'],
        'Something growing or popping up; lighter than an impact.', -17, seed=43)
def bloop_up(seed, sr):
    dur = 0.24; n = int(dur * sr); t = t_axis(dur, sr)
    y = chirp(280 * (1250 / 280) ** (t / dur) ** 0.8, sr) * np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.4
    return normalize(fade(np.stack([y, y], 1), sr, 0.004, 0.01)), 0.004


@recipe('click.ui', 'UI click', 'click', 'onset', ['click', 'mouse', 'ui', 'button', 'tap'],
        'Cursor clicks, taps and button presses.', -18, seed=51)
def click_ui(seed, sr):
    dur = 0.06; n = int(dur * sr); t = t_axis(dur, sr); g = rng(seed)
    y = shaped_noise(n, sr, g, 1800, 9000) * exp_decay(n, sr, 0.0018) + 0.5 * np.sin(2 * np.pi * 3100 * t) * exp_decay(n, sr, 0.005)
    return normalize(stereo(y, width=0.05, gen=g)), 0.0


@recipe('tick.clock', 'Clock tick', 'click', 'onset', ['tick', 'clock', 'timer', 'countdown', 'tension'],
        'A ticking clock; repeat it and speed it up for tension.', -20, seed=52)
def tick_clock(seed, sr):
    dur = 0.05; n = int(dur * sr); t = t_axis(dur, sr); g = rng(seed)
    y = np.sin(2 * np.pi * 3600 * t) * exp_decay(n, sr, 0.003) + shaped_noise(n, sr, g, 3000, 12000) * exp_decay(n, sr, 0.0008) * 0.4
    return normalize(np.stack([y, y], 1)), 0.0


@recipe('tock.wood', 'Wooden tock', 'click', 'onset', ['wood', 'tock', 'knock', 'piece', 'chess', 'board'],
        'A wooden piece set down on a board; small knocks.', -16, seed=53)
def tock_wood(seed, sr):
    dur = 0.16; n = int(dur * sr); t = t_axis(dur, sr); g = rng(seed)
    body = 0.55 * np.sin(2 * np.pi * 520 * t) * exp_decay(n, sr, 0.018) + 0.35 * np.sin(2 * np.pi * 190 * t) * exp_decay(n, sr, 0.035)
    click = shaped_noise(n, sr, g, 1500, 6000) * exp_decay(n, sr, 0.0025) * 0.5
    return normalize(stereo(body + click, width=0.05, gen=g)), 0.0


# ── tones ───────────────────────────────────────────────────────────────────────────────────────────

@recipe('bell.ding', 'Small bell ding', 'bell', 'onset', ['bell', 'ding', 'notification', 'correct', 'chime'],
        'Notifications, a correct answer, a clean "done".', -16, seed=61)
def bell_ding(seed, sr):
    dur = 2.4; n = int(dur * sr); t = t_axis(dur, sr); g = rng(seed); f0 = 1046.5
    # textbook church-bell partial ratios (hum, prime, tierce, quint, nominal, upper partials)
    parts = ((0.5, 0.25, 1.4), (1.0, 1.0, 1.1), (1.2, 0.55, 0.8), (1.5, 0.35, 0.6), (2.0, 0.6, 0.55), (2.5, 0.2, 0.35), (3.0, 0.15, 0.25))
    y = sum(a * np.sin(2 * np.pi * f0 * r * (1 + g.uniform(-0.002, 0.002)) * t + g.uniform(0, 6.28)) * np.exp(-t / tau) for r, a, tau in parts)
    y += shaped_noise(n, sr, g, 2000, 10000) * exp_decay(n, sr, 0.002) * 0.4
    return normalize(fade(stereo(y, width=0.3, gen=g), sr, 0.0005, 0.3)), 0.0005


@recipe('bleep.censor', 'Censor bleep (1 kHz)', 'tone', 'onset', ['bleep', 'censor', 'beep', 'tone', '1khz'],
        'Covering a word; stretch it with render(..., dur=).', -18, seed=62)
def bleep_censor(seed, sr, dur=0.6):
    t = t_axis(dur, sr); y = np.sin(2 * np.pi * 1000 * t)
    return normalize(fade(np.stack([y, y], 1), sr, 0.004, 0.006), -3), 0.0


@recipe('drone.pulse', 'Pulsing sub drone', 'drone', 'onset', ['drone', 'tension', 'pulse', 'sub', 'bed'],
        'A low tension bed under a long moment; fade it in and out.', -16, seed=71)
def drone_pulse(seed, sr):
    dur = 4.0; n = int(dur * sr); t = t_axis(dur, sr); g = rng(seed)
    am = 0.55 + 0.45 * np.sin(2 * np.pi * 5.5 * t - np.pi / 2)
    y = (np.sin(2 * np.pi * 55 * t) + 0.45 * np.sin(2 * np.pi * 110.4 * t) + 0.15 * np.sin(2 * np.pi * 165.2 * t)) * am
    y += lowpass(shaped_noise(n, sr, g, 40, 400, -3), sr, 250) * 0.25
    return normalize(fade(stereo(y, width=0.2, gen=g), sr, 0.4, 0.6)), 0.0


def ids() -> List[str]:
    return sorted(RECIPES)
