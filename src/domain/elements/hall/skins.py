# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the Hall of Fame's sheets are made of, per theme: chess's two skins, and every game's pieces in each.

The Hall is chess-hall grown to four games, so it is drawn in chess-hall's own materials (`chess.skins`), every
medallion, medal, badge, bar and line of lettering as chess draws it, and adds what the other three games are played
with:

  standard  enamel, as chess's pieces are: a light piece white with a black edge, a dark one black with white
            detail, each under the same lamp, a shade toward the lower right or a sheen on the upper left
  print     a drawing on drafting paper, as the games' boards draw their pieces: a light piece paper edged in ink and
            line-shaded on its right, a dark one solid ink with a glint on its upper left

Each piece is drawn once in the file's defs and placed wherever it stands, at any size.
"""
from __future__ import annotations

from ...canvas import Canvas, c
from ...drafting import hair
from ...lettering import f1, fx
from ...standard import elements as SE
from ...standard import pieces as P
from ...standard.pieces import Chip
from ..chess import motion as M
from ..chess.skins import MEDALS, Plate
from ..chess.skins import Print as ChessPrint
from ..chess.skins import Standard as ChessStandard
from . import marks as K

KING = {"light": "white", "dark": "black"}  # chess's sides, by the materials the other games name them


def _defined(cv, key, build) -> str:
    """The id of a piece drawn once in the file's defs, `build` drawing it the first time it is asked for."""
    cv.__dict__.setdefault("_hall", {})
    if key not in cv._hall:
        pid = cv.uid("p")
        cv.defs.append(f'<g id="{pid}">' + build() + "</g>")
        cv._hall[key] = pid
    return cv._hall[key]


def _clip(cv, d: str) -> str:
    """A piece's outline as a clip, for the light or the shading laid inside it, defined once."""
    cv.__dict__.setdefault("_hallclips", {})
    if d not in cv._hallclips:
        cid = cv.uid("s")
        cv.defs.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
        cv._hallclips[d] = cid
    return cv._hallclips[d]


class Pieces:
    """What both skins share: a piece of any game, placed at any size, and the marks round the series' bars."""

    def piece(self, cv, game: str, material: str, x: float, y: float, size: float, *, small: bool = False) -> str:
        """A piece of `game` in `material`, light or dark, filling a box `size` square with its top-left at (x, y):
        chess's own king, or one of the other games' pieces drawn once in the file's defs (`build`). A `small` one,
        as the marks beside a winner's wins in each game set it, is drawn plainer, its milling and shading left off."""
        if game == "chess":
            return self.put(cv, "king", KING[material], x, y, size, sw=1.5 if size >= 20 else 2.2, shadow=False)
        pid = _defined(cv, (game, material, small), lambda: self.build(cv, game, material, small))
        return f'<use href="#{pid}" transform="translate({f1(x)} {f1(y)}) scale({fx(size / 45, 4)})"/>'

    def spotlight(self, cv, cx: float, cy: float, r: float) -> str:
        """Nothing: a print draws the first place's medal as it draws every other, solid."""
        return ""

    def tick(self, x: float, y0: float, y1: float) -> str:
        """The middle of a bar of the series, marked: where one side passes the other."""
        return f'<path d="M{f1(x)} {f1(y0)}V{f1(y1)}" stroke="{c(self.tick_ink)}" stroke-width="1.2"/>'


