# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the Checkers sheet is made of, per theme: the standard theme's enamel and a print's drawing, as chess's
sheets are (`games.skin`), with the men's own materials.

The board is chess's board, drawn by chess's own skin in either material (its squares, its light and its edge),
with each dark square's number set on a tab in its corner, as a numbered drawing tags its parts.

  standard  the men enamel, lit as chess's pieces are: a White man white edged in black, its milled side shaded
            heavier toward the right; a Black man black, its ridges and groove catching the lamp, with a highlight
            on its upper left; the square a man set out from and the one it landed on amber, as chess marks a move,
            a man that must jump glowing red as chess's king in check, a jump's path in amber
  print     a White man paper edged in ink, its milled side shaded heavier toward the right, as a white chessman is;
            a Black man solid ink, its ridges and its groove catching the light, with a glint on its upper left;
            where a man stood drawn in phantom lines, as chess draws where its piece stood, and a jump's path a
            chain line through every square it lands on
"""
from __future__ import annotations

from ...canvas import c
from ...drafting import hair
from ...lettering import f1, fx
from ...standard import pieces as P
from ..games.skin import Print as GamePrint
from ..games.skin import Standard as GameStandard
from .shapes import CROWN, CROWN_FACE, CX, FACE, GROOVE, RX, RY, SHADOW, band, ellipse, ridges, silhouette


def phantom(king: bool, x: float, y: float, s: float, colour: str, op: str, width: float) -> str:
    """A man in phantom lines, long and short dashes, as they stand on the sheet whatever the board's size."""
    k = s / 45
    return (f'<path d="{silhouette(king)}" transform="translate({f1(x)} {f1(y)}) scale({fx(k, 4)})" fill="none" '
            f'stroke="{c(colour)}" stroke-width="{fx(width / k, 2)}" stroke-opacity="{op}" '
            f'stroke-dasharray="{fx(4 / k, 2)} {fx(1.4 / k, 2)} {fx(1 / k, 2)} {fx(1.4 / k, 2)}" '
            f'stroke-linejoin="round"/>')


class Men:
    """The men, in whichever material the skin gives them: a man is drawn once in the file's defs and used."""

    def man_def(self, cv, material: str, king: bool, *, shadow: bool = True, top_only: bool = False) -> str:
        """The id of a man, or a king, drawn once in the file's defs in its 45-unit box, its shadow at its foot.
        `top_only` is a king's upper man alone: what is dropped onto a man to crown it."""
        key = (material, king, shadow, top_only)
        cv.__dict__.setdefault("_men", {})
        if key not in cv._men:
            pid = cv.uid("p")
            g = [f'<g id="{pid}">']
            if shadow and not top_only:
                g.append(self.man_shadow(cv))
            if not top_only:
                g.append(self.man_part(cv, material, FACE))
            if king or top_only:
                g.append(self.man_part(cv, material, CROWN_FACE, crown=True))
            cv.defs.append("".join(g) + "</g>")
            cv._men[key] = pid
        return cv._men[key]

    def man(self, cv, material: str, king: bool, x: float, y: float, s: float, **k) -> str:
        """A man or a king standing on a square `s` wide whose top-left is (x, y)."""
        return (f'<use href="#{self.man_def(cv, material, king, **k)}" transform="translate({f1(x)} {f1(y)}) '
                f'scale({fx(s / 45, 4)})"/>')


