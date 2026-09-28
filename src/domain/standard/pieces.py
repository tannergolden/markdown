# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The standard theme's pieces: a badge's own parts, at every scale.

A badge is two flat panels side by side: a label, black, holding an icon and
a word in bold letter-spaced capitals, and a message in the colour that says
what the word is. The standard theme draws its banners and elements from that
and little else: panels, capitals, the 64 icons and the palette's tokens,
lettered in DejaVu Sans (`sans` and `sans-bold`), the face a badge's Verdana
falls back to.

Every letter is set on a ground it holds 4.5:1 against, the contrast WCAG asks
of body text. `letters_on` puts white on a panel white holds on and black on
the rest, which then always holds, and the two themes fix every other pair.
`text` records each pair it sets in `PAIRS`, so a test can prove every one.

Motion follows the headers' rules: a file that moves is complete without
SMIL, because every animated attribute carries its resting value and the
animation only holds it back until its turn.
"""
from __future__ import annotations

from ..canvas import Canvas, c
from ..draw import icon, solid, up_arrow
from ..lettering import cap_height, f1, flow, fx, width
from ..palette import hexof

# The file draws its own paper, so it reads the same whatever GitHub paints
# behind it: white by day with a hairline of ash, black by night with a
# hairline of charcoal. A label panel is black by day, as a badge's is, and
# charcoal by night, where black would vanish into the paper.
DAY = {"name": "day", "dark": False, "paper": "white", "edge": "ash", "label": "black", "strong": "black",
       "ink": "charcoal", "muted": "slate", "rule": "ash"}
DARK = {"name": "dark", "dark": True, "paper": "black", "edge": "charcoal", "label": "charcoal", "strong": "white",
        "ink": "white", "muted": "ash", "rule": "charcoal"}

# The message panel of the theme's own plates: a header's release or account, an element's subject, the way up.
ACCENT = "cobalt"

# A figure's badge, by the label a header gives it: its icon, and the colour of its message panel.
FIGURES = {
    "PROJECT": ("book", "slate"), "RELEASE": ("tag", "cobalt"), "STARS": ("star", "amber"),
    "FORKS": ("branch", "ocean"), "WATCHERS": ("eye", "steel"), "OPEN ISSUES": ("alert", "tangerine"),
    "OPEN PULL REQUESTS": ("sync", "iris"), "LANGUAGE": ("code", "purple"), "LICENSE": ("scale", "yellow"),
    "UPDATED": ("calendar", "slate"), "CREATED": ("rocket", "slate"), "SITE": ("globe", "cobalt"),
    "ACCOUNT": ("users", "magenta"), "FOLLOWERS": ("users", "denim"), "FOLLOWING": ("eye", "steel"),
    "REPOSITORIES": ("book", "ocean"), "STARS EARNED": ("star", "amber"),
    "CONTRIBUTIONS, LAST YEAR": ("commit", "forest"), "MEMBER SINCE": ("calendar", "slate"),
    "LOCATION": ("pin", "brick"), "COMPANY": ("home", "steel"),
}

# Every (letters, ground, what) a drawing has set, both tokens, so a test can hold each pair to 4.5:1.
PAIRS: set[tuple[str, str, str]] = set()


def theme(th: dict) -> dict:
    """The standard theme for one of GitHub's two: `th` is `canvas.DAY` or `canvas.DARK`."""
    return DARK if th["dark"] else DAY


def figure(label: str) -> tuple[str, str]:
    """A figure's icon and message colour; a label the kit does not know is a slate badge with an info icon."""
    return FIGURES.get(label.upper(), ("info", "slate"))


# --- colour and contrast ----------------------------------------------------------------------

def luminance(token: str) -> float:
    """WCAG's relative luminance of a token."""
    h = hexof(token).lstrip("#")
    ch = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    ch = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in ch]
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]


def contrast(a: str, b: str) -> float:
    """WCAG's contrast ratio between two tokens, from 1 to 21."""
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def letters_on(panel: str) -> str:
    """White letters on a panel white holds 4.5:1 on, else black.

    One or the other always holds: white fails only above a luminance of
    .183, and black holds from .175 up.
    """
    return "white" if contrast("white", panel) >= 4.5 else "black"


# --- drawing ----------------------------------------------------------------------------------

def new(w: float, h: float, title: str, desc: str, stamp: str) -> Canvas:
    """A canvas stamped as the standard theme's."""
    return Canvas(w, h, title=title, desc=desc, stamp=f"standard {stamp}")


def text(cv: Canvas, s: str, *, x: float, y: float, size: float, fill: str, ground: str, face: str = "sans",
         anchor: str = "start", ls: float = 0.0, what: str = "text") -> str:
    """A run of letters in `fill` on `ground`, both tokens, its baseline at `y`, recorded in `PAIRS`."""
    if not s:
        return ""
    PAIRS.add((fill, ground, what))
    return cv.L.text(s, face=face, size=size, x=x, y=y, anchor=anchor, ls=ls, fill=c(fill))


