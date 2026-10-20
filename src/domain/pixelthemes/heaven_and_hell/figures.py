# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The set's two great figures, each the other's twin: the archangel of heaven, armoured in gold over white,
wings of white feathers raised behind it, a halo over its head and a sword of light; and the demon of hell,
standing where the angel stood, bat wings raised where the angel's were, horns where its halo was, a trident where
its sword was and a ball of hellfire in the hand that held the shield.

Every figure is drawn from shapes in its own units, its feet on the ground at (0, 0) and the crown of its head
about 57 units up, scaled by `k` to the room it has, so the same angel stands on a phone and towers over a section.
Each stands in one of two poses: on guard, its weapon held high (`raised`), or keeping vigil, its weapon planted
before it or beside it (`planted`)."""
from __future__ import annotations

import math

from ...holidays.pixel import Pix
from .kit import curve, ellipse, flat, form, glow, outline, poly, spline, stroke
from .palette import C, RAMP, X

GOLD, LINEN, PEARL, AZURE, STEEL = RAMP["gold"], RAMP["linen"], RAMP["pearl"], RAMP["azure"], RAMP["steel"]
HIDE, HORN, MEMBRANE, IRON, FIRE, LAVA = (RAMP["hide"], RAMP["horn"], RAMP["membrane"], RAMP["iron"], RAMP["fire"],
                                          RAMP["lava"])
SHOULDER = (5.0, -44.0)
HEAD = (0.0, -51.6)          # the middle of the face
HEAD_R = (3.9, 4.5)


class Body:
    """A figure's place and size: its units turned into the canvas's cells, and a wing's spread about its
    shoulder."""

    def __init__(self, cx, foot, k=1.0):
        self.cx, self.foot, self.k = cx, foot, k
        self.turn = None           # (side, angle): the wing being drawn, swung out about its shoulder

    def unit(self, x, y):
        if self.turn:
            s, a = self.turn
            ox, oy = SHOULDER[0] * s, SHOULDER[1]
            ca, sa = math.cos(a * s), math.sin(a * s)
            x, y = ox + (x - ox) * ca - (y - oy) * sa, oy + (x - ox) * sa + (y - oy) * ca
        return x, y

    def pt(self, x, y):
        x, y = self.unit(x, y)
        return (self.cx + x * self.k, self.foot + y * self.k)

    def pts(self, points):
        return [self.pt(x, y) for x, y in points]

    def poly(self, points):
        return poly(self.pts(points))

    def ellipse(self, x, y, rx, ry):
        cx, cy = self.pt(x, y)
        return ellipse(cx, cy, rx * self.k, ry * self.k)

    def stroke(self, points, r0, r1=None):
        """A limb, a quill or a blade: never thinner than a cell's half, so at a phone's size it still shows."""
        r1 = r0 if r1 is None else r1
        return stroke(self.pts(points), max(0.55, r0 * self.k), max(0.5, r1 * self.k))


# --------------------------------------------------------------------------- wings
# Each flight feather of a raised wing, (root, bend, tip) in the figure's units for its left wing (the viewer's right),
# outermost first: the primaries hang from the hand of the wing, fanning out and down, the secondaries from its
# forearm, shorter toward the body, so the trailing edge sweeps up from the outer tip to the waist.
FLIGHT = (
    ((26.5, -57.0), (29.5, -42.0), (30.5, -27.5)),
    ((24.5, -60.5), (27.0, -44.0), (27.4, -23.5)),
    ((22.0, -62.5), (24.0, -45.0), (24.0, -21.5)),
    ((19.5, -63.0), (20.8, -46.0), (20.4, -21.5)),
    ((17.0, -62.0), (17.6, -46.0), (16.9, -23.5)),
    ((14.6, -60.0), (14.6, -46.0), (13.6, -26.0)),
    ((12.2, -57.4), (11.8, -46.0), (10.6, -29.0)),
    ((9.8, -54.0), (9.2, -45.0), (8.0, -32.0)),
    ((7.4, -50.0), (6.8, -44.0), (5.8, -35.0)),
)
# The arch of the wing, its leading edge: from the shoulder up over the elbow to the wrist and out to the hand.
ARCH = ((4.5, -44.0), (7.0, -52.5), (11.0, -59.0), (16.0, -63.5), (21.0, -65.0), (25.0, -63.0), (28.0, -58.0))
# The bat wing, its twin: the arm from the shoulder over the elbow to the wrist, the four fingers' tips, and the
# root of its skin at the waist.
BAT_ARM = ((5.0, -44.0), (13.0, -58.0), (21.0, -66.0))
BAT_TIPS = ((28.5, -58.0), (30.0, -41.0), (25.5, -27.0), (15.0, -22.0))
BAT_ROOT = (6.0, -30.0)
# Wings raised high, the guardian's on a cover sheet: the arch rising steeply from the shoulder to a wrist above the
# halo, the flight feathers hanging close down its outside, so the pair stands tall and narrow behind the figure.
FLIGHT_HIGH = (
    ((20.0, -66.0), (22.6, -52.0), (22.9, -35.5)),
    ((18.6, -70.0), (20.8, -54.0), (20.6, -30.5)),
    ((16.6, -72.4), (18.4, -55.0), (17.8, -28.2)),
    ((14.3, -72.2), (15.7, -55.0), (14.9, -27.6)),
    ((12.0, -69.2), (13.0, -53.0), (12.2, -29.6)),
    ((10.0, -64.6), (10.6, -51.0), (9.9, -32.6)),
    ((8.2, -59.6), (8.4, -49.0), (7.9, -35.8)),
    ((6.6, -53.6), (6.6, -46.0), (6.1, -38.8)),
)
ARCH_HIGH = ((4.5, -44.0), (6.5, -53.0), (9.5, -62.0), (12.5, -69.0), (15.5, -73.4), (18.6, -71.6), (20.6, -66.4))
BAT_ARM_HIGH = ((5.0, -44.0), (10.2, -60.0), (15.6, -73.0))
BAT_TIPS_HIGH = ((21.6, -64.0), (23.6, -49.0), (21.4, -35.0), (12.8, -26.5))
BAT_ROOT_HIGH = (6.0, -30.0)
FEATHERS = {"raised": (FLIGHT, ARCH), "high": (FLIGHT_HIGH, ARCH_HIGH)}
BATS = {"raised": (BAT_ARM, BAT_TIPS, BAT_ROOT), "high": (BAT_ARM_HIGH, BAT_TIPS_HIGH, BAT_ROOT_HIGH)}


def feathered_wing(p: Pix, b: Body, side: int, spread=0.0, L="base", style="raised"):
    """A wing of white feathers raised behind a figure on `side` (-1 its right, the viewer's left; 1 its left),
    in its `style`, swung out by `spread` radians: its flight feathers hanging from its arch, fanning out and down,
    each a quill white at its root and falling into a cool shade toward its tip, its trailing edge parted from the
    next by a line of shade, the inner feathers in the shade of the body; over their roots the coverts, two rows of
    small round feathers scale on scale; and the arch's leading edge catching heaven's light, gilt along its top."""
    s = side
    flight, arch = FEATHERS[style]
    b.turn = (s, spread)
    sx = (lambda pts: [(x * s, y) for x, y in pts])
    every = set()
    quills = []
    for i, (root, bend, tip) in enumerate(flight):
        quills.append(b.stroke(curve(sx([root, bend, tip]), 10), 2.6 - 0.12 * i, 1.35))
    for i, cells in enumerate(quills):
        mine = cells - set().union(*quills[i + 1:]) if i + 1 < len(quills) else cells
        shade = i >= len(quills) - 3
        ys = [y for _, y in cells]
        y0, y1 = min(ys), max(ys)
        for (x, y) in mine:
            trail = (x + s, y) not in cells if s > 0 else (x - 1, y) not in cells
            t = (y - y0) / max(1, y1 - y0)
            if trail:
                c = LINEN[3] if t < 0.8 else LINEN[2]
            elif shade:
                c = LINEN[4] if t < 0.7 else LINEN[3]
            else:
                c = LINEN[5] if t < 0.62 else LINEN[4]
            p.px(x, y, c, L)
        every |= cells
    for cells in quills:
        yb = max(y for _, y in cells)
        for (x, y) in cells:
            if y == yb and (x, y + 1) not in every:
                p.px(x, y, LINEN[2], L)
    for row, (off, r) in enumerate(((3.2, 2.3), (6.6, 2.0))):
        pts = spline(sx([arch[1], arch[3], arch[5], arch[6]]), 3)
        for (x, y) in (pts[1:] if row == 0 else pts[1:-1]):
            cx, cy = b.pt(x, y + off)
            c = ellipse(cx, cy, r * b.k, (r + 0.6) * b.k)
            for (qx, qy) in c:
                top = (qx, qy - 1) not in c
                low = (qx, qy + 1) not in c
                p.px(qx, qy, PEARL[6] if top else PEARL[3] if low else PEARL[5], L)
            every |= c
    edge = b.stroke(spline(sx(list(arch)), 3), 1.5, 1.1)
    for (x, y) in edge:
        p.px(x, y, GOLD[6] if (x, y - 1) not in edge else C["white"], L)
    every |= edge
    b.turn = None
    outline(p, every, LINEN[1], LINEN[2], L)
    return every


def bat_wing(p: Pix, b: Body, side: int, spread=0.0, L="base", style="raised"):
    """A bat's wing raised behind a demon on `side`, the twin of the angel's, swung out as far: its arm rising
    from the shoulder over the elbow to the wrist, four long fingers spreading from the wrist, and the skin
    stretched between them, its trailing edge scalloped between their tips, darkest toward the body."""
    s = side
    arm_, tips_, root_ = BATS[style]
    b.turn = (s, spread)
    arm = [(x * s, y) for x, y in arm_]
    tips = [(x * s, y) for x, y in tips_]
    wrist = arm[-1]
    root = (root_[0] * s, root_[1])
    pts = list(arm) + [tips[0]]
    for a, c in zip(tips, tips[1:]):
        mx, my = (a[0] + c[0]) / 2, (a[1] + c[1]) / 2
        pts += [(mx + (wrist[0] - mx) * 0.3, my + (wrist[1] - my) * 0.3), c]
    pts += [((tips[-1][0] + root[0]) / 2, -24.5), root]
    skin = b.poly(pts)
    ux, uy = b.pt(*wrist)
    for (x, y) in skin:
        d = math.hypot(x + 0.5 - ux, y + 0.5 - uy) / (30 * b.k)
        p.px(x, y, MEMBRANE[4 if d > 0.82 else 3 if d > 0.42 else 2], L)
    bones = [b.stroke(arm, 1.6, 1.2)]
    for t_ in tips:
        bones.append(b.stroke([wrist, ((wrist[0] + t_[0]) / 2 + 1.2 * s, (wrist[1] + t_[1]) / 2 - 0.5), t_],
                              0.95, 0.5))
    bone_cells = set().union(*bones)
    for (x, y) in bone_cells:
        lit = (x, y - 1) not in bone_cells
        p.px(x, y, HIDE[4] if lit else HIDE[2], L)
    claw = b.pt(wrist[0] + 0.5 * s, wrist[1] - 2.5)
    p.px(int(claw[0]), int(claw[1]), HORN[5], L)
    p.px(int(claw[0]), int(claw[1]) + 1, HORN[3], L)
    b.turn = None
    cells = skin | bone_cells
    outline(p, cells, MEMBRANE[0], MEMBRANE[2], L)
    return cells


N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def backlight(layer: dict, drawn: set, colour: str, from_below: bool, skip=(), turn=0.35):
    """The light from behind a figure caught along its silhouette, the pixel artist's rim: a line of it just
    inside the figure's outline, where its outer edge turns toward the light, and nowhere in the gaps between its
    limbs. By night the fire behind the demon lights its sides and its underside; by day heaven's glory lights the
    angel's crown and sides. `skip` are cells it leaves alone, a weapon's."""
    edge = {q for q in drawn if any((q[0] + dx, q[1] + dy) not in drawn for dx, dy in N4)}
    inner = {q for q in drawn - edge if any((q[0] + dx, q[1] + dy) in edge for dx, dy in N4)}
    for (x, y) in inner - set(skip):
        nx = ny = 0
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if (x + dx, y + dy) not in drawn:
                    nx += dx
                    ny += dy
        n = math.hypot(nx, ny)
        if n == 0:
            continue
        nx, ny = nx / n, ny / n
        # only an edge that looks out on open air, not across a gap between limbs
        if any((round(x + nx * d), round(y + ny * d)) in drawn for d in (3, 4, 5)):
            continue
        if (from_below and ny > -turn) or (not from_below and ny < turn):
            layer[(x, y)] = colour


def pair(p: Pix, b: Body, wing, spread=0.0, style="raised", rim=None):
    """A pair of wings behind a figure: its left wing drawn once and placed twice, the right as its mirror, both
    behind everything else of it. A wing is shaded the same on either side of the body, so its mirror is its
    right wing as it would be drawn."""
    b.cx = round(b.cx)
    q = Pix(p.w, p.h, lite=p.lite)
    wing(q, b, 1, spread, "base", style)
    cells = q.layers["base"]
    if not cells:
        return
    if rim:
        colour, below, *rest = rim
        backlight(cells, set(cells), colour, below, *(rest or []))
    # what the pair covers, both wings, for whoever measures the figure
    p.winged = getattr(p, "winged", set()) | set(cells) | {(2 * b.cx - 1 - x, y) for x, y in cells}
    sid = p.symbol(("wings", len(p.syms)), dict(cells))
    markup = f'<use href="#{sid}"/><use href="#{sid}" transform="matrix(-1 0 0 1 {2 * b.cx} 0)"/>'
    p.raw(-0.5, markup, markup)


# --------------------------------------------------------------------------- heads
def head_cells(b: Body) -> set:
    return b.ellipse(HEAD[0], HEAD[1], *HEAD_R)


def angel_head(p: Pix, b: Body, skin, hair, L="base"):
    """An angel's head: the face shaded on its skin ramp, its eyes, the shade under its nose and its mouth, and
    its hair falling in curls to its shoulders, a fringe over the brow."""
    k = b.k
    hx, hy = HEAD
    hair_cells = b.ellipse(hx, hy - 1.3, 4.9, 5.0) | b.poly([(-5.0, hy - 1.5), (-5.6, hy + 5.6), (-3.4, hy + 6.2),
                                                              (-3.0, hy + 1.0)]) \
        | b.poly([(5.0, hy - 1.5), (5.6, hy + 5.6), (3.4, hy + 6.2), (3.0, hy + 1.0)])
    form(p, hair_cells, hair, lo=1, hi=5, L=L, depth=2.0)
    for (x, y) in hair_cells:
        if (x * 3 + y * 5) % 7 == 0:
            p.px(x, y, hair[2], L)                        # the curls
    outline(p, hair_cells, hair[0], hair[1], L)
    head = head_cells(b)
    form(p, head, skin, lo=2, hi=5, L=L, depth=2.2)
    fringe = b.ellipse(hx, hy - 3.6, 4.0, 1.9)
    form(p, fringe, hair, lo=2, hi=6, L=L, depth=1.2)
    features(p, b, skin, False, L)


def features(p: Pix, b: Body, skin, demon: bool, L="base", motion=True):
    k = b.k
    cx, cy = b.pt(*HEAD)
    cx, cy = round(cx), round(cy + 0.4 * k)
    ex = max(1, round(1.6 * k))
    if demon:
        Lb = p.blink(1) if motion else L
        for dx in (-ex - 1, ex):
            p.px(cx + dx, cy, FIRE[6], Lb)
            p.px(cx + dx + (1 if dx < 0 else -1), cy, FIRE[4], Lb)
            p.px(cx + dx, cy - 1, HIDE[1], L)               # the brow drawn down over it
            p.px(cx + dx + (1 if dx < 0 else -1), cy - 1, HIDE[0], L)
        glow(p, cx, cy + 0.5, 4 * k, 1.8 * k, X["heat"], (0.25, 0.4), L=Lb)
    else:
        for dx in (-ex - 1, ex):
            p.px(cx + dx, cy, RAMP["brown"][1], L)
            if k >= 1.05:
                p.px(cx + dx, cy - 1, skin[2], L)            # the lids
            if k >= 1.25:
                p.px(cx + dx + (1 if dx < 0 else 0), cy - 2, skin[1], L)     # the brows
                p.px(cx + dx + (-1 if dx < 0 else 1), cy, C["white"], L)     # the whites, toward the sides
    p.px(cx - 1 if not demon else cx, cy + max(1, round(1.3 * k)), skin[2], L)      # the shade under the nose
    my = cy + max(2, round(2.5 * k))
    if demon:
        for dx in range(-2, 2):
            p.px(cx + dx, my, HIDE[0], L)
        p.px(cx - 2, my + 1, HORN[6], L)                    # fangs
        p.px(cx + 1, my + 1, HORN[6], L)
    else:
        p.px(cx - 1, my, skin[1], L)
        p.px(cx, my, skin[1], L)
        if k >= 1.05:
            p.px(cx - 3, my - 1, RAMP["rose"][4], L)          # the flush of its cheeks
            p.px(cx + 2, my - 1, RAMP["rose"][4], L)


def demon_head(p: Pix, b: Body, L="base", motion=True):
    """A demon's head, the angel's twin: its hide shaded red, its ears pointed, its brow drawn down over burning
    eyes that blink, a mouth set with fangs, and its horns curling up out of its brow."""
    hx, hy = HEAD
    ears = b.poly([(-3.4, hy - 0.8), (-6.8, hy - 3.6), (-3.8, hy + 1.6)]) | \
        b.poly([(3.4, hy - 0.8), (6.8, hy - 3.6), (3.8, hy + 1.6)])
    form(p, ears, HIDE, lo=1, hi=4, L=L, depth=1.0)
    head = head_cells(b) | b.poly([(-2.6, hy + 3.4), (2.6, hy + 3.4), (1.2, hy + 5.4), (-1.2, hy + 5.4)])
    form(p, head, HIDE, lo=1, hi=5, L=L, depth=2.2)
    outline(p, head | ears, HIDE[0], HIDE[1], L, only_free=True)
    features(p, b, HIDE, True, L, motion)
    horns(p, b, L)


def halo(p: Pix, b: Body, motion=True, L="base"):
    """A halo of gold over an angel's head, seen a little from below: a ring of light, glinting, a glow round it."""
    cx, cy = b.pt(HEAD[0], HEAD[1] - 8.2)
    rx, ry = 5.8 * b.k, 1.8 * b.k
    ring = ellipse(cx, cy, rx, ry) - ellipse(cx, cy + 0.15 * b.k, rx - 1.3, max(0.6, ry - 1.0))
    for (x, y) in ring:
        left = x + 0.5 < cx
        up = y + 0.5 < cy
        p.px(x, y, GOLD[6] if (left and up) else GOLD[5] if left else GOLD[4] if up else GOLD[3], L)
    glow(p, cx, cy, rx + 3, ry + 3, X["glory"], (0.18, 0.3, 0.45))
    gx, gy = int(cx - rx * 0.55), int(cy - ry * 0.4)
    Lt = p.twinkle(1) if motion else L
    p.px(gx, gy, C["white"], Lt)
    if b.k >= 1.2:
        for dx, dy in ((1, 0), (-1, 0), (0, -1), (0, 1)):
            p.px(gx + dx, gy + dy, GOLD[6], Lt)


def horns(p: Pix, b: Body, L="base"):
    """A demon's horns, curling up and out of its brow and back in at their points, ridged, lit along their
    upper edges."""
    hx, hy = HEAD
    cells = set()
    for s in (-1, 1):
        path = curve([(2.0 * s, hy - 3.2), (6.0 * s, hy - 6.0), (8.2 * s, hy - 11.0), (5.6 * s, hy - 14.6)], 10)
        h = b.stroke(path, 1.6, 0.35)
        cells |= h
        for (x, y) in h:
            ridge = (y * 2 + x) % 3 == 0
            lit = (x - 1, y) not in h or (x, y - 1) not in h
            p.px(x, y, HORN[5] if lit else HORN[2] if ridge else HORN[3], L)
    outline(p, cells, HORN[0], HORN[1], L)


# --------------------------------------------------------------------------- the archangel
def archangel(p: Pix, cx, foot, k=1.0, motion=True, L="base", skin="skin1", hair="blond", pose="raised",
              spread=0.0, wings="raised", rim=False):
    """The archangel on guard at heaven's gate: wings of white feathers raised behind it, armour of gold over a
    tunic of white with an azure cloak, and a sword of light. On guard (`raised`) it holds the sword high in its
    right hand and a round shield of gold on its left arm; keeping vigil (`planted`) it rests both hands on the
    pommel of the sword planted point down before it, the blade shining."""
    b = Body(cx, foot, k)
    SK, HR = RAMP[skin], RAMP[hair]
    light = (GOLD[6], False) if rim else None
    pair(p, b, feathered_wing, spread, wings, rim=light)
    before = dict(p.layers.get(L, {}))
    cloak = b.poly([(-6.0, -44.5), (6.0, -44.5), (9.6, -10), (5.4, -7.5), (0, -9), (-5.4, -7.5), (-9.6, -10)])
    form(p, cloak, AZURE, lo=1, hi=4, L=L, depth=2.2)
    outline(p, cloak, AZURE[0], AZURE[1], L)
    for s_ in (-1, 1):
        leg = b.stroke([(2.2 * s_, -24), (2.6 * s_, -13), (2.4 * s_, -1.5)], 1.7, 1.3)
        form(p, leg, SK, lo=1, hi=4, L=L, depth=1.2)
        greave = {(x, y) for (x, y) in leg if b.pt(0, -14)[1] <= y < b.pt(0, -2)[1]}
        form(p, greave, GOLD, lo=2, hi=5, L=L, depth=1.0)
        outline(p, leg, SK[0], SK[1], L, only_free=True)
        sole = b.poly([(0.8 * s_, -1.6), (4.2 * s_, -1.6), (4.6 * s_, 0), (0.6 * s_, 0)])
        flat(p, sole, SK[3], L)
        for (x, y) in sole:
            if (x, y + 1) not in sole:
                p.px(x, y, GOLD[2], L)
    tunic = b.poly([(-4.8, -34.5), (4.8, -34.5), (6.8, -19.4), (3.6, -18.4), (0, -19.4), (-3.6, -18.4), (-6.8, -19.4)])
    form(p, tunic, LINEN, lo=2, hi=6, L=L, depth=2.4)
    for fx in (-3.0, 0.2, 3.2):
        x0, y0 = b.pt(fx * 0.55, -31)
        x1, y1 = b.pt(fx * 1.25, -19.8)
        for t in range(0, 30):
            u = t / 29
            q = (int(x0 + (x1 - x0) * u), int(y0 + (y1 - y0) * u))
            if q in tunic:
                p.px(q[0], q[1], LINEN[3], L)
    for (x, y) in tunic:
        if (x, y + 1) not in tunic:
            p.px(x, y, GOLD[4], L)
    outline(p, tunic, LINEN[1], LINEN[2], L)
    chest = b.poly([(-5.6, -45), (5.6, -45), (5.0, -38.5), (4.4, -34.0), (-4.4, -34.0), (-5.0, -38.5)])
    form(p, chest, GOLD, lo=2, hi=6, L=L, depth=2.6)
    mx = b.pt(0, 0)[0]
    for (x, y) in chest:
        if abs(x + 0.5 - mx) < 0.5 and y > b.pt(0, -43.5)[1]:
            p.px(x, y, GOLD[3], L)
    belt = b.poly([(-4.8, -35.6), (4.8, -35.6), (4.8, -33.8), (-4.8, -33.8)])
    flat(p, belt, AZURE[2], L)
    for (x, y) in belt:
        if (x, y - 1) not in belt:
            p.px(x, y, AZURE[4], L)
    outline(p, chest, GOLD[0], GOLD[3], L)
    neck = b.poly([(-1.3, -47.8), (1.3, -47.8), (1.3, -44.6), (-1.3, -44.6)])
    form(p, neck, SK, lo=1, hi=4, L=L, depth=1.0)
    if pose == "planted":
        for s_ in (-1, 1):
            arm = b.stroke([(6.4 * s_, -43.5), (6.8 * s_, -38.0), (1.6 * s_, -34.2)], 1.7, 1.4)
            form(p, arm, SK, lo=1, hi=4, L=L, depth=1.2)
            outline(p, arm, SK[0], SK[1], L, only_free=True)
    else:
        arm_l = b.stroke([(6.4, -43.5), (8.6, -37.5), (7.2, -32)], 1.7, 1.4)
        form(p, arm_l, SK, lo=1, hi=4, L=L, depth=1.2)
        outline(p, arm_l, SK[0], SK[1], L, only_free=True)
        shield(p, b, (9.6, -33.5), L)
    for s_ in (-1, 1):
        pa = b.ellipse(6.1 * s_, -44.2, 2.7, 2.1)
        form(p, pa, GOLD, lo=2, hi=6, L=L, depth=1.4)
        outline(p, pa, GOLD[0], GOLD[2], L, only_free=True)
    held = dict(p.layers.get(L, {}))
    if pose == "planted":
        sword(p, b, (0.0, -33.4), motion, L, down=True)
        for s_ in (-1, 1):
            hand = b.ellipse(1.3 * s_, -33.6, 1.5, 1.3)
            form(p, hand, SK, lo=2, hi=5, L=L, depth=1.0)
    else:
        arm_r = b.stroke([(-6.4, -43.5), (-10.5, -48.5), (-10.2, -55.5)], 1.7, 1.4)
        form(p, arm_r, SK, lo=1, hi=4, L=L, depth=1.2)
        outline(p, arm_r, SK[0], SK[1], L, only_free=True)
        sword(p, b, (-10.2, -56.2), motion, L, blade=19 if wings == "high" else 26)
    weapon = {q for q, c in p.layers[L].items() if held.get(q) != c}
    angel_head(p, b, SK, HR, L)
    if light:
        layer = p.layers[L]
        backlight(layer, {q for q, c in layer.items() if before.get(q) != c}, *light, skip=weapon)
    halo(p, b, motion, L)
    return b


def shield(p: Pix, b: Body, at, L="base"):
    """A round shield of gold on the angel's arm, a sun of gold rays about a boss of pearl."""
    k = b.k
    sh = b.ellipse(at[0], at[1], 5.4, 6.0)
    form(p, sh, GOLD, lo=1, hi=6, L=L, depth=2.8)
    sx, sy = b.pt(*at)
    for i in range(8):
        a = math.radians(i * 45 + 22.5)
        for rr in (2.4, 3.4):
            qx, qy = int(sx + math.cos(a) * rr * k), int(sy + math.sin(a) * rr * k)
            p.px(qx, qy, GOLD[6] if -math.cos(a) - math.sin(a) > 0 else GOLD[2], L)
    flat(p, ellipse(sx, sy, 1.6 * k, 1.6 * k), PEARL[6], L)
    outline(p, sh, GOLD[0], GOLD[2], L)


def sword(p: Pix, b: Body, hand, motion=True, L="base", down=False, blade=26):
    """A sword of light: a hilt of gold, a guard swept up at its ends, and a long blade of white light with a
    glow along it; held high, or planted point down with the hilt at `hand`."""
    hx, hy = hand
    d = 1 if down else -1
    grip = b.stroke([(hx, hy - 2.5 * d), (hx, hy + 1.5 * d)], 0.8)
    flat(p, grip, GOLD[2], L)
    gy = hy + 2.0 * d
    guard = b.stroke([(hx - 3.8, gy - 0.9), (hx - 2, gy), (hx + 2, gy), (hx + 3.8, gy - 0.9)] if not down else
                     [(hx - 3.8, gy + 0.9), (hx - 2, gy), (hx + 2, gy), (hx + 3.8, gy + 0.9)], 0.75)
    for (x, y) in guard:
        p.px(x, y, GOLD[5] if (x, y - 1) not in guard else GOLD[3], L)
    flat(p, b.ellipse(hx, hy - 3.3 * d, 1.1, 1.1), GOLD[5], L)
    tip_y = hy + 27 * d if down else hy - blade
    base_y = gy + 0.8 * d
    blade = b.poly([(hx - 1.2, base_y), (hx + 1.2, base_y), (hx + 1.0, tip_y - 3 * d), (hx, tip_y),
                    (hx - 1.0, tip_y - 3 * d)])
    cx0 = b.pt(hx, 0)[0]
    for (x, y) in blade:
        p.px(x, y, C["white"] if x + 0.5 < cx0 + 0.4 else STEEL[5], L)
    if down:
        for (x, y) in blade:
            if (x - 1, y) not in blade or (x + 1, y) not in blade:
                p.px(x, y, GOLD[3] if (x + 1, y) not in blade else GOLD[5], L)
        outline(p, blade, GOLD[2], GOLD[3], L)
    else:
        outline(p, blade, GOLD[3], GOLD[5], L)
    bx, by = b.pt(hx, (base_y + tip_y) / 2)
    glow(p, bx, by, 4 * b.k, 14 * b.k, X["glory"], (0.12, 0.22, 0.34))
    if not down:
        tx, ty = b.pt(hx, tip_y)
        Lt = p.twinkle(0) if motion else L
        p.px(int(tx), int(ty) - 1, C["white"], Lt)
        for dx, dy in ((1, 0), (-1, 0), (0, -1)):
            p.px(int(tx) + dx, int(ty) - 1 + dy, GOLD[6], Lt)


# --------------------------------------------------------------------------- the demon
def demon(p: Pix, cx, foot, k=1.0, motion=True, L="base", pose="raised", spread=0.0, wings="raised", rim=False):
    """The demon at hell's gate, standing where the angel stood: bat wings raised where its wings were, horns where
    its halo was, its red hide bare and hard with muscle, a belt of iron and a loincloth of black, hooves, a tail
    with a barbed tip, a trident of black iron red-hot at its points, and in its other hand a ball of hellfire
    whose light falls on it from below. On guard (`raised`) it holds the trident high; keeping its watch
    (`planted`) it grips the trident planted beside it."""
    b = Body(cx, foot, k)
    light = (LAVA[3], True) if rim else None
    pair(p, b, bat_wing, spread, wings, rim=(LAVA[3], True, (), -0.2) if rim else None)
    before = dict(p.layers.get(L, {}))
    tail = b.stroke(curve([(2, -24), (10, -16), (13, -6), (17, -10)], 14), 1.3, 0.6)
    form(p, tail, HIDE, lo=1, hi=3, L=L, depth=1.0)
    tx, ty = b.pt(17, -10)
    barb = poly([(tx - 0.5, ty - 2.8 * k), (tx + 2.8 * k, ty + 0.3), (tx - 0.4, ty + 2.0 * k), (tx - 1.2, ty)])
    flat(p, barb, HIDE[4], L)
    outline(p, tail | barb, HIDE[0], HIDE[1], L, only_free=True)
    for s in (-1, 1):
        thigh = b.stroke([(2.8 * s, -30), (4.9 * s, -18.5), (3.4 * s, -9)], 2.8, 1.8)
        shin = b.stroke([(3.4 * s, -9), (4.5 * s, -3), (4.1 * s, -1)], 1.5, 1.2)
        leg = thigh | shin
        form(p, leg, HIDE, lo=1, hi=4, L=L, depth=1.8)
        outline(p, leg, HIDE[0], HIDE[1], L, only_free=True)
        hoof = b.poly([(2.4 * s, -1.6), (5.8 * s, -1.6), (6.2 * s, 0), (2.0 * s, 0)])
        flat(p, hoof, IRON[1], L)
        for (x, y) in hoof:
            if (x, y - 1) not in hoof:
                p.px(x, y, IRON[4], L)
    cloth = b.poly([(-3.2, -31), (3.2, -31), (3.0, -17.5), (1.6, -15.6), (0.2, -17.2), (-1.4, -15.2), (-3.0, -17.4)])
    form(p, cloth, IRON, lo=1, hi=3, L=L, depth=1.4)
    outline(p, cloth, IRON[0], IRON[0], L, only_free=True)
    belt = b.poly([(-5.2, -32.6), (5.2, -32.6), (5.2, -30.2), (-5.2, -30.2)])
    form(p, belt, IRON, lo=2, hi=5, L=L, depth=0.8)
    bx_, by_ = b.pt(0, -31.4)
    p.px(int(bx_) - 1, int(by_), RAMP["bone"][5], L)
    p.px(int(bx_), int(by_), RAMP["bone"][4], L)
    torso = b.poly([(-6.0, -45), (6.0, -45), (5.6, -39.5), (4.4, -33), (-4.4, -33), (-5.6, -39.5)])
    form(p, torso, HIDE, lo=1, hi=4, L=L, depth=2.4)
    for s in (-1, 1):
        pec = b.ellipse(2.6 * s, -41.6, 2.8, 2.0)
        form(p, pec, HIDE, lo=2, hi=5, L=L, depth=1.4)
        for (x, y) in pec:
            if (x, y + 1) not in pec:
                p.px(x, y, HIDE[1], L)
        for row in (-37.6, -35.2):
            ax, ay = b.pt(1.6 * s, row)
            p.px(int(ax), int(ay), HIDE[2], L)
            p.px(int(ax) + (1 if s < 0 else -1), int(ay), HIDE[2], L)
    outline(p, torso, HIDE[0], HIDE[1], L)
    for s in (-1, 1):
        pa = b.ellipse(6.2 * s, -44.2, 2.8, 2.2)
        form(p, pa, IRON, lo=1, hi=5, L=L, depth=1.4)
        spike = b.poly([(5.2 * s, -45.4), (7.6 * s, -45.6), (8.8 * s, -50.0)])
        flat(p, spike, IRON[5], L)
        outline(p, pa | spike, IRON[0], IRON[1], L, only_free=True)
    neck = b.poly([(-1.8, -47.8), (1.8, -47.8), (2.0, -44.6), (-2.0, -44.6)])
    form(p, neck, HIDE, lo=1, hi=3, L=L, depth=1.0)
    arm_l = b.stroke([(6.6, -43.5), (9.0, -37.0), (8.4, -31.5)], 2.0, 1.6)
    form(p, arm_l, HIDE, lo=1, hi=4, L=L, depth=1.3)
    outline(p, arm_l, HIDE[0], HIDE[1], L, only_free=True)
    hellfire(p, b, (9.4, -33.6), motion, L)
    if pose == "planted":
        arm_r = b.stroke([(-6.6, -43.5), (-10.0, -38.5), (-10.6, -35.5)], 2.0, 1.6)
        form(p, arm_r, HIDE, lo=1, hi=4, L=L, depth=1.3)
        outline(p, arm_r, HIDE[0], HIDE[1], L, only_free=True)
        held = dict(p.layers.get(L, {}))
        trident(p, b, (-11.0, -36.0), motion, L, planted=True)
        weapon = {q for q, c in p.layers[L].items() if held.get(q) != c}
    else:
        arm_r = b.stroke([(-6.6, -43.5), (-10.6, -48.5), (-10.2, -55.5)], 2.0, 1.6)
        form(p, arm_r, HIDE, lo=1, hi=4, L=L, depth=1.3)
        outline(p, arm_r, HIDE[0], HIDE[1], L, only_free=True)
        held = dict(p.layers.get(L, {}))
        trident(p, b, (-10.2, -56.2), motion, L, reach=13 if wings == "high" else 20)
        weapon = {q for q, c in p.layers[L].items() if held.get(q) != c}
    demon_head(p, b, L, motion)
    if light:
        layer = p.layers[L]
        backlight(layer, {q for q, c in layer.items() if before.get(q) != c}, *light, skip=weapon)
    return b


def trident(p: Pix, b: Body, hand, motion=True, L="base", planted=False, reach=20):
    """A trident of black iron, its three points red-hot: held high, or planted on the rock beside the demon."""
    hx, hy = hand
    low = 0.0 if planted else hy + 9
    head_y = (hy - 21) if planted else hy - reach
    shaft = b.stroke([(hx, low), (hx, head_y)], 0.6)
    for (x, y) in shaft:
        p.px(x, y, IRON[4] if (x - 1, y) not in shaft else IRON[2], L)
    prongs = [b.stroke([(hx - 3.6, head_y - 0.5), (hx - 3.8, head_y - 6.0)], 0.6),
              b.stroke([(hx, head_y + 0.5), (hx, head_y - 8.0)], 0.65),
              b.stroke([(hx + 3.6, head_y - 0.5), (hx + 3.8, head_y - 6.0)], 0.6)]
    cross = b.stroke([(hx - 3.6, head_y), (hx + 3.6, head_y)], 0.65)
    flat(p, cross, IRON[4], L)
    for pr in prongs:
        if not pr:
            continue
        top = min(y for _, y in pr)
        for (x, y) in pr:
            p.px(x, y, LAVA[5] if y <= top + 1 else LAVA[3] if y <= top + 3 else IRON[4], L)
    tips = [b.pt(hx - 3.8, head_y - 6.0), b.pt(hx, head_y - 8.0), b.pt(hx + 3.8, head_y - 6.0)]
    for i, (tx, ty) in enumerate(tips):
        glow(p, tx, ty + 1, 2.4 * b.k, 2.8 * b.k, X["heat"], (0.2, 0.34), L=p.flicker(i) if motion else "haze")
    outline(p, shaft | cross | set().union(*prongs), IRON[0], IRON[1], L, only_free=True)
    if planted:
        for s_ in (-1, 1):
            hand_c = b.ellipse(hx, hy + 0.2 * s_ * 2.2, 1.4, 1.2)
            form(p, hand_c, HIDE, lo=2, hi=4, L=L, depth=1.0)


def hellfire(p: Pix, b: Body, at, motion=True, L="base"):
    """A ball of hellfire on a demon's open hand, flickering, its light thrown on the demon from below."""
    x, y = b.pt(*at)
    r = 2.6 * b.k
    Lf = p.flicker(0) if motion else L
    for (qx, qy) in ellipse(x, y, r, r):
        d = math.hypot(qx + 0.5 - x + 0.6, qy + 0.5 - y + 0.6) / r
        p.px(qx, qy, FIRE[6] if d < 0.35 else FIRE[5] if d < 0.65 else FIRE[4] if d < 0.9 else LAVA[4], Lf)
    for i, (dx, dy) in enumerate(((-1, -1), (1, -2), (0, -3))):
        p.px(int(x + dx * b.k), int(y - r + dy * b.k * 0.6), FIRE[4] if i % 2 else LAVA[4], Lf)
    glow(p, x, y, r * 3.2, r * 3.2, X["heat"], (0.1, 0.2, 0.32), L=p.flicker(0, back=True) if motion else "haze")
    p.lamps.append((x, y, 16 * b.k, 0))
