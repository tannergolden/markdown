# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the chess sheets are made of, per theme: the standard theme's skin and the prints'.

`layout` places every part; a skin draws it. The two skins answer the same questions (a square, a piece, a
medallion, a badge, a rule, a line of capitals) at the same places, so the sheets they make have one layout and
two materials:

  standard  the badges' language: enamel and lit pieces on a card under a black band, cobalt and amber
  print     a drawing: ink on drafting paper, poché for the dark squares, line shading for the light, a phantom
            for where a piece stood, a revision cloud round a king in check, plates for badges

The light is the same lamp in both, up and to the left: the standard theme paints it, a print draws it, with
heavier lines on the sides the lamp does not reach and section lining where its shadow falls.
"""
from __future__ import annotations

import math

from ...canvas import DARK, DAY, Canvas, c
from ...draw import icon
from ...drafting import hair, sheet
from ...lettering import cap_height, f1, fx, width
from ...palette import PALETTE, letters_on
from ...palette import contrast as _contrast
from ...prints import PRINTS, colours
from ...standard import elements as SE
from ...standard import pieces as P
from ...standard.pieces import Chip
from .. import draw as E
from . import motion as M
from .shapes import BASE_SPEC, DETAIL, DOTS, FOOT, PARTS, SPEC

BAND, PAD = 40, 20
MEDALS = ("amber", "ash", "clay")
FACES = ("crimson", "tangerine", "ocean", "forest", "purple", "magenta")


# =========================================================================== the standard theme
def lights(cv, std: dict) -> dict:
    """The file's light, defined once: the shade on a white piece and the sheen on a black one, the soft shadow at
    a piece's foot, the board's surface, the check's glow, the enamel of a medallion, the metal of a medal and the
    band of a glint. Every stop is a palette token at an opacity, as the palette asks of a lighter shade."""
    if getattr(cv, "_lights", None):
        return cv._lights
    night = std["dark"]
    L = {k: cv.uid("g") for k in ("wp", "bp", "sh", "bd", "ck", "en", "mt", "sw")}
    W, B, R = c("white"), c("black"), c("crimson")

    def stops(*s):
        return "".join(f'<stop offset="{o}" stop-color="{col}" stop-opacity="{op}"/>' for o, col, op in s)

    cv.defs.append(
        f'<linearGradient id="{L["wp"]}" x1="0" y1="0" x2="1" y2="1">'
        + stops((".4", B, "0"), ("1", B, ".36")) + "</linearGradient>"
        + f'<linearGradient id="{L["bp"]}" x1="0" y1="0" x2="1" y2="1">'
        + stops(("0", W, ".42"), (".42", W, "0")) + "</linearGradient>"
        + f'<radialGradient id="{L["sh"]}">'
        + stops(("0", B, ".5" if not night else ".6"), (".55", B, ".22"), ("1", B, "0")) + "</radialGradient>"
        + f'<linearGradient id="{L["bd"]}" x1="0" y1="0" x2="1" y2="1">'
        + stops(("0", W, ".2" if not night else ".14"), (".45", W, "0"), (".58", B, "0"),
                ("1", B, ".16" if not night else ".24")) + "</linearGradient>"
        + f'<radialGradient id="{L["ck"]}">'
        + stops(("0", R, "1"), (".55", R, ".78"), ("1", R, "0")) + "</radialGradient>"
        + f'<radialGradient id="{L["en"]}" fx=".3" fy=".24" r=".78">'
        + stops(("0", W, ".55"), (".42", W, "0"), (".78", B, "0"), ("1", B, ".24")) + "</radialGradient>"
        + f'<linearGradient id="{L["mt"]}" x1="0" y1="0" x2="1" y2="1">'
        + stops(("0", W, ".8"), (".36", W, "0"), (".64", B, "0"), ("1", B, ".38")) + "</linearGradient>"
        + f'<linearGradient id="{L["sw"]}">'
        + stops(("0", W, "0"), (".5", W, ".85"), ("1", W, "0")) + "</linearGradient>")
    cv._lights = L
    return L


class StdChip(Chip):
    """The standard badge, which can also draw its two panels apart, so a panel can slide open out of the other."""

    def draw_label(self, cv, x, y, what="badge") -> str:
        return Chip(self.label, "", icon=self.icon, size=self.size, lab=self.lab, heart=self.heart).draw(cv, x, y, what)

    def draw_message(self, cv, x, y, what="badge") -> str:
        base = y + self.h / 2 + SE.cap(self.size) / 2
        return (P.rect(x, y, self.mw, self.h, self.msg)
                + P.text(cv, self.message, x=x + self.pad, y=base, size=self.size, face="sans-bold", ls=self.ls,
                         fill=P.letters_on(self.msg), ground=self.msg, what=what))


class Standard:
    """The standard theme's skin: the board lit and the pieces enamelled, as the theme's banners and badges are."""

    family = "standard"
    label = "standard"

    def __init__(self, theme: str, dark_squares: str = "cobalt"):
        self.theme = theme
        self.std = {"day": P.DAY, "dark": P.DARK}[theme]
        self.dark = self.std["dark"]
        self.dark_squares = dark_squares   # the theme's accent
        self.flash = c("white")
        self.ripple = f'stroke="{c("amber")}" stroke-width="3"'

    # --- the sheet
    def new(self, W, H, title, desc, what, still=""):
        return P.new(W, H, title, desc, f"{what} {self.theme}{still}")

    def board_room(self, x0, y0, s):
        return (x0 - 2, y0 - 2, 8 * s + 4, 8 * s + 4)

    def pawn_glyph(self, x, y, size, fill) -> str:
        """The band's icon: a pawn's silhouette, filled, where the kit's other bands set a stroked icon."""
        return (f'<g transform="translate({f1(x)} {f1(y)}) scale({fx(size / 45, 4)})" fill="{c(fill)}">'
                + "".join(PARTS["pawn"]) + "</g>")

    def frame(self, cv, W, H, kind, glyph, subject, caption="", plain=()) -> None:
        """A standard sheet's card and band, as `standard.elements.frame` draws them, with the band's icon given."""
        std = self.std
        text, size, mw, inside = SE._band(W, kind, subject, caption)
        cid = P.card(cv, std, W, H)
        lab = std["label"]
        on = P.letters_on(lab)
        mark = (self.pawn_glyph(PAD - 2, BAND / 2 - 10, 20, on) if glyph == "pawn"
                else P.icon(glyph, PAD, BAND / 2 - 8, 16, on, 2.1))
        m = [P.rect(0, 0, W - mw, BAND, lab), mark,
             SE.say(cv, kind.upper(), x=PAD + 26, y=BAND / 2 + SE.cap(10.5) / 2, size=10.5, ls=1.1, fill=on,
                    ground=lab, what="element kind")]
        if mw:
            m += [P.rect(W - mw, 0, mw, BAND, P.ACCENT),
                  SE.say(cv, text, x=W - mw / 2, y=BAND / 2 + SE.cap(size) / 2, size=size, ls=size * .1,
                         fill=P.letters_on(P.ACCENT), ground=P.ACCENT, anchor="middle", what="element subject")]
        if caption and inside:
            m.append(SE.say(cv, caption.upper(), x=W - mw - 18, y=BAND / 2 + SE.cap(8.5) / 2, size=8.5, ls=.9,
                            fill="ash", ground=lab, anchor="end", what="caption"))
        cv.add(f'<g clip-path="url(#{cid})">' + "".join(m) + "</g>")
        if caption and not inside:
            cv.add(SE.caps(cv, caption, PAD, BAND + 19, std, 8.5, ls=.9, what="caption"))

    def rule(self, x0, x1, y) -> str:
        return P.rule(x0, x1, y, self.std)

    def vrule(self, x, y0, y1) -> str:
        return f'<path d="M{f1(x)} {f1(y0)}V{f1(y1)}" stroke="{c(self.std["rule"])}"/>'

    # --- lettering
    def _fill(self, role):
        if role == "alert":
            return "crimson" if not self.dark else "rose"
        return self.std[role]

    def say(self, cv, s, x, y, size, *, role="ink", face="bold", anchor="start", ls=0.0, what="label") -> str:
        return SE.say(cv, s, x=x, y=y, size=size, fill=self._fill(role), ground=self.std["paper"],
                      face="sans-bold" if face == "bold" else "sans", anchor=anchor, ls=ls, what=what)

    def caps(self, cv, s, x, y, size=8.5, *, role=None, anchor="start", ls=.8, what="label") -> str:
        return SE.caps(cv, s, x, y, self.std, size, self._fill(role) if role else None, anchor, ls, what=what)

    def heading(self, cv, s, x, y, anchor="start") -> str:
        return SE.caps(cv, s, x, y, self.std, 9, self.std["muted"], anchor, .9, what="heading")

    def width(self, s, face, size, ls=0.0) -> float:
        return width(s, "sans" if face == "regular" else "sans-bold", size, ls)

    def fitted(self, s, size, floor, room, ls_em=0.0) -> float:
        return P.fitted(s, "sans-bold", size, floor, room, ls_em)

    def cap(self, size) -> float:
        return SE.cap(size)

    # --- the board
    def lights(self, cv) -> dict:
        return lights(cv, self.std)

    def squares(self) -> dict:
        light = ("ash", .3) if self.std["name"] == "day" else ("ash", 1)
        return {"light": light, "dark": (self.dark_squares, 1),
                "edge": "black" if self.std["name"] == "day" else "charcoal"}

    def square(self, cv, x, y, size, light: bool, rx: float = 0) -> None:
        tone, op = self.squares()["light" if light else "dark"]
        if self.std["name"] == "day" and tone == "ash":
            cv.add(P.rect(x, y, size, size, "white", rx))
        o = f' fill-opacity="{fx(op)}"' if op < 1 else ""
        r = f' rx="{f1(rx)}"' if rx else ""
        cv.add(f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(size)}" height="{f1(size)}"{r} fill="{c(tone)}"{o}/>')

    def board_base(self, cv, x0, y0, s) -> None:
        """The board lit from the upper left: sunk in a shadow by day and a glow of the accent by night, framed, its
        squares laid."""
        std = self.std
        pal = self.squares()
        self.lights(cv)
        n = 8 * s
        if std["dark"]:
            cv.add(f'<rect x="{f1(x0 - 10)}" y="{f1(y0 - 10)}" width="{f1(n + 20)}" height="{f1(n + 20)}" rx="10" '
                   f'fill="{c(P.ACCENT)}" fill-opacity=".07"/>'
                   f'<rect x="{f1(x0 - 5)}" y="{f1(y0 - 5)}" width="{f1(n + 10)}" height="{f1(n + 10)}" rx="6" '
                   f'fill="{c(P.ACCENT)}" fill-opacity=".14"/>')
        else:
            cv.add(f'<rect x="{f1(x0 + 2)}" y="{f1(y0 + 7)}" width="{f1(n + 3)}" height="{f1(n + 2)}" rx="6" '
                   f'fill="{c("black")}" fill-opacity=".06"/>'
                   f'<rect x="{f1(x0 + .5)}" y="{f1(y0 + 3)}" width="{f1(n + 2.5)}" height="{f1(n + 1.5)}" rx="3" '
                   f'fill="{c("black")}" fill-opacity=".12"/>')
        cv.add(P.rect(x0 - 2, y0 - 2, n + 4, n + 4, pal["edge"], 1.5))
        if std["name"] == "day":
            cv.add(P.rect(x0, y0, n, n, "white"))
        cells = []
        for rank in range(8, 0, -1):
            for f in range(8):
                tone, op = pal["light" if (f + rank - 1) % 2 != 0 else "dark"]
                o = f' fill-opacity="{fx(op)}"' if op < 1 else ""
                cells.append(f'<rect x="{f1(x0 + f * s)}" y="{f1(y0 + (8 - rank) * s)}" width="{f1(s)}" '
                             f'height="{f1(s)}" fill="{c(tone)}"{o}/>')
        cv.add("".join(cells))

    def mark_from(self, cv, x, y, s, last) -> None:
        cv.add(P.rect(x, y, s, s, "white") + f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(s)}" height="{f1(s)}" '
               f'fill="{c("amber")}" fill-opacity=".42"/>')

    def mark_to(self, cv, x, y, s, appear: str) -> None:
        cv.add(f'<g>{appear}' + P.rect(x, y, s, s, "white") + P.rect(x, y, s, s, "amber") + "</g>")

    def board_over(self, cv, clip, x0, y0, s, check, pulse) -> None:
        """The board's surface catching the lamp, and the checked king's square glowing red."""
        L = self.lights(cv)
        n = 8 * s
        over = [f'<rect x="{f1(x0)}" y="{f1(y0)}" width="{f1(n)}" height="{f1(n)}" fill="url(#{L["bd"]})"/>']
        if check:
            kx, ky = check
            over.append(f'<g>{pulse}<circle cx="{f1(kx + s / 2)}" cy="{f1(ky + s / 2)}" r="{f1(s * .86)}" '
                        f'fill="url(#{L["ck"]})"/><rect x="{f1(kx + 1.5)}" y="{f1(ky + 1.5)}" width="{f1(s - 3)}" '
                        f'height="{f1(s - 3)}" fill="none" stroke="{c("crimson")}" stroke-width="2.5"/></g>')
        cv.add(f'<g clip-path="url(#{clip})">' + "".join(over) + "</g>")

    def bevel(self, cv, x0, y0, n) -> None:
        """The bevel of the board's edge: the lamp's side catches it, the far side falls away."""
        cv.add(f'<path d="M{f1(x0)} {f1(y0 + n)}V{f1(y0)}H{f1(x0 + n)}" fill="none" stroke="{c("white")}" '
               f'stroke-opacity=".38"/><path d="M{f1(x0 + n)} {f1(y0)}V{f1(y0 + n)}H{f1(x0)}" fill="none" '
               f'stroke="{c("black")}" stroke-opacity=".3"/>')

    def foot(self, cv, sx, sy, rx, ry, inner) -> str:
        L = self.lights(cv)
        return (f'<ellipse cx="{f1(sx)}" cy="{f1(sy)}" rx="{f1(rx)}" ry="{f1(ry)}" fill="url(#{L["sh"]})">'
                + inner + "</ellipse>")

    # --- the pieces: white with a black edge, black with white detail, each lit
    SIDE = {"white": ("white", "black", "black"), "black": ("black", "black", "white")}   # fill, edge, detail

    def clip_of(self, cv, kind: str) -> str:
        """A piece's silhouette as a clip, for the light that lies over it."""
        cv.__dict__.setdefault("_clips", {})
        if kind not in cv._clips:
            cid = cv.uid("s")
            cv.defs.append(f'<clipPath id="{cid}">' + "".join(PARTS[kind]) + "</clipPath>")
            cv._clips[kind] = cid
        return cv._clips[kind]

    def piece_def(self, cv, kind: str, side: str, sw: float = 1.5, shadow: bool = True) -> str:
        """The id of a piece drawn once in the file's defs, lit, in its 45-unit box, its shadow at its foot."""
        key = (kind, side, sw, shadow)
        cv.__dict__.setdefault("_pieces", {})
        if key not in cv._pieces:
            L = self.lights(cv)
            pid = cv.uid("p")
            fill, edge, detail = self.SIDE[side]
            parts = "".join(PARTS[kind])
            g = [f'<g id="{pid}">']
            if shadow:
                g.append(f'<ellipse cx="24.8" cy="38.8" rx="15.8" ry="3.4" fill="url(#{L["sh"]})"/>')
            g.append(f'<g fill="{c(fill)}" stroke="{c(edge)}" stroke-width="{fx(sw)}" stroke-linejoin="round">{parts}</g>')
            g.append(f'<rect width="45" height="45" clip-path="url(#{self.clip_of(cv, kind)})" '
                     f'fill="url(#{L["wp" if side == "white" else "bp"]})"/>')
            g.append(f'<g fill="none" stroke="{c(edge)}" stroke-width="{fx(sw)}" stroke-linejoin="round">{parts}</g>')
            if DETAIL[kind]:
                dsw = sw * (.95 if side == "white" else 1.05)
                g.append(f'<g fill="none" stroke="{c(detail)}" stroke-width="{fx(dsw)}" stroke-linecap="round">'
                         + DETAIL[kind] + "</g>")
            if kind in DOTS:
                g.append(f'<g fill="{c(detail)}">{DOTS[kind]}</g>')
            if side == "black" and sw < 2:
                g.append(f'<path d="{SPEC[kind]}{BASE_SPEC}" fill="none" stroke="{c("white")}" stroke-opacity=".5" '
                         f'stroke-width="{fx(sw * .9)}" stroke-linecap="round"/>')
            cv.defs.append("".join(g) + "</g>")
            cv._pieces[key] = pid
        return cv._pieces[key]

    def put(self, cv, kind, side, x, y, size, sw=1.5, shadow=True) -> str:
        """A piece filling a square `size` wide with its top-left at (x, y)."""
        pid = self.piece_def(cv, kind, side, sw, shadow)
        return f'<use href="#{pid}" transform="translate({f1(x)} {f1(y)}) scale({fx(size / 45, 4)})"/>'

    def sweep(self, cv, kind, x, y, size, begin, every=9.0) -> str:
        """A band of light that crosses a piece and is gone, `begin` seconds in and every `every` seconds after."""
        if not M.MOTION:
            return ""
        L = self.lights(cv)
        a, b = .0, round(1.1 / every, 3)
        return (f'<g transform="translate({f1(x)} {f1(y)}) scale({fx(size / 45, 4)})"><g clip-path="url(#{self.clip_of(cv, kind)})">'
                f'<rect x="-16" y="-6" width="12" height="58" fill="url(#{L["sw"]})" opacity="0" transform="skewX(-18)">'
                + M.ani("x", "-16;64;64", f"0;{b};1", every, begin=begin, repeat=True)
                + M.ani("opacity", "1;1;0;0", f"0;{round(b - .001, 3)};{b};1", every, begin=begin, repeat=True)
                + "</rect></g></g>")

    def tile_light(self, cv, x, y, w, h, rx=0) -> str:
        r = f' rx="{f1(rx)}"' if rx else ""
        return (f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(w)}" height="{f1(h)}"{r} '
                f'fill="url(#{self.lights(cv)["bd"]})"/>')

    def tray(self, cv, x, y, w, h) -> None:
        """The rank the taken pieces stand on: the board's light square, so both sides' pieces hold on it."""
        tone, op = self.squares()["light"]
        if self.std["name"] == "day":
            cv.add(P.rect(x, y, w, h, "white", 3))
        o = f' fill-opacity="{fx(op)}"' if op < 1 else ""
        cv.add(f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(w)}" height="{f1(h)}" rx="3" fill="{c(tone)}"{o}/>')

    # --- the panel
    def medallion(self, cv, cx, cy, r, side) -> str:
        """A player's medallion: their king on an enamelled disc of the other colour."""
        L = self.lights(cv)
        disc = self.std["label"] if side == "white" else "ash"
        k = 2 * r * .98
        return (f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="{c(disc)}"/>'
                f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="url(#{L["en"]})"/>'
                + self.put(cv, "king", side, cx - k / 2, cy - k / 2 + r * .02, k, shadow=False))

    def turn_ring(self, cv, cx, cy, r, begin) -> str:
        """The cobalt ring round the medallion of the side whose turn it is, closing as the turn arrives."""
        C = 2 * math.pi * r
        L = self.lights(cv)
        dash = (f' stroke-dasharray="{f1(C)}" stroke-dashoffset="0">'
                + M.ani("stroke-dashoffset", f"{f1(C)};{f1(C)};0", f"0;{fx(begin / (begin + .6), 3)};1", begin + .6,
                        spline="0 0 1 1;.3 0 .2 1") + "</circle>") if M.MOTION else "/>"
        return (f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="none" stroke="{c(P.ACCENT)}" stroke-width="2.6" '
                f'transform="rotate(-90 {f1(cx)} {f1(cy)})"' + dash
                + f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="none" stroke="url(#{L["mt"]})" '
                  f'stroke-width="2.6" stroke-opacity=".7"/>')

    def chip(self, label, message="", *, icon=None, size=11.0, lab="label", msg="count") -> StdChip:
        labs = {"label": self.std["label"], "turn": self.std["label"], "accent": P.ACCENT, "safe": "amber",
                "medal1": MEDALS[0], "medal2": MEDALS[1], "medal3": MEDALS[2]}
        msgs = {"alert": "crimson", "count": "slate", "medal1": MEDALS[0], "medal2": MEDALS[1], "medal3": MEDALS[2]}
        return StdChip(label, message, icon=icon, size=size, lab=labs[lab], msg=msgs[msg])

    def glint(self, cv, solid=True) -> tuple[str, str]:
        return f'url(#{self.lights(cv)["sw"]})', ".5"

    KEYS = {"last": "amber", "house": "cobalt", "world": "tangerine", "draws": "gray"}

    def key(self, cv, x, y, size, tone) -> str:
        return P.rect(x, y, size, size, self.KEYS[tone])

    def segment(self, cv, x, y, w, h, tone) -> str:
        return P.rect(x, y, w, h, self.KEYS[tone])

    def row_mark(self, x, y, w, h) -> str:
        return (f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(w)}" height="{f1(h)}" rx="2" fill="{c("amber")}" '
                f'fill-opacity="{".2" if not self.dark else ".16"}"/>')

    # --- the hall of fame
    def face(self, cv, cx, cy, r, p, i, medal=None, glint=False) -> str:
        """A winner's medallion, enamelled: the house's king, or their initials on a colour of their own; a medal of
        metal round the podium's, the gold one glinting."""
        L = self.lights(cv)
        out = []
        if medal is not None:
            ring = MEDALS[medal]
            rr = r + 4.5
            out.append(f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(rr)}" fill="none" stroke="{c(ring)}" '
                       f'stroke-width="3.6"/><circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(rr)}" fill="none" '
                       f'stroke="url(#{L["mt"]})" stroke-width="3.6"/>')
            if glint and M.MOTION:
                out.append(medal_glint(cx, cy, rr))
        if p.get("house"):
            out.append(self.medallion(cv, cx, cy, r, "white"))
        else:
            colour = FACES[i % len(FACES)]
            out.append(f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="{c(colour)}"/>'
                       f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="url(#{L["en"]})"/>')
            size = r * .72
            out.append(SE.say(cv, p["initials"], x=cx, y=cy + SE.cap(size) / 2, size=size, ls=.8,
                              fill=P.letters_on(colour), ground=colour, anchor="middle", what="initials"))
        return "".join(out)

    def draws_disc(self, cv, cx, cy, r) -> str:
        L = self.lights(cv)
        colour = "gray"
        return (f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="{c(colour)}"/>'
                f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="url(#{L["en"]})"/>'
                + SE.say(cv, "=", x=cx, y=cy + SE.cap(r) / 2, size=r, fill=P.letters_on(colour), ground=colour,
                         anchor="middle"))

    def vacant(self, cv, cx, cy, r, i) -> str:
        """A place on the podium nobody has won yet: its medal's ring dashed round an empty disc, and a question."""
        rr = r + 4.5
        return (f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(rr)}" fill="none" stroke="{c(MEDALS[i])}" '
                f'stroke-width="2" stroke-dasharray="4 3" stroke-opacity=".8"/>'
                f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="{c(self.std["rule"])}" fill-opacity=".45"/>'
                + self.say(cv, "?", cx, cy + self.cap(r * .8) / 2, r * .8, role="muted", anchor="middle",
                           what="vacant"))

    def track(self, cv, x, y, w, h) -> str:
        return P.rect(x, y, w, h, self.std["rule"])

    def fill_bar(self, cv, x, y, w, h) -> str:
        return P.rect(x, y, w, h, P.ACCENT)

    def number(self, cv, n, x, y, size) -> str:
        return SE.number(cv, n, x, y, size)

    def badge_file(self, i, p) -> str:
        """Option B: every winner a badge of their own, so each name can link to its profile; the leader's badge
        catches the light every seven seconds."""
        std = self.std
        msg = MEDALS[i] if i < 3 else "slate"
        chip = Chip(f"#{i + 1}  {p['badge']}", f"{p['wins']} win" + ("s" if p["wins"] != 1 else ""),
                    icon="trophy" if i == 0 else "medal", size=11, lab=std["label"], msg=msg)
        cv = P.new(chip.w, chip.h, f"Hall of Fame: {p['badge']}", f"Number {i + 1}, {p['badge']}, {p['wins']} wins",
                   f"elements chess hall badge {self.theme}")
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