class Print(Men, GamePrint):
    """A print's Checkers: chess's board, numbered, and men that stand on it as chess's pieces do."""

    def man_shadow(self, cv) -> str:
        return (f'<ellipse cx="{fx(SHADOW[0], 2)}" cy="{fx(SHADOW[1], 2)}" rx="{fx(SHADOW[2], 2)}" '
                f'ry="{fx(SHADOW[3], 2)}" fill="{c(self.shade)}" fill-opacity="{self.shadow_op}"/>')

    def man_part(self, cv, material: str, face: float, *, crown: bool = False, sw: float = 1.5) -> str:
        """One man of a stack, its face centred at `face` in the 45-unit box: its side, its ridges, its face, its
        groove, and on a king's upper man its crown."""
        fill, edge, detail = self.paint(material)
        esw = sw * .7 if material == "dark" and self.dark else sw
        out = [f'<path d="{band(face)}" fill="{c(fill)}" stroke="{c(edge)}" stroke-width="{fx(esw, 2)}" '
               f'stroke-linejoin="round"/>']
        lines = ridges(face)
        n = len(lines)
        if material == "light":
            # milled ridges, heavier toward the right, where the side turns from the lamp
            for i, (x, y0, y1) in enumerate(lines):
                out.append(f'<path d="M{f1(x)} {f1(y0)}V{f1(y1)}" stroke="{c(edge)}" stroke-width=".55" '
                           f'stroke-opacity="{fx(.22 + .5 * i / n, 2)}"/>')
        else:
            for i, (x, y0, y1) in enumerate(lines):
                op = .32 - .26 * i / n
                out.append(f'<path d="M{f1(x)} {f1(y0)}V{f1(y1)}" stroke="{c("white")}" stroke-width=".55" '
                           f'stroke-opacity="{fx(op * (.7 if self.dark else 1), 2)}"/>')
        out.append(f'<path d="{ellipse(face)}" fill="{c(fill)}" stroke="{c(edge)}" stroke-width="{fx(esw, 2)}"/>')
        groove = c(edge) if material == "light" else c("white")
        gop = "1" if material == "light" else (".3" if self.dark else ".45")
        out.append(f'<path d="{ellipse(face, GROOVE)}" fill="none" stroke="{groove}" stroke-width=".9" '
                   f'stroke-opacity="{gop}"/>')
        if material == "dark":
            out.append(f'<path d="M{f1(CX - RX * .78)} {f1(face - RY * .38)}A{f1(RX * .86)} {f1(RY * .86)} 0 0 1 '
                       f'{f1(CX - RX * .25)} {f1(face - RY * .82)}" fill="none" stroke="{c("white")}" '
                       f'stroke-opacity="{".35" if self.dark else ".55"}" stroke-width="1.2" stroke-linecap="round"/>')
        if crown:
            out.append(f'<path d="{CROWN}" transform="translate({CX} {fx(face - .2, 2)}) scale(1 .62)" '
                       f'fill="{c(detail)}" fill-opacity="{".9" if material == "light" else ".85"}"/>')
        return "".join(out)

    def phantom_man(self, x: float, y: float, s: float, king: bool = False) -> str:
        """A man in phantom lines, long and short dashes: where it stood before it moved, or was taken."""
        return phantom(king, x, y, s, self.mark, ".85", 1.1)

    def from_square(self, cv, x, y, s, king: bool) -> None:
        """Where the last move's man set out from: its square opened to the paper, a dashed box, and the man in
        phantom lines, as chess marks where its piece stood."""
        cv.add(f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(s)}" height="{f1(s)}" fill="{c(self.col["paper"])}"/>'
               f'<rect x="{f1(x + 3)}" y="{f1(y + 3)}" width="{f1(s - 6)}" height="{f1(s - 6)}" fill="none" '
               f'stroke="{c(self.mark)}" stroke-opacity=".8" stroke-dasharray="6 2 1.5 2"/>'
               + self.phantom_man(x, y, s, king))

    def taken_square(self, cv, x, y, s) -> None:
        """A square a jump took a man from: opened to the paper and crossed out fine, as a drawing strikes a part
        that is gone."""
        i = s * .2
        cv.add(f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(s)}" height="{f1(s)}" fill="{c(self.col["paper"])}"/>'
               f'<path d="M{f1(x + i)} {f1(y + i)}L{f1(x + s - i)} {f1(y + s - i)}M{f1(x + s - i)} {f1(y + i)}'
               f'L{f1(x + i)} {f1(y + s - i)}" fill="none" stroke="{c(self.mark)}" stroke-opacity=".35" '
               f'stroke-width=".8"/>')

    def tab(self, cv, n: int, x: float, y: float, size: float) -> str:
        """A dark square's number on a tab of paper in its corner, as a drawing tags its parts."""
        text = str(n)
        w = self.width(text, "bold", size) + 4.4
        h = self.cap(size) + 4
        return (f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(w)}" height="{f1(h)}" fill="{c(self.col["paper"])}" '
                f'{hair(self.col, .45)} stroke-width=".6"/>'
                + self.say(cv, text, x + w / 2, y + h - 2, size, role="muted", anchor="middle"))

    def chain(self, d: str, mask: str = "") -> str:
        """A jump's path, as a drawing shows a part's travel: a chain line, long and short dashes."""
        m = f' mask="url(#{mask})"' if mask else ""
        return (f'<g{m}><path d="{d}" fill="none" stroke="{c(self.col["paper"])}" stroke-width="4.2" '
                f'stroke-linecap="round" stroke-linejoin="round" stroke-opacity=".9"/>'
                f'<path d="{d}" fill="none" stroke="{c(self.mark)}" stroke-width="1.6" stroke-dasharray="9 3 2 3" '
                f'stroke-linecap="round" stroke-linejoin="round"/></g>')

    def landing(self, cx, cy, r) -> str:
        """A point a jump lands on along its way: a small ring on the path."""
        return (f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="{c(self.col["paper"])}" '
                f'stroke="{c(self.mark)}" stroke-width="1.4"/>')


