# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""A trophy case on a print's page: every card a drawing on the print's drafting paper.

In a print the case keeps its style, its sizes and its words, and changes its
material. What the standard theme strikes in metal and enamel, a print draws,
the way a draughtsman draws a part: each card is a small sheet from the set,
its trophy in elevation over a title block, on the same paper the page's
banners are drawn on, with its grid, its border and its zone marks.

  a tier      how far the drawing has got. Unranked is a phantom, dashed where
              the trophy will stand; bronze is drawn in outline, silver gains
              line shading on the side the lamp does not reach, gold its
              section lining, a solid enamel and a glint, platinum its
              ornament, and diamond the rays and the double lining of a
              finished sheet
  progress    a bar along the title block, lined as far as the next tier
  the light   the kit's one lamp, up and to the left: heavier lines, line
              shading and section lining where its shadow falls

The words are lettered as the print's banners letter theirs, in Barlow
Condensed: the ink by day and the night's line by night, quieter words only as
faint as 4.5:1 allows. Every colour is the print's own, its line, its ink and
its paper, with white for a glint, at an opacity where a lighter shade is
wanted, so a card is held to the palette as the print's banners are, a
repository's own print included.

As a print's sheet is drawn in by its plotter, a card's linework draws itself
in as the page opens; a gold card's glint and a platinum card's sparkles move
too, and all of it holds still for a reader who asks for reduced motion.
"""
from __future__ import annotations

import math
from html import escape

from .. import KIT, KIT_VERSION
from ..canvas import DARK, DAY, Canvas, c, prose
from ..drafting import sheet
from ..lettering import cap_height, f1, fx, width
from ..palette import contrast, hexof, letters_on
from ..prints import colours
from .art import (CARD_H, CARD_K, CARD_W, PIN_H, PIN_W, alt_text, case_title, fmt, hex_pts, hexagon, level_label,
                  level_stats, level_xp, next_up_items, next_up_label, pct_label, pin_caption, pin_label, star4,
                  star5, status_text, top_pct)
from .catalogue import ICONS, TIER_NAMES, Core, ach_state, measure

B = 8            # a card's border, as wide as its zone marks need
TB = 170         # the row a card's title block starts at: its drawing above, its words below

# The motion every card shares, all of it in CSS so a reader's reduced motion holds it still: the linework
# drawn in once as the page opens, a glint across a gold card, a platinum card's sparkles, and the burst of a
# tier newly reached. A path that is drawn in is measured as one (pathLength="1"), so if nothing runs it is
# simply complete.
DRAW = ("@keyframes pl{from{stroke-dashoffset:1}}"
        ".pl{stroke-dasharray:1;animation:pl 1.6s cubic-bezier(.3,0,.2,1) .15s both}")
SHINE = ("@keyframes sh{0%{transform:translateX(-110px)}38%,100%{transform:translateX(200px)}}"
         ".sh{animation:sh 6.5s ease-in-out infinite}")
TWINKLE = ("@keyframes tw{0%,100%{opacity:.15;transform:scale(.45)}50%{opacity:1;transform:scale(1)}}"
           ".sp{transform-box:fill-box;transform-origin:center;animation:tw 3.4s ease-in-out infinite}")
BURST = ("@keyframes bu{0%{opacity:0;transform:scale(.4)}22%{opacity:.95}100%{opacity:0;transform:scale(1.3)}}"
         ".bu{transform-box:fill-box;transform-origin:center;animation:bu 1.9s ease-out .2s 1 both}")
CALM = "@media (prefers-reduced-motion:reduce){.pl,.sp{animation:none}.sh,.bu{display:none}}"

# Line shading on a turned part, as a technical illustration draws one: lines along its axis, closer together
# as its surface turns from the lamp. Each is a share of the way from the part's axis to its shaded edge.
TURNED = (.22, .4, .55, .67, .77, .85, .92)


def _rgb(colour: str) -> list[float]:
    h = hexof(colour)
    return [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]


def _lum(ch: list[float]) -> float:
    ch = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in ch]
    return .2126 * ch[0] + .7152 * ch[1] + .0722 * ch[2]


def legible(ink: str, paper: str, base: float, aim: float = 4.6) -> float:
    """The faintest opacity, from `base` up, at which `ink` over `paper` keeps a word to the kit's 4.5:1 (aiming a
    little over, for the paper's grain), as a print's quieter lettering is everywhere."""
    i, p = _rgb(ink), _rgb(paper)
    op = base
    while op < 1:
        mixed = [op * a + (1 - op) * b for a, b in zip(i, p)]
        hi, lo = sorted((_lum(mixed), _lum(p)), reverse=True)
        if (hi + .05) / (lo + .05) >= aim:
            break
        op = round(op + .01, 2)
    return min(op, 1.0)


def circle_d(cx, cy, r) -> str:
    """A circle as a path, so the plotter can draw it in."""
    return f"M{f1(cx - r)} {f1(cy)}a{f1(r)} {f1(r)} 0 1 0 {f1(2 * r)} 0a{f1(r)} {f1(r)} 0 1 0 {f1(-2 * r)} 0Z"


def ellipse_d(cx, cy, rx, ry) -> str:
    return f"M{f1(cx - rx)} {f1(cy)}a{f1(rx)} {f1(ry)} 0 1 0 {f1(2 * rx)} 0a{f1(rx)} {f1(ry)} 0 1 0 {f1(-2 * rx)} 0Z"


def poly_d(pts) -> str:
    return "M" + "L".join(f"{f1(x)} {f1(y)}" for x, y in pts) + "Z"


def rect_d(x, y, w, h) -> str:
    return f"M{f1(x)} {f1(y)}h{f1(w)}v{f1(h)}h{f1(-w)}Z"


class Drawing(Canvas):
    """One file of the case in a print: the kit's sheet canvas in the print's colours for one case, named the way
    every trophy is named, by its aria-label and its title, and declared at the size the standard card is."""

    def __init__(self, tone: str, case: str, w: float, h: float, label: str, t: int = 0, k: float = 1.0,
                 o: dict | None = None):
        super().__init__(w, h, title=label, desc=label, stamp=f"trophy {tone} {case}")
        self.k, self.t, self.o = k, t, o or {}
        th = DARK if case == "night" else DAY
        self.col = col = colours(tone, th)
        self.dark = th["dark"]
        self.line, self.ink, self.paper = c(col["line"]), c(col["ink"]), c(col["paper"])
        self.quiet = legible(col["ink"], col["paper"], .62)
        self.on_block = c(col["paper"] if contrast(col["paper"], col["line"]) >= 4.5 else letters_on(col["line"]))
        # The marks that carry a state, in the line where it holds 3:1 against the paper and in the ink where not.
        self.mark = self.line if contrast(col["line"], col["paper"]) >= 3 else self.ink
        self._hatch: dict = {}
        self.css.append(DRAW + (SHINE if t >= 3 else "") + (TWINKLE if t >= 4 else "")
                        + (BURST if self.o.get("new") and t else "") + CALM)

    def svg(self) -> str:
        label = prose(self.title)
        defs = "".join(self.defs) + self.L.defs()
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{round(self.w * self.k)}" '
                f'height="{round(self.h * self.k)}" viewBox="0 0 {round(self.w)} {round(self.h)}" role="img" '
                f'aria-label="{escape(label, quote=True)}"><!--{KIT} v{KIT_VERSION} {self.stamp}-->'
                f"<title>{escape(label)}</title>" + (f"<style>{''.join(self.css)}</style>" if self.css else "")
                + (f"<defs>{defs}</defs>" if defs else "") + "".join(self.body) + "</svg>\n")

    # -- materials
    def hatch(self, angle: float = 45, gap: float = 3, sw: float = .8, op: float = .8) -> str:
        """Section lining, the draughtsman's tone: lines at an angle in the print's line, each kind defined once."""
        key = (angle, gap, sw, op)
        if key not in self._hatch:
            pid = self.uid("h")
            self.defs.append(f'<pattern id="{pid}" width="{fx(gap)}" height="{fx(gap)}" patternUnits="userSpaceOnUse" '
                             f'patternTransform="rotate({fx(angle)})"><path d="M{fx(gap / 2)} 0V{fx(gap)}" '
                             f'stroke="{self.line}" stroke-width="{fx(sw)}" stroke-opacity="{fx(op)}"/></pattern>')
            self._hatch[key] = pid
        return f"url(#{self._hatch[key]})"

    def glint_band(self) -> str:
        """The band of light a glint sweeps across a part: white, fading out at both edges."""
        if "glint" not in self._hatch:
            gid = self.uid("g")
            w = c("white")
            self.defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{w}" '
                             f'stop-opacity="0"/><stop offset=".5" stop-color="{w}" stop-opacity=".75"/><stop offset="1" '
                             f'stop-color="{w}" stop-opacity="0"/></linearGradient>')
            self._hatch["glint"] = gid
        return f"url(#{self._hatch['glint']})"

    def clip(self, d: str) -> str:
        cid = self.uid("c")
        self.defs.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
        return cid

    def shade_side(self, cx: float, cy: float) -> str:
        """A clip of the half of the sheet the lamp does not reach, down and to the right of (cx, cy)."""
        ax, ay = .78 * 400, -.63 * 400      # along the boundary, which stands across the lamp's light
        sx, sy = .63 * 400, .78 * 400       # away from the lamp
        pts = [(cx + ax, cy + ay), (cx - ax, cy - ay), (cx - ax + sx, cy - ay + sy), (cx + ax + sx, cy + ay + sy)]
        return self.clip(poly_d(pts))

    # -- linework
    def edge(self, d: str, *, sw: float = 1.3, op: float | None = None, fill: str = "none", dash: str = "",
             plot: bool = True, extra: str = "") -> str:
        """An object line, a part's visible edge: drawn in as the page opens, unless it is a phantom."""
        o = f' stroke-opacity="{fx(op)}"' if op is not None else ""
        da = f' stroke-dasharray="{dash}"' if dash else ""
        pl = ' class="pl" pathLength="1"' if plot and not dash else ""
        return (f'<path d="{d}" fill="{fill}" stroke="{self.line}" stroke-width="{fx(sw)}"{o}{da} '
                f'stroke-linejoin="round" stroke-linecap="round"{pl}{extra}/>')

    def phantom(self, d: str, sw: float = 1.1) -> str:
        """A phantom line, long dash and two short: where a part will stand that is not there yet."""
        return self.edge(d, sw=sw, op=.62, dash="7 2 1.5 2 1.5 2", plot=False)

    def chain(self, x0, y0, x1, y1) -> str:
        """A centre line, the long dash and short dash a drawing marks an axis with."""
        return (f'<path d="M{f1(x0)} {f1(y0)}L{f1(x1)} {f1(y1)}" fill="none" stroke="{self.line}" stroke-width=".6" '
                f'stroke-opacity=".55" stroke-dasharray="9 2 2 2"/>')

    def heavy(self, d: str, cx: float, cy: float, sw: float = 2.2) -> str:
        """The same edge drawn heavier where the lamp does not reach: a drawing's light, in line weight."""
        return f'<g clip-path="url(#{self.shade_side(cx, cy)})">' + self.edge(d, sw=sw, plot=False) + "</g>"

    def icon(self, name: str, x: float, y: float, size: float, *, sw: float = 2.0, stroke: str | None = None,
             op: float | None = None, dash: str = "") -> str:
        """One of the case's icons, stroked, its 24 by 24 box's top-left at (x, y)."""
        extra = (f' stroke-opacity="{fx(op)}"' if op is not None else "") + (f' stroke-dasharray="{dash}"' if dash else "")
        return (f'<g transform="translate({f1(x)} {f1(y)}) scale({fx(size / 24, 4)})" fill="none" '
                f'stroke="{stroke or self.line}" stroke-width="{fx(sw)}" stroke-linecap="round" '
                f'stroke-linejoin="round"{extra}>{ICONS[name]}</g>')

    def say(self, s: str, x: float, y: float, size: float, *, face: str = "num", anchor: str = "start",
            ls: float = 0.0, quiet: bool = False, fill: str | None = None) -> str:
        return self.L.text(s, face=face, size=size, x=x, y=y, anchor=anchor, ls=ls, fill=fill or self.ink,
                           opacity=self.quiet if quiet else None)

    def sparkles(self, spots) -> str:
        """Four-pointed sparkles in the line, each twinkling on its own beat."""
        return "".join(f'<g transform="translate({f1(x)} {f1(y)})"><path class="sp" style="animation-delay:{d}s" '
                       f'd="{star4(s)}" fill="{self.line}"/></g>' for x, y, s, d in spots)

    def glint(self, clip: str, x: float, y: float, w: float, h: float, op: float = .7) -> str:
        """A glint sweeping across a part, clipped to it."""
        return (f'<g clip-path="url(#{clip})"><g transform="skewX(-18)"><rect class="sh" x="{f1(x)}" y="{f1(y)}" '
                f'width="{f1(w)}" height="{f1(h)}" fill="{self.glint_band()}" opacity="{fx(op)}"/></g></g>')

    def burst(self, cx: float, cy: float) -> str:
        """Rays that burst once from a tier newly reached."""
        if not self.o.get("new") or not self.t:
            return ""
        rays = "".join(f'M{f1(cx + 26 * math.cos(math.radians(i * 22.5)))} {f1(cy + 26 * math.sin(math.radians(i * 22.5)))}'
                       f'L{f1(cx + (58 if i % 2 else 72) * math.cos(math.radians(i * 22.5)))} '
                       f'{f1(cy + (58 if i % 2 else 72) * math.sin(math.radians(i * 22.5)))}' for i in range(16))
        return f'<path class="bu" d="{rays}" stroke="{self.line}" stroke-width="1.4" stroke-linecap="round"/>'

    def rays(self, cx: float, cy: float, r0: float, r1: float, n: int = 24) -> str:
        """Construction lines struck out from a centre: the finished sheet's sunburst behind a diamond part."""
        d = "".join(f"M{f1(cx + r0 * math.cos(2 * math.pi * i / n))} {f1(cy + r0 * math.sin(2 * math.pi * i / n))}"
                    f"L{f1(cx + r1 * math.cos(2 * math.pi * i / n))} {f1(cy + r1 * math.sin(2 * math.pi * i / n))}"
                    for i in range(n))
        return f'<path d="{d}" stroke="{self.line}" stroke-width=".55" stroke-opacity=".45"/>'