def halo_glint(cx, cy, rr) -> str:
    """The gold medal's glint where the medal is white, after dark: light spilling past both its edges as it runs
    round, on the same beat as `medal_glint`."""
    C = 2 * math.pi * rr
    return (f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(rr)}" fill="none" stroke="{c("white")}" stroke-width="10" '
            f'stroke-linecap="round" stroke-dasharray="7 {f1(C)}" transform="rotate(-150 {f1(cx)} {f1(cy)})" '
            f'stroke-opacity="0">'
            + M.ani("stroke-dashoffset", f"0;0;{f1(-C * .32)};{f1(-C * .32)}", "0;.7;.84;1", M.GLINT, begin=1.6,
                    repeat=True)
            + M.ani("stroke-opacity", "0;0;.34;.34;0;0", "0;.7;.73;.8;.84;1", M.GLINT, begin=1.6, repeat=True)
            + "</circle>")


def medal_glint(cx, cy, rr, paint=None) -> str:
    """A glint running round the gold medal, every `GLINT` seconds: the same beat in every theme."""
    C = 2 * math.pi * rr
    return (f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(rr)}" fill="none" stroke="{paint or c("white")}" '
            f'stroke-width="3.4" stroke-linecap="round" stroke-dasharray="6 {f1(C)}" '
            f'transform="rotate(-150 {f1(cx)} {f1(cy)})" stroke-opacity="0">'
            + M.ani("stroke-dashoffset", f"0;0;{f1(-C * .32)};{f1(-C * .32)}", "0;.7;.84;1", M.GLINT, begin=1.6,
                    repeat=True)
            + M.ani("stroke-opacity", "0;0;.95;.95;0;0", "0;.7;.73;.8;.84;1", M.GLINT, begin=1.6, repeat=True)
            + "</circle>")


