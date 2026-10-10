# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The New Year's Day set's palette: its ramps, its named colours and its sky, and the closed set of every
colour one of its files may use."""
from __future__ import annotations

from ..pixel.shade import tones

# Hand-set ramps, dark to light: shadows lean toward midnight blue, lights toward the gold of lamplight and
# champagne. Every colour a sprite takes is a tone on one of these.
RAMP = {
    "midnight": ["#04060D", "#0A1022", "#121B38", "#1D2B55", "#2F437A", "#5470A8", "#9AAFD6"],
    "gold": ["#3A2604", "#664409", "#946511", "#C08A1C", "#E0B03A", "#F2D27A", "#FCEFC4"],
    "silver": ["#1C2129", "#363E4A", "#59636F", "#86909C", "#B3BCC6", "#D9DFE6", "#F6F8FB"],
    "champagne": ["#4A3A22", "#7A6442", "#A68F66", "#CBB78E", "#E4D5B2", "#F3EAD4", "#FFFAEE"],
    "rose": ["#380A22", "#61133D", "#8C1F58", "#B53176", "#D85395", "#EC8BBA", "#F8C5DC"],
    "teal": ["#05292B", "#0A4548", "#116366", "#1B8585", "#35A8A3", "#76CBC4", "#BDEAE5"],
    "violet": ["#170D2E", "#2A1852", "#402778", "#5A389E", "#7E5CC0", "#A992DB", "#D6CCF1"],
    "bottle": ["#06120C", "#0D2218", "#163826", "#215237", "#33704E", "#5B9676", "#9FC9B1"],
    "dawn": ["#3A1322", "#652033", "#963646", "#C95A5A", "#EB8B6C", "#F7BB94", "#FDE2C6"],
    "coal": ["#050608", "#0D0F14", "#171A22", "#232733", "#343948", "#4B5163", "#6B7285"],
    # The live badge's slate, stepped from #566273 the way this set steps a colour: its shadows toward
    # midnight blue, its lights toward gold.
    "slate": ["#17182B", "#24253C", "#383E53", "#566273", "#A5B6C3", "#E6F8FF", "#F0FDFF"],
}

C = dict(
    white="#FFFFFF", paper="#F7F6F2", grid="#E3E1D8", grid_n="#172036",
    ink="#141A2E", coal="#0D0F14", gold=RAMP["gold"][4], midnight=RAMP["midnight"][3], rose=RAMP["rose"][3],
    teal=RAMP["teal"][3], silver=RAMP["silver"][4], slate="#566273",
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a
# file uses is a token here, in C, in a ramp or in the night sky (see TOKENS).
X = dict(
    muted_day="#4E5672",      # small labels on the day paper
    muted_night="#AEB9D8",    # small labels on the midnight sky
    body_night="#F3F5FB",     # text by night
    accent_day="#7A5200",     # gold letters on the day paper, deep enough to read
    accent_night="#F2D27A",   # gold letters on the midnight sky
    dim_day="#E9E7DF", dim_night="#131B31",    # a chart's dotted guides
    star_faint="#26304D", star_dim="#43507A", star_pale="#FFF6DC",
    moonlit="#8FA0C8",        # the city's glow along a silhouette's edge by night
    shade_ink="#05070D",      # see-through shadow
    node_night="#0E152B",     # a card's face by night
    night_rule="#C9B27E",     # rules by night, champagne
    rule_day="#9A7A3A",       # rules by day, old gold
)

# --------------------------------------------------------------------------- scenery
NIGHT_SKY = ["#04060D", "#070B17", "#0B1122", "#10182E", "#16203B"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})
# The snow underfoot: only it takes a shadow or a light pooled round its foot.
GROUND = {RAMP["silver"][4], RAMP["silver"][5], RAMP["silver"][6], RAMP["midnight"][4], RAMP["midnight"][5],
          RAMP["midnight"][6]}
# The colours confetti comes in.
CONFETTI = ("gold", "rose", "teal", "silver", "violet")

step, ramp_for = tones(RAMP)
