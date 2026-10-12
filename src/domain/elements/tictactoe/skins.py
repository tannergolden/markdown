# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the Tic-Tac-Toe sheet is made of, per theme: the standard theme's enamel and a print's drawing, as chess's
sheets are (`games.skin`), with the marks' own materials.

  standard  chess's standard board: its cells the light squares and the bars between them the dark, sunk in the
            card under the same lamp; the marks pen strokes in enamel, X lit white edged in black and O black with
            the lamp's highlight on it, as chess's pieces are, whoever plays them; the last mark's cell amber, a won
            line struck in amber
  print     a plan view drawn as chess's board is: its shadow in section lining, the bars lined as chess lines its
            dark squares, a fine edge round every cell, and its edge drawn in; X paper edged in ink and
            line-shaded, O solid ink with a glint, as a print draws chess's pieces

Either way each mark has its soft shadow down and to the right, away from the lamp, and the eight lines a game is
won on are drawn faint through the cells while it goes on, all eight, whatever stands on them.
"""
from __future__ import annotations

import math

from ...canvas import c
from ...drafting import hair
from ...lettering import f1, fx
from ...standard import pieces as P
from ..games.skin import Print as GamePrint
from ..games.skin import Standard as GameStandard
from .shapes import PEN, R, SHADOW, SPEC

# Line shading, as on chess's white pieces: lines along the mark's height, closer together toward its right.
SHADE = "".join(f"M{x} 18V82" for x in (58.6, 63.4, 67.6, 71.2, 74.3, 76.9, 79.1))
GLINT = "M31 37.5 37.5 31"        # where the lamp catches a dark X: a short stroke on its upper left arm


def stadium(x1: float, y1: float, x2: float, y2: float, w: float) -> str:
    """A pen stroke from one point to another, `w` wide with round ends, as an outline a clip can use."""
    dx, dy = x2 - x1, y2 - y1
    n = math.hypot(dx, dy)
    px, py = -dy / n * w / 2, dx / n * w / 2
    r = f1(w / 2)
    return (f"M{f1(x1 + px)} {f1(y1 + py)}L{f1(x2 + px)} {f1(y2 + py)}A{r} {r} 0 0 0 {f1(x2 - px)} {f1(y2 - py)}"
            f"L{f1(x1 - px)} {f1(y1 - py)}A{r} {r} 0 0 0 {f1(x1 + px)} {f1(y1 + py)}Z")


def ring(r: float, w: float) -> str:
    """An O's stroke as an outline: two circles, the inner one wound the other way."""
    a, b = r + w / 2, r - w / 2
    return (f"M{f1(50 - a)} 50A{f1(a)} {f1(a)} 0 1 0 {f1(50 + a)} 50A{f1(a)} {f1(a)} 0 1 0 {f1(50 - a)} 50Z"
            f"M{f1(50 - b)} 50A{f1(b)} {f1(b)} 0 1 1 {f1(50 + b)} 50A{f1(b)} {f1(b)} 0 1 1 {f1(50 - b)} 50Z")


BODY = {"X": stadium(26.5, 26.5, 73.5, 73.5, PEN) + stadium(73.5, 26.5, 26.5, 73.5, PEN), "O": ring(R, PEN)}


def cells(x0: float, y0: float, n: float, bar: float) -> str:
    """The nine cells' open faces, from the board's edge or a bar's to the next, as one path."""
    s = n / 3
    out = []
    for i in range(3):
        for j in range(3):
            cx0 = x0 + i * s + (bar / 2 if i else 0)
            cy0 = y0 + j * s + (bar / 2 if j else 0)
            cw = s - (bar / 2 if i else 0) - (bar / 2 if i < 2 else 0)
            ch = s - (bar / 2 if j else 0) - (bar / 2 if j < 2 else 0)
            out.append(f"M{f1(cx0)} {f1(cy0)}h{f1(cw)}v{f1(ch)}h{f1(-cw)}Z")
    return "".join(out)


