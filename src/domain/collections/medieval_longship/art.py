# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Longship set's scenery and sprites, drawn on the shared pixel canvas.

The oak planks the sheet is built of, the carved plait of its border and the prow beasts risen at its corners,
the row of painted shields hung along its top, the fjord its headers open on (walls of snowy crags, the water,
the strand and the longhouse with its gable beasts and its smoke), the longship under sail and the longship
rowing in with her lantern, the sun and the gulls of the day, the aurora's curtains, the moon, the stars and
the brazier of the night, letters chip-carved into the oak, and the things of the ship every element and badge
carries: shields stacked and hung, ropes, rivets, oars, helmed warriors, a bronze brooch and a runestone with
its serpent. Everything is shaded from the one light in the upper left on the set's own ramps; the big quiet
things (a mountain, a hull, a sail, the aurora's bands, the gunwale's shields) are drawn as shapes and pattern
tiles of whole pixels, so the files stay light enough to carry them all."""
from __future__ import annotations

import functools
import math
import random

from ...holidays.pixel import FONTS, Paint, Pix, fold, num, sphere
from .palette import C, LIT, NIGHT_SKY, RAMP, WATER, X, step

OAK, TAR, SEA, DEEP = RAMP["oak"], RAMP["tar"], RAMP["sea"], RAMP["deep"]
IRON, BRONZE, ROPE, FLAME = RAMP["iron"], RAMP["bronze"], RAMP["rope"], RAMP["flame"]
RED, CREAM, OCHRE, MOON = RAMP["red"], RAMP["cream"], RAMP["ochre"], RAMP["moon"]
SKINS = (RAMP["skin0"], RAMP["skin1"], RAMP["skin2"])     # the hand's three skins, light to dark


def wood(night: bool) -> list:
    """The planks' tones: weathered oak by day, tarred by night."""
    return TAR if night else OAK


def water(night: bool) -> list:
    """The sea's tones: the sunlit fjord by day, the deep under the moon."""
    return DEEP if night else SEA


def fells(night: bool) -> list:
    return RAMP["fell_n" if night else "fell"]


def _line(p: Pix, x0, y0, x1, y1, c, L="base"):
    """A one-pixel line from (x0, y0) to (x1, y1)."""
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        p.px(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), c, L)


# --------------------------------------------------------------------------- the paper
PLANK, TILE_W, PLANKS = 12, 208, 6


def _planks(uid: str, seam: str, lit: str, grain: str, knot: str, streaks: bool = True) -> str:
    """A pattern tile of planks, six courses of twelve rows over 208 pixels: each plank's upper seam dark
    and the edge under it lit, two dark streaks of grain and a lighter one wandering the length of every
    plank and breaking now and then, and the odd knot the grain bends round. The grain is periodic, so the
    tile joins without a seam. Without `streaks` the tile keeps the seams, the lit edges and the knots."""
    rnd = random.Random(7)
    cols: dict = {seam: {}, lit: {}, grain: {}, knot: {}}
    knots = {(146, 2), (40, 5)}       # (x, plank) of the knots
    for j in range(PLANKS):
        top = j * PLANK
        cols[seam].setdefault(top, []).extend(range(TILE_W))
        cols[lit].setdefault(top + 1, []).extend(range(TILE_W))
        bases = (top + 3 + rnd.randint(0, 2), top + 7 + rnd.randint(0, 2), top + 5 + rnd.randint(0, 1))
        for s, base in enumerate(bases):
            f1, f2, ph1, ph2 = rnd.choice((1, 2)), rnd.choice((3, 4, 5)), rnd.uniform(0, 6.3), rnd.uniform(0, 6.3)
            gap = rnd.randrange(TILE_W)
            if not streaks:
                continue
            for x in range(TILE_W):
                if (x - gap) % 71 < (9 if s < 2 else 40):
                    continue
                y = base + round(1.1 * math.sin(2 * math.pi * f1 * x / TILE_W + ph1)
                                 + 0.7 * math.sin(2 * math.pi * f2 * x / TILE_W + ph2))
                for (kx, kj) in knots:
                    if kj == j and abs(x - kx) < 6:
                        y += (-1 if y < top + 6 else 1) * (2 if abs(x - kx) < 3 else 1)
                y = min(top + PLANK - 2, max(top + 2, y))
                cols[grain if s < 2 else lit].setdefault(y, []).append(x)
    for (kx, kj) in knots:
        cy = kj * PLANK + 6
        for yy in range(cy - 2, cy + 3):
            for xx in range(kx - 4, kx + 5):
                d = math.hypot((xx + 0.5 - kx - 0.5) / 4.2, (yy + 0.5 - cy - 0.5) / 2.4)
                if d <= 1 and (d > 0.62 or d < 0.3):
                    cols[knot].setdefault(yy, []).append(xx)
    paths = "".join(f'<path stroke="{c}" d="{Pix._d(rows)}"/>' for c, rows in cols.items() if rows)
    return (f'<pattern id="{uid}a" width="{TILE_W}" height="{PLANK * PLANKS}" patternUnits="userSpaceOnUse">'
            f'{paths}</pattern>')


def paper(p: Pix, night: bool, x=0, y=0, w=None, h=None, uid="p"):
    """The ground a drawing sits on: oak planks weathered silver brown by day; by night the same planks
    tarred dark, greened toward the top by the aurora and warmed toward the foot by the brazier. A drawing
    made lighter leaves out the grain, keeping each plank's seam, its lit edge and the knots."""
    w = p.w if w is None else w
    h = p.h - y if h is None else h
    streaks = not p.lite

    def rect(top, rows, fill):
        at = (f' x="{x}"' if x else "") + (f' y="{top}"' if top else "")
        return f'<rect{at} width="{w}" height="{rows}" fill="{fill}"/>'
    if not night:
        p.under.append(rect(y, h, C["paper"]))
        p.defs.append(_planks(uid, OAK[1], OAK[5], OAK[3], OAK[2], streaks))
    else:
        n = len(NIGHT_SKY)
        edges = [y + round(i * h / n) for i in range(n + 1)]
        for i, col in enumerate(NIGHT_SKY):
            p.under.append(rect(edges[i], edges[i + 1] - edges[i], col))
        p.defs.append(_planks(uid, TAR[0], TAR[3], X["grain_night"], X["knot_night"], streaks))
    p.under.append(rect(y, h, f"url(#{uid}a)"))


# --------------------------------------------------------------------------- the night sky
def glow(p: Pix, cx, cy, rx, ry, col, alphas, L="haze", keep=1, only=None):
    """A light's stepped glow, as `Pix.halo` draws it (laid only on the colours in `only` when given); a
    drawing made lighter keeps only its `keep` inner rings, each as strong as it was, and lets the faint outer
    ones go."""
    shape = only is None and max(rx, ry) > 6
    if p.lite and len(alphas) > keep:
        f = keep / len(alphas)
        rx, ry, alphas = rx * f, ry * f, alphas[-keep:]
    p.halo(cx, cy, rx, ry, col, alphas, L, only=only, shape=shape)


def sparkle(p: Pix, x, y, big=False, L="base", warm=False):
    """A four-point glint: a white heart, arms that fade, longer arms on the brightest."""
    arm = BRONZE[6] if warm else X["star_pale"]
    p.px(x, y, C["white"], L)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        p.px(x + dx, y + dy, arm, L)
    if big:
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            p.px(x + dx, y + dy, arm + ":0.5", L)


