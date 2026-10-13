# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the Pentago sheet is made of, per theme: the standard theme's enamel and a print's drawing, as chess's
sheets are (`games.skin`), with the quarters' and the marbles' own materials.

  standard  four quarter plates in the theme's cobalt enamel, the colour of chess's dark squares, lit from the upper
            left as chess's board is, every hole cut clean through and its wall in shade on the side the lamp
            misses; the marbles enamel, White's lit white edged in black and Black's black with the lamp's
            highlight, as chess's pieces are; a ghost a marble of the plate's own enamel ringed inside in a dashed
            line of light; the last marble's hole ringed amber and its quarter's turn marked by an amber arrow, a won
            line joined in amber
  print     each quarter drawn in plan, as a part is: its face in section lining, as chess lines its dark squares,
            every hole cut through it with a centre mark while it is empty and a shade line on the side the lamp
            misses, the whole casting its shadow down and to the right; a White marble paper edged in ink and
            line-shaded, a Black one solid ink with a glint; a ghost lined as the plate is and ringed in phantom
            lines, long and short dashes; the last quarter turn an arrow round the quarter's outer corner
"""
from __future__ import annotations

import math

from ...canvas import c
from ...drafting import hair
from ...lettering import f1, fx
from ...standard import pieces as P
from ..games.skin import Print as GamePrint
from ..games.skin import Standard as GameStandard
from .shapes import DISC, GROOVE, HOLE, SHADE

def circle(cx: float, cy: float, r: float, sweep: int = 0) -> str:
    """A circle as path data, two half arcs, wound one way or the other."""
    return (f"M{f1(cx - r)} {f1(cy)}A{f1(r)} {f1(r)} 0 1 {sweep} {f1(cx + r)} {f1(cy)}"
            f"A{f1(r)} {f1(r)} 0 1 {sweep} {f1(cx - r)} {f1(cy)}Z")


def outline(x: float, y: float, w: float, h: float, rx: float) -> str:
    """The plate's outline: a rectangle with rounded corners, as path data."""
    return (f"M{f1(x + rx)} {f1(y)}H{f1(x + w - rx)}A{f1(rx)} {f1(rx)} 0 0 1 {f1(x + w)} {f1(y + rx)}"
            f"V{f1(y + h - rx)}A{f1(rx)} {f1(rx)} 0 0 1 {f1(x + w - rx)} {f1(y + h)}H{f1(x + rx)}"
            f"A{f1(rx)} {f1(rx)} 0 0 1 {f1(x)} {f1(y + h - rx)}V{f1(y + rx)}A{f1(rx)} {f1(rx)} 0 0 1 "
            f"{f1(x + rx)} {f1(y)}Z")


def walls(holes: list, rh: float, a0: float, a1: float) -> str:
    """The arcs of every hole's wall between two angles, in degrees, as one path."""
    a, b = math.radians(a0), math.radians(a1)
    return "".join(f"M{f1(hx + rh * math.cos(a))} {f1(hy + rh * math.sin(a))}A{f1(rh)} {f1(rh)} 0 0 1 "
                   f"{f1(hx + rh * math.cos(b))} {f1(hy + rh * math.sin(b))}" for hx, hy in holes)


