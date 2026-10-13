# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the Tic-Tac sheet is made of, per theme: the standard theme's enamel and a print's drawing, as chess's
sheets are (`games.skin`), with the marks' own materials.

  standard  chess's standard board in nine: the bars between the boards in the material of chess's dark squares,
            each board's face a shade of them and its nine squares the light squares, sunk in the card under the
            same lamp; the marks pen strokes in enamel, X lit white edged in black and O black with the lamp's
            highlight on it, as chess's pieces are, whoever plays them; the last mark's square amber, the board the
            next mark is sent to filmed in amber and bracketed in it, a won line struck in amber; a ghost a square
            of the bars' enamel with a dashed square of light inside it, framed in amber when it is the last move;
            after dark a closed board washed under the band's charcoal and its big mark, if it is O, edged in ash
  print     a plan view drawn as chess's board is: its shadow in section lining, the bars and each board's face
            lined as chess lines its dark squares, the squares laid on them in paper, each edged, and its edge
            drawn in; X paper edged in ink as heavily as chess's white pieces and line-shaded, O solid ink with a
            glint, as a print draws chess's pieces; the board the next mark is sent to toned in the print's mark
            and bracketed in it; a ghost's square lined as the bars are and edged in phantom lines, long and short
            dashes, as a drawing shows a part not there to use, boxed heavy when it is the last move

Either way each mark has its soft shadow down and to the right, away from the lamp, and a board closed is washed
back: a won one under its winner's mark drawn as large as the board, a drawn one lined across. The move that closed
it stays clear of the wash, its three struck over it, and the brackets are drawn last of all, over the board's edge.
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


def geometry(n: float, small: bool) -> tuple[float, float, float, float]:
    """The board's measures, `n` wide: the bars between the boards, the gutters between a board's squares, a
    board's width and a square's."""
    bar = 9 if small else 11
    gut = 2.6 if small else 3.2
    s = (n - 2 * bar) / 3
    return bar, gut, s, (s - 2 * gut) / 3


def faces(x0: float, y0: float, n: float, small: bool) -> str:
    """The eighty-one squares' faces, every board's nine, as one path."""
    bar, gut, s, q = geometry(n, small)
    out = []
    for bx in range(3):
        for by in range(3):
            X, Y = x0 + bx * (s + bar), y0 + by * (s + bar)
            for i in range(3):
                for j in range(3):
                    out.append(f"M{f1(X + i * (q + gut))} {f1(Y + j * (q + gut))}h{f1(q)}v{f1(q)}h{f1(-q)}Z")
    return "".join(out)


def bars(x0: float, y0: float, n: float, small: bool) -> str:
    """The four bars between the boards, as one path."""
    bar, _, s, _ = geometry(n, small)
    return "".join(f"M{f1(x0 + i * (s + bar) - bar)} {f1(y0)}h{f1(bar)}v{f1(n)}h{f1(-bar)}Z"
                   f"M{f1(x0)} {f1(y0 + i * (s + bar) - bar)}h{f1(n)}v{f1(bar)}h{f1(-n)}Z" for i in (1, 2))


def corners(X: float, Y: float, s: float, small: bool) -> str:
    """A board's four corners, marked as a drawing marks a detail to look at, as path data."""
    o = 3.2 if not small else 2.6
    L = s * .26
    x0, y0, x1, y1 = X - o, Y - o, X + s + o, Y + s + o
    return (f"M{f1(x0)} {f1(y0 + L)}V{f1(y0)}H{f1(x0 + L)}M{f1(x1 - L)} {f1(y0)}H{f1(x1)}V{f1(y0 + L)}"
            f"M{f1(x1)} {f1(y1 - L)}V{f1(y1)}H{f1(x1 - L)}M{f1(x0 + L)} {f1(y1)}H{f1(x0)}V{f1(y1 - L)}")


class Marks:
    """Each mark drawn once in the file's defs, for its mark, material, size and edge, and used wherever it stands:
    a board of eighty-one squares sets the same few marks again and again."""

    def pen_mark(self, cv, mark: str, material: str, x: float, y: float, size: float, *, shadow: bool = True,
                 edge: float = 1.5, big: bool = False) -> str:
        """A mark filling a box `size` wide with its top-left at (x, y); `big` for a won board's own mark, drawn
        across the board on its wash."""
        key = (mark, material, f1(size), f1(edge), shadow, big)
        cv.__dict__.setdefault("_pens", {})
        if key not in cv._pens:
            pid = cv.uid("pm")
            cv.defs.append(f'<g id="{pid}">' + self.pen_body(cv, mark, material, size, shadow=shadow, edge=edge,
                                                             big=big) + "</g>")
            cv._pens[key] = pid
        return f'<use href="#{cv._pens[key]}" x="{f1(x)}" y="{f1(y)}"/>'


