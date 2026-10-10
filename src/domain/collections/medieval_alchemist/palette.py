# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Alchemist set's palette: its ramps of limewash, oak, brass, lead, gold, glass and the elixirs, its day
and its night, and the closed set of every colour one of its files may use. The words' inks, the fire of every
flame and the people's skin are the medieval hand's (see `collections.hand`)."""
from __future__ import annotations

from ...holidays.pixel.shade import tones
from ..hand import MEDIEVAL

# Ramps, dark to light: the limewashed wall by day and by night, the dark oak of the shelves and the bench, brass,
# lead and gold, clear glass and the elixirs it holds, the fire every flame burns with, and the things of the
# laboratory (bone and parchment, the people's skin, a beard, the crocodile's hide, iron and clay, the night sky
# through the window, and the ultramarine ground from lapis). The fire and the skin are the hand's; the rest are
# set by hand. Every colour a sprite takes is a tone on one of these.
RAMP = {
    "lime": ["#6B6150", "#8E846F", "#AFA58E", "#CBC2AB", "#DED6C3", "#E7E1D3", "#F8F5EC"],      # the wall by day
    "dusk": ["#0C0B10", "#141219", "#1D1A23", "#28242F", "#36313E", "#47414F", "#5B5464"],      # and by night
    "oak": ["#1A110A", "#2A1D12", "#3D2C1B", "#523D26", "#6A5133", "#866943", "#A68858"],       # shelves, bench
    "brass": ["#3A280C", "#634512", "#8E6A1E", "#B8902C", "#D8B24A", "#ECD27C", "#F9EDB8"],     # brackets, sphere
    "lead": ["#1E2128", "#2C3039", "#3E434D", "#525863", "#686E79", "#828893", "#A2A7AF"],      # the base metal
    "gold": ["#5A3804", "#8A5A08", "#B88414", "#DEAA24", "#F4C843", "#FCE07C", "#FFF5C4"],      # and the noble one
    "glass": ["#28363A", "#435459", "#677C80", "#91A7A8", "#B9CDCB", "#D9E8E5", "#F3FBF9"],     # clear glass
    "green": ["#062A1A", "#0B442D", "#11613E", "#1A824F", "#2EA865", "#62CA89", "#AEE8C0"],     # the green elixir
    "violet": ["#22103A", "#391A5C", "#552985", "#713FAD", "#9262CB", "#B792E2", "#DFCCF3"],    # the violet
    "red": ["#380A0A", "#601313", "#8C1E1B", "#B62F25", "#D8523E", "#EE866F", "#F9C3B4"],       # cinnabar, wax
    "blue": ["#091D3D", "#112E64", "#1B458E", "#2860B8", "#4485D6", "#7EAEEA", "#C4DBF7"],      # azure
    "amber": ["#3E2204", "#6A3A08", "#99560E", "#C47718", "#E39A2C", "#F4BE62", "#FCE2AE"],     # amber, honey
    "fire": MEDIEVAL.ramp("flame"),      # every flame: the furnace, the lamps, the candles and the lantern
    "bone": ["#4C402F", "#73644A", "#9A8969", "#BDAC89", "#D8CAA8", "#EBE1C7", "#F9F4E6"],      # skull, parchment
    "skin": MEDIEVAL.ramp("skin0"),      # the alchemist's and the homunculus's skin, the hand's lightest
    "skin1": MEDIEVAL.ramp("skin1"),     # and its other two, for the alchemists of a roster
    "skin2": MEDIEVAL.ramp("skin2"),
    "ash": ["#38383C", "#58585E", "#7C7C82", "#A1A1A5", "#C3C3C5", "#DFDFDE", "#F6F6F3"],       # beards, smoke
    "croc": ["#1A1F0D", "#2C3315", "#434B1F", "#5C642B", "#78803B", "#989D56", "#C1C383"],      # the crocodile
    "iron": ["#111113", "#1D1E22", "#2B2D32", "#3C3F45", "#52565D", "#6D7279", "#8E939A"],      # tripods, doors
    "clay": ["#2C1610", "#4A2618", "#6C3A24", "#8E5134", "#AE6E4A", "#C99068", "#E2B696"],      # the athanor
    "sky": ["#04071A", "#090F2E", "#111A46", "#1A2964", "#2A4386", "#4A6BAE", "#8CABDA"],       # through the window
    "lapis": ["#0E1640", "#1A2770", "#24369A", "#3350C8", "#5470DA", "#869CE8", "#C3CEF5"],     # ultramarine
}

C = dict(
    white="#FFFFFF",
    paper=RAMP["lime"][5],                   # the limewashed wall by day
    ink=MEDIEVAL.body[0], ink_n=MEDIEVAL.body[1],     # the words by day and by night, in the hand's ink
    fill="#F7F2E6", fill_n="#26222C",        # a card's face
)
# The elixirs a vessel, a release or a link is filled with, by turns.
ELIXIRS = ("green", "violet", "amber", "red", "blue")

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses is a
# token here, in C, in a ramp or in the night (see TOKENS).
X = dict(
    muted_day=MEDIEVAL.muted[0], muted_night=MEDIEVAL.muted[1],   # small labels, in the hand's quieter ink
    accent_day="#7A1C16",                          # SECTION A-A, arrows and checks by day: cinnabar
    rule_night="#5C5262",                          # a rule on the night wall
    dim_day="#CBC2AB", dim_night="#3A3440",        # a chart's dotted guides
    shade_ink="#0A0806",                           # see-through shadow
    sun="#FFF3C8",                                 # the shaft of sun from the round window
    star="#F4F0E0", star_dim="#8E8AA0",            # the stars through the window
    glint="#FFFDF2",                               # the light on glass and on gold
)

# --------------------------------------------------------------------------- the night
# The wall by night from the top of a sheet to its foot, deep shadow between the flasks' glows, warming a little
# toward the foot where the furnace burns. Every text colour of the night clears 4.5:1 on each band.
NIGHT_SKY = ["#141219", "#15131A", "#17141B", "#19151B", "#1B161B"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})

step, ramp_for = tones(RAMP)