# --- the card: a sheet, its drawing and its title block ------------------------------------------------------------
def _card(tone: str, case: str, core: Core, m: dict, o: dict) -> Drawing:
    """A card's sheet, its title block ruled off on plain paper below the drawing."""
    cv = Drawing(tone, case, CARD_W, CARD_H, alt_text(core, m, o), m["t"], CARD_K, o)
    sheet(cv, cv.col, W=CARD_W, H=CARD_H, border=B, zones=3, rx=12,
          plain=((B, TB, CARD_W - 2 * B, CARD_H - B - TB),))
    cv.add(f'<path d="M{B} {TB}H{CARD_W - B}" stroke="{cv.line}" stroke-opacity=".85" stroke-width="1.2"/>')
    return cv


def _corners(cv: Drawing, core: Core, m: dict) -> None:
    """A card's rank, in a cell at the top left, and the ribbon of a tier newly reached across the top right."""
    o, W = cv.o, CARD_W
    if o.get("rank") and m["t"]:
        lab = pct_label(top_pct(core, m["v"]))
        w = width(lab, "num", 8, .7) + 10
        cv.add(f'<rect x="13" y="13" width="{f1(w)}" height="14" fill="{cv.paper}" stroke="{cv.line}" '
               f'stroke-opacity=".85" stroke-width=".9"/>' + cv.say(lab, 18, 23, 8, ls=.7))
    if o.get("new") and m["t"]:
        pts = [(W - 58, 0), (W - 38, 0), (W, 38), (W, 58)]
        clip = cv.clip(f"M12 0H{W - 12}a12 12 0 0 1 12 12V{CARD_H - 12}a12 12 0 0 1 -12 12H12a12 12 0 0 1 -12 -12V12"
                       "a12 12 0 0 1 12 -12Z")
        cv.add(f'<g clip-path="url(#{clip})"><path d="{poly_d(pts)}" fill="{cv.line}"/></g>'
               f'<g transform="rotate(45 {W - 24} 24)">' + cv.say("NEW", W - 24, 27, 8.5, anchor="middle", ls=1.6,
                                                                   fill=cv.on_block) + "</g>")


