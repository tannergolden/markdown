# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Juneteenth set's palette: its ramps, its named colours and its sky, and the closed set of every
colour one of its files may use."""
from __future__ import annotations

from ..pixel.shade import tones

# Hand-set ramps, dark to light: shadows lean toward the blue of a Gulf evening, lights toward the gold of
# a June sun. Every colour a sprite takes is a tone on one of these.
RAMP = {
    "blue": ["#08123A", "#0E1F63", "#172E8F", "#2242B8", "#3A63D8", "#7196EA", "#B7CDF6"],
    "red": ["#2E0708", "#56100F", "#851917", "#B3241E", "#D93A2B", "#F06B52", "#FBAE95"],
    "linen": ["#4A4238", "#77695A", "#A39583", "#CBBFAE", "#E6DDCF", "#F5F0E6", "#FFFDF8"],
    "green": ["#06180B", "#0B2E15", "#124620", "#1B612C", "#2A7F3B", "#4E9E55", "#8CC47F"],
    "gold": ["#3A2604", "#664409", "#946511", "#C08A1C", "#E0B03A", "#F2D27A", "#FCEFC4"],
    "oak": ["#1C0F07", "#35200F", "#553418", "#784B24", "#9C6734", "#BF8B52", "#DDB582"],
    "brick": ["#240B08", "#441510", "#6B2219", "#913425", "#B24E36", "#CF7658", "#E8A98C"],
    "sand": ["#3D3423", "#6A5B3D", "#978560", "#BFAE84", "#DACCA4", "#EDE3C6", "#FAF5E6"],
    "sea": ["#041C22", "#08323B", "#0E4C57", "#176A74", "#2A8D93", "#5AB2B1", "#9FD6CF"],
    "dusk": ["#05050F", "#0A0B20", "#121436", "#1C1E4C", "#2C2D66", "#474583", "#7470AD"],
    "silver": ["#1C2129", "#363E4A", "#59636F", "#86909C", "#B3BCC6", "#D9DFE6", "#F6F8FB"],
    "coal": ["#050608", "#0D0F14", "#171A22", "#232733", "#343948", "#4B5163", "#6B7285"],
    # Built from #566273 as `make_ramp` builds a ramp, but with its shadows leaning toward blue like the rest.
    "slate": ["#17182B", "#24253C", "#383E53", "#566273", "#A5B6C3", "#E6F8FF", "#F0FDFF"],
}

C = dict(
    white="#FFFFFF", paper="#FBF8F2", grid="#E9E2D4", grid_n="#15173A",
    ink="#151A33", coal="#0D0F14", blue=RAMP["blue"][3], red=RAMP["red"][3], green=RAMP["green"][3],
    gold=RAMP["gold"][4], linen=RAMP["linen"][5], slate="#566273",
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a
# file uses is a token here, in C, in a ramp or in the night sky (see TOKENS).
X = dict(
    muted_day="#545A73",      # small labels on the day paper
    muted_night="#B5BDD9",    # small labels on the night sky
    body_night="#F8F6F0",     # text by night
    dim_day="#ECE6DA", dim_night="#171A3C",    # a chart's dotted guides
    star_faint="#23264A", star_dim="#3D4273", star_pale="#FFF7DE",
    moonlit="#8C93C8",        # the sky's last light along a silhouette's edge by night
    shade_ink="#05060C",      # see-through shadow
    node_night="#0F1230",     # a card's face by night
    night_rule="#C9B27E",     # rules by night, old gold
    rule_day="#8B7B5E",       # rules by day, weathered oak
    violet="#6B3FA0",         # a badge's purple, which the flag's colours do not have
)

# --------------------------------------------------------------------------- scenery
NIGHT_SKY = ["#05050F", "#08091B", "#0D0E28", "#141436", "#1E1B45"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})
_G, _S = RAMP["green"], RAMP["sand"]
# What things stand on: the lawn and the sand. Only it takes a shadow or a light pooled round a foot.
GROUND = {_G[1], _G[2], _G[3], _G[4], _S[2], _S[3], _S[4], _S[5]}
# The colours confetti comes in: the flag's red, blue and white, with gold and green.
CONFETTI = ("red", "blue", "gold", "green", "linen")

step, ramp_for = tones(RAMP)
