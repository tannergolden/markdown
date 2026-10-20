# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The theme's small folk, each with its twin: doves that wheel over heaven and little devils on bat wings that
flap over hell, a cherub with its harp on a cloud and an imp with its pitchfork on a burning rock, and the feathers
that drift down by day where sparks rise by night."""
from __future__ import annotations

import math

from ...holidays.pixel import Pix
from .kit import ellipse, flat, form, glow, outline, poly, stroke
from .palette import C, RAMP, X

GOLD, LINEN, CLOUD, PEARL = RAMP["gold"], RAMP["linen"], RAMP["cloud"], RAMP["pearl"]
HIDE, HORN, MEMBRANE, IRON, FIRE, LAVA = (RAMP["hide"], RAMP["horn"], RAMP["membrane"], RAMP["iron"], RAMP["fire"],
                                          RAMP["lava"])

# A dove flying to the left, its wings up and its wings down: w white, W its shade, v deeper shade, o its edge,
# y its beak, e its eye.
DOVE = (
    ["......o....",
     ".....owo...",
     "....owWo...",
     ".oo.owWo...",
     "oewwwwWwoo.",
     "ywwwwwwWvvo",
     ".ovWWWvoo..",
     "..oo......."],
    ["...........",
     "...........",
     ".oo........",
     "oewwwwwwoo.",
     "ywwwwwwWvvo",
     ".owwWWWvo..",
     "..ovWWvo...",
     "....ooo...."],
)
# An imp flapping, the dove's twin, seen from before: m the bones and edges of its bat wings, M their skin lit by
# the fires, h its hide, H its shade, n its horns, e its burning eyes, t its tail.
IMP = (
    ["m...........m",
     "Mm..n...n..mM",
     "MMm.nhhhn.mMM",
     "MMMmhehehmMMM",
     ".MMMhhhhhMMM.",
     "..M.HhhhH.M..",
     ".....h.h.....",
     "......t......",
     "......tt....."],
    [".............",
     "....n...n....",
     "....nhhhn....",
     "..mmhehehmm..",
     ".mMMhhhhhMMm.",
     "mMMMHhhhHMMMm",
     "MM.M.h.h.M.MM",
     "M.....t.....M",
     "......tt....."],
)


def dove_symbol(p: Pix, frame: int):
    key = ("dove", frame)
    if key not in p.syms:
        pal = {"w": C["white"], "W": LINEN[4], "v": LINEN[2], "o": CLOUD[1], "y": GOLD[3], "e": RAMP["brown"][0]}
        p.symbol(key, {(i, j): pal[ch] for j, r in enumerate(DOVE[frame]) for i, ch in enumerate(r) if ch in pal})
    return key


def imp_symbol(p: Pix, frame: int):
    key = ("imp", frame)
    if key not in p.syms:
        pal = {"m": MEMBRANE[3], "M": MEMBRANE[5], "h": HIDE[4], "H": HIDE[2], "n": HORN[4], "e": FIRE[6],
               "t": HIDE[3]}
        p.symbol(key, {(i, j): pal[ch] for j, r in enumerate(IMP[frame]) for i, ch in enumerate(r) if ch in pal})
    return key


def flock(p: Pix, cx, cy, rx, ry, n, night, motion=True, seed=0, steps=32, dur=8.0):
    """Doves wheeling round (cx, cy) by day, or imps by night, each on a loop of its own, the next the other way
    round, beating their wings as they go. The still file leaves each where its loop begins."""
    import random
    rnd = random.Random(seed)
    frames = [imp_symbol(p, 0), imp_symbol(p, 1)] if night else [dove_symbol(p, 0), dove_symbol(p, 1)]
    for i in range(n):
        a0 = rnd.uniform(0, 2 * math.pi)
        krx, kry = rx * rnd.uniform(0.8, 1.1), ry * rnd.uniform(0.7, 1.0)
        turn = 1 if i % 2 == 0 else -1
        path = [(round(cx + krx * math.cos(a0 + turn * 2 * math.pi * s / steps) - 5),
                 round(cy + kry * math.sin(a0 + turn * 2 * math.pi * s / steps) - 4)) for s in range(steps)]
        if motion:
            p.fly(frames, path, dur * rnd.uniform(0.85, 1.15), z=16, flap=0.3 if not night else 0.22)
        else:
            p.use(frames[i % 2], path[0][0], path[0][1], "base")


def flock_box(cx, cy, rx, ry) -> tuple:
    """The box a flock's loops stay in, a margin round it: what it must keep clear of the words."""
    return (int(cx - rx * 1.1 - 7), int(cy - ry - 6), int(cx + rx * 1.1 + 7), int(cy + ry + 6))