# =========================================================================== the standard theme
class Standard(Pieces, ChessStandard):
    """The standard theme's Hall: chess's enamel, and the other games' pieces lit by the same lamp."""

    def __init__(self, theme: str, dark_squares: str = "cobalt"):
        super().__init__(theme, dark_squares)
        # fill, edge, detail. After dark a black piece stands on the black card itself, not on a square, so its edge
        # catches the light in ash, as a print edges its dark pieces in the night's line; by day it is edged in black.
        rim = "ash" if self.dark else "black"
        self.PAINT = {"light": ("white", "black", "black"), "dark": ("black", rim, "white")}
        self.SIDE = {"white": ("white", "black", "black"), "black": ("black", rim, "white")}

    @property
    def tick_ink(self) -> str:
        return self.std["strong"]

    def spotlight(self, cv, cx: float, cy: float, r: float) -> str:
        """The light on the first place: a warm glow of the gold medal's own amber, falling off round it."""
        cv.__dict__.setdefault("_spot", None)
        if not cv._spot:
            cv._spot = cv.uid("g")
            gold = c("amber")
            cv.defs.append(f'<radialGradient id="{cv._spot}"><stop offset="0" stop-color="{gold}" '
                           f'stop-opacity="{".34" if self.dark else ".3"}"/><stop offset=".45" stop-color="{gold}" '
                           f'stop-opacity="{".12" if self.dark else ".1"}"/><stop offset="1" stop-color="{gold}" '
                           f'stop-opacity="0"/></radialGradient>')
        return f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r * 3.2)}" fill="url(#{cv._spot})"/>'

    def podium(self, cv, steps: list, ground: float, size: float) -> None:
        """The podium's blocks, side by side on the ground: each in its medal's metal, gold, silver and bronze, lit
        from the upper left like every medal on the sheet, its place lettered on its face at `size`. `steps` is each
        block's (x, w, h, place), place 0 for the first. By day they cast a soft shadow down and to the right."""
        L = self.lights(cv)
        if not self.dark:
            cv.add("".join(f'<rect x="{f1(x + 3)}" y="{f1(ground - h + 5)}" width="{f1(w)}" height="{f1(h - 3)}" '
                           f'fill="{c("black")}" fill-opacity=".08"/>' for x, w, h, _ in steps))
        for x, w, h, place in steps:
            tone = MEDALS[place]
            y = ground - h
            cv.add(P.rect(x, y, w, h, tone)
                   + f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(w)}" height="{f1(h)}" fill="url(#{L["mt"]})" '
                     f'fill-opacity=".55"/>'
                   + f'<path d="M{f1(x)} {f1(y + .75)}H{f1(x + w)}" stroke="{c("white")}" stroke-opacity=".55" '
                     f'stroke-width="1.5"/>')
            cv.add(SE.say(cv, str(place + 1), x=x + w / 2, y=y + h / 2 + SE.cap(size) / 2, size=size,
                          fill=P.letters_on(tone), ground=tone, anchor="middle", what="place"))

    def build(self, cv, game: str, material: str, small: bool) -> str:
        """A piece of Tic-Tac-Toe, Connect Four or Checkers in enamel, in its 45-unit box: its body filled and edged
        outside its outline, the lamp's shade or sheen laid inside it, and its detail, a disc's groove, a man's
        milling and the face's groove, with the glint of a dark one."""
        L = self.lights(cv)
        fill, edge, detail = self.PAINT[material]
        light = material == "light"
        sw = 1.6 if not small else 2.3
        glow = f'url(#{L["wp" if light else "bp"]})'
        out = []
        if game in ("tictactoe", "connectfour"):
            body = K.BODY[K.MARKS[material]] if game == "tictactoe" else K.circle(22.5, K.CY, K.DISC)
            out.append(f'<path d="{body}" fill="{c(fill)}" stroke="{c(edge)}" stroke-width="{fx(2 * sw)}" '
                       f'stroke-linejoin="round"/><path d="{body}" fill="{c(fill)}"/>'
                       f'<rect width="45" height="45" clip-path="url(#{_clip(cv, body)})" fill="{glow}"/>')
            if game == "connectfour":
                op = "1" if light else ".42"
                out.append(f'<circle cx="22.5" cy="{K.CY}" r="{K.GROOVE}" fill="none" stroke="{c(detail)}" '
                           f'stroke-width="{fx(sw * .8)}" stroke-opacity="{op}"/>')
            if not light:
                spec = K.O_SPEC if game == "tictactoe" else K.DISC_SPEC
                out.append(f'<path d="{spec}" fill="none" stroke="{c("white")}" stroke-opacity=".6" '
                           f'stroke-width="{fx(sw * .9)}" stroke-linecap="round"/>')
            return "".join(out)
        # checkers: a man, its milled side under its face
        out.append(f'<path d="{K.band()}" fill="{c(fill)}" stroke="{c(edge)}" stroke-width="{fx(sw)}" '
                   f'stroke-linejoin="round"/>')
        if not small:
            lines = K.ridges()
            for i, (x, y0, y1) in enumerate(lines):
                op = (.2 + .45 * i / len(lines)) if light else (.34 - .26 * i / len(lines))
                out.append(f'<path d="M{f1(x)} {f1(y0)}V{f1(y1)}" stroke="{c(edge if light else "white")}" '
                           f'stroke-width=".6" stroke-opacity="{fx(op, 2)}"/>')
        out.append(f'<path d="{K.ellipse(K.FACE)}" fill="{c(fill)}" stroke="{c(edge)}" stroke-width="{fx(sw)}"/>'
                   f'<rect width="45" height="45" clip-path="url(#{_clip(cv, K.silhouette())})" fill="{glow}"/>'
                   f'<path d="{K.ellipse(K.FACE, .6)}" fill="none" stroke="{c(detail)}" stroke-width="{fx(sw * .7)}" '
                   f'stroke-opacity="{"1" if light else ".45"}"/>')
        if not light:
            out.append(f'<path d="M{f1(K.CX - K.RX * .78)} {f1(K.FACE - K.RY * .38)}A{f1(K.RX * .86)} '
                       f'{f1(K.RY * .86)} 0 0 1 {f1(K.CX - K.RX * .25)} {f1(K.FACE - K.RY * .82)}" fill="none" '
                       f'stroke="{c("white")}" stroke-opacity=".6" stroke-width="{fx(sw * .8)}" '
                       f'stroke-linecap="round"/>')
        return "".join(out)

    def badge_file(self, i, p) -> str:
        """Every winner a badge of their own, so each name can link to its profile; the leader's catches the light
        every seven seconds."""
        msg = MEDALS[i] if i < 3 else "slate"
        chip = Chip(f"#{i + 1}  {p['badge']}", f"{p['wins']} win" + ("s" if p["wins"] != 1 else ""),
                    icon="trophy" if i == 0 else "medal", size=11, lab=self.std["label"], msg=msg)
        cv = P.new(chip.w, chip.h, f"Hall of Fame: {p['badge']}", f"Number {i + 1}, {p['badge']}, {p['wins']} wins",
                   f"elements hall-of-fame badge {self.theme}")
        cv.add(chip.draw(cv, 0, 0, "winner"))
        if i == 0 and M.MOTION:
            L = self.lights(cv)
            clip = cv.uid("b")
            cv.defs.append(f'<clipPath id="{clip}"><rect width="{f1(chip.w)}" height="{f1(chip.h)}"/></clipPath>')
            cv.add(f'<g clip-path="url(#{clip})"><rect x="-40" y="-4" width="34" height="{f1(chip.h + 8)}" '
                   f'fill="url(#{L["sw"]})" opacity=".0" transform="skewX(-20)">'
                   + M.ani("x", f"-40;-40;{f1(chip.w + 30)};{f1(chip.w + 30)}", "0;.8;.92;1", M.GLINT, begin=1,
                           repeat=True)
                   + M.ani("opacity", "0;0;.55;.55;0", "0;.8;.81;.92;1", M.GLINT, begin=1, repeat=True)
                   + "</rect></g>")
        return cv.svg()


# =========================================================================== a print
class Print(Pieces, ChessPrint):
    """A print's Hall: chess's drawing, and the other games' pieces drawn as their boards draw them."""

    @property
    def tick_ink(self) -> str:
        return self.col["ink"]

    def podium(self, cv, steps: list, ground: float, size: float) -> None:
        """The podium drawn in elevation, standing on the ground line: each block in the material its medal is drawn
        in, the first solid, the second lined, the third open, its place lettered on its face at `size`; its shadow
        cast down and to the right in section lining."""
        col = self.col
        line = c(col["line"])
        x0, x1 = min(s[0] for s in steps), max(s[0] + s[1] for s in steps)
        shade = "".join(f"M{f1(x + w)} {f1(ground - h + 4)}h4v{f1(h - 4)}h{f1(-w)}v4h{f1(w - 4)}Z"
                        for x, w, h, _ in steps)
        cv.add(f'<path d="{shade}" fill="url(#{self.hatch(cv, "shadow")})"/>')
        for x, w, h, place in steps:
            y = ground - h
            if place == 0:
                cv.add(f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(w)}" height="{f1(h)}" fill="{line}"/>')
            else:
                fill = f'url(#{self.hatch(cv, "bar")})' if place == 1 else c(col["paper"])
                cv.add(f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(w)}" height="{f1(h)}" fill="{c(col["paper"])}"/>'
                       f'<rect x="{f1(x + .6)}" y="{f1(y + .6)}" width="{f1(w - 1.2)}" height="{f1(h - 1.2)}" '
                       f'fill="{fill}" stroke="{line}" stroke-width="1.2"/>')
            cap = self.cap(size)
            cx, base = x + w / 2, y + h / 2 + cap / 2
            if place == 1:   # a lined block's place stands on a plate of paper, so it reads across the lining
                pw = self.width(str(place + 1), "bold", size) + 16
                cv.add(f'<rect x="{f1(cx - pw / 2)}" y="{f1(y + h / 2 - cap / 2 - 6)}" width="{f1(pw)}" '
                       f'height="{f1(cap + 12)}" fill="{c(col["paper"])}" stroke="{line}" stroke-width=".8"/>')
            ink = self.on_block if place == 0 else col["ink"]
            cv.add(cv.L.text(str(place + 1), face="num", size=size * self.K, x=cx, y=base, anchor="middle",
                             fill=c(ink)))
        cv.add(self.plotted(f'<path d="M{f1(x0)} {f1(ground)}H{f1(x1)}" fill="none" stroke="{line}" '
                             f'stroke-width="1.6"/>', x1 - x0))
        ticks = "".join(f"M{f1(x0 + 6 + i * 7)} {f1(ground + 1)}l-5 5" for i in range(int((x1 - x0 - 6) / 7) + 1))
        cv.add(f'<path d="{ticks}" fill="none" {hair(col, .5)} stroke-width=".8"/>')

    def build(self, cv, game: str, material: str, small: bool) -> str:
        """A piece of Tic-Tac-Toe, Connect Four or Checkers drawn as its board draws it, in its 45-unit box: a light
        one paper edged in ink and line-shaded toward its right, a dark one solid ink with a glint on its upper
        left; a disc's groove, a man's milling and the groove round its face."""
        light = material == "light"
        fill, edge = self.sides["white" if light else "black"]
        detail = edge if light else "white"
        e = (1.5 if not small else 2.1) * (.7 if not light and self.dark else 1)
        glint = ".35" if self.dark else ".55"
        out = []
        if game in ("tictactoe", "connectfour"):
            body = K.BODY[K.MARKS[material]] if game == "tictactoe" else K.circle(22.5, K.CY, K.DISC)
            out.append(f'<path d="{body}" fill="{c(fill)}" stroke="{c(edge)}" stroke-width="{fx(2 * e)}" '
                       f'stroke-linejoin="round"/><path d="{body}" fill="{c(fill)}"/>')
            if light and not small:
                half = K.RING + K.PEN / 2 if game == "tictactoe" else K.DISC
                out.append(f'<path d="{K.shade_lines(22.5, half, 4, 43)}" clip-path="url(#{_clip(cv, body)})" '
                           f'fill="none" stroke="{c(edge)}" stroke-width=".7" stroke-opacity=".55"/>')
            if game == "connectfour":
                if light:
                    out.append(f'<circle cx="22.5" cy="{K.CY}" r="{K.GROOVE}" fill="{c(fill)}" stroke="{c(edge)}" '
                               f'stroke-width="{fx(e * .7)}"/>')
                else:
                    out.append(f'<circle cx="22.5" cy="{K.CY}" r="{K.GROOVE}" fill="none" stroke="{c("white")}" '
                               f'stroke-opacity="{".3" if self.dark else ".42"}" stroke-width="{fx(e * .7)}"/>')
            if not light:
                spec = K.O_SPEC if game == "tictactoe" else K.DISC_SPEC
                out.append(f'<path d="{spec}" fill="none" stroke="{c("white")}" stroke-opacity="{glint}" '
                           f'stroke-width="{fx(e * .9)}" stroke-linecap="round"/>')
            return "".join(out)
        out.append(f'<path d="{K.band()}" fill="{c(fill)}" stroke="{c(edge)}" stroke-width="{fx(e)}" '
                   f'stroke-linejoin="round"/>')
        if not small:
            lines = K.ridges()
            for i, (x, y0, y1) in enumerate(lines):
                op = (.22 + .5 * i / len(lines)) if light else (.32 - .26 * i / len(lines)) * (.7 if self.dark else 1)
                out.append(f'<path d="M{f1(x)} {f1(y0)}V{f1(y1)}" stroke="{c(edge if light else "white")}" '
                           f'stroke-width=".55" stroke-opacity="{fx(op, 2)}"/>')
        gop = "1" if light else (".3" if self.dark else ".45")
        out.append(f'<path d="{K.ellipse(K.FACE)}" fill="{c(fill)}" stroke="{c(edge)}" stroke-width="{fx(e)}"/>'
                   f'<path d="{K.ellipse(K.FACE, .6)}" fill="none" stroke="{c(detail)}" stroke-width=".9" '
                   f'stroke-opacity="{gop}"/>')
        if not light:
            out.append(f'<path d="M{f1(K.CX - K.RX * .78)} {f1(K.FACE - K.RY * .38)}A{f1(K.RX * .86)} '
                       f'{f1(K.RY * .86)} 0 0 1 {f1(K.CX - K.RX * .25)} {f1(K.FACE - K.RY * .82)}" fill="none" '
                       f'stroke="{c("white")}" stroke-opacity="{glint}" stroke-width="1.2" stroke-linecap="round"/>')
        return "".join(out)

    def badge_file(self, i, p) -> str:
        """A winner's own badge: the kit's blueprint plate, on its own drafting paper; the leader's catches the
        light every seven seconds, as the standard theme's does."""
        col = self.col
        plate = Plate(self, f"#{i + 1}  {p['badge']}", f"{p['wins']} win" + ("s" if p["wins"] != 1 else ""),
                      icon="trophy" if i == 0 else "medal", size=11)
        cv = Canvas(plate.w, plate.h, title=f"Hall of Fame: {p['badge']}",
                    desc=f"Number {i + 1}, {p['badge']}, {p['wins']} wins",
                    stamp=f"{self.tone} elements hall-of-fame badge {self.theme}")
        grid = cv.uid("p")
        cv.defs.append(f'<pattern id="{grid}" width="10" height="10" patternUnits="userSpaceOnUse">'
                       f'<path d="M10 .5H.5V10" fill="none" {hair(col, .085 if self.dark else .08)}/></pattern>')
        whole = f'width="{f1(plate.w)}" height="{f1(plate.h)}"'
        cv.add(f'<rect {whole} fill="{c(col["paper"])}"/>'
               + ("" if self.dark else f'<rect {whole} fill="{c(col["edge"])}" fill-opacity=".03"/>')
               + f'<rect {whole} fill="url(#{grid})"/>')
        cv.add(plate.draw(cv, 0, 0, "winner").replace(f'fill="{c(col["paper"])}" stroke=', 'fill="none" stroke=', 1))
        if i == 0 and M.MOTION:
            clip = cv.uid("b")
            cv.defs.append(f'<clipPath id="{clip}"><rect width="{f1(plate.w)}" height="{f1(plate.h)}"/></clipPath>')
            cv.add(f'<g clip-path="url(#{clip})"><rect x="-40" y="-4" width="34" height="{f1(plate.h + 8)}" '
                   f'fill="url(#{self.grad(cv, "sl")})" opacity=".0" transform="skewX(-20)">'
                   + M.ani("x", f"-40;-40;{f1(plate.w + 30)};{f1(plate.w + 30)}", "0;.8;.92;1", M.GLINT, begin=1,
                           repeat=True)
                   + M.ani("opacity", "0;0;.3;.3;0", "0;.8;.81;.92;1", M.GLINT, begin=1, repeat=True)
                   + "</rect></g>")
        return cv.svg()