def _bar(cv: Drawing, x: float, y: float, w: float, m: dict) -> str:
    """Progress to the next tier: the bar's outline, lined as far as it has got, and a tick where it stands."""
    out = f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(w)}" height="5" fill="none" stroke="{cv.line}" stroke-opacity=".7" stroke-width=".8"/>'
    fw = w * m["pct"] if m["next"] else w
    if fw > 0:
        fill = cv.line if m["t"] == 5 else cv.hatch(45, 2.2, .9, .95)
        out += f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(max(2, fw))}" height="5" fill="{fill}"/>'
        if m["next"]:
            out += f'<path d="M{f1(x + fw)} {f1(y - 2.5)}V{f1(y + 7.5)}" stroke="{cv.mark}" stroke-width="1.2"/>'
    return out


def _segments(cv: Drawing, x: float, y: float, w: float, m: dict, h: float = 5, gap: float = 3) -> str:
    """The five tiers as five cells: lined once reached, lined as far as it has got in the next, and solid in
    diamond's."""
    sw = (w - gap * 4) / 5
    out = ""
    for i in range(5):
        X = x + i * (sw + gap)
        out += (f'<rect x="{f1(X)}" y="{f1(y)}" width="{f1(sw)}" height="{f1(h)}" fill="none" stroke="{cv.line}" '
                f'stroke-opacity=".7" stroke-width=".8"/>')
        f = 1 if m["t"] > i else (m["pct"] if m["t"] == i else 0)
        if f > 0:
            fill = cv.line if i == 4 else cv.hatch(45, 2.2, .9, .95)
            out += f'<rect x="{f1(X)}" y="{f1(y)}" width="{f1(max(1.5, sw * f))}" height="{f1(h)}" fill="{fill}"/>'
    return out


def _value(cv: Drawing, core: Core, m: dict, cx: float, y: float, size: float) -> str:
    """The value, its unit, and how far it moved this week."""
    vs = fmt(m["v"])
    vw = width(vs, "num", size)
    uw = width(core.unit, "meta", size * .42) + 3 if core.unit else 0
    x0 = cx - (vw + uw) / 2
    out = cv.say(vs, x0, y, size)
    if core.unit:
        out += cv.say(core.unit, x0 + vw + 3, y, size * .42, face="meta", quiet=True)
    delta = cv.o.get("delta")
    if delta:
        dx, dy = x0 + vw + uw + 5, y - size * .44
        out += (f'<path d="M{f1(dx)} {f1(dy)}h6l-3 -5Z" fill="{cv.mark}"/>'
                + cv.say(fmt(delta), dx + 8, dy, 10, face="meta"))
    return out


def _status(cv: Drawing, m: dict, cx: float, y: float, with_tier: bool = True) -> str:
    """The tier, its stars, and how far it is to the next: centred along the title block's foot."""
    parts = []
    if with_tier:
        parts.append(("t", TIER_NAMES[m["t"]].upper(), 8.5, 1.4))
        if m["stars"]:
            parts.append(("s", m["stars"], 0, 0))
        parts.append(("q", "·", 9, 0))
    parts.append(("q", status_text(m), 9, .5))
    widths = [p[1] * 8.4 if p[0] == "s" else width(p[1], "num", p[2], p[3]) for p in parts]
    x = cx - (sum(widths) + 4 * (len(parts) - 1)) / 2
    out = ""
    for p, w in zip(parts, widths):
        if p[0] == "s":
            out += "".join(f'<polygon points="{star5(x + 4 + k * 8.4, y - 3.2, 3.8)}" fill="{cv.mark}"/>'
                           for k in range(p[1]))
        else:
            out += cv.say(p[1], x, y, p[2], ls=p[3], quiet=p[0] == "q")
        x += w + 4
    return out


def _footer(cv: Drawing, core: Core, m: dict, kind: str) -> None:
    """The title block: the trophy's name, its value, its progress, and its tier."""
    big = kind == "none"
    cv.add(cv.say(core.title.upper(), CARD_W / 2, TB + (16 if big else 14), 9.5, anchor="middle", ls=2.2))
    cv.add(_value(cv, core, m, CARD_W / 2, TB + (42 if big else 38), 26 if big else 24))
    if kind == "bar":
        cv.add(_bar(cv, 26, TB + 44, CARD_W - 52, m))
    if kind == "seg":
        cv.add(_segments(cv, 26, TB + 44, CARD_W - 52, m))
    cv.add(_status(cv, m, CARD_W / 2, CARD_H - B - 7, kind != "seg"))


def _ground(cv: Drawing, x0: float, x1: float, y: float) -> str:
    """The line a part stands on, and its shadow cast down and to the right in section lining."""
    return (f'<path d="M{f1(x0 + 12)} {f1(y)}H{f1(x1 + 8)}l-6 5H{f1(x0 + 18)}Z" fill="{cv.hatch(45, 2.4, .7, .7)}"/>'
            f'<path d="M{f1(x0 - 6)} {f1(y)}H{f1(x1 + 12)}" stroke="{cv.line}" stroke-opacity=".7" stroke-width=".8"/>')


# --- the trophy, a cup -------------------------------------------------------------------------------------------
BOWL = "M56 36H124C124 70 111 89 98 94C96 95 95 97 95 100V106H85V100C85 97 84 95 82 94C69 89 56 70 56 36Z"
FOOT = "M80 106H100C100 111 106 114 114 116V121H66V116C74 114 80 111 80 106Z"
HANDS = "M62 44C38 42 36 76 70 84M118 44C142 42 144 76 110 84"