class Print(Marks, GamePrint):
    """A print's Tic-Tac: the board drawn in plan, the marks as pen strokes with a body."""

    def board_base(self, cv, x0, y0, n, small) -> None:
        """The board's shadow; the bars between its boards and each board's face lined as chess lines its dark
        squares, so the board reads as a solid in every ink, as chess's does; and its eighty-one squares laid on
        them in paper, each edged, as firmly as chess lines a light print's darkness."""
        self.sink(cv, x0, y0, n)
        bar, _, s, _ = geometry(n, small)
        boards = "".join(f"M{f1(x0 + bx * (s + bar))} {f1(y0 + by * (s + bar))}h{f1(s)}v{f1(s)}h{f1(-s)}Z"
                         for bx in range(3) for by in range(3))
        cv.add(f'<path d="{bars(x0, y0, n, small)}{boards}" fill="url(#{self.hatch(cv, "square")})"/>')
        d = faces(x0, y0, n, small)
        cv.add(f'<path d="{d}" fill="{c(self.col["paper"])}"/>')
        cv.add(f'<path d="{d}" fill="none" {hair(self.col, min(1, .62 * self.firm))} stroke-width=".8"/>')

    def ghost(self, cv, x, y, q, appear: str = "") -> str:
        """A ghost's square: lined as the bars are, and edged inside in phantom lines, long and short dashes, as a
        drawing shows a part that is not there to use."""
        i = 1.2
        return (f'<g>{appear}<rect x="{f1(x + i)}" y="{f1(y + i)}" width="{f1(q - 2 * i)}" height="{f1(q - 2 * i)}" '
                f'fill="{c(self.col["paper"])}"/><rect x="{f1(x + i)}" y="{f1(y + i)}" width="{f1(q - 2 * i)}" '
                f'height="{f1(q - 2 * i)}" fill="url(#{self.hatch(cv, "square")})"/>'
                f'<rect x="{f1(x + 4)}" y="{f1(y + 4)}" width="{f1(q - 8)}" height="{f1(q - 8)}" fill="none" '
                f'stroke="{c(self.mark)}" stroke-opacity=".85" stroke-width="1.1" stroke-dasharray="5 1.6 1.2 1.6"/>'
                "</g>")

    def brackets(self, X, Y, s, small, appear: str = "") -> str:
        """The board the next mark is sent to, marked at its four corners as a drawing marks a detail: a band of
        paper first, so the marks read across the bars, then the stroke in the print's mark."""
        d, w = corners(X, Y, s, small), 3.4 if not small else 3
        return (f'<g>{appear}<path d="{d}" fill="none" stroke="{c(self.col["paper"])}" stroke-width="{fx(w + 3, 1)}" '
                f'stroke-linecap="square"/><path d="{d}" fill="none" stroke="{c(self.mark)}" '
                f'stroke-width="{fx(w, 1)}" stroke-linecap="square"/></g>')

    def target(self, X, Y, s) -> str:
        """The board the next mark is sent to, lifted: a light tone of the print's mark laid over its squares, as a
        drawing tones the detail it calls out."""
        return (f'<rect x="{f1(X)}" y="{f1(Y)}" width="{f1(s)}" height="{f1(s)}" fill="{c(self.mark)}" '
                f'fill-opacity="{".12" if self.dark else ".08"}"/>')

    def wash(self, X, Y, s) -> str:
        """A closed board washed back, as a drawing ghosts what is done with: paper laid over it."""
        return (f'<rect x="{f1(X - 1)}" y="{f1(Y - 1)}" width="{f1(s + 2)}" height="{f1(s + 2)}" '
                f'fill="{c(self.col["paper"])}" fill-opacity="{".7" if self.dark else ".74"}"/>')

    def drawn(self, cv, X, Y, s) -> str:
        """A drawn board lined across, as the bars are: nobody's."""
        return (f'<rect x="{f1(X + 3)}" y="{f1(Y + 3)}" width="{f1(s - 6)}" height="{f1(s - 6)}" '
                f'fill="url(#{self.hatch(cv, "square")})" fill-opacity=".9"/>')

    def kept(self, x, y, q) -> str:
        """The square of the move that closed its board, kept clear of the wash: boxed heavy on bare paper."""
        return (f'<rect x="{f1(x + 2.4)}" y="{f1(y + 2.4)}" width="{f1(q - 4.8)}" height="{f1(q - 4.8)}" '
                f'fill="{c(self.col["paper"])}" stroke="{c(self.mark)}" stroke-width="2.2"/>')

    def cell_mark(self, cv, x, y, w, h, appear: str) -> None:
        """The last move's square, boxed heavy, as chess boxes the square a piece lands on."""
        cv.add(f'<g>{appear}<rect x="{f1(x + 2.4)}" y="{f1(y + 2.4)}" width="{f1(w - 4.8)}" height="{f1(h - 4.8)}" '
               f'fill="none" stroke="{c(self.mark)}" stroke-width="2.2"/></g>')

    def ghost_mark(self, x, y, q, appear: str = "") -> str:
        """The last move's square when the move was a ghost: boxed heavy over the ghost's lining, as every last
        move's square is, at its very edge so the phantom lines inside it stay clear."""
        return (f'<g>{appear}<rect x="{f1(x + 1.2)}" y="{f1(y + 1.2)}" width="{f1(q - 2.4)}" height="{f1(q - 2.4)}" '
                f'fill="none" stroke="{c(self.mark)}" stroke-width="2.2"/></g>')

    def centre_mark(self, cx, cy, size) -> str:
        """An open square's centre mark, as a drawing marks the centre of a hole: two fine crossing lines."""
        h = size / 2
        return (f'<path d="M{f1(cx - h)} {f1(cy)}H{f1(cx + h)}M{f1(cx)} {f1(cy - h)}V{f1(cy + h)}" fill="none" '
                f'{hair(self.col, .4)} stroke-width=".7"/>')

    # --- the marks
    def _clip(self, cv, mark) -> str:
        cv.__dict__.setdefault("_markclips", {})
        if mark not in cv._markclips:
            cid = cv.uid("s")
            cv.defs.append(f'<clipPath id="{cid}"><path d="{BODY[mark]}"/></clipPath>')
            cv._markclips[mark] = cid
        return cv._markclips[mark]

    def pen_body(self, cv, mark: str, material: str, size: float, *, shadow: bool = True, edge: float = 1.5,
                 big: bool = False) -> str:
        """A mark filling a box `size` wide from the origin: its shadow, its body edged, and its shading or glint.
        `edge` is the edge's width on the sheet, whatever the mark's size; a light mark's is drawn heavier, as
        heavy as chess's white pieces are edged, so an X holds beside a solid O. A big mark is drawn as any other."""
        k = size / 100
        fill, line, detail = self.paint(material)
        e = edge / k * (.7 if material == "dark" and self.dark else 1.3 if material == "light" else 1)
        body = BODY[mark]
        out = [f'<g transform="scale({fx(k, 4)})">']
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
        then the stroke in the print's mark. The same pen strikes a board's three and the game's three boards."""
        return (f'<path d="{line_d}" fill="none" stroke="{c(self.col["paper"])}" stroke-width="{fx(width + 6, 1)}" '
                f'stroke-linecap="round"{extra}>{anim}</path>'
                f'<path d="{line_d}" fill="none" stroke="{c(self.mark)}" stroke-width="{fx(width, 1)}" '
                f'stroke-linecap="round"{extra}>{anim}</path>')


