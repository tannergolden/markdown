# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The badges every holiday set draws: a page's own badges, in the set's pixels.

A set restyles a badge and never changes what it is. Each keeps its style's
height in the kit (for-the-badge 28 px; flat, flat-square and pill 20;
plastic 18; compact 16), so a row never moves when a holiday comes or goes;
it keeps its icon, one of the kit's 64 glyphs, drawn in pixels in the
label's ink; and it keeps its files. A classic badge is one file. A plate
has a day file and a night file. A live badge is one file, its label in the
set's gold and its value in its state's colour, and a live plate keeps room
for every value it can show, so it never changes width. A written colour
becomes the nearest the set has. The set's touch lies in a badge's own top
two rows, and the letters are centred in what is left.
"""
from __future__ import annotations

import math

from ...palette import PALETTE
from ..pixel import GLYPHS, MISSING, Pix, fold, measure

# In the canvas's pixels, which the file draws two to one. `isz` is the icon's size: the kit's 15 and 14
# px icons draw at 7 by 7, its 12 and 10 px ones at 5 by 5.
STYLES = {
    "for-the-badge": dict(h=14, font="57", pad=6, isz=7, gap=3, track=2, corner="sharp"),
    "flat": dict(h=10, font="35", pad=4, isz=7, gap=2, track=1, corner="notch"),
    "flat-square": dict(h=10, font="35", pad=4, isz=7, gap=2, track=1, corner="sharp"),
    "plastic": dict(h=9, font="35", pad=4, isz=5, gap=2, track=1, corner="notch", shine=True),
    "pill": dict(h=10, font="35", pad=6, isz=7, gap=2, track=1, corner="pill"),
    "compact": dict(h=8, font="35", pad=3, isz=5, gap=2, track=1, corner="notch"),
}
TOP = 2          # the rows at a badge's top the set's touch may take
PLATE = "blueprint-"
STATES = ("green", "yellow", "red", "slate")


def inside(x, y, w, h, corner) -> bool:
    """Whether (x, y) is inside a badge `w` by `h` with this corner: square, a notch, or a pill's round end."""
    if corner == "notch":
        return not ((x in (0, w - 1)) and (y in (0, h - 1)))
    if corner == "pill":
        r = h / 2
        dy = abs(y + 0.5 - h / 2)
        inset = math.ceil(r - math.sqrt(max(0.0, r * r - dy * dy)) - 0.35)
        return inset <= x < w - inset
    return True


def _lab(hexc: str) -> tuple:
    """A colour in CIE Lab, for telling which of a set's colours a written one is nearest."""
    def lin(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(int(hexc[i:i + 2], 16)) for i in (1, 3, 5))
    xyz = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047, 0.2126 * r + 0.7152 * g + 0.0722 * b, \
        (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = [t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116 for t in xyz]
    return 116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])


def nearest(hexc: str, swatches: dict) -> str:
    """The name of the swatch whose block is nearest `hexc`."""
    want = _lab(hexc)
    return min(swatches, key=lambda n: (sum((a - b) ** 2 for a, b in zip(want, _lab(swatches[n][0]))), n))