# --------------------------------------------------------------------------- the cherub and the imp
def cherub(p: Pix, x, foot, k=1.0, motion=True, L="base"):
    """A cherub sitting on its cloud, plump and rosy, curls of gold, little wings of white, a halo over it, playing
    a harp of gold held before it. (x, foot) is the middle of the cloud it sits on."""
    SK = RAMP["skin0"]
    HR = RAMP["blond"]

    def pt(u, v):
        return (x + u * k, foot + v * k)

    def ell(u, v, rx, ry):
        cx, cy = pt(u, v)
        return ellipse(cx, cy, rx * k, ry * k)

    def stk(path, r0, r1=None):
        return stroke([pt(u, v) for u, v in path], r0 * k, (r1 if r1 is not None else r0) * k)

    # its wings, behind it
    wings = set()
    for s in (-1, 1):
        w = poly([pt(1.0 * s, -11.5), pt(6.5 * s, -16.5), pt(9.0 * s, -14.0), pt(8.0 * s, -10.5), pt(5.0 * s, -8.0),
                  pt(1.5 * s, -8.5)])
        wings |= w
    form(p, wings, LINEN, lo=3, hi=6, L=L, depth=1.4)
    for (qx, qy) in wings:
        if (qx + qy) % 3 == 0 and (qx, qy + 1) in wings:
            p.px(qx, qy, LINEN[3], L)
    outline(p, wings, LINEN[1], LINEN[2], L)
    # its body, plump, sitting, its legs drawn up
    body = ell(0, -7.0, 3.6, 3.6)
    legs = stk([(-1.5, -4.5), (-4.6, -3.2)], 1.6, 1.4) | stk([(1.5, -4.5), (3.2, -2.6)], 1.6, 1.4)
    form(p, body | legs, SK, lo=2, hi=5, L=L, depth=2.0)
    cloth = poly([pt(-3.6, -6.8), pt(3.6, -8.2), pt(3.4, -5.4), pt(-3.2, -4.6)])
    form(p, cloth, RAMP["azure"], lo=2, hi=5, L=L, depth=1.0)
    outline(p, body | legs | cloth, SK[1], SK[2], L, only_free=True)
    # its head, curls of gold
    head = ell(-0.4, -13.6, 3.3, 3.1)
    form(p, head, SK, lo=2, hi=5, L=L, depth=1.8)
    curls = ell(-0.2, -15.6, 3.5, 1.9) | ell(2.6, -14.2, 1.3, 1.6)
    form(p, curls, HR, lo=2, hi=5, L=L, depth=1.0)
    outline(p, head | curls, HR[1], HR[2], L, only_free=True)
    ex, ey = pt(-1.8, -13.4)
    p.px(int(ex), int(ey), RAMP["brown"][1], L)
    p.px(int(ex) + 2, int(ey), RAMP["brown"][1], L)
    p.px(int(ex) - 1, int(ey) + 1, RAMP["rose"][4], L)
    p.px(int(ex) + 1, int(ey) + 2, SK[2], L)
    # the harp before it, a frame of gold strung with light
    hx, hy = pt(-4.8, -5.0)
    frame = stroke([(hx, hy), (hx - 0.6 * k, hy - 5 * k), (hx + 1.4 * k, hy - 8.4 * k)], 0.75 * k) | \
        stroke([(hx, hy), (hx + 3.2 * k, hy - 1.2 * k)], 0.7 * k)
    for (qx, qy) in frame:
        p.px(qx, qy, GOLD[5] if (qx - 1, qy) not in frame else GOLD[3], L)
    for i in range(3):
        sx = hx + (0.6 + 0.9 * i) * k
        for yy in range(int(hy - (6.6 - 1.4 * i) * k), int(hy - 1 * k)):
            p.px(int(sx), yy, GOLD[6], L)
    arm = stk([(-2.6, -9.0), (-4.4, -7.2)], 1.1)
    form(p, arm, SK, lo=2, hi=5, L=L, depth=1.0)
    # the halo
    hx, hy = pt(-0.2, -19.2)
    ring = ellipse(hx, hy, 3.4 * k, 1.1 * k) - ellipse(hx, hy + 0.2, 3.4 * k - 1.1, max(0.4, 1.1 * k - 0.8))
    for (qx, qy) in ring:
        p.px(qx, qy, GOLD[5] if qx < hx else GOLD[3], L)
    glow(p, hx, hy, 5 * k, 2.6 * k, X["glory"], (0.2, 0.36))
    Lt = p.twinkle(2) if motion else L
    p.px(int(hx - 2 * k), int(hy) - 1, C["white"], Lt)