def stars(p: Pix, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
    """A night's stars at three magnitudes: faint pinpricks, bright points, and a few glints. None is set
    inside a box in `avoid` (x0, y0, x1, y1), so no glint sits in a letter or beside a word."""
    rnd = random.Random(seed)
    for i in range(n):
        x, y = rnd.randrange(x0, x1), rnd.randrange(y0, y1)
        k = rnd.random()
        if any(a <= x < c and b <= y < d for a, b, c, d in avoid):
            continue
        if k < 0.55 or faint:
            p.px(x, y, rnd.choice((X["star_faint"], X["star_dim"])), "haze")
        elif k < 0.9:
            L = p.twinkle(i, back=True) if (twinkling and rnd.random() < 0.5) else "haze"
            p.px(x, y, rnd.choice((C["white"], X["star_pale"], RAMP["aurora"][6])), L)
        else:
            sparkle(p, x, y, big=rnd.random() < 0.4, L=p.twinkle(i, back=True) if twinkling else "haze")


def moon(p: Pix, cx, cy, r, L="base"):
    """A gibbous moon on the hand's moon ramp: shaded as a ball, earthshine on its dark limb, a halo in the
    sky."""
    ox, oy, rr = cx - r * 0.62, cy - r * 0.3, r * 0.98

    def lit(xx, yy):
        return math.hypot(xx + 0.5 - ox, yy + 0.5 - oy) > rr

    glow(p, cx, cy, r * 2.6, r * 2.6, MOON[4], (0.03, 0.05, 0.08, 0.12))
    for yy in range(math.floor(cy - r), math.ceil(cy + r) + 1):
        for xx in range(math.floor(cx - r), math.ceil(cx + r) + 1):
            if math.hypot(xx + 0.5 - cx, yy + 0.5 - cy) <= r and not lit(xx, yy):
                p.px(xx, yy, MOON[0], L)
    sphere(p, cx, cy, r, MOON, L, lo=2, hi=6, rim=False, outline=False, only=lit)
    for (dx, dy) in ((0.25, -0.1), (0.05, 0.5), (0.45, 0.35)):
        qx, qy = math.floor(cx + dx * r), math.floor(cy + dy * r)
        if lit(qx, qy) and math.hypot(qx + 0.5 - cx, qy + 0.5 - cy) <= r - 0.5:
            p.px(qx, qy, MOON[3], L)


def sun(p: Pix, cx, cy, r=3, L="base"):
    """The day's low northern sun: a pale gold disc with a warm rim and a few rays."""
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d = math.hypot(xx + 0.5 - cx - 0.5, yy + 0.5 - cy - 0.5)
            if d <= r + 0.3:
                p.px(xx, yy, X["sun"] if d < r - 0.8 else FLAME[5], L)
    for (dx, dy) in ((r + 2, 0), (-r - 2, 0), (0, r + 2), (0, -r - 2)):
        p.px(cx + dx, cy + dy, FLAME[5] + ":0.6", L)


# The northern lights' bands from the top of the sky down: where each lies (a share of the sky's height), how far
# it swings either way (a share of the height too), how many two-row strips of rays hang from its hem, and how
# bright it burns, the highest the brightest.
BANDS = ((0.28, 0.16, 8, 1.0), (0.58, 0.12, 5, 0.6), (0.84, 0.07, 3, 0.36))
DRIFT = 44.0    # the most seconds the lights take to drift once across the sheet: a slow sweep, as the hand's are
RAY_W = 51      # the rays' pattern repeats every so many pixels, a whole number of times across a drift
GLOW = ((-4, "V", 4, 0.12), (-2, "V", 5, 0.16), (0, "G", 3, 0.28), (2, "G", 4, 0.34), (4, "G", 5, 0.46),
        (5, "G", 6, 0.22), (6, "G", 3, 0.14))
STREAKS = ((-4, 4), (-2, 3), (0, 2), (2, 1))     # the rays rising through a band into its fringe: (row, pattern)


def _stair(x0, tops, foots) -> str:
    """A region from column x0 on, from row tops[i] down to foots[i] (exclusive) in column x0 + i, as one
    path of level and upright steps, so it fills whole pixels."""
    out, run = [f"M{x0} {tops[0]}"], 0
    for i, t in enumerate(tops):
        if i and t != tops[i - 1]:
            out.append(f"h{run}v{t - tops[i - 1]}")
            run = 0
        run += 1
    out.append(f"h{run}V{foots[-1]}")
    run = 0
    for i in range(len(foots) - 1, -1, -1):
        if i < len(foots) - 1 and foots[i] != foots[i + 1]:
            out.append(f"h-{run}v{foots[i] - foots[i + 1]}")
            run = 0
        run += 1
    out.append(f"h-{run}z")
    return "".join(out)


def _region(p: Pix, L, paint, x0, tops, foots):
    """A filled region of whole pixels (see `_stair`) on layer L in `paint` (a colour, a pattern's url, or a
    colour and its opacity). Its cells are kept in the drawing's `filled`, so a check that gathers what a scene
    draws finds them as it finds pixels set one by one."""
    p.shapes[L].append(f'<path fill="{paint}" d="{_stair(x0, tops, foots)}"/>')
    if not hasattr(p, "filled"):
        p.filled = set()
    p.filled.update((x0 + i, y) for i, (t, f) in enumerate(zip(tops, foots)) for y in range(t, f))


def _rays(p: Pix, name, rnd, n, drawn=None) -> list:
    """The rays hanging from a hem, as `n` patterns of upright lines RAY_W pixels wide, one for each two-row
    strip under the hem, each fainter than the one above: a ray in the k-th pattern is in every one before
    it, so each ray runs unbroken from the hem down to its own length, many short and a few long, and each
    fades over its last two strips to a faint tip, violet on the longest. Only the first `drawn` are written
    out, when fewer strips hang."""
    lengths, c = {}, rnd.randrange(2)
    while c < RAY_W:
        lengths[c] = min(n, max(1, round(n * rnd.random() ** 1.5 + rnd.random())))
        c += rnd.choice((2, 2, 3, 3, 4))
    G, V = RAMP["aurora"], RAMP["violet"]
    ids = []

    def own(col):
        """A line's own stroke: none for the rays' green, which is the pattern's (see below)."""
        return "" if col == G[5] else f' stroke="{col}"'
    for k in range(1, n + 1):
        base = 0.5 * (1 - (k - 1) / n) + 0.12
        classes: dict = {}
        for c, ell in lengths.items():
            if ell >= k:
                tip = ell - k
                key = (V[5] if ell > n * 0.6 else G[5], 0.3) if tip == 0 else (G[5], 0.62) if tip == 1 else (G[5], 1.0)
                classes.setdefault(key, []).append(c)
        pid = f"{name}{k}"
        # The rays' green is the pattern's own stroke, which its lines take unless they are violet.
        paths = "".join(f'<path{own(col)} stroke-opacity="{num(round(base * f * 25) / 25)}" d="{Pix._d({0: cols})}"/>'
                        for (col, f), cols in sorted(classes.items()))
        if drawn is None or k <= drawn:
            p.defs.append(f'<pattern id="{pid}" width="{RAY_W}" height="1" patternUnits="userSpaceOnUse" '
                          f'stroke="{G[5]}">{paths}</pattern>')
        ids.append(pid)
    return ids


def _band(x0, tops) -> str:
    """A band two rows deep from column x0 on, its top at row tops[i] in column x0 + i, as path data for a
    stroke two rows wide: a level stroke along each run of columns at one height, so it covers whole pixels
    and its outline is written once."""
    out, start = [], 0
    for i in range(1, len(tops) + 1):
        if i == len(tops) or tops[i] != tops[start]:
            out.append((f"M{x0} {tops[0] + 1}" if start == 0 else f"m0 {tops[start] - tops[start - 1]}")
                       + f"h{i - start}")
            start = i
    return "".join(out).replace(" -", "-")


def _strip(sid, dy, paint) -> str:
    """A band's strip placed `dy` rows down and painted with `paint`."""
    return f'<use href="#{sid}"' + (f' y="{dy}"' if dy else "") + f' stroke="{paint}"/>'


def aurora(p: Pix, x0, y0, x1, y1, seed=1, motion=True, name="au", strong=True, rays=True, z=-18):
    """The northern lights over a night sky, between x0 and x1 and y0 and y1: three bands of green that
    swing along the sheet, the highest the brightest and each lower one fainter toward the fells, each with
    a violet fringe along its upper edge, a bright hem along its foot, and a curtain of rays hanging from the
    hem, many short and a few long, fading as they fall. Each band is one strip of pixels following its swing,
    drawn once and placed again and again down the sky, the rays a pattern of upright lines in it. In a moving
    header the lights drift across the sheet, drawn once and shown again a window to the left, stepping right
    a pixel at a time, so the drift loops without a seam, and each curtain of rays brightens and dims in its
    own time, so the lights shimmer. A still drawing, or a phone's, leaves them where they lie; `strong` is
    the full show, else a fainter one. A drawing made lighter lets each band's glow lose its faintest outer
    rows, the one above its fringe and the one under its hem, with the rays that rise into the first, and its
    longest rays their faint last strip."""
    rnd = random.Random(seed)
    period = x1 - x0
    span = y1 - y0
    tone = {"G": RAMP["aurora"], "V": RAMP["violet"]}
    bands = BANDS[:3 if span >= 40 else 2 if span >= 26 else 1]
    outer = (GLOW[0][0], GLOW[-1][0]) if p.lite else ()
    most = max(n for _, _, n, _ in bands)
    pats = _rays(p, f"{name}r", rnd, most, most - bool(outer)) if rays else []
    parts = []
    for b, (cf, sw, n, bright) in enumerate(bands):
        f1, f2 = rnd.choice((1, 2)), rnd.choice((3, 4))
        ph1, ph2 = rnd.uniform(0, 6.3), rnd.uniform(0, 6.3)
        amp = sw * span
        tops = []
        for i in range(period):
            u = 2 * math.pi * i / period
            yc = y0 + span * cf + amp * math.sin(f1 * u + ph1) + 0.45 * amp * math.sin(f2 * u + ph2)
            tops.append(2 * round(yc / 2))
        sid = f"{name}{b}"
        p.defs.append(f'<path id="{sid}" stroke-width="2" d="{_band(x0, tops)}"/>')
        glow = "".join(_strip(sid, dy, f'{tone[t][i]}" stroke-opacity="{num(a)}') for dy, t, i, a in GLOW
                       if dy not in outer)
        curtain = "".join(_strip(sid, dy, f"url(#{pats[j - 1]})") for dy, j in STREAKS
                          if pats and b < 2 and dy not in outer)
        curtain += "".join(_strip(sid, 6 + 2 * j, f"url(#{pid})") for j, pid in enumerate(pats[:n - bool(outer)]))
        a = bright * (1.0 if strong else 0.75)
        parts.append((a, glow, curtain))

    def dim(a, s):
        return s if a > 0.97 else f'<g opacity="{num(round(a * 25) / 25)}">{s}</g>'
    still = "".join(dim(a, g + c) for a, g, c in parts)
    if not motion:
        p.raw(z, still, still)
        return
    beat = min(0.12, DRIFT / period)   # seconds a step: the whole drift takes no longer than DRIFT
    fine = min((d for d in range(12, 40) if period % d == 0), key=lambda d: abs(d * d - period), default=period)
    shimmer = ("1;.7;1;.55;.9", ".75;1;.6;1;1", "1;1;.65;.85;1")
    field = "".join(dim(a, g + (f'<g>{c}<animate attributeName="opacity" values="{shimmer[b]}" '
                                f'dur="{2.1 + 0.6 * b:.1f}s" repeatCount="indefinite" calcMode="discrete"/></g>'
                                if c else "")) for b, (a, g, c) in enumerate(parts))
    cid, gid = f"{name}c", f"{name}g"
    inner = ";".join(f"{i} 0" for i in range(fine))
    outer = ";".join(f"{i} 0" for i in range(0, period, fine))
    p.raw(z, f'<clipPath id="{cid}"><rect x="{x0}" y="{y0 - 8}" width="{period}" height="{span + 40}"/></clipPath>'
             f'<g clip-path="url(#{cid})"><g><g><g id="{gid}">{field}</g><use href="#{gid}" x="-{period}"/>'
             f'<animateTransform attributeName="transform" type="translate" values="{inner}" dur="{num(fine * beat)}s" '
             f'repeatCount="indefinite" calcMode="discrete"/></g><animateTransform attributeName="transform" '
             f'type="translate" values="{outer}" dur="{num(period * beat)}s" repeatCount="indefinite" '
             f'calcMode="discrete"/></g></g>', still)


# --------------------------------------------------------------------------- the frame
# One tile of the carved border, five pixels deep and fourteen along: two strands plaited over and under each
# other, a link of the plait each way, each strand lit along its upper and left edges (L), its face (F) and its
# shaded edge (S), the ground cut away dark (g) and the groove where a strand dives under the other darker
# still (d). Laid along a side the tile is turned a quarter, so its light still falls from the upper left.
KNOT = ["LLggLLLLLLLggL",
        "SSdLFSgggLddLS",
        "ggLFSgggggLLSg",
        "LLSSdLgggLFSdL",
        "SSggLSLLLSSggL"]
BAND = len(KNOT)


def _knotwork(uid: str, W: list) -> str:
    """The border's tile as a pattern, running along the top. Down a side it is laid with its axes swapped
    (see `frame`), which turns it a quarter and keeps its light in the upper left."""
    tone = {"L": W[6], "F": W[4], "S": W[3], "d": W[0], "g": W[1]}
    cells = {}
    for j, row in enumerate(KNOT):
        for i, ch in enumerate(row):
            cells[(i, j)] = tone[ch]
    paths = "".join(f'<path stroke="{c}" d="{Pix._d(rows)}"/>' for c, rows in _by_colour(cells).items())
    return f'<pattern id="{uid}" width="{len(KNOT[0])}" height="{BAND}" patternUnits="userSpaceOnUse">{paths}</pattern>'


def _by_colour(cells: dict) -> dict:
    out: dict = {}
    for (x, y), c in cells.items():
        out.setdefault(c, {}).setdefault(y, []).append(x)
    return out


# The beast on a ship's prow, risen at the sheet's top left corner over the gunwale, 40 by 28, facing in
# toward the title: its neck rising out of the border down the side with a crest of carved scales (k O),
# its ear curled back in a spiral, a heavy brow over a bronze eye (e p, glint w), the snout curling up at
# its tip with a flared nostril, the jaws open on rows of teeth (t) round a dark gullet (q) and a red tongue
# lolling out and curling (r R); carved oak, lit (O o), its face (f), shaded (m s d), cut dark (k).
PROW = [
    "..kkkk..................................",
    ".kOOOOk.....kkkkk.......................",
    "kOokkOok..kkOOOOOkk..................kk.",
    "kOk..kOk.kOooooooOOkk...............kOOk",
    "kOkkk.ok.kOooooooooOOkkkkkkkkkkkkkkkoOk.",
    "kOOOk.okkOoooookkkoooooOOOOOOOOOOOOOook.",
    ".kOOokkkoooooookepkooooooooooodooooooook",
    ".kkOOoooooooooodkwkooooooooooodkoooooddk",
    "kOOkkOoooooooooddkfffffffffffffffffffsk.",
    "kOOmkkffoooooooooofsktktktktktktktktkk..",
    "kOmmsdkfffffffffffssqqqqqqqqqqqqqqqqk...",
    "kOomsdkkfffffffffsskqqqqqqqqqqqrrrrrrrk.",
    ".kOmsdk.kffffffffsskqqqqqqrrrrrRRkkRrk..",
    ".kOmsdk.kfffffffsssktqtqtqtqtqkkk..rk...",
    "kOOmsdk..kkffffsssssssssssssskk...rrk...",
    "kOmmsdk....kkkkkkkkkkkkkkkkkkk....kk....",
    "kOmmsdk.................................",
    "kOomsdk.................................",
    ".kOmsdk.................................",
    "kOOkkdk.................................",
    "kOmmsdk.................................",
    "kOomsdk.................................",
    ".kOmsdk.................................",
    "kOOkkdk.................................",
    "kOmmsdk.................................",
    "kOomsdk.................................",
    ".kOmsdk.................................",
    "kkkkkkk.................................",
]


def prow_head(p: Pix, x, y, night, flip=False):
    """The prow beast at a top corner, top-left at (x, y), facing in toward the title; `flip` turns it to
    face left. It is drawn once a file and placed, on a layer over the gunwale, whose ends it covers."""
    W = wood(night)
    k = -1 if night else 0
    pal = {"k": W[0], "O": W[6], "o": W[5], "f": W[4], "m": W[3], "s": W[2], "d": W[1], "e": BRONZE[5],
           "p": IRON[0], "w": C["white"], "t": CREAM[6 + k], "q": RED[0], "r": RED[4 + k], "R": RED[2]}
    key = ("prow", night)
    if key not in p.syms:
        p.symbol(key, {(i, j): pal[ch] for j, row in enumerate(PROW) for i, ch in enumerate(row) if ch in pal})
    L = p.layer("prow", z=6)
    if flip:
        p.shapes[L].append(f'<use href="#{p.syms[key]}" transform="matrix(-1 0 0 1 {x + len(PROW[0])} {y})"/>')
    else:
        p.use(key, x, y, L)


def frame(p: Pix, night: bool, heads: bool = False, strake: int = 4, uid="fr"):
    """The sheet's border in carved oak: a plait of two strands down the sides and along the top, a prow
    beast risen at each top corner on a header (`heads`) and an iron boss at each top corner of any other
    sheet, and along the foot the lower strake of a hull, `strake` rows: a plank standing proud of the one
    above it, its upper edge lit and the clinker rivets along it. A footer has none (`strake` 0), for it
    stands on the fjord's water (see `footing`). The top is one tile placed along it, and each side the same
    tile laid with its axes swapped, so the border costs a few hundred bytes however long it runs."""
    w, h = p.w, p.h
    W = wood(night)
    k = -1 if night else 0
    top = h - strake
    p.defs.append(_knotwork(uid + "h", W))
    # A side kept in the defs, its axes swapped, and placed with a use, so the tiles start where it does on
    # either side.
    p.defs.append(f'<rect id="{uid}V" width="{top}" height="{BAND}" fill="url(#{uid}h)" '
                  f'transform="matrix(0 1 1 0 0 0)"/>')
    for bx in (0, w - BAND):
        p.shapes["base"].append(f'<use href="#{uid}V" x="{bx}"/>')
    p.shapes["base"].append(f'<rect width="{w}" height="{BAND}" fill="url(#{uid}h)"/>')
    if strake:
        p.defs.append(_strake(uid + "s", W, strake, night))
        p.shapes["base"].append(f'<rect y="{top}" width="{w}" height="{strake}" fill="url(#{uid}s)"/>')
    if heads:
        prow_head(p, 0, 0, night)
        prow_head(p, w - len(PROW[0]), 0, night, flip=True)
        return
    for cx in (2, w - 3):
        p.rect(cx - 2, 0, 5, 5, W[0])
        for (dx, dy, c) in ((-1, -1, IRON[6 + k]), (0, -1, IRON[5 + k]), (-1, 0, IRON[5 + k]), (0, 0, IRON[4 + k]),
                            (1, 0, IRON[2 + k]), (0, 1, IRON[2 + k]), (1, 1, IRON[1]), (1, -1, IRON[4 + k]),
                            (-1, 1, IRON[3 + k])):
            p.px(cx + dx, 2 + dy, c)


def _strake(uid: str, W: list, rows: int, night: bool) -> str:
    """A pattern tile of the lower strake, 8 wide: its upper edge lit, its face, its foot dark, and a clinker
    rivet with its shadow every eight pixels."""
    k = -1 if night else 0
    cols: dict = {}
    ry = 2 if rows > 4 else 1
    for xx in range(8):
        for yy in range(rows):
            c = W[5] if yy == 0 else W[0] if yy == rows - 1 else W[2] if yy == rows - 2 else W[3]
            if (xx, yy) == (2, ry):
                c = IRON[6 + k]
            elif (xx, yy) == (3, ry):
                c = IRON[4 + k]
            elif (xx, yy) == (2, ry + 1):
                c = IRON[3 + k]
            elif (xx, yy) == (3, ry + 1):
                c = IRON[1]
            cols.setdefault(c, {}).setdefault(yy, []).append(xx)
    paths = "".join(f'<path stroke="{c}" d="{Pix._d(r)}"/>' for c, r in cols.items())
    return f'<pattern id="{uid}" width="8" height="{rows}" patternUnits="userSpaceOnUse">{paths}</pattern>'


# --------------------------------------------------------------------------- shields
# How a round shield is painted, by name: each a function of (dx, dy) from the centre and the radius to the
# paint ramp it takes there.
def _paint(kind: int, dx, dy, r):
    R, O, Cr, T = RED, OCHRE, CREAM, TAR
    if kind == 0:
        return R
    if kind == 1:
        return O if (dx < 0) == (dy < 0) else T
    if kind == 2:
        return Cr if dx < 0 else R
    if kind == 3:
        return Cr if abs(dx) < r * 0.3 or abs(dy) < r * 0.3 else R
    if kind == 4:
        return R if (dx < 0) == (dy < 0) else Cr
    if kind == 5:
        return O if dy < 0 else T
    if kind == 6:
        a = math.atan2(dy, dx)
        return R if int((a + math.pi) / (math.pi / 4)) % 2 else O
    return T if dy < 0 else Cr


def shield_cells(kind: int, r: float, night: bool, boss: bool = True) -> dict:
    """A round painted shield of radius `r` as cells about its centre: its paint lit toward the upper left
    and shaded toward the lower right, a dark rim, and an iron boss in the middle catching the light."""
    k = -1 if night else 0
    cells = {}
    rr = math.ceil(r)
    for yy in range(-rr, rr + 1):
        for xx in range(-rr, rr + 1):
            dx, dy = xx + 0.5, yy + 0.5
            d = math.hypot(dx, dy)
            if d > r + 0.2:
                continue
            ramp = _paint(kind, dx, dy, r)
            if d > r - 0.9:
                t = 1 if ramp is TAR else 0
                cells[(xx, yy)] = ramp[max(0, t + k)] if ramp is not TAR else TAR[0]
                continue
            facing = (dx * -0.6 + dy * -0.8) / max(0.5, d)
            base = 5 if ramp is CREAM else 3 if ramp is not TAR else 2
            t = base + (1 if facing > 0.45 and d > r * 0.4 else 0)
            cells[(xx, yy)] = ramp[max(0, min(6, t + k))]
    if boss:
        br = 1.6 if r >= 4 else 1.1
        for yy in range(-2, 2):
            for xx in range(-2, 2):
                dx, dy = xx + 0.5, yy + 0.5
                d = math.hypot(dx, dy)
                if d <= br:
                    facing = (dx * -0.6 + dy * -0.8) / max(0.3, d)
                    cells[(xx, yy)] = IRON[6 if facing > 0.4 and d < br - 0.4 else 5 if facing > 0 else 2 + k]
        if r >= 4:
            cells[(-1, -1)] = IRON[6]
    return cells


def shield_symbol(p: Pix, kind: int, r: float, night: bool, boss: bool = True):
    key = ("shield", kind, r, night, boss)
    if key not in p.syms:
        p.symbol(key, shield_cells(kind, r, night, boss))
    return key


def shield(p: Pix, cx, cy, kind, r, night, L="base", boss=True):
    """A painted round shield of radius `r` centred on (cx, cy), drawn once a file and placed."""
    p.use(shield_symbol(p, kind, r, night, boss), cx, cy, L)


def hang(p: Pix, cx, cy, kind, r, night, L="base"):
    """A painted round shield of radius `r` centred on (cx, cy), set in pixels over whatever lies under it: a
    ship's row of shields, which share their paints' paths with her hull rather than each its own symbol."""
    for (dx, dy), c in shield_cells(kind, r, night).items():
        p.px(cx + dx, cy + dy, c, L)


def gunwale(p: Pix, x0, x1, y, night, seed=0, spacing=7, twinkling=True, uid="gw", clear=None):
    """The row of shields hung along a gunwale across the sheet's top, from x0 to x1 with the rail at row y:
    a rail of oak riveted with iron, and under it round shields painted red, black, yellow and white,
    quartered and halved by turns, each overlapping the last as they hang on a ship, their iron bosses
    catching the light. Six shields with their stretch of rail are drawn once as a tile the row repeats,
    the last one's edge wrapped under the first; in a moving header a glint on every other boss twinkles.
    Where `clear` names the columns (from, to) kept for the month's mark, the shields pause for it: the rail
    runs on behind the mark, and the shields end whole on either side, as far from its middle on the one side
    as on the other."""
    W = wood(night)
    k = -1 if night else 0
    rnd = random.Random(seed)
    kinds = list(range(8))
    rnd.shuffle(kinds)
    kinds = kinds[:6]
    tw = spacing * len(kinds)
    cells = {}
    for xx in range(tw):
        cells[(xx, 0)], cells[(xx, 1)] = W[5], W[2]
    for xx in range(2, tw, 14):
        cells[(xx, 0)], cells[(xx, 1)] = IRON[6 + k], IRON[3 + k]
    for wrapped in (True, False):
        for i, kind in enumerate(kinds):
            if wrapped and i < len(kinds) - 1:
                continue
            for (dx, dy), c in shield_cells(kind, 4.2, night).items():
                xx = 4 + i * spacing + dx
                if (xx >= tw) == wrapped:
                    cells[(xx - tw if wrapped else xx, 5 + dy)] = c
    runs = [(x0, x1, x0)]     # each run of shields: its first column, the column after its last and its tile's origin
    if clear:
        lo, hi = clear
        n = (lo - 4 - (x0 + 4)) // spacing          # the last shield to end before the mark's columns
        last = x0 + 4 + n * spacing
        start = max(hi, (lo + hi) // 2 * 2 - (last + 3))
        runs = [(x0, last + 3, x0), (start, x1, start)]
        # the last shield's right edge, which the tile leaves under the next shield's left, and the bare rail
        for (dx, dy), c in shield_cells(kinds[n % len(kinds)], 4.2, night).items():
            if dx == 3:
                p.px(last + 3, y + 5 + dy, c)
        p.hline(last + 3, start, y, W[5])
        p.hline(last + 3, start, y + 1, W[2])
    p.defs.append(f'<pattern id="{uid}" x="{x0}" y="{y}" width="{tw}" height="9" patternUnits="userSpaceOnUse">'
                  f'{p._paths(cells)}</pattern>')
    for a, b, o in runs:
        d = (o - x0) % tw       # a run after the pause is shifted along to start on a whole shield
        p.shapes["base"].append(f'<rect x="{a - d}" y="{y}" width="{b - a}" height="9" fill="url(#{uid})"'
                                + (f' transform="translate({d})"/>' if d else "/>"))
    if twinkling:
        bosses = [cx for a, b, o in runs for cx in range(o + 4, b - 3, spacing * (6 if p.lite else 2))]
        for i, cx in enumerate(bosses):
            p.px(cx - 1, y + 4, C["white"], p.twinkle(i))


# --------------------------------------------------------------------------- the carved title
def inlay_fill(r, c, scale, night):
    """Bronze inlaid in the carved letters by night: a band for each row of the face, bright where the
    firelight catches the crown of each stroke and across its middle, deeper between."""
    B = BRONZE
    band = min(6, r // scale)
    return (B[5], B[4], B[3], B[5], B[4], B[3], B[2])[band]


INLAY = Paint("inlay", inlay_fill)


def _strung(p: Pix, key, s, scale, glyph, units):
    """A line of `s` kept once in <defs> under `key`: the symbol `glyph(ch)` names for each letter, placed along
    the line at the letter's advance, `units` to a pixel of the face (1 when the line is scaled as a whole, else
    `scale`). Returns `key`."""
    if key not in p.syms:
        glyphs, _, space = FONTS["57"]
        uses, cx = [], 0
        for ch in fold(s, "57"):
            if ch == " ":
                cx += (space + 1) * units
                continue
            uses.append(f'<use href="#{p.syms[glyph(ch)]}"' + (f' x="{cx}"' if cx else "") + "/>")
            cx += (glyphs[ch][0] + 1) * units
        body = "".join(uses)
        p.symbol(key, shapes=body if units == scale else f'<g transform="scale({scale})">{body}</g>')
    return key


def line(p: Pix, s, scale):
    """A line of a carved title kept once in <defs>, so its shadow, the two faces of its cut and its letters each
    place it whole rather than letter by letter: the glyphs of `s` along it, scaled by `scale`. Returns its key."""
    glyphs = FONTS["57"][0]

    def glyph(ch):
        key = ("glyph", "57", ch)
        if key not in p.syms:
            p.symbol(key, {(col, r): 1 for r, cols in enumerate(glyphs[ch][1]) for col in cols}, mono=True)
        return key
    return _strung(p, ("line", fold(s, "57"), scale), s, scale, glyph, 1)


def carve(p: Pix, x, y, s, scale, light, dark, L="base", shadow=None):
    """The cut of a chip-carved title, drawn before its letters: the letter again a step up in `light`, the
    cut's upper face where it catches the light, a step down in `dark`, its lower face in shade, and under
    both the `shadow` the letter throws, a step down and to the right; any of the three is left out when
    None. Each is the title's line (see `line`) placed once."""
    key = line(p, s, scale)
    off = max(1, round(scale / 2))
    for dx, dy, c in ((off, off + 1, shadow), (0, off, dark), (0, -off, light)):
        if c:
            p.use(key, x + dx, y + dy, L, stroke=c)


def letters(p: Pix, x, y, s, c, scale, L="base", **kw) -> int:
    """A title's letters over its cut: set as the kit sets a title, so the box they take is kept clear of every
    sprite and their paint is the kit's, and then, when they are lettered in one stroke, placed whole as the
    line `carve` placed rather than glyph by glyph. Returns their width."""
    n = len(p.uses.get(L, ()))
    w = p.text(x, y, s, c, "57", scale, L=L, **kw)
    strokes = {u[0] for u in p.uses[L][n:]} if L in p.uses else set()
    if len(strokes) == 1:
        del p.uses[L][n:]
        p.use(line(p, s, scale), x, y, L, stroke=strokes.pop())
    return w


def facets(p: Pix, x, y, s, scale, lit, L="base"):
    """The lit face of a chip-carved title, drawn over its letters: each stroke cut to a ridge, the half of it
    nearer its upper or left edge turned to the light (in `lit`) and the half nearer its lower or right edge
    left in the letter's own dark. Each letter's face is drawn once a file, and the line of them kept once
    and placed."""
    glyphs = FONTS["57"][0]
    top = p.layer(L + "~", None, z=0.3)

    def facet(ch):
        key = ("facet", ch, scale)
        if key not in p.syms:
            cells = {(col * scale + dx, r * scale + dy) for r, cols in enumerate(glyphs[ch][1]) for col in cols
                     for dy in range(scale) for dx in range(scale)}
            face = {}
            for (fx, fy) in cells:
                def run(dx, dy):
                    n = 0
                    while (fx + dx * (n + 1), fy + dy * (n + 1)) in cells:
                        n += 1
                    return n
                if min(run(0, -1), run(-1, 0)) < min(run(0, 1), run(1, 0)):
                    face[(fx, fy)] = 1
            p.symbol(key, face, mono=True)
        return key
    p.use(_strung(p, ("facets", fold(s, "57"), scale), s, scale, facet, scale), x, y, top, stroke=lit)


def glints(p: Pix, x, y, s, scale):
    """Here and there a glint where the inlay catches the firelight: on every third letter whose top row
    has ink (every ninth on a drawing made lighter), at its top-left, twinkling in a moving file."""
    glyphs, _, space = FONTS["57"]
    every = 9 if p.lite else 3
    cx, n = x, 0
    for i, ch in enumerate(fold(s, "57")):
        if ch == " ":
            cx += (space + 1) * scale
            continue
        g = glyphs[ch]
        if i % every == 1 and g[1][0]:
            sparkle(p, cx + min(g[1][0]) * scale + 1, y + 1, L=p.twinkle(n), warm=True)
            n += 1
        cx += (g[0] + 1) * scale


# --------------------------------------------------------------------------- the sea and the fells
def sea(p: Pix, x0, x1, g, night, seed=3, motion=True, L="base", glitter=True):
    """The fjord along the foot of a scene, its surface at row g - 2 and its depth to g + 1: the sunlit water
    paler toward the surface, and crests that glitter in the sun by day (twinkling in a moving file) and lie
    dark by night, where only the moon's path shines (see `moonpath`)."""
    Wt = water(night)
    rnd = random.Random(seed)
    for y in range(g - 2, g + 2):
        t = (4 if y == g - 2 else 3 if y == g - 1 else 2 if y == g else 1)
        for x in range(x0, x1):
            p.px(x, y, Wt[t], L)
    n = max(3, (x1 - x0) // 6)
    for i in range(n):
        x = rnd.randrange(x0 + 1, x1 - 3)
        y = g - 2 + (0 if rnd.random() < 0.6 else 1)
        if night:
            if rnd.random() < 0.5:
                p.hline(x, x + 2, y, Wt[4 if y == g - 2 else 3], L)
            continue
        Lt = p.twinkle(i) if (motion and glitter) else L
        p.hline(x, x + rnd.choice((2, 2, 3)), y, Wt[6 if y == g - 2 else 5], Lt)


def moonpath(p: Pix, x, g, motion=True, L="base"):
    """The moon's light on the water under it: a shivering path of pale glints down the column at x, brightest
    on the surface, twinkling in a moving file."""
    for i, (dx, dy) in enumerate(((0, -2), (-1, -2), (2, -2), (1, -1), (-2, -1), (0, 0), (-1, 1), (2, 0), (1, -2))):
        Lt = p.twinkle(i, back=False) if motion else L
        p.px(x + dx, g + dy, MOON[4] if dy == -2 else MOON[3], Lt)


def fjord_wall(p: Pix, x0, x1, base, height, night, high_left=True, seed=4, sky=None, L="base"):
    """A wall of the fjord from x0 to x1 rising from the water at row `base`: a mountain `height` rows high at
    its outer end (the left when `high_left`) falling in crags and shoulders toward the other, lit on the
    faces that turn to the light, in shadow on those that turn away, gullies scored down it, and snow on its
    heights, by night the snow green under the aurora. `sky`, when given, is the highest row each column may
    reach (where the words above leave off); the whole wall is lowered to keep under it. Drawn as a few
    shapes, so a mountain costs no more than a hill."""
    F = fells(night)
    rnd = random.Random(seed)
    w = x1 - x0
    ph = [rnd.uniform(0, 6.3) for _ in range(3)]
    hs = []
    for i in range(w):
        u = (w - 1 - i) / (w - 1) if not high_left else i / (w - 1)
        h = 1.0 - 0.78 * u ** 1.15
        h += 0.09 * math.sin(2 * math.pi * 2.3 * u + ph[0]) + 0.05 * math.sin(2 * math.pi * 5.1 * u + ph[1])
        hs.append(max(0.06, h))
    scale = height
    if sky is not None:
        scale = min([height] + [(base - sky[i]) / hs[i] for i in range(w)])
    if scale < 6:
        return []
    tops = [base - max(1, round(scale * h)) for h in hs]
    face, lit, shade = (F[3], F[4], F[2]) if not night else (F[2], F[3], F[1])
    snow, snow_shade = (F[6], F[5]) if not night else (X["snow_night"], F[5])
    # the faces turned to the light (the ground rising to the right) and those turned away
    lit_t, shade_t = [], []
    for i in range(w):
        rising = i + 1 < w and tops[i + 1] < tops[i] or (i and tops[i] < tops[i - 1])
        lit_t.append(min(base, tops[i] + (6 + (i * 7) % 5 if rising == high_left else 1)))
        shade_t.append(base if rising == high_left else min(base, tops[i] + 2))
    # snow on the heights, deeper on the faces in the light
    line = base - scale * 0.55
    deep = [max(0, min(4, base - tops[i], round((line - tops[i]) / 3))) for i in range(w)]
    foot = [tops[i] + deep[i] for i in range(w)]
    # Laid from the top down, each from where the one above it leaves off to the water: the whole wall in snow,
    # the light from the snow's foot, the face from the light's, and the shade where the faces turn away. So
    # the outline of its heights is drawn once.
    _fill(p, L, snow, x0, tops, base)
    _fill(p, L, lit, x0, foot, base)
    _fill(p, L, face, x0, [max(a, b) for a, b in zip(lit_t, foot)], base)
    _fill(p, L, shade, x0, [max(a, b) if a < base else base for a, b in zip(shade_t, foot)], base)
    for i in range(w):
        if deep[i] > 1 and (i * 5 + seed) % 7 < 2 and not p.lite:
            p.px(x0 + i, tops[i] + deep[i], snow_shade, L)
    # gullies scored down the face
    for j in range(max(1, w // 12)):
        i = (j * 12 + rnd.randrange(6)) % w
        y0 = tops[i] + deep[i] + 2
        p.vline(x0 + i, y0, min(base, y0 + rnd.randint(4, 9)), shade if not night else F[1], L)
    return tops


def _fill(p: Pix, L, paint, x0, tops, base):
    """Each run of columns from x0 on whose top (tops[i]) lies above row `base`, filled down to it."""
    for a, b in _runs([t < base for t in tops]):
        _region(p, L, paint, x0 + a, tops[a:b], [base] * (b - a))


def _runs(flags) -> list:
    """The runs of True in a list of flags, as (start, end) pairs."""
    out, start = [], None
    for i, f in enumerate(list(flags) + [False]):
        if f and start is None:
            start = i
        elif not f and start is not None:
            out.append((start, i))
            start = None
    return out


# --------------------------------------------------------------------------- the longship
# The hero ship's dragon head, 12 by 11, facing right with its neck coming down at its left to meet the stem:
# carved oak (k cut, O o lit, f face, m s shade), a bronze eye (e) with its glint (w), the jaws open on teeth
# (t) round a dark gullet (q) and a red tongue curling out (r R).
STEM_HEAD = [
    ".kkk........",
    "kOOOk.kkk...",
    "kOkOkkOOOkk.",
    ".kOOoooooOOk",
    ".kOooookekOk",
    "kOooooookwok",
    "kOooffffffkk",
    "kOmktktktk..",
    "kOmsqqrrrrk.",
    "kOmskkkkRrrk",
    "kOmsk...krk.",
]
# The stern post's scroll, 8 by 8: the post rising from the hull and rolling forward on itself.
STERN = [
    "..kkkk..",
    ".kOOOOk.",
    "kOkkkkOk",
    "kOkOOkOk",
    "kOkkOkOk",
    "kOk.kkOk",
    "kOk..kk.",
    "kOk.....",
]


def _carved(night: bool) -> dict:
    """The palette of carved oak sprites: cut, lit, face and shade, bronze eyes, teeth, gullet and tongue."""
    W = wood(night)
    k = -1 if night else 0
    return {"k": W[0], "O": W[6], "o": W[5], "f": W[4], "m": W[3], "s": W[2], "d": W[1], "e": BRONZE[5],
            "p": IRON[0], "w": C["white"], "t": CREAM[6 + k], "q": RED[0], "r": RED[4 + k], "R": RED[2]}


def _sail(p: Pix, x0, top, w, h, night, L, uid="sl"):
    """A square sail of red and cream stripes `w` wide hanging `h` rows under its yard at row `top`,
    bellied so its foot rises toward the clews: one shape filled with a pattern of stripes, lit down its
    weather edge and across its belly, shaded down its lee, along its foot and under the yard. Returns the
    foot row of each column."""
    k = -1 if night else 0
    tops = [top + 1] * w
    foots = [top + h - round(3 * abs(2 * i / (w - 1) - 1) ** 3) for i in range(w)]
    p.defs.append(f'<pattern id="{uid}" x="{x0}" width="6" height="1" patternUnits="userSpaceOnUse">'
                  f'<path stroke="{RED[3 + k]}" d="M0 .5h3"/><path stroke="{CREAM[5 + k]}" d="M3 .5h3"/></pattern>')
    _region(p, L, f"url(#{uid})", x0, tops, foots)
    light, shade = C["white"], X["shade_ink"]
    for c, a, i0, i1, band in ((light, 0.22, 0, 3, None), (light, 0.1, 3, 10, None), (shade, 0.14, w - 9, w, None),
                               (shade, 0.22, w - 4, w, None), (shade, 0.24, 0, w, "foot"), (shade, 0.3, 0, w, "top")):
        t, f = tops[i0:i1], foots[i0:i1]
        if band == "foot":
            t = [ff - 2 for ff in f]
        elif band == "top":
            f = [tt + 1 for tt in t]
        _region(p, L, f'{c}" fill-opacity="{num(a)}', x0 + i0, t, f)
    return foots


def hero_ship(p: Pix, x0, g, night, motion=True, room=60, phase=0):
    """The longship under sail, the hero of a wide header: 50 wide from x0, her waterline at row g - 2. A tarred
    clinker hull of four strakes sweeping up to her ends under an oak gunwale, the stern post rolling forward
    into a scroll and the stem rising in a curve to a carved dragon's head with open jaws; a row of painted
    shields along the gunwale with the crew's helms between them, the oars out with their blades in the
    water and the steersman at the steering oar; a great sail of red and cream stripes bellied on its yard,
    with the stays to her ends. She rides the swell in a moving header, the sea's near edge in front of her
    keel; the water curls white at her bow and flings spray that glitters, and her wake runs out astern.
    Built to the `room` of rows free of words above the water: with 52 rows or more the sail stands full;
    with fewer it is shortened, under 34 it is furled on its lowered yard, under 26 the mast is down and she
    rows, and under 18 nothing is built. Returns the span of the rule she covers."""
    if room < 18:
        return None
    L = p.layer("ship", ("bob", [0, 0, 1, 1, 2, 2, 1, 1, 0, 0, -1, -1], 4.2) if motion else None, z=1)
    W = wood(night)
    T = TAR
    k = -1 if night else 0
    ws = g - 2                                   # the water's surface
    hx, n = x0 + 2, 42                           # the hull's first column and its length
    gys, kys = [], []
    for i in range(n):
        s = abs(2 * i / (n - 1) - 1)
        gys.append(ws - 7 - round(8 * s ** 2.4))
        kys.append(ws + 2 - round(5 * s ** 1.6))
    # the hull: an oak gunwale over four tarred strakes, each lapped over the next with its lap lit
    lap, face = (T[5], T[2]) if not night else (T[6], T[3])
    _region(p, L, face, hx, gys, [ky + 1 for ky in kys])
    for i, (gy, ky) in enumerate(zip(gys, kys)):
        p.px(hx + i, gy, OAK[5 + k], L)
        p.px(hx + i, gy + 1, OAK[2 + k], L)
        for d in (4, 7, 10):
            if gy + d < ky:
                p.px(hx + i, gy + d, lap, L)
        p.px(hx + i, ky, T[0], L)
    pal = _carved(night)
    # the stern post rolling into its scroll, and the stem curving up to its head
    rise = min(10, max(3, room - 34))
    for j in range(rise):
        for dx, c in ((0, W[0]), (1, W[6]), (2, W[3]), (3, W[0])):
            p.px(hx + dx - 1 - j // 4, gys[0] - 1 - j, c, L)
    p.sprite(hx - 1 - (rise - 1) // 4, gys[0] - rise - len(STERN), STERN, pal, 1, L)
    stem = min(12, max(4, room - 32))
    bx = hx + n - 1
    lean = [min(3, j // 3) for j in range(stem)]
    for j in range(stem):
        for dx, c in ((-1, W[0]), (0, W[6]), (1, W[3]), (2, W[0])):
            p.px(bx + dx - lean[j], gys[-1] - 1 - j, c, L)
    hx_ = bx - 1 - lean[-1]
    p.sprite(hx_, gys[-1] - stem - len(STEM_HEAD), STEM_HEAD, pal, 1, L)
    # the mast, the yard and the sail
    mx = hx + n // 2 - 1
    deck = gys[n // 2]
    if room >= 26:
        furled = room < 34
        sail_h = 0 if furled else min(26, room - 26)
        mast_h = (sail_h + 6) if not furled else min(12, room - 18)
        yard = deck - mast_h
        p.vline(mx, yard - 2, deck + 1, ROPE[4 + k], L)
        p.vline(mx + 1, yard - 2, deck + 1, ROPE[2 + k], L)
        p.px(mx, yard - 3, BRONZE[5], L)
        p.px(mx + 1, yard - 3, BRONZE[3], L)
        sx0, sw = mx - 13, 28
        if not furled:
            foots = _sail(p, sx0, yard, sw, sail_h, night, L)
            _line(p, sx0, foots[0] - 1, sx0 - 2, gys[max(0, sx0 - 2 - hx)] - 1, ROPE[2 + k], L)
            _line(p, sx0 + sw - 1, foots[-1] - 1, sx0 + sw + 2, gys[sx0 + sw + 2 - hx] - 1, ROPE[2 + k], L)
        else:
            for xx in range(sx0, sx0 + sw):
                band = (RED if (xx - sx0) // 3 % 2 == 0 else CREAM)
                p.px(xx, yard + 1, band[4 + k], L)
                p.px(xx, yard + 2, band[2 + k], L)
        p.hline(sx0 - 1, sx0 + sw + 1, yard, ROPE[4 + k], L)
        p.px(sx0 - 1, yard + 1, ROPE[2 + k], L)
        p.px(sx0 + sw, yard + 1, ROPE[2 + k], L)
        # the stays from the masthead down to the stern and to the stem
        _line(p, mx - 1, yard - 2, hx + 1 - (rise - 1) // 4, gys[0] - rise, ROPE[2 + k], L)
        _line(p, mx + 2, yard - 2, bx - 1 - lean[-1], gys[-1] - stem + 1, ROPE[2 + k], L)
    # the crew's helms, between where the shields will hang
    for cx in range(hx + 10, hx + n - 9, 10):
        gy = gys[cx - hx]
        for (dx, dy, c) in ((0, -2, IRON[6 + k]), (1, -2, IRON[4 + k]), (-1, -1, IRON[5 + k]), (0, -1, IRON[4 + k]),
                            (1, -1, IRON[3 + k]), (2, -1, IRON[2 + k])):
            p.px(cx + dx, gy + dy, c, L)
    # the oars through their ports, swept aft, their blades at the surface
    near = p.layer("near")
    Wt = water(night)
    foam = Wt[6] if not night else Wt[5]
    for j, ox in enumerate(range(hx + 10, hx + n - 7, 6)):
        oy = gys[ox - hx] + 6
        _line(p, ox, oy, ox - 6, ws - 1, OAK[5 + k] if j % 2 else OAK[4 + k], L)
        p.px(ox, oy, T[0], L)
        p.px(ox - 7, ws, OAK[4 + k], L)
        p.px(ox - 8, ws, OAK[3 + k], L)
        p.px(ox - 9, ws + 1, foam, near)
        p.px(ox - 6, ws + 1, foam, near)
    # the steersman at the stern and his oar
    steersman(p, hx + 4, gys[4] + 1, night, L)
    _line(p, hx + 8, gys[8] + 3, hx + 4, ws + 1, ROPE[3 + k], L)
    # the shields along the gunwale, hung last, over the oars' ports and the steering oar's head
    for i, cx in enumerate(range(hx + 7, hx + n - 6, 5)):
        hang(p, cx, gys[cx - hx] + 3, (i + phase) % 3, 2.6, night, L)
    # the sea's near edge in front of her keel, the bow wave and its spray, and the wake astern
    for yy in range(ws + 1, g + 2):
        for xx in range(x0, bx + 10):
            if p.get(xx, yy, near) is None:
                p.px(xx, yy, Wt[3 if yy == ws + 1 else 2 if yy == ws + 2 else 1], near)
    for (dx, dy) in ((1, 0), (2, 0), (3, 0), (4, 1), (5, 1), (0, 1), (2, -1), (3, -1), (1, -2), (6, 2), (7, 2), (8, 2)):
        p.px(bx + dx, ws + dy, foam, near)
    for i, (dx, dy) in enumerate(((3, -4), (5, -3), (6, -5), (2, -6), (8, -2), (7, -6))):
        p.px(bx + dx, ws + dy, foam if i % 2 else C["white"], p.twinkle(i) if motion else near)
    for xx in range(x0, bx - 2):
        if (xx * 7 + phase) % 9 < 3:
            p.px(xx, ws + 1 + (xx // 6) % 2, foam, near)
    return (x0 - 1, bx + 10)


# The great head on a rowing ship's stem, 18 by 15, facing right, its neck coming down at its left: the
# ear rolled back, the brow over a bronze eye (e, glint w), the snout's nostril, and the jaws open on two rows
# of teeth (t) round a dark gullet (q) with the tongue lolling over the lower jaw (r R); carved oak.
BOW_HEAD = [
    "....kkkk..........",
    "...kOOOOk..kkk....",
    "..kOkkkOkkOOOOkk..",
    "..kOk.kOOooooooOk.",
    "...kkkOoooooooooOk",
    "....kOooooookkdoOk",
    "...kOoooooookekook",
    "..kOoooooooookwdok",
    "..kOooofffffffffkk",
    "..kOomkktktktktk..",
    ".kOmsqqqqqqqqrrrk.",
    ".kOmsqqqqrrrrRRrrk",
    ".kOmskttktktkkRrk.",
    ".kOmsfffffffkk.rk.",
    ".kOmsssssskk......",
]
# A ship's lantern, 5 by 7, hung from its hook: an iron frame round panes of horn (f F), lit by night.
LANTERN = ["..k..", ".kkk.", "kfFfk", "kFFFk", "kfFfk", ".kkk.", "..k.."]


def rowing_ship(p: Pix, x0, g, night, motion=True, room=60, n=66, phase=2):
    """A longship rowing in with her mast stowed, beside a section's title, 90 wide from x0, her waterline at
    row g - 2: the tarred hull of the hero's own make, the stern scrolled, the stem rising tall to a great
    carved head with its jaws open, the sail furled on its yard and laid along the deck on its crutches, a row
    of painted shields with the crew's helms between them, the oars biting, the steersman at the stern, and
    a lantern hung from the stem, cold horn by day and by night burning, flickering, its light on the hull
    and shivering on the water. She rides the swell in a moving header. Built to `room`: the stem is shorter
    as it shrinks, under 26 rows the head is the hero's smaller one and under 24 her shields are shipped;
    under 18 nothing stands. Returns the span of the rule she covers."""
    if room < 18:
        return None
    L = p.layer("ship", ("bob", [0, 0, 1, 1, 2, 2, 1, 1, 0, 0, -1, -1], 4.6) if motion else None, z=1)
    W, T = wood(night), TAR
    k = -1 if night else 0
    ws = g - 2
    hx = x0 + 3
    gys, kys = [], []
    for i in range(n):
        s = abs(2 * i / (n - 1) - 1)
        gys.append(ws - 6 - round(7 * s ** 2.8))
        kys.append(ws + 2 - round(4 * s ** 1.8))
    lap, face = (T[5], T[2]) if not night else (T[6], T[3])
    _region(p, L, face, hx, gys, [ky + 1 for ky in kys])
    for i, (gy, ky) in enumerate(zip(gys, kys)):
        p.px(hx + i, gy, OAK[5 + k], L)
        p.px(hx + i, gy + 1, OAK[2 + k], L)
        for d in (4, 7):
            if gy + d < ky:
                p.px(hx + i, gy + d, lap, L)
        p.px(hx + i, ky, T[0], L)
    pal = _carved(night)
    rise = min(6, max(2, room - 30))
    for j in range(rise):
        for dx, c in ((0, W[0]), (1, W[6]), (2, W[3]), (3, W[0])):
            p.px(hx + dx - 1 - j // 4, gys[0] - 1 - j, c, L)
    p.sprite(hx - 1 - (rise - 1) // 4, gys[0] - rise - len(STERN), STERN, pal, 1, L)
    big = room >= 26
    head = BOW_HEAD if big else STEM_HEAD
    stem = min(16, max(4, room - 30)) if big else min(9, max(3, room - 18))
    bx = hx + n - 1
    lean = [min(4, j // 3) for j in range(stem)]
    for j in range(stem):
        for dx, c in ((-1, W[0]), (0, W[6]), (1, W[3]), (2, W[0])):
            p.px(bx + dx + lean[j], gys[-1] - 1 - j, c, L)
    top = gys[-1] - stem - len(head)
    p.sprite(bx - (1 if big else 1) + lean[-1] - (1 if big else 0), top, head, pal, 1, L)
    # the mast and the yard stowed along the deck on their crutches, the sail furled on the yard
    deck = min(gys[8:n - 8]) - 3
    for cx in (hx + 14, hx + n - 18):
        p.vline(cx, deck + 1, gys[cx - hx], ROPE[2 + k], L)
    p.hline(hx + 6, hx + n - 10, deck, ROPE[4 + k], L)
    p.hline(hx + 6, hx + n - 10, deck + 1, ROPE[2 + k], L)
    for xx in range(hx + 11, hx + n - 15):
        band = RED if (xx - hx) // 3 % 2 else CREAM
        p.px(xx, deck - 1, band[4 + k], L)
        p.px(xx, deck - 2, band[3 + k], L)
    # helms, shields, oars and the steersman
    for cx in range(hx + 9, hx + n - 8, 9):
        gy = gys[cx - hx]
        for (dx, dy, c) in ((0, -2, IRON[6 + k]), (1, -2, IRON[4 + k]), (-1, -1, IRON[5 + k]), (0, -1, IRON[4 + k]),
                            (1, -1, IRON[3 + k]), (2, -1, IRON[2 + k])):
            p.px(cx + dx, gy + dy, c, L)
    kinds = (1, 0, 2, 5, 3)
    if room >= 24:
        for i, cx in enumerate(range(hx + 7, hx + n - 6, 5)):
            shield(p, cx, gys[cx - hx] + 3, kinds[(i + phase) % 3], 2.6, night, L)
    near = p.layer("near")
    Wt = water(night)
    foam = Wt[6] if not night else Wt[5]
    for j, ox in enumerate(range(hx + 10, hx + n - 7, 6)):
        oy = gys[ox - hx] + 6
        _line(p, ox, oy, ox - 6, ws - 1, OAK[5 + k] if j % 2 else OAK[4 + k], L)
        p.px(ox, oy, T[0], L)
        p.px(ox - 7, ws, OAK[4 + k], L)
        p.px(ox - 8, ws, OAK[3 + k], L)
        p.px(ox - 9, ws + 1, foam, near)
    steersman(p, hx + 4, gys[4] + 1, night, L)
    _line(p, hx + 8, gys[8] + 3, hx + 4, ws + 1, ROPE[3 + k], L)
    # the lantern hung from a hook on the stem's forward edge, halfway up it
    j = stem // 2
    lx, ly = bx + lean[j] + 3, gys[-1] - 1 - j
    p.px(lx, ly - 2, IRON[3 + k], L)
    p.px(lx + 1, ly - 2, IRON[3 + k], L)
    glass = {"k": IRON[4] if night else IRON[2], "f": FLAME[4] if night else OCHRE[1],
             "F": FLAME[5] if night else OCHRE[2]}
    p.sprite(lx, ly - 1, LANTERN, glass, 1, L)
    if night:
        Lf = p.flicker(phase)
        p.px(lx + 2, ly + 2, FLAME[6], Lf)
        p.px(lx + 2, ly + 1, FLAME[6], Lf)
        p.px(lx + 1, ly + 2, FLAME[5], Lf)
        glow(p, lx + 2.5, ly + 2.5, 14, 13, FLAME[3], (0.05, 0.1, 0.18), L=Lf)
        lamp(p, lx + 2.5, ly + 2.5, 22, phase, {(lx + i, ly - 1 + j) for j in range(7) for i in range(5)})
        glimmer(p, lx + 2, g, phase)
        for yy in range(ws, g + 1):
            for dx in (-1, 0, 1, 2, 3):
                if (yy + dx) % 2 == 0:
                    p.apx(lx + 2 + dx - (yy - ws) % 2, yy, FLAME[5], 0.8 if dx in (0, 1) else 0.45, Lf)
        p.px(lx + 2, ws, FLAME[6], Lf)
    # the sea's near edge in front of her keel, the bow wave, and the wake astern
    for yy in range(ws + 1, g + 2):
        for xx in range(x0, bx + 2):
            if p.get(xx, yy, near) is None:
                p.px(xx, yy, Wt[3 if yy == ws + 1 else 2 if yy == ws + 2 else 1], near)
    for (dx, dy) in ((1, 0), (2, 0), (3, 0), (4, 1), (5, 1), (0, 1), (2, -1), (3, -1), (6, 2), (7, 2)):
        p.px(bx + dx, ws + dy, foam, near)
    for xx in range(x0, bx - 2):
        if (xx * 7 + phase) % 9 < 3:
            p.px(xx, ws + 1 + (xx // 6) % 2, foam, near)
    return (x0 - 1, bx + 10)


# --------------------------------------------------------------------------- the dragon ship's bow
# The great carved head on a dragon ship's stem, facing left as she rows in, drawn from planes in its own units:
# its snout's tip at x 0 and the back of its skull at x 100, the top of its brow at y 0, so it draws at any size from
# a phone's to a section's. UPPER is its skull and upper jaw, LOWER its lower jaw hanging open, MOUTH the gullet
# between them and TONGUE lolling out over its lower jaw; BROW the ridge over its eye, EAR its ear swept back with its
# tip rolled, CREST three carved lobes down its nape, CURL its snout rolled up at the tip; LIP and JAW the lines its
# teeth stand along, and CHEEK a line carved along its cheek. It is tarred like the hull and picked out in ochre,
# its mouth painted red.
DRAGON = {
    "upper": ((4, 31), (1, 26), (3, 20), (9, 16), (18, 15), (28, 16), (38, 13), (46, 7), (54, 2), (62, 0), (70, 2),
              (78, 7), (86, 13), (94, 21), (100, 30), (101, 38), (96, 46), (88, 50), (78, 48), (66, 44), (57, 40),
              (45, 37), (31, 35), (17, 34), (8, 34)),
    "lower": ((62, 45), (50, 49), (37, 55), (25, 61), (15, 67), (9, 73), (12, 77), (24, 76), (40, 71), (56, 64),
              (70, 58), (82, 54), (90, 51), (82, 48), (70, 47)),
    "mouth": ((5, 34), (17, 35), (31, 36), (45, 38), (57, 41), (64, 45), (50, 49), (37, 55), (25, 61), (12, 69),
              (6, 56), (4, 42)),
    "tongue": ((58, 44), (44, 47), (30, 53), (19, 59), (11, 64), (3, 68), (-3, 72), (-7, 78), (-6, 86), (-1, 85),
               (0, 79), (5, 75), (13, 71), (24, 65), (36, 58), (50, 51)),
    "brow": ((46, 9), (54, 3), (64, 2), (74, 7), (79, 13), (69, 10), (59, 9), (50, 12)),
    "ear": ((76, 9), (86, 2), (98, -5), (110, -9), (120, -8), (124, -3), (121, 2), (116, 2), (117, -2), (113, -3),
            (104, 3), (93, 12), (86, 16)),
    "crest": (((96, 22), (108, 18), (112, 24), (102, 30)), ((99, 33), (111, 31), (113, 38), (102, 42)),
              ((95, 44), (106, 45), (106, 52), (95, 52))),
    "curl": ((6, 17), (3, 11), (6, 6), (12, 5), (16, 8), (15, 12), (11, 13), (10, 10), (8, 12), (9, 16)),
    "lip": ((0, 32), (17, 34), (31, 35), (45, 37), (57, 40), (66, 44), (78, 48), (88, 50)),
    "jaw": ((12, 69), (25, 61), (37, 55), (50, 49), (64, 45)),
    "cheek": ((62, 27), (70, 30), (80, 33), (90, 37), (97, 42)),
}
DRAGON_EYE = (63, 17, 7, 5)       # its centre and its radii
DRAGON_NOSTRIL = (10, 21)
DRAGON_NECK = (90, 46)            # where its neck leaves the back of its head
DRAGON_BOX = (-8, -10, 125, 87)   # the room it takes: (left, top, right, foot)


def _inside(poly, x, y) -> bool:
    n, hit = len(poly), False
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            hit = not hit
    return hit


def _along(line, x):
    """The height of a line, given as points left to right, at x; None off its ends."""
    for (x0, y0), (x1, y1) in zip(line, line[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / max(1e-9, x1 - x0)
    return None


def dragon_head(L: int, night: bool) -> dict:
    """The great carved head of the stem `L` units long, facing left, as {(x, y): colour} about its snout's tip at
    (0, 0) and the top of its brow (see DRAGON): tarred oak lit along its top, its brow, its ear and the lobes of its
    crest picked out in ochre, a line of ochre carved along its cheek, a bronze eye with its dark pupil and a glint,
    the gullet of its open jaws red and dark with teeth along both jaws and two fangs, and its tongue lolling out over
    its lower jaw and curling down; every edge drawn round in the tar's darkest."""
    return dict(_dragon_head(L, night))


@functools.lru_cache(maxsize=32)
def _dragon_head(L: int, night: bool) -> tuple:
    W, R, OC = TAR, RED, OCHRE
    k = -1 if night else 0
    f = L / 100
    D = DRAGON
    region = {}
    left, top, right, foot = DRAGON_BOX
    for py in range(math.floor(top * f) - 1, math.ceil(foot * f) + 1):
        for px in range(math.floor(left * f) - 1, math.ceil(right * f) + 1):
            x, y = (px + 0.5) / f, (py + 0.5) / f
            r = None
            if _inside(D["mouth"], x, y):
                r = "mouth"
            if _inside(D["tongue"], x, y):
                r = "tongue"
            if _inside(D["lower"], x, y):
                r = "lower"
            if _inside(D["ear"], x, y) or any(_inside(c, x, y) for c in D["crest"]):
                r = "ear"
            if _inside(D["upper"], x, y) or _inside(D["curl"], x, y):
                r = "upper"
            if _inside(D["brow"], x, y):
                r = "brow"
            if r:
                region[(px, py)] = r
    wood = {"upper", "lower", "ear", "brow"}
    out = {}
    for (px, py), r in region.items():
        up, down = region.get((px, py - 1)), region.get((px, py + 1))
        x, y = (px + 0.5) / f, (py + 0.5) / f
        if r == "mouth":
            c = R[0]
        elif r == "tongue":
            c = R[1] if down != "tongue" else R[5 + k] if up != "tongue" else R[3 + k]
        elif r == "brow":
            c = OC[5 + k] if up not in ("brow", "upper") else OC[4 + k]
        elif r == "ear":
            c = OC[5 + k] if up != "ear" else OC[2 + k] if down != "ear" else OC[3 + k]
        elif r == "upper":
            d = 0
            while region.get((px, py - d - 1)) in ("upper", "brow"):
                d += 1
            c = W[6] if d == 0 else W[5] if d < max(2, 4 * f) else W[4]
            lip = _along(D["lip"], x)
            if (lip is not None and y > lip - 8) or (x > 86 and c != W[6]):
                c = W[3]
        else:
            c = W[1] if down not in wood else W[2] if up not in wood else W[4] if x < 18 else W[3]
        out[(px, py)] = c
    for (px, py), r in region.items():
        nb = [region.get((px + dx, py + dy)) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        if r in wood and any(n is None or n in ("mouth", "tongue") for n in nb):
            out[(px, py)] = W[0]
        elif r == "tongue" and any(n is None for n in nb):
            out[(px, py)] = R[0]
    for tx in range(12, 60, 7):
        x0, y0 = round(tx * f), _along(D["lip"], tx)
        for dy in range(max(1, round(4 * f))):
            q = (x0, round(y0 * f) + dy)
            if region.get(q) == "mouth":
                out[q] = CREAM[6] if dy == 0 else CREAM[4 + k]
    for tx in range(16, 62, 8):
        x0, y0 = round(tx * f), _along(D["jaw"], tx)
        for dy in range(max(1, round(3 * f))):
            q = (x0, round(y0 * f) - 1 - dy)
            if region.get(q) == "mouth":
                out[q] = CREAM[5 + k]
    for (fx, fy, n, up) in ((13, 34, 8, False), (17, 66, 7, True)):
        for dy in range(max(2, round(n * f))):
            q = (round(fx * f), round(fy * f) + (-dy if up else dy))
            if region.get(q) in ("mouth", "tongue"):
                out[q] = CREAM[6]
    ex, ey, rx, ry = (v * f for v in DRAGON_EYE)
    for py in range(math.floor(ey - ry), math.ceil(ey + ry) + 1):
        for px in range(math.floor(ex - rx), math.ceil(ex + rx) + 1):
            dd = ((px + 0.5 - ex) / rx) ** 2 + ((py + 0.5 - ey) / ry) ** 2
            if dd <= 1:
                out[(px, py)] = W[0] if dd > 0.6 else BRONZE[5 + k] if py + 0.5 < ey else BRONZE[3 + k]
    pupil = round(ex - rx * 0.2)
    out[(pupil, round(ey))] = out[(pupil, round(ey) - 1)] = W[0]
    out[(round(ex - rx * 0.5), round(ey - ry * 0.45))] = CREAM[6]
    nx, ny = (round(v * f) for v in DRAGON_NOSTRIL)
    for q in ((nx, ny), (nx + 1, ny), (nx, ny + 1)):
        out[q] = W[0]
    for px in range(round(62 * f), round(97 * f)):
        y = _along(D["cheek"], px / f)
        if y is not None and region.get((px, round(y * f))) == "upper":
            out[(px, round(y * f))] = OC[3 + k]
    return tuple(out.items())


def stem_path(top, x_top, foot, x_foot, r_top, r_foot, sweep=1.0) -> dict:
    """The line of a dragon ship's stem from her forefoot at (x_foot, foot) up to the head's neck at (x_top, top), as
    {row: (the column of its middle, its half width)}, widening from `r_foot` to `r_top` under the head. At its
    fullest `sweep`, 1, it bows forward toward her bow all the way up; at 0 it rises upright from her forefoot and
    turns toward the head only in its upper half, to stand clear of words beside it."""
    return dict(_stem_path(top, x_top, foot, x_foot, r_top, r_foot, sweep))


@functools.lru_cache(maxsize=4096)
def _stem_path(top, x_top, foot, x_foot, r_top, r_foot, sweep) -> tuple:
    h = max(1, foot - top)
    lean = sweep * max(6, round(h * 0.11))
    start = 0.45 * (1 - sweep)
    out = []
    for y in range(top, foot + 1):
        t = (foot - y) / h
        u = max(0.0, min(1.0, (t - start) / (1 - start)))
        xc = x_foot + (x_top - x_foot) * u * u * (3 - 2 * u) - lean * math.sin(math.pi * t)
        out.append((y, (xc, r_foot + (r_top - r_foot) * t ** 1.8)))
    return tuple(out)


def stem(p: Pix, top, x_top, foot, x_foot, r_top, r_foot, sweep, night, L="base", crest=True):
    """The stem post of a dragon ship rising from her forefoot at (x_foot, foot) to the head's neck at (x_top, top):
    swept forward from her forefoot and up in an easy curve, convex toward her bow and as full as `sweep` (see
    `stem_path`), widening to `r_top` under the head; tarred oak lit down its forward edge and in shade down its
    after one, carved in chevrons of scales along it (left plain on a drawing made lighter), and down its back the
    lobes of the crest picked out in ochre. Returns the column of its middle at each row."""
    W, OC = TAR, OCHRE
    k = -1 if night else 0
    mid = {}
    for y, (xc, r) in stem_path(top, x_top, foot, x_foot, r_top, r_foot, sweep).items():
        a, b = math.floor(xc - r), math.ceil(xc + r)
        for x in range(a, b + 1):
            u = (x + 0.5 - (xc - r)) / max(1, 2 * r)
            c = W[0] if x in (a, b) else W[6] if u < 0.2 else W[5] if u < 0.4 else W[4] if u < 0.62 else \
                W[3] if u < 0.82 else W[2]
            if a < x < b and ((y - top) + abs(x - round(xc))) % 6 == 0 and not p.lite:
                c = W[1]
            p.px(x, y, c, L)
        if crest and (y - top) % 7 in (1, 2, 3) and y < foot - 12:
            for i, c in enumerate((OC[4 + k], OC[3 + k], W[0]) if (y - top) % 7 == 2 else (OC[3 + k], W[0])):
                p.px(b + 1 + i, y, c, L)
        mid[y] = round(xc)
    return mid


def stem_of(xb, ws, L, hx, hy, sweep=1.0) -> tuple:
    """The stem of a dragon ship with her forefoot at column xb on the water at row ws and her head `L` units long
    with its snout at (hx, hy), as full a curve as `sweep`: (top, its column there, foot, its column there, its half
    width under the head and at her forefoot, its sweep), for `stem` and `stem_path`."""
    f = L / 100
    nx, ny = round(hx + DRAGON_NECK[0] * f), round(hy + DRAGON_NECK[1] * f)
    return ny - round(4 * f), nx - round(3 * f), ws + 1, xb, max(4.0, 10 * f), 4.0, sweep


def lantern_of(xb, ws, L, hx, hy, sweep=1.0) -> tuple:
    """Where the lantern of a dragon ship (see `stem_of`) hangs from her stem's forward edge, a third of the way
    down from the head's neck to the water: (x, y, mid), the left of its glass and the row of its hook, and the
    column of the stem's middle there."""
    f = L / 100
    neck = round(hy + DRAGON_NECK[1] * f)
    ly = neck + (ws - neck) // 3
    mid = round(stem_path(*stem_of(xb, ws, L, hx, hy, sweep))[ly][0])
    return mid - round(max(3.0, 9 * f * 0.7)) - 6, ly, mid


def sheer_of(rise: int) -> int:
    """How far a dragon ship's gunwale sweeps up toward her stem over its run amidships, for a stem rising `rise`
    rows from the water to its head's neck: two fifths of it, at most 26."""
    return max(6, min(26, round(rise * 0.4)))


def prow_hero(p: Pix, xb, x1, g, night, motion, L, hx, hy, sweep=1.0, phase=2):
    """The dragon ship rowing in, the hero of a section: her bow coming in from the right, her tarred hull of four
    strakes under an oak gunwale running off the sheet, a row of painted shields along it with the crew's helms
    between them and the oars out biting the water, and from her forefoot at column xb her stem swept up to the
    great carved head (see `dragon_head`), `L` units long with its snout at (hx, hy), its jaws open over the words'
    side of the sheet; a lantern hung from the stem, cold horn by day and by night burning, flickering, its light on
    the stem and shivering on the water. The water curls white at her forefoot and her wake runs out behind her. She
    rides the swell in a moving header. Her stem's curve is as full as `sweep` (see `stem_path`). Returns the span of
    the rule she covers."""
    Ls = p.layer("ship", ("bob", [0, 0, 1, 1, 2, 2, 1, 1, 0, 0, -1, -1], 4.6) if motion else None, z=1)
    T = TAR
    k = -1 if night else 0
    ws = g - 2
    f = L / 100
    n = x1 + 2 - xb
    neck = (round(hx + DRAGON_NECK[0] * f), round(hy + DRAGON_NECK[1] * f))
    sheer = sheer_of(ws - neck[1])
    gys, kys = [], []
    for i in range(n):
        gys.append(ws - 9 - round(sheer * (1 - min(1.0, i / 46)) ** 2.4))
        kys.append(ws + 2 - round(7 * (1 - min(1.0, i / 30)) ** 2))
    lap, face = (T[5], T[2]) if not night else (T[6], T[3])
    _region(p, Ls, face, xb, gys, [ky + 1 for ky in kys])
    for i, (gy, ky) in enumerate(zip(gys, kys)):
        x = xb + i
        p.px(x, gy, OAK[5 + k], Ls)
        p.px(x, gy + 1, OAK[2 + k], Ls)
        for d in (4, 7, 10):
            if gy + d < ky:
                p.px(x, gy + d, lap, Ls)
        p.px(x, ky, T[0], Ls)
    for cx in range(xb + 12, x1, 8):
        gy = gys[cx - xb]
        for (dx, dy, c) in ((0, -2, IRON[6 + k]), (1, -2, IRON[4 + k]), (-1, -1, IRON[5 + k]), (0, -1, IRON[4 + k]),
                            (1, -1, IRON[3 + k]), (2, -1, IRON[2 + k])):
            p.px(cx + dx, gy + dy, c, Ls)
    near = p.layer("near")
    Wt = water(night)
    foam = Wt[6] if not night else Wt[5]
    for j, ox in enumerate(range(xb + 34, x1 - 2, 8)):
        oy = gys[ox - xb] + 7
        _line(p, ox, oy, ox - 7, ws - 1, OAK[5 + k] if j % 2 else OAK[4 + k], Ls)
        p.px(ox, oy, T[0], Ls)
        p.px(ox - 8, ws, OAK[4 + k], Ls)
        p.px(ox - 9, ws, OAK[3 + k], Ls)
        p.px(ox - 10, ws + 1, foam, near)
        p.px(ox - 7, ws + 1, foam, near)
    for i, cx in enumerate(range(xb + 8, x1 + 2, 6)):
        hang(p, cx, gys[cx - xb] + 4, (i + phase) % 5, 3.3, night, Ls)
    # the stem, from her forefoot up to the head's neck
    mid = stem(p, *stem_of(xb, ws, L, hx, hy, sweep), night, Ls)
    for (x, y), c in dragon_head(L, night).items():
        p.px(hx + x, hy + y, c, Ls)
    # the lantern on its hook on the stem's forward edge, a third of the way down from the head
    lx, ly, _ = lantern_of(xb, ws, L, hx, hy, sweep)
    p.hline(lx + 2, mid[ly] - 2, ly - 2, IRON[3 + k], Ls)
    glass = {"k": IRON[4] if night else IRON[2], "f": FLAME[4] if night else OCHRE[1],
             "F": FLAME[5] if night else OCHRE[2]}
    p.sprite(lx, ly - 1, LANTERN, glass, 1, Ls)
    if night:
        Lf = p.flicker(phase)
        p.px(lx + 2, ly + 2, FLAME[6], Lf)
        p.px(lx + 2, ly + 1, FLAME[6], Lf)
        p.px(lx + 1, ly + 2, FLAME[5], Lf)
        glow(p, lx + 2.5, ly + 2.5, 16, 15, FLAME[3], (0.05, 0.1, 0.18), L=Lf)
        lamp(p, lx + 2.5, ly + 2.5, 26, phase, {(lx + i, ly - 1 + j) for j in range(7) for i in range(5)})
        glimmer(p, lx + 2, g, phase)
    # the water curling white at her forefoot, the sea's near edge before her keel, and her wake
    for yy in range(ws + 1, g + 2):
        for xx in range(xb - 12, x1 + 1):
            if p.get(xx, yy, near) is None:
                p.px(xx, yy, Wt[3 if yy == ws + 1 else 2 if yy == ws + 2 else 1], near)
    for (dx, dy) in ((-1, 0), (-2, 0), (-3, 0), (-4, 1), (-5, 1), (0, 1), (-2, -1), (-3, -1), (-6, 2), (-7, 2),
                     (-8, 2)):
        p.px(xb + dx, ws + dy, foam, near)
    for i, (dx, dy) in enumerate(((-4, -4), (-6, -3), (-7, -5), (-3, -6), (-9, -2))):
        p.px(xb + dx, ws + dy, foam if i % 2 else C["white"], p.twinkle(i) if motion else near)
    for xx in range(xb + 4, x1):
        if (xx * 7 + phase) % 9 < 3:
            p.px(xx, ws + 1 + (xx // 6) % 2, foam, near)
    return (min(xb - 13, hx + round(DRAGON_BOX[0] * f)), x1 + 1)


# The small ship's head, 7 by 7, facing right: carved oak, a bronze eye (e), jaws open on a red tongue (r).
STEM_SMALL = [".kkk...", "kOOOkk.", "kOokeOk", "kOooook", "kOktkk.", "kOk.rr.", "kOk...."]


def ship_small(p: Pix, x0, g, night, room=30, phase=0, rowing=False, length=24):
    """The longship for a phone's header, of the hero's own make, `length` + 6 wide from x0, built to the
    `room` of rows free of words above the water at row g: a tarred hull under an oak gunwale, the stern
    scrolled and the stem rising to a small carved head, painted shields along her side and the oars out,
    and with 26 rows or more her striped sail full on its yard, with fewer furled on it, under 16 her mast
    down, and under 12 nothing. `rowing`, she has her mast stowed whatever the room and a lantern on her
    stem, cold by day and burning by night with its light on the water. Returns the span of the rule she
    covers."""
    if room < 12:
        return None
    L = "base"
    W, T = wood(night), TAR
    k = -1 if night else 0
    ws = g - 2
    hx, n = x0 + 2, length
    gys, kys = [], []
    for i in range(n):
        s = abs(2 * i / (n - 1) - 1)
        gys.append(ws - 3 - round(3 * s ** 2.4))
        kys.append(ws + 1 - round(2 * s ** 1.6))
    lap, face = (T[5], T[2]) if not night else (T[6], T[3])
    _region(p, L, face, hx, gys, [ky + 1 for ky in kys])
    for i, (gy, ky) in enumerate(zip(gys, kys)):
        p.px(hx + i, gy, OAK[5 + k], L)
        if gy + 3 < ky:
            p.px(hx + i, gy + 3, lap, L)
        p.px(hx + i, ky, T[0], L)
    pal = _carved(night)
    for (dx, dy, c) in ((0, -1, W[0]), (1, -1, W[6]), (0, -2, W[0]), (1, -2, W[6]), (0, -3, W[0]), (1, -3, W[6]),
                        (1, -4, W[0]), (2, -4, W[6]), (3, -4, W[0]), (3, -3, W[6]), (2, -3, W[0])):
        p.px(hx + dx - 1, gys[0] + dy, c, L)
    stem = 4 if room >= 16 else 2
    bx = hx + n - 1
    for j in range(stem):
        for dx, c in ((-1, W[0]), (0, W[6]), (1, W[0])):
            p.px(bx + dx + j // 3, gys[-1] - 1 - j, c, L)
    p.sprite(bx - 1 + (stem - 1) // 3, gys[-1] - stem - len(STEM_SMALL) + 1, STEM_SMALL, pal, 1, L)
    mx = hx + n // 2 - 1
    deck = gys[n // 2]
    if rowing:
        p.hline(hx + 4, hx + n - 4, deck - 1, ROPE[4 + k], L)
        for xx in range(hx + 6, hx + n - 6):
            p.px(xx, deck - 2, (RED if (xx - hx) // 2 % 2 else CREAM)[4 + k], L)
    elif room >= 16:
        furled = room < 26
        sail_h = 0 if furled else min(13, room - 13)
        mast_h = sail_h + 4 if not furled else max(6, min(9, room - 9))
        yard = deck - mast_h
        p.vline(mx, yard - 1, deck + 1, ROPE[4 + k], L)
        p.px(mx, yard - 2, BRONZE[5], L)
        sx0, sw = mx - 7, 15
        if not furled:
            _sail(p, sx0, yard, sw, sail_h, night, L, uid="sls")
        else:
            for xx in range(sx0, sx0 + sw):
                p.px(xx, yard + 1, (RED if (xx - sx0) // 2 % 2 == 0 else CREAM)[3 + k], L)
        p.hline(sx0 - 1, sx0 + sw + 1, yard, ROPE[4 + k], L)
        _line(p, mx, yard - 1, hx + 1, gys[0] - 3, ROPE[2 + k], L)
        _line(p, mx, yard - 1, bx, gys[-1] - stem, ROPE[2 + k], L)
    if room >= 14 or rowing:
        for i, cx in enumerate(range(hx + 4, hx + n - 3, 3)):
            shield(p, cx, gys[cx - hx] + 2, (i + phase) % 3, 1.8, night, L)
    for px_ in range(hx + 6, hx + n - 3, 5):
        _line(p, px_, gys[px_ - hx] + 3, px_ - 3, ws, OAK[4 + k], L)
    Wt = water(night)
    foam = Wt[6] if not night else Wt[5]
    for xx in range(x0, bx + 2):
        p.px(xx, ws + 1, Wt[3], L)
    for (dx, dy) in ((1, 0), (2, 0), (3, 1), (0, 1)):
        p.px(bx + dx, ws + dy, foam, L)
    if rowing:
        # a lantern on the stem, cold by day and burning by night, its light on the water under it
        lx, ly = bx + 2, gys[-1] - 2
        for (dx, dy, c) in ((0, -1, IRON[3 + k]), (-1, 0, IRON[2 + k]), (1, 0, IRON[2 + k]), (-1, 1, IRON[2 + k]),
                            (1, 1, IRON[2 + k])):
            p.px(lx + dx, ly + dy, c, L)
        p.px(lx, ly, FLAME[6] if night else OCHRE[2], L)
        p.px(lx, ly + 1, FLAME[4] if night else OCHRE[1], L)
        if night:
            Lf = p.flicker(phase)
            glow(p, lx + 0.5, ly + 0.5, 6, 5, FLAME[3], (0.1, 0.2), L=Lf)
            for (dx, dy) in ((0, 0), (1, 1), (0, 2)):
                p.apx(lx + dx, ws + dy, FLAME[5], 0.6, Lf)
    return (x0 - 1, bx + 5)


# A steersman at the tiller, 6 by 9, facing the bow: helm (h, H lit), face (f), beard (b), a cloak (c) and
# the tiller in his hands (t).
STEERSMAN = [".HHh..", ".hhhh.", ".fbf..", ".bbb..", "cccc..", "ccccc.", "cccctt", ".cc...", ".cc..."]


def steersman(p: Pix, x, base, night, L="base"):
    """The steersman standing at the stern, his feet on the row above `base`, his face on the hand's lightest
    skin."""
    k = -1 if night else 0
    pal = {"H": IRON[6 + k], "h": IRON[4 + k], "f": SKINS[0][3 + k], "b": RAMP["blond"][3 + k],
           "c": RAMP["blue"][3 + k], "t": ROPE[3 + k]}
    p.sprite(x, base - len(STEERSMAN), STEERSMAN, pal, 1, L)


# --------------------------------------------------------------------------- the shore
# The longhouse's gable beast at the left end of its roof, 7 by 9: the bargeboards crossed over the roof's end,
# the outer one carved into a beast's head looking out, a bronze eye (e); mirrored at the right end.
GABLE = [
    ".kkk...",
    "kOOOk.k",
    "keOkkOk",
    ".kkOOk.",
    "..kOk..",
    ".kOkOk.",
    ".kk.kOk",
    "......k",
]
# The smoke from the roof's hole, three frames of four puffs rising and drifting off to the right, round and round
# in SMOKE_LOOP seconds: one of the scene's idles.
SMOKE_LOOP = 4.8
SMOKE = (((0, -3), (1, -7), (3, -11), (5, -15)), ((0, -5), (2, -9), (4, -13), (6, -17)),
         ((1, -4), (2, -8), (4, -12), (7, -16)))


def longhouse(p: Pix, x, base, night, phase=0, small=False, motion=True, ceiling=0, L="base"):
    """The longhouse on the shore, its footing on the row above `base`, 32 wide from x (22 if `small`): walls
    of upright oak staves between dark corner posts on a stone footing, a door with a lit lintel and a small
    window, under a turf roof that swells to its ridge like an upturned hull, its eaves in shadow; crossed
    bargeboards at each end of the roof carved into beasts looking out, and smoke curling from the hole in
    the roof, rising in a moving header. By night the window is lit, a steady warm light with a brighter heart
    that flickers, and a little of it falls on the wall round it. No puff of smoke rises above row `ceiling`.
    Returns the row of the ridge's top."""
    T, W, Rk = RAMP["turf"], wood(night), RAMP["rock"]
    k = -1 if night else 0
    w = 22 if small else 32
    wall = 5 if small else 7
    eave = base - 2 - wall
    uid = "lh" + ("s" if small else "")
    p.defs.append(f'<pattern id="{uid}w" x="{x}" width="4" height="1" patternUnits="userSpaceOnUse">'
                  f'<path stroke="{W[4]}" d="M0 .5h1"/><path stroke="{W[3]}" d="M1 .5h2"/>'
                  f'<path stroke="{W[0]}" d="M3 .5h1"/></pattern>')
    _region(p, L, f"url(#{uid}w)", x, [eave + 1] * w, [eave + 1 + wall] * w)
    p.hline(x, x + w, eave + 1, W[1], L)
    p.vline(x, eave + 1, base - 1, W[1], L)
    p.vline(x + w - 1, eave + 1, base - 1, W[1], L)
    for xx in range(x, x + w):
        p.px(xx, base - 1, Rk[2 + k] if (xx - x) % 3 else Rk[3 + k], L)
    door = x + (5 if small else 7)
    for yy in range(base - 1 - (4 if small else 5), base - 1):
        for xx in (door, door + 1, door + 2):
            p.px(xx, yy, W[0] if xx != door + 1 or yy < base - 3 else W[1], L)
    p.hline(door - 1, door + 4, base - 2 - (4 if small else 5), W[5], L)
    wx = x + (14 if small else 20)
    wy = eave + 3
    for (dx, dy) in ((0, 0), (1, 0), (0, 1), (1, 1)):
        p.px(wx + dx, wy + dy, FLAME[3] if night else W[0], L)
    # the turf roof, swelling to its ridge, with tufts along its crest and its eaves in shadow
    tops = []
    for i in range(-2, w + 2):
        s = abs(2 * (i + 2) / (w + 3) - 1)
        tops.append(eave - (3 if small else 5) - round((2 if small else 3) * (1 - s ** 2)))
    p.defs.append(f'<pattern id="{uid}t" width="7" height="3" patternUnits="userSpaceOnUse">'
                  f'<path stroke="{T[3 + k]}" d="M0 .5h7M0 1.5h2m2 0h3M0 2.5h5"/>'
                  f'<path stroke="{T[2 + k]}" d="M2 1.5h2M5 2.5h2"/></pattern>')
    _region(p, L, f"url(#{uid}t)", x - 2, tops, [eave + 1] * len(tops))
    for j, xx in enumerate(range(x - 2, x + w + 2)):
        p.px(xx, tops[j], T[5 + k], L)
        p.px(xx, tops[j] + 1, T[4 + k], L)
        p.px(xx, eave, T[1 + k], L)
        if (xx * 5) % 7 == 1:
            p.px(xx, tops[j] - 1, T[6 + k], L)
    hole = x + w * 3 // 5
    p.px(hole, tops[hole - x + 2], T[0], L)
    p.px(hole + 1, tops[hole - x + 2], T[0], L)
    # the gable beasts
    pal = _carved(night)
    p.sprite(x - 4, tops[0] - 5, GABLE, pal, 1, L)
    p.sprite(x + w - 3, tops[-1] - 5, GABLE, pal, 1, L, flip=True)
    # the smoke from the hole
    smoke = (CREAM[6], Rk[6]) if not night else (Rk[4], Rk[3])
    frames = SMOKE if motion else SMOKE[:1]
    for f, puffs in enumerate(frames):
        Ls = p.seq(f"smoke{f}", f / len(frames), (f + 1) / len(frames), SMOKE_LOOP, keep=f == 0, z=0.5) \
            if len(frames) > 1 else L
        for j, (dx, dy) in enumerate(puffs[:3 if small or p.lite else 4]):
            sx, sy = hole + dx, tops[hole - x + 2] + dy
            if sy < ceiling:
                break
            r = 0.9 + 0.55 * j
            fade = "" if j < 2 else ":0.8" if j == 2 else ":0.6"
            for ey in range(-2, 3):
                for ex in range(-3, 4):
                    if (ex / r) ** 2 + (ey / (r * 0.8)) ** 2 <= 1:
                        p.px(sx + ex, sy + ey, (smoke[0] if ey < 0 or (ex < 0 and ey == 0) else smoke[1]) + fade, Ls)
    if night:
        Lf = p.flicker(phase)
        p.px(wx, wy, FLAME[5], Lf)
        p.px(wx + 1, wy + 1, FLAME[4], Lf)
        glow(p, wx + 1, wy + 1, 5, 4, FLAME[3], (0.08, 0.16), L=p.flicker(phase, back=True))
    return min(tops)


def strand(p: Pix, x0, x1, g, h, night, seed=5, rock_from=None, L="base"):
    """The shore rising from the water at row g - 2 to `h` above it between x0 and x1: sand along the water,
    turf over it, and stones where the ground is rocky (from `rock_from` on). The ground's top is level, so
    a house can stand on it."""
    S, T, Rk = RAMP["sand"], RAMP["turf"], RAMP["rock"]
    rnd = random.Random(seed)
    k = -1 if night else 0
    top = g - 2 - h
    for x in range(x0, x1):
        slope = max(0, round((x0 + 7 - x) * 0.8))
        for y in range(top + slope, g - 1):
            depth = y - top
            if depth == 0:
                c = T[4 + k] if (x % 3) else T[3 + k]
            elif depth == 1:
                c = T[2 + k]
            elif y >= g - 4:
                c = S[4 + k] if y == g - 4 else S[3 + k]
            else:
                c = S[2 + k] if (x * 5 + y * 3) % 17 else S[1 + k]
                if rock_from is not None and x >= rock_from and (x * 7 + y * 11) % 5 == 0:
                    c = Rk[3 + k]
            p.px(x, y, c, L)
    for i in range(3 + (x1 - x0) // 12):
        x = rnd.randrange(x0 + 2, x1 - 2)
        if i % 2 and p.lite:
            continue
        p.px(x, g - 3, Rk[4 + k])
        p.px(x + 1, g - 3, Rk[2 + k])


BRAZIER = [
    ".ccccccc.",
    "iIcCccCIi",
    ".iiiiiii.",
    "..iiiii..",
    "...iii...",
    "..i.i.i..",
    ".i..i..i.",
    ".i..i..i.",
    "i...i...i",
]
# The shore's brazier, 13 by 12: a heap of coals in a wide iron bowl, its rim lit, on a stem and three legs.
BRAZIER_BIG = [
    "...cccCccc...",
    ".ccCcccccCcc.",
    "IIIIIIIIIIIIi",
    ".iIiiiiiiiii.",
    "..iiiiiiiii..",
    "...iiiiiii...",
    ".....iii.....",
    "....i.i.i....",
    "...i..i..i...",
    "..i...i...i..",
    ".i....i....i.",
    "i.....i.....i",
]


def lamp(p: Pix, cx, cy, r, phase, own=()):
    """Register a flame at (cx, cy): once everything is drawn, `firelight` lays its warm light on the planks,
    the shore and the house within `r` of it, flickering with the flame. `own` are the lamp's own pixels."""
    p.lamps.append((cx, cy, r, phase, set(own)))


def firelight(p: Pix):
    """The finishing pass by night: each fire's light on what stands near it, strongest nearest the flame.
    The sky, the words and the water take none (the water takes its own shiver, see `glimmer`). A drawing made
    lighter keeps the pool's inner ring and lets its faint outer one go."""
    base = p.layers["base"]
    col = FLAME[3]
    alphas = (0.1, 0.22)
    n = len(alphas)
    for (cx, cy, r, phase, own) in p.lamps:
        L = p.flicker(phase)
        for y in range(math.floor(cy - r), math.ceil(cy + r) + 1):
            for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
                c = base.get((x, y))
                if c is None or (x, y) in own or c not in LIT:
                    continue
                d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.15) / r
                ring = min(n - 1, int((1 - d) * n))
                if d < 1 and (ring == n - 1 or not p.lite):
                    p.apx(x, y, col, alphas[ring], L)


def glimmer(p: Pix, x, g, phase=0):
    """A fire's light on the water near it: a warm pool on the surface and the streak of its reflection,
    shivering with the flame."""
    Lf = p.flicker(phase)
    glow(p, x + 0.5, g - 0.5, 8, 2.6, FLAME[3], (0.1, 0.2, 0.32), L=Lf, keep=2, only=WATER)
    for yy in range(g - 2, g + 1):
        for dx in (-1, 0, 1):
            if (yy + dx) % 2 == 0:
                p.apx(x + dx, yy, FLAME[4], 0.3, Lf)


def northlight(p: Pix):
    """The finishing pass by night: the aurora's green lying on the water's surface, here and there. A drawing
    made lighter keeps the brighter flecks on the surface itself."""
    base = p.layers["base"]
    for (x, y), c in list(base.items()):
        if c == DEEP[4] and (x * 7 + y) % (6 if p.lite else 3) == 0:
            p.apx(x, y, RAMP["aurora"][4], 0.24, "pool")
        elif c == DEEP[3] and (x * 5 + y) % 7 == 0 and not p.lite:
            p.apx(x, y, RAMP["aurora"][3], 0.16, "pool")


def brazier(p: Pix, x, base, night, phase=0, reach=11, big=False, L="base"):
    """An iron brazier, 9 by 9 (13 by 12 when `big`) with its feet on the row above `base`: a bowl of coals,
    grey and cold by day and by night burning, with flames that leap and flicker, embers in the coals, sparks
    over it, its glow in the air round it and its light on what stands near (see `firelight`)."""
    k = -1 if night else 0
    art = BRAZIER_BIG if big else BRAZIER
    pal = {"i": IRON[3 + k], "I": IRON[5 + k], "c": TAR[2] if night else RAMP["rock"][3],
           "C": FLAME[2] if night else RAMP["rock"][5]}
    y = base - len(art)
    p.sprite(x, y, art, pal, 1, L)
    if not night:
        return
    Lf = p.flicker(phase)
    fx, fy = x + len(art[0]) // 2, y - 1
    cells = [(0, 0, FLAME[6]), (-1, 0, FLAME[5]), (1, 0, FLAME[5]), (-2, 0, FLAME[3]), (2, 0, FLAME[3]),
             (0, -1, FLAME[5]), (-1, -1, FLAME[4]), (1, -1, FLAME[4]), (0, -2, FLAME[4]), (-1, -2, FLAME[3]),
             (1, -3, FLAME[3]), (0, -3, FLAME[3]), (0, -4, FLAME[2])]
    if big:
        cells += [(-3, 0, FLAME[3]), (3, 0, FLAME[3]), (-2, -1, FLAME[3]), (2, -1, FLAME[4]), (1, -2, FLAME[5]),
                  (-1, -3, FLAME[3]), (2, -2, FLAME[3]), (0, -5, FLAME[3]), (1, -5, FLAME[2]), (-1, -6, FLAME[2]),
                  (0, -1, FLAME[6]), (0, -2, FLAME[5]), (1, -4, FLAME[3]), (-2, -3, FLAME[2])]
    for (dx, dy, c) in cells:
        p.px(fx + dx, fy + dy, c, Lf)
    for dx in ((-4, -1, 2, 4) if big else (-2, 0, 2)):
        p.px(fx + dx, y, FLAME[3], p.flicker(phase + 1))
    if big:
        for i, (dx, dy) in enumerate(((-2, -8), (2, -9), (0, -11), (3, -7))):
            p.px(fx + dx, fy + dy, FLAME[5], p.twinkle(i + phase))
    r = 14 if big else 11
    glow(p, fx + 0.5, fy - 1, r, r * 0.8, FLAME[3], (0.07, 0.14, 0.24), L=p.flicker(phase, back=True))
    own = {(fx + dx, fy + dy) for dx, dy, _ in cells} | {(x + i, y + j) for j, row in enumerate(art)
                                                          for i, ch in enumerate(row) if ch != "."}
    lamp(p, fx + 0.5, fy, reach, phase, own)


# --------------------------------------------------------------------------- the footers
# The marks a footer stands on its water, the larger first where it finds room, as (width, the rows it rises over
# the water's surface): the longship under her striped sail, and the raven on its mooring post.
MARKS = {"ship": (36, 21), "raven": (11, 18)}
SWELL = 3       # the most rows a footer's waves rise over its water where the words leave them room


# The stern post of the footer's longship rolling into its scroll, 5 by 6.
FOOT_STERN = [".kkk.", "kOOOk", "kOkOk", "kOkk.", "kOk..", "kOk.."]


def footer_ship(p: Pix, x0, ws, night, sail=True, phase=0, L="base"):
    """The longship that is the design's mark on a footer, 33 wide from x0 with her waterline at row ws, sailing
    to the right: a tarred hull of two strakes under an oak gunwale, sweeping up to her ends; a row of painted
    round shields hung along the gunwale, red, cream, ochre and black by turns, each with its iron boss; the stern
    post rolled into its scroll and the stem rising to its carved dragon's head; the stays from her masthead to
    her ends; and with `sail` her great sail of red and cream stripes bellied on its yard, lit down its weather
    edge and shaded down its lee and along its foot, else the yard lowered on the mast with the sail furled on
    it. Returns the columns her hull spans, which the water before her keel covers (see `footing`)."""
    T, W = TAR, wood(night)
    k = -1 if night else 0
    lap, face = (T[5], T[2]) if not night else (T[6], T[3])
    n, hx = 26, x0 + 3
    ends = (4, 3, 2, 1)
    gys = [ws - 4 - (ends[min(i, n - 1 - i)] if min(i, n - 1 - i) < 4 else 0) for i in range(n)]
    kys = [ws + 1 - ((5, 3, 2, 1)[min(i, n - 1 - i)] if min(i, n - 1 - i) < 4 else 0) for i in range(n)]
    bx, mx = hx + n - 1, hx + n // 2 - 1
    pal = _carved(night)
    if sail:
        yard, sx0, sw = ws - 18, mx - 7, 15
    else:
        yard, sx0, sw = ws - 11, mx - 6, 13
    # the stays from the masthead to her ends, under the sail
    _line(p, mx - 1, yard - 1, hx - 1, gys[0] - 5, ROPE[2 + k], L)
    _line(p, mx + 1, yard - 1, bx + 1, gys[-1] - 5, ROPE[2 + k], L)
    p.vline(mx, yard - 1, ws - 4, ROPE[4 + k], L)
    p.px(mx, yard - 2, BRONZE[5], L)
    if sail:
        for i in range(sw):
            x = sx0 + i
            foot = yard + 11 - round(2 * abs(2 * i / (sw - 1) - 1) ** 3)
            red = (i // 3) % 2 == 0
            ramp, mid = (RED, 3) if red else (CREAM, 5)
            for y in range(yard + 1, foot + 1):
                t = mid
                if i == 0 or (y - yard < 5 and i < 4):
                    t = mid + 1
                if i >= sw - 2 or y == foot or y == yard + 1:
                    t = mid - 1 - (1 if (y == foot and i >= sw - 2) else 0)
                p.px(x, y, ramp[max(0, min(6, t + k))], L)
    else:
        for i in range(sw):
            p.px(sx0 + i, yard + 1, (RED if (i // 3) % 2 == 0 else CREAM)[(3 if (i // 3) % 2 == 0 else 5) + k], L)
            p.px(sx0 + i, yard + 2, (RED if (i // 3) % 2 == 0 else CREAM)[(2 if (i // 3) % 2 == 0 else 3) + k], L)
    p.hline(sx0 - 1, sx0 + sw + 1, yard, ROPE[4 + k], L)
    p.px(sx0 - 1, yard, ROPE[2 + k], L)
    p.px(sx0 + sw, yard, ROPE[2 + k], L)
    # the hull: an oak gunwale over two tarred strakes, each lapped over the next with its lap lit
    for i, (gy, ky) in enumerate(zip(gys, kys)):
        x = hx + i
        p.px(x, gy, OAK[5 + k], L)
        p.px(x, gy + 1, OAK[2 + k], L)
        for y in range(gy + 2, ky):
            p.px(x, y, lap if (y - gy) in (3, 5) else face, L)
        p.px(x, ky, T[0], L)
    for y in range(gys[0], kys[0] + 1):
        p.px(hx - 1, y, T[0], L)
    for y in range(gys[-1], kys[-1] + 1):
        p.px(bx + 1, y, T[0], L)
    # the stern post rolled into its scroll, and the stem rising to the dragon's head
    for j in range(3):
        for dx, c in ((-1, W[0]), (0, W[6]), (1, W[0])):
            p.px(hx + dx, gys[0] - 1 - j, c, L)
    p.sprite(hx - 1, gys[0] - 3 - len(FOOT_STERN), FOOT_STERN, pal, 1, L)
    for j in range(4):
        for dx, c in ((-1, W[0]), (0, W[6]), (1, W[0])):
            p.px(bx + dx + j // 3, gys[-1] - 1 - j, c, L)
    p.sprite(bx, gys[-1] - 4 - len(STEM_SMALL) + 1, STEM_SMALL, pal, 1, L)
    # the shields along the gunwale, each hung from it with its boss
    paints = (RED, CREAM, OCHRE, TAR)
    for j, cx in enumerate(range(hx + 3, hx + n - 3, 3)):
        R = paints[(j + phase) % 4]
        b = 3 if R is not CREAM else 5
        cy = gys[cx - hx] + 2
        for (dx, dy), t in (((0, -1), b + 1), ((-1, 0), b + 1), ((1, 0), b), ((0, 1), b - 1), ((-1, -1), b - 2),
                            ((1, -1), b - 2), ((-1, 1), b - 2), ((1, 1), b - 2)):
            p.px(cx + dx, cy + dy, R[max(0, min(6, t + k))] if R is not TAR else T[max(1, t - 1)], L)
        p.px(cx, cy, IRON[5 + k], L)
    return hx - 1, bx + 1


def _mark_spot(p: Pix, top: int, width: int, rise: int):
    """The first column of a footer's mark `width` wide rising `rise` rows over its water at row `top`: as far
    right as it stands two units clear of every word and a unit clear of everything drawn (the lines ruled
    between the cells, the scale, the arrow, the heart, the brazier) inside the frame; None where it finds no
    room."""
    base = p.layers["base"]
    y0 = top - rise
    if y0 < BAND + 2:
        return None
    for x0 in range(p.w - BAND - 2 - width, BAND + 1, -1):
        if not p.clear_of_words(x0 - 3, y0 - 3, x0 + width + 3, top):
            continue
        if any((x, y) in base for y in range(y0 - 1, top) for x in range(x0 - 1, x0 + width + 1)):
            continue
        return x0
    return None


def _room_over(p: Pix, x, top) -> int:
    """The rows over row `top` at column x clear of every word by two units and of everything drawn, up to
    SWELL."""
    base = p.layers["base"]
    n = 0
    while n < SWELL and p.clear_of_words(x - 1, top - n - 3, x + 2, top) and (x, top - 1 - n) not in base:
        n += 1
    return n


def footing(p: Pix, night: bool):
    """A footer once its words are set: the fjord's water along its foot, two to four rows deep under the lowest
    word by two units, its swell rising in waves a row or three over it wherever the words leave them room, each
    wave lit along its crest and breaking white at its peak; and the design's mark on it at the right end where
    the words leave it room, else the first place from the right where they do: the longship sailing on under
    her striped sail (see `footer_ship`), or where the words leave only a narrow corner, the raven on its mooring
    post. The water lies calm round the mark and covers her keel and the post's foot, and curls white at her
    stem. By night a fire's light shivers on the water under it (see `glimmer`)."""
    w, h = p.w, p.h
    low = max((b[3] for b in p.words), default=0)
    top = min(h - 2, max(h - 4, low + 2))
    kind, x0 = next(((k, x) for k in MARKS for x in [_mark_spot(p, top, *MARKS[k])] if x is not None),
                    (None, None))
    calm = range(x0 - 4, x0 + MARKS[kind][0] + 4) if kind else range(0)
    rnd = random.Random(w * 7 + h)
    ph = rnd.uniform(0, 6.3)
    room = [_room_over(p, x, top) if BAND <= x < w - BAND and x not in calm else 0 for x in range(w)]
    surf = []
    for x in range(w):
        u = (0.5 + 0.5 * math.sin(2 * math.pi * x / 29 + ph)) * 0.7 + (0.5 + 0.5 * math.sin(2 * math.pi * x / 9)) * 0.3
        surf.append(top - round(min(room[max(0, x - 2):x + 3] or [0]) * u ** 1.6))
    Wt = water(night)
    rows = (4, 4, 3, 2, 1)
    for x in range(w):
        for y in range(surf[x], h):
            p.px(x, y, Wt[rows[min(4, max(0, y - top + 1))]])
        if surf[x] < top:
            peak = 0 < x < w - 1 and surf[x] < surf[x - 1] and surf[x] <= surf[x + 1]
            p.px(x, surf[x], Wt[6 if peak and not night else 5])
    for _ in range(w // 10):
        x = rnd.randrange(BAND, w - BAND - 3)
        if x not in calm:
            p.hline(x, x + rnd.choice((2, 3)), top + 1, Wt[4 if not night else 3])
    if kind == "ship":
        a, b = footer_ship(p, x0 + 1, top, night, phase=1)
        for x in range(a, b + 1):
            for y in range(top + 1, h):
                p.px(x, y, Wt[rows[min(4, y - top + 1)]])
        foam = Wt[6] if not night else Wt[5]
        for (dx, dy) in ((1, 0), (2, 0), (3, 1), (0, 1), (4, 1), (2, -1)):
            p.px(b + dx, top + dy, foam)
        for dx in range(2, 12, 3):
            p.px(a - dx, top + 1, foam)
    elif kind == "raven":
        bollard(p, x0 + 6, top, night)
        raven(p, x0, top - 17, night, flip=False, moonlit=True)
        for x in range(x0 + 4, x0 + 9):
            for y in range(top + 1, h):
                p.px(x, y, Wt[rows[min(4, y - top + 1)]])
    if night:
        for (cx, cy, _, phase, _) in list(p.lamps):
            if cy < top:
                glimmer(p, round(cx), top + 2, phase)
    p.marked_at = (kind, x0)


# --------------------------------------------------------------------------- birds
# A gull in flight seen from below, 7 wide, wings raised and then level; a raven the same, 9 wide and black.
GULL = [["#.....#", ".##.##.", "...#..."], ["..#.#..", ".##.##.", "#.....#"]]
RAVEN_FLY = [["#.......#", "##.....##", ".###.###.", "...###...", "....#...."],
             ["....#....", "...###...", ".###.###.", "##.....##", "#.......#"]]


def _bird_symbol(p: Pix, kind: str, frame: int):
    key = ("bird", kind, frame)
    if key not in p.syms:
        art = (GULL if kind == "gull" else RAVEN_FLY)[frame]
        ink = {(i, j) for j, r in enumerate(art) for i, ch in enumerate(r) if ch == "#"}
        if kind == "gull":
            cells = {(i, j): X["gull"] if (i, j - 1) not in ink else X["gull_shade"] for (i, j) in ink}
        else:
            Rv = RAMP["raven"]
            cells = {(i, j): Rv[4] if (i, j - 1) not in ink else Rv[1] for (i, j) in ink}
        p.symbol(key, cells)
    return key


def birds(p: Pix, cx, cy, rx, ry, kind="gull", motion=True, seed=0, steps=40, dur=8.0, L="base"):
    """A bird wheeling in a slow circle over (cx, cy), beating its wings now and then; the still file
    leaves it where its circle begins."""
    rnd = random.Random(seed)
    frames = [_bird_symbol(p, kind, 0), _bird_symbol(p, kind, 1)]
    a0 = rnd.uniform(0, 2 * math.pi)
    w = 7 if kind == "gull" else 9
    path = [(round(cx + rx * math.cos(a0 + 2 * math.pi * s / steps) - w // 2),
             round(cy + ry * math.sin(a0 + 2 * math.pi * s / steps) - 2)) for s in range(steps)]
    if motion:
        p.fly(frames, path, dur, 16, flap=0.55 if kind == "gull" else 0.7)
    else:
        p.use(frames[0], path[0][0], path[0][1], L)


# A raven perched, 11 by 8, facing left: its beak (b), a bronze eye (e), its body black with a blue sheen
# along its back (s), legs (l) and a tail.
RAVEN = [
    "....skk....",
    "...skkkk...",
    "bbbkekkkks.",
    "...kkkkkkss",
    "....kkkkkkks",
    ".....kkkkkk.",
    "......kk.kkk",
    ".....l.l....",
    "....ll.ll...",
]


def raven(p: Pix, x, y, night, L="base", flip=False, moonlit=False):
    """A raven perched, top-left at (x, y); `flip` turns it to face right. By night its sheen is the aurora's
    green, and `moonlit`, on a sheet with no sky to stand against, its feathers catch the moon."""
    Rv = RAMP["raven"]
    pal = {"k": Rv[1], "s": RAMP["aurora"][3] if night else Rv[3], "b": IRON[3], "e": BRONZE[5], "l": IRON[2]}
    if night and moonlit:
        pal.update(k=Rv[3], s=Rv[5], b=IRON[5], l=IRON[4])
    p.sprite(x, y, RAVEN, pal, 1, L, flip=flip)


# --------------------------------------------------------------------------- the lookout
# A warrior keeping watch, drawn to the hand's canon: 16 by 28 from his spear's point to his boots, standing 24
# units from the crown of his helm, his head about a fifth of that, facing left out to sea and leaning on his spear:
# an iron helm with a bronze band and a nasal (H lit, h, d shade, b band, n nasal), his face on one of the hand's
# skins (f, F shade) with a single dark eye (e), a braided beard (y, Y lit), a cloak (c, C lit) pinned with a bronze
# brooch (o), a round shield slung on his back (s rim, S face, R lit, I boss), his tunic (t, T lit) belted (l, k
# its buckle), his legs bound in wool (w, W lit) and his boots (g); his hand on the spear (a), its shaft of ash (p)
# and its iron point (P, I lit). `figure` draws him round with the darkest tone of each thing he is made of.
WATCHMAN = [
    "...P............",
    "..PIP...........",
    "..PPP...........",
    "...p...HHh......",
    "...p..HHhhhd....",
    "...p..bbbbbbd...",
    "...p..nefffFd...",
    "...p.ffffffF....",
    "...p..fyyyF.....",
    "...p..yYyyyc....",
    "...p.cyYyycCss..",
    "...pcCCyYcccsRSs",
    "..aaCCcoccccsRSs",
    "..aaCcccccccsIRs",
    "...pCcccccccsSSs",
    "...pCttTtttcsSSs",
    "...pCtlklltc.ss.",
    "...p.tTtttt.....",
    "...p.tTtttt.....",
    "...p.tTttttt....",
    "...p..ww.ww.....",
    "...p..wW.wW.....",
    "...p..ww.ww.....",
    "...p..wW.wW.....",
    "...p..ww.ww.....",
    "...p..wW.wW.....",
    "...p.ggg.ggg....",
]


def figure(p: Pix, x, y, art, pal, L="base"):
    """Pixel art with its top-left at (x, y) drawn round with an outline, each pixel of it the darkest tone of the
    ramp of what it borders, so the outline is never black and a figure reads against any ground."""
    cells = {(i, j): pal[ch] for j, row in enumerate(art) for i, ch in enumerate(row) if pal.get(ch)}
    edge = {}
    for (i, j), c in cells.items():
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (i + di, j + dj)
            if q not in cells and q not in edge:
                edge[q] = step(c, -6)
    for (i, j), c in {**edge, **cells}.items():
        p.px(x + i, y + j, c, L)


def lookout(p: Pix, x, base, night, cloak="blue", skin=1, L="base"):
    """The lookout keeping watch, his boots on the row above `base`, 16 wide from x: the warrior of WATCHMAN, his
    cloak in the dyed wool `cloak` and his face on the hand's skin `skin`."""
    k = -1 if night else 0
    Cl, S, B = RAMP[cloak], SKINS[skin], RAMP["blond"]
    pal = {"P": IRON[5 + k], "I": IRON[6], "p": ROPE[3 + k], "H": IRON[6 + k], "h": IRON[4 + k], "d": IRON[2 + k],
           "b": BRONZE[4 + k], "n": IRON[3 + k], "f": S[3 + k], "F": S[2 + k], "e": TAR[0], "y": B[3 + k],
           "Y": B[5 + k], "c": Cl[3 + k], "C": Cl[5 + k], "o": BRONZE[5 + k], "t": ROPE[2 + k], "T": ROPE[4 + k],
           "l": TAR[1], "k": BRONZE[5], "w": CREAM[3 + k], "W": CREAM[5 + k], "g": TAR[1], "s": RED[1],
           "S": RED[3 + k], "R": RED[5 + k], "a": S[3 + k]}
    figure(p, x, base - len(WATCHMAN), WATCHMAN, pal, L)


# The beacon's fire basket, 9 by 6, on the top of its pole: iron bands round a heap of logs (o lit, O), its rim lit.
BASKET = [
    "ilOoOolOi",
    "IiiiIiiiI",
    ".i.iIi.i.",
    "..iiIii..",
    "...iIi...",
    "....I....",
]


def beacon(p: Pix, x, base, top, night, phase=0, motion=True, L="base"):
    """The beacon on its pole, 9 wide from x, the pole's foot on the row above `base` and the basket's rim at row
    `top`: a tall pole of ash, stayed with a rope, and on top an iron basket heaped with logs, cold by day and by
    night burning: its flames leaping and flickering, sparks rising over it, its glow in the air round it and its
    light on what stands near (see `firelight`)."""
    k = -1 if night else 0
    cx = x + 4
    for yy in range(top + len(BASKET) - 1, base):
        p.px(cx, yy, ROPE[4 + k], L)
        p.px(cx + 1, yy, ROPE[2 + k], L)
    for yy in range(top + len(BASKET) + 3, base, 9):
        p.hline(cx - 1, cx + 3, yy, IRON[4 + k], L)
    logs = (TAR[3], TAR[1]) if night else (RAMP["rock"][5], OAK[2])
    pal = {"i": IRON[3 + k], "I": IRON[5 + k], "o": logs[0], "O": logs[1], "l": FLAME[2] if night else OAK[3]}
    p.sprite(x, top, BASKET, pal, 1, L)
    if not night:
        return
    Lf = p.flicker(phase)
    fx, fy = cx, top - 1
    cells = [(0, 0, FLAME[6]), (-1, 0, FLAME[5]), (1, 0, FLAME[5]), (-2, 0, FLAME[4]), (2, 0, FLAME[4]),
             (-3, 0, FLAME[3]), (3, 0, FLAME[3]), (0, -1, FLAME[6]), (-1, -1, FLAME[5]), (1, -1, FLAME[4]),
             (-2, -1, FLAME[3]), (2, -1, FLAME[3]), (0, -2, FLAME[5]), (-1, -2, FLAME[4]), (1, -2, FLAME[3]),
             (0, -3, FLAME[4]), (1, -4, FLAME[3]), (-1, -4, FLAME[3]), (0, -5, FLAME[2]), (1, -6, FLAME[2])]
    for (dx, dy, c) in cells:
        p.px(fx + dx, fy + dy, c, Lf)
    for i, (dx, dy) in enumerate(((-2, -8), (2, -9), (0, -11), (-3, -6))):
        p.px(fx + dx, fy + dy, FLAME[5], p.twinkle(i + phase) if motion else L)
    glow(p, fx + 0.5, fy - 1, 13, 11, FLAME[3], (0.07, 0.14, 0.24), L=p.flicker(phase, back=True))
    own = {(fx + dx, fy + dy) for dx, dy, _ in cells} | {(x + i, top + j) for j, row in enumerate(BASKET)
                                                          for i, ch in enumerate(row) if ch != "."}
    lamp(p, fx + 0.5, fy, 24, phase, own)


def crag(p: Pix, x0, x1, g, top, night, seed=9, L="base"):
    """A headland of rock rising from the water at row g - 2 to its crown at row `top` between x0 and x1: a cliff
    falling steeply to the sea on its left, built of great slabs of rock split along their beds, each lit along its
    upper and left edges where it turns to the light and dark along the joints under and after it, those further
    from the sea in deeper shade; the surf white at its foot, and on its crown a turf level enough for a man to
    stand on."""
    Rk, T = RAMP["rock"], RAMP["turf"]
    k = -1 if night else 0
    rnd = random.Random(seed)
    ws = g - 2
    w = x1 - x0
    cliff = min(10, w // 3)
    tops = {x0 + i: top + (round(((cliff - i) / cliff) ** 1.5 * (ws - top - 2)) if i < cliff else 0)
            for i in range(w)}
    seeds = []
    yy = top + 3
    while yy < ws + 4:
        xx = x0 + rnd.randrange(-4, 6)
        while xx < x1 + 10:
            seeds.append((xx + rnd.uniform(-3, 3), yy + rnd.uniform(-1.5, 1.5)))
            xx += rnd.randrange(12, 22)
        yy += rnd.randrange(6, 9)

    def slab(x, y):
        return min(range(len(seeds)), key=lambda n: (x + 0.5 - seeds[n][0]) ** 2 + (2.4 * (y + 0.5 - seeds[n][1])) ** 2)
    own = {(x, y): slab(x, y) for x in range(x0, x1) for y in range(tops[x], ws)}
    for (x, y), n in own.items():
        depth, level, face = y - tops[x], x - x0 >= cliff - 1, x - x0 < cliff
        if depth == 0 and level:
            c = T[4 + k] if x % 3 else T[5 + k]
        elif depth == 1 and level:
            c = T[2 + k]
        elif depth == 0 or own.get((x, y - 1)) != n:
            c = Rk[6 + k] if face or depth <= 2 else Rk[5 + k]
        elif own.get((x, y + 1), n) != n:
            c = Rk[1 + k]
        elif own.get((x + 1, y), n) != n:
            c = Rk[2 + k]
        elif own.get((x - 1, y)) != n:
            c = Rk[5 + k] if face else Rk[4 + k]
        else:
            c = Rk[(4 if face else 3) + k] if (x * 3 + y * 7 + n) % 17 else Rk[2 + k]
        if x - x0 > w * 0.72 and depth > 1:
            c = step(c, -1)
        p.px(x, y, c, L)
    Wt = water(night)
    foam = Wt[6] if not night else Wt[5]
    for dx in range(-2, cliff + 2):
        if (dx + seed) % 3:
            p.px(x0 + dx, ws - (1 if dx in (0, 2) else 0), foam, L)


# --------------------------------------------------------------------------- marks
def axes(p: Pix, cx, cy, half=5, night=False, L="base"):
    """Two bearded axes crossed behind a shield, centred on (cx, cy), from `half` above the centre to
    `half` below, their hafts of ash and their iron heads hanging inward from the top of each haft, a row
    above it at the most, with a lit edge."""
    k = -1 if night else 0
    for d in (-1, 1):
        for i in range(-half, half + 1):
            p.px(cx - d * i, cy + i, ROPE[3 + k] if i > -half + 2 else IRON[2], L)
        hx, hy = cx + d * half, cy - half
        for (dx, dy, c) in ((0, -1, IRON[6 + k]), (-d, -1, IRON[5 + k]), (-d, 0, IRON[4 + k]), (-2 * d, 0, IRON[4 + k]),
                            (-2 * d, 1, IRON[3 + k]), (-d, 1, IRON[3 + k]), (-3 * d, 1, IRON[2 + k])):
            p.px(hx + dx, hy + dy, c, L)


def section_mark(p: Pix, x, y, night, L="base"):
    """A round shield over crossed axes, 13 by 10 from (x, y - 1), for the mark after SECTION A-A: from a
    row above the words to three under them, so it keeps two rows clear of the title's foot above and of
    the tagline below."""
    axes(p, x + 6, y + 4, 4, night, L)
    shield(p, x + 6, y + 4, 0, 4.2, night, L)
    for (dx, dy) in ((-3, 0), (2, 0), (-1, -3), (0, 2)):
        p.px(x + 6 + dx, y + 4 + dy, OCHRE[4 if night else 5], L)


# A hammer pendant on its cord, 9 by 11: the cord's loop (c), the bronze head (B lit, b) with its chip-carved
# line (d), and the shank.
HAMMER = [
    "....c....",
    "...c.c...",
    "...c.c...",
    "BBBBbBBBB",
    "bBBdddBBb",
    "bbbbbbbbb",
    "...bBb...",
    "...bBb...",
    "...bBb...",
    "...bbb...",
    "....b....",
]


def hammer(p: Pix, x, y, night, L="base"):
    """A hammer pendant in bronze on a cord, top-left at (x, y)."""
    k = -1 if night else 0
    pal = {"c": ROPE[2 + k], "B": BRONZE[5 + k], "b": BRONZE[3 + k], "d": BRONZE[1]}
    p.sprite(x, y, HAMMER, pal, 1, L)


def rivets(p: Pix, x0, x1, y, seed=0, night=False, every=(14, 26), L="base"):
    """Clinker rivets along a rule, the seam of the strake the figures stand on: an iron head every so
    often with its shadow, set only where no word lies within two units."""
    k = -1 if night else 0
    rnd = random.Random(seed * 53 + x0)
    x = x0 + rnd.randint(3, 10)
    while x < x1 - 3:
        if p.clear_of_words(x - 3, y - 4, x + 4, y + 3):
            p.px(x, y - 1, IRON[6 + k], L)
            p.px(x + 1, y - 1, IRON[4 + k], L)
            p.px(x, y, IRON[3 + k], L)
            p.px(x + 1, y, IRON[1], L)
        x += rnd.randint(*every)


def heart(p: Pix, x, y, L="base"):
    """A heart painted red, 7 by 6, lit on its upper-left lobe."""
    art = [".54.43.", "5443321", "4433221", ".33221.", "..221..", "...1..."]
    p.sprite(x, y, art, {str(i): RED[i] for i in range(7)}, 1, L)


def stripes(p: Pix, x0, y0, w, h, period=5, L="base"):
    """A field of sail stripes, red and cream by turns, lit along the top and shaded along the foot."""
    for yy in range(y0, y0 + h):
        f = (yy - y0) / max(1, h - 1)
        band = 0 if f < 0.2 else (1 if f < 0.7 else 2)
        for xx in range(x0, x0 + w):
            red = ((xx - x0) // period) % 2 == 0
            p.px(xx, yy, (RED[4], RED[3], RED[1])[band] if red else (CREAM[6], CREAM[5], CREAM[3])[band], L)


# --------------------------------------------------------------------------- oak, iron and shields for the elements
SHIELD_PAINTS = ("red", "cream", "ochre", "tar")


def shield_stack(p: Pix, x0, y0, w, h, night, base, i=0, bronze=False, L="base"):
    """A week's bar as a stack of round shields laid one on another, seen a little from above, `w` by `h` with
    its top at (x0, y0) on row `base`: the top shield's painted face an ellipse halved in two paints round
    its iron boss (bronze on the busiest week's), and under it the rims of the shields below in their paints
    by turns, each lit along its upper edge over a dark seam, the stack lit down its left and shaded down its
    right like a drum."""
    k = -1 if night else 0
    face = min(5, h)
    a, b = SHIELD_PAINTS[i % 4], SHIELD_PAINTS[(i + 1) % 4]
    for yy in range(y0 + face, base):
        j, r = divmod(base - 1 - yy, 3)
        R = RAMP[SHIELD_PAINTS[(j + i) % 4]]
        for xx in range(x0, x0 + w):
            u = (xx + 0.5 - x0) / w
            t = (4 if u < 0.25 else 3 if u < 0.7 else 2) + (1 if R is TAR else 1 if R is CREAM else 0)
            if r == 2:
                t += 1
            c = TAR[1 + (1 if u < 0.25 else 0)] if r == 0 else R[max(0, min(6, t + k))]
            p.px(xx, yy, c, L)
    # the top shield's face: an ellipse, its two halves painted, its rim dark, its boss lit
    cx, cy = x0 + w / 2, y0 + face / 2
    for yy in range(y0, y0 + face):
        for xx in range(x0, x0 + w):
            dx, dy = (xx + 0.5 - cx) / (w / 2), (yy + 0.5 - cy) / (face / 2)
            d = dx * dx + dy * dy
            if d > 1.15 and yy in (y0, y0 + face - 1):
                continue
            R = RAMP[a if dx < 0 else b]
            t = (5 if R is CREAM else 4 if R is not TAR else 3) + (1 if dy < -0.3 else 0) + k
            c = R[max(0, min(6, t))] if d < 0.62 else IRON[2 + k] if dy > 0 else IRON[4 + k]
            p.px(xx, yy, c, L)
    bx, by = round(cx) - 1, y0 + face // 2 - 1
    M = BRONZE if bronze else IRON
    for (dx, dy, t) in ((0, 0, 5), (1, 0, 4), (2, 0, 3), (0, 1, 4), (1, 1, 3), (2, 1, 2)):
        if face > 3 or dy == 0:
            p.px(bx + dx, by + dy, M[min(6, t + 1 + k)] if bronze else M[t + 1 + k], L)
    p.px(bx, by, C["white"] if not night else M[6], L)
    for yy in range(y0 + 1, base):
        if p.get(x0 - 1, yy, L) is None:
            p.px(x0 - 1, yy, TAR[0], L)
        p.px(x0 + w, yy, TAR[0], L)


def tally(q: Pix, ox, oy, night):
    """A tally plank 11 by 15 a numeral is cut into: a lit top and left edge, a shaded foot and right side, a
    streak of grain, and a nail at its head."""
    W = wood(night)
    k = -1 if night else 0
    face, lit, shade = (3, 4, 1) if night else (4, 5, 2)
    for yy in range(15):
        for xx in range(11):
            c = W[face]
            if yy == 0 or xx == 0:
                c = W[lit]
            elif yy == 14 or xx == 10:
                c = W[shade]
            elif yy in (5, 11) and 2 <= xx <= 8:
                c = W[face - 1] if (xx + yy) % 3 else W[face]
            q.px(ox + xx, oy + yy, c)
    q.px(ox + 5, oy + 1, IRON[6 + k])
    q.px(ox + 5, oy + 2, IRON[3 + k])


def plank_card(p: Pix, x, y, w, h, night, L="base"):
    """A schematic card as a plank panel: a streak of grain along the face, an iron band riveted down the
    edge of its icon's cell, and a nail at each corner."""
    W = wood(night)
    k = -1 if night else 0
    for xx in range(x + 14, x + w - 2):
        if (xx * 7) % 13 != 0:
            p.px(xx, y + h - 4 + ((xx // 9) % 2), W[5] if not night else W[3], L)
    for yy in range(y + 1, y + h - 1):
        p.px(x + 10, yy, IRON[4 + k], L)
        p.px(x + 11, yy, IRON[6 + k] if (yy - y) % 4 == 2 else IRON[3 + k], L)
        p.px(x + 12, yy, IRON[1], L)
    for (nx, ny) in ((x + 1, y + 1), (x + w - 3, y + 1), (x + 1, y + h - 3), (x + w - 3, y + h - 3)):
        p.px(nx, ny, IRON[6 + k], L)
        p.px(nx + 1, ny + 1, IRON[2], L)


def rope_colour(night: bool, seed=0):
    """A colour for each pixel of a rope: the tube's light twisted by a darker strand."""
    k = -1 if night else 0

    def colour(s, o, lam, x, y):
        v = 3 + 2.4 * lam + k
        if int(s * 0.8 + o * 1.4 + seed) % 4 == 0:
            v -= 1.6
        return ROPE[max(0, min(6, round(v)))]
    return colour


def rope_over(p: Pix, cells, night, L="base"):
    """A wire redrawn as a rope along its `cells` (x, y, direction): the twist's light and dark strands by
    turns, and its shadow along the row under a level run and the column right of an upright one."""
    k = -1 if night else 0
    for (x, y, d) in cells:
        twist = ((x + y) // 2) % 2 == 0
        p.px(x, y, ROPE[5 + k] if twist else ROPE[3 + k], L)
        if d == "h":
            p.px(x, y + 1, ROPE[1 + k] if twist else ROPE[2 + k], L)
        else:
            p.px(x + 1, y, ROPE[1 + k] if twist else ROPE[2 + k], L)


def lashing(p: Pix, x, y, d, night, L="base"):
    """A lashing round a rope at (x, y): three turns of a darker cord, across a level rope or an upright one."""
    k = -1 if night else 0
    for i in range(3):
        if d == "h":
            p.px(x + i, y - 1, ROPE[2 + k] if i == 1 else ROPE[1 + k], L)
            p.px(x + i, y, ROPE[2 + k] if i == 1 else ROPE[0], L)
            p.px(x + i, y + 1, ROPE[1 + k] if i == 1 else ROPE[0], L)
        else:
            p.px(x - 1, y + i, ROPE[2 + k] if i == 1 else ROPE[1 + k], L)
            p.px(x, y + i, ROPE[2 + k] if i == 1 else ROPE[0], L)
            p.px(x + 1, y + i, ROPE[1 + k] if i == 1 else ROPE[0], L)


def knot(p: Pix, x, y, night=False, L="base"):
    """A knot in a rope at (x, y): a thicker turn, lit on its upper left."""
    k = -1 if night else 0
    for (dx, dy, t) in ((0, -1, 5), (1, -1, 4), (-1, 0, 4), (0, 0, 4), (1, 0, 3), (2, 0, 3), (0, 1, 3), (1, 1, 2)):
        p.px(x + dx, y + dy, ROPE[max(0, t + k)], L)


def hanging_shield(p: Pix, x, gy, kind, night, size="major", L="base"):
    """A shield hung from the rope at (x, gy) by a short cord for a release: a painted shield, a bigger one
    with a bronze boss for a big release, a small one for a patch, and for a release still to come a bare
    rim with no paint in it."""
    k = -1 if night else 0
    p.px(x, gy + 2, ROPE[2 + k], L)
    p.px(x, gy + 3, ROPE[2 + k], L)
    if size == "next":
        for a in range(0, 360, 20):
            px_, py_ = x + 3.2 * math.cos(math.radians(a)), gy + 7 + 3.2 * math.sin(math.radians(a))
            p.px(math.floor(px_), math.floor(py_), IRON[4 + k] if a % 40 else IRON[2], L)
        p.px(x - 1, gy + 6, IRON[3 + k], L)
        p.px(x, gy + 6, IRON[4 + k], L)
        p.px(x - 1, gy + 7, IRON[2 + k], L)
        p.px(x, gy + 7, IRON[2 + k], L)
        return
    if size == "minor":
        shield(p, x, gy + 6, kind, 2.2, night, L)
        return
    if size == "big":
        shield(p, x, gy + 8, kind, 4.2, night, L)
        for (dx, dy, c) in ((-1, -1, BRONZE[6]), (0, -1, BRONZE[5 + k]), (-1, 0, BRONZE[4 + k]), (0, 0, BRONZE[2])):
            p.px(x + dx, gy + 8 + dy, c, L)
        return
    shield(p, x, gy + 7, kind, 3.3, night, L)


def bollard(p: Pix, x, y, night, L="base"):
    """A mooring post for the repository's founding, 5 wide, standing to the rope at (x, y) with the rope's
    end hitched round it."""
    W = wood(night)
    k = -1 if night else 0
    for yy in range(y - 8, y + 2):
        p.px(x - 1, yy, W[4 + k], L)
        p.px(x, yy, W[3 + k], L)
        p.px(x + 1, yy, W[1], L)
    p.px(x - 1, y - 9, W[5], L)
    p.px(x, y - 9, W[5], L)
    for yy in (y - 5, y - 4):
        p.px(x - 2, yy, ROPE[2 + k], L)
        p.px(x - 1, yy, ROPE[3 + k] if yy == y - 5 else ROPE[1], L)
        p.px(x, yy, ROPE[2 + k] if yy == y - 5 else ROPE[1], L)
        p.px(x + 1, yy, ROPE[1], L)
        p.px(x + 2, yy, ROPE[2 + k], L)


# A warrior seen head and shoulders, 13 by 14: a conical iron helm with a nasal (H lit, h, n), eyes (e) in a
# face (f), a beard (b) with its braids (B), a cloak (c, C lit) pinned with a bronze brooch (o).
WARRIOR = [
    ".....HHh.....",
    "....HhhhhH...",
    "....Hhhhhhh..",
    "...hhhhhhhhh.",
    "...hhhhhhhhh.",
    "...fenfeff...",
    "...ffnffff...",
    "..Bfbbbbbfb..",
    "..Bbbbbbbbb..",
    "..BbbBbbBbB..",
    "..b.bBbbB.b..",
    "CCccccbccccc.",
    "Ccccccocccccc",
    "ccccccccccccc",
]
# The bot: a helm with a spectacle mask over the eyes, a mail aventail below it and no beard.
MASKED = [
    ".....HHh.....",
    "....HhhhhH...",
    "....Hhhhhhh..",
    "...hhhhhhhhh.",
    "...hhhhhhhhh.",
    "...mmmmmmm...",
    "...m.mmm.m...",
    "...mmmmmmm...",
    "...aaaaaaa...",
    "...aaaaaaa...",
    "....aaaaa....",
    "CCccccacccccc",
    "Ccccccocccccc",
    "ccccccccccccc",
]
BEARDS = ("blond", "red", "rope", "tar")
CLOAKS = ("blue", "green", "red", "violet")


def warrior(p: Pix, cx, cy, i, night, bot=False, L="base"):
    """A contributor as a warrior, centred on (cx, cy): the `i`-th beard, cloak and skin of the hand's three by
    turns; a bot wears a masked helm over mail."""
    k = -1 if night else 0
    beard, cloak = RAMP[BEARDS[i % len(BEARDS)]], RAMP[CLOAKS[i % len(CLOAKS)]]
    if bot:
        cloak = RAMP["rock"]
    S = SKINS[i % len(SKINS)]
    pal = {"H": IRON[6 + k], "h": IRON[4 + k], "n": IRON[2], "f": S[3 + k], "e": TAR[1], "b": beard[3 + k],
           "B": beard[5 + k] if beard is not TAR else TAR[4], "c": cloak[3 + k], "C": cloak[5 + k], "o": BRONZE[5],
           "m": IRON[3 + k], "a": IRON[5 + k]}
    art = MASKED if bot else WARRIOR
    p.sprite(cx - 6, cy - 7, art, pal, 1, L)
    for j, row in enumerate(art):
        for ii, ch in enumerate(row):
            if ch == "a" and (ii + j) % 2 == 0:
                p.px(cx - 6 + ii, cy - 7 + j, IRON[3 + k], L)
            elif ch == "h" and ii == row.rindex("h") and j > 1:
                p.px(cx - 6 + ii, cy - 7 + j, IRON[2 + k], L)


def brooch(p: Pix, cx, cy, r0, r1, night, seed=2):
    """A bronze brooch round the seal's pressed centre, from r0 to r1: a cast ring chip-carved with notches,
    lit along its upper left, a boss at each quarter, and the pin lying across its foot."""
    k = -1 if night else 0
    for y in range(math.floor(cy - r1) - 1, math.ceil(cy + r1) + 2):
        for x in range(math.floor(cx - r1) - 1, math.ceil(cx + r1) + 2):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            rho = math.hypot(dx, dy)
            if not (r0 - 0.4 <= rho <= r1 - 0.6):
                continue
            facing = (dx * -0.6 + dy * -0.8) / max(0.1, rho)
            a = math.degrees(math.atan2(dy, dx))
            t = 4 if facing > 0.55 else 3 if facing > -0.2 else 2
            if rho > r1 - 1.6:
                t = min(6, t + 1) if facing > 0.3 else 1
            elif rho < r0 + 0.6:
                t = 1 if facing > 0 else 2
            elif int(a + 180) % 24 < 5 and r0 + 1.5 < rho < r1 - 2.5:
                t = 1
            p.px(x, y, BRONZE[max(0, t + k)])
    rm = (r0 + r1) / 2
    for a in (0, 90, 180, 270):
        bx, by = cx + rm * math.cos(math.radians(a)), cy + rm * math.sin(math.radians(a))
        sphere(p, bx, by, 2.2, BRONZE, lo=2, hi=6, outline=False)
    for i in range(round(r1 * 1.6)):
        x = round(cx - r1 * 0.8 + i)
        p.px(x, round(cy + r1 - 1), IRON[5 + k] if i % 3 else IRON[3 + k])


# The serpent's head on a runestone, 12 by 9, facing right at the top of the stone where its body comes in from
# the left along the band's rows: the band's grooves (k) and red ochre (R lit, r), its eye (e), its open jaws
# with a fang (t) closing on the ring its tail is tied in.
RUNE_HEAD = [
    "kkkkkkkkkkk.....",
    "RRRRRRRRRRRkkk..",
    "rrrrrrrrrrRRRRkk",
    "kkkkkrrrrkkrrrRk",
    "....krrrkeekrrRk",
    "....krrrkkkrrrrk",
    "....krrrrrrrkkkk",
    ".....krrrrk.t.t.",
    ".....krrrrkkkkkk",
    "......kkrrrrRRRk",
    "........kkkkkkk.",
]


def runestone(p: Pix, night: bool, uid="rs"):
    """A runestone over the whole canvas, standing on the foot of the sheet: a slab of granite with a rounded,
    uneven top, chipped and higher at one shoulder, the page showing past it, its face grey and speckled with
    lichen, its rim lit along the top and left and dark along the right, and a serpent carved round inside its
    edge and painted red ochre, as the old stones were: its body cut between two grooves, segmented with
    nicks, its tail coiled into a ring at the top of the stone and its head coming round to bite it; tufts of
    grass at its foot. By night the granite is dark and the paint deep."""
    from collections import deque
    Rk, T = RAMP["rock"], RAMP["turf"]
    w, h = p.w, p.h
    k = -1 if night else 0
    rnd = random.Random(5)
    tops = []
    for x in range(w):
        u = x / (w - 1)
        t = 1.0 + 1.2 * u + 0.9 * math.sin(2 * math.pi * 2.6 * u + 1.1) + 0.6 * math.sin(2 * math.pi * 7.3 * u)
        for cx, r in ((15, 15), (w - 22, 22)):
            if (x < cx and cx < w / 2) or (x >= cx and cx > w / 2):
                dx = abs(x + 0.5 - cx)
                t = max(t, r - math.sqrt(max(0.0, r * r - dx * dx)))
        tops.append(max(0, round(t)))
    side = [round(0.8 + 0.8 * math.sin(y / 9 + 0.6)) if y > 20 else 0 for y in range(h)]
    inside = {(x, y) for x in range(w) for y in range(tops[x], h)
              if (x >= side[y] or y < 20) and (x < w - side[y] or y < 20)}
    dist, q = {}, deque()
    for (x, y) in inside:
        if any((x + dx, y + dy) not in inside for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            dist[(x, y)] = 0
            q.append((x, y))
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n in inside and n not in dist:
                dist[n] = dist[(x, y)] + 1
                q.append(n)
    face = Rk[1] if night else Rk[5]
    flecks = (Rk[2], Rk[0], T[2], OCHRE[1]) if night else (Rk[4], Rk[6], T[5], OCHRE[5])
    cols: dict = {}
    for yy in range(14):
        for xx in range(22):
            r = rnd.random()
            if r < 0.16:
                c = flecks[0 if r < 0.08 else 1 if r < 0.11 else 2 if r < 0.145 else 3]
                cols.setdefault(c, {}).setdefault(yy, []).append(xx)
    paths = "".join(f'<path stroke="{c}" d="{Pix._d(r)}"/>' for c, r in cols.items())
    p.defs.append(f'<pattern id="{uid}a" width="22" height="14" patternUnits="userSpaceOnUse">{paths}</pattern>')
    rows: dict = {}
    for (x, y) in inside:
        rows.setdefault(y, []).append(x)
    shape = Pix._d(rows)
    p.under.append(f'<path stroke="{face}" d="{shape}"/><path stroke="url(#{uid}a)" d="{shape}"/>')
    groove, lit, paint = (Rk[0], RED[3], RED[2]) if night else (Rk[2], RED[4], RED[3])
    rim_lit, rim_dark = (Rk[3], Rk[0]) if night else (Rk[6], Rk[3])
    # the knot: the tail's ring at the top of the stone, a little right of the middle, and the head left of it
    kx = w // 2 + 4
    ky = max(tops[kx - 8:kx + 9]) + 7
    gap = range(kx - 24, kx - 7)
    for (x, y), d in dist.items():
        if d == 0:
            up_left = (x - 1, y) not in inside or (x, y - 1) not in inside
            p.px(x, y, rim_lit if up_left and y < h - 1 else rim_dark)
        elif d in (1, 2, 3, 4) and not (x in gap and y < ky):
            if d in (1, 4):
                p.px(x, y, groove)
            else:
                above, left = dist.get((x, y - 1), 0), dist.get((x - 1, y), 0)
                first = (above in (1, 4) and (x, y - 1) in inside) or (left in (1, 4) and (x - 1, y) in inside)
                p.px(x, y, lit if first else paint)
    # the body's segments and the runes nicked along it
    for (x, y), d in dist.items():
        if d in (2, 3) and not (x in gap and y < ky):
            level = dist.get((x - 1, y)) == d and dist.get((x + 1, y)) == d
            along = x if level else y
            if along % 5 == 0:
                p.px(x, y, groove)
    for yy in range(ky - 8, ky + 9):
        for xx in range(kx - 8, kx + 9):
            r = math.hypot(xx + 0.5 - kx, yy + 0.5 - ky)
            if 3.2 <= r <= 7.6:
                facing = (xx + 0.5 - kx) * -0.6 + (yy + 0.5 - ky) * -0.8
                c = groove if (r < 4.2 or r > 6.6) else lit if facing > 0 else paint
                p.px(xx, yy, c)
            elif r < 3.2 and dist.get((xx, yy), 9) in (1, 2, 3, 4):
                p.px(xx, yy, face)
    hy = tops[kx - 24] + 1
    p.sprite(kx - 24, hy, RUNE_HEAD, {"k": groove, "R": lit, "r": paint, "e": BRONZE[5], "t": CREAM[6 + k]})
    # tufts of grass at the stone's foot
    for x0 in (2, 9, w - 12, w - 5):
        for (dx, dy, t) in ((0, -1, 4), (1, -2, 5), (2, -1, 3), (3, -3, 5), (4, -1, 4), (1, -1, 3), (3, -1, 2)):
            p.px(x0 + dx, h + dy, T[t + k])


def braid(p: Pix, x, y, w, h, night, L="base"):
    """A woven band for the ribbon under a seal: the block in red wool with its upper and lower edges
    braided in cream and ochre, and the ends fringed."""
    k = -1 if night else 0
    weave = (CREAM[4], OCHRE[3], RED[2]) if night else (CREAM[5], OCHRE[4], RED[3])
    for xx in range(x - 3, x + w + 3):
        for yy in (y, y + h - 1):
            p.px(xx, yy, weave[((xx - x) // 2 + (0 if yy == y else 1)) % 3], L)
    for i in range(1, 4):
        for yy in range(y + 1, y + h - 1):
            if (yy - y + i) % 2:
                p.px(x - i, yy, RED[2 + k], L)
                p.px(x + w - 1 + i, yy, RED[2 + k], L)


# --------------------------------------------------------------------------- icons
# The things of the ship for the link buttons, 9 by 7, bold enough to read at the kit's size: a painted
# round shield, crossed axes, the longship under sail, and a hammer pendant. Tones: r R red, c cream,
# i I iron, b B bronze, o oak, # the button's ink.
ICONS = {
    "shield": ["..RRRRR..", ".RcccccR.", "RccrrrccR", "RcrrIrrcR", "RccrrrccR", ".RcccccR.", "..RRRRR.."],
    "axes": ["II.....II", "IIi.o.iII", "iI.o.o.Ii", "...o.o...", "....o....", "...o.o...", "..o...o.."],
    "ship": ["....o..d.", ".rcrcrcdd", ".rcrcrc.d", ".rcrcrc.d", "d...o...d", "dddddddd.", ".dddddd.."],
    "hammer": ["...cc.cc.", "...c...c.", "BBBBbBBBB", "bBBbbbBBb", "bbbbbbbbb", "...bBb...", "...bbb..."],
}


def icon_pal(night: bool, ink=None) -> dict:
    """The icons' tones on a button by day or by night."""
    k = -1 if night else 0
    return {"r": RED[3 + k], "R": RED[1], "c": CREAM[5 + k], "i": IRON[3 + k], "I": IRON[6 + k], "b": BRONZE[3 + k],
            "B": BRONZE[5 + k], "o": ROPE[4 + k], "d": TAR[2] if night else OAK[1], "#": ink}

