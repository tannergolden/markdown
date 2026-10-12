# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the Connect Four sheet is made of, per theme: the standard theme's enamel and a print's drawing, as chess's
sheets are (`games.skin`), with the frame's and the discs' own materials.

  standard  the frame in the theme's cobalt enamel, the colour of chess's dark squares, lit from the upper left as
            chess's board is, every hole cut clean through it and its wall in shade on the side the lamp misses; two
            legs on a ground line; the discs enamel, light ones lit white edged in black and dark ones black with the
            lamp's highlight, as chess's pieces are; the last disc's hole ringed amber, a hole to block glowing red as
            chess's king in check, a won line joined in amber
  print     the frame drawn in elevation, as a part standing on the ground is: its face in section lining, as chess
            lines its dark squares, every hole cut through it with a centre mark while it is empty and a shade line
            on the side the lamp misses; two legs on a ground line hatched beneath; the whole casting its shadow down
            and to the right; a light disc paper edged in ink and line-shaded, a dark one solid ink with a glint
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

ARROW = 7                  # the arrow over the column the last disc went in: its head's length


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


def leg_path(legs: list, top: float) -> str:
    return "".join(f"M{f1(lx)} {f1(top)}h{f1(lw)}l{f1(lw * .18)} {f1(lh)}h{f1(-lw * 1.36)}Z" for lx, lw, lh in legs)


def arrow(cx: float, top: float) -> str:
    """The arrow over the frame where the last disc went in: its shaft and its head, as path data, apart."""
    return f"M{f1(cx)} {f1(top - 14)}V{f1(top - 6)}", f"M{f1(cx)} {f1(top)}l-3.2 -{ARROW}h6.4z"


class Print(GamePrint):
    """A print's Connect Four: the frame in elevation, the discs behind it."""

    def disc_def(self, cv, material: str, r: float) -> str:
        """The id of a disc of radius `r`, drawn once in the file's defs about its own centre: its face edged, its
        groove, and its shading or glint; a small one plain, its face and its groove alone."""
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
        """A disc seen face on, centred at (cx, cy), `r` its radius (a frame's disc unless given)."""
        r = r if r is not None else DISC * pitch
        return f'<use href="#{self.disc_def(cv, material, r)}" x="{f1(cx)}" y="{f1(cy)}"/>'

    def frame_shadow(self, cv, x, y, w, h, legs) -> None:
        """The frame's shadow, cast down and to the right in section lining, as chess's board casts its own."""
        d = (f"M{f1(x + w)} {f1(y + 5)}h5v{f1(h - 1)}h{f1(-w + 1)}v-5h{f1(w - 6)}Z"
             + "".join(f"M{f1(lx + lw)} {f1(y + h + 4)}h4v{f1(lh)}h-4Z" for lx, lw, lh in legs))
        cv.add(f'<path d="{d}" fill="url(#{self.hatch(cv, "shadow")})"/>')

    def plate(self, cv, x, y, w, h, holes: list, pitch: float, empty: list) -> None:
        """The frame's face: paper cut through at every hole, lined, edged; each hole edged fine and shaded heavy
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

    def legs(self, cv, legs: list, top: float) -> None:
        """The legs the frame stands on, lined as its face is, and heavier on their shaded sides."""
        d = leg_path(legs, top)
        cv.add(f'<path d="{d}" fill="{c(self.col["paper"])}"/><path d="{d}" fill="url(#{self.hatch(cv, "square")})" '
               f'stroke="{c(self.col["line"])}" stroke-width="1.3" stroke-linejoin="round"/>')

    def ground(self, cv, x0, x1, y) -> None:
        """The ground the frame stands on, as an elevation draws it: a line, and short strokes slanting under it."""
        ticks = "".join(f"M{f1(x0 + 6 + i * 7)} {f1(y + 1)}l-5 5" for i in range(int((x1 - x0 - 6) / 7) + 1))
        cv.add(f'<path d="M{f1(x0)} {f1(y)}H{f1(x1)}" fill="none" stroke="{c(self.col["line"])}" stroke-width="1.4"/>'
               f'<path d="{ticks}" fill="none" {hair(self.col, .5)} stroke-width=".8"/>')

    def hole_ring(self, cv, cx, cy, r, appear: str = "", width: float = 2.2) -> str:
        """A hole ringed heavy, as chess boxes the square a piece lands on."""
        return (f'<g>{appear}<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="none" stroke="{c(self.mark)}" '
                f'stroke-width="{fx(width, 1)}"/></g>')

    def phantom_disc(self, cx, cy, r) -> str:
        """A disc in phantom lines, long and short dashes: where a threatened disc would land."""
        return (f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="none" stroke="{c(self.mark)}" '
                f'stroke-width="1.1" stroke-opacity=".85" stroke-dasharray="4 1.4 1 1.4"/>')

    def slot(self, cx, cy) -> str:
        """A rack's empty slot, where a disc that has been dropped stood: a small mark, faint."""
        return (f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="1.1" fill="{c(self.col["ink"])}" '
                f'fill-opacity="{".3" if self.dark else ".28"}"/>')

    def connect(self, d: str, width: float, extra: str = "", anim: str = "") -> str:
        """Four discs joined, as a drawing joins the parts of an assembly: a band of paper, then the line."""
        return (f'<path d="{d}" fill="none" stroke="{c(self.col["paper"])}" stroke-width="{fx(width + 5, 1)}" '
                f'stroke-linecap="round"{extra}>{anim}</path>'
                f'<path d="{d}" fill="none" stroke="{c(self.mark)}" stroke-width="{fx(width, 1)}" '
                f'stroke-linecap="round"{extra}>{anim}</path>')

    def column_mark(self, cv, col: int, cx: float, under: float, top: float, size: float, appear: str) -> str:
        """The column the last disc fell down: its number set solid, as the strip sets its cells, and an arrow over
        the frame where the disc went in, drawn as a drawing shows a part's travel."""
        w, h = 15, 13
        shaft, head = arrow(cx, top)
        return (f'<g>{appear}<rect x="{f1(cx - w / 2)}" y="{f1(under - h + 2.6)}" width="{w}" height="{h}" '
                f'fill="{c(self.col["line"])}"/>'
                + self.say(cv, str(col), cx, under, size, role="block", anchor="middle")
                + f'<path d="{shaft}" fill="none" stroke="{c(self.mark)}" stroke-width="1.2"/>'
                  f'<path d="{head}" fill="{c(self.mark)}"/></g>')


