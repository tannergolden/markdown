# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The pixel canvas every holiday set draws on, and the SVG it writes.

Every mark lands on a grid of `u`-pixel squares. A drawing is kept as layers
of pixels, drawn low to high: halos behind everything, the stars that
twinkle, the fireworks, the drawing, light pooled on the ground, the flames
and their glows, fog, then whatever flies. A layer holds solid and
see-through pixels, shapes (the big halos) and uses of symbols drawn once in
`<defs>`. A few moving things are raw markup with a still twin.

What moves moves in discrete steps, so a pixel is either lit or not: lights
twinkle, flicker or blink on three staggered phases, a ghost bobs, fog
drifts, a firework is a run of frames each shown for its moment of the loop,
and what flies steps round a path. The still file, for reduced motion, keeps
one frame of each and moves nothing.

Letters are set in the two bitmap faces of `type`, each glyph drawn once as
one path and reused, stroked in the colour it is set in. A set may paint its
titles with a `Paint` and finish them with effects of its own; the canvas
knows nothing about any one holiday.
"""
from __future__ import annotations

import html
import math
import random
from dataclasses import dataclass
from typing import Callable

from .type import FONTS, fold, measure as _measure, wrap as _wrap


def num(v: float) -> str:
    """A coordinate as short as it can be written: two decimals at most, no leading zero."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s.replace("0.", ".", 1) if s.startswith("0.") else s.replace("-0.", "-.", 1)


# How each kind of blinking repeats: opacity values, their key times, the loop's length in seconds and
# how far apart the three phases start. All discrete, so a pixel is either lit or not.
BLINKS = {
    "twinkle": ("1;.28;1", "0;.5;1", 1.5, 0.5),
    "flicker": ("1;.62;.94;.5;1;.8", "0;.16;.3;.47;.62;.82", 1.8, 0.61),
    "blink": ("1;0;1", "0;.9;.95", 5.2, 1.9),
}


@dataclass(frozen=True)
class Paint:
    """How a set paints its titles when their letters take more than one colour.

    `fill(r, c, scale, night)` is the colour at row `r` and column `c` of a
    letter, counted in canvas pixels from its top-left. With `period` 0 the
    letter is painted in bands, one colour for each row of the face, and only
    `r` matters; otherwise the paint is a tile `period` canvas pixels wide,
    repeated along the letter. `variant(mid)`, when given, picks a variant for
    each letter from where its middle falls along the line, 0 to 1, and `fill`
    is then called with it as a fifth argument.
    """
    name: str
    fill: Callable
    period: int = 0
    variant: Callable | None = None


