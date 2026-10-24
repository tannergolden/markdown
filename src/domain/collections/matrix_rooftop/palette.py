# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Rooftop set's palette: the summer sky by day and the night city's deep blue, the blue mirror glass of the
towers, the steel and concrete of the roofs, the brick, the water tower's staves, the long dark coat, the helicopter,
and the closed set of every colour one of its files may use. The words' inks, the phosphor every light burns on, the
moon and the people's skin are the Matrix hand's (see `collections.hand`)."""
from __future__ import annotations

from ...holidays.pixel.shade import tones
from ..hand import MATRIX

# Hand-set ramps, dark to light: the towers' blue mirror glass, the steel of the girders, the plant and the lamps, the
# concrete of the coping, the brick of the facades, the cedar staves of the water tower, the long coat's black
# leather, the haze the far city stands in by day and the dusk it stands in by night, the helicopter's olive drab, the
# pigeons' grey and the clouds, and the street's own paints a badge is lettered in: a cab's yellow, rusted iron, an
# awning's plum and a street sign's green; and the hand's own: one phosphor for every light, one moon, and three skins.
RAMP = {
    "glass": ["#0C1830", "#152747", "#203B66", "#2E5287", "#436EA8", "#6A93C4", "#A6C3DF"],   # blue mirror glass
    "steel": ["#171B21", "#262C34", "#38404A", "#4F5964", "#69747F", "#8A949E", "#B0B8C0"],
    "concrete": ["#45423F", "#605C57", "#7B7670", "#97918A", "#B1ABA2", "#CAC5BC", "#E1DDD5"],
    "brick": ["#341A15", "#4F271F", "#6C3629", "#894734", "#A45E45", "#BC7D5D", "#D3A282"],
    "cedar": ["#2B1C11", "#432E1B", "#5C4227", "#775834", "#927146", "#AD8D5F", "#C8AB82"],
    "coat": ["#08090B", "#0F1114", "#171A1F", "#21252B", "#2D3239", "#3C424A", "#50575F"],
    "haze": ["#5D7387", "#718699", "#859AAB", "#99ADBC", "#ADBFCC", "#C0D0DA", "#D3DFE6"],     # the far city by day
    "dusk": ["#050917", "#091021", "#0E172C", "#141F37", "#1B2944", "#243452", "#304264"],     # and by night
    "olive": ["#191D12", "#272D1D", "#373F29", "#4A5436", "#5F6B47", "#79865D", "#98A57C"],    # the helicopter
    "pigeon": ["#2B2C35", "#424557", "#5B5F74", "#75798F", "#9195A9", "#AEB2C2", "#CDD0DA"],
    "cloud": ["#9EB3C6", "#B4C6D6", "#C9D7E3", "#DAE4EC", "#E7EEF3", "#F1F5F8", "#FAFCFD"],
    "taxi": ["#3B2805", "#664708", "#966A0D", "#C48F15", "#E5AF23", "#F3C84F", "#FBDF8A"],     # a cab's yellow
    "rust": ["#3A1607", "#61250C", "#8A3812", "#B24E1B", "#D2682A", "#E58B50", "#F2B285"],     # rusted iron
    "plum": ["#1F0F27", "#341A42", "#4C275E", "#66367B", "#824B97", "#9F6BB2", "#BF95CD"],     # an awning's plum
    "go": ["#0A2015", "#113421", "#194A30", "#226341", "#2F7E55", "#479A6E", "#6FB78E"],       # a street sign's green
    "flame": MATRIX.ramp("flame"),                                                             # every light
    "moon": MATRIX.ramp("moon"),
    "skin0": MATRIX.ramp("skin0"), "skin1": MATRIX.ramp("skin1"), "skin2": MATRIX.ramp("skin2"),
}

C = dict(
    white="#FFFFFF",
    ink=MATRIX.body[0], body_night=MATRIX.body[1],          # the words by day and by night: the hand's
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses is a
# token here, in C, in a ramp or in the night (see TOKENS).
X = dict(
    muted_day=MATRIX.muted[0],         # small labels on the sky: the hand's
    muted_night=MATRIX.muted[1],       # and by night
    rule_day="#7E95A8", rule_night="#2A3A5A",
    dim_day="#9DB6C9", dim_night="#1A2742",
    shade_ink="#060810",               # see-through shadow
    glasses="#050608",                 # dark glasses
)

# --------------------------------------------------------------------------- the sky
# The summer sky from the top of a sheet to its foot, deepest overhead and paling to the haze over the city; and the
# night's, deepest overhead and lifting toward the city's glow. Every text colour clears 4.5:1 on each band.
DAY_SKY = ["#A6C8E2", "#B2D0E6", "#BED7E8", "#C8DDE9", "#CFE0E8"]
NIGHT_SKY = ["#070D20", "#091126", "#0C152C", "#0F1931", "#121D36", "#152139"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in DAY_SKY} | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})

step, ramp_for = tones(RAMP)
