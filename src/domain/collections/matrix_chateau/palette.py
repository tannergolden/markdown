# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Chateau set's palette: champagne silk damask by day and a wine-dark damask by night, the gilt of its frames,
the hall's marble, its red carpet, its crystal, its linen and its steel, and the closed set of every colour one of its
files may use. The words' inks, the phosphor every candle burns on, the moon and the people's skin are the Matrix
hand's (see `collections.hand`)."""
from __future__ import annotations

from ...holidays.pixel.shade import tones
from ..hand import MATRIX

# Hand-set ramps, dark to light, their shadows leaning purple and their lights leaning gold: the silk the walls are
# hung with by day and by night, the gilding of the frames and the letters, the marble of the columns and the stair,
# the red carpet, the chandelier's crystal, the table's linen, the swords' steel, the mahogany of the rail, the
# chocolate of the cake; and the hand's own: one phosphor for every candle, one moon, and three skins.
RAMP = {
    "silk": ["#6E5A3E", "#93795A", "#B39C78", "#CDB993", "#DDCBA6", "#E8DAB8", "#F3EAD2"],    # champagne damask
    "wine": ["#12070C", "#1E0B13", "#240E18", "#2C121D", "#3A1826", "#4C2032", "#642C42"],    # the night's damask
    "gold": ["#3A1F0E", "#63360F", "#8E5A1A", "#B9852B", "#DDB04A", "#F2D77E", "#FFF3C2"],    # gilding
    "marble": ["#4B4650", "#6E6874", "#938D97", "#B5B0B6", "#D2CECF", "#E7E4E0", "#F7F5F0"],  # white marble
    "vein": ["#2E2A33", "#3F3A45", "#544E5B", "#6A6372", "#837C8A", "#9C96A3", "#B7B2BC"],    # its grey veins
    "carpet": ["#2E0610", "#4F0B16", "#74121E", "#9C1C26", "#C02E30", "#DA5440", "#EC8A68"],  # the red carpet
    "crystal": ["#34404C", "#52626F", "#758894", "#9BAFB8", "#C0D2D6", "#DDEBEB", "#F6FCFA"],  # cut crystal
    "linen": ["#57525E", "#78727F", "#9C96A0", "#BDB8BE", "#D8D4D5", "#EBE8E4", "#FAF8F3"],   # the tablecloth
    "steel": ["#262A35", "#3E4452", "#5C6372", "#7F8795", "#A4ABB7", "#C8CDD5", "#EEF1F4"],   # the swords
    "wood": ["#1F0B08", "#351309", "#4F1F10", "#6B2E19", "#8A4328", "#A9603E", "#C7855F"],    # mahogany
    "cocoa": ["#1C0D09", "#2E160F", "#452217", "#5E3120", "#7A452D", "#9A6142", "#BC8562"],   # the cake
    "cloth": ["#07090B", "#0E1114", "#16191D", "#20242A", "#2C3138", "#3B414A", "#4F565F"],   # a long black coat
    "hair": ["#0B0806", "#140F0B", "#1E1711", "#2A2018", "#372A20", "#46362A", "#584536"],
    "flame": MATRIX.ramp("flame"),                                                            # every candle
    "moon": MATRIX.ramp("moon"),
    "skin0": MATRIX.ramp("skin0"), "skin1": MATRIX.ramp("skin1"), "skin2": MATRIX.ramp("skin2"),
}

C = dict(
    white="#FFFFFF",
    paper=RAMP["silk"][5],                                  # the champagne silk the words sit on by day
    ink=MATRIX.body[0], body_night=MATRIX.body[1],          # the words by day and by night: the hand's
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses is a
# token here, in C, in a ramp or in the night (see TOKENS).
X = dict(
    muted_day=MATRIX.muted[0],         # small labels on the silk: the hand's
    muted_night=MATRIX.muted[1],       # and on the wine
    rule_day="#A87A2C", rule_night="#7A4A1C",
    dim_day="#CDB993", dim_night="#3A1826",
)

# --------------------------------------------------------------------------- the night
# The wine-dark silk from the top of a sheet to its foot: deepest at its head and foot, where the candles' light does
# not reach, and warmest across its middle. Every text colour of the night clears 4.5:1 on each band.
NIGHT_SKY = ["#1E0B13", "#240E18", "#2C121D", "#2C121D", "#240E18", "#1E0B13"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})

step, ramp_for = tones(RAMP)
