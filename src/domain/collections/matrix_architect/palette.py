# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Architect set's palette: the warm white room by day and its grey-black by night, the charcoal plastic of the
televisions and the dark glass of their screens, the white leather of the chair, the console's steel, the pen's brass
and the red enamel of the console's switches, and the closed set of every colour one of its files may use. The words'
inks, the phosphor every screen burns on, the moon and the people's skin are the Matrix hand's (see
`collections.hand`)."""
from __future__ import annotations

from ...holidays.pixel.shade import tones
from ..hand import MATRIX

# Hand-set ramps, dark to light, their shadows leaning purple and their lights leaning gold: the room's walls by day
# and by night, the televisions' charcoal plastic and the pale grey of the frame's, the dark glass of their tubes, the
# chair's white leather, the console's steel, the brass of the pen and the red enamel of its switches; and the
# hand's own: one phosphor for every screen, one moon, three skins.
RAMP = {
    "wall": ["#6F675A", "#968D7D", "#B8B0A0", "#D2CBBC", "#DCD5C7", "#E7E1D4", "#F4F0E6"],     # the room by day
    "dusk": ["#050706", "#0A0D0C", "#0C100E", "#0F1412", "#121815", "#1B2420", "#26322C"],     # the room by night
    "plastic": ["#0E0F13", "#17191E", "#212429", "#2C3037", "#3B4048", "#50565F", "#6B727C"],  # the sets' cases
    "shell": ["#6A6B72", "#83858B", "#9DA0A5", "#B7B9BC", "#CFD0D0", "#E2E2DF", "#F2F2EE"],    # the frame's sets
    "glass": ["#020806", "#040D09", "#06120C", "#0A1A12", "#0E2419", "#143323", "#1D4630"],    # their tubes
    "leather": ["#5E5650", "#857B73", "#A89E94", "#C6BDB2", "#DDD6CC", "#ECE7DF", "#F8F6F1"],  # the white chair
    "steel": ["#22252B", "#363A42", "#4E535C", "#6A7079", "#8B919A", "#AFB4BB", "#D3D6DA"],    # the console
    "suit": ["#3F4350", "#5A5F6E", "#7A7F8E", "#9DA1AE", "#BEC1CB", "#DADCE2", "#EEEFF2"],     # his pale grey suit
    "brass": ["#3A2A10", "#5E4416", "#866320", "#AE862E", "#D1AA45", "#E8CB73", "#F7E7AE"],    # the pen's clip
    "signal": ["#2A0A0E", "#4A1016", "#701B20", "#97282A", "#BB3B36", "#D65E4D", "#EA8E76"],   # red enamel
    "flame": MATRIX.ramp("flame"),                                                             # every screen
    "moon": MATRIX.ramp("moon"),
    "skin0": MATRIX.ramp("skin0"), "skin1": MATRIX.ramp("skin1"), "skin2": MATRIX.ramp("skin2"),
}

C = dict(
    white="#FFFFFF",
    paper=RAMP["wall"][5],                                  # the warm white the words sit on by day
    ink=MATRIX.body[0], body_night=MATRIX.body[1],          # the words by day and by night: the hand's
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses is a
# token here, in C, in a ramp or in the night (see TOKENS).
X = dict(
    muted_day=MATRIX.muted[0],         # small labels on the wall: the hand's
    muted_night=MATRIX.muted[1],       # and in the dark
    rule_day="#9C9384", rule_night="#2F4A3C",
    dim_day="#D2CBBC", dim_night="#1B2420",
)

# --------------------------------------------------------------------------- the night
# The room from the top of a sheet to its foot: darkest at its head and foot, and palest across its middle where the
# screens' light falls. Every text colour of the night clears 4.5:1 on each band.
NIGHT_SKY = ["#0C100E", "#0F1412", "#121815", "#121815", "#0F1412", "#0C100E"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})

step, ramp_for = tones(RAMP)
