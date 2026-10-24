# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Oracle set's palette: a 1999 kitchen's apricot wallpaper by day and its warm dark by night, its oak trim and
glazed tiles, the almond oven and the cookies baking in it, and the closed set of every colour one of its files may
use. The words' inks, the phosphor every light burns on, the moon and the people's skin are the Matrix hand's (see
`collections.hand`)."""
from __future__ import annotations

from ...holidays.pixel.shade import tones
from ..hand import MATRIX

# Hand-set ramps, dark to light: the wallpaper by day and by night, the oak trim and the cabinets, the tiles' glaze
# and their blue, the almond enamel of the oven, the steel of the cooktop, the tray and the spoon, the cookie dough
# and its chocolate, the red of the mug and the curtains, the sunflowers and their leaves, the child's saffron robe,
# the black cat, the day sky through the window; and the hand's own: one phosphor for every light, one moon, and
# three skins. Every colour a sprite takes is a tone on one of these.
RAMP = {
    "paper": ["#7A4A3E", "#9C6450", "#BE8466", "#D8A27E", "#E8BC98", "#F3D3B2", "#FAE6CF"],   # apricot wallpaper
    "umber": ["#0E0709", "#170D0D", "#21140F", "#2B1B13", "#382418", "#4A3220", "#5E422C"],   # the same by night
    "oak": ["#2A140C", "#43220F", "#633617", "#874D20", "#A8692E", "#C68A47", "#DDAE6E"],     # trim and cabinets
    "glaze": ["#5B5246", "#857A68", "#ABA08A", "#C9BEA5", "#DFD6C0", "#EDE6D4", "#F8F4EA"],   # the tiles' cream
    "blue": ["#1B2440", "#283760", "#384D80", "#4E679E", "#6D86B8", "#93A8CF", "#BECDE5"],    # and their blue
    "enamel": ["#3F392E", "#5E5646", "#7F7660", "#A0977E", "#BFB69C", "#D8D0B8", "#ECE7D8"],  # the almond oven
    "steel": ["#1C2028", "#2E343F", "#454D5A", "#616A77", "#838C98", "#AAB2BC", "#D3D9DE"],
    "dough": ["#4A220F", "#6C3616", "#8F4F1E", "#B26D2A", "#CD8E3E", "#E2B062", "#F0CF92"],   # the cookies
    "choc": ["#1C0C08", "#2B140D", "#3C1E12", "#4F2918", "#663622", "#80462D", "#9C5B3C"],    # their chips
    "red": ["#3A0E12", "#5C161A", "#821F22", "#A42C2A", "#C2443A", "#D86A56", "#EA9A84"],     # mug and curtains
    "sun": ["#5C3408", "#83520C", "#A97412", "#CB961C", "#E3B52E", "#F1CE57", "#F9E494"],     # sunflowers
    "leaf": ["#132A16", "#1D3F20", "#29562B", "#386F37", "#4C8846", "#69A35C", "#93C383"],
    "robe": ["#451A0A", "#6B2A0E", "#913D14", "#B5541C", "#D17028", "#E5924A", "#F2B87A"],    # saffron
    "cat": ["#0C0911", "#151019", "#1F1824", "#2A2230", "#372D3E", "#483C50", "#5D4F66"],     # black fur
    "sky": ["#5E7486", "#7891A3", "#94ACBC", "#AFC4D1", "#C7D8E2", "#DCE8EE", "#EEF5F7"],     # through the window
    "flame": MATRIX.ramp("flame"),                                                            # every light
    "moon": MATRIX.ramp("moon"),
    "skin0": MATRIX.ramp("skin0"), "skin1": MATRIX.ramp("skin1"), "skin2": MATRIX.ramp("skin2"),
}

C = dict(
    white="#FFFFFF",
    paper=RAMP["paper"][5],                                 # the wallpaper's ground by day, L* 86
    ink=MATRIX.body[0], body_night=MATRIX.body[1],          # the words by day and by night: the hand's
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses is a
# token here, in C, in a ramp or in the night (see TOKENS).
X = dict(
    muted_day=MATRIX.muted[0],          # quieter words: the hand's
    muted_night=MATRIX.muted[1],
    rule_day="#9C6450", rule_night="#5E422C",
    dim_day="#E3C3A2", dim_night="#33221A",
    accent_day="#7A2A1C",               # a label's red-brown, 6.9:1 on the wallpaper
    steam="#FFF8EE",                    # the cookies' steam and the mug's
    far_day="#BFC4A2", far_stripe="#ADB38F",   # the room beyond the doorway, papered in sage
)

# --------------------------------------------------------------------------- the night
# The wallpaper by night from the top of a sheet to its foot: darkest under the ceiling and warming toward the floor,
# L* 6 to 11, within the hand's night. Every text colour of the night clears 4.5:1 on each band.
NIGHT_SKY = ["#1C110E", "#1F130F", "#22150F", "#25170F", "#281A12"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})

step, ramp_for = tones(RAMP)