# =========================================================================== a print
# Line shading, as a turned part is drawn in a technical illustration: lines along its axis, closer together as
# its surface turns from the lamp, which stands up and to the left.
SHADE = "".join(f"M{x} 1V44" for x in (26.4, 28.6, 30.5, 32.1, 33.5, 34.7, 35.7))
TICKS = 36


def ring_ticks(cx, cy, a, b, n=TICKS) -> str:
    """A dial's ticks, `n` of them, from radius `a` out to `b`."""
    out = []
    for i in range(n):
        t = i * 2 * math.pi / n
        out.append(f"M{f1(cx + a * math.cos(t))} {f1(cy + a * math.sin(t))}L{f1(cx + b * math.cos(t))} "
                   f"{f1(cy + b * math.sin(t))}")
    return "".join(out)


def _rgb(token: str) -> list[float]:
    h = PALETTE[token].lstrip("#")
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def _lum_rgb(ch: list[float]) -> float:
    ch = [v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4 for v in ch]
    return .2126 * ch[0] + .7152 * ch[1] + .0722 * ch[2]


def _lum(token: str) -> float:
    """A palette colour's relative luminance, as WCAG measures it."""
    return _lum_rgb(_rgb(token))


def _legible(ink: str, paper: str, base: float, aim: float = 4.6) -> float:
    """The faintest opacity, from `base` up, at which `ink` laid over `paper` still keeps every word to the kit's
    4.5:1 (aiming a little over, for the paper's grain): a print's quieter lettering is as quiet as it can be and
    no quieter."""
    i, p = _rgb(ink), _rgb(paper)
    op = base
    while op < 1:
        mixed = [op * a + (1 - op) * b for a, b in zip(i, p)]
        hi, lo = sorted((_lum_rgb(mixed), _lum_rgb(p)), reverse=True)
        if (hi + .05) / (lo + .05) >= aim:
            break
        op = round(op + .01, 2)
    return min(op, 1.0)


