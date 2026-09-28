# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The drawing: cards, pins and the two banner cards, as SVG strings.

Every function here is pure: the same measurement and the same options give
byte-identical output, which is what lets `check` compare committed files
against a fresh drawing. There is no date anywhere in an image, so a quiet
day produces no diff.

Two cases are drawn for every image: Night for GitHub's dark theme and Day
for its light one. The README picks one with a `<picture>` element.

Cards are drawn on a 180x244 design and declared 164x222, so two fit across
the 343 px a phone gives a README. Pins are 104x124; three fit across.
"""
from __future__ import annotations

import math
from html import escape

from .. import KIT, KIT_VERSION
from . import calibration
from .catalogue import ICONS, PAL, RARITY_NAMES, RCORE, TIER_NAMES, TIERS, Achievement, Core, ach_state, measure
from .text import Lettering, f1, width

CARD_W, CARD_H, CARD_K = 180, 244, 164 / 180
PIN_W, PIN_H = 104, 124

NIGHT = {
    "day": False, "bg": ("#171C26", "#0A0D13"), "edge": ("#FFFFFF", ".09"), "title": "#8B949E", "value": "#F3F5F7",
    "muted": "#8B949E", "track": ("#FFFFFF", ".08"), "ghost": "#4A5361", "ghost_fill": ("#FFFFFF", ".025"),
    "ghost_icon": "#5A6371", "ghost_disc": "#1A1F27", "ghost_line": "#2E3440",
    "grain": "0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 .07 0", "cone": ".13", "plinth": ("#1C222D", "#262D3A", "#10141C"),
    "shadow": ("#000000", ".6"), "chip": ("#FFFFFF", ".08"), "chip_ink": "#C9D1D9", "up": "#3FB950", "glow": 1.0,
    "dia": ("#6CCBFF", "#C4B2FF", "#F29BDD"), "tier": ("#8B949E", "#DE9A60", "#CDD5DD", "#EDC34A", "#BCD6F0"),
    "spark": "#FFFFFF", "spark_dia": "#E9E2FF", "glass0": "#2A3039", "plaque": "#07090C", "plaque0": "#1C2027",
    "nebula": ".35",
}
DAY = {
    "day": True, "bg": ("#FFFFFF", "#EDF0F3"), "edge": ("#1F2328", ".13"), "title": "#59636E", "value": "#1F2328",
    "muted": "#59636E", "track": ("#1F2328", ".09"), "ghost": "#B3BAC3", "ghost_fill": ("#1F2328", ".03"),
    "ghost_icon": "#A1A9B3", "ghost_disc": "#E9ECEF", "ghost_line": "#D0D5DB",
    "grain": "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 .05 0", "cone": "0", "plinth": ("#D5DAE0", "#E6E9ED", "#C3C9D1"),
    "shadow": ("#1F2328", ".2"), "chip": ("#1F2328", ".06"), "chip_ink": "#424A53", "up": "#1A7F37", "glow": 0.55,
    "dia": ("#2F7DD1", "#7B61E0", "#C2449A"), "tier": ("#6E7781", "#9A5A26", "#6B7682", "#946A07", "#4A6788"),
    "spark": "#8FA6C0", "spark_dia": "#8C7BFF", "glass0": "#C8CED6", "plaque": "#FFFFFF", "plaque0": "#E4E8EC",
    "nebula": ".2",
}
CASES = {"night": NIGHT, "day": DAY}

ANIM = ("@keyframes tw{0%,100%{opacity:.15;transform:scale(.45)}50%{opacity:1;transform:scale(1)}}"
        ".sp{transform-box:fill-box;transform-origin:center;animation:tw 3.4s ease-in-out infinite}"
        "@keyframes sh{0%{transform:translateX(-110px)}38%,100%{transform:translateX(200px)}}.sh{animation:sh 6.5s ease-in-out infinite}"
        "@keyframes fl{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}.fl{animation:fl 5s ease-in-out infinite}")
BURST = ("@keyframes bu{0%{opacity:0;transform:scale(.4)}22%{opacity:.95}100%{opacity:0;transform:scale(1.3)}}"
         ".bu{transform-box:fill-box;transform-origin:center;animation:bu 1.9s ease-out .2s 1 both}")
CALM = "@media (prefers-reduced-motion:reduce){.sp,.fl{animation:none}.sh,.bu{display:none}}"


# --- small geometry and color helpers ----------------------------------------
def fmt(n) -> str:
    return f"{int(round(n)):,}"


def mix(a: str, b: str, t: float) -> str:
    pa, pb = int(a[1:], 16), int(b[1:], 16)

    def ch(s):
        return round(((pa >> s) & 255) * (1 - t) + ((pb >> s) & 255) * t)

    return "#%02X%02X%02X" % (ch(16), ch(8), ch(0))


def metal(t: int) -> list:
    if t == 5:
        return [(0, "#2A3A9E"), (.2, "#55BDF2"), (.4, "#FFFFFF"), (.56, "#BBA7FF"), (.78, "#EC8BD6"), (1, "#2A3A9E")]
    c = TIERS[t]
    return [(0, c["d"]), (.2, c["m"]), (.4, c["h"]), (.54, c["l"]), (.78, c["m"]), (1, c["d"])]


def stops(ramp) -> str:
    return "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in ramp)


def hex_pts(cx, cy, r):
    return [(cx + r * math.cos(math.radians(-90 + 60 * k)), cy + r * math.sin(math.radians(-90 + 60 * k))) for k in range(6)]


def hexagon(cx, cy, r) -> str:
    return " ".join(f"{f1(x)},{f1(y)}" for x, y in hex_pts(cx, cy, r))


def star4(s: float) -> str:
    k = s * .18
    return (f"M0 {f1(-s)}Q{f1(k)} {f1(-k)} {f1(s)} 0Q{f1(k)} {f1(k)} 0 {f1(s)}Q{f1(-k)} {f1(k)} {f1(-s)} 0"
            f"Q{f1(-k)} {f1(-k)} 0 {f1(-s)}Z")


def star5(cx, cy, r) -> str:
    pts = []
    for i in range(10):
        a = math.radians(-90 + 36 * i)
        rr = r * .45 if i % 2 else r
        pts.append(f"{f1(cx + rr * math.cos(a))},{f1(cy + rr * math.sin(a))}")
    return " ".join(pts)


def status_text(m: dict) -> str:
    if m["t"] == 5:
        return f"{int(m['pct'] * 100)}% TO STAR {m['stars'] + 1}" if m["next"] else "ALL STARS"
    return f"{int(m['pct'] * 100)}% TO {m['next'].upper()}"


def top_pct(core: Core, v: int) -> float:
    """Share of the reference population at or above `v`, from the calibration.

    The two modes share some keys (commits, stars), so the mode is read from
    which core list the trophy belongs to."""
    mode = "repository" if any(c is core for c in RCORE) else "profile"
    return calibration.top_pct(mode, core.key, v)


def pct_label(p: float) -> str:
    """TOP 17%, TOP 2.8%, TOP 0.05%: whole numbers from ten, one decimal to one, two figures below."""
    if p >= 10:
        s = str(round(p))
    elif p >= 1:
        s = f"{p:.1f}".rstrip("0").rstrip(".")
    else:
        s = f"{p:.2g}"
        if "e" in s:
            s = f"{p:.3f}".rstrip("0")
    return f"TOP {s}%"


def alt_text(core: Core, m: dict, o: dict) -> str:
    s = f"{core.title} trophy: {TIER_NAMES[m['t']]}"
    if m["stars"]:
        s += f" with {m['stars']} star{'s' if m['stars'] > 1 else ''}"
    s += f", {fmt(m['v'])}" + (f" {core.unit}" if core.unit else "")
    if m["next"]:
        s += f", {int(m['pct'] * 100)}% to {m['next']}"
    if o.get("rank") and m["t"]:
        s += f", {pct_label(top_pct(core, m['v'])).lower()}"
    if o.get("delta"):
        s += f", up {fmt(o['delta'])} this week"
    if o.get("new"):
        s += ", newly reached"
    return s


# --- a canvas: one SVG in progress ------------------------------------------
class Canvas:
    """Shared machinery for one image: theme, glyph collection, defs, footer."""

    def __init__(self, theme: dict, w: int, h: int, label: str, t: int, o: dict | None = None, k: float = 1.0, r: int = 14):
        self.th, self.w, self.h, self.t, self.o, self.r = theme, w, h, t, o or {}, r
        self.L = Lettering()
        css = (ANIM if t >= 3 else "") + (BURST if self.o.get("new") else "")
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{round(w * k)}" height="{round(h * k)}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(label, quote=True)}"><!--{KIT} v{KIT_VERSION} trophy {"day" if theme["day"] else "night"}-->'
            f"<title>{escape(label)}</title>" + (f"<style>{css}{CALM}</style>" if css else "")
        ]

    # -- fragments -------------------------------------------------------------
    def add(self, s: str) -> None:
        self.parts.append(s)

    def txt(self, s, **kw) -> str:
        return self.L.text(s, **kw)

    def tier_fill(self, t: int) -> str:
        return "url(#dia)" if t == 5 else self.th["tier"][t]

    def common_defs(self) -> str:
        th, t, w, h, r = self.th, self.t, self.w, self.h, self.r
        c, n, hot = TIERS[t], TIERS[min(t + 1, 5)], t >= 4
        glow = f"{round(.34 * th['glow'] * 100) / 100:g}" if t else "0"
        return (
            f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{th["bg"][0]}"/><stop offset="1" stop-color="{th["bg"][1]}"/></linearGradient>'
            f'<clipPath id="card"><rect width="{w}" height="{h}" rx="{r}"/></clipPath>'
            f'<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="{th["grain"]}"/></filter>'
            f'<radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{c["l"]}" stop-opacity="{glow}"/><stop offset="1" stop-color="{c["l"]}" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="mh" x1="0" y1="0" x2="1" y2="0">{stops(metal(t))}</linearGradient>'
            f'<linearGradient id="md" x1="0" y1="0" x2="1" y2="1">{stops(metal(t))}</linearGradient>'
            f'<linearGradient id="mdr" x1="1" y1="1" x2="0" y2="0">{stops(metal(t))}</linearGradient>'
            f'<linearGradient id="dia" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{th["dia"][0]}"/><stop offset=".5" stop-color="{th["dia"][1]}"/><stop offset="1" stop-color="{th["dia"][2]}"/></linearGradient>'
            f'<linearGradient id="pb" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{th["dia"][0] if hot else n["m"]}"/><stop offset="1" stop-color="{th["dia"][2] if hot else (n["l"] if th["day"] else n["h"])}"/></linearGradient>'
            '<linearGradient id="shg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/><stop offset=".5" stop-color="#FFFFFF" stop-opacity=".6"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>'
        )

    def card_base(self) -> str:
        th, w, h, r = self.th, self.w, self.h, self.r
        return (f'<g clip-path="url(#card)"><rect width="{w}" height="{h}" fill="url(#bg)"/><rect width="{w}" height="{h}" filter="url(#grain)"/></g>'
                f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{r - .5}" fill="none" stroke="{th["edge"][0]}" stroke-opacity="{th["edge"][1]}"/>')

    def sparkles(self, spots, t: int) -> str:
        fill = self.th["spark_dia"] if t == 5 else self.th["spark"]
        return "".join(f'<g transform="translate({x} {y})"><path class="sp" style="animation-delay:{d}s" d="{star4(s)}" fill="{fill}"/></g>'
                       for x, y, s, d in spots)

    @staticmethod
    def icon(name: str, x: float, y: float, scale: float, stroke: str, sw: float, extra: str = "") -> str:
        return (f'<g transform="translate({f1(x)} {f1(y)}) scale({scale})" fill="none" stroke="{stroke}" stroke-width="{sw}" '
                f'stroke-linecap="round" stroke-linejoin="round"{extra}>{ICONS[name]}</g>')

    def bar(self, x, y, w, m) -> str:
        th = self.th
        fw = max(4, w * m["pct"]) if m["pct"] > 0 else 0
        s = f'<rect x="{x}" y="{y}" width="{w}" height="4" rx="2" fill="{th["track"][0]}" fill-opacity="{th["track"][1]}"/>'
        if fw:
            s += f'<rect x="{x}" y="{y}" width="{f1(fw)}" height="4" rx="2" fill="url(#pb)"/>'
        return s

    def seg_bar(self, x, y, w, h, m, gap=3) -> str:
        th = self.th
        sw = (w - gap * 4) / 5
        s = ""
        for i in range(5):
            X = x + i * (sw + gap)
            s += f'<rect x="{f1(X)}" y="{y}" width="{f1(sw)}" height="{h}" rx="{f1(h / 2)}" fill="{th["track"][0]}" fill-opacity="{th["track"][1]}"/>'
            f = 1 if m["t"] > i else (m["pct"] if m["t"] == i else 0)
            if f > 0:
                col = "url(#dia)" if i == 4 else (TIERS[i + 1]["m"] if th["day"] else TIERS[i + 1]["l"])
                s += f'<rect x="{f1(X)}" y="{y}" width="{f1(max(h, sw * f))}" height="{h}" rx="{f1(h / 2)}" fill="{col}"/>'
        return s

    def value_line(self, core: Core, m: dict, cx, y, size, delta) -> str:
        th = self.th
        vs = fmt(m["v"])
        vw = width(vs, "num", size)
        uw = width(core.unit, "meta", size * .42) + 3 if core.unit else 0
        x0 = cx - (vw + uw) / 2
        s = self.txt(vs, face="num", size=size, x=x0, y=y, fill=th["value"])
        if core.unit:
            s += self.txt(core.unit, face="meta", size=size * .42, x=x0 + vw + 3, y=y, fill=th["muted"])
        if delta:
            dx, dy = x0 + vw + uw + 5, y - size * .44
            s += (f'<polygon points="{f1(dx)},{f1(dy)} {f1(dx + 6)},{f1(dy)} {f1(dx + 3)},{f1(dy - 5)}" fill="{th["up"]}"/>'
                  + self.txt(fmt(delta), face="meta", size=10, x=dx + 8, y=dy, fill=th["up"]))
        return s

    def row(self, parts, cx, y) -> str:
        """A centered row of mixed runs: {'s','face','size','fill','ls'} or {'stars','fill'}."""
        widths = [p["stars"] * 8.4 if "stars" in p else width(p["s"], p.get("face", "meta"), p.get("size", 9), p.get("ls", 0)) for p in parts]
        gap = 4
        x = cx - (sum(widths) + gap * (len(parts) - 1)) / 2
        out = ""
        for p, w in zip(parts, widths):
            if "stars" in p:
                for k in range(p["stars"]):
                    out += f'<polygon points="{star5(x + 4 + k * 8.4, y - 3.2, 3.8)}" fill="{p["fill"]}"/>'
            else:
                out += self.txt(p["s"], face=p.get("face", "meta"), size=p.get("size", 9), x=x, y=y, ls=p.get("ls", 0), fill=p["fill"])
            x += w + gap
        return out

    def status(self, m: dict, cx, y, with_tier=True) -> str:
        th = self.th
        parts = []
        if with_tier:
            parts.append({"s": TIER_NAMES[m["t"]].upper(), "face": "serif", "size": 8.5, "ls": 1.2, "fill": self.tier_fill(m["t"])})
            if m["stars"]:
                parts.append({"stars": m["stars"], "fill": self.tier_fill(5)})
            parts.append({"s": "·", "size": 9, "fill": th["muted"]})
        parts.append({"s": status_text(m), "face": "meta", "size": 9.5, "ls": .5, "fill": th["muted"]})
        return self.row(parts, cx, y)

    def corners(self, core: Core, m: dict) -> str:
        th, o, W = self.th, self.o, self.w
        s = ""
        if o.get("rank") and m["t"]:
            lab = pct_label(top_pct(core, m["v"]))
            w = width(lab, "meta", 8.5, .6) + 12
            s += (f'<rect x="10" y="10" width="{f1(w)}" height="15" rx="7.5" fill="{th["chip"][0]}" fill-opacity="{th["chip"][1]}"/>'
                  + self.txt(lab, face="meta", size=8.5, x=16, y=20.6, ls=.6, fill=th["chip_ink"]))
        if o.get("new") and m["t"]:
            c = TIERS[m["t"]]
            pts = f"{W - 60},0 {W - 38},0 {W},38 {W},60"
            s += (f'<g clip-path="url(#card)"><polygon points="{pts}" fill="url(#md)"/>'
                  f'<polygon points="{pts}" fill="none" stroke="{c["d"]}" stroke-opacity=".5" stroke-width=".8"/></g>')
            ink = "#1C2466" if m["t"] == 5 else mix(c["d"], "#000000", .3)
            s += (f'<g transform="rotate(45 {W - 24.5} 24.5)">'
                  + self.txt("NEW", face="serif", size=8.5, x=W - 24.5, y=27.6, anchor="middle", ls=1.6, fill=ink) + "</g>")
        return s

    def burst(self, cx, cy) -> str:
        if not self.o.get("new") or not self.t:
            return ""
        rays = ""
        for i in range(16):
            a = math.radians(i * 22.5)
            r1, r2 = 26, (58 if i % 2 else 72)
            rays += f'<path d="M{f1(cx + r1 * math.cos(a))} {f1(cy + r1 * math.sin(a))}L{f1(cx + r2 * math.cos(a))} {f1(cy + r2 * math.sin(a))}"/>'
        return f'<g class="bu" stroke="{TIERS[self.t]["l"]}" stroke-width="2" stroke-linecap="round">{rays}</g>'

    def footer(self, core: Core, m: dict, kind: str, y0: int) -> str:
        th = self.th
        s = self.txt(core.title.upper(), face="serif", size=9.5, x=90, y=y0, anchor="middle", ls=2.2, fill=th["title"])
        s += self.value_line(core, m, 90, y0 + 27, 28, self.o.get("delta"))
        if kind == "bar":
            s += self.bar(24, y0 + 35, 132, m)
        if kind == "seg":
            s += self.seg_bar(26, y0 + 35, 128, 4, m)
        return s + self.status(m, 90, 235, kind != "seg")

    def close(self) -> str:
        self.parts.append(f"<defs>{self.L.defs()}</defs></svg>")
        return "".join(self.parts)


def card(theme: dict, core: Core, m: dict, o: dict | None = None) -> Canvas:
    """A card canvas with the shared defs and background already in place."""
    o = o or {}
    cv = Canvas(theme, CARD_W, CARD_H, alt_text(core, m, o), m["t"], o, CARD_K)
    return cv


# --- the crest ---------------------------------------------------------------------
def crest(theme: dict, core: Core, value: int, o: dict | None = None) -> str:
    o = o or {}
    m = measure(core, value)
    t, c, cx, cy = m["t"], TIERS[m["t"]], 90, 96
    cv = card(theme, core, m, o)
    th = cv.th
    hue = core.hue if t else mix(core.hue, "#B8BEC6" if th["day"] else "#2A3038", .8)
    cv.add("<defs>" + cv.common_defs()
           + f'<linearGradient id="mu" gradientUnits="userSpaceOnUse" x1="36" y1="44" x2="144" y2="152">{stops(metal(t))}</linearGradient>'
           + f'<linearGradient id="mur" gradientUnits="userSpaceOnUse" x1="144" y1="152" x2="36" y2="44">{stops(metal(t))}</linearGradient>'
           + f'<radialGradient id="en" cx=".5" cy=".36" r=".72"><stop offset="0" stop-color="{mix(hue, "#FFFFFF", .2)}"/><stop offset=".55" stop-color="{hue}"/><stop offset="1" stop-color="{mix(hue, "#000000", .62)}"/></radialGradient>'
           + f'<linearGradient id="ig" gradientUnits="userSpaceOnUse" x1="0" y1="{cy - 18}" x2="0" y2="{cy + 18}"><stop offset="0" stop-color="{c["h"] if t else "#9AA1AB"}"/><stop offset="1" stop-color="{c["l"] if t else "#5A626D"}"/></linearGradient>'
           + f'<linearGradient id="gem" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{mix(core.hue, "#FFFFFF", .6)}"/><stop offset=".5" stop-color="{core.hue}"/><stop offset="1" stop-color="{mix(core.hue, "#000000", .5)}"/></linearGradient>'
           + f'<linearGradient id="tl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["m"]}"/><stop offset="1" stop-color="{c["d"]}"/></linearGradient>'
           + f'<clipPath id="enc"><polygon points="{hexagon(cx, cy, 42)}"/></clipPath></defs>')
    cv.add(cv.card_base() + f'<circle cx="{cx}" cy="{cy}" r="72" fill="url(#glow)"/>' + cv.burst(cx, cy))
    if t == 0:
        gf = th["ghost_fill"]
        cv.add(f'<polygon points="{hexagon(cx, cy, 51)}" fill="{gf[0]}" fill-opacity="{gf[1]}" stroke="{th["ghost"]}" stroke-width="1.4" stroke-dasharray="3 3" stroke-linejoin="round"/>'
               f'<polygon points="{hexagon(cx, cy, 42)}" fill="{core.hue}" fill-opacity="{".12" if th["day"] else ".16"}" stroke="{th["ghost_line"]}" stroke-width="1" stroke-linejoin="round"/>'
               + cv.icon(core.icon, cx - 17.4, cy - 17.4, 1.45, th["ghost_icon"], 1.7)
               + f'<rect x="40" y="136" width="100" height="16" rx="1.5" fill="{gf[0]}" fill-opacity="{gf[1]}" stroke="{th["ghost"]}" stroke-width="1" stroke-dasharray="3 3"/>'
               + cv.txt("UNRANKED", face="serif", size=8.5, x=cx, y=147.3, anchor="middle", ls=2.2, fill=th["ghost_icon"]))
    else:
        if t >= 4:
            wing = "M46 76C32 66 20 60 8 57C13 69 24 80 42 90ZM43 92C28 88 15 86 4 88C11 97 24 104 42 105ZM45 108C33 110 22 113 12 119C21 124 33 125 47 120Z"
            veins = "M40 84C30 76 20 70 12 64M38 99C28 96 17 94 9 93M42 114C32 115 23 117 17 120"
            cv.add(f'<g fill="url(#mu)" stroke="{c["d"]}" stroke-opacity=".6" stroke-width=".7"><path d="{wing}"/><path d="{wing}" transform="translate(180 0) scale(-1 1)"/></g>'
                   f'<g fill="none" stroke="{c["h"]}" stroke-opacity=".45" stroke-width=".7"><path d="{veins}"/><path d="{veins}" transform="translate(180 0) scale(-1 1)"/></g>')
        cv.add(f'<polygon points="{hexagon(cx, cy + 2.5, 53)}" fill="#000000" fill-opacity="{".16" if th["day"] else ".45"}"/>'
               f'<polygon points="{hexagon(cx, cy, 51)}" fill="url(#mu)" stroke="url(#mu)" stroke-width="5" stroke-linejoin="round"/>'
               f'<polygon points="{hexagon(cx, cy, 46.5)}" fill="url(#mur)"/><polygon points="{hexagon(cx, cy, 42)}" fill="url(#en)"/>'
               f'<g clip-path="url(#enc)"><polygon points="{hexagon(cx, cy, 34)}" fill="none" stroke="#FFFFFF" stroke-opacity=".07"/>'
               f'<polygon points="{hexagon(cx, cy, 26)}" fill="none" stroke="#FFFFFF" stroke-opacity=".06"/>'
               '<path d="M40 54H140V84C112 76 72 90 40 104Z" fill="#FFFFFF" fill-opacity=".09"/>'
               f'<polygon points="{hexagon(cx, cy, 42)}" fill="none" stroke="#000000" stroke-opacity=".35" stroke-width="3"/>'
               + ('<g transform="skewX(-18)"><rect class="sh" x="40" y="40" width="16" height="120" fill="url(#shg)" opacity=".7"/></g>' if t >= 3 else "")
               + "</g>"
               + cv.icon(core.icon, cx - 17.4, cy - 17.4 + 1.4, 1.45, "#000000", 1.7, ' stroke-opacity=".35"')
               + cv.icon(core.icon, cx - 17.4, cy - 17.4 - 1, 1.45, "url(#ig)", 1.7))
        if t >= 2:
            pts = [p for i, p in enumerate(hex_pts(cx, cy, 49)) if i != 3 and not (t >= 3 and i == 0)]
            cv.add("".join(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="1.8" fill="{c["h"]}" stroke="{c["d"]}" stroke-width=".7"/>' for x, y in pts))
        if t >= 5:
            cv.add(f'<path d="M73 36L77 21L84 29L90 16L96 29L103 21L107 36Z" fill="url(#md)" stroke="{c["d"]}" stroke-opacity=".7" stroke-width=".8" stroke-linejoin="round"/>'
                   f'<g fill="#FFFFFF" stroke="{c["d"]}" stroke-opacity=".4" stroke-width=".5"><circle cx="77" cy="21" r="1.6"/><circle cx="90" cy="16" r="1.9"/><circle cx="103" cy="21" r="1.6"/></g>')
        if t >= 3:
            cv.add(f'<polygon points="90,34 99,45 90,58 81,45" fill="url(#md)" stroke="{c["d"]}" stroke-opacity=".6" stroke-width=".8"/>'
                   '<polygon points="90,37.5 96.5,45 90,54.5 83.5,45" fill="url(#gem)"/>'
                   '<polygon points="90,37.5 96.5,45 90,45" fill="#FFFFFF" fill-opacity=".5"/><polygon points="83.5,45 90,54.5 90,45" fill="#000000" fill-opacity=".25"/>')
        dark = mix(c["d"], "#000000", .4)
        cv.add('<path d="M28 140H50V156H28L34 148Z" fill="url(#tl)"/><path d="M152 140H130V156H152L146 148Z" fill="url(#tl)"/>'
               f'<path d="M40 152L50 156V152Z" fill="{dark}"/><path d="M140 152L130 156V152Z" fill="{dark}"/>'
               '<rect x="40" y="136" width="100" height="16" rx="1.5" fill="url(#mh)"/><rect x="40" y="136" width="100" height="1" fill="#FFFFFF" fill-opacity=".35"/>')
        ink = "#1C2466" if t == 5 else mix(c["d"], "#000000", .25)
        name = TIER_NAMES[t].upper()
        if m["stars"]:
            lw, sw = width(name, "serif", 8.5, 2.2), m["stars"] * 8.4
            x0 = cx - (lw + 5 + sw) / 2
            cv.add(cv.txt(name, face="serif", size=8.5, x=x0, y=147.3, ls=2.2, fill=ink)
                   + "".join(f'<polygon points="{star5(x0 + lw + 5 + 4 + k * 8.4, 144, 3.6)}" fill="{ink}"/>' for k in range(m["stars"])))
        else:
            cv.add(cv.txt(name, face="serif", size=8.5, x=cx, y=147.3, anchor="middle", ls=2.2, fill=ink))
    if t >= 4:
        cv.add(cv.sparkles([(26, 42, 4, 0), (154, 48, 3, 1.2), (152, 128, 2.6, .7), (26, 130, 2.2, 1.9)] + ([(120, 18, 2.6, 2.4), (60, 16, 3, 1)] if t == 5 else []), t))
    cv.add(cv.corners(core, m) + cv.footer(core, m, "seg", 182))
    return cv.close()


# --- the achievement pin -------------------------------------------------------
def pin(theme: dict, a: Achievement, cur) -> str:
    st = ach_state(a, cur)
    cx, cy = 52, 48
    earned, secret = st["earned"], st["secret"]
    t = st["rarity"] if earned else 0
    c = TIERS[t]
    pct = 1.0 if st["done"] else st["pct"]
    nm = a.name + (f" {st['tier']}" if st["tier"] else "")
    if secret:
        label = "Secret achievement"
    elif earned:
        label = f"{nm}: earned, {RARITY_NAMES[st['rarity']]}"
        if not st["done"]:
            label += f", {int(pct * 100)}% to {a.name} {st['next_tier']}"
    elif st["measured"]:
        label = f"{nm}: {int(pct * 100)}% ({fmt(st['cur'])} of {fmt(st['next'])})"
    else:
        label = f"{nm}: not measured yet"
    cv = Canvas(theme, PIN_W, PIN_H, label, t, {}, 1.0, 12)
    th = cv.th
    hue = a.hue if earned else mix(a.hue, "#D5DAE0" if th["day"] else "#262C35", .74)
    cv.add("<defs>" + cv.common_defs()
           + f'<radialGradient id="en" cx=".42" cy=".36" r=".75"><stop offset="0" stop-color="{mix(hue, "#FFFFFF", .2)}"/><stop offset=".55" stop-color="{hue}"/><stop offset="1" stop-color="{mix(hue, "#000000", .6 if earned else .25)}"/></radialGradient>'
           + f'<linearGradient id="ig" gradientUnits="userSpaceOnUse" x1="0" y1="{cy - 14}" x2="0" y2="{cy + 14}"><stop offset="0" stop-color="{c["h"] if earned else "#7D858F"}"/><stop offset="1" stop-color="{c["l"] if earned else "#4E5661"}"/></linearGradient>'
           + '<radialGradient id="gl" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".45"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>'
           + f'<clipPath id="fc"><circle cx="{cx}" cy="{cy}" r="27"/></clipPath></defs>')
    cv.add(cv.card_base() + f'<circle cx="{cx}" cy="{cy}" r="48" fill="url(#glow)"/>')
    if not secret and not st["done"]:
        R = 38
        C = 2 * math.pi * R
        rc = TIERS[st["next_rarity"]]
        cv.add(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{th["track"][0]}" stroke-opacity="{th["track"][1]}" stroke-width="2.6"/>')
        if pct > 0:
            col = "url(#dia)" if st["next_rarity"] == 5 else (rc["m"] if th["day"] else rc["l"])
            cv.add(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{col}" stroke-width="2.6" stroke-linecap="round" '
                   f'stroke-dasharray="{f1(C * min(1, pct))} {f1(C)}" transform="rotate(-90 {cx} {cy})"/>')
    if secret:
        cv.add(f'<circle cx="{cx}" cy="{cy}" r="33" fill="{th["ghost_disc"]}" stroke="{th["ghost"]}" stroke-width="1.3" stroke-dasharray="3 3"/>'
               + cv.icon("q", cx - 16.8, cy - 16.8, 1.4, th["ghost_icon"], 2))
    else:
        cv.add(f'<circle cx="{cx}" cy="{cy + 1.5}" r="34" fill="#000000" fill-opacity="{".14" if th["day"] else ".45"}"/><circle cx="{cx}" cy="{cy}" r="33" fill="url(#md)"/>')
        if earned:
            cv.add(f'<circle cx="{cx}" cy="{cy}" r="31.8" fill="none" stroke="{c["d"]}" stroke-opacity=".55" stroke-width="1.5" stroke-dasharray=".9 1.4"/>')
        cv.add(f'<circle cx="{cx}" cy="{cy}" r="29.6" fill="url(#mdr)"/><circle cx="{cx}" cy="{cy}" r="27" fill="url(#en)"/>'
               + cv.icon(a.icon, cx - 13.2, cy - 13.2 + 1.2, 1.1, "#000000", 1.9, ' stroke-opacity=".35"')
               + cv.icon(a.icon, cx - 13.2, cy - 13.2 - .6, 1.1, "url(#ig)", 1.9)
               + f'<g clip-path="url(#fc)"><ellipse cx="42" cy="34" rx="20" ry="10" transform="rotate(-32 42 34)" fill="url(#gl)" opacity="{".7" if earned else ".25"}"/>'
               + ('<g transform="skewX(-18)"><rect class="sh" x="10" y="10" width="12" height="80" fill="url(#shg)" opacity=".6"/></g>' if earned and t >= 3 else "")
               + "</g>")
    if earned and t >= 4:
        cv.add(cv.sparkles([(18, 18, 3, 0), (88, 26, 2.4, 1.2), (86, 74, 2, .6)], t))
    nsize = 7.6 if len(nm) > 15 else 9
    cv.add(cv.txt("???" if secret else nm, face="serif", size=nsize, x=cx, y=101, anchor="middle", ls=.3,
                  fill=th["ghost_icon"] if secret else (th["value"] if earned else th["muted"])))
    if secret:
        cap = "SECRET"
    elif earned:
        cap = RARITY_NAMES[st["rarity"]].upper() + ("" if st["done"] else f" · {fmt(st['cur'])}/{fmt(st['next'])}")
    elif st["measured"]:
        cap = f"{int(pct * 100)}% · {fmt(st['cur'])}/{fmt(st['next'])}"
    else:
        cap = "NOT MEASURED YET"
    cv.add(cv.txt(cap, face="meta", size=8.5, x=cx, y=114, anchor="middle", ls=.8, fill=cv.tier_fill(st["rarity"]) if earned else th["muted"]))
    return cv.close()


# --- the level card and the next-up card ------------------------------------------
TIER_XP = (0, 100, 300, 700, 1500, 3100)
RAR_XP = (0, 50, 100, 200, 400, 800)


def xp_core(core: Core, v: int) -> float:
    m = measure(core, v)
    if m["t"] == 5:
        return 3100 + 400 * m["stars"] + 400 * m["pct"]
    return TIER_XP[m["t"]] + (TIER_XP[m["t"] + 1] - TIER_XP[m["t"]]) * m["pct"]


def xp_ach(a: Achievement, cur) -> int:
    st = ach_state(a, cur)
    return sum(RAR_XP[r] for r in a.rarities[: st["k"]])


def level_xp(L: int) -> int:
    return 15 * L * (L + 1)


def level_stats(cores: list, values: dict, ach: list, curs: dict) -> dict:
    """XP, level, and case completion for a whole case."""
    xp = round(sum(xp_core(c, values[c.key]) for c in cores) + sum(xp_ach(a, curs.get(a.slug)) for a in ach))
    L = 0
    while level_xp(L + 1) <= xp:
        L += 1
    ms = [measure(c, values[c.key]) for c in cores]
    earned = sum(1 for a in ach if ach_state(a, curs.get(a.slug))["earned"])
    completion = (sum(min(1, (m["t"] + (m["pct"] if m["t"] < 5 else 1)) / 5) for m in ms) + earned) / (len(cores) + len(ach))
    return {"xp": xp, "L": L, "lp": (xp - level_xp(L)) / (level_xp(L + 1) - level_xp(L)), "bt": min(5, L // 10 + 1),
            "ms": ms, "earned": earned, "completion": completion}


def level_card(theme: dict, cores: list, values: dict, ach: list, curs: dict, subject: str, foot: tuple) -> str:
    """`foot` is (icon, hue, main text, muted text): the streak line or the release line."""
    W, H = 420, 152
    st = level_stats(cores, values, ach, curs)
    bt, c = st["bt"], TIERS[st["bt"]]
    label = f"{subject}: level {st['L']}, {fmt(st['xp'])} XP, case {round(st['completion'] * 100)}% complete, {foot[2].lower()}"
    cv = Canvas(theme, W, H, label, bt, {}, 1.0, 16)
    th = cv.th
    cv.add("<defs>" + cv.common_defs()
           + '<radialGradient id="en" cx=".5" cy=".38" r=".7"><stop offset="0" stop-color="#3A4C86"/><stop offset=".6" stop-color="#22305A"/><stop offset="1" stop-color="#0F1630"/></radialGradient>'
           + f'<linearGradient id="xp" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c["m"]}"/><stop offset="1" stop-color="{c["l"] if th["day"] else c["h"]}"/></linearGradient>'
           + f'<linearGradient id="cp" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{PAL["emerald"]}"/><stop offset="1" stop-color="{PAL["aqua"]}"/></linearGradient>'
           + f'<clipPath id="enc"><polygon points="{hexagon(78, 76, 40)}"/></clipPath></defs>')
    cv.add(cv.card_base() + '<circle cx="78" cy="76" r="80" fill="url(#glow)"/>')
    Rr = 60
    C = 2 * math.pi * Rr
    cv.add(f'<circle cx="78" cy="76" r="{Rr}" fill="none" stroke="{th["track"][0]}" stroke-opacity="{th["track"][1]}" stroke-width="3"/>'
           f'<circle cx="78" cy="76" r="{Rr}" fill="none" stroke="url(#xp)" stroke-width="3" stroke-linecap="round" stroke-dasharray="{f1(C * st["lp"])} {f1(C)}" transform="rotate(-90 78 76)"/>'
           f'<polygon points="{hexagon(78, 78, 50)}" fill="#000000" fill-opacity="{".16" if th["day"] else ".45"}"/>'
           f'<polygon points="{hexagon(78, 76, 48)}" fill="url(#md)" stroke="url(#md)" stroke-width="4" stroke-linejoin="round"/>'
           f'<polygon points="{hexagon(78, 76, 44)}" fill="url(#mdr)"/><polygon points="{hexagon(78, 76, 40)}" fill="url(#en)"/>'
           '<g clip-path="url(#enc)"><path d="M30 40H130V66C104 60 64 72 30 86Z" fill="#FFFFFF" fill-opacity=".08"/>'
           + ('<g transform="skewX(-18)"><rect class="sh" x="30" y="20" width="16" height="120" fill="url(#shg)" opacity=".5"/></g>' if bt >= 3 else "")
           + "</g>"
           + cv.txt("LEVEL", face="serif", size=7.5, x=78, y=62, anchor="middle", ls=2.2, fill=c["l"])
           + cv.txt(str(st["L"]), face="num", size=36, x=78, y=94, anchor="middle", fill="#FFFFFF")
           + f'<rect x="154" y="22" width="1" height="108" fill="{th["edge"][0]}" fill-opacity="{th["edge"][1]}"/>')
    x0, w = 170, 234
    # A repository is named by its own name: the owner is in the README and
    # the alt text, and the title face has no slash. A name that already
    # ends in an S takes the bare apostrophe, so "trophies" reads as
    # TROPHIES’ TROPHY CASE rather than TROPHIES’S.
    name = subject.rsplit("/", 1)[-1].upper()
    ttl = f"{name}{'’' if name.endswith('S') else '’S'} TROPHY CASE"
    tsz, tls = 12.5, 2.0
    while width(ttl, "serif", tsz, tls) > w and tsz > 8:
        tsz -= .5
        tls = max(.8, tls - .2)
    cv.add(cv.txt(ttl, face="serif", size=tsz, x=x0, y=42, ls=tls, fill=th["value"])
           + cv.txt(f"LEVEL {st['L']}  ·  {fmt(st['xp'])} XP  ·  {fmt(level_xp(st['L'] + 1) - st['xp'])} TO LEVEL {st['L'] + 1}", face="meta", size=9.5, x=x0, y=59, ls=.5, fill=th["muted"])
           + f'<rect x="{x0}" y="65" width="{w}" height="5" rx="2.5" fill="{th["track"][0]}" fill-opacity="{th["track"][1]}"/><rect x="{x0}" y="65" width="{f1(max(5, w * st["lp"]))}" height="5" rx="2.5" fill="url(#xp)"/>'
           + cv.txt(f"CASE {round(st['completion'] * 100)}% COMPLETE" + (f"  ·  {st['earned']} OF {len(ach)} ACHIEVEMENTS" if ach else ""), face="meta", size=9.5, x=x0, y=90, ls=.5, fill=th["muted"])
           + f'<rect x="{x0}" y="96" width="{w}" height="5" rx="2.5" fill="{th["track"][0]}" fill-opacity="{th["track"][1]}"/><rect x="{x0}" y="96" width="{f1(max(5, w * st["completion"]))}" height="5" rx="2.5" fill="url(#cp)"/>'
           + f'<circle cx="{x0 + 7}" cy="120" r="7.5" fill="{foot[1]}"/>' + cv.icon(foot[0], x0 + 2, 115, .42, "#FFFFFF", 2.6)
           + cv.txt(foot[2], face="meta", size=10.5, x=x0 + 20, y=124, ls=.5, fill=th["value"])
           + cv.txt(foot[3], face="meta", size=9.5, x=x0 + 20 + width(foot[2], "meta", 10.5, .5), y=124, ls=.5, fill=th["muted"]))
    if bt >= 4:
        cv.add(cv.sparkles([(30, 24, 3.5, 0), (132, 128, 2.6, 1.2)], bt))
    return cv.close()


def next_up_items(cores: list, values: dict, ach: list, curs: dict, n: int = 3) -> list:
    items = []
    for c in cores:
        m = measure(c, values[c.key])
        if m["next"]:
            items.append({"icon": c.icon, "hue": c.hue, "name": f"{c.title} to {m['next']}", "pct": m["pct"], "left": f"{fmt(m['to_go'])} {c.word}"})
    for a in ach:
        st = ach_state(a, curs.get(a.slug))
        if st["measured"] and st["next"] and not a.passive and not st["secret"]:
            items.append({"icon": a.icon, "hue": a.hue, "name": a.name + (f" {st['next_tier']}" if st["tiered"] else ""),
                          "pct": st["pct"], "left": (f"{fmt(st['next'] - st['cur'])} {a.word} to go").replace("  ", " ")})
    items.sort(key=lambda x: -x["pct"])
    return items[:n]


def next_up_card(theme: dict, cores: list, values: dict, ach: list, curs: dict) -> str:
    W, H = 328, 152
    items = next_up_items(cores, values, ach, curs)
    label = "Next up: " + ", ".join(f"{i['name']} {int(i['pct'] * 100)}%" for i in items)
    cv = Canvas(theme, W, H, label, 0, {}, 1.0, 16)
    th = cv.th
    cv.add("<defs>" + cv.common_defs() + "</defs>" + cv.card_base())
    cv.add(cv.txt("NEXT UP", face="serif", size=8.5, x=24, y=40, ls=2.2, fill=th["title"]))
    for i, it in enumerate(items):
        y = 64 + i * 28
        cv.add(f'<circle cx="30" cy="{y - 4}" r="7" fill="{it["hue"]}" fill-opacity=".9"/>' + cv.icon(it["icon"], 25.4, y - 8.6, .38, "#FFFFFF", 2.8)
               + cv.txt(it["name"], face="meta", size=10.5, x=44, y=y, fill=th["value"])
               + cv.txt(f"{int(it['pct'] * 100)}%", face="meta", size=10, x=304, y=y, anchor="end", fill=th["muted"])
               + f'<rect x="44" y="{y + 5}" width="260" height="3" rx="1.5" fill="{th["track"][0]}" fill-opacity="{th["track"][1]}"/>'
               + f'<rect x="44" y="{y + 5}" width="{f1(max(3, 260 * it["pct"]))}" height="3" rx="1.5" fill="{it["hue"]}"/>'
               + cv.txt(it["left"].upper(), face="meta", size=8, x=44, y=y + 17, ls=.5, fill=th["muted"]))
    return cv.close()


STYLES = {"crest": crest}
