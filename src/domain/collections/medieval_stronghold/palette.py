# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Stronghold set's palette: its ramps, its stone and its heraldic tinctures, the hand's flame and moon, its
night, and the closed set of every colour one of its files may use."""
from __future__ import annotations

from ...holidays.pixel.shade import tones
from ..hand import MEDIEVAL

# Hand-set ramps, dark to light: shadows lean cool, lights lean warm, as dressed stone does under the sun
# and the moon. Every torch, window and dragon's breath burns on the collection's one flame, and the moon is the
# collection's moon (see `collections.hand`). Every colour a sprite takes is a tone on one of these.
RAMP = {
    "stone": ["#2A241F", "#4A433B", "#6B6358", "#8D8577", "#AFA796", "#CFC8B8", "#EBE6DA"],   # limestone by day
    "slate": ["#0E131C", "#1A2230", "#2A3447", "#3E4A60", "#56657E", "#7A89A3", "#A7B4C9"],   # the same stone, moonlit
    "gold": ["#4A2A06", "#7D4E0A", "#B37D10", "#E2A91A", "#FFD23F", "#FFE98C", "#FFFBE3"],    # or: gold leaf and brass
    "gules": ["#3A0810", "#5E0C18", "#8E1B1B", "#B9252A", "#D9453F", "#EE7068", "#FFB8AD"],   # gules: heraldic red
    "azure": ["#0C1A3A", "#15295C", "#1F3F86", "#2A5AB4", "#3F7BD6", "#79A8EC", "#BFD6F7"],   # azure: heraldic blue
    "vert": ["#0C2A14", "#174A22", "#237032", "#2E9641", "#4FB85A", "#86D483", "#C4EDBF"],    # vert: heraldic green
    "purpure": ["#2A0E3A", "#471A5E", "#652885", "#8438AC", "#A35BCB", "#C48BE0", "#E3C4F2"], # purpure
    "argent": ["#4A5260", "#6E7786", "#95A0AE", "#B9C2CD", "#D6DDE5", "#EDF1F5", "#FFFFFF"],  # argent: silver and white
    "iron": ["#0B0C10", "#17191F", "#25282F", "#363A43", "#4A505A", "#646B77", "#8A929E"],    # blackened iron
    "wood": ["#1E120A", "#3A2414", "#5C3B1F", "#7E552E", "#A0743F", "#C29A5E", "#E0C590"],    # oak
    "grass": ["#1F3312", "#33521C", "#4A7326", "#639433", "#7FB244", "#A6D063", "#D4EB9F"],
    "earth": ["#2B2016", "#443325", "#5E4A36", "#7A6349", "#967D5F", "#B29B7A", "#D1BE9E"],   # the hill's rock
    "water": ["#0A2238", "#113A5C", "#1A567F", "#2676A5", "#3F9BC9", "#7CC4E4", "#C2E8F6"],   # the moat
    "tenne": ["#5A1E05", "#9A3A08", "#D4621A", "#F28C28", "#FFB84D", "#FFDD8C", "#FFF6DC"],   # tenne, a badge's orange
    "flame": MEDIEVAL.ramp("flame"),                                                          # torchlight
    "moon": MEDIEVAL.ramp("moon"),
    "cloud": ["#A9A092", "#C0B8AB", "#D6D0C4", "#E8E3DA", "#F3F0EA", "#FAF8F4", "#FFFFFF"],
    "dragon": ["#0B1A12", "#14301F", "#1E4A2E", "#2A6540", "#3C8454", "#5EA874", "#95CBA3"],
}

C = dict(
    white="#FFFFFF",
    paper="#D6CFC0", mortar="#B9B09F", lit="#E6E1D5", shade="#C7BFAE",       # the ashlar by day
    paper_n="#1B2431", mortar_n="#121A26", lit_n="#273243", shade_n="#17202C",   # and by moonlight
    ink=MEDIEVAL.body[0], ink_n=MEDIEVAL.body[1],                              # the words, in the hand's ink
    fill="#F0EADC", fill_n="#2A3447",
    gules=RAMP["gules"][2], gold=RAMP["gold"][3], azure=RAMP["azure"][2], vert=RAMP["vert"][2],
    iron=RAMP["iron"][1],
)
# The tinctures a pennant, a flag or a shield comes in, by turns: gules, or, azure, argent.
TINCTURES = ("gules", "gold", "azure", "argent")

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses
# is a token here, in C, in a ramp or in the night (see TOKENS).
X = dict(
    recess="#5A5246",         # the floor of a carved letter by day, a shade lighter than the cut's shaded wall
    muted_day=MEDIEVAL.muted[0],      # small labels on the day stone, in the hand's quieter ink
    muted_night=MEDIEVAL.muted[1],    # and on the night stone
    dim_day="#BDB4A3", dim_night="#2E3A4E",    # a chart's dotted guides
    star_faint="#3A4660", star_dim="#5A6A88", star_pale="#DCE6F7",
    shade_ink="#070A10",      # see-through shadow
    sky_wash="#C9D6EA",       # see-through moonlight on an edge
    oak_day="#E2C593", oak_day_grain="#D2B47E", oak_day_lit="#EED9B0",     # the inn sign's smoothed planks by day
    oak_night="#3A2414", oak_night_grain="#301D10", oak_night_lit="#4A2F1A",
)

# --------------------------------------------------------------------------- the night
# The night stone from the top of a sheet to its foot: moonlit above, darker below, every band within the hand's
# night.
NIGHT_SKY = ["#1D2736", "#1B2431", "#18202C"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})
# The pixels a torch's light falls on: the stone of the castle and the hill; and the water it shivers on.
STONE = set(RAMP["stone"]) | set(RAMP["slate"]) | set(RAMP["earth"])
WATER = set(RAMP["water"])

step, ramp_for = tones(RAMP)
