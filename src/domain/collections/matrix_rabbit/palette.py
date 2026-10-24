# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Rabbit set's palette: a storybook's spring page, pale yellow-green by day and a deep indigo garden by night,
the clipped hedge and its roses painted red, the playing cards, the white rabbit's fur, his jacket and waistcoat and
his gold watch, the old tree and its hole, and the closed set of every colour one of its files may use. The words'
inks, the phosphor every light burns on, the moon and the people's skin are the Matrix hand's (see
`collections.hand`)."""
from __future__ import annotations

from ...holidays.pixel.shade import tones
from ..hand import MATRIX

# Hand-set ramps, dark to light, shadows leaning purple and lights leaning gold: the page by day and the garden by
# night, the hedge, the roses and the red of the cards, the cards' paper and their black, the rabbit's fur and the
# pink of his ears, his tweed jacket, his blue waistcoat and his gold watch, the tree's bark, the earth of the hole,
# and the bottle's glass; and the hand's own: one phosphor for every light, one moon, and three skins.
RAMP = {
    "page": ["#6F7550", "#8B9268", "#A6AD82", "#BEC59A", "#CDD4A6", "#D8DFB2", "#E6ECC6"],      # the page by day
    "garden": ["#07061A", "#0C0A20", "#100D27", "#13102C", "#1A163A", "#231E4B", "#2F295F"],    # and by night
    "hedge": ["#0E2410", "#173518", "#224A22", "#2F612C", "#3F7A36", "#549442", "#70AD55"],     # the hedge
    "rose": ["#3D0510", "#64091A", "#8E1124", "#B81C2E", "#D93A40", "#EF6A62", "#FAA090"],      # roses, red cards
    "card": ["#4A4038", "#706458", "#988A7C", "#BDB0A2", "#DCD2C4", "#F2EBDF", "#FFFDF7"],      # the cards' paper
    "spade": ["#0D0C14", "#1A1824", "#2A2736", "#3C3849", "#504B5F", "#686277", "#857E94"],     # their black
    "fur": ["#55536A", "#7A788C", "#9F9DAE", "#C0BECB", "#DAD8E2", "#EDEBF2", "#FFFFFF"],       # the rabbit's fur
    "pink": ["#6A2A3A", "#93404F", "#B85A66", "#D57A80", "#E99CA0", "#F5BFC0", "#FCE0DE"],      # his ears and eyes
    "tweed": ["#2E2014", "#46321F", "#5F462C", "#7A5C3B", "#97764E", "#B39366", "#CCB085"],     # his jacket
    "blue": ["#101838", "#182451", "#22336C", "#304689", "#435BA3", "#5E77BB", "#8299CF"],      # his waistcoat
    "gold": ["#3E2A08", "#634510", "#8C661C", "#B38A2E", "#D4AE4A", "#EBCD74", "#FAE9A8"],      # his watch
    "bark": ["#1E140E", "#2E2017", "#412E21", "#56402E", "#6D543E", "#866C51", "#A08767"],      # the old tree
    "soil": ["#0E0806", "#1A100B", "#281A12", "#38261A", "#4A3424", "#5E4430", "#76583F"],      # the hole's earth
    "bottle": ["#0E2A30", "#164048", "#215862", "#2E727C", "#438E96", "#62AAB0", "#8EC6C8"],    # the little bottle
    "flame": MATRIX.ramp("flame"),                                                            # every light
    "moon": MATRIX.ramp("moon"),
    "skin0": MATRIX.ramp("skin0"), "skin1": MATRIX.ramp("skin1"), "skin2": MATRIX.ramp("skin2"),
}

C = dict(
    white="#FFFFFF",
    paper=RAMP["page"][5],                                  # the page's ground by day
    paper_n=RAMP["garden"][3],                              # and the garden's by night
    ink=MATRIX.body[0], body_night=MATRIX.body[1],          # the words by day and by night: the hand's
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses is a
# token here, in C, in a ramp or in the night (see TOKENS).
X = dict(
    muted_day=MATRIX.muted[0],         # the quieter words: the hand's
    muted_night=MATRIX.muted[1],
    rule_day="#8E9670", rule_night="#2E2858",
    dim_day="#C2C99C", dim_night="#1E1A40",
    shade="#1C1E10",                   # a shadow on the page, laid see-through
    shade_n="#05040F",                 # and on the night garden
)

# --------------------------------------------------------------------------- the night
# The garden from the top of a sheet to its foot by night: the indigo sky deepest overhead, a shade lighter low over
# the hedge, where the moon's light lies. Every text colour of the night clears 4.5:1 on each band.
NIGHT_SKY = ["#110E28", "#120F2A", "#13102C", "#13102C", "#14112D", "#15122F"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})

step, ramp_for = tones(RAMP)
