# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Forge set's palette: its ramps, its named colours and its night plate, and the closed set of every
colour one of its files may use.

The design is drawn in the medieval collection's hand (see `collections.hand`): its words take the hand's two inks,
the forge's fire, its coals, its embers and its sparks burn on the hand's flame, the smith's skin is on the hand's
skin, and the hammered plate its words sit on falls within the hand's bands, a cool slate by day and the forge's
dark by night."""
from __future__ import annotations

from ...holidays.pixel.shade import tones
from ..hand import MEDIEVAL

# Hand-set ramps, dark to light. The metals are cool and blued; the hot iron runs from ember red through flame
# yellow to white heat; the leather, the oak and the hearth's stone are warm. The fire is the hand's flame, and the
# smith's skin the hand's skin. Every colour a sprite takes is a tone on one of these.
RAMP = {
    "iron": ["#0A0C12", "#161A24", "#242A38", "#363E4F", "#4D5668", "#6B7587", "#8E99AB"],
    "steel": ["#2B3444", "#3F4A5D", "#596578", "#788496", "#9AA6B6", "#BCC7D4", "#E2EAF2"],
    "coal": ["#06070A", "#0E1015", "#171A22", "#22262F", "#2F3440", "#424857", "#5B6272"],
    "ember": ["#2A0503", "#520C05", "#861A08", "#BC300C", "#E85A14", "#FF8A2A", "#FFB55E"],
    "flame": ["#3E1E04", "#7A3F08", "#B8710E", "#EDA21A", "#FFCC33", "#FFE57A", "#FFF7D6"],
    "brass": ["#2E1E06", "#5C3E0C", "#8C6414", "#B98A22", "#DCAD3C", "#F0CC6A", "#FAE8B0"],
    "leather": ["#1A0D08", "#331A10", "#4F2A18", "#6E3E22", "#8E5630", "#AE7446", "#CE9A6C"],
    "oak": ["#1C1208", "#36240F", "#553A18", "#765426", "#987038", "#B99052", "#D8B47C"],
    "stone": ["#15110E", "#29231D", "#40372E", "#584D41", "#716456", "#8C7E6E", "#A99B8A"],
    "skin": MEDIEVAL.ramp("skin1"),                 # the smith's face and arms: the hand's skin
    "green": ["#06281A", "#0C4A2D", "#146B41", "#1B8A52", "#2FAA68", "#5FC98A", "#A6E6BE"],
    "blue": ["#07192F", "#0E2E58", "#174A86", "#2366B3", "#3E86D4", "#74ABE8", "#B7D4F5"],
    "purple": ["#22103A", "#3B1D62", "#57308B", "#7446AE", "#9263CB", "#B48CE0", "#D8C0F2"],
    "water": ["#0F1A24", "#1B2E3E", "#2A4659", "#3C6178", "#557F98", "#7FA4BA", "#B4CCDA"],
    "fire": MEDIEVAL.ramp("flame"),                 # the forge's fire, its coals, its embers and its sparks
}

# The sheet's own colours: the slate plate by day, the words' inks (the hand's), the rules, and the few flat colours
# the badges and the buttons need.
C = dict(
    white="#FFFFFF",
    plate="#AEBAC8",                                               # the hammered plate by day, a cool slate, L* 75
    ink=MEDIEVAL.body[0], muted_day=MEDIEVAL.muted[0], accent_day="#5C1203", rule_day="#4A5461",
    body_night=MEDIEVAL.body[1], muted_night=MEDIEVAL.muted[1], rule_night="#6E5C50",
    fill_day="#D7DFE7", fill_night="#242A38", dim_day="#919CAA", dim_night="#3A2C26",
    lapis="#1F55CC",                                               # the blue enamel a badge may be written in
)

# The night plate, lit from below by the forge: five bands from the dark at the top to the warmth at the
# foot, L* 4.4 to 15.7, within the hand's night. Every text colour of the night clears 4.5:1 on each of them.
NIGHT_SKY = ["#0E0F14", "#15121A", "#211820", "#2F1E1B", "#382215"]

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses
# is a token here, in C, in a ramp or in the night plate (see TOKENS).
X = dict(
    dent_lo="#8D98A6", dent_wall="#BBC7D4", dent_hi="#D6DFEA",          # a dent's hollow, its lit wall and its rim
    grain_lo="#A6B0BF",                                                  # the brushed grain of the day plate
    dent_n_lo="#06070B", dent_n_wall="#171A22", dent_n_hi="#2A2E39",    # the dents in the dark upper plate by night
    grain_n="#111319",
    dent_w_lo="#241410", dent_w_wall="#3A2419", dent_w_hi="#55382A",    # and in the warm lower plate
    grain_w="#33201A",
    shade_ink="#07060A",                           # see-through shadow
    steam="#E6EDF3",                               # the quench bucket's steam
    smoke="#8A8E99",                               # the chimney's smoke
    heat="#FF6A1A",                                # the light a hot thing throws on what stands near it
)

# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})

step, ramp_for = tones(RAMP)
