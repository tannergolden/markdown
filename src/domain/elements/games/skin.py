# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: LicenseRef-Proprietary
"""The two materials every game's sheet is drawn in: chess's skins, and what a game beside chess adds to them.

Everything chess's skins draw (the sheet and its band or title strip, the rules, the badges and plates, the
medallions, the lettering, the board's light and the plotter) is used as it is. A game adds the same few things to
each, so the four games are one hand in either material:

  words fitted to room   a name, a login or a number at the largest size that fits, down to a floor, and past the
                         floor cut with an ellipsis, as chess fits its own, so nothing on a sheet runs into anything
  the two materials      what chess calls white and black, a game calls light and dark, whatever it plays with:
                         lit white enamel edged in black, or black enamel with the lamp's highlight on it, in the
                         standard theme; paper edged in ink and shaded, or solid ink with a glint, on a print
  a side's medallion     the disc a side's mark is set in: enamel of the other colour, or a print's dial
  what must be looked at a square the rules make the side to move answer, a man that must jump, glowing red as
                         chess's king in check does, or clouded as a print clouds it, and the ring a landing move
                         sends out
"""
from __future__ import annotations

from ...canvas import c
from ...lettering import f1, fx
from ..chess import motion as M
from ..chess.layout import fitting
from ..chess.skins import Print as ChessPrint
from ..chess.skins import Standard as ChessStandard

ELLIPSIS = "…"


class Hand:
    """What every game's skin adds to chess's, the same in both materials."""

    material: dict[str, tuple[str, str, str]]

    # --- lettering, fitted
    def fit(self, s, face: str, size: float, floor: float, room: float, ls: float = 0.0) -> tuple[str, float]:
        """`s` at the largest size, a quarter point at a time from `size` down to `floor`, that fits `room`, and cut
        at the floor with an ellipsis if even that is not enough, as chess fits its words. (what to letter, size)"""
        if room <= self.width(ELLIPSIS, face, floor, ls):
            return "", floor
        return fitting(self, str(s), face, size, floor, room, ls)

    def said(self, cv, s, x, y, size, floor, room, *, role="ink", face="bold", anchor="start",
             ls=0.0) -> tuple[str, float]:
        """A name, a figure or a move, fitted to `room`; returns the markup and the width it took."""
        text, size = self.fit(s, face, size, floor, room, ls)
        return (self.say(cv, text, x, y, size, role=role, face=face, anchor=anchor, ls=ls),
                self.width(text, face, size, ls))

    def capped(self, cv, s, x, y, size, floor, room, *, role=None, anchor="start", ls=.8) -> tuple[str, float]:
        """A line of capitals, fitted to `room`; returns the markup and the width it took."""
        text, size = self.fit(s, "caps", size, floor, room, ls)
        return (self.caps(cv, text, x, y, size, role=role, anchor=anchor, ls=ls),
                self.width(text.upper(), "caps", size, ls))

    # --- the two materials
    def paint(self, material: str) -> tuple[str, str, str]:
        """A side's material as palette tokens: its fill, its edge and the colour of what is cut into it."""
        return self.material[material]

    # --- what every board marks
    def ripple_at(self, cx: float, cy: float, r0: float, r1: float, at: float, *, clip: str = "") -> str:
        """The ring that runs out from where a move lands, `at` seconds in, as chess's landing sends one out."""
        if not M.MOTION:
            return ""
        t = at + .9
        k = fx(at / t, 3)
        g = f'<g clip-path="url(#{clip})">' if clip else "<g>"
        return (f'{g}<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r0)}" fill="none" {self.ripple} opacity="0">'
                + M.ani("r", f"{f1(r0)};{f1(r0)};{f1(r1)};{f1(r1)}", f"0;{k};.98;1", t)
                + M.ani("opacity", "0;0;.9;0;0", f"0;{k};{fx(at / t + .02, 3)};.98;1", t)
                + "</circle></g>")


class Print(Hand, ChessPrint):
    """Chess's print, with the light and dark materials, a side's dial and the revision cloud a game needs."""

    def __init__(self, theme: str, tone: str = "blackprint"):
        super().__init__(theme, tone)
        light, dark = self.sides["white"], self.sides["black"]
        # (fill, edge, detail): the light side paper edged in ink, the dark side solid ink edged in the night's line
        self.material = {"light": (light[0], light[1], light[1]), "dark": (dark[0], dark[1], "white")}

    def medal(self, cv, cx: float, cy: float, r: float, material: str) -> str:
        """A side's medallion before anything is set in it: chess's ring and its dial of ticks."""
        return self.dial(cx, cy, r)

    def clouded(self, cv, x: float, y: float, side: float, pulse: str, *, clip: str = "") -> str:
        """A revision cloud round a square `side` wide at (x, y), as chess clouds a king in check: what the rules make
        the side to move look at. It blooms and pulses on `pulse`."""
        g = f'<g clip-path="url(#{clip})">' if clip else "<g>"
        return (f'{g}<g>{pulse}<path d="{self.cloud(x, y, side)}" fill="none" stroke="{c(self.mark)}" '
                f'stroke-width="1.5" stroke-linejoin="round"/></g></g>')


class Standard(Hand, ChessStandard):
    """Chess's standard skin, with the light and dark enamels, a side's medallion and the check's red glow."""

    def __init__(self, theme: str):
        super().__init__(theme)
        self.material = {"light": self.SIDE["white"], "dark": self.SIDE["black"]}

    def medal(self, cv, cx: float, cy: float, r: float, material: str) -> str:
        """A side's medallion: enamel of the colour that sets its pieces off, as chess sets its kings."""
        return self.enamel(cv, cx, cy, r, self.std["label"] if material == "light" else "ash")

    def clouded(self, cv, x: float, y: float, side: float, pulse: str, *, clip: str = "") -> str:
        """The red glow chess's king in check stands in, round a square `side` wide at (x, y): what the rules make the
        side to move look at. It blooms and pulses on `pulse`."""
        L = self.lights(cv)
        cx, cy = x + side / 2, y + side / 2
        g = f'<g clip-path="url(#{clip})">' if clip else "<g>"
        return (f'{g}<g>{pulse}<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(side * .86)}" fill="url(#{L["ck"]})"/>'
                f'<rect x="{f1(x + 1.5)}" y="{f1(y + 1.5)}" width="{f1(side - 3)}" height="{f1(side - 3)}" '
                f'fill="none" stroke="{c("crimson")}" stroke-width="2.5"/></g></g>')