def trophy(tone: str, case: str, core: Core, value: int, o: dict | None = None) -> str:
    o = o or {}
    m = measure(core, value)
    t = m["t"]
    cv = _card(tone, case, core, m, o)
    body = BOWL + FOOT
    if t >= 5:
        cv.add(cv.rays(90, 66, 52, 76, 28))
    cv.add(cv.burst(90, 64) + cv.chain(90, 18, 90, 156))
    plinth = rect_d(62, 121, 56, 7) + rect_d(52, 128, 76, 16)
    if t == 0:
        cv.add(cv.phantom(HANDS, 1.2) + cv.phantom(BOWL) + cv.phantom(FOOT) + cv.phantom(ellipse_d(90, 36, 34, 5.5))
               + cv.phantom(circle_d(90, 60, 15.5)) + cv.phantom(plinth)
               + cv.icon(core.icon, 78.6, 48.6, 22.8, sw=2.2, op=.55))
    else:
        cup = cv.clip(body)
        # The handles as tubes: a heavy stroke in the line, and the paper down its middle.
        cv.add(f'<path d="{HANDS}" fill="none" stroke="{cv.line}" stroke-width="6.6" stroke-linecap="round"/>'
               f'<path d="{HANDS}" fill="none" stroke="{cv.paper}" stroke-width="4" stroke-linecap="round"/>')
        cv.add(f'<path d="{body}" fill="{cv.paper}"/>')
        if t >= 2:   # line shading down the side the lamp does not reach
            d = "".join(f"M{f1(90 + 34 * k)} 30V122" for k in TURNED)
            cv.add(f'<g clip-path="url(#{cup})"><path d="{d}" stroke="{cv.line}" stroke-width=".75" stroke-opacity=".8"/></g>')
        if t >= 3:   # section lining over the shaded half, and its double lining once the trophy is diamond
            fill = cv.hatch(45, 3, .7, .75)
            cv.add(f'<g clip-path="url(#{cup})"><rect x="96" y="30" width="40" height="95" fill="{fill}"/>'
                   + (f'<rect x="96" y="30" width="40" height="95" fill="{cv.hatch(-45, 3, .6, .6)}"/>' if t >= 5 else "")
                   + "</g>")
        cv.add(cv.heavy(body, 90, 66) + cv.edge(BOWL, fill="none") + cv.edge(FOOT, fill="none"))
        cv.add(f'<path d="{ellipse_d(90, 36, 34, 5.5)}" fill="{cv.paper}"/>'
               f'<path d="{ellipse_d(90, 36.6, 30, 4)}" fill="{cv.hatch(45, 2.2, .7, .8)}"/>'
               + cv.edge(ellipse_d(90, 36, 34, 5.5), sw=1.2))
        # The enamel: a disc on the bowl, solid from gold, its icon cut through it.
        solid = t >= 3
        cv.add(cv.edge(circle_d(90, 60, 17.5), sw=1.2, fill=cv.paper)
               + f'<path d="{circle_d(90, 60, 14.6)}" fill="{cv.line if solid else "none"}" stroke="{cv.line}" stroke-width=".8"/>'
               + cv.icon(core.icon, 78.6, 48.6, 22.8, sw=2.2, stroke=cv.on_block if solid else cv.line))
        if t >= 3:
            cv.add(cv.glint(cup, 30, 20, 18, 110))
    cv.add(cv.edge(plinth, sw=1.1, fill="none") if t else "")
    if t:
        cv.add(f'<path d="{rect_d(54, 130, 72, 12)}" fill="{cv.hatch(0, 2.4, .6, .5)}"/>'
               + f'<rect x="72" y="131.5" width="36" height="9" fill="{cv.paper}" stroke="{cv.line}" stroke-width=".8"/>')
    cv.add(_ground(cv, 52, 128, 144))
    if t >= 4:
        cv.add(cv.sparkles([(44, 34, 4.5, 0), (138, 26, 3.2, 1.2), (134, 100, 2.6, .6), (46, 104, 2.2, 1.9)]
                           + ([(148, 64, 2.6, 2.4), (32, 66, 3, .9)] if t == 5 else [])))
    for i in range(5):   # the five tiers, reached, next and still to come
        x, got, nxt = 90 + (i - 2) * 13, t >= i + 1, t == i
        if got:
            fill = f'fill="{cv.line}"'
        elif nxt:
            fill = f'fill="none" stroke="{cv.mark}" stroke-width="1" stroke-dasharray="2 1.2"'
        else:
            fill = f'fill="none" stroke="{cv.line}" stroke-opacity=".5" stroke-width=".8"'
        cv.add(f'<rect x="-3" y="-3" width="6" height="6" transform="translate({x} 159) rotate(45)" {fill}/>')
    _corners(cv, core, m)
    _footer(cv, core, m, "bar")
    return cv.svg()


# --- the crest, a hexagon on a banner --------------------------------------------------------------------------------
WING = "M46 76C32 66 20 60 8 57C13 69 24 80 42 90ZM43 92C28 88 15 86 4 88C11 97 24 104 42 105ZM45 108C33 110 22 113 12 119C21 124 33 125 47 120Z"
VEINS = "M40 84C30 76 20 70 12 64M38 99C28 96 17 94 9 93M42 114C32 115 23 117 17 120"
CROWN = "M73 36L77 21L84 29L90 16L96 29L103 21L107 36Z"


