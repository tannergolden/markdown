# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-FileCopyrightText: 2017 The Barlow Project Authors (Barlow Condensed outlines)
# SPDX-License-Identifier: MIT
"""The blueprint plates: every badge style again, drawn the way a banner is drawn.

The label is lettered on a print's drafting paper, the value on a solid block
of the print, and the whole plate is framed in the print's line. A plate is
lettered in outlined Barlow Condensed rather than set in a font, so no
viewer's installed fonts can change a letter: every glyph is a path, embedded
once per file and placed with <use>. The outlines are the shared lettering's,
so a plate matches the banner above it, and a label or value with a character
they lack is refused at validation rather than drawn with a hole in it.

A STATIC plate is two files, `<name>.svg` for the day theme and
`<name>-dark.svg` for the night one, because a print has a day and a night.
A LIVE plate, with a gold label, is one file on a gold sheet with its value
on a block of the state's print, since a state is the same state in either
theme.
"""
from __future__ import annotations

import hashlib
from html import escape

from .. import KIT, KIT_VERSION, lettering
from ..palette import ICONS, PALETTE
from ..prints import PRINTS
from .classic import DEFAULT_STYLE, HEALTH_COLORS, HEALTH_NEUTRAL, STYLES, BadgeError, _HEX_COLOR

BLUEPRINT = "blueprint-"
DEFAULT_PRINT = "blueprint"

# A live plate's value block takes the print its state names. Yellow is drawn
# in the orangeprint: a mustard block beside the gold sheet reads as one
# colour, and a state that cannot be told from its label is no signal.
STATE_PRINT = {"green": "greenprint", "yellow": "orangeprint",
               "red": "redprint", "slate": "blackprint"}

# What a twin letters with, per base style: (size, letter-spacing), in px.
# Everything else - height, padding, icon, gap, corner, sheen and case - is
# the base style's own, so swapping a style for its twin never moves a row.
_BLUEPRINT_TYPE = {
    "for-the-badge": (11.0, 1.3),
    "flat": (11.5, 0.35),
    "flat-square": (11.5, 0.35),
    "plastic": (11.0, 0.3),
    "pill": (11.5, 0.35),
    "compact": (9.5, 0.25),
}
BLUEPRINT_STYLES = {
    BLUEPRINT + key: dict(base=key, size=size, ls=ls,
                          **{k: STYLES[key][k] for k in
                             ("h", "pad", "icon", "gap", "rx", "sheen", "caps")})
    for key, (size, ls) in _BLUEPRINT_TYPE.items()
}
DEFAULT_BLUEPRINT = BLUEPRINT + DEFAULT_STYLE

# The two finishes again, in palette tokens: white for the light, ash and
# black for the fall, so a plate carries no colour outside the family.
BLUEPRINT_SHEENS = {
    "soft": (("0", "white", ".1"), ("1", "black", ".1")),
    "deep": (("0", "white", ".7"), (".1", "ash", ".1"),
             (".9", "black", ".3"), ("1", "black", ".5")),
}

# Two cuts: SemiBold (`meta`) letters the label, Bold (`num`) the value. The
# letter is the glyph id's prefix, and neither is a hex digit, so an id can
# never read as a colour.
_FACE_ID = {"meta": "m", "num": "n"}


def _faces() -> dict:
    """The shared lettering's outlines: the same Barlow Condensed every banner is drawn in."""
    return lettering.fonts()


def _glyph(font: dict, ch: str) -> str | None:
    """The glyph that draws `ch`: its own, else its capital, else None."""
    if ch in font["g"]:
        return ch
    up = ch.upper()
    return up if up in font["g"] else None


def missing_glyphs(text: str, face: str = "meta") -> str:
    """The characters of `text` the blueprint lettering cannot draw, once each."""
    font = _faces()[face]
    out = ""
    for ch in text:
        if _glyph(font, ch) is None and ch not in out:
            out += ch
    return out


def _bp_width(text: str, face: str, size: float, ls: float) -> float:
    """Advance width of `text` at `size`, with `ls` between glyphs."""
    font = _faces()[face]
    sc = size / font["upem"]
    total = sum(font["g"][_glyph(font, ch)][1] * sc for ch in text)
    return total + ls * max(len(text) - 1, 0)


def _fx(v: float, places: int = 3) -> str:
    """`v` to at most `places` decimals, trailing zeros dropped. Rounds an
    integer rather than using a format spec, the way banners does, so a near
    tie at the last place comes out the same on every Python."""
    n = round(v * 10 ** places)
    digits = str(abs(n)).rjust(places + 1, "0")
    head, tail = digits[:-places], digits[-places:].rstrip("0")
    return ("-" if n < 0 else "") + head + ("." + tail if tail else "")


def _f1(v: float) -> str:
    return _fx(v, 1)


