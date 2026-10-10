# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-FileCopyrightText: 2018 Metabolize LLC (anafanafo font-metrics data)
# SPDX-License-Identifier: MIT
"""The classic badges: six styles a README already knows, lettered in the reader's Verdana.

A badge is a label and a message side by side, in the badges kit's own
styles, with an icon from the 64. Six styles, grouped by the job:

  Headline   for-the-badge (the default; bold uppercase, 28px)
  Standard   flat (20px, rounded, a soft wash), flat-square (square, flat),
             plastic (18px, bevelled) and pill (20px, fully round)
  Dense      compact (16px)

Unlike every other file the kit draws, a classic badge is set in a font, the
way shields.io sets its own: Verdana, falling back to DejaVu Sans. Its text is
measured with Verdana's real metrics and pinned with `textLength`, so a badge
renders at the same width on every platform. Static badges take a black
label; a live badge takes the gold one, and its message colour carries its
state. These are the badges kit's drawings, byte for byte but for the stamp.
"""
from __future__ import annotations

import hashlib
import re
from html import escape

from .. import KIT, KIT_VERSION
from ..canvas import prose
from ..palette import ICONS, PALETTE

_HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")

# The traffic-light subset a dynamic-health badge may use to represent a
# STATUS with color (plus slate as the reserved "no status yet" neutral).
# Enforced in data.validate() and documented in Document-Styling-&-Formatting.md.
HEALTH_COLORS = {"green", "yellow", "red"}
HEALTH_NEUTRAL = {"slate"}

# The pool a rotating STATIC badge draws its message color from (see
# data.rotate): the whole designed palette EXCEPT the reserved tokens -
# the traffic-light triad (a static badge must never resemble a status), the
# black label color, the gold dynamic-health label, the slate neutral, and
# white (invisible on GitHub's canvas). Sorted for deterministic indexing.
_RANDOM_RESERVED = (
    HEALTH_COLORS
    | HEALTH_NEUTRAL
    | {"black", "gold", "white"}
    # Slot colors the docs law fixes for header identity badges: pink is
    # the Role/Identification slot (FE5196) and purple the Context slot
    # (9C27B0). Rotation must never paint a decorative badge INTO one, or
    # the standards' badge-slot rules would fail the tree.
    | {"pink", "purple"}
)
STATIC_RANDOM_POOL = sorted(t for t in PALETTE if t not in _RANDOM_RESERVED)


FONT = "Verdana,'DejaVu Sans',Geneva,sans-serif"

