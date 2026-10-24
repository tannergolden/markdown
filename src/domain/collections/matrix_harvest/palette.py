# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Harvest set's palette: an ashen lavender sky by day and a black-purple storm by night over the fields where
the machines grow us, the ribbed black conduit and its cables, the dark metal of the towers, the pods' caps and the
harvester, the glass, the harvester's red eyes, the copper of the cables' cores; and the closed set of every colour
one of its files may use. The words' inks, the phosphor every light burns on (the fluid in the pods and the titles'
tubes, and the lightning), the moon and the people's skin are the Matrix hand's (see `collections.hand`)."""
from __future__ import annotations

from ...holidays.pixel.shade import tones
from ..hand import MATRIX

# Hand-set ramps, dark to light: the ashen sky by day and the storm by night, the conduit's black rubber, the dark
# metal of the towers and the machines, the glass of the pods and the tubes, the harvester's eyes, the copper of the
# cables' cores and the pods' contacts; and the hand's own: one phosphor for every light, one moon, and three skins.
# Every colour a sprite takes is a tone on one of these.
RAMP = {
    "ash": ["#4E4660", "#675E7A", "#837A96", "#9E95B0", "#B6ADC6", "#C9C0D6", "#DDD6E6"],      # the sky by day
    "storm": ["#0E0913", "#130D19", "#191121", "#22172D", "#2E2040", "#3E2C55", "#53406C"],    # and by night
    "conduit": ["#08070B", "#110F16", "#1B1822", "#26222F", "#332E3E", "#433D50", "#575066"],  # black rubber
    "metal": ["#121018", "#1E1B26", "#2C2836", "#3C3748", "#4F495C", "#655E73", "#7E778C"],    # towers, machines
    "glass": ["#1E3A33", "#2E5248", "#466E62", "#6A8F82", "#94B2A6", "#BCD2C8", "#E2EEE8"],    # pods and tubes
    "eye": ["#3A0608", "#600A0E", "#8C1216", "#B81E1E", "#E03A30", "#F2705C", "#FCA894"],      # the machine's eyes
    "copper": ["#2A120E", "#45200F", "#663013", "#8A421A", "#A85622", "#C87A3A", "#E0A062"],   # cable cores
    "flame": MATRIX.ramp("flame"),                                                            # every light
    "moon": MATRIX.ramp("moon"),
    "skin0": MATRIX.ramp("skin0"), "skin1": MATRIX.ramp("skin1"), "skin2": MATRIX.ramp("skin2"),
}

C = dict(
    white="#FFFFFF",
    paper=RAMP["ash"][5],                                   # the ashen sky by day, L* 79
    ink=MATRIX.body[0], body_night=MATRIX.body[1],          # the words by day and by night: the hand's
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses is a
# token here, in C, in a ramp or in the night (see TOKENS).
X = dict(
    muted_day=MATRIX.muted[0],          # quieter words: the hand's
    muted_night=MATRIX.muted[1],
    rule_day="#675E7A", rule_night="#3E2C55",
    dim_day="#B6ADC6", dim_night="#22172D",
    accent_day="#3D2A55",               # a label's deep violet, 7.2:1 on the sky
    haze_day="#D3CCDF",                 # the far fields' haze by day
    pod_ink="#0A1A12",                  # initials lettered on a pod's glowing fluid: an ink no other word takes
)

# --------------------------------------------------------------------------- the night
# The storm by night from the top of a sheet to its foot: black-purple under the clouds, warming a little toward
# the far fields, L* 4.5 to 10, within the hand's night. Every text colour of the night clears 4.5:1 on each band.
NIGHT_SKY = ["#130D19", "#160F1D", "#191121", "#1C1325", "#1F1529"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})

step, ramp_for = tones(RAMP)