class _Lettering:
    """Collects the glyphs one plate uses, so each is embedded once."""

    def __init__(self, uid: str) -> None:
        self.uid = uid
        self.used: set[tuple[str, str]] = set()

    def run(self, s: str, *, face: str, size: float, x: float, y: float,
            ls: float, fill: str, middle: bool = False) -> str:
        """A run of outlined glyphs with its baseline at `y`, starting at `x`
        or centred on it."""
        if not s:
            return ""
        font = _faces()[face]
        sc = size / font["upem"]
        x0 = x - _bp_width(s, face, size, ls) / 2 if middle else x
        adv, uses = 0.0, []
        for ch in s:
            key = _glyph(font, ch)
            if key != " ":
                self.used.add((face, key))
                uses.append(f'<use href="#{_FACE_ID[face]}{ord(key)}-{self.uid}" '
                            f'x="{round(adv)}"/>')
            adv += font["g"][key][1] + ls / sc
        return (f'<g transform="translate({_f1(x0)} {_f1(y)}) '
                f'scale({_fx(sc, 5)} {_fx(-sc, 5)})" fill="{fill}">'
                + "".join(uses) + "</g>")

    def defs(self) -> str:
        return "".join(
            f'<path id="{_FACE_ID[face]}{ord(ch)}-{self.uid}" d="{_faces()[face]["g"][ch][0]}"/>'
            for face, ch in sorted(self.used, key=lambda k: (k[0], ord(k[1]))))


def _block(left: float, w: int, h: float, rx: float) -> str:
    """The value's block: square on the label side, the style's corner on the
    outer one, and the whole plate when there is no label."""
    if left <= 0:
        return (f'<rect width="{w}" height="{_fx(h)}"'
                + (f' rx="{_fx(rx)}"' if rx else "") + ' fill="{fill}"/>')
    if not rx:
        return f'<path d="M{_f1(left)} 0H{w}V{_fx(h)}H{_f1(left)}Z" fill="{{fill}}"/>'
    return (f'<path d="M{_f1(left)} 0H{_f1(w - rx)}a{_fx(rx)} {_fx(rx)} 0 0 1 {_fx(rx)} '
            f'{_fx(rx)}V{_f1(h - rx)}a{_fx(rx)} {_fx(rx)} 0 0 1 {_fx(-rx)} {_fx(rx)}'
            f'H{_f1(left)}Z" fill="{{fill}}"/>')


def _plate(label: str, message: str, icon: str | None, style: str,
           reserve: tuple[str, ...], col: dict, seed: str) -> str:
    """Draw one plate in the colours `col` names (palette tokens, or #RRGGBB
    from a repository's own theme):
    paper, wash (or None), grid and its opacity, block, ink (label and icon),
    letters (the value), frame and its opacity."""
    if style not in BLUEPRINT_STYLES:
        raise BadgeError(f"unknown blueprint style {style!r} - one of "
                         f"{', '.join(BLUEPRINT_STYLES)}")
    if icon is not None and icon != "" and icon not in ICONS:
        raise BadgeError(f"unknown icon {icon!r} - list the registry with --icons")
    g = BLUEPRINT_STYLES[style]
    aria = f"{label}: {message}" if label and message else (label or message)
    caps = (lambda s: s.upper()) if g["caps"] else (lambda s: s)
    text, vals = caps(label), [caps(v) for v in (message, *reserve)]
    for face, s in (("meta", text), *(("num", v) for v in vals)):
        gap = missing_glyphs(s, face)
        if gap:
            raise BadgeError(f"the blueprint lettering cannot draw {gap!r} in {s!r}")
    size, ls, pad, h, rx = g["size"], g["ls"], g["pad"], g["h"], g["rx"]
    has = bool(icon)
    iw = (g["icon"] + (g["gap"] if text else 0)) if has else 0.0
    left = (pad + iw + _bp_width(text, "meta", size, ls) + pad) if (text or has) else 0.0
    vw = (max(_bp_width(v, "num", size, ls) for v in vals) + 2 * pad) if any(vals) else 0.0
    w = round(left + vw)
    uid = hashlib.md5(seed.encode()).hexdigest()[:6]
    hx = lambda token: token.upper() if _HEX_COLOR.match(token) else PALETTE[token]
    corner = f' rx="{_fx(rx)}"' if rx else ""
    whole = f'width="{w}" height="{_fx(h)}"{corner}'

    lt = _Lettering(uid)
    defs = [f'<pattern id="p{uid}" width="10" height="10" patternUnits="userSpaceOnUse">'
            f'<path d="M10 .5H.5V10" fill="none" stroke="{hx(col["grid"])}" '
            f'stroke-opacity="{col["grid_op"]}"/></pattern>']
    body = [f'<rect {whole} fill="{hx(col["paper"])}"/>']
    if col["wash"]:
        # A print by day is never quite white: the faintest wash of its line.
        body.append(f'<rect {whole} fill="{hx(col["wash"])}" fill-opacity=".03"/>')
    body.append(f'<rect {whole} fill="url(#p{uid})"/>')
    if vw:
        body.append(_block(left, w, h, rx).replace("{fill}", hx(col["block"])))
    if g["sheen"]:
        stops = "".join(f'<stop offset="{o}" stop-color="{hx(t)}" stop-opacity="{a}"/>'
                        for o, t, a in BLUEPRINT_SHEENS[g["sheen"]])
        defs.append(f'<linearGradient id="g{uid}" x2="0" y2="1">{stops}</linearGradient>')
        body.append(f'<rect {whole} fill="url(#g{uid})"/>')
    # The label's cap height sits on the plate's centre line, and the value
    # shares its baseline, so the two read as one line of lettering.
    font = _faces()["meta"]
    base = h / 2 + font["cap"] * size / font["upem"] / 2
    if has:
        body.append(f'<g transform="translate({_f1(pad)} {_f1((h - g["icon"]) / 2)}) '
                    f'scale({_fx(g["icon"] / 24, 4)})" fill="none" stroke="{hx(col["ink"])}" '
                    f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
                    f'{ICONS[icon]}</g>')
    body.append(lt.run(text, face="meta", size=size, x=pad + iw, y=base, ls=ls,
                       fill=hx(col["ink"])))
    body.append(lt.run(vals[0], face="num", size=size, x=left + vw / 2, y=base, ls=ls,
                       fill=hx(col["letters"]), middle=True))
    body.append(f'<rect x=".5" y=".5" width="{w - 1}" height="{_fx(h - 1)}"'
                + (f' rx="{_fx(max(rx - .5, 0))}"' if rx else "")
                + f' fill="none" stroke="{hx(col["frame"])}" stroke-opacity="{col["frame_op"]}"/>')
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{_fx(h)}" '
        f'viewBox="0 0 {w} {_fx(h)}" role="img" aria-label="{escape(aria)}">'
        f'<!--{KIT} v{KIT_VERSION} badge-->'
        f'<title>{escape(aria)}</title><defs>{"".join(defs)}{lt.defs()}</defs>'
        + "".join(body) + "</svg>"
    )