def lines(cv: Canvas, rows: list[str], th: dict, *, x: float, top: float, size: float, lead: float,
          anchor: str = "start", fill: str | None = None, what: str = "prose") -> str:
    """Prose set a line to `lead`, the first line's capitals standing at `top`."""
    return "".join(text(cv, row, x=x, y=top + size * .76 + i * lead, size=size, fill=fill or th["ink"],
                        ground=th["paper"], anchor=anchor, what=what) for i, row in enumerate(rows))


def prose(s: str, size: float, max_w: float, rows: int = 3) -> tuple[float, list[str]]:
    """`s` in the book face, wrapped into at most `rows` lines no wider than `max_w`, three points smaller at most."""
    if not s:
        return size, []
    return flow(s, "sans", size, size - 3, max_w, 0, rows=rows)


def fitted(s: str, face: str, size: float, floor: float, max_w: float, ls_em: float = 0.0) -> float:
    """The largest size, from `size` down to `floor` a quarter point at a time, at which `s` fits `max_w`."""
    while size > floor and width(s, face, size, size * ls_em) > max_w:
        size -= .25
    return size


def rect(x: float, y: float, w: float, h: float, fill: str, rx: float = 0) -> str:
    r = f' rx="{f1(rx)}"' if rx else ""
    return f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(w)}" height="{f1(h)}"{r} fill="{c(fill)}"/>'


def card(cv: Canvas, th: dict, w: float, h: float) -> str:
    """The card every file is drawn on: the theme's paper inside a hairline edge. Returns a clip to its corners."""
    cv.add(f'<rect x=".5" y=".5" width="{f1(w - 1)}" height="{f1(h - 1)}" rx="6" fill="{c(th["paper"])}" '
           f'stroke="{c(th["edge"])}"/>')
    cid = cv.uid("c")
    cv.defs.append(f'<clipPath id="{cid}"><rect x=".5" y=".5" width="{f1(w - 1)}" height="{f1(h - 1)}" rx="6"/>'
                   "</clipPath>")
    return cid


def rule(x0: float, x1: float, y: float, th: dict) -> str:
    """A hairline across the card, in the theme's rule."""
    return f'<path d="M{f1(x0)} {f1(y)}H{f1(x1)}" stroke="{c(th["rule"])}"/>'


# --- a badge at any size ----------------------------------------------------------------------

class Chip:
    """A badge's two panels, measured before they are drawn.

    The label, with its icon, on the left in the label colour; the message on
    the right in its own. `size` is the letter size; everything else keeps
    the for-the-badge proportions the badges draw at 11 px: 28 tall, 12 of
    padding, a 15 px icon.
    """

    def __init__(self, label: str, message: str = "", *, icon: str | None = None, size: float = 11.0,
                 lab: str = "black", msg: str = "slate", heart: str | None = None, ls_em: float = .09) -> None:
        self.label, self.message = label.upper(), message.upper()
        self.icon, self.size, self.lab, self.msg, self.heart = icon, size, lab, msg, heart
        self.ls = size * ls_em
        k = size / 11
        self.h = 28 * k
        self.pad, self.isz, self.gap = 12 * k, 15 * k, 6 * k
        words = width(self.label, "sans-bold", size, self.ls) if self.label else 0
        self.lw = 2 * self.pad + words + ((self.isz + (self.gap if self.label else 0)) if icon else 0)
        self.mw = (2 * self.pad + width(self.message, "sans-bold", size, self.ls)) if self.message else 0
        self.w = self.lw + self.mw

    def draw(self, cv: Canvas, x: float, y: float, what: str = "badge") -> str:
        out = [rect(x, y, self.lw, self.h, self.lab)]
        base = y + self.h / 2 + cap_height("sans-bold", self.size) / 2
        tx = x + self.pad
        on = letters_on(self.lab)
        if self.icon:
            iy = y + (self.h - self.isz) / 2
            # A heart is filled, in its own colour, the way the love in "built with" is drawn everywhere.
            out.append(solid(self.icon, tx, iy, self.isz, self.heart) if self.heart else
                       icon(self.icon, tx, iy, self.isz, on, 2.1))
            tx += self.isz + self.gap
        out.append(text(cv, self.label, x=tx, y=base, size=self.size, face="sans-bold", ls=self.ls, fill=on,
                        ground=self.lab, what=f"{what} label"))
        if self.message:
            out.append(rect(x + self.lw, y, self.mw, self.h, self.msg))
            out.append(text(cv, self.message, x=x + self.lw + self.pad, y=base, size=self.size, face="sans-bold",
                            ls=self.ls, fill=letters_on(self.msg), ground=self.msg, what=f"{what} message"))
        return "".join(out)


