# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Valentine's Day set's palette: its ramps, its named colours and its sky, and the closed set of every
colour one of its files may use."""
from __future__ import annotations

from ..pixel.shade import tones

# Hand-set ramps, dark to light: shadows lean toward wine and plum, lights toward the warm pink of a
# candle's light on a petal. Every colour a sprite takes is a tone on one of these.
RAMP = {
    "rose": ["#2B0716", "#4E0C24", "#7A1231", "#A8183D", "#D22B47", "#EE6069", "#FCABA6"],
    "blush": ["#3A0D2B", "#63184B", "#922A6C", "#C0468E", "#E274AF", "#F4A5CB", "#FDD8E7"],
    "lace": ["#4A3838", "#786261", "#A48E8B", "#CBB7B1", "#E7D8D2", "#F6EDE8", "#FFFBF8"],
    "cocoa": ["#160A07", "#2C140D", "#472116", "#633021", "#83462D", "#A76842", "#CE9468"],
    "gold": ["#3A2604", "#664409", "#946511", "#C08A1C", "#E0B03A", "#F2D27A", "#FCEFC4"],
    "leaf": ["#07170F", "#0D2A1A", "#164326", "#215D34", "#357B47", "#5A9A62", "#93C18B"],
    "wine": ["#0B0410", "#170819", "#240D27", "#341438", "#4C2151", "#6F3973", "#9E639D"],
    "lilac": ["#1E1131", "#35225B", "#4F3785", "#6D52AF", "#927ACD", "#B9A7E3", "#DFD5F5"],
    "silver": ["#1C2129", "#363E4A", "#59636F", "#86909C", "#B3BCC6", "#D9DFE6", "#F6F8FB"],
    "coal": ["#050608", "#0D0F14", "#171A22", "#232733", "#343948", "#4B5163", "#6B7285"],
    # The slate a live badge says "no data" in, and the tones round it: set by hand, as its shadows lean
    # blue where the ramps `make_ramp` builds lean purple.
    "slate": ["#17182B", "#24253C", "#383E53", "#566273", "#A5B6C3", "#E6F8FF", "#F0FDFF"],
}

C = dict(
    white="#FFFFFF", paper="#FDF7F5", grid="#F2DEE0", grid_n="#221028",
    ink="#2A0E1D", coal="#0D0F14", rose=RAMP["rose"][3], blush=RAMP["blush"][4], gold=RAMP["gold"][4],
    lace=RAMP["lace"][5], cocoa=RAMP["cocoa"][3], leaf=RAMP["leaf"][3], slate="#566273",
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a
# file uses is a token here, in C, in a ramp or in the night sky (see TOKENS).
X = dict(
    muted_day="#6F4757",      # small labels on the day paper
    muted_night="#D6B2C3",    # small labels on the night sky
    body_night="#FFF4F7",     # text by night
    dim_day="#F4E6E8", dim_night="#25102B",    # a chart's dotted guides
    star_faint="#34203D", star_dim="#5A3F63", star_pale="#FFF0F3",
    moonlit="#B58DB6",        # the moon's light along a silhouette's edge by night
    shade_ink="#0B0308",      # see-through shadow
    node_night="#1D0B23",     # a card's face by night
    night_rule="#D9A6BB",     # rules by night, dusty pink
    rule_day="#B8687F",       # rules by day, old rose
)

NIGHT_SKY = ["#0B0410", "#10061A", "#170A22", "#1F0E2B", "#281335"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})
_B, _W, _Lc = RAMP["blush"], RAMP["wine"], RAMP["lace"]
# What things stand on: the lace runner on the table and the stone of the quay. Only it takes a shadow or
# a light pooled round a foot.
RUNNER = {False: (_B[6], _Lc[6], _B[5]), True: (_W[6], _W[5], _W[4])}
STONE = {False: (_Lc[4], _Lc[3], _Lc[2]), True: (_W[4], _W[3], _W[2])}
GROUND = set(RUNNER[False]) | set(RUNNER[True]) | set(STONE[False]) | set(STONE[True])
# The colours petals and paper hearts come in.
PETALS = ("rose", "rose", "blush")

step, ramp_for = tones(RAMP)