class Plate:
    """A print's badge, as the kit's blueprint plates draw one, measured before it is drawn: the label lettered on
    the paper inside the plate's frame, the value on a solid block of the print. A plate with no value is a note,
    in outline, or a statement, solid; either way its proportions are a badge's, 28 tall at 11 px."""

    def __init__(self, sk, label: str, message: str = "", *, icon=None, size: float = 11.0, solo: str = "solid"):
        self.sk, self.icon = sk, icon
        self.label, self.message = label.upper(), message.upper()
        k = size / 11
        self.h, self.pad, self.isz, self.gap = 28 * k, 12 * k, 15 * k, 6 * k
        self.size, self.ls = size * sk.K, 1.3 * k
        self.solid = not self.message and solo == "solid"
        self.lface = "num"
        self.label = E.plain(self.label, self.lface)
        self.message = E.plain(self.message, "num")
        words = width(self.label, self.lface, self.size, self.ls) if self.label else 0
        self.lw = 2 * self.pad + words + ((self.isz + (self.gap if self.label else 0)) if icon else 0)
        self.mw = (2 * self.pad + width(self.message, "num", self.size, self.ls)) if self.message else 0
        self.w = self.lw + self.mw

    def _base(self, y) -> float:
        return y + self.h / 2 + cap_height(self.lface, self.size) / 2

    def draw_label(self, cv, x, y, what="badge") -> str:
        col = self.sk.col
        if self.solid:
            out = [f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(self.lw)}" height="{f1(self.h)}" fill="{c(col["line"])}"/>']
            ink = self.sk.on_block
        else:
            out = [f'<rect x="{f1(x + .5)}" y="{f1(y + .5)}" width="{f1(self.lw - 1)}" height="{f1(self.h - 1)}" '
                   f'fill="{c(col["paper"])}" stroke="{c(col["line"])}" stroke-opacity=".9"/>']
            ink = col["ink"]
        tx = x + self.pad
        if self.icon:
            out.append(icon(self.icon, tx, y + (self.h - self.isz) / 2, self.isz, ink, 2))
            tx += self.isz + self.gap
        out.append(cv.L.text(self.label, face=self.lface, size=self.size, x=tx, y=self._base(y), ls=self.ls,
                             fill=c(ink)))
        return "".join(out)

    def draw_message(self, cv, x, y, what="badge") -> str:
        col = self.sk.col
        return (f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(self.mw)}" height="{f1(self.h)}" fill="{c(col["line"])}"/>'
                + cv.L.text(self.message, face="num", size=self.size, x=x + self.mw / 2,
                            y=y + self.h / 2 + cap_height("num", self.size) / 2, anchor="middle", ls=self.ls,
                            fill=c(self.sk.on_block)))

    def draw(self, cv, x, y, what="badge") -> str:
        return self.draw_label(cv, x, y, what) + (self.draw_message(cv, x + self.lw, y, what) if self.message else "")