def crest(tone: str, case: str, core: Core, value: int, o: dict | None = None) -> str:
    o = o or {}
    m = measure(core, value)
    t, cx, cy = m["t"], 90, 96
    cv = _card(tone, case, core, m, o)
    outer, ring, inner = poly_d(hex_pts(cx, cy, 51)), poly_d(hex_pts(cx, cy, 46.5)), poly_d(hex_pts(cx, cy, 42))
    if t >= 5:
        cv.add(cv.rays(cx, cy, 56, 80, 30))
    cv.add(cv.burst(cx, cy) + cv.chain(cx, 12, cx, 160))
    if t == 0:
        cv.add(cv.phantom(outer) + cv.phantom(inner, .9) + cv.icon(core.icon, cx - 17.4, cy - 17.4, 34.8, sw=1.7, op=.55)
               + cv.phantom(rect_d(40, 136, 100, 16)) + cv.say("UNRANKED", cx, 147.3, 8.5, anchor="middle", ls=2.2,
                                                                quiet=True))
    else:
        if t >= 4:
            wings = f'<path d="{WING}"/><path d="{WING}" transform="translate(180 0) scale(-1 1)"/>'
            veins = f'<path d="{VEINS}"/><path d="{VEINS}" transform="translate(180 0) scale(-1 1)"/>'
            cv.add(f'<g fill="{cv.paper}" stroke="{cv.line}" stroke-width="1" stroke-linejoin="round">{wings}</g>'
                   f'<g fill="{cv.hatch(45, 2.6, .6, .6)}">{wings}</g>'
                   f'<g fill="none" stroke="{cv.line}" stroke-opacity=".6" stroke-width=".6">{veins}</g>')
        # The frame, its two rings, and the field: the outer ring lined from silver, the field kept to the paper.
        cv.add(cv.edge(outer, sw=1.4, fill=cv.paper))
        if t >= 2:
            cv.add(f'<path d="{outer}{ring}" fill-rule="evenodd" fill="{cv.hatch(45, 2.4, .7, .85)}"/>')
        cv.add(cv.edge(ring, sw=.8) + cv.edge(inner, sw=1.2))
        guides = poly_d(hex_pts(cx, cy, 34)) + poly_d(hex_pts(cx, cy, 26))
        cv.add(f'<path d="{guides}" fill="none" stroke="{cv.line}" stroke-opacity=".3" stroke-width=".6"/>')
        field = cv.clip(inner)
        if t >= 3:
            cv.add(f'<g clip-path="url(#{field})"><path d="M90 46L140 96L90 146Z" fill="{cv.hatch(45, 3, .6, .55)}"/></g>')
        cv.add(cv.heavy(outer, cx, cy, 2.4) + cv.icon(core.icon, cx - 17.4, cy - 17.4, 34.8, sw=1.7))
        if t >= 3:
            cv.add(cv.glint(field, 40, 40, 16, 120))
        if t >= 2:   # rivets at the corners
            pts = [p for i, p in enumerate(hex_pts(cx, cy, 49)) if i != 3 and not (t >= 3 and i == 0)]
            cv.add("".join(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="1.8" fill="{cv.paper}" stroke="{cv.line}" '
                           f'stroke-width=".8"/>' for x, y in pts))
        if t >= 5:
            cv.add(cv.edge(CROWN, sw=1, fill=cv.paper) + f'<path d="{CROWN}" fill="{cv.hatch(-45, 2.2, .6, .7)}"/>'
                   + "".join(f'<circle cx="{x}" cy="{y}" r="1.9" fill="{cv.paper}" stroke="{cv.line}" stroke-width=".8"/>'
                             for x, y in ((77, 21), (90, 16), (103, 21))))
        if t >= 3:   # the gem at the top
            cv.add(cv.edge("M90 34L99 45L90 58L81 45Z", sw=1, fill=cv.paper)
                   + f'<path d="M90 37.5L96.5 45L90 54.5Z" fill="{cv.line}" fill-opacity=".85"/>'
                   + f'<path d="M83.5 45H96.5M90 37.5V54.5" stroke="{cv.line}" stroke-width=".6"/>')
        # The banner: a scroll, its ends turned behind it in shadow, the tier lettered across it.
        ends = "M28 140H50V156H28L34 148ZM152 140H130V156H152L146 148Z"
        cv.add(cv.edge(ends, sw=1, fill=cv.paper) + f'<path d="{ends}" fill="{cv.hatch(45, 2.2, .7, .8)}"/>'
               + cv.edge(rect_d(40, 136, 100, 16), sw=1.2, fill=cv.paper))
        name = TIER_NAMES[t].upper()
        if m["stars"]:
            lw, sw = width(name, "num", 8.5, 2.2), m["stars"] * 8.4
            x0 = cx - (lw + 5 + sw) / 2
            cv.add(cv.say(name, x0, 147.3, 8.5, ls=2.2)
                   + "".join(f'<polygon points="{star5(x0 + lw + 5 + 4 + k * 8.4, 144, 3.6)}" fill="{cv.ink}"/>'
                             for k in range(m["stars"])))
        else:
            cv.add(cv.say(name, cx, 147.3, 8.5, anchor="middle", ls=2.2))
    if t >= 4:
        cv.add(cv.sparkles([(26, 42, 4, 0), (154, 48, 3, 1.2), (152, 128, 2.6, .7), (26, 130, 2.2, 1.9)]
                           + ([(120, 18, 2.6, 2.4), (60, 16, 3, 1)] if t == 5 else [])))
    _corners(cv, core, m)
    _footer(cv, core, m, "seg")
    return cv.svg()


# --- the medallion, on its ribbon -----------------------------------------------------------------------------------
def medallion(tone: str, case: str, core: Core, value: int, o: dict | None = None) -> str:
    o = o or {}
    m = measure(core, value)
    t, cx, cy = m["t"], 90, 106
    cv = _card(tone, case, core, m, o)
    left, right = [(56, 10), (82, 10), (102, 66), (76, 66)], [(98, 10), (124, 10), (104, 66), (78, 66)]
    if t >= 5:
        cv.add(cv.rays(cx, cy, 58, 80, 32))
    cv.add(cv.burst(cx, cy))
    # The ribbon's two straps, each with its stripe down the middle, the far one in shadow.
    for pts, shade in ((left, True), (right, False)):
        (ax, ay), (bx, by), (qx, qy), (px, py) = pts
        mid = [(ax + (bx - ax) * .36, ay), (ax + (bx - ax) * .64, ay), (px + (qx - px) * .64, py),
               (px + (qx - px) * .36, py)]
        cv.add(cv.edge(poly_d(pts), sw=1, fill=cv.paper, op=1 if t else .6, dash="" if t else "4 2"))
        if t:
            cv.add(f'<path d="{poly_d(mid)}" fill="{cv.hatch(-60 if shade else 60, 2.2, .7, .8)}"/>'
                   + f'<path d="M{f1(ax + (bx - ax) * .12)} {ay}L{f1(px + (qx - px) * .12)} {py}'
                     f'M{f1(ax + (bx - ax) * .88)} {ay}L{f1(px + (qx - px) * .88)} {py}" stroke="{cv.line}" '
                     f'stroke-width=".6" stroke-opacity=".7"/>')
    # The progress ring round the medal, a dial of ticks, and an arc as far as the next tier.
    R = 52
    C = 2 * math.pi * R
    ticks = "".join(f"M{f1(cx + (R + 3) * math.cos(a))} {f1(cy + (R + 3) * math.sin(a))}"
                    f"L{f1(cx + (R + 5.5) * math.cos(a))} {f1(cy + (R + 5.5) * math.sin(a))}"
                    for a in (math.radians(-90 + 30 * i) for i in range(12)))
    cv.add(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{cv.line}" stroke-opacity=".45" stroke-width=".8"/>'
           f'<path d="{ticks}" stroke="{cv.line}" stroke-opacity=".6" stroke-width=".8"/>')
    p = m["pct"] if m["next"] else 1.0
    if p > 0:
        cv.add(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{cv.mark}" stroke-width="3" '
               f'stroke-dasharray="{f1(C * p)} {f1(C)}" transform="rotate(-90 {cx} {cy})"/>')
        if p < 1:
            a = math.radians(-90 + 360 * p)
            cv.add(f'<circle cx="{f1(cx + R * math.cos(a))}" cy="{f1(cy + R * math.sin(a))}" r="2.6" fill="{cv.paper}" '
                   f'stroke="{cv.mark}" stroke-width="1.2"/>')
    if t == 0:
        cv.add(cv.phantom(circle_d(cx, cy, 44)) + cv.phantom(circle_d(cx, cy, 18), .8)
               + cv.icon(core.icon, cx - 12, cy - 12, 24, sw=2.1, op=.55))
    else:
        disc = circle_d(cx, cy, 44)
        cv.add(cv.edge(disc, sw=1.4, fill=cv.paper)
               + f'<circle cx="{cx}" cy="{cy}" r="42.4" fill="none" stroke="{cv.line}" stroke-width="1.6" '
                 f'stroke-dasharray=".9 1.5"/>'
               + cv.edge(circle_d(cx, cy, 39.5), sw=.8) + cv.edge(circle_d(cx, cy, 36), sw=1))
        face = cv.clip(circle_d(cx, cy, 36))
        if t >= 2:
            cv.add(f'<g clip-path="url(#{face})"><path d="M{cx - 40} {cy + 6}L{cx + 40} {cy - 14}V{cy + 40}H{cx - 40}Z" '
                   f'fill="{cv.hatch(45, 3, .6, .55)}"/></g>')
        # The laurel: two sprigs of leaves round the face, each leaf drawn in outline with its rib.
        leaves = ""
        for side in (-1, 1):
            for i in range(6):
                ang = 104 + i * 21 if side < 0 else 76 - i * 21
                rad = math.radians(ang)
                for dr, tilt in ((2.6, 30), (-2.6, -30)):
                    r = 28.5 + dr
                    x, y = cx + r * math.cos(rad), cy + r * math.sin(rad)
                    rot = ang + 90 - tilt if side < 0 else ang - 90 + tilt
                    leaves += (f'<ellipse cx="{f1(x)}" cy="{f1(y)}" rx="4.4" ry="1.7" '
                               f'transform="rotate({f1(rot)} {f1(x)} {f1(y)})"/>')
        cv.add(f'<g fill="{cv.paper}" stroke="{cv.line}" stroke-width=".65">{leaves}</g>')
        solid = t >= 3
        cv.add(cv.edge(circle_d(cx, cy, 18.5), sw=1.1, fill=cv.paper)
               + f'<path d="{circle_d(cx, cy, 16)}" fill="{cv.line if solid else "none"}" stroke="{cv.line}" stroke-width=".8"/>'
               + cv.icon(core.icon, cx - 12, cy - 12, 24, sw=2, stroke=cv.on_block if solid else cv.line)
               + cv.heavy(disc, cx, cy, 2.4))
        if t >= 3:
            cv.add(cv.glint(face, 40, 60, 16, 100))
    if t >= 4:
        cv.add(cv.sparkles([(40, 60, 4, 0), (140, 70, 3, 1.3), (138, 150, 2.6, .7), (42, 150, 2.2, 2)]
                           + ([(150, 112, 2.6, 2.5), (28, 104, 3, 1)] if t == 5 else [])))
    _corners(cv, core, m)
    _footer(cv, core, m, "none")
    return cv.svg()


