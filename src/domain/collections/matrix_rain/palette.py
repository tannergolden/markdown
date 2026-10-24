# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Rain set's palette: the line printer's greenbar paper and its ribbon by day, the terminal's glass and its case
by night, and the closed set of every colour one of its files may use. The words' inks, the phosphor every light
burns on, the moon and the people's skin are the Matrix hand's (see `collections.hand`)."""
from __future__ import annotations

from ...holidays.pixel.shade import tones
from ..hand import MATRIX

# Hand-set ramps, dark to light: the printout's paper and the ribbon that prints on it by day, the terminal's
# glass and the plastic of its case by night, the desk, the sleeper's clothes and hair, the red half of a two-colour
# ribbon and the manila of a punched card; and the hand's own: one phosphor for every light, one moon, and three
# skins. Every colour a sprite takes is a tone on one of these.
RAMP = {
    "paper": ["#7E8F7E", "#98A996", "#B3C2AE", "#C4D4BF", "#D3E4CF", "#E4E8D4", "#F1F3E6"],   # the printout
    "ribbon": ["#0C211A", "#163328", "#22463A", "#305A4B", "#4A7663", "#6D9783", "#97B9A6"],  # what prints on it
    "glass": ["#020806", "#040D09", "#06120C", "#081610", "#0C1F17", "#123022", "#1B4430"],   # the screen
    "case": ["#0A0F0D", "#121915", "#1A231E", "#243029", "#313F37", "#43544A", "#5B6F63"],    # its plastic
    "desk": ["#120E0B", "#1E1813", "#2C241C", "#3B3127", "#4D4134", "#625443", "#7B6B57"],    # the desk by night
    "cloth": ["#07090A", "#0E1113", "#16191C", "#202428", "#2C3136", "#3B4147", "#4F565D"],   # a black shirt
    "hair": ["#0B0806", "#140F0B", "#1E1711", "#2A2018", "#372A20", "#46362A", "#584536"],
    "beige": ["#4A4538", "#6A6352", "#8A826D", "#A89F87", "#C2BAA0", "#D8D1BA", "#E9E5D3"],   # a 90s case
    "wood": ["#3A2A1C", "#57402B", "#74583C", "#90704D", "#A98A63", "#C2A47D", "#D8BF9C"],    # the desk by day
    "denim": ["#121A2A", "#1C273E", "#283754", "#384B70", "#4C618A", "#677EA4", "#90A4C3"],   # his jeans
    "red": ["#2B0A14", "#4A1220", "#6E1B26", "#93272C", "#B53F37", "#D0624E", "#E68F72"],     # the ribbon's red half
    "manila": ["#3F2E14", "#5F4820", "#81652F", "#A3843F", "#C1A257", "#D9BF7D", "#EDDBAA"],  # a punched card
    "flame": MATRIX.ramp("flame"),                                                            # every light
    "moon": MATRIX.ramp("moon"),
    "skin0": MATRIX.ramp("skin0"), "skin1": MATRIX.ramp("skin1"), "skin2": MATRIX.ramp("skin2"),
}

C = dict(
    white="#FFFFFF",
    paper=RAMP["paper"][5],                                 # the printout's white band
    bar=RAMP["paper"][4],                                   # and its green bar
    ink=MATRIX.body[0], body_night=MATRIX.body[1],          # the words by day and by night: the hand's
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses is a
# token here, in C, in a ramp or in the night (see TOKENS).
X = dict(
    muted_day=MATRIX.muted[0],         # small labels on the printout: the hand's
    muted_night=MATRIX.muted[1],       # and on the glass
    rule_day="#5E7A68", rule_night="#1F5A3A",
    dim_day="#9DB39E", dim_night="#163D29",
)

# --------------------------------------------------------------------------- the night
# The glass from the top of a sheet to its foot: darkest at its edges, where the tube's light falls off, and
# palest across its middle. Every text colour of the night clears 4.5:1 on each band.
NIGHT_SKY = ["#040D09", "#050F0B", "#07140E", "#081610", "#07140E", "#050F0B"]
BAND = 8          # the rows of each band of the greenbar: one line of print
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})

step, ramp_for = tones(RAMP)