def imp_on_rock(p: Pix, x, foot, k=1.0, motion=True, L="base"):
    """The cherub's twin: an imp squatting on its rock, red and wiry, little bat wings, horns and pointed ears, a
    grin set with fangs, its tail curling, a pitchfork of iron held up red-hot. (x, foot) is where its rock is."""
    def pt(u, v):
        return (x + u * k, foot + v * k)

    def ell(u, v, rx, ry):
        cx, cy = pt(u, v)
        return ellipse(cx, cy, rx * k, ry * k)

    def stk(path, r0, r1=None):
        return stroke([pt(u, v) for u, v in path], r0 * k, (r1 if r1 is not None else r0) * k)

    wings = set()
    for s in (-1, 1):
        wings |= poly([pt(1.0 * s, -11.0), pt(5.8 * s, -17.0), pt(9.4 * s, -15.6), pt(8.0 * s, -12.8),
                       pt(8.6 * s, -10.2), pt(6.0 * s, -10.6), pt(5.4 * s, -8.0), pt(1.6 * s, -8.4)])
    for (qx, qy) in wings:
        p.px(qx, qy, MEMBRANE[3] if (qx, qy - 1) in wings else MEMBRANE[5], L)
    outline(p, wings, MEMBRANE[0], MEMBRANE[1], L)
    tail = stk([(2.6, -4.0), (6.4, -2.6), (7.6, -6.2), (6.6, -8.0)], 0.8, 0.5)
    flat(p, tail, HIDE[3], L)
    tx, ty = pt(6.6, -8.4)
    flat(p, poly([(tx - 1.2 * k, ty + 0.4), (tx, ty - 1.8 * k), (tx + 1.2 * k, ty + 0.4)]), HIDE[4], L)
    body = ell(0, -7.0, 3.0, 3.4)
    legs = stk([(-1.4, -4.4), (-3.6, -2.0), (-2.6, -0.6)], 1.3, 1.0) | stk([(1.4, -4.4), (3.0, -2.0), (2.2, -0.6)],
                                                                          1.3, 1.0)
    form(p, body | legs, HIDE, lo=1, hi=5, L=L, depth=1.8)
    outline(p, body | legs | tail, HIDE[0], HIDE[1], L, only_free=True)
    head = ell(-0.3, -13.2, 3.0, 2.8)
    ears = poly([pt(-2.6, -13.8), pt(-5.6, -15.6), pt(-2.8, -12.0)]) | poly([pt(2.0, -13.8), pt(5.0, -15.6),
                                                                              pt(2.2, -12.0)])
    form(p, head | ears, HIDE, lo=1, hi=5, L=L, depth=1.6)
    hn = set()
    for s in (-1, 1):
        hn |= stk([(-0.3 + 1.4 * s, -15.4), (-0.3 + 2.4 * s, -17.6), (-0.3 + 1.6 * s, -19.0)], 0.8, 0.35)
    for (qx, qy) in hn:
        p.px(qx, qy, HORN[5] if (qx, qy - 1) not in hn else HORN[3], L)
    outline(p, head | ears | hn, HIDE[0], HIDE[1], L, only_free=True)
    ex, ey = pt(-1.8, -13.2)
    Lb = p.blink(2) if motion else L
    p.px(int(ex), int(ey), FIRE[6], Lb)
    p.px(int(ex) + 2, int(ey), FIRE[6], Lb)
    p.px(int(ex) - 1, int(ey) + 2, HIDE[0], L)
    p.px(int(ex), int(ey) + 2, HORN[6], L)
    p.px(int(ex) + 1, int(ey) + 2, HIDE[0], L)
    p.px(int(ex) + 2, int(ey) + 2, HORN[6], L)
    # the pitchfork held up before it
    fx, fy = pt(-5.0, -2.0)
    shaft = stroke([(fx, fy), (fx, fy - 15 * k)], 0.5)
    flat(p, shaft, IRON[3], L)
    top = fy - 15 * k
    for dx in (-1.6, 0.0, 1.6):
        prong = stroke([(fx + dx * k, top), (fx + dx * k, top - 3.4 * k)], 0.45)
        for (qx, qy) in prong:
            p.px(qx, qy, LAVA[5] if qy <= top - 2.4 * k else IRON[4], L)
    flat(p, stroke([(fx - 1.6 * k, top), (fx + 1.6 * k, top)], 0.5), IRON[4], L)
    glow(p, fx, top - 3 * k, 3 * k, 2 * k, X["heat"], (0.2, 0.32), L=p.flicker(1) if motion else "haze")
    arm = stk([(-2.2, -9.0), (-4.6, -8.0)], 1.0)
    form(p, arm, HIDE, lo=2, hi=4, L=L, depth=1.0)


