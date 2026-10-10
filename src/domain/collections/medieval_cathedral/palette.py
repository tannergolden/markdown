# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Cathedral set's palette: its ramps of glass, stone, lead and candlelight, its day and its night, and the
closed set of every colour one of its files may use. Its words and its candles' flames are the collection's hand's
(`collections.hand`)."""
from __future__ import annotations

from ...holidays.pixel.shade import tones
from ..hand import MEDIEVAL as HAND

# Hand-set ramps, dark to light. The glass ramps are the colours a window is glazed in, each from the tone it
# takes against the lead to the tone where the glass runs thin and the light comes through; the stone is pale
# limestone by day and the same stone by candlelight at night; the lead is dull and dark. Every colour a sprite
# takes is a tone on one of these.
RAMP = {
    "stone": ["#3A352E", "#5E584F", "#807A6F", "#A39D90", "#C3BDB0", "#DDD8CC", "#F2EEE5"],      # tracery by day
    "dusk": ["#120E0B", "#1E1711", "#2C2219", "#3C2F22", "#4E3E2E", "#63503C", "#7A654C"],       # by candlelight
    "lead": ["#08080A", "#151518", "#232327", "#36363B", "#4D4D54", "#6A6B73", "#8A8B94"],       # the cames
    "ruby": ["#3A0710", "#64101C", "#961A27", "#C42634", "#E04448", "#F27A74", "#FFB9AE"],
    "cobalt": ["#0A1640", "#13276A", "#1D3E9A", "#2A5AC4", "#4A80DE", "#7EAAEE", "#BBD3F7"],
    "emerald": ["#06301A", "#0C4D2A", "#146B3A", "#1E8C4A", "#36AE60", "#6CCB86", "#B0E5BC"],
    "amber": ["#4A2A04", "#7C4A08", "#B0700E", "#D9951A", "#F2B82E", "#FBD86A", "#FFF0B8"],
    "violet": ["#2A0F3A", "#471B5E", "#672A86", "#883DAC", "#A75ECB", "#C590E0", "#E2C5F0"],
    "gold": ["#4E3206", "#7E560C", "#B07E16", "#D9A626", "#F3C84A", "#FBE084", "#FFF5CF"],       # halos and crowns
    "grisaille": ["#6E7A7A", "#8E9A99", "#AEB9B6", "#C9D2CE", "#DDE4E0", "#ECF1EE", "#FAFCFA"],  # white glass
    "candle": HAND.ramp("flame"),                                                               # the flames
    "flesh": ["#4A2A1E", "#7A4A34", "#A86E4E", "#CF9470", "#E5B48F", "#F2CFB0", "#FBE8D6"],      # the saints' faces
    "umber": ["#1E120A", "#36220F", "#523618", "#704C24", "#8E6634", "#AE864E", "#CEAA78"],      # oak, hair and the owl
    "sky": ["#0B1020", "#13203C", "#1F3660", "#345A8E", "#5E8BC0", "#9FC2E4", "#DCEBF7"],  # through the glass
}

C = dict(
    white="#FFFFFF",
    paper="#E7DCCD", came="#C0BBB5",                   # the grisaille quarries by day, warm as stone in the sun,
    #                                                    and the lead between them, pale with the light behind
    paper_n="#2B2118", came_n="#08080A",               # the same panes lit from inside by night, the lead black
    ink=HAND.body[0], ink_n=HAND.body[1],              # the words, in the hand's inks
    fill="#F0EAE1", fill_n="#3A2D22",                  # a card's face
    ruby=RAMP["ruby"][3], cobalt=RAMP["cobalt"][3], emerald=RAMP["emerald"][3], amber=RAMP["amber"][3],
    violet=RAMP["violet"][3], lead=RAMP["lead"][0],
)
# The glass a title's letters, a garland's roundels and a release's beads are glazed in, by turns.
GLAZES = ("ruby", "cobalt", "emerald", "amber")

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses is
# a token here, in C, in a ramp or in the night (see TOKENS).
X = dict(
    muted_day=HAND.muted[0],   # small labels on the day glass, the hand's quieter ink
    muted_night=HAND.muted[1],  # and on the night glass
    rule_day="#9B958D", rule_night="#6B5A47",
    dim_day="#D1C8BC", dim_night="#4A3B2E",            # a chart's dotted guides
    accent_day="#8E1B1B",                              # SECTION A-A, arrows and checks by day
    shade_ink="#07060A",                               # see-through shadow
    sun="#FFF2C0",                                     # the sunbeam
    tint_sky="#DCD9CF", tint_warm="#ECE0CB", tint_cool="#E9D8C9",   # the day panes' casts, one quarry to the next
    pane_warm="#332618", pane_dim="#241B14",                        # the night panes' casts
    star="#F4EFE0", star_dim="#8C8070",
)

# --------------------------------------------------------------------------- the night
# The window by night from the top of a sheet to its foot: dim where the candlelight does not reach, warmest
# toward the foot where the candles stand.
NIGHT_SKY = ["#1F1813", "#271E16", "#2B2118", "#2D2319"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})
# The pixels a candle's light falls on: the stone of the tracery, the sill and the altar.
STONE = set(RAMP["stone"]) | set(RAMP["dusk"])

step, ramp_for = tones(RAMP)