class Badges:
    """The badge layouts. Every drawing hook a set overrides is listed first."""

    # ------------------------------------------------------------------------------------------ hooks
    def badge_top(self, p: Pix, w: int, s: dict, seed: int, night: bool):
        """The set's touch along a badge's top two rows, kept inside its shape (see `inside`)."""

    def badge_label(self) -> tuple:
        """A static badge's label: its block and its letters."""
        raise NotImplementedError

    def badge_gold(self) -> tuple:
        """A live badge's label, the set's gold: its block and its letters."""
        raise NotImplementedError

    def badge_states(self) -> dict:
        """Each state a live badge shows (green, yellow, red, slate): its block and its letters."""
        raise NotImplementedError

    def badge_swatches(self) -> dict:
        """The colours a static badge's value may take, by name: its block, its letters and a pattern (or
        None). A written colour takes the nearest block."""
        raise NotImplementedError

    def badge_pattern(self, pattern: str, x, y, c, s: dict, text_rows: range) -> str:
        """The colour at (x, y) of a block in `pattern`, `c` its plain colour. `text_rows` are the rows its
        letters take, which a pattern that would muddy them keeps out of."""
        return c

    def badge_outline(self, pattern: str) -> str | None:
        """The line round a value block in `pattern`, or None."""
        return None

    def badge_shine(self, c: str, y: int, h: int) -> str:
        """Plastic's gloss at row `y` of `h`: its foot shaded a step."""
        return c

    def plate_colours(self, mode: str) -> dict:
        """A plate's colours in `mode` (day, night or live): its paper and the dot on it, its frame, the
        value's block and letters, and the label's ink. A live plate's block and letters are its state's,
        and its paper's edge is `edge`."""
        raise NotImplementedError

    # ------------------------------------------------------------------------------------ the layouts
    @staticmethod
    def _text_y(s: dict) -> int:
        """Where the letters sit: centred between the set's two top rows and the foot."""
        cap = 7 if s["font"] == "57" else 5
        return TOP + max(0, (s["h"] - TOP - 1 - cap) // 2)

    @staticmethod
    def _layout(style: str, label: str, message: str, icon, reserve=()):
        """The style, the label and value as lettered, and the widths of the label's block and the
        value's, the value's kept wide enough for each of `reserve` too."""
        s = STYLES[style]
        lab, msg = fold(label.upper(), s["font"]), fold(message.upper(), s["font"])
        lw = measure(lab, s["font"], 1, s["track"])
        room = max([measure(msg, s["font"], 1, s["track"])]
                   + [measure(fold(str(v).upper(), s["font"]), s["font"], 1, s["track"]) for v in reserve])
        extra = 1 if s["corner"] == "pill" else 0
        left = (s["pad"] + (s["isz"] + s["gap"] if icon else 0) + lw + s["pad"] - 1 + extra) if (lab or icon) else 0
        right = (s["pad"] + room + s["pad"] - 1 + extra) if room or not left else 0
        return s, lab, msg, left, right, room

    def _letters(self, p: Pix, s: dict, left, right, room, lab, msg, icon, lab_ink, msg_ink):
        """The icon and the label in the label's ink, the value in its own, centred in its block."""
        ty = self._text_y(s)
        x = s["pad"] + (1 if s["corner"] == "pill" else 0)
        if icon:
            cap = 7 if s["font"] == "57" else 5
            p.sprite(x, ty + (cap - s["isz"]) // 2, GLYPHS[s["isz"]][icon], {"#": lab_ink})
            x += s["isz"] + s["gap"]
        if lab:
            p.text(x, ty, lab, lab_ink, s["font"], track=s["track"])
        mw = measure(msg, s["font"], 1, s["track"])
        mx = left + s["pad"] - (0 if s["corner"] == "pill" else 1) + (room - mw) // 2
        if msg:
            p.text(mx, ty, msg, msg_ink, s["font"], track=s["track"])

    def classic_badge(self, style: str, label: str, message: str, icon, lab: tuple, val: tuple,
                      pattern=None, night=False) -> Pix:
        """A classic badge: the label and the value on two blocks of colour, in the style's own shape."""
        s, labt, msg, left, right, room = self._layout(style, label, message, icon)
        w, h = left + right, s["h"]
        p = Pix(w, h)
        ty = self._text_y(s)
        rows = range(ty - 1, ty + (7 if s["font"] == "57" else 5) + 1)
        for y in range(h):
            for x in range(w):
                if not inside(x, y, w, h, s["corner"]):
                    continue
                c = lab[0] if x < left else val[0]
                if x >= left and pattern:
                    c = self.badge_pattern(pattern, x, y, c, s, rows)
                if s.get("shine"):
                    c = self.badge_shine(c, y, h)
                p.px(x, y, c)
        line = self.badge_outline(pattern) if pattern else None
        if line:
            for y in range(h):
                for x in range(left, w):
                    if inside(x, y, w, h, s["corner"]) and (y in (0, h - 1) or not inside(x + 1, y, w, h, s["corner"])):
                        p.px(x, y, line)
        self.badge_top(p, w, s, len(label) + len(message), night)
        self._letters(p, s, left, right, room, labt, msg, icon, lab[1], val[1])
        return p

    def plate_badge(self, style: str, label: str, message: str, icon, mode: str, state: str | None = None,
                    reserve=()) -> Pix:
        """A plate, a style's blueprint twin: the label on dotted paper, the value on a solid block, the
        whole framed. A static plate has a day and a night drawing; a live one is drawn once."""
        s, labt, msg, left, right, room = self._layout(style, label, message, icon, reserve)
        w, h = left + right, s["h"]
        p = Pix(w, h)
        k = self.plate_colours(mode)
        block, letters = self.badge_states()[state or "green"] if mode == "live" else (k["block"], k["letters"])
        for y in range(h):
            for x in range(w):
                if inside(x, y, w, h, s["corner"]):
                    c = (k["dot"] if (x % 4 == 2 and y % 4 == 2) else k["paper"]) if x < left else block
                    p.px(x, y, c)
        for y in range(h):
            for x in range(w):
                if not inside(x, y, w, h, s["corner"]):
                    continue
                if y in (0, h - 1) or not inside(x - 1, y, w, h, s["corner"]) or not inside(x + 1, y, w, h, s["corner"]):
                    p.px(x, y, k["frame"] if mode != "live" else k["edge"] if x < left else self.plate_edge(block))
        self.badge_top(p, w, s, len(label) * 3 + len(message), mode == "night")
        self._letters(p, s, left, right, room, labt, msg, icon, k["ink"], letters)
        return p

    def plate_edge(self, block: str) -> str:
        """The edge round a live plate's value: its block a step darker."""
        return block

    # ------------------------------------------------------------------------------------ the entry point
    def can_letter(self, style: str, *texts: str) -> bool:
        """Whether the set's lettering draws every character of `texts` in `style`."""
        font = STYLES[style.removeprefix(PLATE)]["font"]
        MISSING.clear()
        for t in texts:
            fold(str(t).upper(), font)
        ok = not MISSING
        MISSING.clear()
        return ok

    def badge(self, *, style: str, label: str, message: str, icon: str | None, label_hex: str, message_hex: str,
              live: bool, state: str | None, reserve: tuple, rels: list, stamp: str) -> dict | None:
        """One badge's files, {path: svg}, at the kit's paths `rels`: a classic badge or a live one in one
        file, a static plate in its day and night files. None when the set's lettering cannot draw it,
        and the kit draws it as it always does."""
        plate = style.startswith(PLATE)
        base = style.removeprefix(PLATE)
        if base not in STYLES or not self.can_letter(style, label, message, *reserve):
            return None
        icon = icon if icon and icon in GLYPHS[STYLES[base]["isz"]] else None
        said = f"{label}: {message}" if label and message else (label or message)

        def done(p: Pix) -> str:
            return p.svg(said, "", still=True, stamp=stamp) + "\n"
        if live:
            st = state if state in STATES else "slate"
            if plate:
                return {rels[0]: done(self.plate_badge(base, label, message, icon, "live", st, reserve))}
            return {rels[0]: done(self.classic_badge(base, label, message, icon, self.badge_gold(),
                                                     self.badge_states()[st]))}
        if plate:
            return {rel: done(self.plate_badge(base, label, message, icon, mode, None, reserve))
                    for rel, mode in zip(rels, ("day", "night"))}
        swatches = self.badge_swatches()
        lab = self.badge_label() if label_hex.upper() == PALETTE["black"].upper() \
            else swatches[nearest(label_hex, swatches)][:2]
        block, ink, pattern = swatches[nearest(message_hex, swatches)]
        return {rels[0]: done(self.classic_badge(base, label, message, icon, lab, (block, ink), pattern))}
