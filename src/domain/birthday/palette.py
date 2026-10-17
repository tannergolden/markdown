# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Birthday set's palette: its ramps, its named colours and its night, and the closed set of every colour one of
its files may use."""
from __future__ import annotations

from ..holidays.pixel.shade import tones

# Hand-set ramps, dark to light: the frostings, the cake and the wrapping paper, the candles' flame, and the plum of a
# room with the lights off. Shadows lean toward plum and lights toward the candles' gold. Every colour a sprite takes
# is a tone on one of these.
RAMP = {
    "strawberry": ["#4E0F33", "#7A1A4A", "#A82B62", "#D9487F", "#F07BA3", "#F9AEC8", "#FDDDE9"],
    "cream": ["#5A4330", "#8A6E50", "#B89A74", "#DCC39C", "#EEDDBF", "#F8EEDC", "#FFFBF4"],
    "cocoa": ["#1F0D08", "#3B1A10", "#5A2C1A", "#7A4327", "#9C5E3A", "#BE8560", "#DDB08D"],
    "mint": ["#0D3029", "#164C41", "#1F6B5A", "#2D8F77", "#4FB698", "#8CD8BE", "#CDF1E3"],
    "lemon": ["#4D3806", "#7A5A0C", "#A67F16", "#CFA524", "#EBC740", "#F7E187", "#FEF4C8"],
    "lilac": ["#21143D", "#362260", "#4E3585", "#6A4DA9", "#8E73C9", "#B9A5E3", "#E4DBF6"],
    "sky": ["#0C2742", "#143F66", "#1F5B8E", "#2F7DB6", "#56A3D8", "#94C7EC", "#D3EAF9"],
    "flame": ["#5A1800", "#8C3200", "#C25500", "#EC8000", "#FFAA22", "#FFD46A", "#FFF3C4"],
    "cherry": ["#3D0610", "#650C1E", "#93152D", "#C0223E", "#E04257", "#F28089", "#FCC3C6"],
    "plum": ["#0B0612", "#160C22", "#211333", "#2E1C47", "#43295F", "#614385", "#9077B3"],
    # The live badge's slate, stepped from #566273 the way this set steps a colour: its shadows toward plum, its
    # lights toward the candles' gold.
    "slate": ["#1A172B", "#24253C", "#383E53", "#566273", "#A5B6C3", "#E6F8FF", "#F0FDFF"],
}

C = dict(
    white="#FFFFFF", paper="#FFF7EE", ink="#2B1630", coal="#0E0A12", slate="#566273",
    strawberry=RAMP["strawberry"][3], mint=RAMP["mint"][3], lemon=RAMP["lemon"][4], lilac=RAMP["lilac"][3],
    sky=RAMP["sky"][3], cocoa=RAMP["cocoa"][3], flame=RAMP["flame"][5],
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses is a token
# here, in C, in a ramp or in the night (see TOKENS).
X = dict(
    muted_day="#7A4F69",      # small labels on the day paper
    muted_night="#CDB9D6",    # small labels in the dark
    body_night="#FBF2F7",     # text in the dark
    accent_day="#A3285A",     # strawberry letters on the day paper, deep enough to read
    rule_day="#C46A92",       # rules by day, a dusty strawberry
    night_rule="#D9A7C2",     # rules in the dark, frosting caught by the candles
    dim_day="#F1E6DA", dim_night="#1B1029",   # a chart's dotted guides
    star_faint="#3A2852", star_dim="#5A4478", star_pale="#FFF1DE",
    shade_ink="#1A0B14",      # see-through shadow
    node_night="#1A0F28",     # a card's face in the dark
)

# --------------------------------------------------------------------------- the room
# The dark, top to foot: a room with the lights off, warmer toward the table the candles stand on.
NIGHT_SKY = ["#0E0818", "#130B20", "#190F2A", "#1F1433", "#26193D"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})
# The frostings, the wrapping papers and the sprinkles come in these.
PASTELS = ("strawberry", "mint", "lemon", "lilac", "sky")
# The tablecloth the scenes stand on: only it takes a shadow or the candles' light pooled on it.
GROUND = {RAMP["strawberry"][3], RAMP["strawberry"][4], RAMP["strawberry"][5], RAMP["cream"][4], RAMP["cream"][5],
          RAMP["cream"][6]}

step, ramp_for = tones(RAMP)
