# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Longship set's palette: its ramps of oak, sea, sail and sky, its day and its night, and the closed set
of every colour one of its files may use. The words' inks, the fires, the moon and the people's skin are the
medieval hand's (see `collections.hand`)."""
from __future__ import annotations

from ...holidays.pixel.shade import tones
from ..hand import MEDIEVAL

# Hand-set ramps, dark to light: the oak weathered silver by day and tarred by night, the sea by sun and by
# moon, the paints of the shields and the sail, iron, bronze and rope, the northern lights, and the shore
# with its longhouse; and the hand's own: one flame for every fire, one moon, and three skins. Every colour a
# sprite takes is a tone on one of these.
RAMP = {
    "oak": ["#3A2C1E", "#5B4A36", "#7D6B52", "#9E8C70", "#C4B395", "#D7CAAF", "#E8DEC8"],      # the planks by day
    "tar": ["#07090B", "#0D1013", "#161A1D", "#212629", "#2E3337", "#3E4449", "#555C62"],      # the same planks tarred
    "sea": ["#0F2F45", "#17455F", "#215E7D", "#2E7A9C", "#4A9DBD", "#7FC3DA", "#C4E6F0"],      # the fjord by day
    "deep": ["#050C14", "#091624", "#0E2234", "#153248", "#1F4762", "#2F6584", "#4F8FB0"],     # and under the moon
    "fell": ["#2B3A4A", "#3F5468", "#5A7188", "#7A91A6", "#9DB1C2", "#C2D1DD", "#E6EEF4"],     # the mountains by day
    "fell_n": ["#060A12", "#0B1220", "#111C2E", "#19283E", "#243852", "#35506C", "#4F6E8C"],   # and by night
    "red": ["#3A0B0B", "#5F1313", "#8A1D1A", "#B32A24", "#D4473B", "#E8766A", "#F5B3A8"],      # shield and sail paint
    "cream": ["#6E6250", "#8F8268", "#AFA184", "#CFC3A4", "#E6DCC2", "#F3ECD8", "#FCF8EE"],    # undyed wool and lime
    "ochre": ["#4A2E08", "#7A4E0C", "#A87414", "#CF9A1F", "#E8B93A", "#F3D16A", "#FBE8A8"],    # yellow paint
    "iron": ["#0A0B0E", "#161920", "#242931", "#353B46", "#4B525E", "#67707C", "#8C95A2"],     # bosses, rivets, helms
    "bronze": ["#3B2208", "#6A3F10", "#9A6118", "#C38429", "#DFA543", "#EFC46F", "#F8E2A8"],   # inlay and brooches
    "rope": ["#3A2A14", "#5E4722", "#836633", "#A68648", "#C2A463", "#D9BE85", "#EDD9B0"],     # hemp and the mast
    "flame": MEDIEVAL.ramp("flame"),                                                           # every fire
    "moon": MEDIEVAL.ramp("moon"),                                                             # the moon
    "aurora": ["#0A3A2A", "#0F5A3C", "#167F52", "#22A66A", "#44C98A", "#7EE2B0", "#C5F4DC"],   # the lights, green
    "violet": ["#2A1040", "#44206A", "#5E3390", "#7A4DB2", "#9A70CC", "#BC9BE0", "#DECAF2"],   # and violet
    "turf": ["#1C2E10", "#2F4A1A", "#456A24", "#5F8B30", "#7DAA42", "#A5C968", "#D0E6A2"],     # the roof and the shore
    "rock": ["#26292C", "#3B3F43", "#52575C", "#6B7177", "#878D93", "#A7ADB2", "#CBD0D4"],     # the shore's stone
    "sand": ["#4A3E2A", "#6E5E42", "#92805C", "#B09E78", "#C9B994", "#DDD0B0", "#EEE6CC"],     # the strand
    "skin0": MEDIEVAL.ramp("skin0"), "skin1": MEDIEVAL.ramp("skin1"), "skin2": MEDIEVAL.ramp("skin2"),
    "blond": ["#4A3410", "#7A5A1C", "#A8822C", "#CDA646", "#E3C56A", "#EEDA98", "#F7ECC4"],    # braids and beards
    "blue": ["#0E1E3C", "#17305C", "#214784", "#2E62AC", "#4A84C8", "#7FAADC", "#BDD4EE"],     # dyed wool
    "green": ["#0A2A14", "#114422", "#1A5E2F", "#237A3A", "#35994C", "#62BC72", "#A6DEAE"],    # dyed wool, and a badge
    "raven": ["#05070B", "#0D1118", "#161C26", "#222B38", "#30405A", "#4A6080", "#7E97B8"],    # black with a blue sheen
}

C = dict(
    white="#FFFFFF",
    paper=RAMP["oak"][4],                                   # the weathered planks by day
    ink=MEDIEVAL.body[0], body_night=MEDIEVAL.body[1],      # the words by day and by night: the hand's
    fill="#E8DEC8", fill_night="#1F2224",
    red=RAMP["red"][2], ochre=RAMP["ochre"][4], bronze=RAMP["bronze"][4], iron=RAMP["iron"][2],
)
# The paints a shield, a stripe or a release comes in, by turns.
PAINTS = ("red", "ochre", "cream", "tar")

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses
# is a token here, in C, in a ramp or in the night (see TOKENS).
X = dict(
    muted_day=MEDIEVAL.muted[0],       # small labels on the day planks: the hand's
    muted_night=MEDIEVAL.muted[1],     # and on the tarred planks
    accent_day="#6E1512",      # the paint a day's accents are written in
    dim_day="#9E8C70", dim_night="#2B2E31",     # a chart's dotted guides
    rule_night="#4C5055",
    star_faint="#3A4A4C", star_dim="#6C7E80", star_pale="#DDEBEC",
    shade_ink="#060504",       # see-through shadow
    sun="#FFE89A",             # the day's sun
    gull="#F4F2EC", gull_shade="#AEB2B8",
    grain_night="#1B1F23", knot_night="#111416",   # the grain of the tarred planks, and the odd knot
    snow_night="#A8DCCB",                          # snow on the fells under the aurora
)

# --------------------------------------------------------------------------- the night
# The tarred planks from the top of a sheet to its foot: greened by the aurora above, warmed by the brazier
# below, and dark between. Every text colour of the night clears 4.5:1 on each band.
NIGHT_SKY = ["#0C1A1B", "#0E1617", "#121313", "#171210", "#1B140D"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})
# The pixels the brazier's light falls on: the planks, the shore and the longhouse; and the water it shivers on.
LIT = set(RAMP["oak"]) | set(RAMP["tar"]) | set(RAMP["sand"]) | set(RAMP["rock"]) | set(RAMP["turf"]) | \
    set(RAMP["rope"]) | set(RAMP["fell_n"])
WATER = set(RAMP["sea"]) | set(RAMP["deep"])

step, ramp_for = tones(RAMP)