def turn_arrow(X: float, Y: float, q: float, qk: str, way: str, inset: float) -> tuple[str, str]:
    """The arrow round a quarter's outer corner that marks the way it turned, inside the plate's margin: from the
    middle of one outer edge round the corner to the middle of the other, clockwise or anticlockwise as the board is
    seen. Its shaft and its head, as path data."""
    corner = {"ul": (X, Y), "ur": (X + q, Y), "ll": (X, Y + q), "lr": (X + q, Y + q)}[qk]
    sx = 1 if qk in ("ul", "ll") else -1             # inward from the corner, across and down
    sy = 1 if qk in ("ul", "ur") else -1
    cx, cy = corner[0] + sx * inset, corner[1] + sy * inset
    side = (cx, cy + sy * (q / 2 - inset))           # the middle of the outer side edge
    end_ = (cx + sx * (q / 2 - inset), cy)           # the middle of the outer top or bottom edge
    start, end = (side, end_) if (qk in ("ul", "lr")) == (way == "cw") else (end_, side)
    r = q * .12

    def toward(pt, k):
        dx, dy = pt[0] - cx, pt[1] - cy
        d = math.hypot(dx, dy)
        return cx + dx / d * k, cy + dy / d * k
    a, b = toward(start, r), toward(end, r)
    shaft = (f"M{f1(start[0])} {f1(start[1])}L{f1(a[0])} {f1(a[1])}Q{f1(cx)} {f1(cy)} {f1(b[0])} {f1(b[1])}"
             f"L{f1(end[0])} {f1(end[1])}")
    ux, uy = end[0] - b[0], end[1] - b[1]
    n = math.hypot(ux, uy)
    ux, uy = ux / n, uy / n
    h = 8.5
    head = (f"M{f1(end[0] + ux * h * .55)} {f1(end[1] + uy * h * .55)}L{f1(end[0] - ux * h * .45 - uy * h * .48)} "
            f"{f1(end[1] - uy * h * .45 + ux * h * .48)}L{f1(end[0] - ux * h * .45 + uy * h * .48)} "
            f"{f1(end[1] - uy * h * .45 - ux * h * .48)}Z")
    return shaft, head


def turn_icon(x: float, cy: float, r: float, way: str) -> tuple[str, str, str, float]:
    """A quarter turn written small, `r` in radius from `x`: a circular arrow, its head the way the quarter went. Its
    arc, its head, the flip that turns a clockwise arrow anticlockwise, and the room it takes."""
    a0, a1 = math.radians(-60), math.radians(225)
    cx = x + r
    p0 = (cx + r * math.cos(a0), cy + r * math.sin(a0))
    p1 = (cx + r * math.cos(a1), cy + r * math.sin(a1))
    tx, ty = -math.sin(a1), math.cos(a1)             # the way round, clockwise, at the arrow's end
    h = r * .75
    nx, ny = -ty, tx
    head = (f"M{f1(p1[0] + tx * h)} {f1(p1[1] + ty * h)}L{f1(p1[0] + nx * h * .55)} {f1(p1[1] + ny * h * .55)}"
            f"L{f1(p1[0] - nx * h * .55)} {f1(p1[1] - ny * h * .55)}Z")
    arc = f"M{f1(p0[0])} {f1(p0[1])}A{f1(r)} {f1(r)} 0 1 1 {f1(p1[0])} {f1(p1[1])}"
    flip = f' transform="translate({f1(2 * cx)} 0) scale(-1 1)"' if way == "acw" else ""
    return arc, head, flip, 2 * r + r * .35


