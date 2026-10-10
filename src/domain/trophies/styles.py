# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The four other card styles: trophy (the default, a cup), medallion, crystal and plaque.

Each draws the same measurement the crest does, with the same footer, so a
consumer can switch `style:` without anything else changing. Importing this
module registers them in `art.STYLES`.
"""
from __future__ import annotations

import math

from .art import (STYLES, Canvas, alt_text, card, f1, fmt, metal, mix, pct_label, status_text, stops, top_pct,
                  width)
from .catalogue import TIER_NAMES, TIERS, Core, measure


def trophy(theme: dict, core: Core, value: int, o: dict | None = None) -> str:
    o = o or {}
    m = measure(core, value)
    t, c, hue = m["t"], TIERS[m["t"]], core.hue
    bowl = "M56 36H124C124 70 111 89 98 94C96 95 95 97 95 100V106H85V100C85 97 84 95 82 94C69 89 56 70 56 36Z"
    foot = "M80 106H100C100 111 106 114 114 116V121H66V116C74 114 80 111 80 106Z"
    hands = "M62 44C38 42 36 76 70 84M118 44C142 42 144 76 110 84"
    cv = card(theme, core, m, o)
    th = cv.th
    cv.add("<defs>" + cv.common_defs()
           + f'<linearGradient id="mu" gradientUnits="userSpaceOnUse" x1="38" y1="0" x2="142" y2="0">{stops(metal(t))}</linearGradient>'
           + f'<linearGradient id="cone" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity="{th["cone"]}"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>'
           + f'<linearGradient id="rim" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{mix(c["d"], "#000000", .35)}"/><stop offset="1" stop-color="{c["m"]}"/></linearGradient>'
           + f'<linearGradient id="pl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{th["plinth"][1]}"/><stop offset="1" stop-color="{th["plinth"][2]}"/></linearGradient>'
           + f'<radialGradient id="en" cx=".4" cy=".35" r=".75"><stop offset="0" stop-color="{mix(hue, "#FFFFFF", .25)}"/><stop offset=".6" stop-color="{hue}"/><stop offset="1" stop-color="{mix(hue, "#000000", .55)}"/></radialGradient>'
           + f'<clipPath id="cup"><path d="{bowl}"/><path d="{foot}"/></clipPath></defs>')
    cv.add(cv.card_base())
    if th["cone"] != "0":
        cv.add('<path d="M72 0H108L152 150H28Z" fill="url(#cone)"/>')
    cv.add('<circle cx="90" cy="72" r="64" fill="url(#glow)"/>' + cv.burst(90, 64)
           + f'<ellipse cx="90" cy="145" rx="48" ry="3.5" fill="{th["shadow"][0]}" fill-opacity="{th["shadow"][1]}"/>'
           + f'<rect x="62" y="121" width="56" height="7" rx="1.5" fill="{th["plinth"][0]}"/><rect x="62" y="121" width="56" height="1" fill="#FFFFFF" fill-opacity=".1"/>'
           + '<rect x="52" y="128" width="76" height="16" rx="2" fill="url(#pl)"/><rect x="52" y="128" width="76" height="1" fill="#FFFFFF" fill-opacity=".12"/>'
           + f'<rect x="72" y="131" width="36" height="10" rx="1.5" fill="url(#mh)" opacity="{1 if t else .35}"/><rect x="74" y="132.6" width="32" height="6.8" rx="1" fill="{"url(#en)" if t else th["ghost_line"]}"/>')
    if t == 0:
        g, gf = th["ghost"], th["ghost_fill"]
        cv.add(f'<path d="{hands}" fill="none" stroke="{g}" stroke-width="2" stroke-dasharray="3 3" stroke-linecap="round"/>'
               f'<path d="{bowl}" fill="{gf[0]}" fill-opacity="{gf[1]}" stroke="{g}" stroke-width="1.4" stroke-dasharray="3 3"/>'
               f'<path d="{foot}" fill="{gf[0]}" fill-opacity="{gf[1]}" stroke="{g}" stroke-width="1.4" stroke-dasharray="3 3"/>'
               f'<ellipse cx="90" cy="36" rx="34" ry="5.5" fill="none" stroke="{g}" stroke-width="1.4" stroke-dasharray="3 3"/>'
               f'<circle cx="90" cy="60" r="15.5" fill="none" stroke="{g}" stroke-width="1.2" stroke-dasharray="2 2"/>'
               + cv.icon(core.icon, 78.6, 48.6, .95, th["ghost_icon"], 2.2))
    else:
        cv.add(f'<path d="{hands}" fill="none" stroke="url(#mu)" stroke-width="6.5" stroke-linecap="round"/>'
               f'<path d="{hands}" fill="none" stroke="{c["h"]}" stroke-opacity=".35" stroke-width="1.2" stroke-linecap="round" transform="translate(0 -1.4)"/>'
               f'<path d="{foot}" fill="url(#mu)"/><path d="{bowl}" fill="url(#mu)"/>'
               f'<ellipse cx="90" cy="100" rx="7.5" ry="2.6" fill="url(#mu)" stroke="{c["d"]}" stroke-opacity=".6" stroke-width=".6"/>'
               f'<path d="M66 116H114" stroke="{c["d"]}" stroke-opacity=".5" stroke-width=".8"/>'
               f'<ellipse cx="90" cy="36" rx="34" ry="5.5" fill="url(#rim)" stroke="{c["h"]}" stroke-opacity=".75" stroke-width="1.2"/>'
               '<g clip-path="url(#cup)"><ellipse cx="68" cy="60" rx="3.6" ry="24" fill="#FFFFFF" fill-opacity=".30"/><ellipse cx="114" cy="56" rx="2" ry="17" fill="#FFFFFF" fill-opacity=".12"/></g>'
               '<circle cx="90" cy="61.2" r="17.5" fill="#000000" fill-opacity=".25"/><circle cx="90" cy="60" r="17.5" fill="url(#md)"/><circle cx="90" cy="60" r="14.6" fill="url(#en)"/>'
               '<ellipse cx="85" cy="53" rx="8.5" ry="4.2" transform="rotate(-25 85 53)" fill="#FFFFFF" fill-opacity=".28"/>'
               + cv.icon(core.icon, 78.6, 49.4, .95, "#000000", 2.2, ' stroke-opacity=".35"')
               + cv.icon(core.icon, 78.6, 48.6, .95, c["h"] if t == 1 else "#FFFFFF", 2.2))
        if t >= 3:
            cv.add('<g clip-path="url(#cup)"><g transform="skewX(-18)"><rect class="sh" x="30" y="20" width="18" height="110" fill="url(#shg)"/></g></g>')
    if t >= 4:
        cv.add(cv.sparkles([(46, 40, 4.5, 0), (136, 30, 3.2, 1.2), (130, 98, 2.6, .6), (50, 100, 2.2, 1.9)] + ([(146, 66, 2.6, 2.4), (34, 64, 3, .9)] if t == 5 else []), t))
    for i in range(5):
        x, got, nxt = 90 + (i - 2) * 13, t >= i + 1, t == i
        col = "url(#dia)" if i == 4 else (TIERS[i + 1]["m"] if th["day"] else TIERS[i + 1]["l"])
        fill = f'fill="{col}"' if got else f'fill="none" stroke="{col if nxt else th["ghost"]}" stroke-opacity="{".8" if nxt else "1"}"'
        cv.add(f'<rect x="-3" y="-3" width="6" height="6" transform="translate({x} 159) rotate(45)" {fill}/>')
    cv.add(cv.corners(core, m) + cv.footer(core, m, "bar", 182))
    return cv.close()


def medallion(theme: dict, core: Core, value: int, o: dict | None = None) -> str:
    o = o or {}
    m = measure(core, value)
    t, c, cx, cy = m["t"], TIERS[m["t"]], 90, 108
    cv = card(theme, core, m, o)
    th = cv.th
    hue = core.hue if t else ("#B8BFC8" if th["day"] else "#3A414B")
    base = mix(hue, "#FFFFFF" if th["day"] and not t else "#000000", .58 if t else .3)
    edge = c["l"] if t else th["ghost"]
    band = "".join(f'<stop offset="{o_}" stop-color="{col}"/>' for o_, col in
                   [(0, base), (.1, base), (.1, edge), (.15, edge), (.15, base), (.36, base), (.36, hue), (.64, hue),
                    (.64, base), (.85, base), (.85, edge), (.9, edge), (.9, base), (1, base)])
    Rr = 52
    C = 2 * math.pi * Rr
    n, hot = TIERS[min(t + 1, 5)], t >= 4
    cv.add("<defs>" + cv.common_defs()
           + f'<linearGradient id="rl" gradientUnits="userSpaceOnUse" x1="56" y1="4" x2="79.8" y2="-3.2">{band}</linearGradient>'
           + f'<linearGradient id="rr" gradientUnits="userSpaceOnUse" x1="124" y1="4" x2="100.2" y2="-3.2">{band}</linearGradient>'
           + '<linearGradient id="rs" gradientUnits="userSpaceOnUse" x1="0" y1="28" x2="0" y2="68"><stop offset="0" stop-color="#000000" stop-opacity="0"/><stop offset="1" stop-color="#000000" stop-opacity=".5"/></linearGradient>'
           + f'<radialGradient id="face" cx=".4" cy=".34" r=".78"><stop offset="0" stop-color="{c["h"]}"/><stop offset=".45" stop-color="{c["l"]}"/><stop offset="1" stop-color="{c["m"]}"/></radialGradient>'
           + f'<radialGradient id="en" cx=".4" cy=".35" r=".75"><stop offset="0" stop-color="{mix(core.hue, "#FFFFFF", .22)}"/><stop offset=".6" stop-color="{core.hue}"/><stop offset="1" stop-color="{mix(core.hue, "#000000", .55)}"/></radialGradient>'
           + '<radialGradient id="gl" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".55"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>'
           + f'<linearGradient id="pr" gradientUnits="userSpaceOnUse" x1="38" y1="0" x2="142" y2="0"><stop offset="0" stop-color="{th["dia"][0] if hot else n["m"]}"/><stop offset="1" stop-color="{th["dia"][2] if hot else (n["l"] if th["day"] else n["h"])}"/></linearGradient>'
           + f'<clipPath id="fc"><circle cx="{cx}" cy="{cy}" r="36"/></clipPath></defs>')
    cv.add(cv.card_base() + f'<circle cx="{cx}" cy="{cy - 6}" r="70" fill="url(#glow)"/>' + cv.burst(cx, cy)
           + '<polygon points="56,2 82,2 102,68 76,68" fill="url(#rl)"/><polygon points="98,2 124,2 104,68 78,68" fill="url(#rr)"/>'
           '<polygon points="56,2 82,2 102,68 76,68" fill="url(#rs)"/><polygon points="98,2 124,2 104,68 78,68" fill="url(#rs)"/>'
           f'<circle cx="{cx}" cy="{cy}" r="{Rr}" fill="none" stroke="{th["track"][0]}" stroke-opacity="{th["track"][1]}" stroke-width="3.5"/>')
    if m["pct"] > 0:
        p = m["pct"]
        a = math.radians(-90 + 360 * p)
        ex, ey = f1(cx + Rr * math.cos(a)), f1(cy + Rr * math.sin(a))
        cv.add(f'<circle cx="{cx}" cy="{cy}" r="{Rr}" fill="none" stroke="url(#pr)" stroke-width="3.5" stroke-linecap="round" stroke-dasharray="{f1(C * p)} {f1(C)}" transform="rotate(-90 {cx} {cy})"/>')
        if p < 1:
            cv.add(f'<circle cx="{ex}" cy="{ey}" r="3.6" fill="{n["m"] if th["day"] else "#FFFFFF"}" fill-opacity=".25"/><circle cx="{ex}" cy="{ey}" r="1.9" fill="{n["d"] if th["day"] else "#FFFFFF"}"/>')
    if t == 0:
        cv.add(f'<circle cx="{cx}" cy="{cy}" r="44" fill="{th["ghost_disc"]}" stroke="{th["ghost"]}" stroke-width="1.4" stroke-dasharray="3 3"/>'
               f'<circle cx="{cx}" cy="{cy}" r="18" fill="none" stroke="{th["ghost_line"]}"/>' + cv.icon(core.icon, cx - 12, cy - 12, 1, th["ghost_icon"], 2.1))
    else:
        leaves = ""
        for side in (-1, 1):
            for i in range(6):
                ang = 104 + i * 21 if side < 0 else 76 - i * 21
                rad = math.radians(ang)
                for dr, tilt in ((2.6, 30), (-2.6, -30)):
                    r = 28.5 + dr
                    x, y = cx + r * math.cos(rad), cy + r * math.sin(rad)
                    rot = ang + 90 - tilt if side < 0 else ang - 90 + tilt
                    leaves += f'<ellipse cx="{f1(x)}" cy="{f1(y)}" rx="4.4" ry="1.7" transform="rotate({f1(rot)} {f1(x)} {f1(y)})"/>'
        cv.add(f'<circle cx="{cx}" cy="{cy + 2}" r="45" fill="#000000" fill-opacity="{".18" if th["day"] else ".45"}"/>'
               f'<circle cx="{cx}" cy="{cy}" r="44" fill="url(#md)"/>'
               f'<circle cx="{cx}" cy="{cy}" r="42.6" fill="none" stroke="{c["d"]}" stroke-opacity=".55" stroke-width="1.8" stroke-dasharray=".9 1.5"/>'
               f'<circle cx="{cx}" cy="{cy}" r="39.5" fill="url(#mdr)"/><circle cx="{cx}" cy="{cy}" r="36" fill="url(#face)"/>'
               f'<g fill="{c["d"]}" fill-opacity=".42">{leaves}</g>'
               f'<circle cx="{cx}" cy="{cy + .8}" r="18.5" fill="#000000" fill-opacity=".25"/><circle cx="{cx}" cy="{cy}" r="18.5" fill="url(#mdr)"/><circle cx="{cx}" cy="{cy}" r="16" fill="url(#en)"/>'
               + cv.icon(core.icon, cx - 12, cy - 11.2, 1, "#000000", 2, ' stroke-opacity=".35"')
               + cv.icon(core.icon, cx - 12, cy - 12, 1, c["h"] if t == 1 else "#FFFFFF", 2)
               + '<g clip-path="url(#fc)"><ellipse cx="76" cy="90" rx="26" ry="14" transform="rotate(-32 76 90)" fill="url(#gl)"/>'
               + ('<g transform="skewX(-18)"><rect class="sh" x="40" y="60" width="16" height="100" fill="url(#shg)"/></g>' if t >= 3 else "") + "</g>")
    if t >= 4:
        cv.add(cv.sparkles([(44, 66, 4, 0), (138, 78, 3, 1.3), (132, 148, 2.6, .7), (48, 148, 2.2, 2)] + ([(150, 118, 2.6, 2.5), (30, 106, 3, 1)] if t == 5 else []), t))
    cv.add(cv.corners(core, m) + cv.footer(core, m, "none", 187))
    return cv.close()


def crystal(theme: dict, core: Core, value: int, o: dict | None = None) -> str:
    o = o or {}
    m = measure(core, value)
    t, c = m["t"], TIERS[m["t"]]
    cv = card(theme, core, m, o)
    th = cv.th
    P = {"T": (90, 22), "LS": (64, 60), "FL": (80, 53), "FR": (100, 53), "RS": (116, 60), "LB": (68, 122), "BL": (81, 128),
         "BR": (99, 128), "RB": (112, 122), "B": (90, 152)}
    pts = lambda keys: " ".join(f"{P[k][0]},{P[k][1]}" for k in keys)  # noqa: E731
    sil = pts(["T", "RS", "RB", "B", "LB", "LS"])
    faces = [(("LS", "FL", "BL", "LB"), "#000000", ".30"), (("FL", "FR", "BR", "BL"), "#FFFFFF", ".05"), (("FR", "RS", "RB", "BR"), "#FFFFFF", ".16"),
             (("T", "LS", "FL"), "#FFFFFF", ".22"), (("T", "FL", "FR"), "#FFFFFF", ".42"), (("T", "FR", "RS"), "#FFFFFF", ".10"),
             (("LB", "BL", "B"), "#000000", ".38"), (("BL", "BR", "B"), "#000000", ".18"), (("BR", "RB", "B"), "#000000", ".08")]
    p = 1.0 if t == 5 else m["pct"]
    yF = 152 - p * (152 - 22)
    glass = c["d"] if t else th["glass0"]
    lit1, lit2, lit3 = ("#FFFFFF", "#B4A8FF", "#56BDF2") if t == 5 else (c["h"], c["l"], c["m"])
    ring_col = "url(#dia)" if t == 5 else c["l"]
    nb = c["m"] if t else "#3A414B"
    cv.add("<defs>" + cv.common_defs()
           + f'<linearGradient id="gs" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{mix(glass, "#FFFFFF", .08)}"/><stop offset="1" stop-color="{mix(glass, "#000000", .45)}"/></linearGradient>'
           + f'<linearGradient id="lt" gradientUnits="userSpaceOnUse" x1="0" y1="{f1(yF)}" x2="0" y2="152"><stop offset="0" stop-color="{lit1}"/><stop offset=".35" stop-color="{lit2}"/><stop offset="1" stop-color="{lit3}"/></linearGradient>'
           + f'<radialGradient id="nb" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{nb}" stop-opacity="{th["nebula"]}"/><stop offset="1" stop-color="{nb}" stop-opacity="0"/></radialGradient>'
           + f'<radialGradient id="en" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{core.hue}" stop-opacity="{".5" if t else ".15"}"/><stop offset="1" stop-color="{core.hue}" stop-opacity="0"/></radialGradient>'
           + '<filter id="bl" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>'
           + f'<clipPath id="xs"><polygon points="{sil}"/></clipPath></defs>')
    cv.add(cv.card_base() + '<circle cx="58" cy="70" r="60" fill="url(#nb)"/><circle cx="126" cy="112" r="56" fill="url(#nb)"/><circle cx="90" cy="86" r="66" fill="url(#glow)"/>' + cv.burst(90, 86)
           + f'<ellipse cx="90" cy="168" rx="36" ry="5" fill="url(#en)"/><ellipse cx="90" cy="168" rx="30" ry="4" fill="{c["l"] if t else "#3A414B"}" fill-opacity="{".4" if t else ".25"}" filter="url(#bl)"/>')

    def shard(x, y, r, d):
        return (f'<g transform="translate({x} {y}) rotate({r})"><polygon class="{"fl" if t >= 3 else ""}" style="animation-delay:{d}s" points="0,-6 4,3 -3,4" '
                f'fill="{c["l"] if t else th["ghost"]}" fill-opacity=".6" stroke="{c["h"] if t else th["ghost"]}" stroke-opacity=".5" stroke-width=".5"/></g>')

    cv.add(shard(40, 44, -20, 0) + shard(142, 50, 25, 1.4) + shard(138, 130, 160, .7) + shard(44, 120, 200, 2.1))
    rings = [(-14, 46, 10), (18, 40, 8)] if t >= 5 else [(-14, 46, 10)] if t >= 4 else []

    def ring_arc(rot, rx, ry, front):
        return (f'<path d="M{90 - rx} 88A{rx} {ry} 0 0 {0 if front else 1} {90 + rx} 88" transform="rotate({rot} 90 88)" fill="none" '
                f'stroke="{ring_col}" stroke-width="{"1.4" if front else "1"}" stroke-opacity="{".9" if front else ".45"}"/>')

    cv.add(f'<g class="{"fl" if t >= 3 else ""}">' + "".join(ring_arc(r, a, b, False) for r, a, b in rings)
           + f'<polygon points="{sil}" fill="url(#gs)" fill-opacity=".92"/>')
    if p > 0:
        cv.add(f'<g clip-path="url(#xs)"><rect x="60" y="{f1(yF)}" width="60" height="{f1(152 - yF)}" fill="url(#lt)" fill-opacity=".92"/>'
               + (f'<rect x="60" y="{f1(yF - .6)}" width="60" height="1.4" fill="#FFFFFF" fill-opacity=".9"/>' if p < 1 else "") + "</g>")
    cv.add("".join(f'<polygon points="{pts(k)}" fill="{f}" fill-opacity="{op}"/>' for k, f, op in faces)
           + '<g fill="none" stroke="#FFFFFF" stroke-opacity=".32" stroke-width=".6" stroke-linejoin="round">' + "".join(f'<polygon points="{pts(k)}"/>' for k, _, _ in faces) + "</g>"
           + f'<polygon points="{sil}" fill="none" stroke="{c["h"] if t else "#6E7681"}" stroke-opacity=".6" stroke-width=".9" stroke-linejoin="round"/>'
           + cv.icon(core.icon, 80.4, 83.2, .8, "#000000", 2.2, ' stroke-opacity=".3"')
           + cv.icon(core.icon, 80.4, 82.4, .8, "#FFFFFF" if t else th["ghost_icon"], 2.2, f' stroke-opacity="{".85" if t else ".8"}"')
           + '<path d="M84 62L86 116" stroke="#FFFFFF" stroke-opacity=".35" stroke-width="1.6" stroke-linecap="round"/>')
    if t >= 3:
        cv.add('<g clip-path="url(#xs)"><g transform="skewX(-18)"><rect class="sh" x="40" y="10" width="14" height="150" fill="url(#shg)" opacity=".8"/></g></g>')
    cv.add("".join(ring_arc(r, a, b, True) for r, a, b in rings) + "</g>")
    if t >= 4:
        cv.add(cv.sparkles([(52, 30, 4, 0), (132, 26, 3, 1.2), (146, 96, 2.6, .6), (34, 86, 2.4, 1.9)] + ([(120, 150, 2.6, 2.4), (58, 150, 3, 1)] if t == 5 else []), t))
    cv.add(cv.corners(core, m) + cv.footer(core, m, "none", 193))
    return cv.close()


def plaque(theme: dict, core: Core, value: int, o: dict | None = None) -> str:
    o = o or {}
    m = measure(core, value)
    t, c = m["t"], TIERS[m["t"]]
    W, H = 264, 88
    cv = Canvas(theme, W, H, alt_text(core, m, o), t, o, 1.0, 5)
    th = cv.th
    cv.add("<defs>" + cv.common_defs()
           + f'<linearGradient id="mv" x1="0" y1="0" x2=".35" y2="1">{stops(metal(t))}</linearGradient>'
           + '<pattern id="br" width="4" height="2" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#FFFFFF" fill-opacity=".07"/></pattern></defs>')
    cv.add(f'<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="{th["plaque"]}"/><rect width="{W}" height="{H}" filter="url(#grain)"/>'
           f'<rect width="80" height="{H}" fill="{"url(#mv)" if t else th["plaque0"]}"/><rect width="80" height="{H}" fill="url(#br)"/>'
           + ('<g transform="skewX(-18)"><rect class="sh" x="-10" y="0" width="16" height="88" fill="url(#shg)" opacity=".7"/></g>' if t >= 3 else "")
           + f'<rect x="80" width="1" height="{H}" fill="{th["edge"][0]}" fill-opacity="{th["edge"][1]}"/>'
           + (f'<polygon points="0,0 26,0 0,26" fill="{th["up"]}"/>' if o.get("new") and t else "")
           + f'</g><rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="4.5" fill="none" stroke="{th["edge"][0]}" stroke-opacity="{th["edge"][1]}"/>')
    if t == 0:
        cv.add(cv.icon("trophy", 18.4, 22.4, 1.8, th["ghost"], 1.5, ' stroke-dasharray="2 2"'))
    else:
        cv.add(cv.icon("trophy", 19, 23.2, 1.8, c["h"], 1.5, ' stroke-opacity=".6"')
               + cv.icon("trophy", 18.4, 22.4, 1.8, "#1C2466" if t == 5 else mix(c["d"], "#000000", .25), 1.5))
    if t >= 4:
        cv.add(cv.sparkles([(14, 14, 3, 0), (66, 74, 2.4, 1.1)], t))
    cv.add(f'<circle cx="102" cy="21" r="6.5" fill="{core.hue}" fill-opacity="{".9" if t else ".25"}"/>' + cv.icon(core.icon, 97.2, 16.2, .4, "#FFFFFF", 2.6)
           + cv.txt(core.title.upper(), face="serif", size=9, x=114, y=24.3, ls=1.8, fill=th["title"]))
    right = TIER_NAMES[t].upper()
    rw = width(right, "serif", 9, 1.8)
    cv.add(cv.txt(right, face="serif", size=9, x=250, y=24.3, anchor="end", ls=1.8, fill=cv.tier_fill(t)))
    from .art import star5
    for k in range(m["stars"]):
        cv.add(f'<polygon points="{star5(250 - rw - 8 - k * 8.4, 21, 3.6)}" fill="{cv.tier_fill(5)}"/>')
    vw = width(fmt(value), "num", 27)
    uw = (width(core.unit, "meta", 27 * .42) + 3) if core.unit else 0
    delta = o.get("delta")
    cv.add(cv.value_line(core, m, 96 + vw / 2 + uw / 2, 56, 27, delta))
    used = 96 + vw + uw + (13 + width(fmt(delta), "meta", 10) if delta else 0)
    sub = ("NEW  ·  " if o.get("new") and t else "") + status_text(m)
    if o.get("rank") and t and used + 8 + width(pct_label(top_pct(core, value)) + "  ·  " + sub, "meta", 9, .5) <= 250:
        sub = pct_label(top_pct(core, value)) + "  ·  " + sub
    cv.add(cv.txt(sub, face="meta", size=9, x=250, y=55, anchor="end", ls=.5, fill=th["muted"]) + cv.seg_bar(96, 67, 154, 5, m))
    return cv.close()


STYLES.update({"trophy": trophy, "medallion": medallion, "crystal": crystal, "plaque": plaque})