class Print(GamePrint):
    """A print's Tic-Tac-Toe: the board drawn in plan, the marks as pen strokes with a body."""

    def board_base(self, cv, x0, y0, n, bar) -> None:
        """The board's shadow, the lined bars between its cells, and every cell's fine edge."""
        self.sink(cv, x0, y0, n)
        s = n / 3
        bars = "".join(f"M{f1(x0 + i * s - bar / 2)} {f1(y0)}h{f1(bar)}v{f1(n)}h{f1(-bar)}Z"
                       f"M{f1(x0)} {f1(y0 + i * s - bar / 2)}h{f1(n)}v{f1(bar)}h{f1(-n)}Z" for i in (1, 2))
        cv.add(f'<path d="{bars}" fill="url(#{self.hatch(cv, "square")})"/>')
        cv.add(f'<path d="{cells(x0, y0, n, bar)}" fill="none" {hair(self.col, .5)} stroke-width=".7"/>')

    def cell_mark(self, cv, x, y, w, h, appear: str) -> None:
        """The last mark's cell, boxed heavy, as chess boxes the square a piece lands on."""
        cv.add(f'<g>{appear}<rect x="{f1(x + 2.4)}" y="{f1(y + 2.4)}" width="{f1(w - 4.8)}" height="{f1(h - 4.8)}" '
               f'fill="none" stroke="{c(self.mark)}" stroke-width="2.2"/></g>')

    def centre_mark(self, cx, cy, size) -> str:
        """An open cell's centre mark, as a drawing marks the centre of a hole: two fine crossing lines."""
        h = size / 2
        return (f'<path d="M{f1(cx - h)} {f1(cy)}H{f1(cx + h)}M{f1(cx)} {f1(cy - h)}V{f1(cy + h)}" fill="none" '
                f'{hair(self.col, .4)} stroke-width=".7"/>')

    def open_lines(self, d: str) -> str:
        """The eight lines a game is won on, faint, long and short dashes, as a drawing draws centre lines."""
        return (f'<path d="{d}" fill="none" stroke="{c(self.col["line"])}" stroke-opacity=".28" stroke-width=".7" '
                f'stroke-dasharray="12 3 2 3"/>')

    # --- the marks
    def _clip(self, cv, mark) -> str:
        cv.__dict__.setdefault("_markclips", {})
        if mark not in cv._markclips:
            cid = cv.uid("s")
            cv.defs.append(f'<clipPath id="{cid}"><path d="{BODY[mark]}"/></clipPath>')
            cv._markclips[mark] = cid
        return cv._markclips[mark]

    def pen_mark(self, cv, mark: str, material: str, x: float, y: float, size: float, *, shadow: bool = True,
                 edge: float = 1.5) -> str:
        """A mark filling a box `size` wide with its top-left at (x, y): its shadow, its body edged, and its shading
        or glint. `edge` is the edge's width on the sheet, whatever the mark's size."""
        k = size / 100
        fill, line, detail = self.paint(material)
        e = edge / k * (.7 if material == "dark" and self.dark else 1)
        body = BODY[mark]
        out = [f'<g transform="translate({f1(x)} {f1(y)}) scale({fx(k, 4)})">']
        if shadow:
            out.append(f'<path d="{body}" transform="translate({fx(SHADOW[0], 2)} {fx(SHADOW[1], 2)})" '
                       f'fill="{c(self.shade)}" fill-opacity="{self.shadow_op}" fill-rule="nonzero"/>')
        out.append(f'<path d="{body}" fill="{c(fill)}" stroke="{c(line)}" stroke-width="{fx(2 * e, 2)}" '
                   f'stroke-linejoin="round"/><path d="{body}" fill="{c(fill)}"/>')
        if material == "light":
            out.append(f'<path d="{SHADE}" clip-path="url(#{self._clip(cv, mark)})" fill="none" stroke="{c(line)}" '
                       f'stroke-width="{fx(.8 / k, 2)}" stroke-opacity=".55"/>')
        else:
            out.append(f'<path d="{SPEC if mark == "O" else GLINT}" fill="none" stroke="{c("white")}" '
                       f'stroke-opacity="{".35" if self.dark else ".55"}" stroke-width="{fx(1.3 / k, 2)}" '
                       f'stroke-linecap="round"/>')
        return "".join(out) + "</g>"

    def strike(self, line_d: str, width: float, extra: str = "", anim: str = "") -> str:
        """A won line struck through, as a pen strikes a row: a band of paper first, so it reads across the marks,
        then the stroke in the print's mark."""
        return (f'<path d="{line_d}" fill="none" stroke="{c(self.col["paper"])}" stroke-width="{fx(width + 6, 1)}" '
                f'stroke-linecap="round"{extra}>{anim}</path>'
                f'<path d="{line_d}" fill="none" stroke="{c(self.mark)}" stroke-width="{fx(width, 1)}" '
                f'stroke-linecap="round"{extra}>{anim}</path>')