class Pix:
    """A drawing on a grid of `u`-pixel squares, kept as layers of pixels and written as one SVG."""
    Z = {"haze": -20, "tb": -15, "fw": -12, "far": -10, "base": 0, "pool": 3, "fl": 8, "tw": 10, "fog": 14,
         "bob": 12, "near": 20}

    def __init__(self, w: int, h: int, u: int = 2, lite: bool = False):
        self.w, self.h, self.u = int(w), int(h), u
        self.lite = lite             # drawn lighter, to fit a budget: titles without their glow or finish
        self.layers: dict[str, dict] = {}
        self.meta: dict[str, list] = {}
        self.uses: dict[str, list] = {}
        self.shapes: dict[str, list] = {}
        self.defs: list[str] = []
        self.syms: dict = {}
        self.under: list[str] = []   # raw SVG in unit space, drawn before the pixels
        self.raws: list = []         # (z, order, moving markup, still markup)
        self.lamps: list = []        # flames and bulbs whose light falls on what stands near them
        self.words: list = []        # (x0, y0, x1, y1) of every line of text set, so nothing lies on it
        self._n = 0
        self.layer("base")
        self.layer("haze")

    # ---- layers
    def layer(self, name: str, anim: tuple | None = None, z: float | None = None) -> str:
        if name not in self.layers:
            self.layers[name], self.uses[name], self.shapes[name] = {}, [], []
            key = name.rstrip("0123456789+~")
            self.meta[name] = [self.Z.get(key, 0) if z is None else z, self._n, None]
            self._n += 1
        if anim:
            self.meta[name][2] = anim
        return name

    def twinkle(self, phase: int, back: bool = False) -> str:
        """One of three twinkling layers: the lights are split between them so they never all go dark.
        `back` puts the twinkling behind the drawing, for the stars in the sky."""
        if back:
            return self.layer(f"tb{phase % 3}", ("twinkle", phase % 3), z=-15)
        return self.layer(f"tw{phase % 3}", ("twinkle", phase % 3))

    def flicker(self, phase: int, back: bool = False) -> str:
        """One of three flickering layers, for a flame and the face it lights. `back` puts the flicker
        behind the drawing, for the glow a lantern throws around itself."""
        if back:
            return self.layer(f"fb{phase % 3}", ("flicker", phase % 3), z=-5)
        return self.layer(f"fl{phase % 3}", ("flicker", phase % 3))

    def blink(self, phase: int = 0, z: float = 1) -> str:
        """A light that goes out now and then: eyes in the dark, a firefly between flashes."""
        return self.layer(f"bl{phase % 3}", ("blink", phase % 3), z=z)

    def seq(self, name: str, t0: float, t1: float, dur: float, keep: bool = False, z: float = -12) -> str:
        """A frame of something that happens in turn, shown from `t0` to `t1` of a loop `dur` seconds
        long and hidden the rest of the time. The still file keeps only the frames marked `keep`."""
        return self.layer(name, ("seq", t0, t1, dur, keep), z=z)

    def _over(self, L: str) -> str:
        """The see-through layer just above `L`, for light laid over its solid pixels."""
        name = L + "+"
        if name not in self.layers:
            self.layer(name, self.meta[L][2], z=self.meta[L][0] + 0.5)
        return name

    def raw(self, z: float, moving: str, still: str):
        """Markup of its own, placed among the layers at depth `z`: `still` stands in for `moving`
        in the reduced-motion file."""
        self.raws.append((z, self._n, moving, still))
        self._n += 1

    # ---- pixels
    def px(self, x, y, c, L="base"):
        if c is None:
            return
        if ":" in c:
            col, a = c.split(":")
            self.apx(x, y, col, float(a), L)
            return
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            if L not in self.layers:
                self.layer(L)
            self.layers[L][(x, y)] = c

    def apx(self, x, y, col, a, L="haze"):
        """A see-through pixel. Over a solid one it goes on the layer's overlay, so the colour stays a
        token and the light is laid on top; where one of its own colour lies already, the two add up."""
        x, y = int(x), int(y)
        if not (0 <= x < self.w and 0 <= y < self.h) or a <= 0:
            return
        if L not in self.layers:
            self.layer(L)
        old = self.layers[L].get((x, y))
        if old and ":" not in old:
            L = self._over(L)
            old = self.layers[L].get((x, y))
        if old:
            c0, a0 = old.split(":")
            if c0 == col:
                a = 1 - (1 - float(a0)) * (1 - a)
            elif float(a0) >= a:
                return
        a = min(0.92, round(a * 25) / 25)
        if a > 0:
            self.layers[L][(x, y)] = f"{col}:{a:g}"

    def get(self, x, y, L="base"):
        return self.layers[L].get((int(x), int(y))) if L in self.layers else None

    def rect(self, x, y, w, h, c, L="base"):
        for yy in range(int(y), int(y + h)):
            for xx in range(int(x), int(x + w)):
                self.px(xx, yy, c, L)

    def hline(self, x0, x1, y, c, L="base"):
        self.rect(x0, y, x1 - x0, 1, c, L)

    def vline(self, x, y0, y1, c, L="base"):
        self.rect(x, y0, 1, y1 - y0, c, L)

    def box(self, x, y, w, h, c, L="base", notch=False):
        """A one-pixel outline, its corners left open when notched."""
        for xx in range(x, x + w):
            for yy in (y, y + h - 1):
                if not notch or xx not in (x, x + w - 1):
                    self.px(xx, yy, c, L)
        for yy in range(y + 1, y + h - 1):
            self.px(x, yy, c, L)
            self.px(x + w - 1, yy, c, L)

    def bevel(self, x, y, w, h, light, dark, L="base"):
        """A raised edge: the top and left catch the light, the bottom and right fall into shade."""
        self.hline(x, x + w - 1, y, light, L)
        self.vline(x, y, y + h - 1, light, L)
        self.hline(x + 1, x + w, y + h - 1, dark, L)
        self.vline(x + w - 1, y + 1, y + h, dark, L)

    def dashed(self, x0, y0, x1, y1, colors, dash=3, L="base"):
        """A dashed rectangle whose dashes cycle through `colors`."""
        pts = [(x, y0) for x in range(x0, x1)] + [(x1 - 1, y) for y in range(y0 + 1, y1)] + \
              [(x, y1 - 1) for x in range(x1 - 2, x0 - 1, -1)] + [(x0, y) for y in range(y1 - 2, y0, -1)]
        for i, (x, y) in enumerate(pts):
            self.px(x, y, colors[(i // dash) % len(colors)], L)

    def sprite(self, x, y, art, pal, s=1, L="base", flip=False, reuse=False):
        """Pixel art from rows of characters, each looked up in `pal`. `reuse` draws it once in <defs>
        and places it with <use>, for a sprite that appears again and again; it is then drawn over
        everything else on its layer, so only a sprite nothing is later drawn over should ask for it."""
        rows = [r[::-1] if flip else r for r in art]
        if reuse and s == 1:
            key = ("sprite", tuple(rows), tuple(sorted((k, v) for k, v in pal.items() if v)))
            if key not in self.syms:
                self.symbol(key, {(i, j): pal[ch] for j, r in enumerate(rows) for i, ch in enumerate(r) if pal.get(ch)})
            self.use(key, x, y, L)
            return
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                c = pal.get(ch)
                if c:
                    self.rect(x + i * s, y + j * s, s, s, c, L)

    # ---- symbols: drawn once in <defs>, placed with <use>
    def symbol(self, key, cells: dict | None = None, shapes: str = "", mono: bool = False) -> str:
        """Keep a drawing once: `cells` maps (dx, dy) to a colour, `shapes` is raw SVG drawn under them.
        A `mono` symbol is one path with no colour of its own; it takes the stroke of where it is used."""
        if key in self.syms:
            return self.syms[key]
        sid = f"q{len(self.syms)}"
        if mono:
            rows = {}
            for (x, y) in cells:
                rows.setdefault(y, []).append(x)
            self.defs.append(f'<path id="{sid}" d="{self._d(rows)}"/>')
        else:
            self.defs.append(f'<g id="{sid}">{shapes}{self._paths(cells or {})}</g>')
        self.syms[key] = sid
        return sid

    def use(self, key, x, y, L="base", stroke=None, scale=1):
        if L not in self.layers:
            self.layer(L)
        self.uses[L].append((stroke, self.syms[key], x, y, scale))

    def stamp(self, key, draw, x, y, pad=24):
        """Draw a thing once and place it as often as it appears: `draw(q, ox, oy)` draws it on a scratch
        canvas with its origin at (ox, oy). Each of its layers is kept as one symbol and placed here at
        (x, y) on the layer of the same name, so its flame still flickers and its glow still glows."""
        k = ("stamp", key)
        if k not in self.syms:
            q = Pix(2 * pad, 2 * pad)
            draw(q, pad, pad)
            names = []
            for name in q.layers:
                cells, shapes = q.layers[name], q.shapes[name]
                if q.uses[name]:
                    raise ValueError("a stamp is drawn in pixels and shapes only")
                if not cells and not shapes:
                    continue
                under = f'<g transform="translate(-{pad} -{pad})">{"".join(shapes)}</g>' if shapes else ""
                self.symbol((k, name), {(cx - pad, cy - pad): c for (cx, cy), c in cells.items()}, shapes=under)
                names.append((name, q.meta[name][2], q.meta[name][0]))
            self.syms[k] = names
        for name, anim, z in self.syms[k]:
            if name not in self.layers:
                self.layer(name, anim, z=z)
            self.use((k, name), x, y, name)

    def fly(self, frames: list, path: list, dur: float, z: float = 16, flap: float = 0.36):
        """Something that flies: `frames` are symbol keys shown in turn (wings up, wings down), `path`
        the (x, y) it steps through, one step at a time, round and round. The still file shows the
        first frame at the path's first point."""
        ids = [self.syms[f] for f in frames]
        steps = ";".join(f"{x} {y}" for x, y in path)
        n = len(ids)
        uses = []
        for i, sid in enumerate(ids):
            vals = ";".join("1" if j == i else "0" for j in range(n))
            hidden = ' opacity="0"' if i else ""
            uses.append(f'<use href="#{sid}"{hidden}><animate attributeName="opacity" '
                        f'values="{vals}" dur="{num(flap * n)}s" repeatCount="indefinite" calcMode="discrete"/></use>')
        moving = (f'<g>{"".join(uses)}<animateTransform attributeName="transform" type="translate" values="{steps}" '
                  f'dur="{num(dur)}s" repeatCount="indefinite" calcMode="discrete"/></g>')
        x0, y0 = path[0]
        self.raw(z, moving, f'<use href="#{ids[0]}" x="{x0}" y="{y0}"/>')

    # ---- light
    def halo(self, cx, cy, rx, ry, col, alphas=(0.06, 0.11, 0.17), L="haze", only=None, shape=None):
        """A stepped glow: rings of one light, stronger toward the middle. A small glow, or one laid
        only on certain pixels (`only`, a set of colours on the base layer), is drawn in pixels; a big
        one as stacked ellipses, each ring's opacity chosen so the stack reads as the same steps."""
        n = len(alphas)
        if shape is None:
            shape = only is None and max(rx, ry) > 6
        if shape:
            prev = 0.0
            for k, a in enumerate(alphas):
                f = (n - k) / n
                o = 1 - (1 - a) / (1 - prev)
                prev = a
                if L not in self.layers:
                    self.layer(L)
                self.shapes[L].append(f'<ellipse cx="{num(cx)}" cy="{num(cy)}" rx="{num(rx * f)}" ry="{num(ry * f)}" '
                                      f'fill="{col}" fill-opacity="{num(o)}"/>')
            return
        base = self.layers["base"]
        for y in range(math.floor(cy - ry), math.ceil(cy + ry) + 1):
            for x in range(math.floor(cx - rx), math.ceil(cx + rx) + 1):
                d = math.hypot((x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry)
                if d >= 1:
                    continue
                if only is not None and base.get((x, y)) not in only:
                    continue
                self.apx(x, y, col, alphas[min(n - 1, int((1 - d) * n))], L)

    # ---- text
    @staticmethod
    def measure(s, font="57", scale=1, track=1) -> int:
        return _measure(s, font, scale, track)

    @staticmethod
    def wrap(s, maxw, font="57", scale=1, track=1) -> list[str]:
        return _wrap(s, maxw, font, scale, track)

    @staticmethod
    def _cells(x, y, s, font, scale, track):
        """Every canvas pixel `s` inks when set with its top-left at (x, y), and its width."""
        glyphs, _, space = FONTS[font]
        cells = set()
        cx = x
        for ch in fold(s, font):
            if ch == " ":
                cx += (space + track) * scale
                continue
            g = glyphs[ch]
            for r, cols in enumerate(g[1]):
                for col in cols:
                    for dy in range(scale):
                        for dx in range(scale):
                            cells.add((cx + col * scale + dx, y + r * scale + dy))
            cx += (g[0] + track) * scale
        return cells, cx - x - track * scale

    def text(self, x, y, s, c, font="57", scale=1, L="base", track=1, **kw):
        """Set a line of text (see `_text`) and remember the box it takes, a pixel all round."""
        s = fold(s, font)
        w = self._text(x, y, s, c, font, scale, L, track, **kw)
        glyphs = FONTS[font][0]
        rows = max(len(glyphs[ch][1]) for ch in s if ch != " ") if s.strip() else 0
        self.words.append((x - 1, y - 1, x + w + 1, y + rows * scale + 1))
        return w

    def clear_of_words(self, x0, y0, x1, y1) -> bool:
        """Whether the box from (x0, y0) to (x1, y1), ends excluded, touches no text."""
        return not any(x0 < b[2] and b[0] < x1 and y0 < b[3] and b[1] < y1 for b in self.words)

    def _text(self, x, y, s, c, font="57", scale=1, L="base", track=1, shadow=None, paint=None, bevel=None,
              glow=None, night=False, outline=None, finish=None):
        """Set `s` with its top-left at (x, y); returns the width.

        `shadow` is drawn half a font pixel down-right, `outline` a pixel round
        every letter, `bevel` a (light, dark) pair that lights the left edges and
        shades the foot, and `glow` a (colour, alphas) halo stepped out from the
        letters a pixel a ring, outermost first. `paint` paints the letters with
        a set's `Paint` instead of one colour. `finish(p, cells, scale, layer,
        rnd, y)` lays a set's own effect over the letters' pixels, like slime.
        Plain text is set from glyphs drawn once and reused, as the kits set theirs.
        """
        if self.lite:
            glow = finish = None
        glyphs, _, space = FONTS[font]
        placed, cx = [], x
        for ch in s:
            if ch == " ":
                cx += (space + track) * scale
                continue
            g = glyphs[ch]
            key = ("glyph", font, ch)
            if key not in self.syms:
                self.symbol(key, {(col, r): 1 for r, cols in enumerate(g[1]) for col in cols}, mono=True)
            placed.append((key, cx))
            cx += (g[0] + track) * scale
        w = cx - x - track * scale
        if not (shadow or paint or bevel or glow or outline or finish):
            for key, gx in placed:
                self.use(key, gx, y, L, stroke=c, scale=scale)
            return w
        strokes = {}
        if paint:
            for key, gx in placed:
                variant = None
                if paint.variant:
                    variant = paint.variant((gx + glyphs[key[2]][0] * scale / 2 - x) / max(1, w))
                strokes[gx] = f"url(#{self._pattern(paint, scale, night, variant)})"
        cells = self._cells(x, y, s, font, scale, track)[0] if (bevel or finish) else set()
        off = max(1, scale // 2)
        if shadow:
            for key, gx in placed:
                self.use(key, gx + off, y + off, L, stroke=shadow, scale=scale)
        if outline:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                for key, gx in placed:
                    self.use(key, gx + dx, y + dy, L, stroke=outline, scale=scale)
        if glow:
            self._glow(placed, y, scale, *glow)
        for key, gx in placed:
            self.use(key, gx, y, L, stroke=strokes.get(gx, c), scale=scale)
        top = self.layer(L + "~", self.meta[L][2] if L in self.meta else None,
                         z=(self.meta[L][0] if L in self.meta else 0) + 0.3)
        if bevel and scale >= 3:
            light, dark = bevel
            for (gx, gy) in cells:
                if (gx, gy + 1) not in cells:
                    self.px(gx, gy, dark, top)
                elif (gx - 1, gy) not in cells:
                    self.px(gx, gy, light, top)
        if finish:
            finish(self, cells, scale, top, random.Random(len(s) * 7 + x * 3 + y), y)
        return w

    def _glow(self, placed, y, scale, col, alphas):
        """A halo round each letter, a ring a pixel, the outermost faintest: each ring a letter's rows as
        strokes a little longer and wider than the letter's own, drawn once and reused."""
        n = len(alphas)
        for ring, a in enumerate(alphas):
            d = (n - ring) / scale
            for key, gx in placed:
                gkey = ("glow", key, scale, n - ring)
                if gkey not in self.syms:
                    rows = FONTS[key[1]][0][key[2]][1]
                    parts, at = [], None
                    for r, cols in enumerate(rows):
                        runs, start, prev = [], None, None
                        for cc in sorted(cols):
                            if prev is not None and cc == prev + 1:
                                prev = cc
                                continue
                            if prev is not None:
                                runs.append((start, prev - start + 1))
                            start = prev = cc
                        if prev is not None:
                            runs.append((start, prev - start + 1))
                        for (rx, rw) in runs:
                            sx, sy = rx - d, r + 0.5
                            parts.append(f"M{num(sx)} {num(sy)}h{num(rw + 2 * d)}" if at is None
                                         else f"m{num(sx - at[0])} {num(sy - at[1])}h{num(rw + 2 * d)}")
                            at = (sx + rw + 2 * d, sy)
                    sid = f"q{len(self.syms)}"
                    self.defs.append(f'<path id="{sid}" stroke-width="{num(1 + 2 * d)}" d="{"".join(parts)}"/>')
                    self.syms[gkey] = sid
                self.use(gkey, gx, y, "haze", stroke=f"{col}:{a:g}", scale=scale)

    def _pattern(self, paint: Paint, scale: int, night: bool, variant=None) -> str:
        """A `Paint` as a pattern a title's letters are stroked with, drawn once a file for each size of
        letter (and each variant). A letter's path is drawn in its face's units, so the tile is set in
        them too and starts at each letter's top-left. The tile is made of filled shapes: a browser paints
        thin strokes inside a pattern poorly when the file asks for crisp edges."""
        tail = "" if variant is None else str(variant)
        pid = f"pa{paint.name}{scale}{'n' if night else 'd'}{tail}"
        if ("pattern", pid) in self.syms:
            return pid

        def fill(r, c):
            return paint.fill(r, c, scale, night) if variant is None else paint.fill(r, c, scale, night, variant)

        rects: dict = {}
        if not paint.period:
            for band in range(7):
                rects.setdefault(fill(band * scale, 0), []).append(f"M0 {band}h4v1h-4z")
            body = "".join(f'<path fill="{col}" d="{"".join(ds)}"/>' for col, ds in rects.items())
            self.defs.append(f'<pattern id="{pid}" width="4" height="7" patternUnits="userSpaceOnUse">{body}</pattern>')
        else:
            period, rows = paint.period, {}
            for r in range(7 * scale):     # each row's runs of one colour, then rows with the same runs merged
                runs, cc = [], 0
                while cc < period:
                    col = fill(r, cc)
                    e = cc
                    while e < period and fill(r, e) == col:
                        e += 1
                    runs.append((col, cc, e - cc))
                    cc = e
                rows[r] = tuple(runs)
            r = 0
            while r < 7 * scale:
                e = r
                while e < 7 * scale and rows[e] == rows[r]:
                    e += 1
                for (col, cc, wd) in rows[r]:
                    rects.setdefault(col, []).append(f"M{cc} {r}h{wd}v{e - r}h-{wd}z")
                r = e
            body = "".join(f'<path fill="{col}" d="{"".join(ds)}"/>' for col, ds in rects.items())
            self.defs.append(f'<pattern id="{pid}" width="{num(period / scale)}" height="7" '
                             f'patternUnits="userSpaceOnUse"><g transform="scale({num(1 / scale)})">{body}</g></pattern>')
        self.syms[("pattern", pid)] = pid
        return pid

    def vtext(self, x, y, s, c, L="base"):
        """Small capitals turned a quarter to read upward, their foot at (x, y + length): a
        dimension's figure beside a vertical dimension line, the way a drawing sets it."""
        glyphs, _, space = FONTS["35"]
        s = fold(s, "35")
        cy = y + self.measure(s, "35") - 1
        for ch in s:
            if ch == " ":
                cy -= space + 1
                continue
            g = glyphs[ch]
            for r, cols in enumerate(g[1]):
                for col in cols:
                    self.px(x + r, cy - col, c, L)
            cy -= g[0] + 1
        self.words.append((x - 1, y - 1, x + 6, y + self.measure(s, "35") + 1))

    # ---- output
    @staticmethod
    def _d(rows: dict) -> str:
        """Path data for pixels of one colour, {y: [x, ...]}. A column of lone pixels, two or more
        tall, is one vertical stroke down the middle of its column; everything else is a horizontal
        stroke along the middle of its row. Every move after the first is relative to where the
        last stroke ended, so the numbers stay small."""
        cells = {(x, y) for y, xs in rows.items() for x in xs}
        lone = {(x, y) for (x, y) in cells if (x - 1, y) not in cells and (x + 1, y) not in cells}
        vertical, used = [], set()
        for (x, y) in sorted(lone, key=lambda q: (q[0], q[1])):
            if (x, y) in used or (x, y - 1) in lone:
                continue
            h = 1
            while (x, y + h) in lone:
                h += 1
            if h >= 2:
                vertical.append((y, x, h))
                used.update((x, y + i) for i in range(h))
        strokes = []
        left = {}
        for (x, y) in cells - used:
            left.setdefault(y, []).append(x)
        for y, xs in left.items():
            xs.sort()
            start = prev = xs[0]
            for x in xs[1:]:
                if x == prev + 1:
                    prev = x
                    continue
                strokes.append((y, start, "h", prev - start + 1))
                start = prev = x
            strokes.append((y, start, "h", prev - start + 1))
        strokes += [(y, x, "v", h) for (y, x, h) in vertical]
        strokes.sort(key=lambda s: (s[0], s[1]))
        out, at = [], None
        for (y, x, kind, n) in strokes:
            sx, sy = (x, y + 0.5) if kind == "h" else (x + 0.5, y)
            if at is None:
                out.append(f"M{num(sx)} {num(sy)}{kind}{n}")
            else:
                out.append(f"m{num(sx - at[0])} {num(sy - at[1])}{kind}{n}")
            at = (sx + n, sy) if kind == "h" else (sx, sy + n)
        return "".join(out).replace(" -", "-")

    def _paths(self, pix: dict) -> str:
        by = {}
        for (x, y), c in pix.items():
            by.setdefault(c, {}).setdefault(y, []).append(x)
        out = []
        for c, rows in sorted(by.items()):
            if ":" in c:
                col, a = c.split(":")
                out.append(f'<path stroke="{col}" stroke-opacity="{num(float(a))}" d="{self._d(rows)}"/>')
            else:
                out.append(f'<path stroke="{c}" d="{self._d(rows)}"/>')
        return "".join(out)

    @staticmethod
    def _uses(uses: list) -> str:
        by = {}
        for stroke, sid, x, y, scale in uses:
            by.setdefault(stroke, []).append((y, x, sid, scale))
        out = []
        for stroke, us in by.items():
            parts, rows = [], {}
            for (y, x, sid, scale) in us:
                if scale == 1:
                    rows.setdefault(y, []).append((x, sid))
                else:
                    parts.append(f'<use href="#{sid}" transform="translate({num(x)} {num(y)}) scale({scale})"/>')
            for y, row in rows.items():
                if len(row) >= 3:   # a line of letters shares its row: one translate, then x alone
                    inner = "".join(f'<use href="#{sid}" x="{num(x)}"/>' for x, sid in row)
                    parts.append(f'<g transform="translate(0 {num(y)})">{inner}</g>')
                else:
                    parts += [f'<use href="#{sid}" x="{num(x)}" y="{num(y)}"/>' for x, sid in row]
            if stroke and ":" in stroke and not stroke.startswith("url("):
                col, a = stroke.split(":")
                out.append(f'<g stroke="{col}" stroke-opacity="{num(float(a))}">{"".join(parts)}</g>')
            else:
                out.append(f'<g stroke="{stroke}">{"".join(parts)}</g>' if stroke else "".join(parts))
        return "".join(out)

    def svg(self, title: str, desc: str, still: bool = False, stamp: str = "") -> str:
        """The finished file. `still` is the reduced-motion drawing: nothing twinkles, flickers or blinks,
        a run of frames holds the one it keeps, fog holds where it lies and what flies rests where its
        path begins."""
        W, H = self.w * self.u, self.h * self.u
        items = [(self.meta[n][0], self.meta[n][1], "layer", n) for n in self.layers]
        items += [(z, o, "raw", (mv, st)) for (z, o, mv, st) in self.raws]
        body, defs = [], list(self.defs)
        for z, _, kind, what in sorted(items, key=lambda t: (t[0], t[1])):
            if kind == "raw":
                body.append(what[1] if still else what[0])
                continue
            name = what
            anim = self.meta[name][2]
            content = "".join(self.shapes[name]) + self._paths(self.layers[name]) + self._uses(self.uses[name])
            if not content:
                continue
            if anim and anim[0] == "seq":
                _, t0, t1, dur, keep = anim
                if still:
                    if keep:
                        body.append(content)
                    continue
                if t0 <= 0:
                    vals, kt = "1;0", f"0;{num(t1)}"
                elif t1 >= 1:
                    vals, kt = "0;1", f"0;{num(t0)}"
                else:
                    vals, kt = "0;1;0", f"0;{num(t0)};{num(t1)}"
                body.append(f'<g opacity="0">{content}<animate attributeName="opacity" values="{vals}" keyTimes="{kt}" '
                            f'dur="{num(dur)}s" repeatCount="indefinite" calcMode="discrete"/></g>')
            elif anim and anim[0] in BLINKS and not still:
                vals, kt, dur, gap = BLINKS[anim[0]]
                body.append(f'<g>{content}<animate attributeName="opacity" values="{vals}" keyTimes="{kt}" '
                            f'dur="{dur:g}s" begin="{num(anim[1] * gap)}s" repeatCount="indefinite" calcMode="discrete"/></g>')
            elif anim and anim[0] == "bob" and not still:
                _, lift, dur = anim
                vals = ";".join(f"0 {-v}" for v in lift)
                body.append(f'<g>{content}<animateTransform attributeName="transform" type="translate" values="{vals}" '
                            f'dur="{num(dur)}s" repeatCount="indefinite" calcMode="discrete"/></g>')
            elif anim and anim[0] == "drift":
                _, x0, y0, x1, y1, period, cid, speed = anim
                if still:
                    body.append(f'<g clip-path="url(#{cid})">{content}</g>')
                else:
                    gid = f"{cid}g"
                    defs.append(f'<g id="{gid}">{content}</g>')
                    steps = ";".join(f"{i} 0" for i in range(period))
                    body.append(f'<g clip-path="url(#{cid})"><g><use href="#{gid}"/><use href="#{gid}" x="-{period}"/>'
                                f'<animateTransform attributeName="transform" type="translate" values="{steps}" '
                                f'dur="{num(period * speed)}s" repeatCount="indefinite" calcMode="discrete"/></g></g>')
            else:
                body.append(content)
        dstr = "".join(defs)
        # A badge says only what it reads: its name is its title, and it has no description.
        named = (f'aria-labelledby="t d" shape-rendering="crispEdges"><title id="t">{html.escape(title)}</title>'
                 f'<desc id="d">{html.escape(desc)}</desc>') if desc else \
            (f'aria-label="{html.escape(title)}" shape-rendering="crispEdges"><title>{html.escape(title)}</title>')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
                f'role="img" {named}'
                + (f"<!--{stamp}-->" if stamp else "")
                + f'<g transform="scale({self.u})">{"<defs>" + dstr + "</defs>" if dstr else ""}'
                f'{"".join(self.under)}{"".join(body)}</g></svg>')