class Standard(Marks, GameStandard):
    """The standard theme's Tic-Tac: chess's board in nine boards of nine, and marks of enamel lit as its pieces are."""

    def board_base(self, cv, x0, y0, n, small) -> None:
        """The board sunk in the card as chess's is: the bars between the boards in the dark squares' enamel, each
        board's face a shade of it, and its squares the light squares'."""
        pal = self.squares()
        self.sink(cv, x0, y0, n)
        cv.add(P.rect(x0, y0, n, n, pal["dark"][0]))
        bar, _, s, _ = geometry(n, small)
        tone, op = pal["light"]
        under = "".join(f"M{f1(x0 + bx * (s + bar))} {f1(y0 + by * (s + bar))}h{f1(s)}v{f1(s)}h{f1(-s)}Z"
                        for bx in range(3) for by in range(3))
        cv.add(f'<path d="{under}" fill="{c(tone)}" fill-opacity="{".3" if self.dark else ".22"}"/>')
        d = faces(x0, y0, n, small)
        if self.std["name"] == "day":
            cv.add(f'<path d="{d}" fill="{c("white")}"/>')
        o = f' fill-opacity="{fx(op)}"' if op < 1 else ""
        cv.add(f'<path d="{d}" fill="{c(tone)}"{o}/>')

    def ghost(self, cv, x, y, q, appear: str = "") -> str:
        """A ghost's square: sunk in the bars' enamel under the lamp, with a dashed square of light inside it, a part
        of the board that is not there to use."""
        L = self.lights(cv)
        i = .8
        return (f'<g>{appear}' + P.rect(x + i, y + i, q - 2 * i, q - 2 * i, self.squares()["dark"][0])
                + f'<rect x="{f1(x + i)}" y="{f1(y + i)}" width="{f1(q - 2 * i)}" height="{f1(q - 2 * i)}" '
                  f'fill="url(#{L["bd"]})"/><rect x="{f1(x + 4)}" y="{f1(y + 4)}" width="{f1(q - 8)}" '
                  f'height="{f1(q - 8)}" fill="none" stroke="{c("white")}" stroke-opacity=".7" stroke-width="1.1" '
                  'stroke-dasharray="5 1.6 1.2 1.6"/></g>')

    def brackets(self, X, Y, s, small, appear: str = "") -> str:
        """The board the next mark is sent to, its four corners marked in amber, the colour the last move is marked
        in, edged in black so they read across the bars and the card."""
        d, w = corners(X, Y, s, small), 2.6 if not small else 2.2
        return (f'<g>{appear}<path d="{d}" fill="none" stroke="{c("black")}" stroke-width="{fx(w + 2.6, 1)}" '
                f'stroke-linecap="square"/><path d="{d}" fill="none" stroke="{c("amber")}" '
                f'stroke-width="{fx(w, 1)}" stroke-linecap="square"/></g>')

    def target(self, X, Y, s) -> str:
        """The board the next mark is sent to, lifted: a film of amber, the colour its brackets are, over its
        squares."""
        return (f'<rect x="{f1(X)}" y="{f1(Y)}" width="{f1(s)}" height="{f1(s)}" fill="{c("amber")}" '
                f'fill-opacity="{".2" if self.dark else ".16"}"/>')

    def wash(self, X, Y, s) -> str:
        """A closed board washed back under a film of the card: by night a film of the band's charcoal, so a black
        mark under it is pushed back as a white one is, not left at full strength under a film of black."""
        film, op = ("charcoal", ".8") if self.dark else (self.std["paper"], ".7")
        return (f'<rect x="{f1(X - 1)}" y="{f1(Y - 1)}" width="{f1(s + 2)}" height="{f1(s + 2)}" '
                f'fill="{c(film)}" fill-opacity="{op}"/>')

    def drawn(self, cv, X, Y, s) -> str:
        """A drawn board lined across in the dark squares' enamel, faint: nobody's."""
        cid = cv.uid("d")
        cv.defs.append(f'<clipPath id="{cid}"><rect x="{f1(X + 3)}" y="{f1(Y + 3)}" width="{f1(s - 6)}" '
                       f'height="{f1(s - 6)}"/></clipPath>')
        step = 6
        d = "".join(f"M{f1(X + k)} {f1(Y + s)}L{f1(X + k + s)} {f1(Y)}" for k in range(-int(s), int(s), step))
        return (f'<g clip-path="url(#{cid})"><path d="{d}" fill="none" stroke="{c(self.squares()["dark"][0])}" '
                f'stroke-opacity="{".5" if self.dark else ".38"}" stroke-width="1.6"/></g>')

    def kept(self, x, y, q) -> str:
        """The square of the move that closed its board, kept clear of the wash, amber as the last move's is."""
        return P.rect(x, y, q, q, "white") + P.rect(x, y, q, q, "amber")

    def cell_mark(self, cv, x, y, w, h, appear: str) -> None:
        """The last move's square, amber, as chess marks the square a piece lands on."""
        cv.add(f'<g>{appear}' + P.rect(x, y, w, h, "white") + P.rect(x, y, w, h, "amber") + "</g>")

    def ghost_mark(self, x, y, q, appear: str = "") -> str:
        """The last move's square when the move was a ghost: an amber frame round the ghost's enamel, the colour the
        last move is marked in."""
        return (f'<g>{appear}<rect x="{f1(x + 1.2)}" y="{f1(y + 1.2)}" width="{f1(q - 2.4)}" height="{f1(q - 2.4)}" '
                f'fill="none" stroke="{c("amber")}" stroke-width="2.4"/></g>')

    def centre_mark(self, cx, cy, size) -> str:
        """An open square's centre, marked with a small cross, faint."""
        h = size / 2
        tone = "charcoal" if self.dark else "slate"
        return (f'<path d="M{f1(cx - h)} {f1(cy)}H{f1(cx + h)}M{f1(cx)} {f1(cy - h)}V{f1(cy + h)}" fill="none" '
                f'stroke="{c(tone)}" stroke-opacity=".55" stroke-width=".9"/>')

    def pen_body(self, cv, mark: str, material: str, size: float, *, shadow: bool = True, edge: float = 1.5,
                 big: bool = False) -> str:
        """A mark filling a box `size` wide from the origin, in enamel: its shadow, its body edged in black, and the
        lamp across it, a shade on the light enamel and a sheen and a highlight on the dark. A big dark mark after
        dark, a won board's O on its charcoal wash, is edged in ash, so it stands above its own board."""
        k = size / 100
        L = self.lights(cv)
        fill, line, _ = self.paint(material)
        if big and self.dark and material == "dark":
            line = "ash"
        e = edge / k
        body = BODY[mark]
        out = [f'<g transform="scale({fx(k, 4)})">']
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