# --------------------------------------------------------------------------- #
# Character advance widths, measured from the real font so a badge is sized
# the way shields.io sizes its own (no more guessed average width: 'W' is
# 12.4px, 'I' is 6.0px). Ranges are (loCodepoint, hiCodepoint, px). Derived
# from the MIT-licensed anafanafo dataset (Copyright (c) 2018 Metabolize LLC,
# the measurement tables shields.io itself uses): Verdana bold 10px scaled
# linearly to 11px, and Verdana normal 11px as-is. Non-ASCII falls back to a
# generous default so a badge can pad, never overflow. `textLength` on every
# <text> pins the rendered run to these widths on every platform, so a
# viewer without Verdana (Linux/DejaVu) sees the same badge geometry.
# --------------------------------------------------------------------------- #
_W_BOLD11 = (
    (32, 32, 3.762), (33, 33, 4.422), (34, 34, 6.457), (35, 35, 9.537),
    (36, 36, 7.821), (37, 37, 13.992), (38, 38, 9.482), (39, 39, 3.652),
    (40, 41, 5.973), (42, 42, 7.821), (43, 43, 9.537), (44, 44, 3.971),
    (45, 45, 5.28), (46, 46, 3.971), (47, 47, 7.579), (48, 57, 7.821),
    (58, 59, 4.422), (60, 62, 9.537), (63, 63, 6.787), (64, 64, 10.604),
    (65, 65, 8.536), (66, 66, 8.382), (67, 67, 7.964), (68, 68, 9.13),
    (69, 69, 7.513), (70, 70, 7.15), (71, 71, 8.921), (72, 72, 9.207),
    (73, 73, 6.006), (74, 74, 6.105), (75, 75, 8.481), (76, 76, 7.007),
    (77, 77, 10.428), (78, 78, 9.317), (79, 79, 9.35), (80, 80, 8.063),
    (81, 81, 9.35), (82, 82, 8.602), (83, 83, 7.81), (84, 84, 7.502),
    (85, 85, 8.932), (86, 86, 8.404), (87, 87, 12.408), (88, 88, 8.404),
    (89, 89, 8.107), (90, 90, 7.612), (91, 91, 5.973), (92, 92, 7.579),
    (93, 93, 5.973), (94, 94, 9.537), (95, 96, 7.821), (97, 97, 7.348),
    (98, 98, 7.689), (99, 99, 6.468), (100, 100, 7.689), (101, 101, 7.304),
    (102, 102, 4.642), (103, 103, 7.689), (104, 104, 7.832), (105, 105, 3.762),
    (106, 106, 4.433), (107, 107, 7.381), (108, 108, 3.762), (109, 109, 11.638),
    (110, 110, 7.832), (111, 111, 7.557), (112, 113, 7.689), (114, 114, 5.467),
    (115, 115, 6.523), (116, 116, 5.016), (117, 117, 7.832), (118, 118, 7.15),
    (119, 119, 10.769), (120, 120, 7.359), (121, 121, 7.161), (122, 122, 6.567),
    (123, 123, 7.821), (124, 124, 5.973), (125, 125, 7.821), (126, 126, 9.537),
)
_W_NORM11 = (
    (32, 32, 3.87), (33, 33, 4.33), (34, 34, 5.05), (35, 35, 9.0),
    (36, 36, 6.99), (37, 37, 11.84), (38, 38, 7.99), (39, 39, 2.95),
    (40, 41, 5.0), (42, 42, 6.99), (43, 43, 9.0), (44, 44, 4.0),
    (45, 45, 5.0), (46, 46, 4.0), (47, 47, 5.0), (48, 57, 6.99),
    (58, 59, 5.0), (60, 62, 9.0), (63, 63, 6.0), (64, 64, 11.0),
    (65, 65, 7.52), (66, 66, 7.54), (67, 67, 7.68), (68, 68, 8.48),
    (69, 69, 6.96), (70, 70, 6.32), (71, 71, 8.53), (72, 72, 8.27),
    (73, 73, 4.63), (74, 74, 5.0), (75, 75, 7.62), (76, 76, 6.12),
    (77, 77, 9.27), (78, 78, 8.23), (79, 79, 8.66), (80, 80, 6.63),
    (81, 81, 8.66), (82, 82, 7.65), (83, 83, 7.52), (84, 84, 6.78),
    (85, 85, 8.05), (86, 86, 7.52), (87, 87, 10.88), (88, 88, 7.54),
    (89, 89, 6.77), (90, 90, 7.54), (91, 93, 5.0), (94, 94, 9.0),
    (95, 96, 6.99), (97, 97, 6.61), (98, 98, 6.85), (99, 99, 5.73),
    (100, 100, 6.85), (101, 101, 6.55), (102, 102, 3.87), (103, 103, 6.85),
    (104, 104, 6.96), (105, 105, 3.02), (106, 106, 3.79), (107, 107, 6.51),
    (108, 108, 3.02), (109, 109, 10.7), (110, 110, 6.96), (111, 111, 6.68),
    (112, 113, 6.85), (114, 114, 4.69), (115, 115, 5.73), (116, 116, 4.33),
    (117, 117, 6.96), (118, 118, 6.51), (119, 119, 9.0), (120, 121, 6.51),
    (122, 122, 5.78), (123, 123, 6.98), (124, 124, 5.0), (125, 125, 6.98),
    (126, 126, 9.0),
)

# Style geometry. `ls` is inter-character letter-spacing; `caps` uppercases
# the text (the for-the-badge identity); `rx` is the corner radius, 0 for
# square; `sheen` picks the overlay gradient, None for a flat chip; `mscale`
# scales the 11px metric tables to this style's font size, since the tables
# are measured at 11px and advance widths are linear in size.
#
# rx and sheen were one `deco` flag until a rounded-but-flat style needed
# them apart. Every combination is now reachable, which is what the pill and
# compact styles are.
SHEENS = {
    # The classic flat wash: a barely-there light-to-dark overlay.
    "soft": ('<stop offset="0" stop-color="#bbb" stop-opacity=".1"/>'
             '<stop offset="1" stop-opacity=".1"/>'),
    # The plastic bevel: a bright top edge falling to a dark bottom one.
    "deep": ('<stop offset="0" stop-color="#fff" stop-opacity=".7"/>'
             '<stop offset=".1" stop-color="#aaa" stop-opacity=".1"/>'
             '<stop offset=".9" stop-color="#000" stop-opacity=".3"/>'
             '<stop offset="1" stop-color="#000" stop-opacity=".5"/>'),
}

