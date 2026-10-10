# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Thanksgiving set's scenery and sprites, drawn on the shared pixel canvas.

Ported from the set's approved preview: the paper, the sky and the frame, the scenery a header stands on,
and every sprite, each shaded from the one light in the upper left on the set's own ramps."""
from __future__ import annotations

import math
import random

from ..pixel import FONTS, LX, LY, LZ, Paint, Pix, num
from .palette import C, GROUND, NIGHT_SKY, RAMP, X, step


def autumn_fill(r, c, scale, night):
    """The colour a title's letter takes at row `r` and column `c` of the letter, counted in pixels from
    its top-left: the turn of the leaves from top to foot, a band for each row of the face, wheat gold
    through squash to cranberry, the way a maple turns from its crown down. By night every band is a tone
    or two lighter, so each keeps 4.5:1 against the evening sky."""
    Wh, S, Cr = RAMP["wheat"], RAMP["squash"], RAMP["cranberry"]
    band = min(6, r // scale)
    if night:
        return (Wh[5], Wh[4], S[5], S[4], X["maple_night"], X["maple_night"], X["maple_deep_night"])[band]
    return (Wh[4], Wh[3], S[4], S[3], Cr[4], Cr[3], Cr[2])[band]


# The turn of the leaves as the paint a title's letters take: one tile a letter tall, a band a row of its face.
AUTUMN = Paint("autumn", autumn_fill)


def title_edge(p: Pix, ch: str, scale: int, shadow: str, edge: str):
    """A day title's letter from beneath, drawn once a file for each letter and size and placed where the
    letter is: its shadow half a font pixel down and to the right, and over it a dark edge a pixel wide all
    round (the letter moved a pixel left, right, up and down), which the painted letter covers but for the
    edge. It is the shadow and outline `Pix.text` would draw, in one use a letter instead of five, built
    from the letter's own glyph. Returns the symbol's key."""
    key = ("edge", ch, scale, shadow, edge)
    if key not in p.syms:
        glyph = ("glyph", "57", ch)         # the letter as `Pix.text` keeps it, so it is drawn once in the file
        if glyph not in p.syms:
            p.symbol(glyph, {(col, r): 1 for r, cols in enumerate(FONTS["57"][0][ch][1]) for col in cols}, mono=True)
        g, d, off = p.syms[glyph], num(1 / scale), num(max(1, scale // 2) / scale)
        p.symbol(key, {}, shapes=f'<use href="#{g}" x="{off}" y="{off}" stroke="{shadow}"/><g stroke="{edge}">'
                                 + "".join(f'<use href="#{g}" {a}="{s}{d}"/>' for a in "xy" for s in ("-", "")) + "</g>")
    return key


def paper(p: Pix, night: bool, x=0, y=0, w=None, h=None, dots=True, uid="p"):
    """The ground a drawing sits on: linen paper with a dot grid by day, by night an evening sky that
    warms toward the horizon in five bands, the last light still in it."""
    w = p.w if w is None else w
    h = p.h if h is None else h
    if not night:
        p.under.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{C["paper"]}"/>')
        if dots:
            p.defs.append(f'<pattern id="{uid}d" width="8" height="8" patternUnits="userSpaceOnUse">'
                          f'<rect x="4" y="4" width="1" height="1" fill="{C["grid"]}"/></pattern>')
            p.under.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{uid}d)"/>')
        return
    n = len(NIGHT_SKY)
    edges = [y + round(i * h / n) for i in range(n + 1)]
    for i, col in enumerate(NIGHT_SKY):
        p.under.append(f'<rect x="{x}" y="{edges[i]}" width="{w}" height="{edges[i + 1] - edges[i]}" fill="{col}"/>')
    if dots:
        p.defs.append(f'<pattern id="{uid}d" width="8" height="8" patternUnits="userSpaceOnUse">'
                      f'<rect x="4" y="4" width="1" height="1" fill="{C["grid_n"]}"/></pattern>')
        p.under.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{uid}d)"/>')


def sparkle(p: Pix, x, y, big=False, L="base", night=True, warm=False):
    """A four-point glint: a white heart, arms that fade, longer arms on the brightest."""
    arm = RAMP["wheat"][5] if warm else X["star_pale"]
    p.px(x, y, C["white"], L)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        p.px(x + dx, y + dy, arm, L)
    if big:
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            p.px(x + dx, y + dy, arm + ":0.5", L)


def stars(p: Pix, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
    """An evening's stars at three magnitudes: faint pinpricks, bright points, and a few glints. None is
    set inside a box in `avoid` (x0, y0, x1, y1), so no glint sits in a letter or beside a word."""
    rnd = random.Random(seed)
    for i in range(n):
        x, y = rnd.randrange(x0, x1), rnd.randrange(y0, y1)
        k = rnd.random()
        if any(a <= x < c and b <= y < d for a, b, c, d in avoid):
            continue
        if k < 0.5 or faint:
            p.px(x, y, rnd.choice((X["star_faint"], X["star_dim"])), "haze")
        elif k < 0.88:
            L = p.twinkle(i, back=True) if (twinkling and rnd.random() < 0.5) else "haze"
            p.px(x, y, rnd.choice((C["white"], RAMP["wheat"][6], X["star_pale"])), L)
        else:
            sparkle(p, x, y, big=rnd.random() < 0.4, L=p.twinkle(i, back=True) if twinkling else "haze",
                    warm=rnd.random() < 0.4)


def wicker_frame(p: Pix, night: bool, x=0, y=0, w=None, h=None, inner=True, uid="rod"):
    """The sheet's border: a band of wicker three pixels wide, straw strands woven over and under brown
    stakes, lit along its top-left edge, like the rim of a harvest basket; inside it a cranberry rule.
    Each side is one pattern tile placed along it, so the border costs a few hundred bytes."""
    w = p.w if w is None else w
    h = p.h if h is None else h
    Wh, B = RAMP["wheat"], RAMP["bark"]
    k = -1 if night else 0
    straw = (Wh[5 + k], Wh[4 + k], Wh[2 + k])
    stake = (B[5 + k], B[4 + k], B[2 + k])

    def tile(horizontal):
        cells = {}
        for a in range(8):
            for b in range(3):
                s_ = a // 4
                on_stake = a % 4 == 1
                over = (b != 1) if s_ == 0 else (b == 1)
                if on_stake and over:
                    c = stake[b]
                else:
                    c = straw[b]
                    near = (a % 4 in (0, 2)) and ((b != 1) if s_ == 0 else (b == 1))
                    if near:
                        c = step(c, -1)          # the strand dips where it passes under a stake
                cells[(a, b) if horizontal else (b, a)] = c
        return cells

    for name, horizontal in (("h", True), ("v", False)):
        cells = tile(horizontal)
        tw, th = (8, 3) if horizontal else (3, 8)
        p.defs.append(f'<pattern id="{uid}{name}" width="{tw}" height="{th}" patternUnits="userSpaceOnUse">'
                      f'{p._paths(cells)}</pattern>')
    p.defs.append(f'<rect id="{uid}H" width="{w}" height="3" fill="url(#{uid}h)"/>')
    p.defs.append(f'<rect id="{uid}V" width="3" height="{h - 6}" fill="url(#{uid}v)"/>')
    for (name, bx, by) in (("H", x, y), ("H", x, y + h - 3), ("V", x, y + 3), ("V", x + w - 3, y + 3)):
        p.shapes["base"].append(f'<use href="#{uid}{name}" x="{bx}" y="{by}"/>')
    if inner:
        p.box(x + 3, y + 3, w - 6, h - 6, RAMP["cranberry"][4] if night else RAMP["cranberry"][3])


# --------------------------------------------------------------------------- leaves
# A maple leaf, point up, stem at the foot, in three tones lit from the upper left: a, b, c, and d the stem.
MAPLE9 = ["....a....", "...aab...", "a..aab..b", "aa.abb.bb", ".aaabbbb.", "aaaabbbbc", ".aabbbbc.", "...abc...",
          "....d...."]
MAPLE7 = ["...a...", "a.aab.b", "aaabbbb", ".aabbc.", "aabbbcc", "..bcc..", "...d..."]
MAPLE5 = ["..a..", "a.ab.", "aabbb", ".abc.", "..d.."]
OAK = ["..a..", ".aab.", "..ab.", ".abbc", "..bc.", ".bbc.", "..d.."]
TINY = [".a.", "abc"]


def leaf_pal(fam, night, lift=0):
    """A leaf's tones in the family `fam`: lit, mid, shade and the stem."""
    R = RAMP[fam]
    k = (-1 if night else 0) + lift
    t = {"cranberry": 4, "squash": 4, "wheat": 4, "bark": 4, "sage": 4}[fam]
    return {"a": R[max(1, min(6, t + 1 + k))], "b": R[max(1, min(6, t + k))], "c": R[max(1, min(6, t - 1 + k))],
            "d": RAMP["bark"][2 + (0 if night else 1)]}


def leaf(p: Pix, x, y, fam="squash", night=False, kind="maple7", L="base", flip=False, turn=0, reuse=True):
    """A leaf, top-left at (x, y): a maple leaf 9, 7 or 5 across, an oak leaf 5 by 7, or a scrap of one
    3 by 2. `turn` quarter-turns it and `flip` mirrors it, so leaves that lie about or fall need not all
    lie the same way."""
    art = {"maple9": MAPLE9, "maple7": MAPLE7, "maple5": MAPLE5, "oak": OAK, "tiny": TINY}[kind]
    for _ in range(turn % 4):
        art = ["".join(row[i] for row in reversed(art)) for i in range(len(art[0]))]
    p.sprite(x, y, art, leaf_pal(fam, night), 1, L, flip=flip, reuse=reuse)


def acorn(p: Pix, x, y, night=False, L="base"):
    """An acorn, 4 by 6, top-left at (x, y): a stalk, a cap of scales shaded round, and the nut below it,
    lit on its left with a glint."""
    B, Wh = RAMP["bark"], RAMP["wheat"]
    k = -1 if night else 0
    art = [".s..", "cCCd", "CcCd", ".nNm", ".nNm", "..m."]
    pal = {"s": B[3 + k], "c": B[4 + k], "C": B[3 + k], "d": B[2 + k], "n": Wh[4 + k], "N": Wh[3 + k], "m": Wh[2 + k]}
    p.sprite(x, y, art, pal, 1, L)


def leaves_on(p: Pix, x0, x1, y, seed=7, L="base", night=False, gap=(7, 20), big=0.0):
    """Fallen leaves lying along a ledge whose top edge is row `y`: scraps of red, orange, gold and brown,
    now and then a whole maple leaf lying on its side where `big` allows, and an acorn among them. None
    lies where it would touch a word."""
    rnd = random.Random(seed * 131 + x0)
    x = x0 + rnd.randint(1, 5)
    fams = ("cranberry", "squash", "wheat", "squash", "bark", "cranberry", "wheat")
    i = 0
    while x < x1 - 3:
        fam = fams[(i + seed) % len(fams)]
        r = rnd.random()
        if big and r < big and x + 7 < x1 and p.clear_of_words(x, y - 5, x + 5, y):
            leaf(p, x, y - 5, fam, night, "maple5", L, flip=rnd.random() < 0.5, turn=rnd.choice((1, 3)))
            x += 5
        elif r > 0.93 and x + 4 < x1 and p.clear_of_words(x, y - 6, x + 4, y):
            acorn(p, x, y - 6, night, L)
            x += 4
        elif not p.clear_of_words(x, y - 2, x + 5, y):     # nothing lies where it would touch a word
            pass
        else:
            leaf(p, x, y - 2, fam, night, "tiny", L, flip=rnd.random() < 0.5)
            if rnd.random() < 0.4:
                leaf(p, x + 2, y - 2, fams[(i + seed + 2) % len(fams)], night, "tiny", L, flip=True)
                x += 2
        x += rnd.randint(*gap)
        i += 1


def _garland_span(sp, sag, night, gap, variant):
    """One span of the garland, tack to tack, as pixels: the twine sagging `sag` rows at its middle, a leaf
    tied on at every `gap` pixels, by turns a maple leaf hanging from it and a smaller one standing up from
    it, and between them a sprig of cranberries or an acorn."""
    B, Cr = RAMP["bark"], RAMP["cranberry"]
    twine, glint = (B[4], B[5]) if night else (B[3], B[5])
    k = -1 if night else 0
    oy = 6                                                   # room above the twine for the standing leaves
    q = Pix(sp + 2, sag + oy + 10)
    pts = [(xx, oy + round(sag * 4 * (xx / sp) * (1 - xx / sp))) for xx in range(sp)]
    for i, (xx, yy) in enumerate(pts):
        q.px(xx, yy, glint if i % 9 == 4 else twine)
    for (a_, b_) in zip(pts, pts[1:]):
        if abs(a_[1] - b_[1]) > 1:
            for yy in range(min(a_[1], b_[1]), max(a_[1], b_[1])):
                q.px(a_[0], yy, twine)
    fams = ("cranberry", "squash", "wheat", "bark", "squash", "cranberry", "sage", "wheat")
    for n, (xx, yy) in enumerate(pts[gap // 2::gap]):
        if sp - xx < 5:
            break
        fam = fams[(n + 3 * variant) % len(fams)]
        if n % 2 == 0:                                       # a maple leaf hanging from the twine by its stem
            leaf(q, xx - 3, yy + 1, fam, night, "maple7", turn=2, reuse=False)
        else:                                                # a smaller one tied on standing up
            leaf(q, xx - 2, yy - 5, fam, night, "maple5", flip=(n + variant) % 4 == 1, reuse=False)
        mx = xx + gap // 2
        if mx < sp - 2:
            my = pts[mx][1]
            if (n + variant) % 3 == 2:                       # an acorn on its stalk
                acorn(q, mx - 1, my + 1, night)
            else:                                            # a sprig of cranberries
                for (dx, dy, t) in ((0, 1, 4), (-1, 2, 4), (0, 2, 5), (1, 2, 3), (0, 3, 3)):
                    q.px(mx + dx, my + dy, Cr[t + k])
    return {(x, y - oy): c for (x, y), c in q.layers["base"].items()}


def garland(p: Pix, x0, x1, y, span=45, sag=4, night=False, gap=8):
    """A garland along the top: a twine rope sagging between tacks, autumn leaves tied along it at every
    `gap` pixels, by turns hanging from it and standing up from it, red, orange, gold and brown, and at
    each tack a pair of acorns. Each span is drawn once, in two orders of colour that take turns, and
    hung again and again; the last span is cut to fit."""
    xs = list(range(x0, x1, span))
    for i, xa in enumerate(xs):
        sp = min(span, x1 - xa)
        if sp < 6:
            continue
        key = ("garland", sp, sag, night, gap, i % 2)
        if key not in p.syms:
            p.symbol(key, _garland_span(sp, sag, night, gap, i % 2))
        p.use(key, xa, y)
    for xa in xs + [x1]:
        key = ("acornpair", night)
        if key not in p.syms:
            q = Pix(10, 8)
            acorn(q, 0, 0, night)
            acorn(q, 3, 1, night)
            p.symbol(key, dict(q.layers["base"]))
        p.use(key, min(xa, x1 - 4) - 3, y - 1)


# --------------------------------------------------------------------------- the ground and the trees
def ground(p: Pix, x0, x1, y_top, y_bot, seed=5, night=False, L="base", litter=True):
    """The ground along the foot of a drawing: a rolling crest of earth with tufts of dry grass standing
    up from it, darker toward the rule it rests on, and fallen leaves scattered over it."""
    E, S = RAMP["earth"], RAMP["sage"]
    rnd = random.Random(seed)
    h = rnd.randint(2, 3)
    prev = h
    tops = {}
    for x in range(x0, x1):
        h = max(1, min(y_bot - y_top, h + rnd.choice((-1, 0, 0, 0, 1))))
        top = y_bot - h
        tops[x] = top
        for yy in range(top, y_bot):
            c = E[5] if yy == top else (E[4] if yy < y_bot - 1 else E[3])
            if night:
                c = E[4] if yy == top else (E[3] if yy < y_bot - 1 else E[2])
            if yy == top and h < prev:
                c = step(c, -1)
            p.px(x, yy, c, L)
        prev = h
        r_ = rnd.random()
        if r_ < 0.22:
            p.px(x, top - 1, S[3 + (0 if night else 1)] if rnd.random() < 0.5 else S[2 + (0 if night else 1)], L)
            if r_ < 0.07:
                p.px(x, top - 2, RAMP["wheat"][3 + (-1 if night else 0)], L)
    if litter:
        fams = ("cranberry", "squash", "wheat", "bark")
        for x in range(x0 + 1, x1 - 2, 1):
            if rnd.random() < 0.16:
                leaf(p, x, tops[x] - 1, fams[rnd.randrange(4)], night, "tiny", L, flip=rnd.random() < 0.5)


def treeline(p: Pix, x0, x1, base, h=12, night=False, seed=3, L="base", taper=(True, True)):
    """A line of trees in their autumn colours along the far edge of the ground, their foot on row `base`:
    rounded crowns that overlap, each a red, an orange, a gold or a late green, lit on its upper left and
    speckled with its darker leaves. By night they stand dark against the sky with the moon's light on
    their crowns. `taper` lowers the line toward either end."""
    K = RAMP["coal"]
    rnd = random.Random(seed)
    crowns = []
    x = x0 - 2
    fams = ("squash", "cranberry", "wheat", "squash", "sage", "cranberry", "wheat")
    while x < x1 + 2:
        r = rnd.uniform(3.5, 6.5)
        hc = rnd.uniform(0.55, 1.0) * h
        f0 = (x - x0) / max(1, x1 - x0)
        if taper[0]:
            hc *= min(1.0, 0.45 + f0 * 3.5)
        if taper[1]:
            hc *= min(1.0, 0.45 + (1 - f0) * 3.5)
        crowns.append((x + r * 0.5, r, hc, fams[len(crowns) % len(fams)]))
        x += rnd.uniform(3.5, 6.5)
    top, owner = {}, {}
    for xx in range(x0, x1):
        best = None
        for cr in crowns:
            cxc, r, hc, fam = cr
            dxn = (xx + 0.5 - cxc) / r
            if abs(dxn) >= 1:
                continue
            t = base - hc * math.sqrt(1 - dxn * dxn) ** 0.6
            if best is None or t < best[0]:
                best = (t, cr)
        if best:
            top[xx], owner[xx] = round(best[0]), best[1]
    for xx, ty in top.items():
        cxc, r, hc, fam = owner[xx]
        F = RAMP[fam]
        for yy in range(ty, base):
            dxn = (xx + 0.5 - cxc) / r
            dyn = (yy + 0.5 - (base - hc * 0.6)) / max(1.0, hc * 0.6)
            lit = -dxn * 0.55 - dyn * 0.6
            edge = yy == ty
            if night:
                c = K[3] if lit > 0.35 else K[2]
                if edge and dxn < -0.25:
                    c = K[4]
            else:                                            # far off, so paler and softer than what stands in front
                c = F[5] if lit > -0.1 else F[4]
                if edge and dxn < 0.1:
                    c = F[6]
            if not edge and (xx * 7919 ^ yy * 104729 ^ seed * 31) % 11 == 0:
                c = K[1] if night else F[4]
            p.px(xx, yy, c, L)


def field_hill(p: Pix, x0, x1, crest, foot, night=False, L="base"):
    """A low hill far off, rising from row `foot` to row `crest` between x0 and x1: a harvested field on it
    in rows of pale stubble that follow its curve, lit along its crest and darker toward its right. By
    night it is dark earth with the moon along its crest."""
    Wh, E = RAMP["wheat"], RAMP["earth"]
    cx, hw, hh = (x0 + x1) / 2, (x1 - x0) / 2, foot - crest
    for x in range(x0, x1):
        u = (x + 0.5 - cx) / hw
        top = round(foot - hh * max(0.0, 1 - u * u) ** 0.55)
        for y in range(top, foot):
            furrow = (y - top) % 2 == 1
            if night:
                c = X["moonlit"] if y == top and u < 0.3 else (E[3] if not furrow else E[2])
            else:
                c = Wh[6] if y == top else (Wh[4] if furrow else Wh[5])
                if u > 0.45 and y > top:
                    c = step(c, -1)
            p.px(x, y, c, L)


def autumn_tree(p: Pix, cx, base, h=46, night=False, seed=4, L="base", clip=None):
    """A tree in its autumn colours standing on row `base`: a trunk shaded round from the left that
    forks into limbs, and a crown of many small clumps of leaves, most of them the tree's own colour and
    some a second, each clump lit on its upper left within a crown lit on its upper left, speckled with
    darker leaves and ragged at its edge. By night its colours are dim and the harvest moon lights its
    upper edge. Returns where its crown is, for the leaves that fall from it."""
    B, K = RAMP["bark"], RAMP["coal"]
    rnd = random.Random(seed)
    trunk_h = round(h * 0.45)
    tw = max(2.0, h / 16)
    for j in range(trunk_h + 2):
        yy = base - 1 - j
        t = j / max(1, trunk_h)
        half = tw * (1 - 0.3 * t) + (1.2 if j < 2 else 0)
        xc = cx + 0.6 * math.sin(t * 2.2)
        for xx in range(math.floor(xc - half), math.ceil(xc + half)):
            if clip and not clip[0] <= xx < clip[1]:
                continue
            u = (xx + 0.5 - xc) / half
            if abs(u) > 1:
                continue
            if night:
                c = K[4] if u < -0.6 else (K[2] if u < 0.3 else K[1])
            else:
                c = B[4] if u < -0.5 else (B[3] if u < 0.3 else B[2])
            p.px(xx, yy, c, L)
    for sgn in (-1, 1):                                      # two limbs up into the crown
        pts = {}
        _line(pts, cx + sgn * 1, base - trunk_h, cx + sgn * h * 0.22, base - trunk_h - h * 0.2)
        for q in pts:
            if not clip or clip[0] <= q[0] < clip[1]:
                p.px(q[0], q[1], (K[2] if night else B[3]), L)
                p.px(q[0], q[1] + 1, (K[1] if night else B[2]), L)
    cy = base - trunk_h - h * 0.27
    rx, ry = h * 0.44, h * 0.34
    main, accent = {0: ("squash", "wheat"), 1: ("cranberry", "squash"), 2: ("wheat", "squash")}[seed % 3]
    weights = [main] * 7 + [accent] * 3
    clumps = []
    tries = 0
    while len(clumps) < max(14, int(h * 0.9)) and tries < 1200:
        tries += 1
        u, v = rnd.uniform(-1, 1), rnd.uniform(-1, 1)
        if u * u + v * v > 1:
            continue
        clumps.append((cx + u * rx, cy + v * ry, rnd.uniform(0.07, 0.11) * h, rnd.choice(weights)))
    clumps.sort(key=lambda c_: c_[1])
    owner = {}
    for yy in range(math.floor(cy - ry), math.ceil(cy + ry) + 1):          # the crown's shaded heart,
        for xx in range(math.floor(cx - rx), math.ceil(cx + rx) + 1):      # seen between the clumps
            if clip and not clip[0] <= xx < clip[1]:
                continue
            if ((xx + 0.5 - cx) / (rx * 0.82)) ** 2 + ((yy + 0.5 - cy) / (ry * 0.82)) ** 2 <= 1:
                owner[(xx, yy)] = None
    for (ccx, ccy, r, fam) in clumps:
        for yy in range(math.floor(ccy - r) - 1, math.ceil(ccy + r) + 1):
            for xx in range(math.floor(ccx - r) - 1, math.ceil(ccx + r) + 1):
                if clip and not clip[0] <= xx < clip[1]:
                    continue
                d = math.hypot(xx + 0.5 - ccx, (yy + 0.5 - ccy) * 1.1)
                if d > r + (0.7 if (xx * 3 + yy * 7 + seed) % 4 == 0 else 0):
                    continue
                owner[(xx, yy)] = (ccx, ccy, r, fam)
    for (xx, yy), own in owner.items():
        whole = -((xx + 0.5 - cx) / rx * 0.6 + (yy + 0.5 - cy) / ry * 0.75)
        if own is None:                                      # deep in the crown, between the clumps
            F = RAMP[main]
            p.px(xx, yy, F[0] if night else (F[2] if whole > -0.2 else F[1]), L)
            continue
        ccx, ccy, r, fam = own
        F = RAMP[fam]
        local = -((xx + 0.5 - ccx) * 0.6 + (yy + 0.5 - ccy) * 0.75) / r
        lit = 0.35 * local + 0.85 * whole
        edge = any((xx + dx, yy + dy) not in owner for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if night:                                            # its colours dim, the moon along its edge
            c_ = F[2] if lit > 0.35 else F[1]
            if edge and whole > 0.45:
                c_ = F[3]
        else:
            c_ = F[5] if lit > 0.55 else (F[4] if lit > 0.0 else (F[3] if lit > -0.6 else F[2]))
        if (xx * 7919 ^ yy * 104729 ^ seed * 31) % 13 == 0 and not edge:    # a darker leaf here and there
            c_ = F[max(0, F.index(c_) - 1)]
        p.px(xx, yy, c_, L)
    return dict(cx=cx, cy=cy, rx=rx)


def harvest_moon(p: Pix, cx, cy, r, L="base"):
    """The harvest moon low in the evening sky: a big amber disc lit almost face on, a little brighter
    toward the upper left and darker at its limb, soft grey seas and a few craters, and a warm halo
    stepping out into the sky round it."""
    M = RAMP["moon"]
    p.halo(cx, cy, r * 2.4, r * 2.4, M[4], (0.03, 0.05, 0.08, 0.12))
    cells = {}
    for y in range(math.floor(cy - r) - 1, math.ceil(cy + r) + 1):
        for x in range(math.floor(cx - r) - 1, math.ceil(cx + r) + 1):
            dx, dy = (x + 0.5 - cx) / r, (y + 0.5 - cy) / r
            d2 = dx * dx + dy * dy
            if d2 > 1:
                continue
            nz = math.sqrt(1 - d2)
            lam = 0.55 * nz + 0.45 * max(0.0, dx * LX + dy * LY + nz * LZ)
            cells[(x, y)] = 3.0 + 3.0 * lam
    for (mx, my, mr) in ((-0.3, -0.2, 0.3), (0.22, 0.12, 0.24), (-0.05, 0.46, 0.2), (0.42, -0.32, 0.15)):
        sx, sy = cx + mx * r, cy + my * r
        for q in cells:
            d = math.hypot(q[0] + 0.5 - sx, q[1] + 0.5 - sy) / (mr * r)
            if d <= 0.72:
                cells[q] -= 1.0
            elif d <= 1.0:
                cells[q] -= 0.5
    for (x, y), v in cells.items():
        p.px(x, y, M[max(2, min(6, round(v)))], L)
    for (mx, my) in ((0.3, 0.45), (-0.52, 0.18), (0.05, -0.55)):
        qx, qy = math.floor(cx + mx * r), math.floor(cy + my * r)
        if (qx, qy) in cells and (qx + 1, qy + 1) in cells:
            p.px(qx, qy, M[2], L)
            p.px(qx + 1, qy + 1, M[6], L)
    for (x, y) in list(cells):
        far = (x + 0.5 - cx) * LX + (y + 0.5 - cy) * LY < -0.7 * r
        if far and any((x + dx, y + dy) not in cells for dx, dy in ((1, 0), (0, 1))):
            p.px(x, y, M[3], L)
    return cells


def glow_cells(cx, cy, rx, ry, col, alphas, skip=()):
    """A small stepped glow as see-through pixels around (cx, cy), leaving out the pixels in `skip`."""
    out, n = {}, len(alphas)
    for y in range(math.floor(cy - ry), math.ceil(cy + ry) + 1):
        for x in range(math.floor(cx - rx), math.ceil(cx + rx) + 1):
            d = math.hypot((x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry)
            if d < 1 and (x, y) not in skip:
                out[(x, y)] = f"{col}:{alphas[min(n - 1, int((1 - d) * n))]:g}"
    return out


def light_pool(p: Pix, cx, y, rx, ry, night, col=None):
    """A light pooled on the earth round its foot: only the ground takes it."""
    col = col or RAMP["wheat"][4]
    if night:
        p.halo(cx, y, rx, ry, col, (0.1, 0.18, 0.27, 0.36), L="pool", only=GROUND)
    else:
        p.halo(cx, y, rx, ry, col, (0.05, 0.09), L="pool", only=GROUND)


# --------------------------------------------------------------------------- motion: leaves and steam
def fall_path(x, y, gy, drift, phase) -> list:
    """The steps a leaf takes from (x, y) down to row `gy`, swaying from side to side as it comes down and
    landing a little to the side by `drift`."""
    n = max(14, round((gy - y) / 2.2))
    path = []
    for s in range(n):
        t = s / (n - 1)
        path.append((round(x + drift * t + 3.2 * math.sin(2 * math.pi * (t * 1.6 + phase))), round(y + (gy - 4 - y) * t)))
    return path


def falling_leaves(p: Pix, falls, night, motion=True, z=16):
    """Leaves coming down: each (x, y, ground, fam, drift, dur, phase) starts at (x, y), sways side to side
    as it falls, turning as it goes, lands at row `ground` a little to the side by `drift`, lies there a
    moment and is gone, round and round. The still file leaves each at the first step of its fall. A leaf
    whose fall would cross a word is left out, in both files."""
    for i, (x, y, gy, fam, drift, dur, phase) in enumerate(falls):
        path = fall_path(x, y, gy, drift, phase)
        if not all(p.clear_of_words(px - 1, py - 1, px + 8, py + 8) for px, py in path + [(x, y)]):
            continue
        frames = []
        for f, (turn, flip) in enumerate(((0, False), (1, False), (0, True))[:3 if motion else 1]):
            key = ("falling", fam, night, f)
            if key not in p.syms:
                q = Pix(9, 9)
                leaf(q, 0, 0, fam, night, "maple7", turn=turn, flip=flip, reuse=False)
                p.symbol(key, dict(q.layers["base"]))
            frames.append(key)
        if not motion:
            p.use(frames[0], *path[0], "near")
            continue
        path += [path[-1]] * 3 + [(-20, -20)] * 2          # it lies a moment, then it is gone
        p.fly(frames, path, dur, z=z, flap=0.3)


GOOSE_UP = ["w.....w", ".ww.ww.", "...b...", "......."]
GOOSE_DOWN = [".......", "...b...", ".ww.ww.", "w.....w"]
V_PLACES = ((0, 0), (9, -4), (9, 4), (18, -8), (18, 8))


def geese(p: Pix, enter, still, leave, night, motion=True, dur=18.0, z=15):
    """A skein of geese in a V, heading south: five birds, the leader in front, their wings beating out of
    step with their neighbours'. They come in at `enter`, pass `still` and fly off at `leave`, a step at a
    time, and then the sky is empty a while before they come round again. The still file holds them at
    `still`. By night they are dark shapes with the moon on their wings. A flight that would cross a word
    is left out, in both files."""
    def leg(a_, b_):
        n_ = max(4, round(math.hypot(b_[0] - a_[0], b_[1] - a_[1]) / 3))
        return [(round(a_[0] + (b_[0] - a_[0]) * s / n_), round(a_[1] + (b_[1] - a_[1]) * s / n_)) for s in range(n_)]

    out, back = leg(still, leave), leg(enter, still)
    if not all(p.clear_of_words(x - 1, y - 11, x + 26, y + 11) for x, y in back + out + [still]):
        return
    K = RAMP["coal"]
    pal = ({"b": K[0], "w": K[3]} if not night else {"b": K[5], "w": X["moonlit"]})
    beats = (GOOSE_UP, GOOSE_DOWN)
    frames = []
    for f in range(2 if motion else 1):
        key = ("geese", night, f)
        if key not in p.syms:
            q = Pix(30, 26)
            for i, (dx, dy) in enumerate(V_PLACES):
                q.sprite(dx, 10 + dy, beats[(f + i) % 2], pal, 1)
            p.symbol(key, {(x, y - 12): c_ for (x, y), c_ in q.layers["base"].items()})
        frames.append(key)
    if not motion:
        p.use(frames[0], *still, "near")
        return
    path = out + [(-80, -80)] * round((len(out) + len(back)) * 0.5) + back
    p.fly(frames, path, dur, z=z, flap=0.2)


def steam(p: Pix, x, y, night, motion=True, phase=0, dur=2.4):
    """Steam rising from something hot, its foot at (x, y): three wisps that curl as they climb, shown in
    turn so the steam seems to rise. The still file keeps the first."""
    col = RAMP["linen"][5] if night else RAMP["linen"][2]
    alpha = 0.55 if night else 0.5
    shapes = [[(0, 0), (1, -1), (1, -2), (0, -3), (0, -4), (1, -5)],
              [(1, 0), (0, -1), (0, -2), (1, -3), (1, -4), (0, -5), (0, -6)],
              [(0, -1), (1, -2), (1, -3), (0, -4), (0, -5), (1, -6), (1, -7)]]
    for f, pts in enumerate(shapes):
        L = p.seq(f"stm{phase}{f}", round(f / 3, 3), round((f + 1) / 3, 3), dur, keep=f == 0, z=13) if motion else "near"
        for (dx, dy) in pts:
            p.apx(x + dx, y + dy, col, alpha if dy > -4 else alpha * 0.6, L)
            p.apx(x + dx + 3, y + dy + 1, col, alpha * 0.8 if dy > -4 else alpha * 0.5, L)
        if not motion:
            break


# --------------------------------------------------------------------------- light that falls on things
def lamp(p: Pix, cx, cy, r, phase, own=()):
    """Register a flame at (cx, cy): once everything is drawn, `lamplight` lays its warm light on
    whatever stands within `r` of it, flickering with the flame. `own` are the lamp's own pixels."""
    p.lamps.append((cx, cy, r, phase, set(own)))


def lamplight(p: Pix, night: bool):
    """The finishing pass: each candle's light on the drawn things near it (the pie, the pumpkins, the
    hay, the ground), strongest nearest the flame. The paper, the sky and the words take none."""
    base = p.layers["base"]
    col = RAMP["wheat"][5]
    alphas = (0.08, 0.15, 0.24) if night else (0.035, 0.07)
    n = len(alphas)
    for (cx, cy, r, phase, own) in p.lamps:
        L = p.flicker(phase)
        for y in range(math.floor(cy - r), math.ceil(cy + r) + 1):
            for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
                if (x, y) not in base or (x, y) in own:
                    continue
                d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.25) / r
                if d < 1:
                    p.apx(x, y, col, alphas[min(n - 1, int((1 - d) * n))], L)


def contact(p: Pix, cx, y, rx):
    """The shadow a thing standing on the ground leaves right under it: only the earth takes it."""
    p.halo(cx + 0.5, y + 0.5, rx, 1.7, X["shade_ink"], (0.22, 0.38), L="pool", only=GROUND, shape=False)


def _line(cells: dict, x0, y0, x1, y1, tag=1):
    """A one-pixel line, each step touching the last."""
    x0, y0, x1, y1 = math.floor(x0), math.floor(y0), math.floor(x1), math.floor(y1)
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = 1 if x0 < x1 else -1, 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        cells.setdefault((x0, y0), tag)
        if (x0, y0) == (x1, y1):
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


# --------------------------------------------------------------------------- the harvest
def pumpkin(p: Pix, cx, base, rx, ry=None, night=False, L="base", vine=True, fam="squash"):
    """A pumpkin sitting on row `base`, centred on `cx`: its lobes bulge, each lit from the upper left with
    a streak down its lit side, creased where it meets the one behind; a curved stem with a cut end and,
    on a big one, a leaf and a curl of vine. `fam` "linen" makes it a white pumpkin. By night it is dim,
    lit along its rim by the harvest moon."""
    P, S, W = RAMP[fam], RAMP["sage"], RAMP["bark"]
    ry = ry or max(2.5, rx * 0.74)
    cy = base - ry
    n = 5 if rx >= 6 else 3
    lobes = []
    for i in range(n):
        off = (i - (n - 1) / 2) / ((n - 1) / 2)
        lobes.append((abs(off), cx + off * rx * (0.6 if n == 5 else 0.48), rx * (0.45 if n == 5 else 0.56),
                      ry * (0.95 if off == 0 else (1.0 if abs(off) < 0.6 else 0.9))))
    owner, lam_ = {}, {}
    for k in sorted(range(n), key=lambda i: -lobes[i][0]):
        ao, lcx, hw, hh = lobes[k]
        for y in range(math.floor(cy - hh) - 1, math.ceil(cy + hh) + 1):
            for x in range(math.floor(lcx - hw) - 1, math.ceil(lcx + hw) + 1):
                lx, ly = (x + 0.5 - lcx) / hw, (y + 0.5 - cy) / hh
                if lx * lx + ly * ly > 1 or y >= base:
                    continue
                gx, gy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
                gz = math.sqrt(max(0.0, 1 - min(1.0, gx * gx + gy * gy)))
                lz = math.sqrt(max(0.0, 1 - lx * lx - ly * ly))
                nx, ny, nz = 0.45 * gx + 0.55 * lx, 0.45 * gy + 0.55 * ly, 0.45 * gz + 0.55 * lz
                ln = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
                owner[(x, y)] = k
                lam_[(x, y)] = max(0.0, (nx * LX + ny * LY + nz * LZ) / ln)
    for (x, y), k in owner.items():
        lam = lam_[(x, y)]
        v = (0.9 + 2.6 * lam) if night else (1.3 + 3.9 * lam)
        if fam == "linen":                                    # a white pumpkin stays pale in its shadows
            v = (1.5 + 2.4 * lam) if night else (2.5 + 3.3 * lam)
        if any(owner.get((x + dx, y)) is not None and lobes[owner[(x + dx, y)]][0] < lobes[k][0] for dx in (-1, 1)):
            v -= 1.15
        p.px(x, y, P[max(1, min(5, round(v)))], L)
    for k, (ao, lcx, hw, hh) in enumerate(lobes):
        if lcx > cx + 0.5:
            continue
        sx = round(lcx - 0.34 * hw - 0.5)
        mine = [y for (x, y), o in owner.items() if o == k and x == sx]
        if not mine:
            continue
        y0, y1 = min(mine), max(mine)
        top_ = y0 + max(1, round((y1 - y0) * 0.18))
        for y in range(top_, top_ + max(1, round((y1 - y0) * 0.38))):
            if owner.get((sx, y)) == k:
                p.px(sx, y, P[4] if night else P[5], L)
    for (x, y) in list(owner):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q in owner or q[1] >= base:
                continue
            lit = (q[0] + 0.5 - cx) * LX + (q[1] + 0.5 - cy) * LY > 0.25 * rx
            soft = 1 if fam == "linen" and not night else 0
            p.px(q[0], q[1], (X["moonlit"] if night else P[1 + soft]) if lit and dy <= 0 else P[soft], L)
    top = min(y for (x, y), o in owner.items() if lobes[o][0] == 0)
    sw = 2 if rx >= 6 else 1
    sh = max(2, round(ry * 0.42))
    sx0 = round(cx) - sw // 2
    p.hline(sx0 - 1, sx0 + sw + 1, top, P[2] if night else P[3], L)
    for j in range(1, sh + 1):
        lean = round(0.9 * (j / sh) ** 2 * (sw + 0.5))
        for i in range(sw):
            c = (S[3] if i == 0 else S[2]) if sw == 2 else S[3]
            if night:
                c = S[2] if i == 0 else S[1]
            p.px(sx0 + i + lean, top - j, c, L)
    cap = round(0.9 * (sw + 0.5))
    for i in range(sw):
        p.px(sx0 + i + cap, top - sh - 1, W[5] if i == 0 else W[4], L)
    if vine and rx >= 8:
        for (dx, dy) in ((sw + 1, -1), (sw + 2, -2), (sw + 3, -2), (sw + 4, -1), (sw + 4, 0), (sw + 3, 0)):
            p.px(sx0 + dx, top + dy, S[3] if not night else S[2], L)
        for (dx, dy, t) in ((-1, -1, 4), (-2, -1, 4), (-3, -2, 5), (-2, -2, 4), (-3, -1, 3), (-4, -1, 3), (-4, 0, 2),
                            (-3, 0, 2), (-2, 0, 2)):
            p.px(sx0 + dx, top + dy, S[t - 1] if night else S[t], L)
    return owner


def gourd(p: Pix, x, base, kind="stripe", night=False, L="base"):
    """A gourd sitting on row `base` with its left edge at `x`: a round one striped green and cream, a
    pear-shaped one gold above and green below, or a warty yellow crookneck with its neck curled over; each
    lit on its upper left, with a stalk."""
    S, Wh, Ln, B = RAMP["sage"], RAMP["wheat"], RAMP["linen"], RAMP["bark"]
    k = -1 if night else 0

    def blob(cx, cy, rx, ry, colour):
        for y in range(math.floor(cy - ry), math.ceil(cy + ry) + 1):
            for xx in range(math.floor(cx - rx), math.ceil(cx + rx) + 1):
                dx, dy = (xx + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
                d2 = dx * dx + dy * dy
                if d2 > 1 or y >= base:
                    continue
                lam = max(0.0, dx * LX + dy * LY + math.sqrt(1 - d2) * LZ)
                p.px(xx, y, colour(xx, y, lam), L)
    if kind == "stripe":
        cx, cy = x + 3.5, base - 2.8
        blob(cx, cy, 3.5, 2.9, lambda xx, y, lam: (Ln[(5 if lam > 0.55 else 4) + k] if (xx - x) % 3 == 1
                                                     else S[(4 if lam > 0.55 else 3) + k]))
        p.px(x + 3, base - 6, B[3 + k], L)
        p.px(x + 4, base - 7, B[3 + k], L)
    elif kind == "pear":
        blob(x + 2.8, base - 2.6, 2.8, 2.6, lambda xx, y, lam: S[(5 if lam > 0.6 else 4 if lam > 0.3 else 3) + k])
        blob(x + 2.8, base - 6.2, 1.7, 1.9, lambda xx, y, lam: Wh[(5 if lam > 0.5 else 4) + k])
        p.px(x + 3, base - 9, B[3 + k], L)
    else:
        blob(x + 3.6, base - 3.0, 3.0, 3.0, lambda xx, y, lam: Wh[(5 if lam > 0.6 else 4 if lam > 0.3 else 3) + k])
        for (dx, dy, t) in ((2, -6, 5), (1, -7, 5), (0, -7, 4), (-1, -6, 4), (-1, -5, 3), (2, -7, 4), (1, -8, 4)):
            p.px(x + 1 + dx, base + dy, Wh[t + k], L)
        for (dx, dy) in ((2, -3), (4, -2), (5, -4)):
            p.px(x + dx, base + dy, Wh[6 + k], L)          # warts, catching the light
        p.px(x - 1, base - 5, S[3 + k], L)


def apple(p: Pix, x, y, night=False, L="base"):
    """An apple, 5 by 6, top-left at (x, y): red, lit on its upper left with a glint, a stalk and a leaf."""
    R, S, B = RAMP["cranberry"], RAMP["sage"], RAMP["bark"]
    k = -1 if night else 0
    art = ["..sl.", ".hAb.", "aAAbc", "aAbbc", "abbcc", ".bcc."]
    p.sprite(x, y, art, {"s": B[2 + k], "l": S[4 + k], "h": R[6 + k], "a": R[5 + k], "A": R[4 + k], "b": R[3 + k],
                         "c": R[2 + k]}, 1, L)


def grapes(p: Pix, x, y, night=False, L="base"):
    """A bunch of grapes, 5 by 6, top-left at (x, y): purple grapes, each lit on its upper left."""
    P, B = RAMP["plum"], RAMP["bark"]
    k = -1 if night else 0
    art = ["..s..", "abab.", "babab", ".abab", "..ab.", "...b."]
    p.sprite(x, y, art, {"s": B[3 + k], "a": P[5 + k], "b": P[3 + k]}, 1, L)


# --------------------------------------------------------------------------- the turkey
def turkey(p: Pix, cx, base, night=False, L="base", s=1.0):
    """A turkey standing on row `base`, centred on `cx`, facing us, `s` its size (1 is about 28 across):
    its tail fanned out behind it, each feather brown at its root and banded cranberry, squash and gold out
    to a pale tip, lit on its left and parted from the next by a dark line; a ring of shorter bronze
    feathers over their roots; a round bronze body with its feathers in scales and a paler breast, its
    wings drooping at its sides; a red neck and a pale blue face with bright eyes, a gold beak, a red snood
    over it and a red wattle; orange legs and three-toed feet."""
    B, Cr, S, Wh, Ln, K, Sl = (RAMP[n] for n in ("bark", "cranberry", "squash", "wheat", "linen", "coal", "slate"))
    k = -1 if night else 0
    R = 13.5 * s
    fy = base - 11.5 * s
    big = s >= 0.8
    n = 11 if big else 9

    def fan(radius, count):
        cells = {}
        for y in range(math.floor(fy - radius) - 1, math.ceil(fy + 2 * s) + 1):
            for x in range(math.floor(cx - radius) - 1, math.ceil(cx + radius) + 1):
                dx, dy = x + 0.5 - cx, y + 0.5 - fy
                rho = math.hypot(dx, dy)
                th = math.atan2(-dy, dx)
                if th < -0.22:
                    th += 2 * math.pi
                if not -0.22 <= th <= math.pi + 0.22:
                    continue
                f = (math.pi + 0.22 - th) / ((math.pi + 0.44) / count)
                j, within = min(count - 1, int(f)), f - int(f)
                if rho > radius * (1 - 0.12 * ((within - 0.5) * 2) ** 2):
                    continue
                cells[(x, y)] = (j, within, rho / radius)
        return cells

    for (x, y), (j, within, fr) in fan(R, n).items():
        tip = fr >= 0.93
        c = (B[3 + k] if fr < 0.58 else Cr[3 + k] if fr < 0.72 else S[4 + k] if fr < 0.85 else Wh[4 + k] if not tip
             else Ln[5 + k])
        if within < 0.42 and not tip:
            c = step(c, 1)                                   # each feather lit on its left
        if within < 0.1 or within > 0.93:
            c = step(c, -2) if not tip else B[2 + k]         # the parting between two feathers
        p.px(x, y, c, L)
    for (x, y), (j, within, fr) in fan(R * 0.6, n - 2).items():   # the shorter feathers over the tail's root
        c = B[4 + k] if within < 0.45 else B[3 + k]
        if fr > 0.84:
            c = Wh[3 + k] if within < 0.6 else B[5 + k]
        if within < 0.12 or within > 0.92:
            c = B[2 + k]
        p.px(x, y, c, L)
    # the wings, drooping at its sides behind the body
    by, brx, bry = base - 7.0 * s, 6.4 * s, 6.1 * s
    for sgn in (-1, 1):
        wcx, wcy, wrx, wry = cx + sgn * 5.4 * s, by + 1.4 * s, 2.3 * s, 4.4 * s
        for y in range(math.floor(wcy - wry), math.ceil(wcy + wry) + 1):
            for x in range(math.floor(wcx - wrx) - 1, math.ceil(wcx + wrx) + 1):
                dx, dy = (x + 0.5 - wcx) / wrx, (y + 0.5 - wcy) / wry
                if dx * dx + dy * dy > 1 or y >= base - 1:
                    continue
                c = B[(3 if sgn < 0 else 2) + k]
                if dy < -0.5:
                    c = B[(4 if sgn < 0 else 3) + k]
                if sgn * dx > 0.5:
                    c = B[1 + max(0, k + 1)]
                p.px(x, y, c, L)
    # the body: bronze, its feathers in scales, lit on its upper left
    body = {}
    for y in range(math.floor(by - bry) - 1, math.ceil(by + bry) + 1):
        for x in range(math.floor(cx - brx * 0.82) - 1, math.ceil(cx + brx * 0.82) + 1):
            dx, dy = (x + 0.5 - cx) / (brx * 0.82), (y + 0.5 - by) / bry
            d2 = dx * dx + dy * dy
            if d2 > 1:
                continue
            nz = math.sqrt(1 - d2)
            lam = max(0.0, dx * LX + dy * LY + nz * LZ)
            t = 2 + round(2.4 * lam)
            if abs(dx) < 0.45 and dy < 0.4:
                t += 1                                        # the breast
            if big and y % 2 == 0 and (x + (y // 2) % 2 * 2) % 4 == 0 and d2 < 0.75:
                t -= 1                                        # a scale of feathers
            body[(x, y)] = B[max(1, min(6, t + k))]
    for (q, c) in body.items():
        p.px(q[0], q[1], c, L)
    for (x, y) in list(body):
        if (x, y + 1) not in body and y > by:
            p.px(x, y, B[1 + max(0, k + 1)], L)
    # the neck and the head
    hx, hy = round(cx) - (2 if big else 1), round(base - (21.0 if big else 20.5) * s)
    art = ([".aaa.", "aWaWb", "aKwKb", ".rwc.", ".rrc.", "..r.."] if big else [".a.", "KaK", "rwr", ".r."])
    pal = {"a": Sl[4] if not night else Sl[3], "b": Sl[3] if not night else Sl[2], "K": K[0], "W": Ln[6], "w": Wh[4 + k],
           "c": Cr[4 + k], "r": Cr[3 + k]}
    for yy in range(hy + len(art), math.floor(by - bry) + 2):
        p.px(round(cx) - (1 if big else 0), yy, Cr[3 + k], L)
        if big:
            p.px(round(cx), yy, Cr[2 + k], L)
    p.sprite(hx, hy, art, pal, 1, L)
    # the legs and feet
    for lx in (round(cx - 2.4 * s), round(cx + 2.4 * s) - 1):
        for yy in range(round(by + bry) - 1, base):
            p.px(lx, yy, S[3 + k], L)
        for dx in (-1, 0, 1):
            p.px(lx + dx, base - 1, S[2 + k] if dx else S[3 + k], L)


# --------------------------------------------------------------------------- the horn of plenty
def cornucopia(p: Pix, x, base, night=False, L="base", phase=0):
    """A horn of plenty lying on row `base`, its tail curled up and over at the left and its mouth open to
    the right, about 46 across with its spill: woven wicker, braided in rings with the strands running
    slantwise between them, lit along its top and shaded underneath, a braided rim round its mouth and dark
    inside. Spilling out of it: grapes over the lip, stalks of wheat, an ear of corn in its husk, an apple,
    a pumpkin, a pear and a striped gourd, with a leaf or two among them."""
    Wh, B, K = RAMP["wheat"], RAMP["bark"], RAMP["coal"]
    k = -1 if night else 0
    P0, P1, P2, P3 = (x + 9.0, base - 20.0), (x - 3.0, base - 19.0), (x + 1.0, base - 2.0), (x + 25.0, base - 9.0)
    samples, s_acc, prev = [], 0.0, None
    for i in range(121):
        t = i / 120
        bx_ = (1 - t) ** 3 * P0[0] + 3 * (1 - t) ** 2 * t * P1[0] + 3 * (1 - t) * t * t * P2[0] + t ** 3 * P3[0]
        by_ = (1 - t) ** 3 * P0[1] + 3 * (1 - t) ** 2 * t * P1[1] + 3 * (1 - t) * t * t * P2[1] + t ** 3 * P3[1]
        if prev:
            s_acc += math.hypot(bx_ - prev[0], by_ - prev[1])
        prev = (bx_, by_)
        samples.append((bx_, by_, 0.7 + 7.1 * t ** 1.7, s_acc, t))
    horn = {}
    for (sx_, sy_, r, sa, t) in samples:
        for yy in range(math.floor(sy_ - r) - 1, math.ceil(sy_ + r) + 1):
            for xx in range(math.floor(sx_ - r) - 1, math.ceil(sx_ + r) + 1):
                dx, dy = xx + 0.5 - sx_, yy + 0.5 - sy_
                if dx * dx + dy * dy <= r * r and yy < base:
                    horn[(xx, yy)] = (dx / max(0.7, r), dy / max(0.7, r), sa, t, r)
    total = samples[-1][3]
    for (q, (ox, oy, sa, t, r)) in horn.items():
        lam = max(0.0, ox * LX + oy * LY + 0.5)
        v = 2.2 + 2.8 * lam
        ring = (total - sa) % 3.2 < 0.9
        if ring:
            v -= 1.2                                             # the braided rings
        elif int((total - sa) * 1.1 + (ox + oy) * r * 0.9) % 2 == 0:
            v += 0.6                                             # the strands, slantwise between them
        c = Wh[max(1, min(6, round(v + k)))]
        if oy > 0.72 and not ring:
            c = B[3 + k]
        p.px(q[0], q[1], c, L)
    # the mouth: a braided rim round the dark inside
    mx, my, mr = P3[0] + 0.5, P3[1], 7.8
    for yy in range(math.floor(my - mr) - 1, math.ceil(my + mr) + 1):
        for xx in range(math.floor(mx - 3), math.ceil(mx + 4)):
            e = ((xx + 0.5 - mx) / 2.9) ** 2 + ((yy + 0.5 - my) / (mr + 0.5)) ** 2
            if e > 1 or yy >= base:
                continue
            inner = ((xx + 0.5 - mx - 0.7) / 1.7) ** 2 + ((yy + 0.5 - my) / (mr - 1.3)) ** 2 <= 1
            if inner:
                c = K[1] if yy < my + 2 else B[1]
            else:
                c = (Wh[5 + k] if (xx + yy) % 2 else Wh[3 + k]) if yy < my else (Wh[4 + k] if (xx + yy) % 2 else Wh[2 + k])
            p.px(xx, yy, c, L)
    # the spill
    Sg, Ln = RAMP["sage"], RAMP["linen"]
    for i, (ex, ey) in enumerate(((x + 27, base - 16), (x + 29, base - 18), (x + 31, base - 19))):   # wheat
        for j in range(5):
            p.px(ex + j // 2, ey - j, Wh[3 + k], L)
        for j in range(3):
            p.px(ex + 2 + j // 2, ey - 5 - j, Wh[5 + k] if j % 2 == 0 else Wh[4 + k], L)
            p.px(ex + 3 + j // 2, ey - 5 - j, Wh[4 + k], L)
        p.px(ex + 4, ey - 9, Wh[6 + k], L)
    corn = ["....hh", "...hkk", "..hkkk", ".hkkk.", "hkkk..", "kk...."]
    p.sprite(x + 29, base - 15, corn, {"h": Ln[4 + k], "k": Wh[5 + k] if not night else Wh[4]}, 1, L)
    grapes(p, x + 24, base - 17, night, L)
    grapes(p, x + 27, base - 15, night, L)
    apple(p, x + 23, base - 7, night, L)
    pumpkin(p, x + 33, base - 1, 5.5, night=night, L=L, vine=False)
    pear = ["..s.", ".gg.", ".gh.", "gggh", "gghh", ".hh."]
    p.sprite(x + 40, base - 7, pear, {"s": B[2 + k], "g": Sg[5 + k], "h": Sg[4 + k]}, 1, L)
    gourd(p, x + 28, base - 1, "stripe", night, L)
    leaf(p, x + 44, base - 6, "cranberry", night, "maple5", L, reuse=False)
    return horn


# --------------------------------------------------------------------------- sheaves, corn and hay
def wheat_sheaf(p: Pix, cx, base, h=22, night=False, L="base"):
    """A sheaf of wheat standing on row `base`, about `h` tall: stalks bound at the waist with twine,
    their heads fanning out above, each a golden ear with its awns, and their cut ends fanning out below."""
    Wh, B = RAMP["wheat"], RAMP["bark"]
    k = -1 if night else 0
    tie = base - round(h * 0.42)
    cells = {}
    n = 9
    for i in range(n):
        f = (i - (n - 1) / 2) / ((n - 1) / 2)
        _line(cells, cx + f * h * 0.24, base - 1, cx + f * 1.2, tie, ("stalk", f))
        a = -math.pi / 2 + f * 0.62
        hx, hy = cx + f * 1.2 + math.cos(a) * h * 0.38, tie + math.sin(a) * h * 0.38
        _line(cells, cx + f * 1.2, tie, hx, hy, ("stalk", f))
        for j in range(4):                                  # the ear: kernels in pairs up the stalk's end
            ex, ey = hx + math.cos(a) * j * 1.1, hy + math.sin(a) * j * 1.1
            cells[(math.floor(ex), math.floor(ey))] = ("ear", f)
            cells[(math.floor(ex + math.cos(a + math.pi / 2)), math.floor(ey + math.sin(a + math.pi / 2)))] = ("ear2", f)
        ax, ay = hx + math.cos(a) * 5.4, hy + math.sin(a) * 5.4
        cells.setdefault((math.floor(ax), math.floor(ay)), ("awn", f))
    for (q, (kind, f)) in cells.items():
        if kind == "stalk":
            c = Wh[3 + k] if f < 0.2 else Wh[2 + k]
        elif kind == "ear":
            c = Wh[5 + k] if f < 0.3 else Wh[4 + k]
        elif kind == "ear2":
            c = Wh[4 + k] if f < 0.3 else Wh[3 + k]
        else:
            c = Wh[6 + k]
        p.px(q[0], q[1], c, L)
    for dx in range(-2, 3):
        p.px(round(cx) + dx, tie, B[3 + k] if dx < 1 else B[2 + k], L)
        p.px(round(cx) + dx, tie + 1, B[2 + k], L)


def corn_bundle(p: Pix, x, y, night=False, L="base"):
    """Three ears of ornamental corn hung together, top-left at (x, y), about 12 by 17: their papery husks
    pulled up and tied in a knot, and below it the ears, their kernels every colour of the harvest."""
    Ln, B = RAMP["linen"], RAMP["bark"]
    k = -1 if night else 0
    rnd = random.Random(7)
    husk = ["a..d..a", ".ad.da.", "..ada..", "...k..."]
    p.sprite(x + 2, y, husk, {"a": Ln[4 + k], "d": Ln[3 + k], "k": B[3 + k]}, 1, L)
    kern = [RAMP["cranberry"][4 + k], RAMP["squash"][4 + k], RAMP["wheat"][4 + k], RAMP["plum"][4 + k], Ln[5 + k],
            RAMP["cranberry"][3 + k], RAMP["wheat"][5 + k]]
    for e, (ex, tilt) in enumerate(((x + 1, -1), (x + 5, 0), (x + 9, 1))):
        for j in range(11):
            for i in range(3):
                if j == 10 and i != 1:
                    continue
                xx = ex + i + round(tilt * j / 7)
                c = rnd.choice(kern)
                if i == 2:
                    c = step(c, -1)
                p.px(xx, y + 4 + j, c, L)
        for j in range(3):
            p.px(ex + 1 + (0 if j < 2 else tilt), y + 3 + j - 1, Ln[3 + k], L)


def hay_bale(p: Pix, x, base, w=20, h=10, night=False, L="base"):
    """A bale of hay on row `base`, `w` by `h`, seen from a little above and to the left: its top face
    lit, its long face in straw laid in streaks, its end in shade with the straw's cut ends showing, two
    bands of twine round it and a few loose straws sticking out."""
    Wh, B = RAMP["wheat"], RAMP["bark"]
    k = -1 if night else 0
    rnd = random.Random(x * 7 + base * 3)
    top, lid, end = base - h, 3, 3
    fw = w - end
    cells = {}
    for yy in range(top + lid, base):                          # the long face
        j = yy - top - lid
        xx = x
        while xx < x + fw:
            run = rnd.randint(2, 5)
            t = 4 if j < 2 else (3 if j < h - lid - 2 else 2)
            t += rnd.choice((0, 0, 1, -1)) if 0 < j else 1
            for i in range(run):
                if xx + i < x + fw:
                    cells[(xx + i, yy)] = t
            xx += run
    for yy in range(top, top + lid):                          # the top face, lit
        j = yy - top
        for xx in range(x + 1 + (lid - 1 - j), x + fw + (lid - 1 - j) + 1):
            cells[(xx, yy)] = 5 + (1 if rnd.random() < 0.18 else 0) - (1 if rnd.random() < 0.2 else 0)
    for yy in range(top + 1, base):                            # the end, in shade, the cut straw showing
        j = yy - top
        for xx in range(x + fw, x + w):
            if j < lid and xx - (x + fw) > lid - 1 - (lid - j):
                continue
            cells[(xx, yy)] = rnd.choice((2, 3, 3)) if j >= lid else 3
    for (q, t) in cells.items():
        p.px(q[0], q[1], Wh[max(1, min(6, t + k))], L)
    for fx in (round(w * 0.28), round(w * 0.64)):              # the twine, over the top and down the face
        for yy in range(top, base):
            j = yy - top
            xx = x + fx + (lid - 1 - j if j < lid else 0)
            p.px(xx, yy, B[4 + k] if j < lid else B[3 + k], L)
            if j >= lid:
                p.px(xx + 1, yy, Wh[2 + k] if (yy % 3) else Wh[3 + k], L)
    for yy in range(top + lid, base):
        p.px(x + fw, yy, Wh[2 + k], L)                         # the edge between face and end
    p.hline(x, x + w, base - 1, Wh[1 + max(0, k + 1)], L)
    for (dx, dy) in ((3, -1), (9, -1), (14, -1), (-1, lid + 2), (-1, lid + 5), (w, lid + 3)):
        if rnd.random() < 0.8:
            p.px(x + dx, top + dy, Wh[5 + k] if dy < 0 else Wh[4 + k], L)


# --------------------------------------------------------------------------- the farm
def corn_shock(p: Pix, cx, base, h=26, night=False, L="base", seed=3):
    """A shock of corn standing on row `base`, about `h` tall: the dried stalks stood on end in a cone and
    tied near the top, their cut ends showing above the tie with a tassel or two, the stalks' long leaves
    hanging down its sides, pale and curled, the whole lit on its left."""
    Wh, Ln, B = RAMP["wheat"], RAMP["linen"], RAMP["bark"]
    k = -1 if night else 0
    rnd = random.Random(seed)
    tie = base - round(h * 0.74)
    half = h * 0.28
    for y in range(tie, base):                                   # the cone of stalks
        t = (y - tie) / max(1, base - 1 - tie)
        hw = 1.6 + (half - 1.6) * t
        for x in range(math.floor(cx - hw), math.ceil(cx + hw)):
            f = (x + 0.5 - cx) / hw
            if abs(f) > 1:
                continue
            tone = 4 if f < -0.35 else (3 if f < 0.4 else 2)
            if int((f + 1) * 6.5) % 2 == 0:
                tone -= 1                                        # the stalks, converging on the tie
            p.px(x, y, Wh[max(1, tone + k)], L)
    for i in range(7):                                           # the stalks' ends above the tie
        f = (i - 3) / 3
        _cells = {}
        _line(_cells, cx + f * 1.3, tie - 1, cx + f * 4.4, base - h + abs(f) * 3.0, 1)
        for (x, y) in _cells:
            p.px(x, y, Wh[(4 if f < 0.2 else 3) + k], L)
        p.px(math.floor(cx + f * 4.4), math.floor(base - h + abs(f) * 3.0) - 1, Wh[5 + k], L)
    for j in range(9):                                           # the long leaves, hanging down its sides
        side = -1 if j % 2 == 0 else 1
        y0 = tie + 2 + rnd.randint(0, round((base - tie) * 0.55))
        t = (y0 - tie) / max(1, base - 1 - tie)
        x0 = cx + side * (1.6 + (half - 1.6) * t) - side * rnd.uniform(0.5, 2.5)
        for m in range(rnd.randint(4, 7)):
            xx, yy = math.floor(x0 + side * m * 0.8), math.floor(y0 + 0.14 * m * m)
            if yy >= base - 1:
                break
            p.px(xx, yy, Ln[(4 if side < 0 else 3) + k], L)
    for dx in range(-2, 2):
        p.px(round(cx) + dx, tie, B[3 + k] if dx < 0 else B[2 + k], L)
        p.px(round(cx) + dx, tie + 1, B[2 + k], L)


def scarecrow(p: Pix, cx, base, night=False, L="base"):
    """A scarecrow on its post, standing on row `base`, about 30 tall with its arms out 19 wide: a straw
    hat with a band, a burlap head with button eyes and a stitched smile, a plaid shirt with straw at the
    cuffs and the neck, patched blue trousers with straw at the ankles, and a crow on its arm."""
    Wh, Ln, B, Cr, Sl, K = (RAMP[n] for n in ("wheat", "linen", "bark", "cranberry", "slate", "coal"))
    k = -1 if night else 0
    X0 = round(cx) - 9
    top = base - 30
    art = [
        "......hhhhh........",
        "......hHHHh........",
        "......bbbbb........",
        "...hhhhhhhhhhh.....",
        ".....sssssSS.......",
        ".....sKsssKS.......",
        ".....sssssSS.......",
        ".....smsmsmS.......",
        "......ssmSS........",
        "......tyyyt........",
        "yyPpPpPpPpPpPpPpPyy",
        "yyPpPpPpPpPpPpPpPyy",
        ".....pPpPpPp.......",
        ".....PpPpPpP.......",
        ".....pPpPpPp.......",
        ".....PpPpPpP.......",
        ".....dddddddd......",
        ".....dD..w..dD.....",
        ".....dD..w..dD.....",
        ".....dD..w..dD.....",
        ".....dq..w..dD.....",
        ".....dD..w..dD.....",
        ".....yy..w..yy.....",
        ".........w.........",
        ".........w.........",
        ".........w.........",
        ".........w.........",
        ".........w.........",
        ".........w.........",
        "........www........",
    ]
    pal = {"h": Wh[4 + k], "H": Wh[5 + k], "b": Cr[3 + k], "s": Ln[3 + k], "S": Ln[2 + k], "K": K[0],
           "m": B[2 + k], "t": B[3 + k], "y": Wh[5 + k], "P": Cr[3 + k], "p": Ln[4 + k] if not night else Ln[2],
           "d": Sl[3] if not night else Sl[2], "D": Sl[2] if not night else Sl[1], "q": Cr[4 + k],
           "w": B[3 + k]}
    p.sprite(X0, top, art, pal, 1, L)
    crow = [".kk..", "kkkkb", ".kk.."]
    p.sprite(X0 + 1, top + 7, crow, {"k": K[1] if not night else K[3], "b": Wh[4 + k]}, 1, L)


def barn(p: Pix, x, base, night=False, L="base", phase=0):
    """A red barn far off, standing on row `base` with its left corner at `x`, 16 wide under a gambrel
    roof, and a silo beside it: board walls lit on the left, white trim, big doors braced with a white X
    and a hayloft door above them. By night the walls are dark and its windows are lit."""
    Cr, B, Ln, K, Sl, Wh = (RAMP[n] for n in ("cranberry", "bark", "linen", "coal", "slate", "wheat"))
    k = -1 if night else 0
    w, wall, roof = 16, 7, 7
    top = base - wall - roof
    cx = x + w / 2
    for j in range(roof):                                         # the gambrel roof
        yy = top + j
        hw = 2.5 + j * 1.6 if j < 3 else 7.3 + (j - 3) * 0.45
        for xx in range(math.floor(cx - hw), math.ceil(cx + hw)):
            c = K[3] if night else B[1]
            if xx < cx:
                c = (K[4] if night else B[2]) if j < 3 else (K[3] if night else B[1])
            if (xx == math.floor(cx - hw) or j == 0) and night:
                c = X["moonlit"]
            p.px(xx, yy, c, L)
    for j in range(wall):                                         # the walls, in boards
        yy = top + roof + j
        for xx in range(x, x + w):
            c = Cr[(4 if xx < x + 5 else 3) + (k * 2)] if night else Cr[4 if xx < x + 5 else 3]
            if night:
                c = Cr[1] if xx < x + 5 else Cr[0]
            if (xx - x) % 2 == 1:
                c = step(c, -1) if c != Cr[0] else Cr[0]
            p.px(xx, yy, c, L)
        p.px(x, yy, Ln[5 + k], L)
        p.px(x + w - 1, yy, Ln[4 + k], L)
    for xx in range(x, x + w):
        p.px(xx, top + roof, Ln[5 + k], L)                        # the trim under the eaves
    dx0 = round(cx) - 3
    for j in range(6):                                            # the big doors, framed and braced with an X
        yy = base - 6 + j
        for i in range(7):
            c = Cr[2] if not night else Cr[0]
            if i in (0, 6) or j == 0 or (j >= 1 and i in (j, 6 - j)):
                c = Ln[5] if not night else Ln[2]
            p.px(dx0 + i, yy, c, L)
    lx, ly = round(cx) - 1, top + 3                               # the hayloft door
    for (ddx, ddy) in ((0, 0), (1, 0), (0, 1), (1, 1)):
        p.px(lx + ddx, ly + ddy, (Wh[5] if night else B[1]), L)
    for (ddx, ddy) in ((-1, -1), (0, -1), (1, -1), (2, -1), (-1, 0), (2, 0), (-1, 1), (2, 1)):
        p.px(lx + ddx, ly + ddy, Ln[5 + k] if not night else Ln[2], L)
    wins = [(x + 2, base - 5), (x + w - 3, base - 5)]
    for (wx, wy) in wins:                                          # two small windows
        for (ddx, ddy) in ((0, 0), (0, 1)):
            p.px(wx + ddx, wy + ddy, Wh[5] if night else Sl[2], L)
    if night:
        lamp_cells = ({(lx, ly), (lx + 1, ly), (lx, ly + 1), (lx + 1, ly + 1)}
                      | {(wx, wy + d) for wx, wy in wins for d in (0, 1)})
        for (qx, qy), c in glow_cells(lx + 1, ly + 1, 2.6, 2.4, Wh[5], (0.25, 0.4), lamp_cells).items():
            p.px(qx, qy, c, "haze")
    # the silo beside it
    sx, sw, sh = x + w + 1, 5, wall + roof + 2
    for j in range(sh):
        yy = base - 1 - j
        for i in range(sw):
            c = Ln[(4 if i < 2 else (3 if i < 4 else 2)) + k] if not night else (K[4] if i < 2 else K[3])
            if j % 4 == 3:
                c = step(c, -1) if not night else K[2]
            p.px(sx + i, yy, c, L)
    for (ddx, ddy, t) in ((1, 0, 4), (2, 0, 4), (3, 0, 3), (0, 1, 4), (1, 1, 5), (2, 1, 4), (3, 1, 3), (4, 1, 3)):
        c = Sl[t + k] if not night else (X["moonlit"] if ddy == 0 else K[4])
        p.px(sx + ddx, base - 1 - sh - 1 + ddy, c, L)


# --------------------------------------------------------------------------- the table
def pie(p: Pix, x, base, night=False, L="base", w=17, slice_=True):
    """A pumpkin pie in its dish on row `base`, `w` wide, seen from a little above: a crimped golden crust
    round a smooth orange filling lit toward the upper left, a spoon of cream on top, the dish's side below
    the rim and, where a slice has been cut and taken, the dish showing and the cut face of the filling."""
    S, Wh, Ln = RAMP["squash"], RAMP["wheat"], RAMP["linen"]
    k = -1 if night else 0
    rx, ry = w / 2, 3.4
    cx, cy = x + rx, base - 2 - ry
    for yy in range(math.floor(cy - ry) - 1, base):
        for xx in range(x, x + w):
            dx, dy = (xx + 0.5 - cx) / rx, (yy + 0.5 - cy) / ry
            e = dx * dx + dy * dy
            if yy >= cy and abs(dx) <= 1 and e > 1:
                p.px(xx, yy, Ln[4 + k] if dx < -0.3 else (Ln[3 + k] if dx < 0.5 else Ln[2 + k]), L)   # the dish
                continue
            if e > 1:
                continue
            ang = math.atan2(dy, dx)
            if slice_ and 0.22 < ang < 1.15 and e > 0.08:        # the slice that has been taken
                edge = ang < 0.42 or ang > 0.98
                if edge:
                    c = S[3 + k] if e < 0.62 else Wh[3 + k]      # the cut face: filling, then crust
                else:
                    c = Ln[5 + k] if dy < 0.55 else Ln[4 + k]     # the dish's floor
                p.px(xx, yy, c, L)
                continue
            if e > 0.6:
                crimp = int((ang + math.pi) / (2 * math.pi) * 22) % 2 == 0
                c = Wh[(5 if crimp else 4) + k] if dy < 0.2 else Wh[(4 if crimp else 3) + k]
            else:
                lit = -dx * 0.5 - dy * 0.6
                c = S[(5 if lit > 0.35 else (4 if lit > -0.2 else 3)) + k]
            p.px(xx, yy, c, L)
    for (dx, dy, c) in ((0, -1, Ln[6]), (1, -1, Ln[5 + k]), (-1, 0, Ln[5 + k]), (0, 0, Ln[6]), (1, 0, Ln[5 + k]),
                        (2, 0, Ln[4 + k])):
        p.px(round(cx) - 2 + dx, round(cy) + dy - 1, c, L)


def candle(p: Pix, x, base, h=11, night=False, L="base", phase=0, motion=True):
    """A taper candle in a brass holder standing on row `base`: the holder's dish and stem lit on the
    left, the cream taper with a drip down its side, a black wick and a flame three pixels wide, white at
    its heart and orange at its tip, that flickers with its glow and lights what stands near it."""
    Wh, Ln, S = RAMP["wheat"], RAMP["linen"], RAMP["squash"]
    k = -1 if night else 0
    for (dx, c) in ((-2, Wh[4 + k]), (-1, Wh[5 + k]), (0, Wh[4 + k]), (1, Wh[3 + k]), (2, Wh[2 + k])):
        p.px(x + dx, base - 1, c, L)
    p.px(x, base - 2, Wh[4 + k], L)
    p.px(x - 1, base - 3, Wh[5 + k], L)
    p.px(x, base - 3, Wh[4 + k], L)
    p.px(x + 1, base - 3, Wh[3 + k], L)
    top = base - 3 - h
    for yy in range(top, base - 3):
        p.px(x, yy, Ln[6 + k] if yy > top else Ln[5 + k], L)
        p.px(x + 1, yy, Ln[4 + k], L)
    p.px(x - 1, top + 2, Ln[5 + k], L)
    p.px(x - 1, top + 3, Ln[5 + k], L)
    p.px(x, top - 1, RAMP["coal"][2], L)
    Lf = p.flicker(phase) if motion else L
    flame = ((0, -6, S[4]), (0, -5, Wh[5]), (1, -5, S[5]), (-1, -4, Wh[5]), (0, -4, Wh[6]), (1, -4, Wh[5]),
             (-1, -3, S[4]), (0, -3, Wh[6]), (1, -3, S[4]), (0, -2, S[3]))
    for (dx, dy, c) in flame:
        p.px(x + dx, top + dy + 1, c, Lf)
    own = {(x + dx, top + dy + 1) for dx, dy, _ in flame}
    for (qx, qy), c in glow_cells(x + 0.5, top - 3.0, 3.2, 4.2, Wh[5], (0.3, 0.5) if night else (0.1, 0.18), own).items():
        p.px(qx, qy, c, Lf)
    holder = {(x + dx, yy) for dx in (-2, -1, 0, 1, 2) for yy in range(top - 1, base)}
    lamp(p, x + 0.5, top - 2, 10 if night else 6, phase, own | holder)


def heart(p: Pix, x, y, L="base"):
    """A heart, 7 by 6, lit on its upper-left lobe."""
    Rr = RAMP["cranberry"]
    art = [".64.43.", "6544432", "5443321", ".33321.", "..321..", "...1..."]
    p.sprite(x, y, art, {str(i): Rr[i] for i in range(7)}, 1, L)