def rows(chips: list, max_w: float, gap: float = 8.0) -> list[list]:
    """Badges in rows no wider than `max_w`, in order, each row filled before the next, as a README wraps them."""
    out: list[list] = []
    for chip in chips:
        if out and row_width(out[-1] + [chip], gap) <= max_w:
            out[-1].append(chip)
        else:
            out.append([chip])
    return out


def row_width(row: list, gap: float = 8.0) -> float:
    return sum(chip.w for chip in row) + gap * (len(row) - 1)


class Outline:
    """A badge drawn in outline: a frame, an icon and a word in the ink, on the paper.

    It is a badge's shape for something said rather than measured: the
    motto, a note, a planned release.
    """

    def __init__(self, label: str, *, icon: str | None = None, size: float = 10.5, ls_em: float = .12) -> None:
        self.label, self.icon, self.size, self.ls = label.upper(), icon, size, size * ls_em
        k = size / 11
        self.h, self.pad, self.isz, self.gap = 28 * k, 12 * k, 14 * k, 7 * k
        self.w = 2 * self.pad + width(self.label, "sans-bold", size, self.ls) + ((self.isz + self.gap) if icon else 0)

    def draw(self, cv: Canvas, x: float, y: float, th: dict, what: str = "outline", dashed: bool = False) -> str:
        ink = th["ink"]
        dash = ' stroke-dasharray="3 2"' if dashed else ""
        out = [f'<rect x="{f1(x + .75)}" y="{f1(y + .75)}" width="{f1(self.w - 1.5)}" height="{f1(self.h - 1.5)}" '
               f'fill="{c(th["paper"])}" stroke="{c(ink)}" stroke-width="1.5"{dash}/>']
        tx = x + self.pad
        if self.icon:
            out.append(icon(self.icon, tx, y + (self.h - self.isz) / 2, self.isz, ink, 2.1))
            tx += self.isz + self.gap
        out.append(text(cv, self.label, x=tx, y=y + self.h / 2 + cap_height("sans-bold", self.size) / 2,
                        size=self.size, face="sans-bold", ls=self.ls, fill=ink, ground=th["paper"], what=what))
        return "".join(out)


class Action:
    """A badge that goes somewhere: the label panel with its icon and word, and a short panel of the accent
    carrying an arrow. `up` turns the arrow to point up, for the way back to the top."""

    def __init__(self, label: str, *, icon_name: str | None = None, size: float = 11.0, lab: str = "black",
                 up: bool = False) -> None:
        self.chip = Chip(label, "", icon=icon_name, size=size, lab=lab)
        self.aw, self.up = 30 * size / 11, up
        self.h, self.w = self.chip.h, self.chip.w + self.aw

    def draw(self, cv: Canvas, x: float, y: float, what: str = "action") -> str:
        ch = self.chip
        s = 14 * ch.size / 11
        ax, ay = x + ch.w + (self.aw - s) / 2, y + (ch.h - s) / 2
        on = letters_on(ACCENT)
        arrow = up_arrow(ax, ay, s, on, 2.3) if self.up else icon("arrow", ax, ay, s, on, 2.3)
        return ch.draw(cv, x, y, what) + rect(x + ch.w, y, self.aw, ch.h, ACCENT) + arrow


# --- motion -----------------------------------------------------------------------------------

def rise(markup: str, begin: float, dur: float = .45, lift: float = 6.0) -> str:
    """Markup that fades up into place `begin` seconds after the page opens, once, and stays."""
    t = begin + dur
    k = fx(begin / t, 3)
    return (f'<g opacity="1"><animate attributeName="opacity" values="0;0;1" keyTimes="0;{k};1" dur="{fx(t, 2)}s" '
            f'fill="freeze"/><animateTransform attributeName="transform" type="translate" '
            f'values="0 {f1(lift)};0 {f1(lift)};0 0" keyTimes="0;{k};1" dur="{fx(t, 2)}s" calcMode="spline" '
            f'keySplines="0 0 1 1;.2 .7 .3 1" fill="freeze"/>{markup}</g>')


def wipe(cv: Canvas, markup: str, x: float, y: float, w: float, h: float, begin: float = 0.0,
         dur: float = .6) -> str:
    """Markup revealed left to right, as a panel sliding open, once."""
    cid = cv.uid("c")
    t = begin + dur
    k = fx(begin / t, 3) if begin else "0"
    cv.defs.append(f'<clipPath id="{cid}"><rect x="{f1(x)}" y="{f1(y)}" width="{f1(w)}" height="{f1(h)}">'
                   f'<animate attributeName="width" values="0;0;{f1(w)}" keyTimes="0;{k};1" dur="{fx(t, 2)}s" '
                   f'calcMode="spline" keySplines="0 0 1 1;.2 .7 .2 1" fill="freeze"/></rect></clipPath>')
    return f'<g clip-path="url(#{cid})">{markup}</g>'