class Standard(GameStandard):
    """The standard theme's Connect Four: a frame of the accent's enamel, discs of enamel lit as chess's pieces."""

    def disc_def(self, cv, material: str, r: float) -> str:
        """The id of a disc of radius `r`, drawn once in the file's defs about its own centre: its enamel face edged
        in black, the lamp across it, its groove, and on a dark one the lamp's highlight; a small one plainer."""
        key = (material, f1(r))
        cv.__dict__.setdefault("_discs", {})
        if key not in cv._discs:
            L = self.lights(cv)
            pid = cv.uid("p")
            fill, edge, _ = self.paint(material)
            g = GROOVE / DISC * r
            small = r < 7
            # a small dark disc may stand on the bare card, as a move's mark does: after dark it is edged light
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

    def frame_shadow(self, cv, x, y, w, h, legs) -> None:
        """The frame set on the card under the lamp, as chess's board is: a soft shadow by day, the accent's glow by
        night; and behind its holes the light squares' colour, so an empty hole reads apart from either disc."""
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
        """The frame's face: the accent's enamel cut through at every hole and lit as chess's board is, each hole's
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

    def legs(self, cv, legs: list, top: float) -> None:
        """The legs the frame stands on, of its enamel, edged."""
        L = self.lights(cv)
        d = leg_path(legs, top)
        cv.add(f'<path d="{d}" fill="{c(P.ACCENT)}"/><path d="{d}" fill="url(#{L["bd"]})" '
               f'stroke="{c(self.squares()["edge"])}" stroke-width="1.3" stroke-linejoin="round"/>')

    def ground(self, cv, x0, x1, y) -> None:
        """The ground the frame stands on: a line, and the frame's shadow along it."""
        cv.add(f'<path d="M{f1(x0 + 4)} {f1(y + 2.5)}H{f1(x1 - 4)}" fill="none" stroke="{c("black")}" '
               f'stroke-opacity="{".45" if self.dark else ".1"}" stroke-width="5" stroke-linecap="round"/>'
               f'<path d="M{f1(x0)} {f1(y)}H{f1(x1)}" fill="none" stroke="{c(self.squares()["edge"])}" '
               f'stroke-width="1.4" stroke-linecap="round"/>')

    def hole_ring(self, cv, cx, cy, r, appear: str = "", width: float = 2.2) -> str:
        """A hole ringed amber, as chess marks the square a piece lands on."""
        return (f'<g>{appear}<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="none" stroke="{c("amber")}" '
                f'stroke-width="{fx(width + .6, 1)}"/></g>')

    def phantom_disc(self, cx, cy, r) -> str:
        """A disc in phantom lines, white on the red glow: where a threatened disc would land."""
        return (f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="none" stroke="{c("white")}" '
                f'stroke-width="1.4" stroke-opacity=".9" stroke-dasharray="4 1.4 1 1.4"/>')

    def slot(self, cx, cy) -> str:
        """A rack's empty slot, where a disc that has been dropped stood: a small dot, faint."""
        return (f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="1.2" fill="{c("charcoal" if self.dark else "slate")}" '
                f'fill-opacity=".45"/>')

    def connect(self, d: str, width: float, extra: str = "", anim: str = "") -> str:
        """Four discs joined in amber, the colour the last move is marked in, edged in black so it reads across the
        frame and the discs."""
        return (f'<path d="{d}" fill="none" stroke="{c("black")}" stroke-width="{fx(width + 3.5, 1)}" '
                f'stroke-linecap="round"{extra}>{anim}</path>'
                f'<path d="{d}" fill="none" stroke="{c("amber")}" stroke-width="{fx(width, 1)}" '
                f'stroke-linecap="round"{extra}>{anim}</path>')

    def column_mark(self, cv, col: int, cx: float, under: float, top: float, size: float, appear: str) -> str:
        """The column the last disc fell down: its number on an amber block, the colour of the last move, and an
        arrow over the frame where the disc went in."""
        w, h = 15, 13
        shaft, head = arrow(cx, top)
        ink = c(self.std["strong"])
        return (f'<g>{appear}' + P.rect(cx - w / 2, under - h + 2.6, w, h, "amber")
                + P.text(cv, str(col), x=cx, y=under, size=size, face="sans-bold", fill=P.letters_on("amber"),
                         ground="amber", anchor="middle", what="column")
                + f'<path d="{shaft}" fill="none" stroke="{ink}" stroke-width="1.2"/><path d="{head}" fill="{ink}"/>'
                  "</g>")
