# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the brain feels, on the screen of the console it lives on and in the light of its jar.

Its moods come round in turn, two and a half seconds each: focused, its brows down over its work; happy, blushing;
in love, its eyes hearts; struck by an idea, eyes wide and mouth open, every fold of it lit and lightning down its
wires; and cool, in shades with a glint on them. The screen shows each one's face in its own phosphor, and the light
the jar throws on the wall takes each one's colour: the fluid's aqua, brass, the tissue's pink, the lightning's
violet and the enamel's blue. The still file holds the happy face."""
from __future__ import annotations

import random

from ...holidays.pixel import Pix
from . import brain as BR
from . import lab as LB
from .kit import glow
from .palette import C, RAMP

FLUID, TISSUE, BRASS, ARC, ENAMEL, NIXIE = (RAMP["fluid"], RAMP["tissue"], RAMP["brass"], RAMP["arc"], RAMP["enamel"],
                                            RAMP["nixie"])

LOOP = 12.5
MOODS = ("focused", "happy", "love", "idea", "cool")
STILL = "happy"
# Each face 13 by 7: '#' in the mood's phosphor, 'o' a blush, 'w' a glint.
FACES = {
    "focused": [".##.......##.", "...#.....#...", ".###.....###.", ".#.#.....#.#.", ".###.....###.",
                ".............", "....#####...."],
    "happy": ["..#.......#..", ".#.#.....#.#.", "#...#...#...#", "oo.........oo", "..#.......#..",
              "...#######...", "....#####...."],
    "love": [".##.##.##.##.", "######.######", ".####...####.", "..##.....##..", "oo.........oo",
             "...#.....#...", "....#####...."],
    "idea": [".###.....###.", "#...#...#...#", "#.#.#...#.#.#", "#...#...#...#", ".###.....###.",
             ".....###.....", ".....###....."],
    "cool": ["#############", ".#####.#####.", ".###w#.###w#.", "..###...###..", ".............",
             "........###..", "......###...."],
}


def window(i: int) -> tuple:
    return i / len(MOODS), (i + 1) / len(MOODS)


def ink(mood: str, night: bool) -> str:
    return {"love": TISSUE[5], "idea": NIXIE[5], "cool": ENAMEL[6]}.get(mood, FLUID[5] if not night else FLUID[6])


def face_key(p: Pix, mood: str, night: bool):
    """A face drawn once, to be placed at its size on whatever screen shows it."""
    key = ("face", mood, night)
    if key not in p.syms:
        pal = {"#": ink(mood, night), "o": TISSUE[4], "w": C["white"]}
        p.symbol(key, {(i, j): pal[ch] for j, row in enumerate(FACES[mood]) for i, ch in enumerate(row) if ch in pal})
    return key


def face(night: bool, motion: bool):
    """A screen showing the brain's face in each mood in turn, for `lab.jar` to set into its console."""
    def draw(p: Pix, x, y, w, h):
        LB.screen(p, x, y, w, h, night)
        for i, mood in enumerate(MOODS):
            t0, t1 = window(i)
            if motion and not p.lite:
                L = p.seq(f"face{i}", t0, t1, LOOP, keep=mood == STILL, z=2)
            elif mood == STILL:
                L = "base"
            else:
                continue
            art = FACES[mood]
            sc = 2 if (w - 2 >= 2 * len(art[0]) and h - 2 >= 2 * len(art)) else 1
            fx = x + (w - sc * len(art[0])) // 2
            fy = y + (h - sc * len(art)) // 2
            p.use(face_key(p, mood, night), fx, fy, L, scale=sc)
    return draw


def light(p: Pix, cx, cy, rx, ry, night: bool, motion: bool):
    """The light the jar throws on the wall, in the colour of each mood in turn; the still file keeps the happy
    one's."""
    colours = {"focused": FLUID[4], "happy": BRASS[5], "love": TISSUE[4], "idea": ARC[5], "cool": ENAMEL[5]}
    alphas = (0.11, 0.2) if not night else (0.1, 0.2)
    for i, mood in enumerate(MOODS):
        t0, t1 = window(i)
        if motion and not p.lite:
            L = p.seq(f"mood{i}", t0, t1, LOOP, keep=mood == STILL, z=-14)
        elif mood == STILL:
            L = "haze"
        else:
            continue
        glow(p, cx, cy, rx, ry, colours[mood], alphas, L=L, shape=True)


def idea(p: Pix, parts: dict, night: bool, motion: bool):
    """The idea striking: every fold lit at once, and lightning down the wires from the cap to the electrodes."""
    if not motion or p.lite:
        return
    t0, _ = window(MOODS.index("idea"))
    L = p.seq("idea", t0, t0 + 0.06, LOOP, z=9)
    bx, by, k = parts["brain"]
    BR.flash(p, bx, by, k, night, L)
    rnd = random.Random(3)
    for (ex, ey) in parts["electrodes"]:
        LB.strike(p, LB.bolt(rnd, ex + rnd.uniform(-3, 3), parts["fluid"] + 1, ex, ey - 1, jag=1.4), night, L)
