# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Hovercraft set's palette: the pale rust-grey concrete of a sewer tunnel lit by the ship's floodlights by day
and the tunnel's black by night, the riveted steel of the frame and the ship's hull, the scuffed plate the title is
stencilled on and its paint, the brick, the rust, the water, and the machine that comes out of the drain with its
red eyes; and the closed set of every colour one of its files may use. The words' inks, the phosphor every light
burns on, the moon and the people's skin are the Matrix hand's (see `collections.hand`)."""
from __future__ import annotations

from ...holidays.pixel.shade import tones
from ..hand import MATRIX

# Hand-set ramps, dark to light: the tunnel's concrete by day and its dark by night, the gunmetal of the frame and
# the hull, the pale steel of the title's plate, the stencil paint, rust, brick, the water by day, the machine's
# iron and its red eyes; and the hand's own: one phosphor for every light, one moon, and three skins. Every colour a
# sprite takes is a tone on one of these.
RAMP = {
    "concrete": ["#5E534C", "#7A6E66", "#968980", "#AFA297", "#C1B4A8", "#CDC1B5", "#DDD3C8"],  # by day
    "tunnel": ["#060607", "#09090A", "#0C0C0E", "#101012", "#16161A", "#1F1F24", "#2A2A30"],    # by night
    "steel": ["#14171C", "#22272E", "#343A43", "#4A515B", "#646C76", "#858D96", "#AAB1B8"],     # frame and hull
    "plate": ["#4C5664", "#68727F", "#848E9A", "#9CA6B2", "#B0BAC6", "#C3CBD4", "#D8DEE4"],     # the title's plate
    "drab": ["#1E2212", "#2C321A", "#3C4424", "#4E5830", "#636E3E", "#7C8752", "#99A26E"],      # stencil paint
    "rust": ["#3A1A0E", "#5A2A14", "#7A3C1A", "#9A5024", "#B66A34", "#CC8A50", "#DDAA76"],
    "brick": ["#2E140E", "#4A2016", "#682E1E", "#844028", "#9E5636", "#B6704A", "#CA8E68"],
    "water": ["#141A16", "#1D2620", "#28332B", "#344238", "#435246", "#566556", "#6E7C6C"],     # by day
    "iron": ["#0E0C12", "#1A1720", "#282430", "#383242", "#4A4356", "#5E566C", "#766E84"],      # the machine
    "eye": ["#3A0608", "#600A0E", "#8C1216", "#B81E1E", "#E03A30", "#F2705C", "#FCA894"],       # its eyes
    "flame": MATRIX.ramp("flame"),                                                             # every light
    "moon": MATRIX.ramp("moon"),
    "skin0": MATRIX.ramp("skin0"), "skin1": MATRIX.ramp("skin1"), "skin2": MATRIX.ramp("skin2"),
}

C = dict(
    white="#FFFFFF",
    paper=RAMP["concrete"][5],                              # the tunnel's concrete by day, L* 79
    plate_night="#171C22",                                  # the title's plate in the dark, L* 10
    ink=MATRIX.body[0], body_night=MATRIX.body[1],          # the words by day and by night: the hand's
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses is a
# token here, in C, in a ramp or in the night (see TOKENS).
X = dict(
    muted_day=MATRIX.muted[0],          # quieter words: the hand's
    muted_night=MATRIX.muted[1],
    rule_day="#7A6E66", rule_night="#343A43",
    dim_day="#B9AC9F", dim_night="#1A1A1E",
    accent_day="#5A2A14",               # a label's rust, 6.7:1 on the concrete
    drop="#BFD6D0",                     # a drop of water catching the light
)

# --------------------------------------------------------------------------- the night
# The tunnel by night from the top of a sheet to its foot: black under the vault, a breath lighter toward the water,
# L* 3.3 to 6, within the hand's night. Every text colour of the night clears 4.5:1 on each band.
NIGHT_SKY = ["#0C0C0D", "#0D0D0F", "#0E0E10", "#0F0F11", "#121214"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})

step, ramp_for = tones(RAMP)