# A feather drifting down, tipping one way and the other as it falls: a white vane, its shaded edge, its quill.
FEATHER = (["....aq", "..aab.", ".aab..", "ab...."], ["qa....", ".baa..", "..baa.", "....ba"])


def feather_symbol(p: Pix, frame: int):
    key = ("feather", frame)
    if key not in p.syms:
        pal = {"a": C["white"], "b": LINEN[3], "q": GOLD[4]}
        p.symbol(key, {(i, j): pal[ch] for j, r in enumerate(FEATHER[frame]) for i, ch in enumerate(r) if ch in pal})
    return key


def drift(p: Pix, box, n, night, motion=True, seed=0):
    """Ambient motion in a stretch of sky clear of words, `box` (x0, y0, x1, y1): by day white feathers drifting
    down from heaven, rocking as they fall; by night sparks rising off the fires below, swaying as they climb. Each
    goes round on a slow loop of its own; the still file shows none of them."""
    import random
    if not motion or p.lite:
        return
    x0, y0, x1, y1 = box
    if x1 - x0 < 6 or y1 - y0 < 16 or not p.clear_of_words(x0 - 2, y0 - 2, x1 + 2, y1 + 2):
        return
    rnd = random.Random(seed)
    if night:
        from .sheet import rising
        rising(p, x0 + 1, x1 - 1, y0, y1, n, seed=seed, dur=rnd.uniform(5.0, 7.0))
        return
    frames = [feather_symbol(p, 0), feather_symbol(p, 1)]
    for i in range(n):
        x = rnd.randrange(x0 + 2, max(x0 + 3, x1 - 6))
        steps = rnd.randint(22, 30)
        phase = rnd.uniform(0, 6.3)
        path = [(x + round(3 * math.sin(phase + 2 * math.pi * s_ * 1.5 / steps)),
                 round(y0 + (y1 - 4 - y0) * s_ / (steps - 1))) for s_ in range(steps)]
        p.fly(frames, path, rnd.uniform(9.0, 12.0), z=16, flap=0.9)