class Print:
    """A print's skin: the same sheet drawn as a drawing, on the kit's drafting paper in the print's line and ink.

    White is white and black is black in either light, as a chess set is: the house's pieces paper-white edged in
    ink, GitHub's solid ink, edged in the night's line after dark so they hold on the dark sheet."""

    family = "print"
    K = 1.04   # Barlow's capitals stand as tall as DejaVu's at this much larger: the same cap height at every size

    def __init__(self, theme: str, tone: str = "blackprint"):
        self.theme = theme
        self.th = DARK if theme == "dark" else DAY
        self.dark = self.th["dark"]
        self.tone = self.label = tone
        self.col = colours(tone, self.th)
        p = PRINTS[tone]
        ink, night = p["ink"], p.get("night", "white")
        self.sides = {"white": ("white", ink if not self.dark else "black"),
                      "black": (ink if not self.dark else "black", ink if not self.dark else night)}
        self.shade = ink if not self.dark else "black"          # what a shadow is laid in
        # A lighter line lays a lighter tone: by day, darkness is lined more firmly in a light print (mustard,
        # tangerine, teal) than in blackprint's charcoal, so a dark square reads equally dark in every print.
        self.firm = (1 - _lum("charcoal")) / (1 - _lum(p["line"]))
        col = self.col
        # Every word keeps the kit's 4.5:1: quieter lettering only as faint as each print's ink and paper allow,
        # letters on a solid block in the paper's colour where that holds and in the palette's own choice where it
        # does not (black on mustard, tangerine and teal by day), and the marks that carry the game (the last
        # move, the check, the turn) in the ink where a light line would fall under 3:1.
        self.muted = _legible(col["ink"], col["paper"], .66)
        self.quiet = _legible(col["ink"], col["paper"], .72)
        self.on_block = col["paper"] if _contrast(col["paper"], col["line"]) >= 4.5 else letters_on(col["line"])
        self.mark = col["line"] if _contrast(col["line"], col["paper"]) >= 3 else col["ink"]
        self.light_line = _lum(col["line"]) > .4      # a white line after dark: a glint shows as a glow round it
        self.shadow_op = ".2" if not self.dark else ".5"
        self.flash = c("white")
        self.ripple = f'stroke="{c(self.col["line"])}" stroke-width="1.6"'

    # --- the sheet
    def new(self, W, H, title, desc, what, still=""):
        return Canvas(W, H, title=title, desc=desc, stamp=f"{self.tone} {what} {self.theme}{still}")

    def board_room(self, x0, y0, s):
        """The paper the board is drawn on, left plain of the grid, with room for the shadow it casts."""
        return (x0 - 2, y0 - 2, 8 * s + 10, 8 * s + 10)

    def frame(self, cv, W, H, kind, glyph, subject, caption="", plain=()) -> None:
        """The drafting sheet, and across its head, in the standard band's place, a title strip: the kind on a
        solid cell at the left, the subject on one at the right, the caption before it, a rule where the band ends."""
        col = self.col
        narrow = W < 400
        B = 10 if narrow else 12
        scatter = cv.L.scatter                            # the zone marks, in the panel's cut: one set of figures
        cv.L.scatter = lambda items, **k: scatter(items, **{**k, "face": "num"})
        sheet(cv, col, W=W, H=H, border=B, zones=4 if narrow else 8, plain=tuple(plain))
        del cv.L.scatter
        edge = B + 1.6                                    # the border line's inner edge
        mid = (edge + BAND) / 2
        line, paper = c(col["line"]), self.on_block
        K = self.K
        name = E.plain(kind.upper(), "num")
        kx1 = PAD + 26 + width(name, "num", 10.5 * K, 1.6) + 14
        m = [f'<rect x="{f1(edge)}" y="{f1(edge)}" width="{f1(kx1 - edge)}" height="{f1(BAND - edge)}" fill="{line}"/>']
        if glyph == "pawn":
            m.append(f'<g transform="translate({f1(PAD - 2)} {f1(mid - 10.6)}) scale({fx(20 / 45, 4)})" '
                     f'fill="{c(paper)}">' + "".join(PARTS["pawn"]) + "</g>")
        else:
            m.append(icon(glyph, PAD, mid - 8, 16, paper, 2.1))
        m.append(cv.L.text(name, face="num", size=10.5 * K, x=PAD + 26, y=mid + cap_height("num", 10.5 * K) / 2,
                           ls=1.6, fill=c(paper)))
        right = W - edge
        text, mw = "", 0
        if subject:
            for text in (subject.upper(), subject.upper().rsplit("/", 1)[-1]):
                text = E.plain(text, "num")
                size = 10.0
                while size > 7.5 and width(text, "num", size * K, size * .16) > right - kx1 - 36:
                    size -= .25
                if kx1 + 36 + width(text, "num", size * K, size * .16) <= right:
                    break
            mw = 36 + width(text, "num", size * K, size * .16)
            m.append(f'<rect x="{f1(right - mw)}" y="{f1(edge)}" width="{f1(mw)}" height="{f1(BAND - edge)}" '
                     f'fill="{line}"/>')
            m.append(cv.L.text(text, face="num", size=size * K, x=right - mw / 2, y=mid + cap_height("num", size * K) / 2,
                               anchor="middle", ls=size * .16, fill=c(paper)))
        if caption:
            cap_text = E.plain(caption.upper(), "num")
            cw = width(cap_text, "num", 8.5 * K, 1.4)
            if kx1 + 18 + cw <= right - mw - 18:
                m.append(cv.L.text(cap_text, face="num", size=8.5 * K, x=right - mw - 18,
                                   y=mid + cap_height("num", 8.5 * K) / 2, anchor="end", ls=1.4, fill=c(col["ink"]),
                                   opacity=self.quiet))
            else:
                m.append(self.caps(cv, caption, PAD, BAND + 19, 8.5, ls=.9))
        m.append(f'<path d="M{f1(edge)} {BAND}H{f1(right)}" fill="none" {hair(col, .9)} stroke-width="1.2"/>')
        cv.add("".join(m))

    def _plotted(self, markup: str, length: float) -> str:
        """Linework the plotter draws in as the file opens, as every print's sheet is drawn (`drafting.plot`)."""
        if not M.MOTION:
            return markup
        n = f1(length + 2)
        tag = markup[1:markup.index(" ")]
        return markup.replace("/>", f' stroke-dasharray="{n} {n}" stroke-dashoffset="0"><animate '
                              f'attributeName="stroke-dashoffset" values="{n};{n};0" keyTimes="0;.25;1" dur="1.4s" '
                              f'calcMode="spline" keySplines="0 0 1 1;.3 0 .2 1" fill="freeze"/></{tag}>', 1)

    def rule(self, x0, x1, y) -> str:
        return self._plotted(f'<path d="M{f1(x0)} {f1(y)}H{f1(x1)}" fill="none" {hair(self.col, .55)} '
                             f'stroke-width=".8"/>', x1 - x0)

    def vrule(self, x, y0, y1) -> str:
        return self._plotted(f'<path d="M{f1(x)} {f1(y0)}V{f1(y1)}" fill="none" {hair(self.col, .55)} '
                             f'stroke-width=".8"/>', y1 - y0)

    # --- lettering: Barlow Condensed, the prints' own, the bold cut for names and figures
    def _paint(self, role):
        if role == "paper":
            return self.col["paper"], None
        if role == "muted":
            return self.col["ink"], self.muted
        return self.col["ink"], None

    def say(self, cv, s, x, y, size, *, role="ink", face="bold", anchor="start", ls=0.0, what="") -> str:
        """A name, a figure or a move as it is written; a sentence ("regular") in capitals, as a drawing is
        lettered."""
        s = str(s).upper() if face == "regular" else str(s)
        tok, op = self._paint(role)
        return cv.L.text(E.plain(s, "num"), face="num", size=size * self.K, x=x, y=y, anchor=anchor,
                         ls=ls if face != "regular" else .5, fill=c(tok), opacity=op)

    def caps(self, cv, s, x, y, size=8.5, *, role=None, anchor="start", ls=.8, what="") -> str:
        tok, op = self._paint(role or "muted")
        return cv.L.text(E.plain(str(s).upper(), "num"), face="num", size=size * self.K, x=x, y=y, anchor=anchor,
                         ls=ls * 1.6, fill=c(tok), opacity=op)

    def heading(self, cv, s, x, y, anchor="start") -> str:
        return self.caps(cv, s, x, y, 9, ls=.9, anchor=anchor)

    def width(self, s, face, size, ls=0.0) -> float:
        if face == "caps":
            return width(E.plain(str(s).upper(), "num"), "num", size * self.K, ls * 1.6)
        if face == "regular":
            return width(E.plain(str(s).upper(), "num"), "num", size * self.K, .5)
        return width(E.plain(str(s), "num"), "num", size * self.K, ls)

    def fitted(self, s, size, floor, room, ls_em=0.0) -> float:
        while size > floor and width(E.plain(str(s), "num"), "num", size * self.K, size * ls_em) > room:
            size -= .25
        return size

    def cap(self, size) -> float:
        return cap_height("num", size * self.K)

    # --- materials
    # angle, gap, weight, opacity by day and by night. Darkness, a dark square or a shadow, is laid in the shade's
    # ink, so it stays darker than the paper after dark too; material, a bar or a medal, in the print's line.
    HATCH = {"square": (45, 3.4, .9, .62, .8), "shadow": (45, 2.2, .8, .6, .8), "bar": (45, 3, 1, 1, 1),
             "ring": (45, 2, .8, 1, 1)}
    DARKNESS = ("square", "shadow")

    def _hatch(self, cv, key: str) -> str:
        """Section lining, the draughtsman's tone: lines at an angle, each pattern defined once per file."""
        cv.__dict__.setdefault("_hatches", {})
        if key not in cv._hatches:
            angle, gap, sw, day, night = self.HATCH[key]
            pid = cv.uid("h")
            cv.defs.append(f'<pattern id="{pid}" width="{fx(gap)}" height="{fx(gap)}" patternUnits="userSpaceOnUse" '
                           f'patternTransform="rotate({fx(angle)})"><path d="M{fx(gap / 2)} 0V{fx(gap)}" '
                           f'stroke="{c(self.shade if key in self.DARKNESS and self.dark else self.col["line"])}" '
                           f'stroke-width="{fx(sw)}" '
                           f'stroke-opacity="{fx(night if self.dark else min(1, day * self.firm) if key in self.DARKNESS else day)}"/></pattern>')
            cv._hatches[key] = pid
        return cv._hatches[key]

    def _grad(self, cv, key: str) -> str:
        """A band of light for a glint: the paper's white by day and the night's line after dark ("sw"), or the
        print's line for a glint across paper ("sl")."""
        cv.__dict__.setdefault("_grads", {})
        if key not in cv._grads:
            gid = cv.uid("g")
            tone = {"sw": c("white"), "sl": c(self.col["line"]), "sp": c(self.col["paper"])}[key]
            cv.defs.append(f'<linearGradient id="{gid}"><stop offset="0" stop-color="{tone}" stop-opacity="0"/>'
                           f'<stop offset=".5" stop-color="{tone}" stop-opacity=".85"/>'
                           f'<stop offset="1" stop-color="{tone}" stop-opacity="0"/></linearGradient>')
            cv._grads[key] = gid
        return cv._grads[key]

    # --- the board
    def square(self, cv, x, y, size, light: bool, rx: float = 0) -> None:
        if not light:
            r = f' rx="{f1(rx)}"' if rx else ""
            cv.add(f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(size)}" height="{f1(size)}"{r} '
                   f'fill="url(#{self._hatch(cv, "square")})"/>')

    def board_base(self, cv, x0, y0, s) -> None:
        """The board as a plan view: its shadow cast down and to the right in section lining, its dark squares
        lined, the fine lines between all sixty-four."""
        n = 8 * s
        cv.add(f'<path d="M{f1(x0 + n + 2)} {f1(y0 + 4)}H{f1(x0 + n + 7)}V{f1(y0 + n + 7)}H{f1(x0 + 4)}'
               f'V{f1(y0 + n + 2)}H{f1(x0 + n + 2)}Z" fill="url(#{self._hatch(cv, "shadow")})"/>')
        d = "".join(f"M{f1(x0 + f * s)} {f1(y0 + (8 - rank) * s)}h{f1(s)}v{f1(s)}h{f1(-s)}Z"
                    for rank in range(8, 0, -1) for f in range(8) if (f + rank - 1) % 2 == 0)
        cv.add(f'<path d="{d}" fill="url(#{self._hatch(cv, "square")})"/>')
        grid = "".join(f"M{f1(x0 + i * s)} {f1(y0)}V{f1(y0 + n)}M{f1(x0)} {f1(y0 + i * s)}H{f1(x0 + n)}"
                       for i in range(1, 8))
        cv.add(f'<path d="{grid}" fill="none" {hair(self.col, .3)} stroke-width=".6"/>')

    def _phantom(self, cv, kind, x, y, s) -> str:
        """A piece in phantom lines, long and short dashes: the drawing's way to show where a moving part was."""
        return (f'<use href="#{self.shape(cv, kind)}" transform="translate({f1(x)} {f1(y)}) scale({fx(s / 45, 4)})" '
                f'fill="none" stroke="{c(self.mark)}" stroke-width="1.1" stroke-opacity=".85" '
                f'stroke-dasharray="4 1.4 1 1.4" stroke-linejoin="round"/>')

    def mark_from(self, cv, x, y, s, last) -> None:
        col = self.col
        cv.add(f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(s)}" height="{f1(s)}" fill="{c(col["paper"])}"/>'
               f'<rect x="{f1(x + 3)}" y="{f1(y + 3)}" width="{f1(s - 6)}" height="{f1(s - 6)}" fill="none" '
               f'stroke="{c(self.mark)}" stroke-opacity=".8" stroke-dasharray="6 2 1.5 2"/>'
               + self._phantom(cv, last["piece"], x, y, s))

    def mark_to(self, cv, x, y, s, appear: str) -> None:
        col = self.col
        cv.add(f'<g>{appear}<rect x="{f1(x)}" y="{f1(y)}" width="{f1(s)}" height="{f1(s)}" fill="{c(col["paper"])}"/>'
               f'<rect x="{f1(x + 2.2)}" y="{f1(y + 2.2)}" width="{f1(s - 4.4)}" height="{f1(s - 4.4)}" fill="none" '
               f'stroke="{c(self.mark)}" stroke-width="2.2"/></g>')

    def _cloud(self, x, y, s) -> str:
        """A revision cloud round a square: scallops bulging out, four to a side, the mark a drawing puts round
        whatever needs looking at."""
        i = 1.4
        x0, y0, w = x + i, y + i, s - 2 * i
        ch = w / 4
        r = f1(ch * .62)
        arc = lambda dx, dy: f"a{r} {r} 0 0 1 {f1(dx)} {f1(dy)}"
        return (f"M{f1(x0)} {f1(y0)}" + "".join(arc(ch, 0) for _ in range(4)) + "".join(arc(0, ch) for _ in range(4))
                + "".join(arc(-ch, 0) for _ in range(4)) + "".join(arc(0, -ch) for _ in range(4)) + "Z")

    def board_over(self, cv, clip, x0, y0, s, check, pulse) -> None:
        """The checked king's revision cloud, kept within the board as the standard theme keeps its glow, so a king
        on the edge is clouded inside the frame rather than across it."""
        if check:
            kx, ky = check
            cv.add(f'<g clip-path="url(#{clip})"><g>{pulse}<path d="{self._cloud(kx, ky, s)}" fill="none" '
                   f'stroke="{c(self.mark)}" stroke-width="1.5" stroke-linejoin="round"/></g></g>')

    def bevel(self, cv, x0, y0, n) -> None:
        """The board's edge, drawn in, and heavier along the two sides the lamp does not reach: the shade lines a
        drawing gives a solid lit from the upper left."""
        line = c(self.col["line"])
        cv.add(self._plotted(f'<rect x="{f1(x0 - .8)}" y="{f1(y0 - .8)}" width="{f1(n + 1.6)}" height="{f1(n + 1.6)}" '
                             f'fill="none" stroke="{line}" stroke-width="1.6"/>', 4 * (n + 1.6)),
               self._plotted(f'<path d="M{f1(x0 + n + 1.4)} {f1(y0 - 1.6)}V{f1(y0 + n + 1.4)}H{f1(x0 - 1.6)}" '
                             f'fill="none" stroke="{line}" stroke-width="2.8"/>', 2 * n + 6))

    def foot(self, cv, sx, sy, rx, ry, inner) -> str:
        return (f'<ellipse cx="{f1(sx)}" cy="{f1(sy)}" rx="{f1(rx)}" ry="{f1(ry)}" fill="{c(self.shade)}" '
                f'fill-opacity="{self.shadow_op}">' + inner + "</ellipse>")

    # --- the pieces: the same silhouettes, drawn in ink, each kind's parts defined once in the file
    def shape(self, cv, kind: str) -> str:
        """The id of a kind's silhouette, its parts defined once in the file's defs and gathered in one group, so
        every piece of the kind, its clip and its phantom use the same outlines rather than repeat them."""
        cv.__dict__.setdefault("_shapes", {})
        if kind not in cv._shapes:
            ids = []
            for part in PARTS[kind]:
                for one in part.replace("/><", "/>\n<").split("\n"):
                    pid = cv.uid("t")
                    ids.append(pid)
                    cv.defs.append(one.replace("<", f'<', 1).replace(" ", f' id="{pid}" ', 1))
            gid = cv.uid("t")
            cv.defs.append(f'<g id="{gid}">' + "".join(f'<use href="#{i}"/>' for i in ids) + "</g>")
            cv._shapes[kind] = (gid, ids)
        return cv._shapes[kind][0]

    def clip_of(self, cv, kind: str) -> str:
        """A piece's silhouette as a clip, for the shading laid inside it: its parts used, not repeated."""
        cv.__dict__.setdefault("_clips", {})
        if kind not in cv._clips:
            self.shape(cv, kind)
            cid = cv.uid("s")
            cv.defs.append(f'<clipPath id="{cid}">' + "".join(f'<use href="#{i}"/>' for i in cv._shapes[kind][1])
                           + "</clipPath>")
            cv._clips[kind] = cid
        return cv._clips[kind]

    def piece_def(self, cv, kind: str, side: str, sw: float = 1.5, shadow: bool = True) -> str:
        key = (kind, side, sw, shadow)
        cv.__dict__.setdefault("_pieces", {})
        if key not in cv._pieces:
            pid = cv.uid("p")
            fill, edge = self.sides[side]
            detail = edge if side == "white" else "white"
            parts = "".join(PARTS[kind])
            g = [f'<g id="{pid}">']
            if shadow:
                g.append(f'<ellipse cx="{FOOT[0]}" cy="{FOOT[1]}" rx="{FOOT[2]}" ry="{FOOT[3]}" fill="{c(self.shade)}" '
                         f'fill-opacity="{self.shadow_op}"/>')
            # after dark a black piece is edged in the night's line, finer than by day, so it reads as black, not as
            # a white outline, even where a README scales the sheet down
            esw = sw * .7 if side == "black" and self.dark else sw
            g.append(f'<use href="#{self.shape(cv, kind)}" fill="{c(fill)}" stroke="{c(edge)}" stroke-width="{fx(esw)}" '
                     f'stroke-linejoin="round"/>')
            if side == "white":
                g.append(f'<path d="{SHADE}" clip-path="url(#{self.clip_of(cv, kind)})" fill="none" stroke="{c(edge)}" '
                         f'stroke-width="{".7" if sw < 2 else ".9"}" stroke-opacity=".55"/>')
                g.append(f'<use href="#{self.shape(cv, kind)}" fill="none" stroke="{c(edge)}" stroke-width="{fx(sw)}" '
                         f'stroke-linejoin="round"/>')
            if DETAIL[kind]:
                dsw = sw * (.95 if side == "white" else 1.05)
                g.append(f'<g fill="none" stroke="{c(detail)}" stroke-width="{fx(dsw)}" stroke-linecap="round">'
                         + DETAIL[kind] + "</g>")
            if kind in DOTS:
                g.append(f'<g fill="{c(detail)}">{DOTS[kind]}</g>')
            if side == "black" and sw < 2:
                g.append(f'<path d="{SPEC[kind]}{BASE_SPEC}" fill="none" stroke="{c("white")}" '
                         f'stroke-opacity="{".35" if self.dark else ".55"}" '
                         f'stroke-width="{fx(sw * .9)}" stroke-linecap="round"/>')
            cv.defs.append("".join(g) + "</g>")
            cv._pieces[key] = pid
        return cv._pieces[key]

    put = Standard.put

    def sweep(self, cv, kind, x, y, size, begin, every=9.0) -> str:
        if not M.MOTION:
            return ""
        b = round(1.1 / every, 3)
        return (f'<g transform="translate({f1(x)} {f1(y)}) scale({fx(size / 45, 4)})"><g clip-path="url(#{self.clip_of(cv, kind)})">'
                f'<rect x="-16" y="-6" width="12" height="58" fill="url(#{self._grad(cv, "sw")})" opacity="0" '
                f'transform="skewX(-18)">'
                + M.ani("x", "-16;64;64", f"0;{b};1", every, begin=begin, repeat=True)
                + M.ani("opacity", "1;1;0;0", f"0;{round(b - .001, 3)};{b};1", every, begin=begin, repeat=True)
                + "</rect></g></g>")

    def tile_light(self, cv, x, y, w, h, rx=0) -> str:
        """A print shows no surface: what bounds a tile is its drawn edge."""
        r = f' rx="{f1(rx)}"' if rx else ""
        return (f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(w)}" height="{f1(h)}"{r} fill="none" {hair(self.col, .7)} '
                f'stroke-width=".8"/>')

    def tray(self, cv, x, y, w, h) -> None:
        cv.add(f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(w)}" height="{f1(h)}" rx="3" fill="{c(self.col["paper"])}" '
               f'{hair(self.col, .55)} stroke-width=".8"/>')

    # --- the panel
    def _dial(self, cx, cy, r) -> str:
        """The prints' medallion: a ring and its dial of ticks on the paper, the ticks one dashed circle."""
        col = self.col
        rm, C = r - 2.05, 2 * math.pi * (r - 2.05)
        return (f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="{c(col["paper"])}" stroke="{c(col["line"])}" '
                f'stroke-width="1.4"/><circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(rm)}" fill="none" {hair(col, .55)} '
                f'stroke-width="1.9" stroke-dasharray=".7 {fx(C / TICKS - .7, 2)}"/>')

    def medallion(self, cv, cx, cy, r, side) -> str:
        k = 2 * r * .84
        return self._dial(cx, cy, r) + self.put(cv, "king", side, cx - k / 2, cy - k / 2 + r * .02, k, shadow=False)

    def turn_ring(self, cv, cx, cy, r, begin) -> str:
        """A heavier ring round the side whose turn it is, drawn in as the turn arrives."""
        C = 2 * math.pi * r
        dash = (f' stroke-dasharray="{f1(C)}" stroke-dashoffset="0">'
                + M.ani("stroke-dashoffset", f"{f1(C)};{f1(C)};0", f"0;{fx(begin / (begin + .6), 3)};1", begin + .6,
                        spline="0 0 1 1;.3 0 .2 1") + "</circle>") if M.MOTION else "/>"
        return (f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="none" stroke="{c(self.mark)}" '
                f'stroke-width="2.2" transform="rotate(-90 {f1(cx)} {f1(cy)})"' + dash)

    def chip(self, label, message="", *, icon=None, size=11.0, lab="label", msg="count") -> Plate:
        return Plate(self, label, message, icon=icon, size=size, solo="outline" if lab in ("safe", "label") else "solid")

    def glint(self, cv, solid=True) -> tuple[str, str]:
        """A band across the turn plate: white across a dark block, the sheet's colour across a light one (a white
        block after dark), the line's across a plate's paper."""
        if not solid:
            return f'url(#{self._grad(cv, "sl")})', ".3"
        return (f'url(#{self._grad(cv, "sp")})', ".35") if self.light_line else (f'url(#{self._grad(cv, "sw")})', ".5")

    def key(self, cv, x, y, size, tone) -> str:
        """A key's swatch, in the material its part is drawn in: solid, lined or open; the last move's, its mark."""
        col = self.col
        line = c(col["line"])
        if tone == "house":
            return f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(size)}" height="{f1(size)}" fill="{line}"/>'
        if tone == "last":
            return (f'<rect x="{f1(x + .8)}" y="{f1(y + .8)}" width="{f1(size - 1.6)}" height="{f1(size - 1.6)}" '
                    f'fill="{c(col["paper"])}" stroke="{c(self.mark)}" stroke-width="1.6"/>')
        fill = f'url(#{self._hatch(cv, "bar")})' if tone == "world" else c(col["paper"])
        return (f'<rect x="{f1(x + .4)}" y="{f1(y + .4)}" width="{f1(size - .8)}" height="{f1(size - .8)}" '
                f'fill="{fill}" stroke="{line}" stroke-width=".8"/>')

    def segment(self, cv, x, y, w, h, tone) -> str:
        line = c(self.col["line"])
        if tone == "house":
            return f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(w)}" height="{f1(h)}" fill="{line}"/>'
        fill = f'url(#{self._hatch(cv, "bar")})' if tone == "world" else c(self.col["paper"])
        return (f'<rect x="{f1(x + .4)}" y="{f1(y + .4)}" width="{f1(max(w - .8, .4))}" height="{f1(h - .8)}" '
                f'fill="{fill}" stroke="{line}" stroke-width=".8"/>')

    def row_mark(self, x, y, w, h) -> str:
        """The latest move's row, boxed: kept a few pixels in from the left, clear of a phone's border."""
        return (f'<rect x="{f1(x + 3)}" y="{f1(y)}" width="{f1(w - 3)}" height="{f1(h)}" rx="2" '
                f'fill="{c(self.col["line"])}" fill-opacity=".07" {hair(self.col, .45)} stroke-width=".8"/>')

    # --- the hall of fame
    def face(self, cv, cx, cy, r, p, i, medal=None, glint=False) -> str:
        """A winner's medallion on its dial; round the podium's, a medal in the materials of the series bar: the
        gold one solid, the silver lined, the bronze open."""
        col = self.col
        line = c(col["line"])
        out = []
        if medal is not None:
            rr = r + 4.5
            if medal == 0:
                out.append(f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(rr)}" fill="none" stroke="{line}" '
                           f'stroke-width="3.6"/>')
            else:
                if medal == 1:
                    out.append(f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(rr)}" fill="none" '
                               f'stroke="url(#{self._hatch(cv, "ring")})" stroke-width="3.6"/>')
                out.append(f'<path d="M{f1(cx - rr + 1.8)} {f1(cy)}a{f1(rr - 1.8)} {f1(rr - 1.8)} 0 1 0 '
                           f'{f1(2 * rr - 3.6)} 0a{f1(rr - 1.8)} {f1(rr - 1.8)} 0 1 0 {f1(-2 * rr + 3.6)} 0Z'
                           f'M{f1(cx - rr - 1.8)} {f1(cy)}a{f1(rr + 1.8)} {f1(rr + 1.8)} 0 1 0 {f1(2 * rr + 3.6)} 0'
                           f'a{f1(rr + 1.8)} {f1(rr + 1.8)} 0 1 0 {f1(-2 * rr - 3.6)} 0Z" fill="none" stroke="{line}" '
                           f'stroke-width=".9"/>')
            if glint and M.MOTION:
                out.append(halo_glint(cx, cy, rr) if self.light_line else medal_glint(cx, cy, rr, paint=c("white")))
        if p.get("house"):
            out.append(self.medallion(cv, cx, cy, r, "white"))
        else:
            size = r * .72
            out.append(self._dial(cx, cy, r) + self.say(cv, p["initials"], cx, cy + self.cap(size) / 2, size, ls=.8,
                                                        anchor="middle"))
        return "".join(out)

    def draws_disc(self, cv, cx, cy, r) -> str:
        return self._dial(cx, cy, r) + self.say(cv, "=", cx, cy + self.cap(r) / 2, r, anchor="middle")

    def vacant(self, cv, cx, cy, r, i) -> str:
        """A place on the podium nobody has won yet: a dial inside a dashed ring, and a question."""
        rr = r + 4.5
        return (f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(rr)}" fill="none" stroke="{c(self.col["line"])}" '
                f'stroke-width="1.2" stroke-dasharray="4 3"/>' + self._dial(cx, cy, r)
                + self.say(cv, "?", cx, cy + self.cap(r * .8) / 2, r * .8, role="muted", anchor="middle"))

    def track(self, cv, x, y, w, h) -> str:
        return f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(w)}" height="{f1(h)}" fill="none" {hair(self.col, .5)}/>'

    def fill_bar(self, cv, x, y, w, h) -> str:
        return (f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(w)}" height="{f1(h)}" fill="url(#{self._hatch(cv, "bar")})" '
                f'stroke="{c(self.col["line"])}"/>')

    def number(self, cv, n, x, y, size) -> str:
        """A callout's number in a bubble, as a drawing numbers its notes."""
        col = self.col
        r = size / 2
        return (f'<circle cx="{f1(x + r)}" cy="{f1(y + r)}" r="{f1(r - .6)}" fill="{c(col["paper"])}" '
                f'stroke="{c(col["line"])}" stroke-width="1.2"/>'
                + self.say(cv, str(n), x + r, y + r + self.cap(size * .62) / 2, size * .62, anchor="middle"))

    def badge_file(self, i, p) -> str:
        """A winner's own badge: the kit's blueprint plate, on its own drafting paper; the leader's catches the
        light every seven seconds, as the standard theme's does."""
        col = self.col
        plate = Plate(self, f"#{i + 1}  {p['badge']}", f"{p['wins']} win" + ("s" if p["wins"] != 1 else ""),
                      icon="trophy" if i == 0 else "medal", size=11)
        cv = Canvas(plate.w, plate.h, title=f"Hall of Fame: {p['badge']}",
                    desc=f"Number {i + 1}, {p['badge']}, {p['wins']} wins", stamp=f"{self.tone} elements chess hall badge {self.theme}")
        grid = cv.uid("p")
        cv.defs.append(f'<pattern id="{grid}" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M10 .5H.5V10" '
                       f'fill="none" {hair(col, .085 if self.dark else .08)}/></pattern>')
        whole = f'width="{f1(plate.w)}" height="{f1(plate.h)}"'
        cv.add(f'<rect {whole} fill="{c(col["paper"])}"/>'
               + ("" if self.dark else f'<rect {whole} fill="{c(col["edge"])}" fill-opacity=".03"/>')
               + f'<rect {whole} fill="url(#{grid})"/>')
        body = plate.draw(cv, 0, 0, "winner").replace(f'fill="{c(col["paper"])}" stroke=', 'fill="none" stroke=', 1)
        cv.add(body)
        if i == 0 and M.MOTION:
            clip = cv.uid("b")
            cv.defs.append(f'<clipPath id="{clip}"><rect width="{f1(plate.w)}" height="{f1(plate.h)}"/></clipPath>')
            cv.add(f'<g clip-path="url(#{clip})"><rect x="-40" y="-4" width="34" height="{f1(plate.h + 8)}" '
                   f'fill="url(#{self._grad(cv, "sl")})" opacity=".0" transform="skewX(-20)">'
                   + M.ani("x", f"-40;-40;{f1(plate.w + 30)};{f1(plate.w + 30)}", "0;.8;.92;1", M.GLINT, begin=1,
                           repeat=True)
                   + M.ani("opacity", "0;0;.3;.3;0", "0;.8;.81;.92;1", M.GLINT, begin=1, repeat=True)
                   + "</rect></g>")
        return cv.svg()
