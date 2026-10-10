# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Chessmen set's palette: its ramps of walrus ivory and its patina, bone stained red, the oak of the board
and the hall, the hearth's fire and its smoke, stone, iron, leather and gilt, the stains a piece may take, its day
and its night, and the closed set of every colour one of its files may use.

The design is drawn in the medieval collection's hand (see `collections.hand`): its words take the hand's two inks,
its fires burn on the hand's flame ramp, and the ivory and the wool its words sit on by day fall within the hand's
band, a polished cream rather than a glare."""
from __future__ import annotations

from ...holidays.pixel.shade import tones
from ..hand import MEDIEVAL

# Hand-set ramps, dark to light. Walrus ivory runs from the brown of a deep cut to the cream of a polished face, and
# its patina from the dark of the oldest hollow to the pale honey of a worn edge; the red is bone stained with
# madder, as half the pieces once were; the hall is the dark of a Norse hall at night, warmest nearest its fire.
# The stains are the dyes a carver had (woad, weld, verdigris, sloe and madder), each soaked into ivory. The fire of
# the hearth, the lamp and the candle is the hand's flame. Every colour a sprite takes is a tone on one of these.
RAMP = {
    "ivory": ["#4A331A", "#6E5132", "#957651", "#B99C73", "#D6BF97", "#EADAB9", "#F9F1E0"],     # walrus ivory
    "honey": ["#3D2508", "#5E3D0E", "#835A17", "#A57724", "#C2963B", "#DAB767", "#EDD9A1"],     # its patina
    "stain": ["#330B07", "#53140E", "#771F15", "#992E1F", "#B84631", "#D27156", "#E9A78F"],     # bone stained red
    "oak": ["#1A1109", "#291B0F", "#3B2816", "#523920", "#6B4C2C", "#87653B", "#A6814F"],       # board, posts, bench
    "hall": ["#090604", "#100B07", "#17100B", "#20160F", "#2B1E14", "#39281B", "#4B3524"],      # the hall by night
    "fire": MEDIEVAL.ramp("flame"),                                                               # the hand's flame
    "smoke": ["#2A2623", "#3B3632", "#504A45", "#67605A", "#817A73", "#9E978F", "#BFB9B1"],
    "stone": ["#1F1D1A", "#312E2A", "#46423C", "#5E5951", "#79736A", "#968F84", "#B7B1A6"],     # kerb and kist
    "iron": ["#101113", "#1B1D20", "#292C30", "#3C4045", "#53585E", "#70767C", "#969CA3"],
    "leather": ["#22130A", "#361E10", "#4F2F19", "#6A4125", "#875733", "#A6754A", "#C4996D"],   # the purse
    "gilt": ["#392707", "#5F420F", "#866019", "#AC8127", "#C9A141", "#E0C372", "#F2E2AC"],      # the horn's mounts
    "woad": ["#0D1A33", "#162B52", "#21407A", "#30599E", "#4E78BA", "#82A2D2", "#BDCDE8"],
    "weld": ["#3A2F07", "#5B4A0C", "#806A14", "#A48A20", "#C2AA3A", "#D9C76C", "#ECE1A8"],
    "verd": ["#0C2A1C", "#13402B", "#1C5B3E", "#287953", "#40986C", "#72B794", "#B0D8C0"],
    "sloe": ["#1B0F20", "#2C1833", "#402449", "#583462", "#734F7D", "#957599", "#C0A7C2"],
    "wall": ["#4E3E2B", "#634F37", "#7A6345", "#8E7553", "#A08562", "#B29673", "#C3A884"],     # the hall's planks
    "wool": ["#8C7B5E", "#B3A182", "#CDBD9C", "#DCCDAE", "#E6D9BC", "#EBE0C7", "#F6EEDB"],     # the hanging
}

C = dict(
    white="#FFFFFF",
    paper="#E9DEC7",                         # the polished ivory every sheet is by day, L* 88.8
    ink=MEDIEVAL.body[0], ink_n=MEDIEVAL.body[1],   # the words by day and by night: the hand's
    fill="#E9E1CE", fill_n="#241911",        # a card's face
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses is a
# token here, in C, in a ramp or in the night (see TOKENS).
X = dict(
    grain="#DFD0B2", sheen="#EFE8D8",        # the grain of the tusk, a shade under and over the polish
    crack="#D5C29D",                         # the craquelure of old ivory
    muted_day=MEDIEVAL.muted[0], muted_night=MEDIEVAL.muted[1],   # small labels by day and by night: the hand's
    accent_day="#8A2A1C", accent_night="#E6A55A",  # SECTION A-A, arrows and checks: madder, and firelight
    rule_day="#B8A07A", rule_night="#5A4632",
    dim_day="#D8C7A5", dim_night="#3A2C20",  # a chart's dotted guides
    shade_ink="#0A0604",                     # see-through shadow
    glint="#FFFBEF",                         # the light along a carving
    ember="#FF6A1A",                         # the hearth's light on the edge of a letter by night
    kist="#D8D2C6", kist_fleck="#CCC5B8",    # the kist's front slab, a pale stone flecked a shade darker
    kist_night="#2B2824", kist_fleck_n="#33302B",   # and by night
)

# --------------------------------------------------------------------------- the night
# The ivory by night from the top of a sheet to its foot: a dark hall, a little warmer toward the floor the hearth
# stands on. The hearth's own warmth is laid over it from the side it burns on (see `art.hearthlight`). Every text
# colour of the night clears 4.5:1 on each band and on the warmest of that light.
NIGHT_SKY = ["#140E0A", "#150F0A", "#17100B", "#18110C", "#1A120D"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})

step, ramp_for = tones(RAMP)