def render_blueprint(label: str, message: str, icon: str | None = None,
                     style: str = DEFAULT_BLUEPRINT, tone: str = DEFAULT_PRINT,
                     dark: bool = False, reserve: tuple[str, ...] = ()) -> str:
    """A static plate: the label on the print's drafting paper, the value on a
    block of the print. `tone` is a key of PRINTS; `dark` draws the night
    file. `reserve` sizes the value block for the widest of these values too,
    so a value that changes keeps the plate the same width."""
    if tone not in PRINTS:
        raise BadgeError(f"unknown print {tone!r} - one of {', '.join(PRINTS)}; "
                         "a repository adds its own under prints in its settings")
    p = PRINTS[tone]
    night = p.get("night", "white")
    if dark:
        col = dict(paper=p["sheet"], wash=None, grid=night, grid_op=".085",
                   block=night, ink=night, letters=p["sheet"], frame=night, frame_op=".9")
    else:
        col = dict(paper="white", wash=p["line"], grid=p["line"], grid_op=".08",
                   block=p["line"], ink=p["ink"], letters="white", frame=p["line"],
                   frame_op=".9")
    seed = f"{label}|{message}|{icon}|{style}|{tone}|{dark}|{'|'.join(reserve)}"
    return _plate(label, message, icon, style, tuple(reserve), col, seed)


def _state(token: str) -> str:
    """The health token a message colour names, whether written as the token
    or as its hex, so a live plate and validate() agree on what is legal."""
    want = PALETTE.get(token, token).upper()
    for tok in sorted(HEALTH_COLORS | HEALTH_NEUTRAL):
        if PALETTE[tok].upper() == want:
            return tok
    raise BadgeError(f"a live plate's state must be one of "
                     f"{', '.join(sorted(HEALTH_COLORS | HEALTH_NEUTRAL))}, not {token!r}")


def render_live(label: str, message: str, icon: str | None = None,
                style: str = DEFAULT_BLUEPRINT, state: str = "green",
                reserve: tuple[str, ...] = ()) -> str:
    """A live plate: the label on a gold sheet, the value on a block of the
    state's print. One file serves both themes."""
    p = PRINTS[STATE_PRINT[_state(state)]]
    col = dict(paper="gold", wash=None, grid="black", grid_op=".12", block=p["line"],
               ink="black", letters=p.get("night", "white"), frame="black", frame_op=".35")
    seed = f"{label}|{message}|{icon}|{style}|live|{_state(state)}|{'|'.join(reserve)}"
    return _plate(label, message, icon, style, tuple(reserve), col, seed)