# --- the crystal, filling as it grows ---------------------------------------------------------------------------
PTS = {"T": (90, 22), "LS": (64, 58), "FL": (80, 51), "FR": (100, 51), "RS": (116, 58), "LB": (68, 118),
       "BL": (81, 124), "BR": (99, 124), "RB": (112, 118), "B": (90, 148)}
FACES = (("LS", "FL", "BL", "LB"), ("FL", "FR", "BR", "BL"), ("FR", "RS", "RB", "BR"), ("T", "LS", "FL"),
         ("T", "FL", "FR"), ("T", "FR", "RS"), ("LB", "BL", "B"), ("BL", "BR", "B"), ("BR", "RB", "B"))
# The facets the lamp does not reach, which take a second lining: the right and the underside.
SHADED = (("FR", "RS", "RB", "BR"), ("T", "FR", "RS"), ("LB", "BL", "B"), ("BL", "BR", "B"), ("BR", "RB", "B"))


def crystal(tone: str, case: str, core: Core, value: int, o: dict | None = None) -> str:
    o = o or {}
    m = measure(core, value)
    t = m["t"]
    cv = _card(tone, case, core, m, o)

    def pts(keys):
        return [PTS[k] for k in keys]

    sil = poly_d(pts(("T", "RS", "RB", "B", "LB", "LS")))
    p = 1.0 if t == 5 else m["pct"]
    top, bottom = 22, 148
    level = bottom - p * (bottom - top)
    if t >= 5:
        cv.add(cv.rays(90, 86, 50, 78, 28))
    cv.add(cv.burst(90, 86) + cv.chain(90, 14, 90, 158))

    def shard(x, y, r):
        return (f'<g transform="translate({x} {y}) rotate({r})">'
                + cv.edge("M0 -6L4 3L-3 4Z", sw=.8, fill=cv.paper, plot=False, op=1 if t else .6)
                + (f'<path d="M0 -6L4 3L-3 4Z" fill="{cv.hatch(45, 1.8, .5, .7)}"/>' if t >= 2 else "") + "</g>")

    cv.add(shard(40, 44, -20) + shard(142, 50, 25) + shard(138, 128, 160) + shard(44, 118, 200))
    rings = [(-14, 46, 10), (18, 40, 8)] if t >= 5 else [(-14, 46, 10)] if t >= 4 else []
    # A ring's far half is hidden behind the crystal, so it is drawn as a hidden line, dashed, before it.
    for rot, rx, ry in rings:
        cv.add(f'<path d="M{90 - rx} 86A{rx} {ry} 0 0 1 {90 + rx} 86" transform="rotate({rot} 90 86)" fill="none" '
               f'stroke="{cv.line}" stroke-width=".8" stroke-opacity=".7" stroke-dasharray="3 2"/>')
    if t == 0:
        cv.add(cv.phantom(sil) + f'<path d="{"".join(poly_d(pts(k)) for k in FACES)}" fill="none" stroke="{cv.line}" '
               f'stroke-opacity=".3" stroke-width=".6" stroke-dasharray="3 2"/>'
               + cv.icon(core.icon, 79.2, 77.2, 21.6, sw=2.1, op=.55))
    else:
        clip = cv.clip(sil)
        cv.add(f'<path d="{sil}" fill="{cv.paper}"/>')
        if p > 0:   # the crystal fills with the trophy's progress, lined, its level marked as a drawing marks one
            cv.add(f'<g clip-path="url(#{clip})"><rect x="60" y="{f1(level)}" width="60" height="{f1(bottom - level)}" '
                   f'fill="{cv.hatch(45, 2.6 if t < 3 else 2.2, .7, .85)}"/></g>')
            if p < 1:
                lx = 118
                cv.add(f'<g clip-path="url(#{clip})"><path d="M60 {f1(level)}H120" stroke="{cv.mark}" stroke-width="1.2"/></g>'
                       f'<path d="M{lx + 2} {f1(level)}H{lx + 16}" stroke="{cv.line}" stroke-width=".7"/>'
                       f'<path d="M{lx + 6} {f1(level - 5)}h7l-3.5 5Z" fill="none" stroke="{cv.line}" stroke-width=".8"/>')
        cv.add(f'<g clip-path="url(#{clip})">' + "".join(f'<path d="{poly_d(pts(k))}" fill="{cv.hatch(-45, 3, .55, .45)}"/>'
                                                       for k in SHADED) + "</g>")
        cv.add(f'<path d="{"".join(poly_d(pts(k)) for k in FACES)}" fill="none" stroke="{cv.line}" stroke-width=".7" '
               f'stroke-linejoin="round"/>' + cv.edge(sil, sw=1.4) + cv.heavy(sil, 90, 86, 2.2))
        cv.add(f'<circle cx="90" cy="88" r="12.5" fill="{cv.paper}" stroke="{cv.line}" stroke-width=".8"/>'
               + cv.icon(core.icon, 79.2, 77.2, 21.6, sw=2.1))
        if t >= 3:
            cv.add(cv.glint(clip, 40, 10, 14, 150, .8))
    for rot, rx, ry in rings:   # and the near half in front of it, solid
        cv.add(f'<path d="M{90 - rx} 86A{rx} {ry} 0 0 0 {90 + rx} 86" transform="rotate({rot} 90 86)" fill="none" '
               f'stroke="{cv.line}" stroke-width="1.2"/>')
    cv.add(f'<path d="{ellipse_d(90, 160, 30, 3.5)}" fill="{cv.hatch(45, 2.2, .6, .65)}"/>')
    if t >= 4:
        cv.add(cv.sparkles([(52, 30, 4, 0), (132, 26, 3, 1.2), (146, 96, 2.6, .6), (34, 86, 2.4, 1.9)]
                           + ([(120, 146, 2.6, 2.4), (58, 146, 3, 1)] if t == 5 else [])))
    _corners(cv, core, m)
    _footer(cv, core, m, "none")
    return cv.svg()