STYLES = {
    # --- Headline: bold uppercase, letter-spaced. Mastheads and doc headers.
    "for-the-badge": dict(h=28.0, pad=12.0, icon=15.0, gap=6.0, fs=11,
                          weight="700", ls=1.0, caps=True, y=18.5,
                          table=_W_BOLD11, fallback=11.0, mscale=1.0,
                          rx=0.0, sheen=None),
    # --- Standard: natural case, body rows. Square, rounded, bevelled, round.
    "flat": dict(h=20.0, pad=6.0, icon=14.0, gap=3.0, fs=11,
                 weight="400", ls=0.0, caps=False, y=14.0,
                 table=_W_NORM11, fallback=9.0, mscale=1.0,
                 rx=3.0, sheen="soft"),
    "flat-square": dict(h=20.0, pad=6.0, icon=14.0, gap=3.0, fs=11,
                        weight="400", ls=0.0, caps=False, y=14.0,
                        table=_W_NORM11, fallback=9.0, mscale=1.0,
                        rx=0.0, sheen=None),
    # The shape shields.io calls plastic. The codemod maps a plastic hotlink
    # onto this rather than flattening it, so a migration keeps its look.
    "plastic": dict(h=18.0, pad=6.0, icon=12.0, gap=3.0, fs=11,
                    weight="400", ls=0.0, caps=False, y=13.0,
                    table=_W_NORM11, fallback=9.0, mscale=1.0,
                    rx=4.0, sheen="deep"),
    # Wider padding, because a pill's round caps eat into the space the text
    # would otherwise sit in.
    "pill": dict(h=20.0, pad=10.0, icon=14.0, gap=4.0, fs=11,
                 weight="400", ls=0.0, caps=False, y=14.0,
                 table=_W_NORM11, fallback=9.0, mscale=1.0,
                 rx=10.0, sheen=None),
    # --- Dense: a table of twenty badges, or one inline in a sentence, where
    # the standard chip is taller than the line it sits on.
    "compact": dict(h=16.0, pad=5.0, icon=10.0, gap=3.0, fs=9,
                    weight="400", ls=0.0, caps=False, y=11.2,
                    table=_W_NORM11, fallback=9.0, mscale=9 / 11,
                    rx=2.0, sheen=None),
}

# Styles grouped by the job you are choosing them for, rather than by the
# order they were added. Same contract as ICON_GROUPS: drift-safe, with the
# gallery computing the leftovers, so a new style still reaches the page.
STYLE_GROUPS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("Headline", "Bold uppercase and letter-spaced. Mastheads, and the "
                 "document headers the styling standard expects.",
     ("for-the-badge",)),
    ("Standard", "Natural case, for a body row. The same chip square, "
                 "rounded, bevelled, or fully round.",
     ("flat", "flat-square", "plastic", "pill")),
    ("Dense", "Shorter than a line of text, for a table of many badges or "
              "one sitting inline in a sentence.",
     ("compact",)),
)

DEFAULT_STYLE = "for-the-badge"


class BadgeError(ValueError):
    """A badge definition the generator refuses to render silently."""


def _lum(hexc: str) -> float:
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


# The dark ink: GitHub's own text colour, for a segment white letters cannot hold.
_DARK = "#1f2328"


def _contrast(a: str, b: str) -> float:
    """WCAG's contrast ratio between two #RRGGBB colours, from 1 to 21."""
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _ink(bg: str) -> str:
    """The letters' colour on a segment: white where white holds 4.5:1 against it, else the dark ink.

    4.5:1 is the contrast WCAG asks of text, and every letter the kit sets
    is held to it: the standard theme's, the live plates', and these. White
    holds on the darker half of the palette (black, slate, blue, red,
    purple); from there up the dark ink does, and on the few mid-tones where
    neither quite holds, the one that holds more is used. The badges kit
    kept white until a luminance of .6, which left white on gold, green and
    orange at 2.5:1 to 3.5:1.
    """
    white = _contrast("#ffffff", bg)
    if white >= 4.5:
        return "#ffffff"
    dark = _contrast(_DARK, bg)
    return _DARK if dark >= 4.5 or dark > white else "#ffffff"


def _color(token: str, field: str) -> str:
    """Resolve a palette token or #RRGGBB hex; refuse anything else."""
    if token in PALETTE:
        return PALETTE[token]
    if _HEX_COLOR.match(token or ""):
        return token
    raise BadgeError(
        f"unknown color {token!r} for {field} - use a palette token "
        f"({', '.join(PALETTE)}) or #RRGGBB"
    )


def _text_width(s: str, table, fallback: float, ls: float) -> float:
    """Advance width of `s` from the font table, plus letter-spacing."""
    total = 0.0
    for ch in s:
        cp = ord(ch)
        for lo, hi, w in table:
            if lo <= cp <= hi:
                total += w
                break
        else:
            total += fallback
    if len(s) > 1:
        total += ls * (len(s) - 1)
    return total