class Standard(Men, GameStandard):
    """The standard theme's Checkers: chess's standard board, numbered, and men of enamel lit as its pieces are."""

    def man_shadow(self, cv) -> str:
        return (f'<ellipse cx="{fx(SHADOW[0], 2)}" cy="{fx(SHADOW[1], 2)}" rx="{fx(SHADOW[2], 2)}" '
                f'ry="{fx(SHADOW[3], 2)}" fill="url(#{self.lights(cv)["sh"]})"/>')

    def man_part(self, cv, material: str, face: float, *, crown: bool = False, sw: float = 1.5) -> str:
        """One man of a stack, in enamel: its side milled and shaded away from the lamp, its face, its groove, the
        lamp across it, and on a king's upper man its crown."""
        L = self.lights(cv)
        fill, edge, detail = self.paint(material)
        out = [f'<path d="{band(face)}" fill="{c(fill)}" stroke="{c(edge)}" stroke-width="{fx(sw, 2)}" '
               f'stroke-linejoin="round"/>']
        lines = ridges(face)
        n = len(lines)
        for i, (x, y0, y1) in enumerate(lines):
            if material == "light":
                out.append(f'<path d="M{f1(x)} {f1(y0)}V{f1(y1)}" stroke="{c(edge)}" stroke-width=".55" '
                           f'stroke-opacity="{fx(.18 + .5 * i / n, 2)}"/>')
            else:
                out.append(f'<path d="M{f1(x)} {f1(y0)}V{f1(y1)}" stroke="{c("white")}" stroke-width=".55" '
                           f'stroke-opacity="{fx(.4 - .3 * i / n, 2)}"/>')
        out.append(f'<path d="{ellipse(face)}" fill="{c(fill)}" stroke="{c(edge)}" stroke-width="{fx(sw, 2)}"/>'
                   f'<path d="{ellipse(face)}" fill="url(#{L["wp" if material == "light" else "bp"]})"/>')
        groove = c(edge if material == "light" else "white")
        out.append(f'<path d="{ellipse(face, GROOVE)}" fill="none" stroke="{groove}"'
                   f' stroke-width=".9" stroke-opacity="{".75" if material == "light" else ".35"}"/>')
        if material == "dark":
            out.append(f'<path d="M{f1(CX - RX * .78)} {f1(face - RY * .38)}A{f1(RX * .86)} {f1(RY * .86)} 0 0 1 '
                       f'{f1(CX - RX * .25)} {f1(face - RY * .82)}" fill="none" stroke="{c("white")}" '
                       f'stroke-opacity=".5" stroke-width="1.2" stroke-linecap="round"/>')
        if crown:
            out.append(f'<path d="{CROWN}" transform="translate({CX} {fx(face - .2, 2)}) scale(1 .62)" '
                       f'fill="{c(detail)}" fill-opacity="{".9" if material == "light" else ".85"}"/>')
        return "".join(out)

    def phantom_man(self, x: float, y: float, s: float, king: bool = False) -> str:
        """A man in phantom lines, white on the dark square it stood on: where a jump took it."""
        return phantom(king, x, y, s, "white", ".9", 1.3)

    def from_square(self, cv, x, y, s, king: bool) -> None:
        """Where the last move's man set out from, amber, as chess marks where its piece stood."""
        self.mark_from(cv, x, y, s, None)

    def taken_square(self, cv, x, y, s) -> None:
        """A square a jump took a man from: the man stood there is drawn in phantom lines over it."""

    def tab(self, cv, n: int, x: float, y: float, size: float) -> str:
        """A dark square's number on a tab of the paper in its corner, as a drawing tags its parts."""
        text = str(n)
        w = self.width(text, "bold", size) + 4.4
        h = self.cap(size) + 4
        return (P.rect(x, y, w, h, self.std["paper"], 1.5)
                + self.say(cv, text, x + w / 2, y + h - 2, size, role="muted", anchor="middle", what="square"))

    def chain(self, d: str, mask: str = "") -> str:
        """A jump's path, in amber, the colour of the last move, through every square it lands on."""
        m = f' mask="url(#{mask})"' if mask else ""
        return (f'<g{m}><path d="{d}" fill="none" stroke="{c(self.std["paper"])}" stroke-width="5" '
                f'stroke-linecap="round" stroke-linejoin="round" stroke-opacity=".85"/>'
                f'<path d="{d}" fill="none" stroke="{c("amber")}" stroke-width="2.2" stroke-dasharray="9 3 2 3" '
                f'stroke-linecap="round" stroke-linejoin="round"/></g>')

    def landing(self, cx, cy, r) -> str:
        """A point a jump lands on along its way: a small ring on the path."""
        return (f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="{c(self.std["paper"])}" '
                f'stroke="{c("amber")}" stroke-width="1.6"/>')
