# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Thanksgiving set's palette: its ramps, its named colours and its sky, and the closed set of every
colour one of its files may use."""
from __future__ import annotations

from ..pixel.shade import make_ramp, tones  # noqa: F401  (make_ramp: a ramp built from one colour)

# Hand-set ramps, dark to light: shadows lean toward plum, lights toward the gold of late afternoon
# and of candlelight. Every colour a sprite takes is a tone on one of these.
RAMP = {
    "squash": ["#3A1406", "#63240B", "#8F3A12", "#C05A1C", "#E07E2E", "#F2A65A", "#FAD29E"],
    "cranberry": ["#2E0710", "#4F0C1C", "#74142A", "#9B2335", "#BF3E4A", "#DE6E6E", "#F4AEA6"],
    "wheat": ["#3E2A08", "#6A4B10", "#977019", "#C39A2C", "#DDBB52", "#EDD58C", "#FAF0CC"],
    "sage": ["#1A2410", "#2C3B1B", "#43562A", "#5E7438", "#7E934E", "#A6B676", "#D2DCAE"],
    "bark": ["#1A0F09", "#2E1A10", "#4A2B1A", "#6B4026", "#8C5A37", "#B07E55", "#D6AB82"],
    "linen": ["#3A3129", "#6A5D50", "#9C8D7C", "#C9BCA8", "#E6DCCB", "#F5EEE2", "#FFFCF6"],
    "plum": ["#1C0A1A", "#33112F", "#4F1B47", "#6E2A63", "#8E4581", "#B170A5", "#D6A6CD"],
    "moon": ["#4A3420", "#7A5530", "#AD7A40", "#D9A459", "#EFC47E", "#FADFAA", "#FFF4DC"],
    "earth": ["#120C09", "#1F1510", "#2E2019", "#403024", "#554234", "#6E5A4A", "#8C7766"],
    "coal": ["#070504", "#120D0B", "#1E1613", "#2C211C", "#3E3029", "#57463C", "#7A6556"],
}
RAMP["slate"] = make_ramp("#566273")

C = dict(
    white="#FFFFFF", paper="#F8F2E7", grid="#E6DAC6", grid_n="#2A1B18",
    ink="#2A1A10", coal="#120D0B", squash=RAMP["squash"][3], cranberry=RAMP["cranberry"][3],
    wheat=RAMP["wheat"][4], sage=RAMP["sage"][3], slate="#566273",
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a
# file uses is a token here, in C, in a ramp or in the night sky (see TOKENS).
X = dict(
    muted_day="#6B4F3D",      # small labels on the day paper
    muted_night="#CDB79F",    # small labels on the evening sky
    body_night="#F6EEE2",     # text by night
    accent_day="#9E3413",     # rust letters on the day paper
    accent_night="#F2A65A",   # squash letters on the evening sky
    dim_day="#EDE3D2", dim_night="#2C1D1A",    # a chart's dotted guides
    star_faint="#3A2A28", star_dim="#5C4640", star_pale="#FFF1DA",
    moonlit="#B98E62",        # the harvest moon's light along a silhouette's edge
    shade_ink="#0B0605",      # see-through shadow
    node_night="#21150F",     # a card's face by night
    night_rule="#C79A6B",     # rules by night
    rule_day="#8C5A37",       # rules by day
    maple_night="#E8664A",    # a title's red by night, light enough to read on the sky
    maple_deep_night="#D9573F",
)

# --------------------------------------------------------------------------- scenery
NIGHT_SKY = ["#0C0708", "#120A0C", "#190E10", "#211315", "#2A1819"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})
# The ground's earth: only it takes a shadow or a candle's light pooled round its foot.
GROUND = {RAMP["earth"][2], RAMP["earth"][3], RAMP["earth"][4], RAMP["earth"][5]}
# The families a turning leaf takes, each a ramp: most red, orange or gold, a few still green or gone brown.
LEAF_RAMPS = ("cranberry", "squash", "wheat", "bark", "sage")

step, ramp_for = tones(RAMP)