class Print(GamePrint):
    """A print's Pentago: the quarters in plan, the marbles seen through their holes."""

    def disc_def(self, cv, material: str, r: float) -> str:
        """The id of a marble of radius `r`, drawn once in the file's defs about its own centre: its face edged,
        its groove, and its shading or glint; a small one plain, its face and its groove alone."""
        key = (material, f1(r))
        cv.__dict__.setdefault("_discs", {})
        if key not in cv._discs:
            pid = cv.uid("p")
            fill, edge, detail = self.paint(material)
            g = GROOVE / DISC * r
            small = r < 7
            ew = (".9" if material == "dark" and self.dark else "1.3") if not small else ".8"
            out = [f'<g id="{pid}"><circle r="{f1(r)}" fill="{c(fill)}" stroke="{c(edge)}" stroke-width="{ew}"/>']
            if material == "light":
                if not small:
                    cid = cv.uid("s")
                    cv.defs.append(f'<clipPath id="{cid}"><circle r="{f1(r)}"/></clipPath>')
                    lines = "".join(f"M{f1(k * r)} {f1(-r)}V{f1(r)}" for k in SHADE)
                    out.append(f'<path d="{lines}" clip-path="url(#{cid})" fill="none" stroke="{c(edge)}" '
                               f'stroke-width=".7" stroke-opacity=".5"/>')
                out.append(f'<circle r="{f1(g)}" fill="{c(fill)}" stroke="{c(edge)}" '
                           f'stroke-width="{".9" if not small else ".6"}"/>')
            else:
                out.append(f'<circle r="{f1(g)}" fill="none" stroke="{c("white")}" '
                           f'stroke-opacity="{".3" if self.dark else ".42"}" '
                           f'stroke-width="{".9" if not small else ".6"}"/>')
                if not small:
                    a, b = math.radians(-165), math.radians(-112)
                    rr = (r + g) / 2 + r * .08
                    out.append(f'<path d="M{f1(rr * math.cos(a))} {f1(rr * math.sin(a))}A{f1(rr)} {f1(rr)} 0 0 1 '
                               f'{f1(rr * math.cos(b))} {f1(rr * math.sin(b))}" fill="none" stroke="{c("white")}" '
                               f'stroke-opacity="{".4" if self.dark else ".6"}" stroke-width="1.2" '
                               f'stroke-linecap="round"/>')
            cv.defs.append("".join(out) + "</g>")
            cv._discs[key] = pid
        return cv._discs[key]

    def disc(self, cv, material: str, cx: float, cy: float, pitch: float, *, r: float | None = None) -> str:
        """A marble seen face on, centred at (cx, cy), `r` its radius (a hole's marble unless given)."""
        r = r if r is not None else DISC * pitch
        return f'<use href="#{self.disc_def(cv, material, r)}" x="{f1(cx)}" y="{f1(cy)}"/>'

    def frame_shadow(self, cv, x, y, w, h) -> None:
        """A quarter's shadow, cast down and to the right in section lining, as chess's board casts its own."""
        d = f"M{f1(x + w)} {f1(y + 5)}h5v{f1(h - 1)}h{f1(-w + 1)}v-5h{f1(w - 6)}Z"
        cv.add(f'<path d="{d}" fill="url(#{self.hatch(cv, "shadow")})"/>')

    def plate(self, cv, x, y, w, h, holes: list, pitch: float, empty: list) -> None:
        """A quarter's face: paper cut through at every hole, lined, edged; each hole edged fine and shaded heavy
        on its upper left, where its wall turns from the lamp; an empty hole's centre marked."""
        rh = HOLE * pitch
        rx = pitch * .16
        outer = outline(x, y, w, h, rx)
        cut = "".join(circle(hx, hy, rh) for hx, hy in holes)
        cv.add(f'<path d="{outer}{cut}" fill="{c(self.col["paper"])}" fill-rule="evenodd"/>'
               f'<path d="{outer}{cut}" fill="url(#{self.hatch(cv, "square")})" fill-rule="evenodd"/>')
        cv.add(f'<path d="{cut}" fill="none" {hair(self.col, .8)} stroke-width=".9"/>')
        cv.add(f'<path d="{walls(holes, rh, -205, -25)}" fill="none" stroke="{c(self.col["line"])}" '
               f'stroke-width="1.5" stroke-linecap="round"/>')
        if empty:
            k = rh * .42
            marks = "".join(f"M{f1(hx - k)} {f1(hy)}H{f1(hx + k)}M{f1(hx)} {f1(hy - k)}V{f1(hy + k)}"
                            for hx, hy in empty)
            cv.add(f'<path d="{marks}" fill="none" {hair(self.col, .4)} stroke-width=".7"/>')
        cv.add(self.plotted(f'<path d="{outer}" fill="none" stroke="{c(self.col["line"])}" stroke-width="1.6"/>',
                            2 * (w + h)))
        cv.add(self.plotted(f'<path d="M{f1(x + w - rx * .3)} {f1(y + rx)}V{f1(y + h - rx)}A{f1(rx)} {f1(rx)} 0 0 1 '
                            f'{f1(x + w - rx)} {f1(y + h)}H{f1(x + rx)}" fill="none" stroke="{c(self.col["line"])}" '
                            f'stroke-width="2.8"/>', w + h))

    def hole_ring(self, cv, cx, cy, r, appear: str = "", width: float = 2.2) -> str:
        """A hole ringed heavy, as chess boxes the square a piece lands on."""
        return (f'<g>{appear}<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="none" stroke="{c(self.mark)}" '
                f'stroke-width="{fx(width, 1)}"/></g>')

    def slot(self, cx, cy) -> str:
        """A rack's empty slot, where a marble that has been set stood: a small mark, faint."""
        return (f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="1.1" fill="{c(self.col["ink"])}" '
                f'fill-opacity="{".3" if self.dark else ".28"}"/>')

    def connect(self, d: str, width: float, extra: str = "", anim: str = "") -> str:
        """Five marbles joined, as a drawing joins the parts of an assembly: a band of paper, then the line."""
        return (f'<path d="{d}" fill="none" stroke="{c(self.col["paper"])}" stroke-width="{fx(width + 5, 1)}" '
                f'stroke-linecap="round"{extra}>{anim}</path>'
                f'<path d="{d}" fill="none" stroke="{c(self.mark)}" stroke-width="{fx(width, 1)}" '
                f'stroke-linecap="round"{extra}>{anim}</path>')

    def ghost_marble(self, cv, cx: float, cy: float, r: float) -> str:
        """A ghost: a marble that is nobody's, lined as the plate is and ringed inside in phantom lines, long and
        short dashes, as a drawing shows a part that is not there to use."""
        return (f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="{c(self.col["paper"])}"/>'
                f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="url(#{self.hatch(cv, "square")})" '
                f'stroke="{c(self.col["line"])}" stroke-width=".9"/>'
                f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r * .74)}" fill="none" stroke="{c(self.mark)}" '
                f'stroke-opacity=".85" stroke-width="1.1" stroke-dasharray="{fx(r * .32, 1)} {fx(r * .1, 1)} '
                f'{fx(r * .07, 1)} {fx(r * .1, 1)}"/>')

    def turn_mark(self, X, Y, q, qk, way, inset, appear: str = "") -> str:
        """The last quarter turn, an arrow round the quarter's outer corner: a band of paper first, so it reads
        across the plate, then the stroke in the print's mark."""
        shaft, head = turn_arrow(X, Y, q, qk, way, inset)
        paper, ink = c(self.col["paper"]), c(self.mark)
        return (f'<g>{appear}<path d="{shaft}" fill="none" stroke="{paper}" stroke-width="6" stroke-linecap="round" '
                f'stroke-linejoin="round"/><path d="{head}" fill="{paper}" stroke="{paper}" stroke-width="3" '
                f'stroke-linejoin="round"/><path d="{shaft}" fill="none" stroke="{ink}" stroke-width="2.4" '
                f'stroke-linecap="round" stroke-linejoin="round"/><path d="{head}" fill="{ink}"/></g>')

    def turn_glyph(self, x, cy, r, way, role="ink") -> tuple[str, float]:
        """A quarter turn as a move writes it: a circular arrow in the words' ink. Returns it and its width."""
        arc, head, flip, w = turn_icon(x, cy, r, way)
        colour, op = self._paint(role)
        ink, o = c(colour), f' opacity="{fx(op)}"' if op is not None else ""
        return (f'<g{flip}{o}><path d="{arc}" fill="none" stroke="{ink}" stroke-width="{fx(max(1.2, r * .28), 2)}" '
                f'stroke-linecap="round"/><path d="{head}" fill="{ink}"/></g>', w)

