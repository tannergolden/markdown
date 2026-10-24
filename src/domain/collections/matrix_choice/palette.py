# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Choice set's palette: an old hotel room's damask wallpaper, dusty rose by day and wine-black by night, its
oxblood leather and brass, the red and the blue of the two pills, and the closed set of every colour one of its files
may use. The words' inks, the phosphor every light burns on, the moon and the people's skin are the Matrix hand's
(see `collections.hand`)."""
from __future__ import annotations

from ...holidays.pixel.shade import tones
from ..hand import MATRIX

# Hand-set ramps, dark to light, shadows leaning purple and lights leaning gold: the wallpaper by day and by night,
# the chesterfield's oxblood leather and its brass nails, the candy-red gel of the title and the red pill, the blue
# pill, the mahogany of the furniture, glass, the storm outside by day and by night, the curtains' green velvet and
# the box's satin; and the hand's own: one phosphor for every light, one moon, and three skins.
RAMP = {
    "rose": ["#5A3440", "#7E4D58", "#A06C72", "#BE8B8E", "#D3A5A5", "#DEB8B5", "#E9CCC5"],      # the paper by day
    "wine": ["#12050B", "#1A080F", "#230E14", "#2D131B", "#3A1A23", "#4B2430", "#603340"],      # and by night
    "oxblood": ["#2B0610", "#470B16", "#66121D", "#861D24", "#A8302F", "#C54C42", "#DE7A62"],   # the leather
    "brass": ["#3B2208", "#5C3A10", "#81591B", "#A87D2B", "#CBA143", "#E6C66C", "#F8E8A8"],     # its nails
    "candy": ["#4D0717", "#7E0B1E", "#B11222", "#DD1F2C", "#F5474A", "#FF8478", "#FFD2C4"],     # the red gel
    "blue": ["#0D1550", "#142380", "#1C38B4", "#2C58E2", "#5A85F6", "#97B6FF", "#D6E3FF"],      # the blue pill
    "mahogany": ["#1C0B08", "#30140D", "#482114", "#62301D", "#7F4429", "#9E5D3A", "#BE7D52"],  # the furniture
    "glass": ["#1E2A38", "#314455", "#4B6273", "#6C8595", "#91A9B6", "#B9CDD5", "#E3EEF0"],     # glass and water
    "storm": ["#2B2C3B", "#3D4052", "#545869", "#6D7283", "#8A909F", "#A8AEBB", "#C8CDD6"],     # the day's storm
    "night": ["#05060C", "#0A0C17", "#101424", "#171C31", "#20273F", "#2B3450", "#384464"],     # and the night's
    "velvet": ["#061410", "#0B2219", "#123326", "#1B4634", "#275B43", "#367154", "#4C8A69"],    # the curtains
    "satin": ["#5A4E40", "#807360", "#A39780", "#C1B69E", "#D8CFB9", "#E8E2D0", "#F6F3E8"],     # the box's lining
    "flame": MATRIX.ramp("flame"),                                                            # every light
    "moon": MATRIX.ramp("moon"),
    "skin0": MATRIX.ramp("skin0"), "skin1": MATRIX.ramp("skin1"), "skin2": MATRIX.ramp("skin2"),
}

C = dict(
    white="#FFFFFF",
    paper=RAMP["rose"][5],                                  # the wallpaper's ground by day
    paper_n=RAMP["wine"][2],                                # and by night
    ink=MATRIX.body[0], body_night=MATRIX.body[1],          # the words by day and by night: the hand's
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses is a
# token here, in C, in a ramp or in the night (see TOKENS).
X = dict(
    muted_day=MATRIX.muted[0],         # the quieter words: the hand's
    muted_night=MATRIX.muted[1],
    rule_day="#9E6870", rule_night="#5A2A36",
    dim_day="#C99A9B", dim_night="#3A1A24",
    shade="#2A0A14",                   # the shadow a thing casts on the wallpaper, laid see-through
)

# --------------------------------------------------------------------------- the night
# The wallpaper from the top of a sheet to its foot by night: darkest under the ceiling and along the floor, a
# shade warmer across the middle where the lamp's light carries. Every text colour of the night clears 4.5:1 on each.
NIGHT_SKY = ["#1E0B11", "#210D13", "#230E14", "#230E14", "#210D13", "#1E0B11"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})

step, ramp_for = tones(RAMP)
