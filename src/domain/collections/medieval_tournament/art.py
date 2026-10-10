# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Tournament set's scenery and sprites, drawn on the shared pixel canvas.

The pavilion's canvas every sheet is cut from, its striped poles with their gilt finials and guy ropes, the
dagged valance along its top and the lanterns hung from it by night, letters of painted silk edged in gold cord,
the lists with their tilt, the knights in plate on their caparisoned horses under their crests, the pavilions open,
laced shut or with a knight being armed in the door, the tree of shields, the tiered stand with its ladies and
lords and its herald, the quintain in its yard, the tilt's barrier a footer stands on with the herald's trumpet
and lantern at its corner, the torches of the night, and the things of the tournament every element and badge is
made of: lances, vamplates, bannerets, the herald's score cheque, crested helms with their mantling and the prize
on its cushion. Everything is shaded from the one light in the upper left on the set's own ramps."""
from __future__ import annotations

import math
import random

from ...holidays.designs.banners import MARK_Y
from ...holidays.pixel import FONTS, Paint, Pix, fold, num
from ..hand import MEDIEVAL
from .palette import C, LIT, NIGHT_SKY, RAMP, SKINS, X, step

K = RAMP["sable"][1]                 # the outline every figure is drawn round with
V, A, G, S = RAMP["vert"], RAMP["argent"], RAMP["or"], RAMP["steel"]
WD, FL, CV, DU = RAMP["wood"], RAMP["flame"], RAMP["canvas"], RAMP["dusk"]


def skin(n: int, night: bool) -> dict:
    """A face and its hands on the hand's skin `n` (0 the lightest, 2 the darkest), a tone darker by night: `f` the
    face, `F` where the light falls on it, `e` its shade and `d` an eye, a single dark unit."""
    k = -1 if night else 0
    R = SKINS[n]
    return {"f": R[3 + k], "F": R[4 + k], "e": R[2 + k], "d": R[0]}


def mark_box(p: Pix, margin=2) -> tuple:
    """The box the month's mark takes at the top centre of a header, `margin` units more all round: (x0, y0, x1, y1),
    ends excluded. A header keeps it clear of its scene whether or not it is drawn as its month's design."""
    n = MEDIEVAL.mark_size
    x0, y0 = p.w // 2 - n // 2, MARK_Y - n // 2
    return (x0 - margin, y0 - margin, x0 + n + margin, y0 + n + margin)


def flip(art: list) -> list:
    """Pixel art turned to face the other way."""
    return [row[::-1] for row in art]


def stamp(p: Pix, x, y, art, pal, L="base", below=None, above=None):
    """Pixel art from rows of characters with its top-left at (x, y), each looked up in `pal`; a character the
    palette lacks is left clear. Rows from `below` down, and above `above`, are left out: what a fence or a
    stand hides."""
    for j, row in enumerate(art):
        yy = y + j
        if (below is not None and yy >= below) or (above is not None and yy < above):
            continue
        for i, ch in enumerate(row):
            c = pal.get(ch)
            if c:
                p.px(x + i, yy, c, L)


def keep(p: Pix, cells):
    """Remember cells a shape fills without setting them pixel by pixel, so a check that gathers what a scene draws
    finds them as it finds pixels set one by one."""
    if not hasattr(p, "filled"):
        p.filled = set()
    p.filled.update(cells)


def prop(p: Pix, x0, y0, x1, y1):
    """Remember the box a tall sprite stands in (a pavilion with its pennon, a banner, a lance held upright), so
    what is hung from the valance afterwards keeps off it."""
    if not hasattr(p, "props"):
        p.props = []
    p.props.append((x0, y0, x1, y1))


def _blocks(rows: dict) -> str:
    """Path data filling the cells {y: [x, ...]} as blocks: each row's runs, a run that lies the same in the rows
    under it one block with them, every move after the first relative to the last block's corner."""
    blocks, last = [], {}
    for y in sorted(rows):
        xs = sorted(set(rows[y]))
        runs, start = [], xs[0]
        for a, b in zip(xs, xs[1:] + [None]):
            if b != a + 1:
                runs.append((start, a - start + 1))
                start = b
        now = {}
        for run in runs:
            block = last.get(run)
            if block is not None and block[1] + block[3] == y:
                block[3] += 1
            else:
                block = [run[0], y, run[1], 1]
                blocks.append(block)
            now[run] = block
        last = now
    out, at = [], None
    for x, y, w, h in sorted(blocks, key=lambda b: (b[1], b[0])):
        out.append((f"M{x} {y}" if at is None else f"m{x - at[0]} {y - at[1]}") + f"h{w}v{h}h-{w}z")
        at = (x, y)
    return "".join(out).replace(" -", "-")


def paths(cols: dict) -> str:
    """Paths for {colour or colour:alpha: {y: [x, ...]}}: each colour's cells as strokes along their rows, or as
    filled blocks where the rows repeat enough to make that shorter (a pattern's tile drawn either way is the same)."""
    out = []
    for c, rows in cols.items():
        if not rows:
            continue
        col, a = c.split(":") if ":" in c else (c, None)
        strokes, blocks = Pix._d(rows), _blocks(rows)
        if len(blocks) + 2 < len(strokes):
            out.append(f'<path fill="{col}"' + (f' fill-opacity="{a}"' if a else "") + f' d="{blocks}"/>')
        else:
            out.append(f'<path stroke="{col}"' + (f' stroke-opacity="{a}"' if a else "") + f' d="{strokes}"/>')
    return "".join(out)


# --------------------------------------------------------------------------- the paper
PANEL = 24          # a panel of the pavilion's canvas: two of them, plain and dyed, repeat across a sheet


def _canvas(uid: str, night: bool) -> str:
    """A pattern tile of the pavilion's canvas, two panels wide and four rows tall: each panel's seam, the fold
    of the cloth into it in shade, the running stitch down it, and a faint weave across the cloth. By day the
    second panel is dyed the livery's pale green; by night both lie in the lanterns' light, the dyed one deeper."""
    T = 2 * PANEL
    cols: dict = {}

    def put(c, x, y):
        cols.setdefault(c, {}).setdefault(y, []).append(x)
    for y in range(4):
        for x in range(T):
            dyed = x >= PANEL
            u = x % PANEL
            if night:
                if dyed and u not in (0, 1):
                    put(f"{X['shade_ink']}:.16", x, y)
                if u == 0:
                    put(DU[0], x, y)
                elif u == 1 and y < 2:
                    put(f"{DU[5]}:.5", x, y)
                elif u == PANEL - 1:
                    put(f"{X['shade_ink']}:.2", x, y)
                continue
            if dyed and u not in (0, 1):
                put(X["panel_b"], x, y)
            if u == 0:
                put(X["seam_b"] if dyed else X["seam_a"], x, y)
            elif u == 1 and y == 0:
                put(X["stitch_b"] if dyed else X["stitch_a"], x, y)
            elif u == PANEL - 1:
                put(X["seam_a"] if dyed else X["seam_b"], x, y)
    return f'<pattern id="{uid}c" width="{T}" height="4" patternUnits="userSpaceOnUse">{paths(cols)}</pattern>'


def band_edges(h: int) -> list:
    n = len(NIGHT_SKY)
    return [round(i * h / n) for i in range(n + 1)]


def paper(p: Pix, night: bool, uid="p"):
    """The ground a drawing sits on: the canvas of a pavilion, unbleached and sunlit by day in broad panels, every
    other one dyed the livery's pale green, stitched at its seams; by night the same canvas from inside, lit by the
    lanterns hung along the ridge, warm under them and falling to deep blue toward the hem and the poles."""
    w, h = p.w, p.h
    p.sheet = uid
    p.night = night
    if not night:
        p.under.append(f'<rect width="{w}" height="{h}" fill="{X["panel_a"]}"/>')
    else:
        edges = band_edges(h)
        for i, col in enumerate(NIGHT_SKY):
            if edges[i + 1] > edges[i]:
                p.under.append(f'<rect y="{edges[i]}" width="{w}" height="{edges[i + 1] - edges[i]}" fill="{col}"/>')
    p.defs.append(_canvas(uid, night))
    p.under.append(f'<rect width="{w}" height="{h}" fill="url(#{uid}c)"/>')
    if night:
        lanterns(p)


GLOW = (0.1, 0.2, 0.32)          # a flame's glow in the air round it, ring by ring: deep orange, so that over
                                 # the night's blue it reads as warm light and never as a grey smudge
WASH = (0.03, 0.06, 0.09)        # the lanterns' warm wash high on the night's canvas, ring by ring to its heart
POOL = (0.025, 0.05, 0.07)       # the pool of light under a hanging lantern: the two together still leave every
                                 # word its contrast on the brightest of the night's bands


def lanterns(p: Pix):
    """By night the light of the lanterns hung along the ridge: a broad warm wash high on the canvas, warmest under
    the ridge's middle, and the canvas falling to deep blue at the poles and toward the hem."""
    w, h = p.w, p.h
    halo(p, w / 2, -10, w * 0.62, min(h * 0.9, 84), FL[2], WASH, shape=True)
    for x0 in (0, w):
        p.halo(x0, h * 0.62, 34, h * 0.9, RAMP["night"][1], (0.16, 0.32), shape=True)


# A lantern of pierced brass hung on its chain from the valance, 7 by 19: its hook, the chain, the pointed roof lit on
# its left, the glass with the flame in it, the foot and its drop. 1 the outline; 5 4 3 2 the brass light to dark;
# 7 the lit glass; 6 the flame, which flickers.
HANGING = [
    "...1...",
    "..121..",
    "...1...",
    "...2...",
    "...1...",
    "...2...",
    "...1...",
    "..141..",
    ".15431.",
    "1544331",
    "1111111",
    "1376721",
    "1366621",
    "1376721",
    "1377721",
    "1111111",
    ".14321.",
    "..121..",
    "...1...",
]
HANG_TOP = 7        # the row a hanging lantern's hook is caught on, behind the valance's dags


def hanging_lanterns(p: Pix):
    """By night a lantern hung from the valance near each pole of a header, lit: each as far in from its pole as
    the words leave it, or failing that a little further in, never within two units of a word with its glow, nor of
    a pavilion, a banner or a lance the scene has set up, the flame flickering in its glass, a small glow round the
    glass and a pool of its light on the canvas under it. Where nothing leaves it room, that lantern hangs out of
    sight, as the left one does where the standard of the lists has its cresset burning and the right one where
    the stand's lanterns burn under its canopy."""
    w = p.w
    lw, lh = len(HANGING[0]), len(HANGING)
    top = HANG_TOP
    inner = max(7, round(w * 0.09))
    reach = round(w * 0.2)
    for i, xs in enumerate(([*range(inner, 5, -1), *range(inner + 1, reach)],
                            [*range(w - inner - lw, w - 5 - lw), *range(w - inner - lw - 1, w - reach - lw, -1)])):
        if (i == 0 and getattr(p, "cresset", False)) or (i == 1 and getattr(p, "lit_stand", False)):
            continue
        x = next((x for x in xs if p.clear_of_words(x - 6, top - 2, x + lw + 6, top + lh + 5)
                  and all(x + lw + 2 <= a or x - 2 >= c or top + lh + 2 <= b or VALANCE_FOOT >= d
                          for a, b, c, d in getattr(p, "props", ()))), None)
        if x is None:
            continue
        cx, cy = x + lw / 2, top + 13
        halo(p, cx, cy + 10, 30, 30, FL[2], POOL, shape=True)
        halo(p, cx, cy, 7, 7, FL[3], GLOW, L=flick(p, i + 2, back=True))
        cells = {(x + c, top + r): ch for r, row in enumerate(HANGING) for c, ch in enumerate(row) if ch != "."}
        pal = {"1": K, "2": G[1], "3": G[3], "4": G[4], "5": G[6], "6": FL[6], "7": FL[4]}
        for (xx, yy), ch in cells.items():
            p.px(xx, yy, pal[ch], flick(p, i + 2) if ch == "6" else "base")
        lamp(p, cx, cy, 12, i + 2, {xy for xy, ch in cells.items() if ch in "67"})


def bg_at(p: Pix, night: bool, y: int) -> str:
    """The colour behind row `y`: by day the key a label's backing is laid in, lifted off the canvas when the
    drawing is finished (see `lift_keys`), so a backing over a dyed panel leaves the panel; by night the row's
    band, which `lift_keys` lifts too."""
    if not night:
        return X["key"]
    edges = band_edges(p.h)
    for i in range(len(NIGHT_SKY)):
        if y < edges[i + 1]:
            return NIGHT_SKY[i]
    return NIGHT_SKY[-1]


def lift_keys(p: Pix):
    """Lift every label's backing off the drawing once it is finished: the backing has already cleared what lay
    under the label (a dimension's line, a wire, the time line), and the canvas, its panels and its light show
    through where it was."""
    keys = {X["key"]} | set(NIGHT_SKY)
    base = p.layers["base"]
    for xy in [xy for xy, c in base.items() if c in keys]:
        del base[xy]


# --------------------------------------------------------------------------- spangles
def spangle(p: Pix, x, y, L="base", big=False):
    """A gold spangle sewn on the canvas catching the light: a bright heart and four short arms."""
    p.px(x, y, G[6], L)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        p.px(x + dx, y + dy, G[4], L)
    if big:
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            p.px(x + dx, y + dy, G[3] + ":0.6", L)