class Standard(GameStandard):
    """The standard theme's Pentago: quarters of the accent's enamel, marbles of enamel lit as chess's pieces."""

    def disc_def(self, cv, material: str, r: float) -> str:
        """The id of a marble of radius `r`, drawn once in the file's defs about its own centre: its enamel face
        edged in black, the lamp across it, its groove, and on a dark one the lamp's highlight; a small one plainer."""
        key = (material, f1(r))
        cv.__dict__.setdefault("_discs", {})
        if key not in cv._discs:
            L = self.lights(cv)
            pid = cv.uid("p")
            fill, edge, _ = self.paint(material)
            g = GROOVE / DISC * r
            small = r < 7
            # a small dark marble may stand on the bare card, as a move's mark does: after dark it is edged light
            rim = "ash" if small and material == "dark" and self.dark else edge
            out = [f'<g id="{pid}"><circle r="{f1(r)}" fill="{c(fill)}" stroke="{c(rim)}" '
                   f'stroke-width="{"1.3" if not small else ".8"}"/>'
                   f'<circle r="{f1(r)}" fill="url(#{L["wp" if material == "light" else "bp"]})"/>']
            if material == "light":
                out.append(f'<circle r="{f1(g)}" fill="none" stroke="{c(edge)}" stroke-opacity=".7" '
                           f'stroke-width="{".9" if not small else ".6"}"/>')
            else:
                out.append(f'<circle r="{f1(g)}" fill="none" stroke="{c("white")}" stroke-opacity=".32" '
                           f'stroke-width="{".9" if not small else ".6"}"/>')
                if not small:
                    a, b = math.radians(-165), math.radians(-112)
                    rr = (r + g) / 2 + r * .08
                    out.append(f'<path d="M{f1(rr * math.cos(a))} {f1(rr * math.sin(a))}A{f1(rr)} {f1(rr)} 0 0 1 '
                               f'{f1(rr * math.cos(b))} {f1(rr * math.sin(b))}" fill="none" stroke="{c("white")}" '
                               f'stroke-opacity=".5" stroke-width="1.2" stroke-linecap="round"/>')
            cv.defs.append("".join(out) + "</g>")
            cv._discs[key] = pid
        return cv._discs[key]

    disc = Print.disc

    def frame_shadow(self, cv, x, y, w, h) -> None:
        """A quarter set on the card under the lamp, as chess's board is: a soft shadow by day, the accent's glow by
        night; and behind its holes the light squares' colour, so an empty hole reads apart from either marble."""
        rx = h * .02 + 6
        tone, op = self.squares()["light"]
        back = ((P.rect(x + 2, y + 2, w - 4, h - 4, "white", rx) if not self.dark else "")
                + f'<rect x="{f1(x + 2)}" y="{f1(y + 2)}" width="{f1(w - 4)}" height="{f1(h - 4)}" rx="{f1(rx)}" '
                  f'fill="{c(tone)}"' + (f' fill-opacity="{fx(op)}"/>' if op < 1 else "/>"))
        if self.dark:
            cv.add(f'<rect x="{f1(x - 10)}" y="{f1(y - 10)}" width="{f1(w + 20)}" height="{f1(h + 20)}" '
                   f'rx="{f1(rx + 8)}" fill="{c(P.ACCENT)}" fill-opacity=".07"/>'
                   f'<rect x="{f1(x - 5)}" y="{f1(y - 5)}" width="{f1(w + 10)}" height="{f1(h + 10)}" '
                   f'rx="{f1(rx + 4)}" fill="{c(P.ACCENT)}" fill-opacity=".14"/>' + back)
        else:
            cv.add(f'<rect x="{f1(x + 2)}" y="{f1(y + 7)}" width="{f1(w + 3)}" height="{f1(h + 2)}" rx="{f1(rx + 2)}" '
                   f'fill="{c("black")}" fill-opacity=".06"/>'
                   f'<rect x="{f1(x + .5)}" y="{f1(y + 3)}" width="{f1(w + 2.5)}" height="{f1(h + 1.5)}" '
                   f'rx="{f1(rx)}" fill="{c("black")}" fill-opacity=".12"/>')
        cv.add(back)

    def plate(self, cv, x, y, w, h, holes: list, pitch: float, empty: list) -> None:
        """A quarter's face: the accent's enamel cut through at every hole and lit as chess's board is, each hole's
        wall in shade on its upper left and catching the lamp on its lower right, and its edge."""
        L = self.lights(cv)
        rh = HOLE * pitch
        rx = pitch * .16
        outer = outline(x, y, w, h, rx)
        cut = "".join(circle(hx, hy, rh) for hx, hy in holes)
        cv.add(f'<path d="{outer}{cut}" fill="{c(P.ACCENT)}" fill-rule="evenodd"/>'
               f'<path d="{outer}{cut}" fill="url(#{L["bd"]})" fill-rule="evenodd"/>')
        cv.add(f'<path d="{walls(holes, rh - .9, -205, -25)}" fill="none" stroke="{c("black")}" stroke-opacity=".38" '
               f'stroke-width="1.8" stroke-linecap="round"/>'
               f'<path d="{walls(holes, rh - .6, -25, 155)}" fill="none" stroke="{c("white")}" stroke-opacity=".3" '
               f'stroke-width="1" stroke-linecap="round"/>')
        cv.add(f'<path d="{outer}" fill="none" stroke="{c(self.squares()["edge"])}" stroke-width="1.5"/>')

    def hole_ring(self, cv, cx, cy, r, appear: str = "", width: float = 2.2) -> str:
        """A hole ringed amber, as chess marks the square a piece lands on."""
        return (f'<g>{appear}<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="none" stroke="{c("amber")}" '
                f'stroke-width="{fx(width + .6, 1)}"/></g>')

    def slot(self, cx, cy) -> str:
        """A rack's empty slot, where a marble that has been set stood: a small dot, faint."""
        return (f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="1.2" fill="{c("charcoal" if self.dark else "slate")}" '
                f'fill-opacity=".45"/>')

    def connect(self, d: str, width: float, extra: str = "", anim: str = "") -> str:
        """Five marbles joined in amber, the colour the last move is marked in, edged in black so it reads across
        the quarters and the marbles."""
        return (f'<path d="{d}" fill="none" stroke="{c("black")}" stroke-width="{fx(width + 3.5, 1)}" '
                f'stroke-linecap="round"{extra}>{anim}</path>'
                f'<path d="{d}" fill="none" stroke="{c("amber")}" stroke-width="{fx(width, 1)}" '
                f'stroke-linecap="round"{extra}>{anim}</path>')


    def ghost_marble(self, cv, cx: float, cy: float, r: float) -> str:
        """A ghost: a marble of the plate's own enamel, lit as it is, ringed inside in a dashed line of light: nobody's
        marble, and plainly not one of the two sides'."""
        L = self.lights(cv)
        return (f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="{c(P.ACCENT)}" stroke="{c(self.squares()["edge"])}" '
                f'stroke-width="1.1"/><circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="url(#{L["bd"]})"/>'
                f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r * .74)}" fill="none" stroke="{c("white")}" '
                f'stroke-opacity=".75" stroke-width="1.1" stroke-dasharray="{fx(r * .32, 1)} {fx(r * .1, 1)} '
                f'{fx(r * .07, 1)} {fx(r * .1, 1)}"/>')

    def turn_mark(self, X, Y, q, qk, way, inset, appear: str = "") -> str:
        """The last quarter turn, an amber arrow round the quarter's outer corner, the colour the last move is marked
        in, edged in black so it reads across the plate."""
        shaft, head = turn_arrow(X, Y, q, qk, way, inset)
        return (f'<g>{appear}<path d="{shaft}" fill="none" stroke="{c("black")}" stroke-width="5.6" '
                f'stroke-linecap="round" stroke-linejoin="round"/><path d="{head}" fill="{c("black")}" '
                f'stroke="{c("black")}" stroke-width="2.6" stroke-linejoin="round"/><path d="{shaft}" fill="none" '
                f'stroke="{c("amber")}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
                f'<path d="{head}" fill="{c("amber")}"/></g>')

    def turn_glyph(self, x, cy, r, way, role="ink") -> tuple[str, float]:
        """A quarter turn as a move writes it: a circular arrow in the words' ink. Returns it and its width."""
        arc, head, flip, w = turn_icon(x, cy, r, way)
        ink = c(self._fill(role))
        return (f'<g{flip}><path d="{arc}" fill="none" stroke="{ink}" stroke-width="{fx(max(1.2, r * .28), 2)}" '
                f'stroke-linecap="round"/><path d="{head}" fill="{ink}"/></g>', w)
