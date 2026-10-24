# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Subway set's palette: the station's glazed tile, pale celadon by day and teal-black after hours, the mosaic's
terracotta, ochre and cobalt, the train's stainless steel, the tunnel's dark, the platform's concrete and its yellow
line, the bench's oak, the long dark coat, and the closed set of every colour one of its files may use. The words'
inks, the phosphor every light burns on, the moon and the people's skin are the Matrix hand's (see
`collections.hand`)."""
from __future__ import annotations

from ...holidays.pixel.shade import tones
from ..hand import MATRIX

# Hand-set ramps, dark to light: the wall's celadon glaze, the mosaic's terracotta, ochre, cobalt and bottle green,
# the train's stainless steel, the dark of the tunnel, the platform's concrete and its safety yellow, the bench's oak,
# the long coat's black wool, the clock's white enamel and a red summer dress; and the hand's own: one phosphor for
# every light, one moon, and three skins.
RAMP = {
    "glaze": ["#4D7A70", "#67968B", "#82B0A5", "#9FC9BE", "#B9DCD2", "#CFE8E0", "#E4F3EE"],   # the wall's tile
    "terra": ["#3E1308", "#64220F", "#8C3418", "#B24A24", "#CC6A3A", "#E08F5E", "#EFB48C"],   # the mosaic
    "ochre": ["#4A3208", "#74510F", "#9E721A", "#C49428", "#DDB246", "#ECCD78", "#F6E3AE"],
    "cobalt": ["#0C1A40", "#13296A", "#1C3D96", "#2A55BD", "#4574D6", "#729AE6", "#A8C2F2"],
    "bottle": ["#06231A", "#0B3627", "#124B36", "#1B6247", "#287C5B", "#43987A", "#72B79E"],
    "steel": ["#272D33", "#3F474F", "#5A646D", "#7B858E", "#9DA6AE", "#C1C8CD", "#E0E5E8"],   # the train
    "tunnel": ["#020505", "#040A0A", "#071010", "#0B1717", "#101F1F", "#172929", "#213636"],
    "concrete": ["#3F3D3A", "#5A5752", "#75716B", "#918C85", "#ACA79F", "#C6C1B9", "#DEDAD3"],
    "yellow": ["#4A3906", "#79600B", "#A78414", "#D2AA21", "#E9C63C", "#F4DB76", "#FBEDB2"],
    "oak": ["#2C1B10", "#462F1B", "#634528", "#815D36", "#9E7848", "#B99461", "#D2B183"],
    "coat": ["#08090B", "#0F1114", "#171A1F", "#21252B", "#2D3239", "#3C424A", "#50575F"],
    "enamel": ["#6C7470", "#8E9690", "#B0B7B1", "#CDD3CD", "#E2E7E1", "#F0F3EE", "#FBFCFA"],   # the clock's face
    "dress": ["#2E0811", "#510E1C", "#7A1525", "#A41E2C", "#C83236", "#DE5A4E", "#EE8A74"],     # a summer dress
    "flame": MATRIX.ramp("flame"),                                                             # every light
    "moon": MATRIX.ramp("moon"),
    "skin0": MATRIX.ramp("skin0"), "skin1": MATRIX.ramp("skin1"), "skin2": MATRIX.ramp("skin2"),
}

C = dict(
    white="#FFFFFF",
    tile="#C9E4DA", tile_lit="#D5EBE3", grout="#B4CCC3",                # the wall by day
    tile_n="#0C1D1E", tile_lit_n="#0E2224", grout_n="#081415",          # and after hours
    ink=MATRIX.body[0], body_night=MATRIX.body[1],                       # the words by day and by night: the hand's
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses is a
# token here, in C, in a ramp or in the night (see TOKENS).
X = dict(
    muted_day=MATRIX.muted[0],         # small labels on the tile: the hand's
    muted_night=MATRIX.muted[1],       # and by night
    rule_day="#7E9C93", rule_night="#24403C",
    dim_day="#A9C4BB", dim_night="#15302C",
    shade_ink="#030707",               # see-through shadow
    glasses="#050608",                 # dark glasses
)
TILE_W, TILE_H = 8, 4       # a tile of the wall, its grout beyond it, laid in a running bond
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in X.values()})

step, ramp_for = tones(RAMP)