def stars(p: Pix, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
    """By night the gold spangles sewn here and there on the pavilion's canvas, catching the lanterns' light: most
    a single point, a few with arms, some twinkling in a moving header. None inside a box in `avoid`. A drawing made
    lighter sews a third of them."""
    rnd = random.Random(seed)
    for i in range(n if not p.lite else (n + 2) // 3):
        x, y = rnd.randrange(x0, x1), rnd.randrange(y0, y1)
        k = rnd.random()
        if any(a <= x < c and b <= y < d for a, b, c, d in avoid):
            continue
        if k < 0.6 or faint:
            p.px(x, y, G[3] + (":0.5" if faint else ":0.8"), "haze")
        elif k < 0.9:
            p.px(x, y, G[5], p.twinkle(i, back=True) if twinkling and rnd.random() < 0.6 else "haze")
        else:
            spangle(p, x, y, L=p.twinkle(i, back=True) if twinkling else "haze", big=rnd.random() < 0.4)


# --------------------------------------------------------------------------- the frame
POLE = 4            # the columns a tent pole and its shadow take at each side of a sheet
FINIAL = [          # the gilt finial on a pole's head, 7 by 9: a spike, a ball, a collar over the pole
    "...Y...",
    "...G...",
    "..YGg..",
    ".YGGGg.",
    "KYGGGgo",
    "KGGGggo",
    ".KgggoK",
    "..KooK.",
    "..KGgK.",
]


def _pole(uid: str, night: bool) -> str:
    """A pattern tile of a tent pole, four columns by six rows: bands of the livery's green and white wound
    round it, lit down its left and shaded down its right, and its shadow on the canvas beside it."""
    k = -1 if night else 0
    cols: dict = {}
    for y in range(6):
        for x in range(4):
            if x == 3:
                c = K
            else:
                green = ((y + x) // 3) % 2 == 0
                R, t = (V, (5, 4, 2)[x]) if green else (A, (6, 5, 3)[x])
                c = R[max(0, t + k)]
            cols.setdefault(c, {}).setdefault(y, []).append(x)
    return f'<pattern id="{uid}" width="4" height="6" patternUnits="userSpaceOnUse">{paths(cols)}</pattern>'


def rope(p: Pix, x, y0, y1, night: bool, uid="rp", L="base"):
    """A guy rope hanging down the side of a sheet at column x: its strands twisted, light and dark by turns, and
    a wooden runner on it every so often."""
    k = -1 if night else 0
    if ("rope", uid) not in p.syms:
        p.defs.append(f'<pattern id="{uid}" width="1" height="4" patternUnits="userSpaceOnUse">'
                      f'<path stroke="{WD[3 + k]}" d="M.5 0v2"/><path stroke="{WD[5 + k]}" d="M.5 2v2"/></pattern>')
        p.syms[("rope", uid)] = uid
    p.shapes[L].append(f'<rect x="{x}" y="{y0}" width="1" height="{y1 - y0}" fill="url(#{uid})"/>')
    for y in range(y0 + 14, y1 - 6, 34):
        for dy, row in enumerate(("KK", "lL", "lL", "KK")):
            for dx, ch in enumerate(row):
                p.px(x - 1 + dx, y + dy, {"K": K, "l": WD[4 + k], "L": WD[2 + k]}[ch], L)


def finial(p: Pix, x, y, night: bool, L="base"):
    """The gilt finial on a pole's head, drawn once a file and set on each pole."""
    k = -1 if night else 0
    key = ("finial", night)
    if key not in p.syms:
        pal = {"Y": G[6 + k], "G": G[4 + k], "g": G[3 + k], "o": G[1], "K": K}
        p.symbol(key, {(i, j): pal[ch] for j, row in enumerate(FINIAL) for i, ch in enumerate(row) if ch in pal})
    p.use(key, x, y, L)


def _dags(uid: str, night: bool, w=6, h=2) -> str:
    """A pattern tile of a small scalloped edge, two scallops wide: green and white tongues, lit on their left,
    with a dark rim along their curve."""
    k = -2 if night else 0
    cols: dict = {}
    for i, R in enumerate((V, A)):
        lit, mid, dk = (R[4 + k // 2], R[3 + k // 2], R[1 + k // 2]) if R is V else (R[6 + k], R[5 + k], R[3 + k])
        for x in range(w):
            xx = i * w + x
            cols.setdefault(lit if x == 0 else dk if x == w - 1 else mid, {}).setdefault(0, []).append(xx)
            if 0 < x < w - 1:
                cols.setdefault(K if x in (1, w - 2) else dk, {}).setdefault(1, []).append(xx)
    return f'<pattern id="{uid}" width="{2 * w}" height="{h}" patternUnits="userSpaceOnUse">{paths(cols)}</pattern>'


def cord_pattern(p: Pix, night: bool) -> str:
    """The twist of a gold cord as a pattern three pixels each way: light, middle and dark gold by turns along the
    diagonal. Returns its id, made once a file."""
    key = ("cordpat", night)
    if key not in p.syms:
        tones = (G[6], G[5], G[3]) if night else (G[5], G[4], G[2])
        cols: dict = {}
        for y in range(3):
            for x in range(3):
                cols.setdefault(tones[(x + y) % 3], {}).setdefault(y, []).append(x)
        pid = f"cord{'n' if night else 'd'}"
        p.defs.append(f'<pattern id="{pid}" width="3" height="3" patternUnits="userSpaceOnUse">{paths(cols)}</pattern>')
        p.syms[key] = pid
    return p.syms[key]


def cord(p: Pix, x0, x1, y, night: bool, L="base"):
    """A gold cord along a row and the one under it, its strands twisted, with its shaded underside."""
    pid = cord_pattern(p, night)
    p.shapes[L].append(f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="2" fill="url(#{pid})"/>')
    keep(p, {(x, y + dy) for x in range(x0, x1) for dy in (0, 1)})


def frame(p: Pix, night: bool, header: bool = False, footer: bool = False, uid="fr"):
    """The sheet's border: a striped tent pole down each side with a gilt finial on its head and a guy rope beside
    it; along the top of any sheet but a header (whose valance `valance` hangs) a slim valance, a gold cord over a
    band of green and a dagged edge; along the foot the canvas's hem, which a footer leaves to the tilt's barrier
    that `footing` lays under it once its words are set."""
    w, h = p.w, p.h
    k = -1 if night else 0
    p.defs.append(_pole(uid + "p", night))
    top = 5
    p.shapes["base"].append(f'<rect y="{top}" width="4" height="{h - top}" fill="url(#{uid}p)"/>')
    p.shapes["base"].append(f'<rect x="{w - 4}" y="{top}" width="4" height="{h - top}" fill="url(#{uid}p)" '
                            f'transform="matrix(-1 0 0 1 {2 * w - 4} 0)"/>')
    for xx, side in ((4, 1), (w - 5, -1)):
        rope(p, xx, top + 3, h - 3, night)
    if not header:
        p.hline(0, w, 0, K)
        cord(p, 0, w, 1, night)
        p.hline(0, w, 3, V[2 + k])
        p.defs.append(_dags(uid + "d", night))
        p.shapes["base"].append(f'<rect y="4" width="{w}" height="2" fill="url(#{uid}d)"/>')
    for x in (-2, w - 5):
        finial(p, x, 0, night)
    if not footer:
        for x in range(4, w - 4):
            p.apx(x, h - 4, X["shade_ink"], 0.16, "base")
        p.hline(0, w, h - 3, CV[5 + k] if not night else DU[5])
        p.hline(0, w, h - 2, V[3 + k])
        p.hline(0, w, h - 1, K)


# --------------------------------------------------------------------------- the valance
DAG = 10            # a dag's width along the valance
DAG_ART = [         # a dag of the valance, its outer rows first: 0 lit edge, 1 body, 2 shaded edge, K its hem
    "0111111112",
    "0111111112",
    "0111111112",
    "K01111112K",
    ".K011112K.",
    "..KKKKKK..",
]
DAG_HEAD = 3        # the rows of a dag that hang still; the rest ripple
VALANCE_FOOT = 12   # the last row the valance and its fringe reach, two clear of a title's dimension


def _dag_cells(white: bool, night: bool, rows=range(0, 6)) -> dict:
    """A dag's cells (its rows `rows`), with its gold fringe hung under its hem: a thread under every pixel of the
    hem, every other one longer and in shade. By night the silk is in shadow and the white falls to grey."""
    k = -2 if night else 0
    R = A if white else V
    tones = (R[5 + k], R[4 + k], R[2 + k]) if white else (R[4 + k // 2], R[3 + k // 2], R[1 + k // 2])
    out = {}
    for j in rows:
        for i, ch in enumerate(DAG_ART[j]):
            if ch == ".":
                continue
            out[(i, j)] = K if ch == "K" else tones[int(ch)]
    if 5 in rows:
        for i in range(2, DAG - 2):
            out[(i, 6)] = G[4]
            if (i + (1 if white else 0)) % 2 == 0:
                out[(i, 7)] = G[2]
    return out


def dag_runs(p: Pix, x0, x1) -> tuple:
    """Where the valance's dags hang between x0 and x1: two runs, (left, count) each, that end either side of the
    month's mark's box, two units clear of it, so no dag is cut at the roundel's edge and the valance pauses under
    it whether or not it is drawn."""
    a, _, b, _ = mark_box(p)
    left, right = max(0, (a - x0) // DAG), max(0, (x1 - b) // DAG)
    return (a - left * DAG, left), (b, right)


def valance(p: Pix, x0, x1, night: bool, seed=0, L="base", uid="va"):
    """The valance along a header's top, from x0 to x1: a gold cord along its head over a band of green silk with a
    gold chevron embroidered along it, and under it the dags, rounded tongues of green and white by turns, each
    hemmed and fringed in gold, hanging in two runs that pause at the top centre for the month's mark (see
    `dag_runs`). The lower half of every dag and its fringe ripple in the wind, a wave running along the valance a
    dag at a time (two dags at a time in a drawing made lighter); a still drawing leaves them hanging. By night the
    silk lies in shadow and the gold catches the light. The band, the dags' heads and each group of dags that lift
    together are pattern tiles, laid once for both runs (the right run's tiles shifted to carry on where the left
    run's leave off), so the valance costs little however wide."""
    k = -1 if night else 0
    p.hline(x0, x1, 0, K, L)
    cord(p, x0, x1, 1, night, L)
    band: dict = {}
    for x in range(4):
        zig = (x // 2) % 2
        for j, t in enumerate((3, 2)):
            c = G[4 + k] if j == zig else V[t + k]
            band.setdefault(c, {}).setdefault(j, []).append(x)
    p.defs.append(f'<pattern id="{uid}b" y="3" width="4" height="2" patternUnits="userSpaceOnUse">{paths(band)}'
                  f'</pattern>')
    p.shapes[L].append(f'<rect x="{x0}" y="3" width="{x1 - x0}" height="2" fill="url(#{uid}b)"/>')
    keep(p, {(x, y) for x in range(x0, x1) for y in range(3, 5)})
    (off, left), (rx, right) = dag_runs(p, x0, x1)
    at = [off + i * DAG for i in range(left)] + [rx + i * DAG for i in range(right)]   # each dag's left edge
    n = len(at)
    top = 5
    for a, b in ((x0, off), (off + left * DAG, rx), (rx + right * DAG, x1)):
        p.hline(a, b, top, V[1 + k], L)

    def lay(layer, pid, y, h, first, last, every):
        """Every `every`-th dag from the `first` to the `last`, by their order along the valance, laid in the pattern
        `pid`, which tiles them as though the two runs were one: the left run's in place, and the right run's in a
        block shifted along to where that run hangs."""
        ends = ((first, first + (left - 1 - first) // every * every), (left + (first - left) % every, last))
        for lo, hi in ends:
            if not (first <= lo <= hi <= last):
                continue
            dx = rx - off - left * DAG if lo >= left else 0
            shift = f' transform="translate({dx} 0)"' if dx else ""
            p.shapes[layer].append(f'<rect x="{off + lo * DAG}" y="{y}" width="{(hi - lo + 1) * DAG}" height="{h}" '
                                   f'fill="url(#{pid})"{shift}/>')
    heads: dict = {}
    for i in range(2):
        white = (i + seed) % 2 == 1
        for (dx, dy), c in _dag_cells(white, night, rows=range(DAG_HEAD)).items():
            heads.setdefault(c, {}).setdefault(dy, []).append(i * DAG + dx)
    p.defs.append(f'<pattern id="{uid}h" x="{off}" y="{top}" width="{2 * DAG}" height="{DAG_HEAD}" '
                  f'patternUnits="userSpaceOnUse">{paths(heads)}</pattern>')
    if n:
        lay(L, f"{uid}h", top, DAG_HEAD, 0, n - 1, 1)
    keep(p, {(x + dx, y) for x in at for dx in range(DAG) for y in range(top, top + DAG_HEAD)})
    groups = 4 if not p.lite else 2
    for g in range(min(groups, n)):
        white = (g + seed) % 2 == 1
        key = ("dag", white, night)
        if key not in p.syms:
            p.symbol(key, {(dx, dy - DAG_HEAD): c
                           for (dx, dy), c in _dag_cells(white, night, rows=range(DAG_HEAD, 6)).items()})
        lift = [1 if (s - 2 * g) % (2 * groups) in (0, 1) else 0 for s in range(2 * groups)]
        Lg = p.layer(f"rip{g}", ("bob", lift, 2.4), z=0.6)
        last = g + (n - 1 - g) // groups * groups
        p.defs.append(f'<pattern id="{uid}r{g}" x="{off + g * DAG}" y="{top + DAG_HEAD}" width="{groups * DAG}" '
                      f'height="5" patternUnits="userSpaceOnUse"><use href="#{p.syms[key]}"/></pattern>')
        lay(Lg, f"{uid}r{g}", top + DAG_HEAD, 5, g, last, groups)
        keep(p, {(at[i] + dx, top + dy) for i in range(g, n, groups)
                 for (dx, dy) in _dag_cells(white, night, rows=range(DAG_HEAD, 6))})
    if night:
        a, _, b, _ = mark_box(p)
        for i, x in enumerate(range(x0 + 7, x1 - 4, 23)):
            if not a <= x < b:
                p.px(x, 1, G[6], p.twinkle(i))


# --------------------------------------------------------------------------- the silk title
def silk_fill(r, c, scale, night):
    """Painted silk: a band a row of the face, its sheen high on each stroke and its fold dark at the foot."""
    band = min(6, r // scale)
    if night:
        return (V[5], V[6], V[5], V[4], V[4], V[4], V[3])[band]
    return (V[3], V[4], V[3], V[2], V[2], V[2], V[1])[band]


SILK = Paint("silk", silk_fill)


def _glyph_cells(ch: str, scale: int) -> set:
    g = FONTS["57"][0][ch]
    return {(col * scale + dx, r * scale + dy) for r, cols in enumerate(g[1]) for col in cols
            for dy in range(scale) for dx in range(scale)}


def _cord_symbols(p: Pix, ch: str, scale: int, shaded: bool = True) -> tuple:
    """The gold cord laid round a letter, drawn once a letter and size as shapes with no colour of their own: the
    ring a pixel wide all round the letter, stroked with the cord's twist, and (when `shaded`) the part of it along
    the letter's lower and right edges, where the cord stands off the canvas in shade."""
    key, low = ("cord", ch, scale), ("cordshade", ch, scale)
    if key not in p.syms or (shaded and low not in p.syms):
        cells = _glyph_cells(ch, scale)
        ring = set()
        for (x, y) in cells:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    q = (x + dx, y + dy)
                    if q not in cells:
                        ring.add(q)
        p.symbol(key, {q: 1 for q in ring}, mono=True)
        if shaded:
            under = {(x, y) for (x, y) in ring if ((x - 1, y) in cells or (x, y - 1) in cells
                                                  or (x - 1, y - 1) in cells)
                     and not ((x + 1, y) in cells or (x, y + 1) in cells)}
            p.symbol(low, {q: 1 for q in under}, mono=True)
    return key, (low if shaded else None)


AROUND = tuple((dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dx or dy)
LOW = ((1, 0), (0, 1), (1, 1))      # where the cord lies below or right of a stroke, in shade...
HIGH = ((-1, 0), (0, -1))           # ...unless it also lies left of or above one, where it is lit


def _shifted(tid: str, offsets) -> str:
    """The group `tid` placed again at each of `offsets`, a pixel or so from where it lies."""
    return "".join(f'<use href="#{tid}"' + (f' x="{dx}"' if dx else "") + (f' y="{dy}"' if dy else "") + "/>"
                   for dx, dy in offsets)


def silk_title(p: Pix, x, y, s, night: bool, scale: int, motion: bool = False, L="base") -> int:
    """A title in letters of painted silk appliqued on the canvas, edged in gold cord: each letter's shadow on the
    sunlit canvas, the cord laid round it, its underside in shade, and the silk in bands, its sheen high on every
    stroke. In a wide moving header a gleam of light runs slowly across the silk now and then; by night the cord
    catches the lanterns' light and glints. A small title's cord is laid plain, its twist too fine to read. The line's
    letters are set once, the silk's and the cord's each as a group the drawing places as often as it needs them (the
    gleam is the silk's group again), so a long title costs little more than its letters. A title two pixels to the
    font's unit has its plain cord laid round the whole line at once: the line's letters placed again a pixel off
    on every side, then a pixel below and right in shade and a pixel above and left lit again, and the letters over
    them, which comes out pixel for pixel as each letter's own ring would, its letters standing far enough apart that
    no ring meets the next letter. Returns the width."""
    glyphs, _, space = FONTS["57"]
    s = fold(s, "57")
    cx = x
    placed = []
    for ch in s:
        if ch == " ":
            cx += (space + 1) * scale
            continue
        placed.append((ch, cx))
        cx += (glyphs[ch][0] + 1) * scale
    w = cx - x - scale
    if not placed:
        return max(0, w)
    tid = f"tt{len(p.defs)}"
    twist = f"url(#{cord_pattern(p, night)})" if scale >= 3 else (G[4] if not night else G[5])
    shade = G[1] if not night else G[3]
    whole = scale == 2
    rings, unders, letters = [], [], []
    for ch, gx in placed:
        if not whole:
            ring, under = _cord_symbols(p, ch, scale)
            rings.append(f'<use href="#{p.syms[ring]}" x="{gx - x}"/>')
            unders.append(f'<use href="#{p.syms[under]}" x="{gx - x}"/>')
        key = ("glyph", "57", ch)
        if key not in p.syms:
            p.symbol(key, {(col, r): 1 for r, cols in enumerate(glyphs[ch][1]) for col in cols}, mono=True)
        letters.append(f'<use href="#{p.syms[key]}" x="{num((gx - x) / scale)}"/>')
    group = f'<g id="{tid}" transform="translate({x} {y}) scale({scale})">{"".join(letters)}</g>'
    if whole:
        p.defs.append(f'{group}<g id="{tid}r">{_shifted(tid, AROUND)}</g>')
        shadow = f'<use href="#{tid}r" x="1" y="1" stroke="{X["shade_ink"]}" opacity=".3"/>'
        low = f'<g stroke="{shade}">{_shifted(tid, LOW)}</g><g stroke="{twist}">{_shifted(tid, HIGH)}</g>'
    else:
        p.defs.append(f'<g id="{tid}r" transform="translate({x} {y})">{"".join(rings)}</g>{group}')
        shadow = f'<use href="#{tid}r" x="1" y="1" stroke="{X["shade_ink"]}" stroke-opacity=".3"/>'
        low = f'<g transform="translate({x} {y})" stroke="{shade}">{"".join(unders)}</g>'
    silk = p._pattern(SILK, scale, night)
    body = ((shadow if not night else "") + f'<use href="#{tid}r" stroke="{twist}"/>' + low
            + f'<use href="#{tid}" stroke="url(#{silk})"/>')
    p.raw(0.1, body, body)
    rows = max(len(glyphs[ch][1]) for ch, _ in placed)
    p.words.append((x - 1, y - 1, x + w + 1, y + rows * scale + 1))
    if motion and scale >= 2:
        gleam(p, x, y, scale, w, tid, night)
    if night and scale >= 2:
        for i, (ch, gx) in enumerate(placed[1::3]):
            p.px(gx - 1, y - 1, G[6], p.twinkle(i))
    return w


def gleam(p: Pix, x, y, scale, w, tid, night):
    """The gleam that runs across a silk title: its letters again (the line's group `tid`) in the silk's palest
    sheen, seen only through a narrow slanting window that sweeps across the line, rests, and comes round again
    every `glint` seconds of the collection's hand, as every title of the year glints."""
    h = 7 * scale
    band = 3 * scale
    cid = f"gl{len(p.raws)}"
    a, b = x - band - h, x + w + band
    poly = f"0 {y + h} {band} {y + h} {band + h} {y - 1} {h} {y - 1}"
    sheen = V[6] if not night else X["glint"]
    dur = num(MEDIEVAL.glint)
    moving = (f'<clipPath id="{cid}"><polygon points="{poly}"><animateTransform attributeName="transform" '
              f'type="translate" values="{a} 0;{b} 0;{b} 0" keyTimes="0;.45;1" dur="{dur}s" '
              f'repeatCount="indefinite"/></polygon></clipPath><g clip-path="url(#{cid})" stroke="{sheen}" '
              f'stroke-opacity=".7"><use href="#{tid}"/></g>')
    p.raw(0.4, moving, "")


# --------------------------------------------------------------------------- the knights
# A horse at the charge, facing right, in a caparison to its fetlocks, hand-drawn: its ear sleeves, the eye hole,
# the face going down to the muzzle and the bit; the cloth over the neck and the body, lit along the back, its
# folds, the gold border over the hem and the hem dagged. K outline; 2-5 the caparison dark to light; g G Y the
# gold border; e the eye; b the bit; t T the tail.
HORSE = [
    "......................K.K...........",
    ".....................K4KK5K.........",
    "....................K5544554K.......",
    "..................KK554444444K......",
    "................KK5544444KKK4K......",
    "...............K55444444KeK44K......",
    ".............KK5444444444KK3444K....",
    "...KKKKKKKKKK554444443344444444K....",
    "..K55555555554444444443334K34444K...",
    "tTK444444444444443333333KK.KK3444K..",
    "TtK44344443444433333333K....K3b42K..",
    ".K443343334333433333332K.....KK2K...",
    ".K4333233323333233333333K...........",
    ".KgggggggggggggggggggggggK..........",
    ".KGYGGGYGGGGYGGGGYGGGGYGGK..........",
    ".K23332333233323332333233K..........",
    "..KK2KK2KK2KK2KK2KK2KK2KK...........",
]
# The legs below the hem at the charge: (x, y, rows): the far hind under the body, the near hind thrown back, the
# far fore folded, the near fore reaching. h H j the leg, k the hoof.
LEGS = [
    (9, 16, ["KhK.", ".KhK", ".KhK", "..Kk"]),
    (2, 16, ["...KHK", "..KHK.", ".KjK..", "KHK...", "Kk...."]),
    (18, 16, ["KhK", "KhK", ".KhK", "KhK.", "Kk.."]),
    (21, 16, ["KHK...", ".KjK..", "..KHK.", "...KHK", "....Kk"]),
]
# Standing: the legs square under the body, a forefoot raised, pawing.
LEGS_REST = [
    (3, 16, ["KhK", "KhK", "KhK", "KkK"]),
    (6, 16, ["KHK", "KjK", "KHK", "KkK"]),
    (19, 16, ["KhK", "KhK", "KhK", "KkK"]),
    (22, 16, ["KHK.", "KjHK", ".KkK"]),
]
HORSE_BIT = (30, 10)
SEAT = (6, -9)      # where a rider's art stands on the horse's art: his seat (row 16) on its back (row 7)

# The rider, facing right: the torse his crest stands on, the great helm with its sight and its mantling streaming
# back, the jupon of his arms over the plate, the saddle's cantle, and his leg in plate down the horse's side to
# the stirrup. K outline; a-e steel dark to light; 2-5 his tincture; n N gold; l L the saddle's wood.
RIDER = [
    "...Kn4n4nK....",
    "..KKKcddeK....",
    ".K4KbcddeeK...",
    "K445KbcddeeK..",
    "K43nKbKKKKKKK.",
    "K3nNKbbccddK..",
    ".KnKKKbbccK...",
    "..K.K445G4K...",
    "...K3445G45K..",
    "..KlK344G44K..",
    "..KlL3344G4K..",
    "..KllK33G33K..",
    "...KKKbbccdK..",
    "......KbbcdeK.",
    ".......KKbcdK.",
    ".........KbcK.",
    ".........KbcK.",
    "........KbcdeK",
    "........KnnnnK",
]
RIDER_TOP = 5       # the rows a crest takes over the torse
# The arm laid over a couched lance, and the vamplate before the hand.
ARM = [
    "....KccK....",
    "...KbcdeK...",
    "...KbcdK....",
    "..KbcK......",
    "..KbccdddeKK",
    "...KKKKKKKK.",
]
VAMPLATE = ["K..", "eK.", "ddK", "cdK", "bcK", "abK", "aK.", "K.."]
# The arm raised with the lance held upright, for a knight at rest.
ARM_UP = [
    "....KccK..",
    "...KbcdeK.",
    "...KbcdK..",
    "....KbcK..",
    ".....KbdK.",
    "......KKK.",
]
# The crests over the torse: a lion's head with its mane and its tongue out; a swan's neck; a stag's head.
CRESTS = {
    "lion": ["...o.o.o......", "..oGoGoGo.....", "..oGGGGoYo....", "..oGGGoYKYo...", "..oGGGoYYYK...",
             "...oGGoYrr....", "....ooooo....."],
    "swan": ["....KKK.......", "...KWWWKq.....", "...KWKWqq.....", "....KWK.......", "....KWwK......"],
    "stag": ["..K.K.K.K.....", "..KK.K.KK.....", "...KHHHK......", "...KHKHHq.....", "....KHHK......"],
}
# The shield on a knight's near arm when he shows his left side, painted with his arms: a swan, a lion, a stag's
# head (c the charge on the field 3).
SHIELDS = {
    "swan": ["KKKKKK", "K3cc3K", "Kccc3K", "K3cC3K", "K333CK", ".K33K.", "..KK.."],
    "lion": ["KKKKKK", "K3c33K", "Kccc3K", "K3cc3K", "K3c3cK", ".K33K.", "..KK.."],
    "stag": ["KKKKKK", "Kc3c3K", "K3cc3K", "K3cc3K", "K33c3K", ".K33K.", "..KK.."],
    "chevron": ["KKKKKK", "K3333K", "K3cc3K", "Kc33cK", "K3333K", ".K33K.", "..KK.."],
    "bend": ["KKKKKK", "Kc333K", "K3c33K", "K33c3K", "K333cK", ".K33K.", "..KK.."],
}
# What each knight bears: his tincture, the metal of his charges and his lance's paint.
ARMS = {"lion": ("gules", "or"), "swan": ("azure", "argent"), "stag": ("purpure", "or")}

# The near knight at a third larger again, for a joust or a camp with the room for him: the horse at the charge in
# its caparison, the lion of his arms worked in gold on its flank (c), its ear sleeves, the eye hole and the bit;
# the legs at the charge and at rest; the rider from the torse to the stirrup with his jupon of his arms (G its
# charge); the arm over a couched lance and the arm raised with the lance upright; the vamplate. His crest is the
# large one the helms bear (`CREST_L`). Letters as for the middling knight.
HORSE_L = [
    ".....................................K5K.K5K......",
    "....................................K53KK53K......",
    "...................................K54455445K.....",
    "..................................K5444444445K....",
    ".................................K5444444KKK45K...",
    "................................K54444444KeK445K..",
    "..............................KK5444444444K4443K..",
    ".............................K554444444444444445K.",
    "...........................KK54444444442244444445K",
    "..........................K554444444443KK52444443K",
    "........................KK5444444444443K.KK524442K",
    "......................KK554444444444443K...KK5b2K.",
    "......KKKKKKKKKKKKKKKK55444444444444443K.....KKK..",
    "....KK555555555555555544444444444444442K..........",
    "...K554444444444444444444444444444444445K.........",
    "..K544444244cc44424444444424444442444443K.........",
    ".K54443332cccc333243333333243333324333345K........",
    ".K44333324ccKc332433333332433333243333343K........",
    "K5433333243cc3332433333332433333243333343K........",
    "K43333324333333243333333243333324333333445K.......",
    "KgggggggggggggggggggggggggggggggggggggggggK.......",
    "KGYGGGGGYGGGGGYGGGGGYGGGGGYGGGGGYGGGGGYGGGK.......",
    "K23233233233233233233233233233233233233233K.......",
    ".KK22K22K22K22K22K22K22K22K22K22K22K22K22KK.......",
    "...KK.KK.KK.KK.KK.KK.KK.KK.KK.KK.KK.KK.KK.........",
]
LEGS_L = [
    (1, 24, ["....KHjK", "...KHjK.", "...KHjK.", "..KHjK..", ".KHjK...", ".KHK....", "KHK.....", "Kkk....."]),
    (13, 24, ["KhhK.", "KhhK.", ".KhK.", ".KhK.", ".KhhK", "..KhK", "..KhK", "..Kkk"]),
    (29, 24, ["KhhK..", "KhhK..", "KhhK..", ".KhhK.", "..KhK.", ".KhK..", "KkK..."]),
    (34, 24, ["KHjK....", ".KHjK...", "..KHjK..", "...KHjK.", "....KHjK", ".....KHK", ".....Kkk"]),
]
LEGS_L_REST = [
    (4, 24, ["KHjK", "KHjK", "KHjK", "KHjK", "KHjK", "KHHK", "KkkK"]),
    (9, 24, ["KhhK", "KhhK", "KhhK", "KhhK", "KhhK", "KhhK", "KkkK"]),
    (29, 24, ["KhhK", "KhhK", "KhhK", "KhhK", "KhhK", "KhhK", "KkkK"]),
    (34, 24, ["KHjK.", "KHjK.", ".KHjK", ".KHjK", "KHjK.", "KkkK."]),
]
# The small knight, three quarters of the middling one, for the far side of a narrow joust and for a phone's: his
# horse, its legs at the charge, the rider with his arm over the couched lance and its vamplate, his crest and the
# shield on his near arm.
HORSE_S = [
    "...................K.K....",
    "..................K5K5K...",
    ".................K544445K.",
    "................K544Ke45K.",
    "..............KK54444444K.",
    "..KKKKKKKKKKKK5444442344K.",
    ".K5555555555554444443K53bK",
    "K5444444444444444332K.KKK.",
    "K44333233332333233332K....",
    "K43332333323333233332K....",
    "KgggggggggggggggggggK.....",
    "KGYGGGYGGGGYGGGGYGGGK.....",
    ".KK2KK2KK2KK2KK2KK2KK.....",
]
LEGS_S = [
    (1, 12, ["..KHK", ".KHK.", "KHK..", "Kk..."]),
    (7, 12, ["KhK.", ".KhK", ".KhK", ".Kk."]),
    (14, 12, ["KhK.", "KhK.", ".KhK", "Kk.."]),
    (17, 12, ["KHK..", ".KHK.", "..KHK", "...Kk"]),
]
HORSE_S_BIT = (24, 6)
SEAT_S = (4, -4)
RIDER_S = [
    "..KnNnK...",
    ".KdeeedK..",
    "K4KcdwdK..",
    "43KKKKKKK.",
    "3nKbcddK..",
    ".K.KbcK...",
    "..K44G4K..",
    "..K4GGG4K.",
    "KlK34G43K.",
    "KlK3333K..",
    ".KKbccdK..",
    "....KbcdK.",
    "....KbcdK.",
    "....KnnnK.",
]
ARM_S = ["..KcK....", ".KbcK....", "KbcdeeKK.", ".KKKKKK.."]
VAMPLATE_S = ["K..", "dK.", "cdK", "bcK", "aK.", "K.."]
SHIELD_S = ["KKKKK", "K3c3K", "KcccK", "K3c3K", ".K3K.", "..K.."]
CRESTS_S = {
    "lion": [".o.o..", "oGGoYo", "oGoYKY", "oGoYrK", ".ooo.."],
    "swan": [".KK..", "KWWKq", ".KWK.", "KWWK."],
    "stag": ["K.K.K", ".KHK.", ".KHK.", "..K.."],
}
# The crests the knights ride under, as a herald would have them seen from the far side of the lists: bold, outlined
# and larger than life, each with its x along the rider's art. The near knight's gold lion's head with its mane
# framing its face and its tongue out; the far knight's swan with its neck curved and its gilt beak; and smaller
# ones for the smaller knights. Letters as for the riders, with q for a beak.
RIDER_CRESTS = {
    "L": {"lion": (["...K.K.K.K....", "..KoKoKoKoK...", ".KoGGoGGoGoK..", "KoGGGGGGGGGoK.", "KGGGGGGoYYYYK.",
                    "KoGGGGoYYKYYYK", "KGGGGGoYYYYYYK", "KoGGGGoYYYYKKK", "KGGGGGoYYrrrK.", ".KoGGGGoYYYK..",
                    "..KoGoGoKKK...", "...KKKKKK....."], 3)},
    "M": {"swan": (["..KKK.....", ".KWWWK....", ".KWKWKqK..", "..KWWqqqK.", "...KWK.K..", "...KWK....",
                    "KK.KWWK...", "KWKKWWWK..", "KWWWWWWWK.", ".KwWWWWwK.", "..KKKKKK.."], 2)},
    "S": {"swan": ([".KKK...", "KWWKqK.", ".KWqqK.", ".KWK...", "KKWWK..", "KWWwWK.", ".KKKK.."], 1)},
}

HORSE_L_BIT = (46, 11)
SEAT_L = (12, -6)    # the rider's art's top-left from the horse's: his seat (row 19) on its back (row 13)
RIDER_L = [
    ".....KnNnNnNK.......",
    "....KKKKKKKKKK......",
    "...K4KdeeeeeddK.....",
    "..K44KcdewweddK.....",
    ".K445KcdeeeeddK.....",
    "K4435KcddeeeddK.....",
    "K43nNKbKKKKKKKKKK...",
    "K3nNKKbccdKdKdK.....",
    ".KnN4KbccddddddK....",
    "..KK3KbbccdddddK....",
    "...K.KKKKKKKKKKK....",
    "......KbcddeK.......",
    ".....K44444444K.....",
    "....K4455555544K....",
    "....K445GG55544K....",
    "....K44GGGG4443K....",
    "....K344GG44433K....",
    "..KlK33444443333K...",
    "..KlLK333333332K....",
    "..KllK22222222K.....",
    "...KKKbbcccddK......",
    ".......KbbccddK.....",
    "........KbbcddeK....",
    ".........KbccdeK....",
    "..........KbcdeK....",
    "..........KbcddK....",
    ".........KbccdeeK...",
    ".........KnnnnnnK...",
]
ARM_L = ["..KccK......", ".KbcdeK.....", ".KbcddK.....", ".KbcdK......", "KbcdK.......", "KbccddddeeKK",
         ".KKKKKKKKKK."]
ARM_UP_L = ["..KccK..", ".KbcdeK.", ".KbcddK.", "..KbcdK.", "...KbcdK", "....KdeK", ".....KK."]
VAMPLATE_L = ["K...", "eK..", "edK.", "ddcK", "cdcK", "bccK", "abK.", "aK..", "K..."]


def rider_pal(tinc: str, metal: str, night: bool) -> dict:
    k = -1 if night else 0
    T, M = RAMP[tinc], RAMP[metal]
    return {"K": K, "a": S[1], "b": S[2 + k], "c": S[3 + k], "d": S[4 + k], "e": S[5 + k], "w": S[6],
            "2": T[1], "3": T[2 + k], "4": T[3 + k], "5": T[4 + k], "n": G[3 + k], "N": G[5 + k], "o": G[1],
            "G": G[4 + k], "Y": G[5 + k], "l": WD[2 + k], "L": WD[4 + k], "W": A[6 + k], "w_": A[3],
            "q": G[4 + k], "H": RAMP["horse"][4 + k], "c_": M[5 + k], "C": M[3 + k], "r": RAMP["gules"][4 + k]}


def horse_pal(tinc: str, night: bool, metal="or") -> dict:
    k = -1 if night else 0
    T, Hs, M = RAMP[tinc], RAMP["horse"], RAMP[metal]
    return {"K": K, "2": T[1], "3": T[2 + k], "4": T[3 + k], "5": T[4 + k], "g": G[2 + k], "G": G[4 + k],
            "Y": G[5 + k], "e": A[5], "b": G[5], "h": Hs[2 + k], "H": Hs[3 + k], "j": Hs[5 + k],
            "k": RAMP["sable"][3], "t": Hs[1], "T": Hs[3 + k], "c": M[4 + k] if metal != "argent" else M[5 + k]}


def mounted(p: Pix, x, y, crest: str, night: bool, face=1, legs=None, below=None, arm="couched", shield=False,
            size="M", L="base"):
    """A knight on his horse with the horse's art's top-left at (x, y), facing right (1) or left (-1), middling
    ("M") or a third larger again ("L"): the horse in its caparison of his tincture with its legs (at the charge
    unless `legs` says otherwise), and on it the rider, his crest on his helm. `arm` is the arm over a couched lance
    (drawn by `couched_arm` after the lance), or raised holding it upright ("up"), or none. `shield` hangs his
    painted shield on his near arm (a knight facing left shows his left side). Rows from `below` down are hidden,
    as the tilt hides a far horse. Returns the rider's art's top-left."""
    tinc, metal = ARMS[crest]
    hp, rp = horse_pal(tinc, night, metal), rider_pal(tinc, metal, night)
    big = size == "L"
    horse_art, rider_art, default_legs = {"L": (HORSE_L, RIDER_L, LEGS_L), "S": (HORSE_S, RIDER_S, LEGS_S)}.get(
        size, (HORSE, RIDER, LEGS))
    legs = legs if legs is not None else default_legs
    W, rw = len(horse_art[0]), len(rider_art[0])
    fl = (lambda a: a) if face > 0 else flip
    stamp(p, x, y, fl(horse_art), hp, L, below=below)
    for (lx, ly, rows) in legs:
        gx = x + lx if face > 0 else x + W - lx - len(rows[0])
        stamp(p, gx, y + ly, fl(rows), hp, L, below=below)
    rx, ry, _, _, _ = knight_points(x, y, size, face)
    cp = dict(rp)
    cp["w"] = A[3]
    if crest in RIDER_CRESTS.get(size, {}):
        crest_art, cx = RIDER_CRESTS[size][crest]
        stamp(p, rx + cx if face > 0 else rx + rw - cx - len(crest_art[0]), ry - len(crest_art), fl(crest_art), cp, L)
    elif size in ("L", "S"):
        crest_art, cx = (CREST_L[crest], 4) if big else (CRESTS_S[crest], 2)
        stamp(p, rx + cx if face > 0 else rx + rw - cx - len(crest_art[0]), ry - len(crest_art), fl(crest_art), cp,
              L)
    else:
        stamp(p, rx, ry - len(CRESTS[crest]), fl([r.ljust(rw, ".")[:rw] for r in CRESTS[crest]]), cp, L)
    stamp(p, rx, ry, fl(rider_art), rp, L, below=below)
    if arm == "up":
        up = ARM_UP_L if big else ARM_UP
        ax, ay = (6, 12) if big else (0, 7)
        stamp(p, rx + ax if face > 0 else rx + rw - ax - len(up[0]), ry + ay, fl(up), rp, L)
    if shield and not big:
        sp = {"K": K, "3": rp["3"], "c": rp["c_"], "C": rp["C"]}
        if size == "S":
            stamp(p, rx + 1 if face < 0 else rx + rw - 6, ry + 6, SHIELD_S, sp, L)
        else:
            sx = rx + 4 if face > 0 else rx + rw - 4 - 6
            stamp(p, sx, ry + 7, SHIELDS[crest], sp, L)
    return rx, ry


def knight_points(x, y, size, face):
    """Where a mounted knight's parts fall, from his horse's art's top-left (x, y): his rider's art's top-left, the
    grip (where a couched lance passes under his arm), the heart of the shield on his near arm when he shows his
    left side, and the top of his crest."""
    if size == "L":
        W, (sx, sy), rw = len(HORSE_L[0]), SEAT_L, len(RIDER_L[0])
        rx = x + sx if face > 0 else x + W - sx - rw
        ry = y + sy
        return rx, ry, (rx + 16 if face > 0 else rx + rw - 17, ry + 17), (rx + rw - 8, ry + 15), ry - 7
    if size == "S":
        W, (sx, sy), rw = len(HORSE_S[0]), SEAT_S, len(RIDER_S[0])
        rx = x + sx if face > 0 else x + W - sx - rw
        ry = y + sy
        return rx, ry, (rx + 8 if face > 0 else rx + 1, ry + 9), (rx + 3, ry + 8), ry - 4
    W, (sx, sy), rw = len(HORSE[0]), SEAT, len(RIDER[0])
    rx = x + sx if face > 0 else x + W - sx - rw
    ry = y + sy
    return rx, ry, (rx + 12 if face > 0 else rx + 2, ry + 10), (rx + 6, ry + 10), ry - RIDER_TOP


def couched_arm(p: Pix, rx, ry, crest: str, night: bool, face=1, size="M", L="base"):
    """The rider's arm laid over his couched lance and the vamplate before his hand, drawn after the lance."""
    tinc, metal = ARMS[crest]
    rp = rider_pal(tinc, metal, night)
    if size == "L":
        rw = len(RIDER_L[0])
        if face > 0:
            stamp(p, rx + 6, ry + 12, ARM_L, rp, L)
            stamp(p, rx + 17, ry + 13, VAMPLATE_L, rp, L)
        else:
            stamp(p, rx + rw - 6 - len(ARM_L[0]), ry + 12, flip(ARM_L), rp, L)
            stamp(p, rx + rw - 17 - 4, ry + 13, flip(VAMPLATE_L), rp, L)
        return
    if size == "S":
        rw = len(RIDER_S[0])
        if face > 0:
            stamp(p, rx + 2, ry + 8, ARM_S, rp, L)
            stamp(p, rx + 9, ry + 7, VAMPLATE_S, rp, L)
        else:
            stamp(p, rx + rw - 2 - len(ARM_S[0]), ry + 8, flip(ARM_S), rp, L)
            stamp(p, rx + rw - 9 - 3, ry + 7, flip(VAMPLATE_S), rp, L)
        return
    rw = len(RIDER[0])
    if face > 0:
        stamp(p, rx, ry + 7, ARM, rp, L)
        stamp(p, rx + 12, ry + 6, VAMPLATE, rp, L)
    else:
        stamp(p, rx + rw - len(ARM[0]), ry + 7, flip(ARM), rp, L)
        stamp(p, rx + rw - 12 - 3, ry + 6, flip(VAMPLATE), rp, L)


def lance_bands(tinc: str, metal: str, night: bool) -> tuple:
    """A lance's paint, (lit, shade) for its bands of metal and for its bands of tincture."""
    k = -1 if night else 0
    T, M = RAMP[tinc], RAMP[metal]
    return ((M[6 + k], M[2 + k]) if metal == "argent" else (M[5 + k], M[2 + k])), (T[4 + k], T[1 + k])


def lance(p: Pix, x0, y0, x1, y1, tinc: str, night: bool, stop=None, coronel=True, metal="or", start=0, L="base"):
    """A jousting lance from its butt (x0, y0) to its head (x1, y1), two rows thick, painted in a spiral of its
    knight's tincture and a metal, the coronel's blunt crown of steel on its head; or broken off `stop` pixels along,
    where it has shattered. `start` leaves out the length nearest the butt, hidden behind the one who holds it."""
    k = -1 if night else 0
    bands = lance_bands(tinc, metal, night)
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    last = n if stop is None else stop
    for i in range(start, last + 1):
        xx, yy = round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)
        hi, lo = bands[((i + 1) // 2) % 2 == 0]
        p.px(xx, yy, hi, L)
        p.px(xx, yy + 1, lo, L)
    if stop is None and coronel:
        d = 1 if x1 > x0 else -1
        p.px(x1 + d, y1, S[5 + k], L)
        p.px(x1 + d, y1 + 1, S[3 + k], L)
        p.px(x1 + 2 * d, y1 - 1, S[4 + k], L)
        p.px(x1 + 2 * d, y1 + 2, S[2 + k], L)
    elif stop is not None:
        xx, yy = round(x0 + (x1 - x0) * last / n), round(y0 + (y1 - y0) * last / n)
        d = 1 if x1 > x0 else -1
        p.px(xx + d, yy - 1, WD[5 + k], L)
        p.px(xx + d, yy + 2, WD[4 + k], L)
        p.px(xx + 2 * d, yy, WD[6 + k], L)


# --------------------------------------------------------------------------- the lists
def tilt(p: Pix, x0, x1, top, foot, night: bool, uid="tl", L="base"):
    """The tilt the knights run along: an oak rail on posts capped in gilt, and hung from it a cloth of the host's
    white, its folds catching the light, with a band of his green along its foot and a gold fringe; from row
    `top` to row `foot`. The cloth and its foot are pattern tiles, so the tilt costs little however long it runs."""
    k = -1 if night else 0
    h = foot - top
    for j, c in enumerate((K, WD[5 + k], WD[3 + k], WD[1 + k])):
        p.hline(x0, x1, top + j, c, L)
    cloth: dict = {}
    hem: dict = {}
    for x in range(6):
        cloth.setdefault(A[(6, 5, 5, 5, 4, 3)[x] + k - (1 if night else 0)], {}).setdefault(0, []).append(x)
        hem.setdefault(V[(4, 4, 3, 3, 3, 2)[x] + k], {}).setdefault(0, []).append(x)
        hem.setdefault(V[2 + k] if x else V[1 + k], {}).setdefault(1, []).append(x)
        hem.setdefault(G[4 + k] if x % 2 else K, {}).setdefault(2, []).append(x)
    p.defs.append(f'<pattern id="{uid}" x="{x0}" width="6" height="1" patternUnits="userSpaceOnUse">{paths(cloth)}'
                  f'</pattern><pattern id="{uid}h" x="{x0}" y="{foot - 3}" width="6" height="3" '
                  f'patternUnits="userSpaceOnUse">{paths(hem)}</pattern>')
    p.shapes[L].append(f'<rect x="{x0}" y="{top + 4}" width="{x1 - x0}" height="{h - 7}" fill="url(#{uid})"/>'
                       f'<rect x="{x0}" y="{foot - 3}" width="{x1 - x0}" height="3" fill="url(#{uid}h)"/>')
    keep(p, {(x, y) for x in range(x0, x1) for y in range(top, foot)})
    for px in range(x0 + 4, x1 - 2, 18):
        p.px(px, top - 1, WD[4 + k], L)
        p.px(px + 1, top - 1, WD[2 + k], L)
        p.px(px, top - 2, G[6 + k], L)
        p.px(px + 1, top - 2, G[3 + k], L)


def ground(p: Pix, x0, x1, top, g, night: bool, uid="gd", L="base"):
    """The lists' ground from row `top` to row g: turf, its upper edge lit, and the sand of the tiltyard where the
    horses have run, in a pattern tile."""
    k = -1 if night else 0
    Tf = RAMP["turf"]
    h = g - top + 1
    cols: dict = {}
    for y in range(h):
        for x in range(8):
            if y == 0:
                c = Tf[5 + k] if x % 4 else Tf[4 + k]
            elif y == 1:
                c = Tf[4 + k] if (x + y) % 3 else Tf[3 + k]
            else:
                c = CV[4 + k] if (x * 3 + y * 5) % 7 else CV[3 + k]
            cols.setdefault(c, {}).setdefault(y, []).append(x)
    p.defs.append(f'<pattern id="{uid}" x="{x0}" y="{top}" width="8" height="{h}" patternUnits="userSpaceOnUse">'
                  f'{paths(cols)}</pattern>')
    p.shapes[L].append(f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{h}" fill="url(#{uid})"/>')
    keep(p, {(x, y) for x in range(x0, x1) for y in range(top, top + h)})


# --------------------------------------------------------------------------- torches and their light
CRESSET = ["I.I.I", "IcCcI", ".IiI.", "..I.."]


def lamp(p: Pix, cx, cy, r, phase, own=()):
    """Register a flame at (cx, cy): once everything is drawn, `firelight` lays its warm light on what stands
    within `r` of it, flickering with the flame. `own` are the flame's own pixels."""
    p.lamps.append((cx, cy, r, phase, set(own)))


def flick(p: Pix, phase: int, back: bool = False) -> str:
    """The flickering layer a flame of `phase` burns on. A drawing made lighter to fit its budget lets every flame
    keep one time, so it carries one flicker and not three: each still burns and flickers."""
    return p.flicker(0 if p.lite else phase, back=back)


def halo(p: Pix, cx, cy, rx, ry, col, alphas, L="haze", shape=None):
    """A stepped glow (see `Pix.halo`). A drawing made lighter keeps its light but leaves out the faint outer ring,
    the glow drawn to its inner rings' reach."""
    if p.lite and len(alphas) > 1:
        f = (len(alphas) - 1) / len(alphas)
        rx, ry, alphas = rx * f, ry * f, alphas[1:]
    p.halo(cx, cy, rx, ry, col, alphas, L=L, shape=shape)


PLATE = set(RAMP["steel"][2:])     # the plate a torch's light glints on


def firelight(p: Pix):
    """The finishing pass by night: each flame's light on the wood, the canvas, the steel and the silks nearest it;
    and where plate armour turns its edge to a torch that stands near, a glint of the fire along that edge out to the
    torch's reach, flickering with the flame. The words take none. A drawing made lighter keeps the glints and the
    light nearest each flame, and leaves out the faint outer ring of its wash."""
    base, cloth = p.layers["base"], getattr(p, "cloth", {})
    for (cx, cy, r, phase, own) in p.lamps:
        L = flick(p, phase)
        for y in range(math.floor(cy - r), math.ceil(cy + r) + 1):
            for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
                c = base.get((x, y)) or cloth.get((x, y))
                if c is None or (x, y) in own or c not in LIT:
                    continue
                d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.1) / r
                if d >= 1:
                    continue
                if c in PLATE and r >= 20:
                    sx, sy = (cx > x + 0.5) - (cx < x + 0.5), (cy > y + 0.5) - (cy < y + 0.5)
                    if any(base.get(q) not in PLATE for q in ((x + sx, y), (x, y + sy)) if q != (x, y)):
                        p.px(x, y, FL[4] if d < 0.5 else FL[3], L)
                        continue
                if d < (0.45 if p.lite else 0.7):
                    p.apx(x, y, FL[4], 0.22, L)


def flame(p: Pix, x, y, phase=0, big=False, reach=14, L=None):
    """A flame whose foot is (x, y): tongues that leap and flicker, sparks over it, its glow in the air round it
    and its light on what stands near (see `firelight`). Night only."""
    Lf = L or flick(p, phase)
    cells = [(0, 0, 6), (-1, 0, 5), (1, 0, 5), (-2, 0, 3), (2, 0, 3), (0, -1, 6), (-1, -1, 4), (1, -1, 5),
             (0, -2, 5), (-1, -2, 3), (1, -3, 4), (0, -3, 4), (0, -4, 3), (1, -5, 2)]
    if big:
        cells += [(-3, 0, 2), (3, 0, 2), (-2, -1, 3), (2, -1, 3), (1, -2, 4), (-1, -4, 2), (2, -3, 2), (0, -5, 3),
                  (0, -6, 2)]
    for (dx, dy, t) in cells:
        p.px(x + dx, y + dy, FL[t], Lf)
    for i, (dx, dy) in enumerate(((-2, -7), (2, -8), (0, -10)) if big else ((-1, -7), (1, -8))):
        p.px(x + dx, y + dy, FL[5], p.twinkle(i + phase))
    r = 10 if big else 8
    halo(p, x + 0.5, y - 1.5, r, r * 0.9, FL[2], GLOW, L=flick(p, phase, back=True))
    lamp(p, x + 0.5, y - 1, reach, phase, {(x + dx, y + dy) for dx, dy, _ in cells})


def torch(p: Pix, x, foot, night: bool, h=18, phase=0, big=False, reach=14, L="base"):
    """A torch on a pole, its foot on row `foot`: an iron cresset on an oak pole, by day heaped with its tow, black
    with pitch and cold, and by night burning (see `flame`)."""
    k = -1 if night else 0
    for y in range(foot - h + 4, foot):
        p.px(x + 2, y, WD[4 + k], L)
        p.px(x + 3, y, WD[2 + k], L)
    top = foot - h
    stamp(p, x, top, CRESSET, {"I": S[2 + k], "i": S[4 + k], "c": DU[2] if night else DU[1], "C": FL[1] if night
                               else DU[3]}, L)
    if night:
        flame(p, x + 2, top, phase=phase, big=big, reach=reach)
    else:
        stamp(p, x + 1, top - 2, [".k.", "kKk"], {"k": DU[2], "K": DU[0]}, L)


# --------------------------------------------------------------------------- the burst
BURST_TIMES = ((0.42, 0.5), (0.5, 0.64), (0.64, 0.8), (0.8, 1.0))
STRIKE = 4.0        # seconds a strike takes, round and round: a figure's loop, within the hand's four to eight
TILT = 4.0          # seconds a run at the quintain takes, the sack swinging round after the blow
WAVE = 4.0          # seconds a lady takes to wave her favour to the lists and back
CORONEL = ["K.K.K", "eKeKe", "KdddK", ".KdK."]      # the broken coronel: its crown of blunt points on its socket
# The slivers the shaft flies into: each one's angle (an arc over the strike), how fast it flies against the rest,
# and whether it is raw wood from the break or a painted piece of the shaft.
SLIVERS = ((-176, 0.8, 1), (-160, 1.05, 0), (-141, 0.9, 0), (-122, 1.15, 1), (-104, 0.95, 0), (-86, 1.1, 0),
           (-68, 0.9, 1), (-50, 1.15, 0), (-32, 0.95, 0), (-14, 1.05, 1), (-2, 0.8, 0))
SPARKS = ((-4, -7), (6, -5), (-8, -1), (5, 4), (1, -10), (-6, 5), (9, -1), (-2, 7))


def _turned(art: list, q: int) -> list:
    """Pixel art turned a quarter round clockwise `q` times."""
    for _ in range(q % 4):
        art = ["".join(art[len(art) - 1 - j][i] for j in range(len(art))) for i in range(len(art[0]))]
    return art


def burst(p: Pix, cx, cy, tinc: str, night: bool, motion: bool, name="bs", away=1, spare=frozenset()):
    """The burst where a lance breaks on a shield, centred on (cx, cy). First the flash of the strike, a star of
    white and gold with long rays; then the shaft's slivers, raw wood and painted, flying out in an arc over it and
    falling as they go, and its broken coronel spinning away forward (`away` the way it flies) and dropping. In a
    moving header the strike comes round and round, frame by frame; a still drawing keeps the flash with the
    slivers bursting round it and the coronel in the air. By night the flash is fire and throws sparks. The flash
    leaves the cells in `spare` (the struck knight) to him beyond its heart, its rays breaking out round him. A drawing
    made lighter shows the strike in two frames, the flash and then the slivers in the air, and by night leaves out
    the glow the flash throws round it."""
    k = -1 if night else 0
    T = RAMP[tinc]
    core, inner, mid, outer = (C["white"], FL[6], FL[5], FL[4]) if night else (C["white"], G[6], FL[4], FL[3])

    def flash(L, r):
        put = p.px

        def px(x, y, c, L):
            if (x, y) not in spare or abs(x - cx) + abs(y - cy) <= 2:
                put(x, y, c, L)
        for d in range(2, r + 1):
            c = inner if d <= r // 3 + 1 else mid if d <= (2 * r) // 3 else outer
            for ux, uy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                px(cx + ux * d, cy + uy * d, c, L)
        for d in range(1, (2 * r) // 3):
            c = inner if d <= r // 3 else mid if d < (2 * r) // 3 - 1 else outer
            for ux, uy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
                px(cx + ux * d, cy + uy * d, c, L)
        for j in range(1, r // 3 + 1):
            for ux, uy in ((2, 1), (-2, 1), (2, -1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2)):
                px(cx + ux * j, cy + uy * j, mid if j < r // 3 else outer, L)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if abs(dx) + abs(dy) < 2 or r > 6:
                    px(cx + dx, cy + dy, core, L)

    def slivers(L, r, drop, every=1, long=3):
        for i, (a, v, painted) in enumerate(SLIVERS[::every]):
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            x, y = cx + ca * r * v, cy + sa * r * v + drop * (0.6 + 0.4 * v)
            head, tail = (T[4 + k], T[2 + k]) if painted else (WD[6 + k], WD[4 + k])
            p.px(round(x), round(y), head, L)
            for j in range(1, long):
                p.px(round(x - ca * j), round(y - sa * j + drop * 0.15 * j), tail if j == long - 1 else head, L)

    def coronel(L, q, x, y):
        art = _turned(CORONEL, q)
        stamp(p, x - len(art[0]) // 2, y - len(art) // 2, art, {"K": K, "e": S[5 + k], "d": S[3 + k]}, L)

    def sparks(L, f):
        for i, (dx, dy) in enumerate(SPARKS):
            p.px(cx + dx * (f + 2) // 2, cy + dy * (f + 2) // 2, (FL[6], G[6], FL[5])[i % 3], L)
    # each frame: the flash's reach, how far the slivers have flown and fallen, and where the coronel is
    steps = ((0, 9, 4, 0, None), (1, 5, 8, 1, (5, -5, 1)), (2, 0, 13, 4, (10, -9, 2)), (3, 0, 17, 9, (14, -7, 3)))
    times = BURST_TIMES
    if p.lite:
        steps, times = (steps[0], steps[2]), (BURST_TIMES[0], (BURST_TIMES[1][0], BURST_TIMES[3][1]))
    if motion:
        for (f, r, fly, drop, cor), t in zip(steps, times):
            L = p.seq(f"{name}{f}", *t, STRIKE, keep=False, z=2)
            if r:
                flash(L, r)
            if f:
                slivers(L, fly, drop, every=1 if f < 3 else 2, long=3 if f < 3 else 2)
            if cor:
                coronel(L, cor[2], cx + cor[0] * away, cy + cor[1])
            if night and f < 2:
                sparks(L, f)
    else:
        L = p.layer(f"{name}1", z=2)
        flash(L, 7)
        slivers(L, 10, 1)
        coronel(L, 1, cx + 8 * away, cy - 8)
        if night:
            sparks(L, 1)
    if night and not p.lite:
        halo(p, cx + 0.5, cy + 0.5, 11, 10, FL[3], GLOW,
               L=p.seq(f"{name}g", 0.42, 0.64, STRIKE, z=-5) if motion else "haze")


# --------------------------------------------------------------------------- the joust
JOUST_W = 54        # the middling joust's width
SPREAD_W = 104      # the slot from which the large joust spreads out along the tilt
LAYOUTS = {         # each staging: near knight's size, far knight's size, the near horse's art's top over the ground,
    #                 the far one's x from the slot's left and its top over the ground, the tilt's top, the rows the
    #                 staging rises (its far crest and the burst's slivers) and the narrowest slot it stands in
    "spread": ("L", "M", 31, 60, 42, 31, 60, SPREAD_W),
    "rising": ("L", "M", 31, 36, 48, 34, 70, 54),
    "diagonal": ("L", "S", 31, 35, 42, 30, 56, 52),
    "middling": ("M", "M", 21, 18, 28, 15, 42, JOUST_W),
    "compact": ("S", "S", 16, 20, 19, 13, 28, 48),
}


def joust(p: Pix, x0, g, night: bool, motion: bool = True, near="lion", far="swan", layout="middling", width=None,
          reach=None, uid="tl"):
    """The joust at the moment of impact on the ground at row g from x0: the far knight beyond the tilt, higher and
    smaller, riding left with his shield toward us, his horse hidden by the tilt below its flank; the tilt; the near
    knight riding right before it. Both lances are couched, painted in their knights' tinctures, and meet over the
    tilt: the far knight's crossing it from over his horse's neck to the near knight's shield on his far side, where
    a flash peeps round him; the near knight's breaking on the far knight's shield in a burst of splinters. The
    `layout` sets its size (see `LAYOUTS`): spread along the tilt, the near knight a third larger and the far one
    middling, a lance's length apart; rising, the near knight large and the far one middling, higher beyond a taller
    tilt; diagonal, the near knight large and the far one small, high over his horse's head; in both of these the
    far knight rides as far ahead as `reach` lets him; middling, both middling; or compact, both small, for a phone.
    The tilt runs `width` from x0. Returns the span of the rule it covers."""
    nsize, fsize, ntop, fdx, ftop, ttop, _, least = LAYOUTS[layout]
    width = max(width or least, least)
    x1 = x0 + width
    (ntinc, nmetal), (ftinc, fmetal) = ARMS[near], ARMS[far]
    nx, ny = x0, g - ntop
    fx, fy = x0 + (reach if reach is not None and layout in ("rising", "diagonal") else fdx), g - ftop
    nrx, nry, grip, _, _ = knight_points(nx, ny, nsize, 1)
    frx, fry, fgrip, shield, _ = knight_points(fx, fy, fsize, -1)
    top = g - ttop
    mounted(p, fx, fy, far, night, face=-1, below=top + 1, arm=None, shield=True, size=fsize)
    foot = g - (10 if nsize == "L" else 3)
    tilt(p, x0, x1, top, foot, night, uid=uid)
    ground(p, x0, x1, foot, g, night, uid=uid + "g")
    aim = {"L": (nrx + 14, nry + 10), "M": (nrx + 9, nry + 7), "S": (nrx + 6, nry + 7)}[nsize]
    lance(p, fgrip[0] + 9, fgrip[1] - 3, aim[0], aim[1], ftinc, night, coronel=False, metal=fmetal, start=7)
    q = Pix(p.w, p.h)
    mounted(q, nx, ny, near, night, face=1, arm=None, size=nsize)
    hidden = set(q.layers["base"])
    mounted(p, nx, ny, near, night, face=1, arm=None, size=nsize)
    bit = {"L": HORSE_L_BIT, "M": HORSE_BIT, "S": HORSE_S_BIT}[nsize]
    _rein(p, nx + bit[0], ny + bit[1], grip[0] - 4, grip[1] + 1, night)
    hit = (shield[0] - 3, shield[1])
    back = {"L": 8, "M": 12, "S": 8}[nsize]
    d = max(abs(hit[0] - grip[0]), abs(hit[1] - grip[1]), 1)
    butt = (round(grip[0] - (hit[0] - grip[0]) * back / d), round(grip[1] - (hit[1] - grip[1]) * back / d))
    n = max(abs(hit[0] - butt[0]), abs(hit[1] - butt[1]))
    lance(p, butt[0], butt[1], hit[0], hit[1], ntinc, night, stop=n - 4, metal=nmetal)
    if motion:
        Lw = p.seq("lw", 0, 0.42, STRIKE, z=1)
        bands = lance_bands(ntinc, nmetal, night)
        for i in range(n - 4, n + 1):
            xx, yy = round(butt[0] + (hit[0] - butt[0]) * i / n), round(butt[1] + (hit[1] - butt[1]) * i / n)
            hi, lo = bands[((i + 1) // 2) % 2 == 0]
            p.px(xx, yy, hi, Lw)
            p.px(xx, yy + 1, lo, Lw)
    couched_arm(p, nrx, nry, near, night, size=nsize)
    q = Pix(p.w, p.h)
    mounted(q, fx, fy, far, night, face=-1, below=top + 1, arm=None, shield=True, size=fsize)
    burst(p, hit[0], hit[1], ntinc, night, motion, spare=frozenset(q.layers["base"]))
    # where the far knight's lance strikes the near knight's shield, on his far side: a flash peeping round him
    hot, warm = (FL[6], FL[5]) if night else (FL[4], FL[3])
    for f, r in (((0, 4),) if motion else ((1, 3),)):
        L = p.seq(f"bs{f}", *BURST_TIMES[f], STRIKE, keep=False, z=2) if motion else p.layer(f"bs{f}", z=2)
        star = [(0, 0, C["white"])] + [(ux * j, uy * j, hot if j < r else warm) for j in range(1, r + 1)
                                        for ux, uy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        star += [(ux * j, uy * j, warm) for j in range(1, r // 2 + 1)
                 for ux, uy in ((1, 1), (-1, 1), (1, -1), (-1, -1))]
        for dx, dy, c in star:
            if (aim[0] + dx, aim[1] + dy) not in hidden:
                p.px(aim[0] + dx, aim[1] + dy, c, L)
    return (x0 - 1, x1 + 1)


def joust_cells(p: Pix, layout, x0, g, width=None, reach=None) -> set:
    """Every cell a staging of the joust would cover on a sheet like `p`, by day or by night with its sparks, drawn
    on a scratch canvas: what a scene tests against the words before it draws the joust."""
    cells = set()
    for night in (False, True):
        q = Pix(p.w, p.h)
        joust(q, x0, g, night, motion=True, layout=layout, width=width, reach=reach)
        cells |= set(getattr(q, "filled", ()))
        for layer in q.layers.values():
            cells |= set(layer)
    return cells


def _rein(p: Pix, x0, y0, x1, y1, night: bool):
    """The rein from the bit back to the rider's bridle hand, under his arm."""
    c = WD[1] if not night else WD[0]
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(1, n):
        p.px(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), c)


# --------------------------------------------------------------------------- pavilions
def _wall_tile(p: Pix, pid: str, w: int, colour_at, x0=0) -> str:
    """A pattern one row tall across a wall `w` wide from x0, each column's colour from `colour_at(i)`: a wall
    striped and lit across its width costs one row of runs however tall it stands."""
    cols: dict = {}
    for i in range(w):
        cols.setdefault(colour_at(i), {}).setdefault(0, []).append(i)
    p.defs.append(f'<pattern id="{pid}" x="{x0}" width="{w}" height="1" patternUnits="userSpaceOnUse">{paths(cols)}'
                  f'</pattern>')
    return pid


def pavilion(p: Pix, cx, foot, night: bool, tinc="gules", w=21, h=26, door=True, banner=True, motion=True,
             phase=0, seed=0, far=False, great=False, state="open", L="base"):
    """A round pavilion standing on row `foot`, `w` wide about cx and `h` tall to the top of its roof: its wall of
    canvas striped in its knight's tincture and white, lit on its left and shaded on its right; its roof a cone
    striped the same, its foot hung with a dagged valance; its door looped back on a dark inside; and on its pole a
    gilt knop and a pennon of the tincture streaming in the wind. By night its canvas glows from within, its door a
    pool of warm light. A `far` pavilion stands back behind the lists in paler tints and a softer outline by day,
    and by night glows lower, so what stands before it reads first. A knight's `great` pavilion has its door
    drawn wide, its flaps tied back with gold, and by night the light within pours out of it onto the ground. Its
    `state` may instead be "closed", its door laced shut down its seam, or "arming", its door looped wide on a
    knight being armed within, his squire setting his great helm on his head (see `ARMING`)."""
    k = -1 if night else 0
    T = RAMP[tinc]
    wall = round(h * 0.48)
    roof = h - wall
    x0 = cx - w // 2
    eave = foot - wall
    if far:
        lit = (T[3], T[2], T[1], FL[3], FL[2], FL[1]) if night else (T[6], T[5], T[4], A[6], A[6], A[5])
        rim = T[0] if night else T[3]
    else:
        lit = (T[6], T[5], T[4], FL[5], FL[5], FL[4]) if night else (T[4], T[3], T[2], A[6], A[5], A[4])
        rim = K

    def stripe(coloured, t):
        return lit[(0 if coloured else 3) + 1 - t]

    def wall_colour(i):
        u = (i + 0.5) / w
        t = 1 if u < 0.2 else 0 if u < 0.75 else -1
        return stripe((i // 3) % 2 == 0, t)
    pid = _wall_tile(p, f"pw{seed}", w, wall_colour, x0)
    p.shapes[L].append(f'<rect x="{x0}" y="{eave}" width="{w}" height="{wall}" fill="url(#{pid})"/>')
    keep(p, {(x, y) for x in range(x0, x0 + w) for y in range(eave, foot)})
    p.vline(x0 - 1, eave, foot, rim, L)
    p.vline(x0 + w, eave, foot, rim, L)
    p.hline(x0, x0 + w, foot - 1, T[1] if not night else T[2], L)
    if door and state == "closed":
        dh = min(wall - 2, 10)
        for y in range(foot - dh, foot):
            p.px(cx, y, stripe(False, -1), L)
            p.px(cx - 1, y, stripe(True, 1) if (y - foot) % 2 else stripe(False, 1), L)
        for y in (foot - dh + 2, foot - dh // 2 - 1):
            p.px(cx - 1, y, G[5 + k], L)
            p.px(cx, y, G[3 + k], L)
        for j in range(3):
            p.px(cx - 1 - j, foot - 1 - j, stripe(True, -1), L)
    elif door and state == "arming":
        dh = min(wall - 2, len(ARMING) + 2)
        wide = len(ARMING[0]) // 2 + 1
        for y in range(foot - dh, foot):
            j = y - (foot - dh)
            half = min(wide, wide - 3 + j // 2)
            for xx in range(cx - half, cx + half):
                t = abs(xx + 0.5 - cx) / wide + (dh - j) / dh * 0.5
                p.px(xx, y, ((FL[6] if t < 0.45 else FL[5] if t < 0.8 else FL[4]) if night
                             else (DU[1] if t < 0.7 else DU[2])), L)
            for side in (-1, 1):
                edge = cx - half - 1 if side < 0 else cx + half
                p.px(edge, y, stripe(False, 1 if side < 0 else -1), L)
                if j > dh // 2:
                    p.px(edge + side, y, stripe(True, 0), L)
        for side in (-1, 1):
            p.px(cx + side * (wide + 2) - (1 if side > 0 else 0), foot - dh // 2, G[5 + k], L)
        stamp(p, cx - len(ARMING[0]) // 2, foot - len(ARMING), ARMING, arming_pal(night), L)
        if night:
            hot = flick(p, phase)
            for j in range(2):
                for xx in range(cx - wide + 1 - j * 2, cx + wide - 1 + j * 2):
                    p.apx(xx, foot + j, FL[4], 0.36 - 0.12 * j, hot)
            lamp(p, cx + 0.5, foot - 6, 18, phase,
                 {(xx, yy) for xx in range(cx - wide - 1, cx + wide + 1) for yy in range(foot - dh, foot)})
            halo(p, cx + 0.5, foot - 8, 15, 12, FL[2], GLOW, L=flick(p, phase, back=True))
    elif door and great:
        dh = min(wall - 2, 14)
        for y in range(foot - dh, foot):
            j = y - (foot - dh)
            half = min(5, 2 + j // 2)
            for xx in range(cx - half, cx + half):
                t = abs(xx + 0.5 - cx) / 5 + (dh - j) / dh * 0.6
                p.px(xx, y, ((FL[6] if t < 0.45 else FL[5] if t < 0.8 else FL[4]) if night
                             else (DU[1] if t < 0.7 else DU[2])), L)
            for side in (-1, 1):
                edge = cx - half - 1 if side < 0 else cx + half
                p.px(edge, y, stripe(False, 1 if side < 0 else -1), L)
                if j > dh // 2:
                    p.px(edge + side, y, stripe(True, 0), L)
        for side in (-1, 1):
            p.px(cx + side * 7 - (1 if side > 0 else 0), foot - dh // 2, G[5 + k], L)
        if night:
            hot = flick(p, phase)
            for j in range(3):
                for xx in range(cx - 5 - j * 2, cx + 5 + j * 2):
                    p.apx(xx, foot + j, FL[4], 0.42 - 0.12 * j, hot)
            lamp(p, cx + 0.5, foot - 3, 16, phase,
                 {(xx, yy) for xx in range(cx - 6, cx + 6) for yy in range(foot - dh, foot)})
            halo(p, cx + 0.5, foot - 5, 13, 10, FL[2], GLOW, L=flick(p, phase, back=True))
    elif door:
        dx = cx - 3
        dh = min(wall - 2, 9)
        inside = (CV[2], CV[3]) if far and not night else (DU[2], DU[3])
        for y in range(foot - dh, foot):
            for xx in range(dx + 1, dx + 5):
                if y > foot - dh + (1 if xx - dx in (1, 4) else 0):
                    p.px(xx, y, (FL[5] if (xx - dx) in (2, 3) else FL[4]) if night else inside[(xx - dx) % 2], L)
            p.px(dx, y, stripe(False, 1) if y < foot - 2 else stripe(False, -1), L)
            p.px(dx + 5, y, stripe(False, -1), L)
        if night:
            lamp(p, cx + 0.5, foot - 3, 12, phase,
                 {(xx, yy) for xx in range(dx, dx + 6) for yy in range(foot - dh, foot)})
            halo(p, cx + 0.5, foot - 4, 9, 7, FL[2], GLOW, L=flick(p, phase, back=True))
    apex = eave - roof
    for y in range(apex + 1, eave):
        f = (y - apex) / roof
        half = max(1, round((w / 2 + 1) * f))
        for x in range(cx - half, cx + half + 1):
            u = (x - cx) / max(1, half)
            coloured = (math.floor((u * 3.5) + 10)) % 2 == 0
            t = 1 if x == cx - half else -1 if x == cx + half else 0
            p.px(x, y, stripe(coloured, t), L)
        p.px(cx - half - 1, y, rim, L)
        p.px(cx + half + 1, y, rim, L)
    vid = f"pv{seed}"
    band = (T[3], T[4], G[4]) if far and not night else (K, T[2 + k], G[3 + k])
    p.defs.append(f'<pattern id="{vid}" x="{x0 - 1}" y="{eave}" width="6" height="3" patternUnits="userSpaceOnUse">'
                  f'<path stroke="{band[0]}" d="M0 .5h6"/><path stroke="{band[1]}" d="M0 1.5h3m0 1h2"/>'
                  f'<path stroke="{band[2]}" d="M3 1.5h3m-3 1h2"/></pattern>')
    p.shapes[L].append(f'<rect x="{x0 - 1}" y="{eave}" width="{w + 2}" height="3" fill="url(#{vid})"/>')
    keep(p, {(x, y) for x in range(x0 - 1, x0 + w + 1) for y in range(eave, eave + 3)})
    for y in range(apex - 9, apex + 1):
        p.px(cx, y, WD[4 + k], L)
    p.px(cx, apex - 10, G[6 + k], L)
    p.px(cx - 1, apex - 9, G[3 + k], L)
    p.px(cx + 1, apex - 9, G[3 + k], L)
    if banner:
        pennon(p, cx + 1, apex - 8, tinc, night, motion=motion, phase=phase, seed=seed)
    prop(p, x0 - 1, apex - 11, max(x0 + w + 1, cx + 12), foot)
    return (x0 - 1, x0 + w + 1)


# A knight being armed in a pavilion's door, 19 wide and 20 tall: bare-headed in his plate (S s d), turned to his
# squire, a gold belt (y) and his tassets' red lining (r) at his waist; his squire in the host's green (q Q), belted in
# gold (o), reaching up to set the great helm (S s d, its T-shaped sight K) on his head. f the knight's face and hands
# and g the squire's (each figure's own skin), h H their hair, k their shoes; the doorway's inside is left as it is
# drawn.
ARMING = [
    "..KKKKKKK..........",
    ".KSSSSSsdK.........",
    ".KKKKKKKdKf........",
    ".KSSSKSsdKfK..KKK..",
    ".KsSSKssdKqK.KhHhK.",
    "..KKKKKKKqQK.KhhhK.",
    "..KhhhhhKqQK.KhKfK.",
    "..KhffKfKqQK.KfffK.",
    "..KhffffK.qQKKffK..",
    "...KfffK.KqQqKKqK..",
    ".KKdSSSdKKqQqQqqqK.",
    "KSSSSSSsdKKqqQqKqK.",
    "KSKSSSssKdKqqQqKfK.",
    "KSKSSssdKdKqqqqqK..",
    "KfKyyyyyKfKooooooK.",
    ".KKrSSsrKK.KqqqQK..",
    "..KSdKKSdK.KQKKQK..",
    "..KSdK.SdK.KQK.KQK.",
    "..KSdK.SdK.KQK.KQK.",
    ".KKKdK.KKdKKkK.KkK.",
]
ARMING = [row[:10] + row[10:].replace("f", "g") for row in ARMING]      # the squire's own hands and face


def arming_pal(night: bool) -> dict:
    """The knight being armed and his squire: the knight on the lightest of the hand's skins, his squire on the
    middle one."""
    k = -1 if night else 0
    return {"K": K, "S": S[6] if night else S[6 + k], "s": S[4 + k], "d": S[2 + k], "y": G[5 + k],
            "r": RAMP["gules"][3 + k], "q": V[4 + k], "Q": V[2 + k], "o": G[4 + k], "f": skin(0, night)["f"],
            "g": skin(1, night)["f"], "h": WD[1 + k], "H": WD[3 + k], "k": WD[1 + k]}


# The tree of shields' crown, as clumps of leaves (their centres from the trunk and the crown's top, and their radii).
CLUMPS = ((0, 7, 8), (-9, 11, 8.5), (8, 10, 8.5), (-15, 17, 6), (15, 16, 6), (-5, 18, 8), (6, 18, 7.5))
TREE_W = 41         # the tree of shields' width, its crown's leaves and its shields


def shield_tree(p: Pix, cx, foot, night: bool, motion: bool = True, h=50, seed=0, L="base"):
    """The tree of shields, `h` tall on the ground at row `foot` about cx: an oak in leaf, lit on its left (by night
    dark against the canvas, but for what light falls on it), hung under its crown with the shields of the knights
    who hold the lists, where a challenger came to strike the shield of the knight he would meet; the one last
    struck hangs askew on its strap and, in a moving header, swings, a glint of gold at the blow. A drawing made
    lighter shades its leaves two pixels square. Returns the span it covers."""
    k = -1 if night else 0
    Tf = RAMP["turf"]
    top = foot - h
    rnd = random.Random(seed)
    trunk = top + 19
    for y in range(trunk, foot):
        for dx, c in ((-1, WD[4 + k]), (0, WD[3 + k]), (1, WD[2 + k]), (2, WD[1 + k])):
            p.px(cx + dx, y, c, L)
    for dx, c in ((-3, WD[3 + k]), (-2, WD[4 + k]), (3, WD[2 + k]), (4, WD[1 + k])):
        p.px(cx + dx, foot - 1, c, L)
    p.px(cx - 2, foot - 2, WD[3 + k], L)
    p.px(cx + 3, foot - 2, WD[2 + k], L)
    for i in range(1, 12):
        p.px(cx - i, trunk + 4 - i // 2, WD[3 + k], L)
        p.px(cx + 1 + i, trunk + 3 - i // 2, WD[2 + k], L)
    leaves = {}
    for y in range(top, top + 26):
        for x in range(cx - 21, cx + 22):
            best = None
            for (dx, dy, r) in CLUMPS:
                d = math.hypot(x + 0.5 - (cx + dx), (y + 0.5 - (top + dy)) * 1.1) / r
                if d < 1 and (best is None or d < best[0]):
                    best = (d, dx, dy, r)
            if best:
                d, dx, dy, r = best
                if p.lite:
                    jitter = random.Random(seed * 7919 + (x // 2) * 131 + y // 2).uniform(-0.45, 0.45)
                else:
                    jitter = rnd.uniform(-0.45, 0.45)
                light = (-(x + 0.5 - cx - dx) - (y + 0.5 - top - dy) * 1.2) / r + jitter
                leaves[(x, y)] = 6 if light > 0.95 else 5 if light > 0.3 else 4 if light > -0.4 else 3
    dark = -3 if night else 0
    for (x, y), t in leaves.items():
        edge = any((x + ex, y + ey) not in leaves for ex, ey in ((1, 0), (0, 1), (-1, 0), (0, -1)))
        lit_edge = edge and t >= 5 and (x, y - 1) not in leaves
        p.px(x, y, Tf[max(0, (4 if lit_edge else 2 if edge else t) + dark)], L)
    for i, (arms, field, metal) in enumerate(CHALLENGERS):
        sx, sy = cx - 20 + i * 8, top + 22 + (0, 2, 1, 2, 0)[i]
        sp = {"K": K, "3": RAMP[field][3 + k] if field != "sable" else RAMP["sable"][3],
              "c": RAMP[metal][5 + k] if metal != "argent" else A[6 + k], "C": RAMP[metal][3 + k]}
        art = SHIELDS[arms]
        p.vline(sx + 2, sy - 3, sy, WD[1 + k], L)
        p.vline(sx + 3, sy - 3, sy, WD[1 + k], L)
        if i != 2:
            stamp(p, sx, sy, art, sp, L)
            continue
        frames = (1, -1) if motion else (1,)
        for f, lean in enumerate(frames):
            Lf = p.seq(f"st{seed}_{f}", f / 2, (f + 1) / 2, 2.2, keep=f == 0, z=0.5) if len(frames) > 1 else L
            stamp(p, sx, sy, [(" " * max(0, lean * (j // 3))) + row if lean > 0 else row[max(0, -lean * (j // 3)):]
                              for j, row in enumerate(art)], sp, Lf)
        if motion:
            Lg = p.seq(f"sg{seed}", 0, 0.14, 2.2, z=2)
            for gx, gy, c in ((7, 1, G[6]), (8, 0, G[5]), (8, 2, G[5]), (9, 1, G[4])):
                p.px(sx + gx, sy + gy, c, Lg)
    prop(p, cx - 22, top - 1, cx + 22, foot)
    return (cx - 22, cx + 22)


PENNON = [  # a pennon streaming right from its staff in two positions of its ripple: 1 the tincture, 2 its fold
    ["11111111..", "112111211.", "1111111111", "21112111..", "111......."],
    ["1111111...", "1121111211", "111111111.", "2111211...", "11........"],
]


def pennon(p: Pix, x, y, tinc: str, night: bool, motion=True, phase=0, seed=0, L="base", face=1):
    """A pennon of the tincture streaming from a staff at (x, y), forked at its tail and shaded at its folds: in a
    moving header it ripples between two positions; a still drawing keeps the first. Each position is drawn once a
    file and placed."""
    k = -1 if night else 0
    T = RAMP[tinc]
    frames = range(2) if motion else (0,)
    for f in frames:
        art = PENNON[(f + phase) % 2]
        key = ("pennon", tinc, night, (f + phase) % 2, face)
        if key not in p.syms:
            rows = art if face > 0 else flip(art)
            p.symbol(key, {(i, j): (T[3 + k] if ch == "1" else T[1 + k]) for j, row in enumerate(rows)
                           for i, ch in enumerate(row) if ch != "."})
        Lf = p.seq(f"streamer{seed % 3}_{f}", f / 2, (f + 1) / 2, 0.9 + 0.1 * (seed % 3), keep=f == 0, z=0.5) \
            if len(frames) > 1 else L
        p.use(key, x if face > 0 else x - len(art[0]) + 1, y, Lf)


# --------------------------------------------------------------------------- the stand and the herald
# The herald, facing left, blowing his trumpet: his hat (h), his face (f), his tabard quartered of his lord's arms
# (q Q, g G), his sleeve (s), hose (o) and shoes; the trumpet (Y y) with its bell, and the banner hung from it (b B,
# its charge c, its fringe Y).
HERALD = [
    "....................KKK..",
    "...................KhhhK.",
    "..................KhhhhhK",
    "...................KffeK.",
    "K.................KffffK.",
    "YK...............KYfffK..",
    "YYKKKKKKKKKKKKKKKYyK.K...",
    "YYyyyyyyyyyyyyyyyyK..K...",
    "YK.bbBbbbBb...KsKqqQQgK..",
    "K..bbccbbBb...KssqqQQGgK.",
    "...bcccbbBb..KsKKqqQQgGK.",
    "...bbccbbBb..KsK.QQqqGgK.",
    "...bbbcbbBb..KfK.QQqqgGK.",
    "...bbbbbbBb...K..QQqqGgK.",
    "...YbYbYbYb......KQQqqK..",
    "..................KoKoK..",
    "..................KoKoK..",
    "..................KoKoK..",
    ".................KkKKkK..",
]
# The spectators in the stand, head and shoulders over its parapet, 8 wide and 14 tall: a lady in her tall hennin
# banded in gold with her veil streaming from it; a lady waving her favour of red silk to the lists; a lord in his
# chaperon; and a lord in his cap with a gold feather. h H the hat, v V the veil, k the hair, f F e the face and its
# eyes, d D the gown or the doublet, n N gold, r R the favour.
FOLK = {
    "lady": ["...K....", "..KHK...", "..KHhK..", ".KHhhKv.", ".KHhhKvv", "KHhhhhKv", "KnnnnnKV", "KkfFfkKv",
             "KfeFefKV", ".KfffK.v", "..KfK..V", ".KDdddK.", "KDDnddDK", "KDDdddDK"],
    "wave": ["rr.....K....", "rRr...KHK...", ".rK...KHhK..", ".fK..KHhhKv.", ".dK..KHhhKvv", ".KdKKHhhhhKv",
             ".KdKKnnnnnKV", "..KdKkfFfkKv", "..KdKfeFefKV", "...KDKfffK.v", "....KDdKfK.V", ".....KDdddK.",
             "....KDDnddDK", "....KDDdddDK"],
    "lord": ["........", "........", "...KK...", ".KKHHKK.", "KHHHHHhK", "KhHHHhhK", "KhhKKKKh", "KkfFfkK.",
             "KfeFefK.", ".KfffK..", "..KfK...", ".KDdddK.", "KDnDdnDK", "KDDdddDK"],
    "cap": ["......n.", ".....nN.", "..KKKnK.", ".KHHHHK.", "KHHHHHHK", "KKKKKKKK", ".KkfFfK.", ".KfeFeK.",
            ".KffffK.", "..KffK..", "..KffK..", ".KDdddK.", "KDDnddDK", "KDDdddDK"],
}
FAVOUR = (["rr", "rRr", ".r"], ["Rr", "rrR", "r."])     # the favour's silk in two places as it is waved
# Each tier's spectators, left to right, (kind, hat, gown, skin) and how far along the stand each stands: each face on
# one of the hand's three skins, light to dark.
TIERS = (
    ((("wave", "gules", "azure", 0), 0), (("lord", "vert", "tenne", 2), 13), (("lady", "azure", "gules", 1), 22),
     (("cap", "tenne", "purpure", 0), 31), (("lady", "purpure", "vert", 2), 40)),
    ((("lady", "or", "purpure", 1), 3), (("cap", "gules", "azure", 2), 13), (("lady", "vert", "gules", 0), 23),
     (("lord", "azure", "or", 1), 33)),
)
# The arms of the knights who ride today, hung along the stand's front: the lion, the swan and the stag, and a
# chevron and a bend for the challengers (3 the field, c the charge).
CHALLENGERS = (("lion", "gules", "or"), ("chevron", "vert", "or"), ("swan", "azure", "argent"),
               ("bend", "sable", "argent"), ("stag", "purpure", "or"))


def herald(p: Pix, x, foot, night: bool, L="base"):
    """The herald on the ground at row `foot`, facing left, his trumpet raised with his lord's banner hung from it
    (25 wide from x). By night his tabard and his trumpet's gold take the torchlight."""
    k = -1 if night else 0
    Gu, Az = RAMP["gules"], RAMP["azure"]
    pal = {"K": K, "h": V[2 + k], "f": skin(1, night)["f"], "e": K, "q": Gu[3 + k], "Q": Az[3 + k], "g": G[4 + k],
           "G": G[2 + k], "s": Gu[2 + k], "o": RAMP["sable"][3], "k": K, "Y": G[5 + k], "y": G[3 + k],
           "b": Gu[3 + k], "B": Gu[1 + k], "c": G[5 + k]}
    stamp(p, x, foot - len(HERALD), HERALD, pal, L)


def _tile(p: Pix, pid: str, x0, y0, w: int, h: int, colour_at) -> str:
    """A pattern tile `w` by `h` placed from (x0, y0), each cell's colour from `colour_at(i, j)` (None leaves it
    clear)."""
    cols: dict = {}
    for j in range(h):
        for i in range(w):
            c = colour_at(i, j)
            if c:
                cols.setdefault(c, {}).setdefault(j, []).append(i)
    p.defs.append(f'<pattern id="{pid}" x="{x0}" y="{y0}" width="{w}" height="{h}" patternUnits="userSpaceOnUse">'
                  f'{paths(cols)}</pattern>')
    return pid


def fill(p: Pix, pid: str, x, y, w, h, L="base"):
    """A block laid in a pattern, its cells kept as a sprite's."""
    p.shapes[L].append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{pid})"/>')
    keep(p, {(xx, yy) for xx in range(x, x + w) for yy in range(y, y + h)})


STAND_W = 48        # the stand's width between its outer posts


def stand_height(tiers: int, banners: bool = True) -> int:
    """The rows a stand of `tiers` tiers rises over its ground, its banners included or not."""
    return 11 + 8 + 14 * tiers + 1 + 4 + 6 + (11 if banners else 0)


def stand(p: Pix, x0, foot, night: bool, motion: bool = True, w=STAND_W, seed=0, tiers=2, banners=True, L="base"):
    """The stand the ladies and the lords watch from, `w` wide from x0 on the ground at row `foot`, rising in
    `tiers` tiers: oak posts with hangings of the tinctures between them, dagged and fringed in gold; over them the
    gallery's parapet hung with purple under a gold border, the shields of the knights who ride today hung along it;
    behind it the spectators head and shoulders over it, ladies in their tall hennins with their veils and lords in
    their chaperons and feathered caps, one lady waving her favour to the lists, and over them a second tier behind
    its own rail; the stand's back of dark oak behind them; over all a canopy striped green and white with a dagged
    valance along its front, three lanterns hung under it, and a banner on each of its outer posts. By night the
    lanterns burn and light the faces under them. Returns the span it covers."""
    k = -1 if night else 0
    P = RAMP["purpure"]
    low = foot - 19
    top = low - 14 * tiers
    valance = top - 4
    roof = valance - 6
    posts = [x0, x0 + w // 3, x0 + 2 * w // 3, x0 + w - 2]
    planks = (WD[1 + k], WD[2 + k]) if not night else (DU[1], DU[2])
    fill(p, _tile(p, f"sb{seed}", x0, top - 1, 5, 1, lambda i, j: planks[0] if i == 0 else planks[1]), x0 + 2,
         top - 1, w - 2, low - top + 1, L)
    for b, (a, z) in enumerate(zip(posts, posts[1:])):
        T = RAMP[("gules", "azure", "vert")[(b + seed) % 3]]
        hh = foot - 1 - (low + 8)

        def hang(i, j, T=T, hh=hh):
            if j == 0:
                return G[4 + k]
            if j < hh - 3:
                return T[(3, 3, 2, 3)[i % 4] + k]
            if j < hh - 2:
                return T[2 + k]
            if j == hh - 2:
                return T[1 + k] if i % 4 != 3 else None
            return G[3 + k] if i % 4 == 1 else None
        fill(p, _tile(p, f"sh{seed}{b}", a + 2, low + 8, 4, hh, hang), a + 2, low + 8, z - a - 2, hh, L)
    for px in posts:
        reach = roof - (11 if banners and px in (posts[0], posts[-1]) else 0)
        p.vline(px, reach, foot, WD[4 + k], L)
        p.vline(px + 1, reach, foot, WD[2 + k], L)
    rnd = random.Random(seed + 5)
    for tier in range(tiers - 1, -1, -1):
        base = low - 14 * tier
        if tier:
            p.hline(x0 - 1, x0 + w + 1, base, WD[5 + k], L)
            p.hline(x0 - 1, x0 + w + 1, base + 1, RAMP["gules"][2 + k], L)
            p.hline(x0 - 1, x0 + w + 1, base + 2, RAMP["gules"][1 + k], L)
        for (kind, hat, gown, n), dx in TIERS[tier]:
            art = FOLK[kind]
            if dx + len(art[0]) > w - 1:
                continue
            face = skin(n, night)
            pal = {"K": K, "h": RAMP[hat][3 + k], "H": RAMP[hat][5 + k], "v": A[6 + k], "V": A[4 + k],
                   "k": RAMP["horse"][1 + k], "f": face["f"], "F": face["F"], "e": face["d"], "d": RAMP[gown][3 + k],
                   "D": RAMP[gown][5 + k], "n": G[5 + k], "N": G[3 + k], "r": RAMP["gules"][4 + k],
                   "R": RAMP["gules"][2 + k]}
            fx, fy = x0 + dx, base + 2 - len(art) + rnd.choice((0, 0, 1))
            pal["K"] = None
            if kind == "wave":
                stamp(p, fx, fy, [row.replace("r", ".").replace("R", ".") for row in art], pal, L, below=base + 1)
                frames = range(2) if motion else (0,)
                for f in frames:
                    Lf = L if len(frames) == 1 else p.seq(f"favour_{f}", f / 2, (f + 1) / 2, WAVE, keep=f == 0, z=0.5)
                    stamp(p, fx, fy, FAVOUR[f], pal, Lf)
            else:
                stamp(p, fx, fy, art, pal, L, below=base + 1)

    def parapet(i, j):
        if j == 0:
            return K
        if j == 1:
            return G[4 + k] if i % 3 else G[2 + k]
        if j == 7:
            return P[1 + k]
        return P[3 + k] if (i // 2) % 2 else P[2 + k]
    fill(p, _tile(p, f"sp{seed}", x0 - 1, low, 6, 8, parapet), x0 - 1, low, w + 2, 8, L)
    n = min(len(CHALLENGERS), (w - 2) // 9)
    gap = (w - 6 * n) / (n + 1)
    for i, (arms, field, metal) in enumerate(CHALLENGERS[:n]):
        sp = {"K": K, "3": RAMP[field][3 + k] if field != "sable" else RAMP["sable"][3],
              "c": RAMP[metal][5 + k] if metal != "argent" else A[6 + k], "C": RAMP[metal][3 + k]}
        stamp(p, x0 + round(gap + i * (6 + gap)), low + 1, SHIELDS[arms], sp, L)
    rows = valance - roof
    canopy = _tile(p, f"sc{seed}", x0, roof, 8, rows,
                   lambda i, j: (V, A)[i // 4][(3, 5)[i // 4] + (1 if j == 0 else 0) + k])
    p.shapes[L].append(f'<path d="M{x0 + rows - 4} {roof}h{w + 8 - 2 * rows}' + "v1h1" * (rows - 1)
                       + f'v1h-{w + 6}' + "v-1h1" * (rows - 1) + f'z" fill="url(#{canopy})"/>')
    layer = p.layers[L]
    if not hasattr(p, "cloth"):
        p.cloth = {}
    for y in range(roof, valance):
        inset = valance - 1 - y
        under = {(x, y) for x in range(x0 - 3 + inset, x0 + w + 3 - inset)}
        for xy in under & set(layer):
            del layer[xy]
        keep(p, under)
        p.cloth.update({(x, y): (V, A)[(x - x0) // 4 % 2][(3, 5)[(x - x0) // 4 % 2] + (1 if y == roof else 0) + k]
                        for (x, y) in under})
        p.px(x0 - 4 + inset, y, K, L)
        p.px(x0 + w + 3 - inset, y, K, L)
    p.hline(x0 - 1, x0 + w + 1, roof - 1, K, L)

    def front(i, j):
        green = i < 4
        if j == 0:
            return V[2 + k] if green else A[3 + k]
        if j == 1:
            return (V[3 + k] if green else A[5 + k]) if i % 4 else K
        if i % 4 in (1, 2):
            return (V[2 + k] if green else A[3 + k]) if j == 2 else (G[4 + k] if i % 2 else G[2 + k])
        return None
    fill(p, _tile(p, f"sv{seed}", x0 - 3, valance, 8, 4, front), x0 - 3, valance, w + 6, 4, L)
    if banners:
        for i, px in enumerate((posts[0], posts[-1])):
            T = RAMP[("vert", "gules")[(i + seed) % 2]]
            ty = roof - 11
            bx = px + 2 if i == 0 else px - 8
            p.px(px, ty - 1, G[6 + k], L)
            p.px(px + 1, ty - 1, G[3 + k], L)
            p.hline(min(bx, px) - 1, max(bx + 8, px + 2) + 1, ty + 1, WD[3 + k], L)
            for j in range(8):
                for c in range(8):
                    edge = c in (0, 7) or j == 0
                    charge = 2 <= c <= 5 and 2 <= j <= 5 and (c + j) % 3 != 0
                    col = G[4 + k] if edge else G[5 + k] if charge else T[3 + k]
                    if j == 7 and c % 2:
                        continue
                    p.px(bx + c, ty + 2 + j, T[1 + k] if j == 7 else col, L)
    for i, lx in enumerate((x0 + w // 4, x0 + w // 2, x0 + 3 * w // 4)):
        p.px(lx, valance + 4, S[2 + k], L)
        art = (".KKK.", "KgWgK", "KgFgK", ".KoK.")
        for j, row in enumerate(art):
            for dx, ch in enumerate(row):
                c = {"K": K, "g": G[3 + k], "o": G[1], "W": FL[6] if night else A[5],
                     "F": FL[5] if night else A[3]}.get(ch)
                if c:
                    p.px(lx - 2 + dx, valance + 5 + j, c, flick(p, i + 1) if night and ch in "WF" else L)
        if night:
            lamp(p, lx + 0.5, valance + 7, 15, i + 1,
                 {(lx - 2 + dx, valance + 5 + j) for dx in range(5) for j in range(4)})
            p.lit_stand = True
    prop(p, x0 - 4, roof - (13 if banners else 2), x0 + w + 4, foot)
    return (x0 - 4, x0 + w + 4)


STILL_HOIST = 18    # the columns of a standard nearest its staff, which hang still while its fly ripples


def lists_standard(p: Pix, x, foot, top, night: bool, motion=True, seed=0, w=36, L="base"):
    """The standard of the lists on its tall staff at x, from row `foot` up to its gilt knop over row `top`: a long
    standard tapering to its fly, St George's cross at the hoist and the host's livery of green over white along it
    with his gold knots, its fly cut in a swallow tail and its edges fringed in gold. In a moving header its fly
    ripples while the hoist hangs still. Halfway down the staff an iron cresset hangs on its bracket, cold by day
    and burning by night, so the torch that lights the knights' plate stands where the standard does."""
    k = -1 if night else 0
    Gu = RAMP["gules"]
    for y in range(top, foot):
        p.px(x, y, WD[4 + k], L)
        p.px(x + 1, y, WD[2 + k], L)
    stamp(p, x - 1, top - 3, [".N.", "NnN", "KnK"], {"N": G[6 + k], "n": G[3 + k], "K": WD[2 + k]}, L)
    h = 11

    def cloth(i, f, Lf):
        taper = (i * 3) // w
        wave = round(math.sin((i + 4 * f) / 4.2) * min(1.6, max(0, i - STILL_HOIST + 4) / 7))
        y0, y1 = top + taper + wave, top + h - 1 - taper + wave
        mid = (y0 + y1) / 2
        notch = max(0, i - (w - 9)) * 0.55
        for y in range(y0, y1 + 1):
            if notch and abs(y - mid) < notch - 0.5:
                continue
            if y in (y0, y1) or (notch and abs(y - mid) < notch + 0.5):
                c = G[4 + k]
            elif i < 8:
                c = Gu[3 + k] if i in (3, 4) or abs(y - mid) < 1 else A[6 + k]
            elif i == 8:
                c = G[3 + k]
            else:
                c = (V[3 + k] if y < mid - 0.5 else A[5 + k]) if y != round(mid - 0.5) else G[3 + k]
                u, v = (i - 13) % 11 - 1, y - round(mid - 0.5)
                if i < w - 6 and abs(u) <= 1 and abs(u) + abs(v) <= 2 and abs(v) <= 2:
                    c = G[5 + k]
            p.px(x + 2 + i, y, c, Lf)
    for i in range(STILL_HOIST):
        cloth(i, 0, L)
    frames = range(2) if motion else (0,)
    for f in frames:
        Lf = p.seq(f"flag_{f}", f / 2, (f + 1) / 2, 1.6, keep=f == 0, z=0.5) if len(frames) > 1 else L
        for i in range(STILL_HOIST, w):
            cloth(i, f, Lf)
    cy = top + 2 * (foot - top) // 3
    stamp(p, x + 2, cy - 4, ["..IcCcI", "...IiI.", "....I..", "IIIII.."], {"I": S[2 + k], "i": S[4 + k],
                                                                          "c": DU[2] if night else DU[1],
                                                                          "C": FL[1] if night else DU[3]}, L)
    if night:
        flame(p, x + 6, cy - 4, phase=seed, reach=21)
        p.cresset = True
    else:
        stamp(p, x + 5, cy - 6, [".k.", "kKk"], {"k": DU[2], "K": DU[0]}, L)
    prop(p, x - 2, top - 4, x + w + 3, foot)


# --------------------------------------------------------------------------- crested helms
# The great helm facing out with its T-shaped sight, the torse it wears and its mantling falling on both sides in
# dagged leaves, at three sizes. K outline; a b c d e steel dark to light, w its glint; t T the torse (tincture,
# metal); 3 4 the mantling's tincture (shade, light), n N its lining of metal.
HELM_L = [
    "........KKKKKKKK........",
    ".......KtTtTtTtTK.......",
    "......K4KKKKKKKK4K......",
    ".....K43KdeeedccK34K....",
    "....K433KdewedccK334K...",
    "...K4nN3KdeeedccK3Nn4K..",
    "..K43Nn3KKKKKKKKK3nN34K.",
    "..K3nN43KddKKccbK34Nn3K.",
    ".K43N343KdeKKcbbK343N34K",
    ".K3nN3K3KddKKcbbK3K3Nn3K",
    "K43N3KK3KdeKKcbbK3KK3N34",
    "K3nNK.K3KddcccbbK3K.KNn3",
    "K3N3K.K43KdcccbK34K.K3N3",
    ".KnK..KK3KKccbbK3KK..KnK",
    "..K...K4nKKKKKKKKn4K..K.",
    "......K3NnK....KnN3K....",
    ".......KKK......KKK.....",
]
CREST_L = {  # 12 wide, over the torse's middle
    "lion": ["..o.o.o.....", ".oGoGoGoo...", "oGGGGGGoYo..", "oGGGGGoYKYo.", "oGGGGoYYYYYo", "oGGGGoYYYooK",
             ".oGGGGoYrrr.", "..ooooooo..."],
    "swan": [".....KKK....", "....KWWWK...", "....KWKWqq..", ".....KWK....", "..KK.KWK....", ".KWWKKWWK...",
             "..KWWWWWK..."],
    "stag": ["K.K....K.K..", "K.KK..KK.K..", ".KK.KK.KK...", "...KHHHK....", "...KHKHK....", "....KHHK....",
             "....KHHK...."],
}
HELM_S = [  # 15 wide, for a contributor's avatar and today's mark
    ".....KKKKK.....",
    "....KtTtTtK....",
    "...KKKKKKKKK...",
    "..K4KdeedcK4K..",
    ".K43KdewdcK34K.",
    "K4nNKKKKKKKNn4K",
    "K3N3KdKKcbK3N3K",
    "K3n3KeKKbbK3n3K",
    ".KNKKdccbbKKNK.",
    "..K.K3KKKK3K.K.",
    ".....KK..KK....",
]
CREST_S = {  # 7 wide, over the torse
    "lion": [".o.o...", "oGGoYo.", "oGoYKY.", "oGoYrK.", ".ooo..."],
    "swan": ["..KK...", ".KWKq..", "..KW...", "KK.KW..", ".KWWWK."],
    "stag": ["K.K.K.K", ".KK.KK.", "..KHK..", "..KHH..", "..KHK.."],
    "griffin": ["..KK...", ".KGKq..", "KGGK...", "KGGGK..", ".KGGK.."],
    "boar": ["....KK.", ".KKKBBK", "KBBBKBq", ".KBBBK.", "..K.K.."],
}


HELM_M = [  # 19 wide and 14 tall, for a contributor's avatar: its mantling cut in dags short of the helm's foot
    ".....KKKKKKKKK.....",
    "....KtTtTtTtTtK....",
    "...K4KKKKKKKKK4K...",
    "..K43KdeeeedcK34K..",
    ".K433KdeweedcK334K.",
    "K4nN3KdeeeddcK3Nn4K",
    "K3Nn3KKKKKKKKK3nN3K",
    "K43N4KddeKccbK4N34K",
    "K3nN3KdeeKcbbK3Nn3K",
    "K4N3KKddeKcbbKK3N4K",
    "KnK3KKdeeKcbbKK3KnK",
    ".KK4K.KdcccbK.K4KK.",
    "..KnK.KdcccbK.KnK..",
    "...K..KKKKKKK..K...",
]
CREST_M = {  # 9 wide, over the torse
    "lion": [".o.o.o...", "oGoGoGo..", "oGGGGoYo.", "oGGGoYKYo", "oGGGoYYYK", ".oGGoYrr.", "..ooooo.."],
    "swan": ["...KKK...", "..KWWWKqq", "...KWK...", "KK.KWK...", "KWWKWWK..", ".KWWWWWK."],
    "stag": ["K.K...K.K", "KK.K.K.KK", ".KK.K.KK.", "...KHK...", "...KHHK..", "...KHK..."],
    "griffin": ["...KK....", "..KGGKqq.", ".KGGGK...", "KGGGGK...", "KGGGGGK..", ".KGGGK..."],
    "boar": [".........", "....KKK..", ".KKKBBBK.", "KBBBBKBqq", ".KBBBBBK.", "..K.K.K.."],
}


HELM_X = [  # 11 wide and 10 tall, for the mark beside SECTION A-A: a stag's antlers, the torse, the helm, the mantling
    "..K.K.K.K..",
    "..KK.K.KK..",
    "...KtTtK...",
    "..KKKKKKK..",
    ".4KdeedcK4.",
    "43KKKKKKK34",
    "3nKdKKcbKn3",
    ".3KdccbbK3.",
    "..KKKKKKK..",
    "...........",
]


def crest_pal(night: bool, tinc: str, metal: str) -> dict:
    k = -1 if night else 0
    T, M = RAMP[tinc], RAMP[metal]
    return {"K": K, "a": S[1], "b": S[2 + k], "c": S[3 + k], "d": S[4 + k], "e": S[5 + k], "w": S[6],
            "t": T[3 + k], "T": M[4 + k] if metal != "argent" else M[5 + k], "3": T[2 + k], "4": T[3 + k],
            "n": M[2 + k] if metal != "argent" else M[3 + k], "N": M[4 + k] if metal != "argent" else M[5 + k],
            "o": G[1], "G": G[4 + k], "Y": G[5 + k], "W": A[6 + k], "q": G[4 + k], "H": RAMP["horse"][4 + k],
            "B": RAMP["sable"][4 + k], "r": RAMP["gules"][4 + k]}


def crested_helm(p: Pix, x, y, crest: str, night: bool, tinc="gules", metal="or", size="L", L="base"):
    """A crested great helm with its mantling, its top-left at (x, y) (the crest's top): large ("L"), 24 wide and
    24 tall; middling ("M"), 19 wide and 20 tall; the section mark's ("X"), 11 by 10; or small, 15 wide and 16
    tall."""
    pal = crest_pal(night, tinc, metal)
    if size == "L":
        stamp(p, x + 6, y + 7 - len(CREST_L[crest]), CREST_L[crest], pal, L)
        stamp(p, x, y + 7, HELM_L, pal, L)
    elif size == "M":
        stamp(p, x + 5, y + 6 - len(CREST_M[crest]), CREST_M[crest], pal, L)
        stamp(p, x, y + 6, HELM_M, pal, L)
    elif size == "X":
        stamp(p, x, y, HELM_X, pal, L)
    else:
        stamp(p, x + 4, y, CREST_S[crest], pal, L)
        stamp(p, x, y + 5, HELM_S, pal, L)


# --------------------------------------------------------------------------- a knight at rest, and the helm show
# His squire, standing facing out at his horse's head: his cap of the livery, his face, a tunic and hose parted of
# purpure and gold, his belt, and his hands at his sides, the near one holding his knight's lance. h H the cap, f F e
# the face lit to shaded, r his hair, y Y q Q the tunic's gold and purpure, b the belt, o O the hose, k the shoes.
SQUIRE = [
    "....KKKK....",
    "...KhHHhK...",
    "..KhHHhhhK..",
    "..KKKKKKKK..",
    "..KrffffrK..",
    "..KfKffKfK..",
    "..KfffffeK..",
    "...KfeefK...",
    "....KffK....",
    "...KyKKqK...",
    "..KyyYqQqK..",
    ".KyKyYqQKqK.",
    ".KyKyyqqKqK.",
    ".KfKyyqqKfK.",
    "..KKbbbbKK..",
    "...KyyqqK...",
    "...KyyqqK...",
    "...KyKKqK...",
    "...KoK.KOK..",
    "...KoK.KOK..",
    "...KoK.KOK..",
    "...KoK.KOK..",
    "..KkkK.KkkK.",
]


def squire(p: Pix, x, foot, crest: str, night: bool, motion=True, seed=0, L="base"):
    """The knight's squire on the ground at row `foot`, 12 wide from x, holding his knight's lance upright at his
    side, its butt on the ground and its coronel high over the horse's head, its spiral of the knight's tincture and
    gold and his pennon streaming from it."""
    k = -1 if night else 0
    tinc, _ = ARMS[crest]
    T, P = RAMP[tinc], RAMP["purpure"]
    face = skin(2, night)
    stamp(p, x, foot - len(SQUIRE), SQUIRE, {"K": K, "h": P[3 + k], "H": P[4 + k], "f": face["f"],
                                             "e": face["e"], "r": RAMP["horse"][2 + k], "y": G[4 + k],
                                             "Y": G[5 + k], "q": P[3 + k], "Q": P[4 + k], "b": WD[2 + k],
                                             "o": P[2 + k], "O": G[3 + k], "k": RAMP["sable"][3]}, L)
    lx, top = x - 1, foot - 54
    for y in range(top, foot):
        band = ((y - top) // 2) % 2
        p.px(lx, y, G[5 + k] if band else T[4 + k], L)
        p.px(lx + 1, y, G[2 + k] if band else T[1 + k], L)
    p.px(lx, top - 1, S[5 + k], L)
    p.px(lx + 1, top - 1, S[3 + k], L)
    p.px(lx, top - 2, S[4 + k], L)
    stamp(p, lx - 1, foot - 13, ["KffK", "KfeK"], {"K": K, "f": face["f"], "e": face["e"]}, L)
    pennon(p, lx + 2, top + 1, tinc, night, motion=motion, seed=20 + seed)
    prop(p, lx - 1, top - 3, x + 13, foot)


def door_lances(p: Pix, cx, foot, top, crest: str, night: bool, motion=True, seed=0, L="base"):
    """A lance planted in the ground at each side of a pavilion's door about cx, from row `foot` up to row `top`,
    its pennon streaming from its head and the knight's shield hung on it: his arms on the one, his colours
    quartered on the other."""
    k = -1 if night else 0
    tinc, metal = ARMS[crest]
    T, M = RAMP[tinc], RAMP[metal]
    sp = {"K": K, "3": T[3 + k], "c": M[5 + k], "C": M[3 + k]}
    for i, lx in enumerate((cx - 9, cx + 8)):
        for y in range(top, foot):
            band = ((y - top) // 2 + i) % 2
            p.px(lx, y, M[5 + k] if band else T[4 + k], L)
            p.px(lx + 1, y, M[2 + k] if band else T[1 + k], L)
        p.px(lx, top - 1, S[5 + k], L)
        p.px(lx + 1, top - 1, S[3 + k], L)
        art = SHIELDS[crest] if i == 0 else ["KKKKKK", "K33ccK", "K33ccK", "KccK3K", "Kcc33K", ".Kc3K.", "..KK.."]
        stamp(p, lx - 2, foot - 16, art, sp, L)
        pennon(p, lx + 2, top + 1, tinc, night, motion=motion, phase=i + 1, seed=30 + seed)
    prop(p, cx - 12, top - 3, cx + 22, foot)


def knight_at_rest(p: Pix, x, foot, crest: str, night: bool, motion=True, face=-1, seed=0, size="M", L="base"):
    """A knight at rest on his horse standing on row `foot`, facing left (toward the title) or right: the horse
    square on its feet, one forefoot raised, in its caparison. A middling one, 36 wide from x, holds his lance
    upright in his raised hand, its butt on his stirrup, his pennon streaming from it behind him; a large one, a
    third larger again and 50 wide, sits with his hand on his reins while his squire holds his lance (see
    `squire`)."""
    tinc, metal = ARMS[crest]
    k = -1 if night else 0
    if size == "L":
        W = len(HORSE_L[0])
        rx, ry = mounted(p, x, foot - 32, crest, night, face=face, legs=LEGS_L_REST, arm=None, size="L")
        rw = len(RIDER_L[0])
        rp = rider_pal(tinc, metal, night)
        if face > 0:
            stamp(p, rx + 6, ry + 12, ARM_L, rp, L)
            _rein(p, x + HORSE_L_BIT[0], foot - 32 + HORSE_L_BIT[1], rx + 17, ry + 18, night)
        else:
            stamp(p, rx + rw - 6 - len(ARM_L[0]), ry + 12, flip(ARM_L), rp, L)
            _rein(p, x + W - 1 - HORSE_L_BIT[0], foot - 32 + HORSE_L_BIT[1], rx + rw - 18, ry + 18, night)
        prop(p, x - 1, ry - 10, x + W + 1, foot)
        return (x - 1, x + W + 1)
    W, rw = len(HORSE[0]), len(RIDER[0])
    rx, ry = mounted(p, x, foot - 20, crest, night, face=face, legs=LEGS_REST, arm="up")
    hx = rx + 6 if face > 0 else rx + rw - 7
    top = ry - 22
    T = RAMP[tinc]
    for y in range(top, ry + 18):
        band = ((y - top) // 2) % 2
        p.px(hx, y, G[5 + k] if band else T[4 + k], L)
        p.px(hx + 1, y, G[2 + k] if band else T[1 + k], L)
    p.px(hx, top - 1, S[5 + k], L)
    p.px(hx + 1, top - 1, S[3 + k], L)
    p.px(hx, top - 2, S[4 + k], L)
    stamp(p, hx - 1 if face < 0 else hx, ry + 6, ["KccK", "KdeK"] if face > 0 else ["KccK", "KdeK"],
          rider_pal(tinc, metal, night), L)
    pennon(p, hx + 2 if face < 0 else hx - 1, top + 1, tinc, night, motion=motion, seed=20 + seed,
           face=1 if face < 0 else -1)
    prop(p, x - 1, top - 3, x + W + 1, foot)
    return (x - 1, x + W + 1)


def helm_stand(p: Pix, x, foot, crest: str, night: bool, tinc="gules", metal="or", size="L", post=None, L="base"):
    """The helm show: a crested great helm with its mantling set on a turned oak post, 24 wide from x on the ground
    at row `foot` and 35 tall, as the helms were shown before a tournament; or ("M") a middling helm, 19 wide, on a
    shorter post, 27 tall; or ("S") a small helm, 15 wide and 16 tall, set down on row `foot` itself, as on a
    barrier's rail. `post` stands the large or the middling helm on a post that many rows tall in place of its own,
    eleven rows for the large and seven for the middling."""
    k = -1 if night else 0
    if size == "S":
        crested_helm(p, x, foot - 16, crest, night, tinc, metal, "S", L)
        prop(p, x - 1, foot - 17, x + 16, foot)
        return
    big = size == "L"
    rows = post if post is not None else 11 if big else 7
    crested_helm(p, x, foot - rows - (23 if big else 19), crest, night, tinc, metal, "L" if big else "M", L)
    c, top = (x + 11 if big else x + 9), foot - rows
    for y in range(top, foot):
        p.px(c, y, WD[5 + k], L)
        p.px(c + 1, y, WD[3 + k], L)
    p.hline(c - 3, c + 5, foot - 1, WD[2 + k], L)
    p.hline(c - 2, c + 4, foot - 2, WD[4 + k], L)
    p.px(c - 1, top - 1, WD[4 + k], L)
    p.px(c + 2, top - 1, WD[2 + k], L)
    prop(p, x - 1, foot - rows - (25 if big else 21), x + (25 if big else 20), foot)


def lance_rack(p: Pix, x, foot, night: bool, n=3, h=34, L="base"):
    """A rack of lances standing ready, their butts in a trough and their heads leaning on a bar: each painted in a
    spiral of its knight's tincture and gold, a vamplate on each."""
    k = -1 if night else 0
    for i, tinc in enumerate(("gules", "azure", "purpure")[:n]):
        T = RAMP[tinc]
        lx = x + 2 + i * 4
        for y in range(foot - h + i * 2, foot - 1):
            band = ((y + i) // 2) % 2
            p.px(lx, y, G[5 + k] if band else T[4 + k], L)
            p.px(lx + 1, y, G[2 + k] if band else T[1 + k], L)
        p.px(lx, foot - h + i * 2 - 1, S[5 + k], L)
        vy = foot - 12
        for (dx, dy, c) in ((-1, 0, S[5 + k]), (0, 0, S[4 + k]), (1, 0, S[3 + k]), (2, 0, S[2 + k]), (-1, 1, K),
                            (0, 1, S[3 + k]), (1, 1, S[2 + k]), (2, 1, K)):
            p.px(lx + dx, vy + dy, c, L)
    p.hline(x, x + 4 * n + 3, foot - h + 8, WD[4 + k], L)
    p.hline(x, x + 4 * n + 3, foot - h + 9, WD[2 + k], L)
    for y in range(foot - 4, foot):
        p.hline(x, x + 4 * n + 3, y, WD[3 + k] if y > foot - 4 else WD[5 + k], L)
    p.vline(x, foot - h + 8, foot, WD[2 + k], L)
    p.vline(x + 4 * n + 3, foot - h + 8, foot, WD[1 + k], L)
    prop(p, x - 1, foot - h - 1, x + 4 * n + 5, foot)


# --------------------------------------------------------------------------- the quintain
# The quintain the knights practise at: its shield quartered gules and argent with a gilt boss, lit on its left (R r s
# the red light to dark, W w the white, B the boss); and the sack of sand that swings round on the arm's short end
# (b B q the sacking light to dark).
QSHIELD = [
    "KKKKKKKKKKK",
    "KRrrrrWWWwK",
    "KRrrrrWWWwK",
    "KRrrrrWWWwK",
    "KRrrrKKWWwK",
    "KRrrKYGKWwK",
    "KWWWKGgKrsK",
    "KWWWWKKrrsK",
    ".KWWWWrrrK.",
    ".KWWWWrrsK.",
    "..KWWWrsK..",
    "...KWWrK...",
    "....KKK....",
]
QBAG = [
    "...K...",
    "..KbK..",
    ".KbBbK.",
    "KbBBbbK",
    "KbBbbqK",
    "KbbbbqK",
    "KbbbqqK",
    ".KbqqK.",
    "..KKK..",
]
QUINTAIN_W = 31     # from the shield's left edge to the end of the arm's short end
QUINTAIN_H = 36     # the rows it rises over its ground, the pivot's knob included


def quintain_post(p: Pix, x, foot, night: bool, motion: bool = True, seed=0, L="base"):
    """The quintain on the ground at row `foot`, 31 wide from x, the shield's left edge: an oak post on its feet,
    an iron pivot on its head and the arm across it, the shield on the arm's long end toward the lists and on its
    short end the sack of sand on its chain, which swings in a moving header. Returns the span it covers."""
    k = -1 if night else 0
    Gu = RAMP["gules"]
    pal = {"K": K, "R": Gu[4 + k], "r": Gu[3 + k], "s": Gu[2 + k], "W": A[6 + k], "w": A[4 + k], "Y": G[6 + k],
           "G": G[4 + k], "g": G[2 + k], "b": CV[3 + k], "B": CV[5 + k], "q": CV[1 + k]}
    post, top = x + 20, foot - 34
    arm = top + 4
    for y in range(arm, foot - 2):
        for dx, c in ((-1, K), (0, WD[5 + k]), (1, WD[4 + k]), (2, WD[2 + k]), (3, K)):
            p.px(post + dx, y, c, L)
    for xx in range(post - 6, post + 10):
        p.px(xx, foot - 3, K, L)
        p.px(xx, foot - 2, WD[5 + k] if xx < post else WD[4 + k], L)
        p.px(xx, foot - 1, WD[2 + k], L)
    for xx in (post - 7, post + 10):
        p.vline(xx, foot - 2, foot, K, L)
    for i in range(3):
        p.px(post - 2 - i, foot - 4 - i, WD[4 + k], L)
        p.px(post + 4 + i, foot - 4 - i, WD[2 + k], L)
    stamp(p, post - 1, top, [".KKK.", "KIiiK", "KiiiK"], {"K": K, "I": S[5 + k], "i": S[3 + k]}, L)
    p.px(post + 1, top - 1, S[5 + k], L)
    for xx in range(x + 5, post + 10):
        p.px(xx, arm, K, L)
        p.px(xx, arm + 1, WD[5 + k], L)
        p.px(xx, arm + 2, WD[2 + k], L)
        p.px(xx, arm + 3, K, L)
    p.vline(post + 10, arm + 1, arm + 3, K, L)
    stamp(p, x, arm - 4, QSHIELD, pal, L)
    bx = post + 8
    frames = (0, 3) if motion else (0,)
    for f, swing in enumerate(frames):
        Lf = p.seq(f"qs{seed}_{f}", f / 2, (f + 1) / 2, TILT, keep=f == 0, z=0.5) if len(frames) > 1 else L
        for j, y in enumerate(range(arm + 4, arm + 12)):
            p.px(bx + swing * j // 8, y, S[2 + k] if j % 2 else S[4 + k], Lf)
        stamp(p, bx - 3 + swing, arm + 12, QBAG, pal, Lf)
    prop(p, x - 1, top - 2, post + 11, foot)
    return (x - 1, post + 11)


TILTING_W = {"M": 72, "L": 89}      # a knight running at the quintain, from his horse's tail to the quintain's end


def tilting(p: Pix, x, foot, night: bool, motion: bool = True, crest="stag", seed=0, size="M", L="base"):
    """A knight running at the quintain, `TILTING_W` wide from x on the ground at row `foot`, middling ("M") or a
    third larger again ("L"), as the near knight of a joust rides: on his horse in its caparison, his lance couched
    and its coronel striking the shield at the arm's long end, which a flash of gold marks in a moving header, the
    sack swinging round behind. Returns the span it covers."""
    if size == "L":
        qx = x + TILTING_W["L"] - QUINTAIN_W
        hx, hy = x, foot - 32
        rx, ry = mounted(p, hx, hy, crest, night, face=1, legs=LEGS_L, arm=None, size="L", L=L)
        grip = knight_points(hx, hy, "L", 1)[2]
        _rein(p, hx + HORSE_L_BIT[0], hy + HORSE_L_BIT[1], grip[0] - 4, grip[1] + 1, night)
    else:
        qx = x + 41
        hx, hy = x, foot - 21
        rx, ry = mounted(p, hx, hy, crest, night, face=1, arm=None, L=L)
        _rein(p, hx + HORSE_BIT[0], hy + HORSE_BIT[1], rx + 9, ry + 10, night)
    span = quintain_post(p, qx, foot, night, motion=motion, seed=seed, L=L)
    tinc = ARMS[crest][0]
    if size == "L":
        hit = (qx - 3, foot - 28)
        d = max(abs(hit[0] - grip[0]), abs(hit[1] - grip[1]), 1)
        lance(p, round(grip[0] - (hit[0] - grip[0]) * 8 / d), round(grip[1] - (hit[1] - grip[1]) * 8 / d), *hit,
              tinc, night, L=L)
        couched_arm(p, rx, ry, crest, night, size="L", L=L)
    else:
        lance(p, rx - 4, ry + 10, qx - 3, foot - 28, tinc, night, L=L)
        couched_arm(p, rx, ry, crest, night, L=L)
    if motion:
        Lf = p.seq(f"qf{seed}", 0, 0.12, TILT, z=2)
        for dx, dy, c in ((-1, 0, G[6]), (-2, -2, G[5]), (-2, 2, G[5]), (-4, 0, G[4]), (0, -3, G[4]),
                          (0, 3, G[4])):
            p.px(qx + dx, foot - 28 + dy, c, Lf)
    return (x - 1, span[1])


# --------------------------------------------------------------------------- the footer's barrier and herald's mark
# The herald's trumpet hung across a pole with his lord's banner hanging from it, and a lantern on the pole's head:
# 16 wide, the pole (p P) running on down from the last row to whatever it stands on. K the outlines, G g z the
# lantern's brass, L l w its glass, Y y z the trumpet's gold, b B the banner, c its lion and its cords, f its fringe.
MARK = [
    "...........KK...",
    "..........KGgK..",
    ".........KGGggK.",
    ".........KLwLlK.",
    ".........KlLllK.",
    ".........KggzzK.",
    "..........KpPK..",
    "KK.........pP...",
    "YyK........pP...",
    "YYyKKKKKKKKpPKKK",
    "YYYYYYYYYYYpPYYK",
    "YYYyyyyyyyypPyyK",
    "YYzKKKKKKKKpPKKK",
    "YzK.c....c.pP...",
    "KK.KbbbbbbbBP...",
    "...KbccbbbbBP...",
    "...KcccbbcbBP...",
    "...KbccccbcBP...",
    "...KbbcccbbBP...",
    "...KbcbbccbBP...",
    "...KbbbbbbbBP...",
    "...KffffffffP...",
    "....f.f.f.fpP...",
]
# The same two rows shorter, the trumpet hung close under the lantern, where the notes leave the mark less room.
MARK_SHORT = MARK[:5] + ["KK" + MARK[5][2:], "YyK" + MARK[6][3:]] + MARK[9:]
MARK_W = 16


def footer_mark(p: Pix, x, y, night: bool):
    """Where the herald's mark goes at the corner of a footer's closing notes, its lantern's ring at row y - 6: drawn
    by `footing` once the footer's words are set, standing on what lies under it."""
    p.mark_at = (x, y - 6)


def herald_mark(p: Pix, x, top, foot, night: bool, short=False, L="base"):
    """The herald's mark from row `top` to row `foot`, 16 wide from x: his trumpet hung across a pole with his lord's
    banner hanging from it, red with a gold lion and a gold fringe, and a lantern on the pole's head, its glass pale
    by day and by night lit, flickering, its light on the pole, the gold and the canvas round it."""
    k = -1 if night else 0
    Gu = RAMP["gules"]
    art = MARK_SHORT if short else MARK
    stamp(p, x, top, art, {"K": K, "p": WD[4 + k], "P": WD[2 + k], "G": G[5 + k], "g": G[3 + k], "z": G[2 + k],
                           "L": FL[6] if night else A[4], "l": FL[5] if night else A[3], "w": FL[6] if night else A[5],
                           "Y": G[6 + k], "y": G[4 + k], "b": Gu[3 + k], "B": Gu[1 + k], "c": G[5 + k],
                           "f": G[4 + k]}, L)
    for y in range(top + len(art), foot):
        last = y == foot - 1
        for dx, c in ((10, K if last else None), (11, WD[4 + k]), (12, WD[2 + k]), (13, K if last else None)):
            if c:
                p.px(x + dx, y, c, L)
    if night:
        p.px(x + 11, top + 3, FL[6], flick(p, 1))
        halo(p, x + 12, top + 4, 7, 6, FL[2], GLOW, L=flick(p, 1, back=True))
        lamp(p, x + 12, top + 4, 13, 1, {(x + i, top + j) for j in range(3, 5) for i in range(10, 14)})
    prop(p, x - 1, top - 1, x + MARK_W + 1, foot)


RISE = 5            # the most rows the barrier rises over its lowest where a footer's cells leave it room
RUN = 28            # the fewest columns a stretch of the barrier rises along
BAY = 32            # the columns between the posts along a stretch of the barrier


def _room(p: Pix, x, top, rule: str, boxes) -> int:
    """The rows over row `top` at column x clear of every word by two rows and of anything else drawn by two (a
    ruled line between cells beside it excepted), up to RISE."""
    base = p.layers["base"]
    n = 0
    while n < RISE:
        y = top - 1 - n
        if (x, y) in base or not p.clear_of_words(x - 1, y - 2, x + 2, y + 1) \
                or any(a <= x < c and b <= y < d for a, b, c, d in boxes):
            break
        if any(base.get((x + dx, y + dy)) not in (None, rule) for dx in (-1, 0, 1) for dy in (-2, -1)):
            break
        n += 1
    return n


def barrier(p: Pix, tops: list, night: bool, L="base", uid="tr"):
    """The tilt's barrier along a footer's foot, its top at column x at row `tops[x]`: an oak rail along its top, lit,
    and under it the planking painted in boards of green and white by turns, down to a band of the host's green and
    a gold fringe along the foot (where it is lowest, the rail on the fringe alone); an oak post capped in gilt
    wherever its rail steps up or down and at every bay wherever it stands five rows tall or more, and its shadow on
    the canvas over it wherever that leaves the words their room."""
    k = -1 if night else 0
    w, h = p.w, p.h
    base = p.layers[L]
    planks = (V[4 + k], V[3 + k], V[3 + k], V[2 + k], A[6 + k], A[5 + k], A[5 + k], A[3 + k])
    foot: dict = {}
    for x in range(6):
        foot.setdefault(V[(4, 4, 3, 3, 3, 2)[x] + k], {}).setdefault(0, []).append(x)
        foot.setdefault(G[4 + k] if x % 2 else K, {}).setdefault(1, []).append(x)
    p.defs.append(f'<pattern id="{uid}k" width="8" height="1" patternUnits="userSpaceOnUse">'
                  f'{paths({c: {0: [i]} for i, c in enumerate(planks)})}</pattern>'
                  f'<pattern id="{uid}f" y="{h - 2}" width="6" height="2" patternUnits="userSpaceOnUse">'
                  f'{paths(foot)}</pattern>')
    p.shapes[L].append(f'<rect y="{h - 2}" width="{w}" height="2" fill="url(#{uid}f)"/>')
    x = 0
    while x < w:
        t = tops[x]
        b = next((i for i in range(x, w) if tops[i] != t), w)
        if h - t > 2:
            p.hline(x, b, t, K, L)
        p.hline(x, b, t + (1 if h - t > 2 else 0), WD[5 + k], L)
        if h - 2 > t + 2:
            p.shapes[L].append(f'<rect x="{x}" y="{t + 2}" width="{b - x}" height="{h - 4 - t}" '
                               f'fill="url(#{uid}k)"/>')
        for xx in range(x, b):
            if (xx, t - 1) not in base and p.clear_of_words(xx - 1, t - 2, xx + 2, t + 1):
                p.apx(xx, t - 1, X["shade_ink"], 0.2, L)
        keep(p, {(xx, y) for xx in range(x, b) for y in range(t, h)})
        x = b
    steps = [x for x in range(5, w - 4) if tops[x] != tops[x - 1]]
    posts = [x if tops[x] < tops[x - 1] else x - 2 for x in steps]
    posts += [x for x in range(BAY // 2, w - 8, BAY) if tops[x] <= h - 5 and tops[x] == tops[x + 1]
              and all(abs(x - q) > 6 for q in steps) and not any(base.get((x + d, tops[x] - 2)) for d in (-1, 0, 1, 2))]
    for px in posts:
        t = min(tops[px], tops[px + 1])
        for dx, c in ((0, WD[4 + k]), (1, WD[2 + k])):
            p.vline(px + dx, t, h - 2, c, L)
        if p.clear_of_words(px, t - 2, px + 2, t):
            p.px(px, t - 1, G[6 + k], L)
            p.px(px + 1, t - 1, G[3 + k], L)


# The design's mark at its sizes, the larger first, each (helm, its post's rows, width): the large helm on its own
# post and on a short one, the middling helm on its post, and the small helm set down on a barrier's rail (see
# `helm_stand`).
HELMS = {"L": ("L", 11, 24), "Ls": ("L", 3, 24), "M": ("M", 7, 19), "S": ("S", 0, 15)}
CANVAS_TOP = 7      # the first row a footer's mark may reach, a clear row under the valance along its top


def _helm_cells(size: str) -> frozenset:
    """Every cell of the design's mark at `size` (see `HELMS`), the crested great helm on its post, from the foot of
    its post's left column: what a footer tests against its words before it sets the mark."""
    if size not in _HELM_CELLS:
        q = Pix(30, 40)
        helm, post, _ = HELMS[size]
        helm_stand(q, 0, 40, "lion", False, size=helm, post=post)
        _HELM_CELLS[size] = frozenset((x, y - 40) for x, y in q.layers["base"])
    return _HELM_CELLS[size]


_HELM_CELLS: dict = {}


def helm_spot(p: Pix, x0, x1, foot, from_right=True, sizes=("L", "Ls", "M")):
    """Where the design's mark stands on row `foot` between columns x0 and x1, from the right end or from the left:
    (x, size), the first of `sizes` (see `HELMS`) that fits before the next, every cell of it two units clear of
    every word, one clear of anything drawn there and none above `CANVAS_TOP`; None where none fits."""
    base = p.layers["base"]
    for size in sizes:
        cells, w = _helm_cells(size), HELMS[size][2]
        if foot + min(y for _, y in cells) < CANVAS_TOP:
            continue
        for x in range(x1 - w, x0 - 1, -1) if from_right else range(x0, x1 - w + 1):
            if all(p.clear_of_words(x + i - 2, foot + j - 2, x + i + 3, foot + j + 3) for i, j in cells) and not any(
                    (x + i + di, foot + j + dj) in base for i, j in cells for di in (-1, 0, 1) for dj in (-1, 0)):
                return x, size
    return None


def footing(p: Pix, night: bool, rule: str, helm=()):
    """A footer once its words are set: the herald's mark at the corner of its notes, its pole standing on the
    barrier or, on a phone, on the rule under the notes, the shorter mark where they leave it less room; the tilt's
    barrier along its foot, the whole width, as low as the lowest word leaves it and rising by up to five rows in
    each cell that leaves it room along RUN columns or more, the ruled lines between them standing on it, a post
    capped in gilt at every bay where it stands five rows tall or more; and the design's mark, the crested great
    helm, at the first place `helm` finds it room: each place a search (x0, x1, foot, from_right, sizes) for
    `helm_spot`, a foot of None standing the helm on the barrier at its lowest. The barrier runs on behind it, and
    the footer keeps where the helm stands as `helm_at`, (x, size, foot)."""
    w, h = p.w, p.h
    base = p.layers["base"]
    low = max((b[3] for b in p.words), default=0)
    top = min(h - 2, max(h - 6, low + 2))
    mark = getattr(p, "mark_at", None)
    if mark:
        x0, mtop = mark
        foot = next((y for y in range(mtop + 1, top) if base.get((x0 + 11, y)) == rule), top)
        art = MARK if foot - mtop > len(MARK) else MARK_SHORT if foot - mtop >= len(MARK_SHORT) else None
        for x in range(x0, x0 + 4) if art else ():
            if x + MARK_W < w - 4 and p.clear_of_words(x - 1, mtop - 1, x + MARK_W + 1, foot) and not any(
                    (i, j) in base for i in range(x - 1, x + MARK_W + 1) for j in range(mtop, foot)):
                herald_mark(p, x, mtop, foot, night, short=art is MARK_SHORT)
                break
    spot = None
    for x0, x1, stand, from_right, sizes in helm:
        stand = top if stand is None else stand
        found = helm_spot(p, x0, x1, stand, from_right, sizes)
        if found:
            spot = (*found, stand)
            break
    boxes = list(getattr(p, "props", []))
    if spot and spot[1] == "S":
        boxes.append((spot[0] - 2, 0, spot[0] + HELMS["S"][2] + 2, h))      # the rail it is set down on stays low
    room = [_room(p, x, top, rule, boxes) if 4 < x < w - 4 else 0 for x in range(w)]
    ruled = {x for x in range(5, w - 4) if sum(base.get((x, y)) == rule for y in range(top - RISE - 2, top)) >= 2
             and base.get((x - 1, top - 3)) != rule and base.get((x + 1, top - 3)) != rule}
    runs, x = [], 5
    while x < w - 4:
        if room[x] < 3 or x in ruled:
            x += 1
            continue
        b = next((i for i in range(x, w - 4) if room[i] < 3 or i in ruled), w - 4)
        if b - x >= RUN:
            if runs and x - runs[-1][1] == 1 and runs[-1][1] in ruled:
                runs[-1][1] = b
            else:
                runs.append([x, b])
        x = b
    tops = [top] * w
    for a, b in runs:
        tops[a:b] = [top - min(room[i] for i in range(a, b) if i not in ruled)] * (b - a)
    for xy in [xy for xy, c in base.items() if c == rule and xy[1] >= tops[xy[0]]]:
        del base[xy]
    barrier(p, tops, night)
    if spot:
        size, post, _ = HELMS[spot[1]]
        helm_stand(p, spot[0], spot[2], "lion", night, size=size, post=post)
        p.helm_at = spot
    return top


# --------------------------------------------------------------------------- links
# Icons for the bannerets, 9 by 7, in gold on the tincture: a crested helm, a trumpet, a crown, crossed lances.
# G gold, g its shade, Y its light, K a dark line.
ICONS = {
    "helm": [".YYGGGGg.", "YGGGGGGgg", "GKKKKKKKg", "GGGgKGGgg", "GGGgKGGgg", ".GGgKGgg.", "..ggggg.."],
    "trumpet": ["........Y", ".......YG", "YGGGGGGGG", "YgggggggG", ".gG.G....", ".GGGG....", ".gGgG...."],
    "crown": ["Y..Y..Y..", "YG.GY.GY.", "GGGGGGGG.", "GgYgYgGg.", "GGGGGGGG.", "gggggggg.", "........."],
    "lances": ["Y.......Y", ".G.....G.", "..G...G..", "...G.G...", "..GgYgG..", ".G.....G.", "g.......g"],
}
LINK_SPRITES = ("helm", "trumpet", "crown", "lances")
LINK_TINCTURES = ("gules", "azure", "vert", "purpure")


def icon_pal(night: bool) -> dict:
    k = -1 if night else 0
    return {"G": G[5 + k], "g": G[3 + k], "Y": G[6 + k], "K": K}


def banneret(p: Pix, w: int, seed: int, night: bool):
    """A link button finished as a banneret hung from a lance laid across its top: the lance painted in a spiral
    of gold and the tincture with a gilt knob at its butt and its coronel at its head, the cloth of a tincture
    under it with its light along the top and its shade along the foot, its foot dagged and fringed in gold. The
    lance and the dagged foot are pattern tiles, so a long label costs no more than a short one."""
    k = -1 if night else 0
    tinc = LINK_TINCTURES[seed % len(LINK_TINCTURES)]
    T = RAMP[tinc]
    base = p.layers["base"]
    for xy in [xy for xy in base if xy[1] >= 3 and 1 <= xy[0] < w - 1 and xy[1] <= 10]:
        del base[xy]
    for xy in [xy for xy in base if xy[1] in (1, 2, 11, 12)]:
        del base[xy]
    p.rect(1, 3, w - 2, 8, T[2 + k])
    p.hline(1, w - 1, 3, T[3 + k])
    p.hline(1, w - 1, 10, T[1 + k])
    p.vline(0, 3, 11, K)
    p.vline(w - 1, 3, 11, K)
    lid, fid = f"ln{tinc}{int(night)}", f"lf{tinc}{int(night)}"
    p.defs.append(f'<pattern id="{lid}" width="4" height="2" patternUnits="userSpaceOnUse">'
                  f'<path stroke="{G[5 + k]}" d="M0 .5h2"/><path stroke="{T[4 + k]}" d="M2 .5h2"/>'
                  f'<path stroke="{G[2 + k]}" d="M0 1.5h2"/><path stroke="{T[1 + k]}" d="M2 1.5h2"/></pattern>')
    p.shapes["base"].append(f'<rect y="1" width="{w}" height="2" fill="url(#{lid})"/>')
    p.defs.append(f'<pattern id="{fid}" x="1" y="11" width="4" height="2" patternUnits="userSpaceOnUse">'
                  f'<path stroke="{G[4 + k]}" d="M0 .5h1"/><path stroke="{T[1 + k]}" d="M1 .5h1"/>'
                  f'<path stroke="{G[3 + k]}" d="M2 .5h1"/><path stroke="{K}" d="M3 .5h1"/>'
                  f'<path stroke="{G[4 + k]}" d="M0 1.5h1"/><path stroke="{G[2 + k]}" d="M1 1.5h1"/></pattern>')
    p.shapes["base"].append(f'<rect x="1" y="11" width="{w - 2}" height="2" fill="url(#{fid})"/>')
    p.px(0, 0, G[6 + k])
    p.px(0, 1, G[4 + k])
    p.px(0, 2, G[2 + k])
    p.px(w - 1, 1, S[5 + k])
    p.px(w - 1, 2, S[3 + k])


# --------------------------------------------------------------------------- the elements
CARD_SHIELD = [     # the heater shield a card's icon is worked on: e its lit edge, T its field, d its shade
    "KKKKKKKKKKK",
    "KeTTTTTTTdK",
    "KeTTTTTTTdK",
    "KeTTTTTTTdK",
    "KeTTTTTTTdK",
    "KeTTTTTTTdK",
    "KeTTTTTTTdK",
    "KeTTTTTTTdK",
    "KeTTTTTTTdK",
    ".KeTTTTTdK.",
    ".KeTTTTTdK.",
    "..KeTTTdK..",
    "...KTTdK...",
    "....KKK....",
]


def silk_card(p: Pix, x, y, w, h, night: bool, seed: int, ink: str, face: str):
    """A schematic's card as a banner of painted silk: a gold cord laid all round its edge; at its head a band of
    its knight's tincture, its lower edge cut in small dags; on its face a heater shield of the tincture hung under
    the band, the card's icon worked on it in gold (the layout drew the icon in `ink`, which this takes up and works
    again on the shield); and a fold of shade along its foot."""
    k = -1 if night else 0
    T = RAMP[LINK_TINCTURES[seed % len(LINK_TINCTURES)]]
    icon_y = y + (h - 7) // 2
    icon = {(xx - x - 2, yy - icon_y) for yy in range(icon_y, icon_y + 7) for xx in range(x + 2, x + 9)
            if p.get(xx, yy) == ink}
    for (u, v) in icon:
        p.px(x + 2 + u, icon_y + v, face)
    for xx in range(x + 1, x + w - 1):
        p.px(xx, y + 1, T[3 + k])
        if (xx - x) % 4:
            p.px(xx, y + 2, T[2 + k] if (xx - x) % 4 != 3 else T[1 + k])
    sy = y + max(3, (h - len(CARD_SHIELD)) // 2)
    stamp(p, x + 2, sy, CARD_SHIELD, {"K": K, "e": T[4 + k], "T": T[3 + k], "d": T[2 + k]})
    for (u, v) in icon:
        p.px(x + 4 + u, sy + 1 + v, G[5 + k] if (u, v - 1) not in icon else G[3 + k] if (u, v + 1) in icon
             else G[4 + k])
    pid = cord_pattern(p, night)
    trim = p.layer("trim", z=0.1)
    for (rx, ry, rw, rh) in ((x, y, w, 1), (x, y + h - 1, w, 1), (x, y, 1, h), (x + w - 1, y, 1, h)):
        p.shapes[trim].append(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="url(#{pid})"/>')
    keep(p, {(xx, yy) for xx in range(x, x + w) for yy in (y, y + h - 1)})
    p.hline(x + 14, x + w - 1, y + h - 2, (CV[4] if not night else DU[3]))


def cord_wire(p: Pix, cells, night: bool):
    """A schematic's wire as a gold cord: its strands twisted, light and dark by turns along it, its shade along
    the row under a level run and the column beside an upright one, and a knot where it bends."""
    k = -1 if night else 0
    kinds: dict = {}
    for i, (x, y, d) in enumerate(cells):
        kinds.setdefault((x, y), set()).add(d)
        p.px(x, y, G[5 + k] if (i // 2) % 2 else G[3 + k])
        if d == "h":
            p.px(x, y + 1, G[1 + k])
        else:
            p.px(x + 1, y, G[1 + k])
    for (x, y), ds in kinds.items():
        if len(ds) == 2:
            for (dx, dy, t) in ((0, 0, 6), (-1, 0, 4), (1, 0, 3), (0, -1, 5), (0, 1, 2), (1, 1, 1)):
                p.px(x + dx, y + dy, G[max(0, t + k)])


def lance_bar(p: Pix, bx, base, bw, v, night: bool, i=0):
    """A week's commits as a tilting lance standing upright on the base line, `v` tall: its shaft painted in a
    spiral of its tincture and gold, lit on its left, narrowing to the coronel at its head, and the vamplate's
    cone round it a little way up from its butt."""
    k = -1 if night else 0
    T = RAMP[LINK_TINCTURES[i % len(LINK_TINCTURES)]]
    sw = max(2, bw - 2 if bw >= 6 else bw)
    sx = bx + (bw - sw) // 2
    top = base - v
    for y in range(top, base):
        f = (base - y) / max(1, v)
        nw = sw if f < 0.7 else max(2, sw - 1) if f < 0.88 else max(1, sw - 2)
        ox = sx + (sw - nw) // 2
        for xx in range(ox, ox + nw):
            band = ((y + (xx - ox)) // 2) % 2
            u = (xx - ox) / max(1, nw - 1)
            if band:
                c = G[5 + k] if u < 0.4 else G[3 + k]
            else:
                c = T[4 + k] if u < 0.4 else T[2 + k]
            p.px(xx, y, c)
    p.px(sx + sw // 2, top - 1, S[5 + k])
    if v >= 10 and bw >= 4:
        vy = base - max(4, v // 5)
        for j, dw in enumerate((0, 1, 1, 2)):
            for xx in range(bx - dw, bx + bw + dw):
                p.px(xx, vy - j, S[(5 if xx < bx + bw // 2 else 3) + k] if j < 3 else K)
        p.hline(bx - 2, bx + bw + 2, vy - 4, S[6 + k])
    for y in range(top, base):
        if p.get(bx - 1, y) is None:
            p.px(sx - 1, y, K)
        p.px(sx + sw, y, K)


def quintain_face(night: bool):
    """The colour of the quintain's target at (x, y) on a dial about (cx, cy) of radius r: a round shield painted
    gyronny of four, gules and argent by turns from the left, in pale tints by day and in shadow by night so every
    figure on it keeps its contrast. None off the shield."""
    gu, ar = (RAMP["gules"][6], A[6]) if not night else (RAMP["gules"][2], DU[3])

    def colour(x, y, cx, cy, r):
        dx, dy = x + 0.5 - cx, cy - (y + 0.5)
        if dy < -0.5 or math.hypot(dx, dy) >= r - 4.6:
            return None
        return ar if min(3, int(math.degrees(math.atan2(max(dy, 0), dx)) // 45)) % 2 else gu
    return colour


def quintain_ring(p: Pix, arc, night: bool):
    """The dial as the quintain's target: a round shield painted gyronny of four gules and argent (see
    `quintain_face`), bound in an iron rim bent over it between two dark edges, its gold rivets the dial's
    ticks."""
    from ...holidays.pixel import tube
    k = -1 if night else 0
    cx, cy, r = p.dial
    colour = quintain_face(night)
    for y in range(math.floor(cy - r), math.ceil(cy) + 1):
        for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
            c = colour(x, y, cx, cy, r)
            if c:
                p.px(x, y, c)

    def rim(s, o, lam, x, y):
        if abs(o) > 0.78:
            return K
        return S[5 + k] if lam > 0.62 else S[4 + k] if lam > 0.4 else S[3 + k] if lam > 0.2 else S[2 + k]
    tube(p, arc, 3.4, rim, outline=K)


def quintain_hand(p: Pix, night: bool, accent: str):
    """The dial's hand redrawn as a tilting lance laid from the quintain's pivot to the count, in place of the
    plain line the layout drew in `accent`: its shaft two pixels thick and painted in a spiral of gules and gold,
    its vamplate a steel cone across it a third of the way out, and the coronel's blunt crown at its head."""
    cx, cy, r = p.dial
    reach = r - 11
    hand = [(x, y) for (x, y), c in p.layers["base"].items() if c == accent
            and (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= reach ** 2]
    if not hand:
        return
    k = -1 if night else 0
    colour = quintain_face(night)
    for (x, y) in hand:
        c = colour(x, y, cx, cy, r)
        if c:
            p.px(x, y, c)
    far = max(hand, key=lambda q: (q[0] - cx) ** 2 + (q[1] - cy) ** 2)
    ux, uy = far[0] + 0.5 - (cx + 0.5), far[1] + 0.5 - (cy + 0.5)
    n = math.hypot(ux, uy) or 1
    ux, uy = ux / n, uy / n
    vx, vy = -uy, ux
    if vy > 0:
        vx, vy = -vx, -vy
    Gu = RAMP["gules"]
    length = reach + 1

    def at(t, o):
        return round(cx + 0.5 + ux * t + vx * o - 0.5), round(cy + 0.5 + uy * t + vy * o - 0.5)
    for i in range(3, round(length * 4)):
        t = i / 4
        band = int(t) // 3 % 2
        p.px(*at(t, 0.5), G[5 + k] if band else Gu[4 + k])
        p.px(*at(t, -0.5), G[3 + k] if band else Gu[2 + k])
    vt = length * 0.3
    for dt, half in ((0, 1.25), (1, 2), (2, 2.75), (3, 3.25)):
        for j in range(-round(half * 4), round(half * 4) + 1):
            o = j / 4
            edge = abs(o) > half - 0.6
            p.px(*at(vt + dt, o), K if dt == 3 and edge else S[5 + k] if o > 0.5 else S[4 + k] if o > -0.5
                 else S[2 + k])
    for j in range(-9, 10):
        o = j / 4
        p.px(*at(length, o), S[5 + k] if o > 0 else S[3 + k])
    for o in (-2, 0, 2):
        p.px(*at(length + 1.2, o), S[6 + k] if o >= 0 else S[4 + k])


def material(i, xx, yy, y0, y1, lift, night: bool) -> str:
    """The silks of the lists by turns: a pavilion's stripes of green and white, chequy gules and or, barry azure
    and white, lozengy purpure and or, the white of a tabard powdered with gold, and a tenne damask."""
    k = -1 if night else 0
    Gu, Az, P, Tn = RAMP["gules"], RAMP["azure"], RAMP["purpure"], RAMP["tenne"]
    kind = i % 6
    if kind == 0:
        c = V[3 + k] if (xx // 3) % 2 == 0 else A[5 + k]
    elif kind == 1:
        c = Gu[3 + k] if ((xx // 3) + (yy // 3)) % 2 == 0 else G[4 + k]
    elif kind == 2:
        c = Az[2 + k] if ((yy - y0) // 2) % 2 == 0 else A[5 + k]
    elif kind == 3:
        c = G[4 + k] if (abs((xx % 6) - 3) + abs(((yy - y0) % 6) - 3)) <= 1 else P[2 + k]
    elif kind == 4:
        c = G[3 + k] if (xx % 5 == 2 and (yy - y0) % 4 == 1) else A[5 + k]
    else:
        c = Tn[4 + k] if (xx + yy) % 4 == 0 else Tn[3 + k]
    try:
        return step(c, lift)
    except KeyError:
        return c


def cheque(q: Pix, ox, oy, night: bool, L="far"):
    """A cell of the herald's score cheque, 11 by 15, a numeral is painted in: parchment ruled in brown ink round
    its edge and across its head and its foot, where the herald marked each lance broken. It lies on a layer under
    the drawing's own, so its numeral, whatever its colour, is always painted over it."""
    paper_, rule_, lit = (CV[6], CV[2], C["white"]) if not night else (DU[5], DU[2], DU[6])
    for yy in range(15):
        for xx in range(11):
            c = paper_
            if xx in (0, 10) or yy in (0, 14):
                c = rule_
            elif yy in (2, 12):
                c = rule_ if xx % 2 else paper_
            elif xx == 1 or yy == 1:
                c = lit
            q.px(ox + xx, oy + yy, c, L)


def tilt_line(p: Pix, x0, x1, y, night: bool):
    """The time line as the tilt: an oak rail, lit along its top, over a strip of the host's white cloth with his
    green along its foot, up to today."""
    k = -1 if night else 0
    p.hline(x0, x1, y - 1, K)
    p.hline(x0, x1, y, WD[5 + k])
    p.hline(x0, x1, y + 1, WD[3 + k])
    p.hline(x0, x1, y + 2, A[4 + k])
    p.hline(x0, x1, y + 3, V[3 + k])


def release_pennon(p: Pix, x, gy, kind: str, night: bool, i=0):
    """A release on the tilt: a pennon of a tincture on a pole stood at the rail, a square banner for a big one,
    a small pennon for a patch, a pennon only outlined for one still to come, and a pavilion pitched for the
    repository's founding."""
    k = -1 if night else 0
    T = RAMP[LINK_TINCTURES[i % len(LINK_TINCTURES)]]
    if kind == "made":
        for yy in range(gy - 6, gy):
            w = (yy - (gy - 6)) + 1
            for xx in range(x - w // 2 - 1, x + w // 2 + 1):
                p.px(xx, yy, (V[3 + k] if (xx - x) % 2 else A[5 + k]))
        p.px(x, gy - 7, G[6 + k])
        p.px(x, gy - 1, DU[2])
        return
    h = 9 if kind in ("major", "next") else 12 if kind == "big" else 6
    for yy in range(gy - h, gy):
        p.px(x, yy, WD[4 + k])
    p.px(x, gy - h - 1, G[6 + k])
    if kind == "next":
        for (dx, dy) in ((1, 0), (2, 0), (3, 0), (4, 1), (3, 2), (2, 2), (1, 2), (1, 1)):
            p.px(x + dx, gy - h + dy, X["rule_day"] if not night else X["rule_night"])
        return
    if kind == "big":
        for dy in range(6):
            for dx in range(1, 7):
                p.px(x + dx, gy - h + dy, T[3 + k] if dy < 5 or dx % 2 else G[4 + k])
        for dy in range(5):
            p.px(x + 6, gy - h + dy, G[4 + k])
        return
    n = 5 if kind == "major" else 3
    for dx in range(1, n + 1):
        for dy in range(0, 3 if dx < n else 2):
            p.px(x + dx, gy - h + dy, T[3 + k] if dy < 2 else T[1 + k])


def today_helm(p: Pix, x, y, night: bool):
    """A crested great helm at today's end of the tilt, its foot on the rail."""
    crested_helm(p, x - 7, y - 17, "lion", night, "gules", "or", "S")


QSHIELD_S = [  # the bot's quintain's shield, 7 by 8
    "KKKKKKK",
    "KRrrWwK",
    "KRrrWwK",
    "KWWWrsK",
    "KWWWrsK",
    ".KWWrK.",
    "..KWK..",
    "...K...",
]


def knight_avatar(p: Pix, cx, cy, i, night: bool, bot=False):
    """A contributor as a crested great helm with its mantling, 19 wide and 20 tall about (cx, cy), in their own
    tinctures and with their own crest, by turns; a bot as the quintain, the wooden post the knights tilt at, its
    shield on its arm's long end and the sack of sand on its short end."""
    k = -1 if night else 0
    if bot:
        Gu = RAMP["gules"]
        pal = {"K": K, "R": Gu[4 + k], "r": Gu[3 + k], "s": Gu[2 + k], "W": A[6 + k], "w": A[4 + k],
               "b": CV[3 + k], "B": CV[5 + k], "q": CV[1 + k]}
        top = cy - 9
        post = cx + 1
        for y in range(top + 4, cy + 9):
            for dx, c in ((-1, K), (0, WD[5 + k]), (1, WD[3 + k]), (2, K)):
                p.px(post + dx, y, c)
        for xx in range(post - 5, post + 7):
            p.px(xx, cy + 8, K)
            p.px(xx, cy + 9, WD[4 + k] if xx < post + 1 else WD[2 + k])
        stamp(p, post - 1, top, [".KK.", "KIiK", "KiiK"], {"K": K, "I": S[5 + k], "i": S[3 + k]})
        for xx in range(cx - 7, cx + 9):
            p.px(xx, top + 3, K)
            p.px(xx, top + 4, WD[5 + k])
            p.px(xx, top + 5, WD[2 + k])
            p.px(xx, top + 6, K)
        p.vline(cx + 9, top + 4, top + 6, K)
        stamp(p, cx - 9, top + 2, QSHIELD_S, pal)
        for j in range(3):
            p.px(cx + 7, top + 7 + j, S[4 + k] if j % 2 else S[2 + k])
        stamp(p, cx + 5, top + 10, ["..K..", ".KbK.", "KbBbK", "KBbqK", "KbbqK", ".KqK."], pal)
        return
    crests = ("lion", "swan", "stag", "griffin", "boar")
    tincs = (("gules", "or"), ("azure", "argent"), ("vert", "or"), ("purpure", "argent"), ("sable", "or"))
    tinc, metal = tincs[i % len(tincs)]
    crested_helm(p, cx - 9, cy - 10, crests[i % len(crests)], night, tinc, metal, "M")


def silk_ribbon(p: Pix, x, y, w, h, night: bool, tail=4):
    """The lady's favour under the seal: her ribbon of blue silk, its edges gold, its ends falling either side cut
    in forks."""
    Az = RAMP["azure"]
    for j in range(h):
        for i in range(tail):
            c = Az[1] if j in (0, h - 1) else Az[2]
            if j == 0:
                c = G[4]
            drop = 1 if i >= 2 else 0
            if i == tail - 1 and j == h // 2:
                continue
            p.px(x - 1 - i, y + j + drop, c)
            p.px(x + w + i, y + j + drop, c)


TASSEL = [".n.", "nNn", ".n.", "nnn", "NnN", "n.n"]      # a gold tassel: its knob, its head and its fringe
FLEURON = ["..N..", ".NGg.", "N.G.g", "oNGgo", ".oGo."]      # a fleuron standing on the circlet's rim


def cushion(p: Pix, cx, cy, r0, r1, night: bool):
    """The tourney's prize round the seal: a plump cushion of crimson velvet under it, its top lit and its front
    in shade, piped in gold and tufted with gold buttons, a gold tassel hanging from each corner; and sitting on
    it about the seal's disc a gold circlet, lit on its upper left, set with a ruby, a sapphire and an emerald by
    turns, its fleurons standing upright along its upper rim as a crown's do."""
    k = -1 if night else 0
    Gu = RAMP["gules"]
    W, H, my = r1 + 4, 12, cy + 15
    for y in range(my - H - 1, my + H + 2):
        for x in range(cx - W - 1, cx + W + 2):
            dx, dy = (x + 0.5 - cx) / W, (y + 0.5 - my) / H
            e = dx ** 4 + dy ** 4
            if e > 1:
                continue
            if e > 0.8:
                c = G[4 + k] if dy < 0.2 and dx < 0.6 else G[2 + k]
            elif dy < 0.15:
                c = Gu[4 + k] if dy < -0.55 + 0.3 * abs(dx) else Gu[3 + k]
            else:
                c = Gu[2 + k] if dy < 0.6 else Gu[1 + k]
            p.px(x, y, c)
    for bx in (-0.62, 0.62):
        p.px(round(cx + bx * W), my - 4, G[5 + k])
        p.px(round(cx + bx * W) + 1, my - 3, G[2 + k])
    for (tx, ty) in ((cx - W + 1, my - H + 2), (cx + W - 3, my - H + 2), (cx - W, my + H - 2),
                     (cx + W - 2, my + H - 2)):
        stamp(p, tx, ty, TASSEL, {"n": G[3 + k], "N": G[5 + k]})
    rr = r0 + 1
    for y in range(math.floor(cy - rr) - 2, math.ceil(cy + rr) + 3):
        for x in range(math.floor(cx - rr) - 2, math.ceil(cx + rr) + 3):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            d = math.hypot(dx, dy)
            if rr - 1.2 <= d < rr + 1.0:
                lit = (-dx - dy) / max(d, 1.0)
                c = G[6 + k] if lit > 0.75 else G[5 + k] if lit > 0.2 else G[4 + k] if lit > -0.4 else G[2 + k]
                p.px(x, y, G[1] if d >= rr + 0.4 and lit < -0.2 else c)
    for i, ox in enumerate(range(-16, 17, 8)):
        top = math.floor(cy - math.sqrt(max(0.0, (rr + 0.6) ** 2 - ox ** 2)))
        stamp(p, cx + ox - 2, top - 5, FLEURON, {"N": G[6 + k], "G": G[4 + k], "g": G[2 + k], "o": G[1]})
    gems = (Gu[4 + k], RAMP["azure"][4 + k], V[4 + k])
    for i, a in enumerate(range(15, 360, 30)):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        gx, gy = math.floor(cx + rr * ca - 0.5), math.floor(cy + rr * sa - 0.5)
        c = gems[i % 3]
        for (ox, oy) in ((0, 0), (1, 0), (0, 1), (1, 1)):
            p.px(gx + ox, gy + oy, c)
        p.px(gx, gy, C["white"])


ROSE = [".rr.", "rRrr", "rrRr", ".gg."]


def rose(p: Pix, x, y, night: bool):
    """A white rose, the lady's token, pinned to the front of the prize's cushion at the seal's foot."""
    k = -1 if night else 0
    stamp(p, x, y, ROSE, {"r": A[5 + k], "R": A[6 + k], "g": V[3 + k]})


def proclamation(p: Pix, night: bool):
    """The herald's proclamation board over the whole card: a panel of parchment in an oak frame, the frame lit
    along its top and left and shaded along its foot and right, hung between the striped poles with a slim valance
    over it, as a herald set his notice up at the lists."""
    k = -1 if night else 0
    w, h = p.w, p.h
    paper(p, night, uid="pl")
    frame(p, night, uid="plf")
    for x in range(5, w - 5):
        p.px(x, 7, WD[5 + k])
        p.px(x, h - 5, WD[1 + k])
    for y in range(7, h - 4):
        p.px(5, y, WD[5 + k])
        p.px(w - 6, y, WD[1 + k])
    for (bx, by) in ((6, 8), (w - 8, 8), (6, h - 7), (w - 8, h - 7)):
        p.px(bx, by, S[5 + k])
        p.px(bx + 1, by + 1, S[2 + k])


LIST_POST = 16      # the counter-lists' posts stand this far apart


def counter_lists(p: Pix, x0, x1, y, night: bool, seed=0, L="base"):
    """The counter-lists along a rule at row y: the low oak fence round the lists, two rails on posts set every
    sixteen units with their heads capped in gilt, laid as a pattern only where no word lies within two units, each
    run beginning and ending at a post."""
    k = -1 if night else 0
    ok = [p.clear_of_words(x - 2, y - 8, x + 3, y + 2) for x in range(x0, x1)]
    runs, start = [], None
    for i, good in enumerate(ok + [False]):
        if good and start is None:
            start = i
        elif not good and start is not None:
            a = -(-(x0 + start + 1) // LIST_POST) * LIST_POST
            b = ((x0 + i - 3) // LIST_POST) * LIST_POST + 2
            if b - a >= LIST_POST + 2:
                runs.append((a, b))
            start = None
    if not runs:
        return
    pid = f"cl{'n' if night else 'd'}{y}"
    if ("lists", pid) not in p.syms:
        cols: dict = {}
        for r in range(6):
            for x in range(LIST_POST):
                if x < 2:
                    c = (G[5 + k], G[3 + k])[x] if r == 0 else (WD[4 + k], WD[2 + k])[x]
                else:
                    c = {1: WD[5 + k], 2: WD[3 + k], 4: WD[4 + k], 5: WD[2 + k]}.get(r)
                if c:
                    cols.setdefault(c, {}).setdefault(r, []).append(x)
        p.defs.append(f'<pattern id="{pid}" y="{y - 6}" width="{LIST_POST}" height="6" patternUnits="userSpaceOnUse">'
                      f'{paths(cols)}</pattern>')
        p.syms[("lists", pid)] = pid
    for a, b in runs:
        p.shapes[L].append(f'<rect x="{a}" y="{y - 6}" width="{b - a}" height="6" fill="url(#{pid})"/>')
        keep(p, {(x, y - 6 + r) for x in range(a, b) for r in range(6) if r != 3 or (x - a) % LIST_POST < 2})


def scale_lance(p: Pix, x0, y0, w, h, period=5, L="base"):
    """The graphic scale's bar as a tilting lance laid along it: painted gules and gold by turns, a colour every
    `period` pixels, lit along its top and shaded along its foot."""
    night = getattr(p, "night", False)
    k = -1 if night else 0
    Gu = RAMP["gules"]
    for x in range(x0, x0 + w):
        red = ((x - x0) // period) % 2 == 0
        for y in range(y0, y0 + h):
            j = (y - y0) / max(1, h - 1)
            t = 1 if j < 0.3 else 0 if j < 0.75 else -1
            p.px(x, y, (Gu[3 + t + k] if red else G[4 + t + k]), L)