# --- the plaque, a plate across the row -------------------------------------------------------------------------------
def plaque(tone: str, case: str, core: Core, value: int, o: dict | None = None) -> str:
    o = o or {}
    m = measure(core, value)
    t = m["t"]
    W, H = 264, 88
    cv = Drawing(tone, case, W, H, alt_text(core, m, o), t, 1.0, o)
    sheet(cv, cv.col, W=W, H=H, border=5, zones=6, rx=5, plain=((80, 5, W - 85, H - 10),))
    # The plate's left: a panel lined as the tier is reached, its trophy cut through it.
    panel = rect_d(5, 5, 75, H - 10)
    if t:
        cv.add(f'<path d="{panel}" fill="{cv.hatch(45, 3.2 if t < 3 else 2.4, .8, .8)}"/>'
               + (f'<path d="{panel}" fill="{cv.hatch(-45, 3.2, .6, .6)}"/>' if t >= 5 else "")
               + f'<path d="{circle_d(42.5, 44, 24)}" fill="{cv.line if t >= 3 else cv.paper}" stroke="{cv.line}" stroke-width="1.2"/>'
               + cv.icon("trophy", 25.7, 27.2, 33.6, sw=1.5, stroke=cv.on_block if t >= 3 else cv.line))
        if t >= 3:
            cv.add(cv.glint(cv.clip(panel), -10, 0, 16, 88))
    else:
        cv.add(cv.phantom(circle_d(42.5, 44, 24)) + cv.icon("trophy", 25.7, 27.2, 33.6, sw=1.5, op=.55, dash="2 2"))
    cv.add(f'<path d="M80 5V{H - 5}" stroke="{cv.line}" stroke-width="1.2"/>')
    if t >= 4:
        cv.add(cv.sparkles([(16, 16, 3, 0), (68, 74, 2.4, 1.1)]))
    if o.get("new") and t:
        cv.add(f'<path d="M5 5H31L5 31Z" fill="{cv.line}"/>')
    cv.add(f'<circle cx="102" cy="21" r="6.5" fill="none" stroke="{cv.line}" stroke-width="1"/>'
           + cv.icon(core.icon, 97.2, 16.2, 9.6, sw=2.6)
           + cv.say(core.title.upper(), 114, 24.3, 9, ls=1.8))
    right = TIER_NAMES[t].upper()
    rw = width(right, "num", 9, 1.8)
    cv.add(cv.say(right, 250, 24.3, 9, anchor="end", ls=1.8))
    for k in range(m["stars"]):
        cv.add(f'<polygon points="{star5(250 - rw - 8 - k * 8.4, 21, 3.6)}" fill="{cv.mark}"/>')
    vw = width(fmt(value), "num", 27)
    uw = (width(core.unit, "meta", 27 * .42) + 3) if core.unit else 0
    delta = o.get("delta")
    cv.add(_value(cv, core, m, 96 + vw / 2 + uw / 2, 56, 27))
    used = 96 + vw + uw + (13 + width(fmt(delta), "meta", 10) if delta else 0)
    sub = ("NEW  ·  " if o.get("new") and t else "") + status_text(m)
    if o.get("rank") and t and used + 8 + width(pct_label(top_pct(core, value)) + "  ·  " + sub, "num", 9, .5) <= 250:
        sub = pct_label(top_pct(core, value)) + "  ·  " + sub
    cv.add(cv.say(sub, 250, 55, 9, anchor="end", ls=.5, quiet=True) + _segments(cv, 96, 66, 154, m))
    return cv.svg()


STYLES = {"trophy": trophy, "crest": crest, "medallion": medallion, "crystal": crystal, "plaque": plaque}


