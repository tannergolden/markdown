# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Hoard set's palette: its ramps of chalk, sandstone, frost, the great stones, hoard gold, garnet, the
dragon's scales, its ember breath and the snow at the barrow's mouth, its day and its night, and the closed set
of every colour one of its files may use. The words' inks, the breath's ember and the moon are the medieval
hand's (see `collections.hand`)."""
from __future__ import annotations

from ...holidays.pixel.shade import tones
from ..hand import MEDIEVAL

# Hand-set ramps, dark to light. The barrow's chamber is walled in chalk laid dry, its flints in it, a warm pale
# stone lit cold by the snow at its mouth and warmer still by the gold; its great stones are grey and carved; the
# hoard is red gold set with garnets, after the cloisonne of the ship burial; the dragon is the blue of deep shadow,
# its belly and its horns old ivory, its breath an ember on the hand's flame; the moon is the hand's; and the night
# outside the mouth is blue over the snow. Every colour a sprite takes is a tone on one of these.
RAMP = {
    "chalk": ["#60554D", "#81756A", "#A3978A", "#C2B7AA", "#D9CFC1", "#E6DDD0", "#F3EDE3"],     # the wall by day
    "sand": ["#5C5141", "#7E705A", "#A19174", "#C2B293", "#D8CBAF", "#E7DDC8", "#F3EEE3"],      # its sandstone
    "flint": ["#16191E", "#23272E", "#343941", "#4A5058", "#656B74", "#868C94", "#ABB0B6"],     # flint nodules
    "frost": ["#2E4A68", "#45668A", "#6587AA", "#8DAAC6", "#B8CDE0", "#DCE8F2", "#F6FAFD"],     # ice and snow
    "stone": ["#25262A", "#37393E", "#4D5056", "#666A70", "#83878C", "#A3A6AA", "#C6C8CB"],     # the great stones
    "earth": ["#0F0C0B", "#191412", "#251D19", "#332822", "#44362D", "#59483B", "#73604E"],     # the barrow floor
    "gold": ["#4A2606", "#77410B", "#A56313", "#CF8B1F", "#EBB23A", "#F8D46E", "#FFF0BC"],      # hoard gold
    "garnet": ["#2B0410", "#4F0719", "#760C24", "#9E1430", "#C42540", "#E05B6C", "#F2A0AA"],    # the cut garnets
    "drake": ["#0B0D1E", "#16203F", "#223566", "#2F4C8C", "#4268B0", "#6890CC", "#A3BEE6"],     # the dragon's scales
    "wing": ["#140B24", "#24133F", "#371E5C", "#4C2C7A", "#633F96", "#8362B3", "#AD94D2"],      # its wings
    "bone": ["#3B3125", "#5F5240", "#86775D", "#AE9F80", "#CDC0A2", "#E4DAC3", "#F6F1E5"],      # belly, horns
    "ember": MEDIEVAL.ramp("flame"),                                                            # its breath
    "moon": MEDIEVAL.ramp("moon"),                                                              # the moon
    "smoke": ["#26282F", "#3A3D46", "#535661", "#6E717C", "#8D909A", "#B2B4BB", "#D8D9DD"],     # its smoke
    "night": ["#05070F", "#0A0E1C", "#10172C", "#18233F", "#243455", "#344A70", "#4E6890"],     # the night outside
    "iron": ["#111215", "#1C1E22", "#2A2D33", "#3C4048", "#53585F", "#6E737B", "#8F949B"],      # bands, the helm
    "silver": ["#3A3E44", "#575C63", "#787D85", "#9BA0A7", "#BCC0C6", "#D9DCE0", "#F1F3F5"],    # tinned bronze, blades
    "oak": ["#1C130B", "#2E1F10", "#443016", "#5C421F", "#775729", "#946F38", "#B38D51"],       # the chest's lid
    "glass": ["#081538", "#0E245E", "#173788", "#2250B0", "#3A6DCC", "#6F97DF", "#AFC6F0"],     # blue glass inlay
    "amber": ["#3B1D03", "#673306", "#954E0C", "#C06B15", "#DE8F28", "#EFB45B", "#FADBA3"],     # amber beads
    "emerald": ["#04261A", "#073D2A", "#0C5A3E", "#167A53", "#24A06D", "#5DC596", "#A6E5C8"],   # an emerald
}

C = dict(
    white="#FFFFFF",
    ink=MEDIEVAL.body[0], ink_n=MEDIEVAL.body[1],      # the words by day and by night: the hand's
    fill="#F8F7F3", fill_n="#1E1916",                  # a card's face
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses is a
# token here, in C, in a ramp or in the night (see TOKENS).
X = dict(
    muted_day=MEDIEVAL.muted[0], muted_night=MEDIEVAL.muted[1],    # small labels by day and by night: the hand's
    accent_day="#861027",                              # SECTION A-A, arrows and checks by day: garnet
    accent_night="#F4C55A",                            # and by night: gold
    rule_day="#A6A29A", rule_night="#5B4D42",          # the rules
    dim_day="#C9CDD1", dim_night="#3A322C",            # a chart's dotted guides
    speck_n="#18131A", flint_n="#08090C", rim_n="#18171D",  # the chalk's grain and its flints by night
    shade_ink="#07060A",                               # see-through shadow
    glint="#FFFBEA",                                   # light on gold and ice
)

# --------------------------------------------------------------------------- the night
# The barrow by night from the top of a sheet to its foot: deep shadow under the lintel, warming a little toward
# the floor where the hoard lies, and never darker than the hand's night. Every text colour of the night clears
# 4.5:1 on each band.
NIGHT_SKY = ["#0F1016", "#101015", "#111014", "#121113", "#141112", "#151211", "#171311"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})

step, ramp_for = tones(RAMP)