def render(label: str, message: str, label_color: str = "black",
           message_color: str = "blue", icon: str | None = None,
           style: str = DEFAULT_STYLE) -> str:
    """Render one badge SVG. label/message are free text; colors are palette
    tokens or #RRGGBB; icon is a key in ICONS (or None); style is one of
    STYLES. Raises BadgeError on any input it cannot honor exactly."""
    if style not in STYLES:
        raise BadgeError(f"unknown style {style!r} - one of {', '.join(STYLES)}")
    if icon is not None and icon != "" and icon not in ICONS:
        raise BadgeError(
            f"unknown icon {icon!r} - list the registry with --icons"
        )
    g = STYLES[style]
    # The accessible name keeps the author's casing; only the DISPLAY text
    # is uppercased by the for-the-badge style.
    aria = f"{label}: {message}" if label and message else (label or message)
    if g["caps"]:
        label, message = label.upper(), message.upper()
    lc, mc = _color(label_color, "label_color"), _color(message_color, "message_color")
    li, mi = _ink(lc), _ink(mc)
    has = bool(icon) and icon in ICONS
    ms = g["mscale"]
    lt = _text_width(label, g["table"], g["fallback"], g["ls"] / ms) * ms
    mt = _text_width(message, g["table"], g["fallback"], g["ls"] / ms) * ms
    lw = g["pad"] + (g["icon"] + g["gap"] if has else 0) + lt + g["pad"]
    mw = g["pad"] + mt + g["pad"]
    w, h = lw + mw, g["h"]
    tx = g["pad"] + (g["icon"] + g["gap"] if has else 0)

    # Deterministic per-badge ids so many badges can be inlined in one page
    # without gradient/clip collisions (and --check stays byte-stable).
    uid = hashlib.md5(
        f"{label}|{message}|{lc}|{mc}|{icon}|{style}".encode()
    ).hexdigest()[:6]

    defs = clip_open = clip_close = sheen = ""
    grad = SHEENS.get(g["sheen"] or "", "")
    if g["rx"] or grad:
        inner = ""
        if grad:
            inner += (f'<linearGradient id="g{uid}" x2="0" y2="100%">'
                      f'{grad}</linearGradient>')
        if g["rx"]:
            inner += (f'<clipPath id="c{uid}"><rect width="{w:.1f}" '
                      f'height="{h:.0f}" rx="{g["rx"]:g}" fill="#fff"/></clipPath>')
        defs = f"<defs>{inner}</defs>"
        if g["rx"]:
            clip_open = f'<g clip-path="url(#c{uid})">'
            clip_close = "</g>"
        if grad:
            sheen = f'<rect width="{w:.1f}" height="{h:.0f}" fill="url(#g{uid})"/>'

    glyph = ""
    if has:
        glyph = (f'<g transform="translate({g["pad"]:.1f},{(h - g["icon"]) / 2:.1f}) '
                 f'scale({g["icon"] / 24:.4f})" fill="none" stroke="{li}" stroke-width="2.2" '
                 f'stroke-linecap="round" stroke-linejoin="round">{ICONS[icon]}</g>')

    def cell(x: float, text: str, tw: float, ink: str) -> str:
        if not text:
            return ""
        shadow = ""
        if g["sheen"] and ink == "#ffffff":
            # The flat style's classic legibility shadow under white text.
            shadow = (f'<text x="{x:.1f}" y="{g["y"] + 1:.1f}" fill="#010101" '
                      f'fill-opacity=".3" text-anchor="middle" font-family="{FONT}" '
                      f'font-size="{g["fs"]}" font-weight="{g["weight"]}" '
                      f'textLength="{tw:.1f}">{escape(prose(text))}</text>')
        spacing = f' letter-spacing="{g["ls"]:g}"' if g["ls"] else ""
        return (f'{shadow}<text x="{x:.1f}" y="{g["y"]:.1f}" fill="{ink}" '
                f'text-anchor="middle" font-family="{FONT}" font-size="{g["fs"]}" '
                f'font-weight="{g["weight"]}"{spacing} '
                f'textLength="{tw:.1f}">{escape(prose(text))}</text>')

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
        f'role="img" aria-label="{escape(prose(aria))}">'
        f'<!--{KIT} v{KIT_VERSION} badge-->'
        f'<title>{escape(prose(aria))}</title>{defs}{clip_open}'
        f'<rect width="{lw:.1f}" height="{h:.0f}" fill="{lc}"/>'
        f'<rect x="{lw:.1f}" width="{mw:.1f}" height="{h:.0f}" fill="{mc}"/>'
        f'{sheen}{clip_close}{glyph}'
        f'{cell(tx + lt / 2, label, lt, li)}'
        f'{cell(lw + mw / 2, message, mt, mi)}</svg>'
    )