# --- the achievement pin ---------------------------------------------------------------------------------------------
def pin(tone: str, case: str, a, cur) -> str:
    st = ach_state(a, cur)
    cx, cy = 52, 46
    earned, secret = st["earned"], st["secret"]
    t = st["rarity"] if earned else 0
    pct = 1.0 if st["done"] else st["pct"]
    nm = a.name + (f" {st['tier']}" if st["tier"] else "")
    cv = Drawing(tone, case, PIN_W, PIN_H, pin_label(a, cur), t)
    sheet(cv, cv.col, W=PIN_W, H=PIN_H, border=5, zones=2, rx=10, plain=((5, 86, PIN_W - 10, PIN_H - 91),))
    cv.add(f'<path d="M5 86H{PIN_W - 5}" stroke="{cv.line}" stroke-opacity=".8" stroke-width="1"/>')
    if t >= 5:
        cv.add(cv.rays(cx, cy, 36, 44, 20))
    if not secret and not st["done"]:   # how far along, as an arc round the pin
        R = 36
        C = 2 * math.pi * R
        cv.add(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{cv.line}" stroke-opacity=".45" stroke-width=".8"/>')
        if pct > 0:
            cv.add(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{cv.mark}" stroke-width="2.4" '
                   f'stroke-dasharray="{f1(C * min(1, pct))} {f1(C)}" transform="rotate(-90 {cx} {cy})"/>')
    if secret:
        cv.add(cv.phantom(circle_d(cx, cy, 31)) + cv.icon("q", cx - 15.6, cy - 15.6, 31.2, sw=2, op=.6))
    elif not earned:
        cv.add(cv.phantom(circle_d(cx, cy, 31)) + cv.phantom(circle_d(cx, cy, 25), .8)
               + cv.icon(a.icon, cx - 12.6, cy - 12.6, 25.2, sw=1.9, op=.6))
    else:
        disc = circle_d(cx, cy, 31)
        cv.add(cv.edge(disc, sw=1.3, fill=cv.paper))
        if t >= 2:
            cv.add(f'<circle cx="{cx}" cy="{cy}" r="29.6" fill="none" stroke="{cv.line}" stroke-width="1.4" '
                   f'stroke-dasharray=".9 1.4"/>')
        if t >= 3:
            cv.add(f'<path d="{disc}{circle_d(cx, cy, 25)}" fill-rule="evenodd" fill="{cv.hatch(45, 2.2, .7, .85)}"/>')
        solid = t >= 4
        cv.add(cv.edge(circle_d(cx, cy, 25), sw=1, fill=cv.line if solid else cv.paper)
               + cv.icon(a.icon, cx - 12.6, cy - 12.6, 25.2, sw=1.9, stroke=cv.on_block if solid else cv.line)
               + cv.heavy(disc, cx, cy, 2.2))
        if t >= 4:
            cv.add(cv.glint(cv.clip(circle_d(cx, cy, 25)), 20, 14, 10, 70, .55))
            cv.add(cv.sparkles([(16, 16, 3, 0), (88, 22, 2.4, 1.2), (88, 70, 2, .6)]))
    size = 9
    name = "???" if secret else nm
    while size > 7 and width(name, "num", size, .3) > PIN_W - 14:
        size -= .25
    cv.add(cv.say(name, cx, 101, size, anchor="middle", ls=.3, quiet=not earned))
    cv.add(cv.say(pin_caption(st), cx, 114, 8, anchor="middle", ls=.7, quiet=not earned))
    return cv.svg()


# --- the level card and the next-up card ---------------------------------------------------------------------------
def level_card(tone: str, case: str, cores: list, values: dict, ach: list, curs: dict, subject: str,
               foot: tuple) -> str:
    """`foot` is (icon, hue, main text, muted text): the streak line or the release line. A print draws its icon
    in its own line, so the hue is the standard look's alone."""
    W, H = 420, 152
    st = level_stats(cores, values, ach, curs)
    bt = st["bt"]
    cv = Drawing(tone, case, W, H, level_label(st, subject, foot), bt)
    sheet(cv, cv.col, W=W, H=H, border=8, zones=7, rx=12, plain=((156, 8, W - 164, H - 16),))
    cx, cy = 80, 76
    # The level's badge: a hexagon in section, its field solid and its number cut through it, the ring round it
    # drawn as far as the next level.
    Rr = 60
    C = 2 * math.pi * Rr
    cv.add(f'<circle cx="{cx}" cy="{cy}" r="{Rr}" fill="none" stroke="{cv.line}" stroke-opacity=".45" stroke-width=".8"/>'
           f'<circle cx="{cx}" cy="{cy}" r="{Rr}" fill="none" stroke="{cv.mark}" stroke-width="3" '
           f'stroke-dasharray="{f1(C * st["lp"])} {f1(C)}" transform="rotate(-90 {cx} {cy})"/>')
    outer, inner = poly_d(hex_pts(cx, cy, 48)), poly_d(hex_pts(cx, cy, 40))
    cv.add(cv.edge(outer, sw=1.4, fill=cv.paper)
           + f'<path d="{outer}{poly_d(hex_pts(cx, cy, 44))}" fill-rule="evenodd" fill="{cv.hatch(45, 2.4, .7, .85)}"/>'
           + cv.edge(poly_d(hex_pts(cx, cy, 44)), sw=.8) + f'<path d="{inner}" fill="{cv.line}"/>'
           + cv.heavy(outer, cx, cy, 2.4))
    if bt >= 3:
        cv.add(cv.glint(cv.clip(inner), 30, 20, 16, 120, .45))
    cv.add(cv.say("LEVEL", cx, cy - 14, 7.5, anchor="middle", ls=2.2, fill=cv.on_block)
           + cv.say(str(st["L"]), cx, cy + 18, 34, anchor="middle", fill=cv.on_block))
    cv.add(f'<path d="M156 8V{H - 8}" stroke="{cv.line}" stroke-opacity=".85" stroke-width="1.2"/>')
    x0, w = 172, 232
    ttl = case_title(subject)
    tsz, tls = 13, 2.0
    while width(ttl, "num", tsz, tls) > w and tsz > 8:
        tsz -= .5
        tls = max(.8, tls - .2)
    cv.add(cv.say(ttl, x0, 38, tsz, ls=tls)
           + cv.say(f"LEVEL {st['L']}  ·  {fmt(st['xp'])} XP  ·  {fmt(level_xp(st['L'] + 1) - st['xp'])} TO LEVEL "
                    f"{st['L'] + 1}", x0, 56, 9.5, ls=.5, quiet=True)
           + _track(cv, x0, 62, w, st["lp"], 45)
           + f'<path d="M164 78H{W - 16}" stroke="{cv.line}" stroke-opacity=".4" stroke-width=".7"/>'
           + cv.say(f"CASE {round(st['completion'] * 100)}% COMPLETE"
                    + (f"  ·  {st['earned']} OF {len(ach)} ACHIEVEMENTS" if ach else ""), x0, 93, 9.5, ls=.5, quiet=True)
           + _track(cv, x0, 99, w, st["completion"], -45)
           + f'<path d="M164 112H{W - 16}" stroke="{cv.line}" stroke-opacity=".4" stroke-width=".7"/>'
           + f'<circle cx="{x0 + 7}" cy="{126}" r="7.5" fill="{cv.line}"/>'
           + cv.icon(foot[0], x0 + 2, 121, 10.08, sw=2.6, stroke=cv.on_block)
           + cv.say(foot[2], x0 + 20, 130, 10.5, ls=.5)
           + cv.say(foot[3], x0 + 20 + width(foot[2], "num", 10.5, .5), 130, 9.5, ls=.5, quiet=True))
    if bt >= 4:
        cv.add(cv.sparkles([(30, 22, 3.5, 0), (134, 130, 2.6, 1.2)]))
    return cv.svg()


def _track(cv: Drawing, x: float, y: float, w: float, share: float, angle: float) -> str:
    """A long bar: its outline, lined as far as it has got."""
    return (f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(w)}" height="6" fill="none" stroke="{cv.line}" '
            f'stroke-opacity=".7" stroke-width=".8"/>'
            f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(max(3, w * share))}" height="6" fill="{cv.hatch(angle, 2.2, .9, .95)}"/>'
            f'<path d="M{f1(x + max(3, w * share))} {f1(y - 2)}V{f1(y + 8)}" stroke="{cv.mark}" stroke-width="1.2"/>')


def next_up_card(tone: str, case: str, cores: list, values: dict, ach: list, curs: dict) -> str:
    W, H = 328, 152
    items = next_up_items(cores, values, ach, curs)
    cv = Drawing(tone, case, W, H, next_up_label(items))
    sheet(cv, cv.col, W=W, H=H, border=8, zones=5, rx=12, plain=((8, 46, W - 16, H - 54),))
    # The title in a solid cell, as a sheet's title strip carries its name, and the rows ruled as a schedule.
    tw = width("NEXT UP", "num", 9.5, 2.2) + 22
    cv.add(f'<rect x="16" y="20" width="{f1(tw)}" height="18" fill="{cv.line}"/>'
           + cv.say("NEXT UP", 27, 32.4, 9.5, ls=2.2, fill=cv.on_block)
           + f'<path d="M8 46H{W - 8}" stroke="{cv.line}" stroke-opacity=".85" stroke-width="1.2"/>')
    for i, it in enumerate(items):
        y = 66 + i * 28
        cv.add(f'<circle cx="30" cy="{y - 4}" r="7.5" fill="none" stroke="{cv.line}" stroke-width="1"/>'
               + cv.icon(it["icon"], 25.4, y - 8.6, 9.1, sw=2.8)
               + cv.say(it["name"], 44, y, 10.5)
               + cv.say(f"{int(it['pct'] * 100)}%", 304, y, 10, anchor="end", quiet=True)
               + f'<rect x="44" y="{y + 5}" width="260" height="3.5" fill="none" stroke="{cv.line}" stroke-opacity=".6" stroke-width=".7"/>'
               + f'<rect x="44" y="{y + 5}" width="{f1(max(3, 260 * it["pct"]))}" height="3.5" fill="{cv.hatch(45, 2, .8, .95)}"/>'
               + cv.say(it["left"].upper(), 44, y + 17.5, 8, ls=.5, quiet=True))
    return cv.svg()