class Standard(GameStandard):
    """The standard theme's Tic-Tac-Toe: chess's board in three cells, and marks of enamel lit as its pieces are."""

    def board_base(self, cv, x0, y0, n, bar) -> None:
        """The board sunk in the card as chess's is: the bars between the cells in the dark squares' enamel, the
        cells the light squares'."""
        pal = self.squares()
        self.sink(cv, x0, y0, n)
        cv.add(P.rect(x0, y0, n, n, pal["dark"][0]))
        d = cells(x0, y0, n, bar)
        tone, op = pal["light"]
        if self.std["name"] == "day":
            cv.add(f'<path d="{d}" fill="{c("white")}"/>')
        o = f' fill-opacity="{fx(op)}"' if op < 1 else ""
        cv.add(f'<path d="{d}" fill="{c(tone)}"{o}/>')

    def cell_mark(self, cv, x, y, w, h, appear: str) -> None:
        """The last mark's cell, amber, as chess marks the square a piece lands on."""
        cv.add(f'<g>{appear}' + P.rect(x, y, w, h, "white") + P.rect(x, y, w, h, "amber") + "</g>")

    def centre_mark(self, cx, cy, size) -> str:
        """An open cell's centre, marked with a small cross, faint."""
        h = size / 2
        tone = "charcoal" if self.dark else "slate"
        return (f'<path d="M{f1(cx - h)} {f1(cy)}H{f1(cx + h)}M{f1(cx)} {f1(cy - h)}V{f1(cy + h)}" fill="none" '
                f'stroke="{c(tone)}" stroke-opacity=".55" stroke-width=".9"/>')

    def open_lines(self, d: str) -> str:
        """The eight lines a game is won on, faint, in the accent."""
        return (f'<path d="{d}" fill="none" stroke="{c(P.ACCENT)}" stroke-opacity="{".5" if self.dark else ".38"}" '
                f'stroke-width=".9" stroke-dasharray="12 3 2 3"/>')

    def pen_mark(self, cv, mark: str, material: str, x: float, y: float, size: float, *, shadow: bool = True,
                 edge: float = 1.5) -> str:
        """A mark filling a box `size` wide with its top-left at (x, y), in enamel: its shadow, its body edged in
        black, and the lamp across it, a shade on the light enamel and a sheen and a highlight on the dark."""
        k = size / 100
        L = self.lights(cv)
        fill, line, _ = self.paint(material)
        e = edge / k
        body = BODY[mark]
        out = [f'<g transform="translate({f1(x)} {f1(y)}) scale({fx(k, 4)})">']
        if shadow:
            out.append(f'<path d="{body}" transform="translate({fx(SHADOW[0], 2)} {fx(SHADOW[1], 2)})" '
                       f'fill="{c("black")}" fill-opacity="{".4" if self.dark else ".16"}"/>')
        out.append(f'<path d="{body}" fill="{c(fill)}" stroke="{c(line)}" stroke-width="{fx(2 * e, 2)}" '
                   f'stroke-linejoin="round"/><path d="{body}" fill="{c(fill)}"/>'
                   f'<path d="{body}" fill="url(#{L["wp" if material == "light" else "bp"]})"/>')
        if material == "dark":
            out.append(f'<path d="{SPEC if mark == "O" else GLINT}" fill="none" stroke="{c("white")}" '
                       f'stroke-opacity=".5" stroke-width="{fx(1.3 / k, 2)}" stroke-linecap="round"/>')
        return "".join(out) + "</g>"

    def strike(self, line_d: str, width: float, extra: str = "", anim: str = "") -> str:
        """A won line struck through in amber, the colour the last move is marked in, edged in black so it reads
        across the cells and the marks."""
        return (f'<path d="{line_d}" fill="none" stroke="{c("black")}" stroke-width="{fx(width + 3.5, 1)}" '
                f'stroke-linecap="round"{extra}>{anim}</path>'
                f'<path d="{line_d}" fill="none" stroke="{c("amber")}" stroke-width="{fx(width, 1)}" '
                f'stroke-linecap="round"{extra}>{anim}</path>')
