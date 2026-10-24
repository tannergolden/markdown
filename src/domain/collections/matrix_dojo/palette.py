# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Dojo set's palette: the shoji's paper and its kumiko of pale hinoki by day, the same paper by night lit from
behind by the city, black lacquer and gold leaf, the tatami and its brocade edge, the fighters' training clothes,
and the closed set of every colour one of its files may use. The words' inks, the phosphor every light burns on,
the moon and the people's skin are the Matrix hand's (see `collections.hand`)."""
from __future__ import annotations

from ...holidays.pixel.shade import tones
from ..hand import MATRIX

# Hand-set ramps, dark to light: the shoji's honey paper and the hinoki its kumiko are cut from by day, the paper by
# night with the city's blue behind it, black lacquer with its red-brown depth and gold leaf, the tatami's rush and
# the shimenawa's straw, the shide's white paper and the foam of the painted wave, the fighters' training clothes and
# their hair, the stone lantern's granite, the dark wood of the round window's frame, the cherry's petals, the red of
# the painted sun and the paper lantern's tassel, the sky through the round window, and the persimmon, wisteria and
# moss a badge's colours are dyed in; and the hand's own: one phosphor for every light, one moon, and three skins.
RAMP = {
    "paper": ["#6B5838", "#907B57", "#B4A07A", "#D1BE98", "#E8D9B6", "#EFE3C6", "#F8F0DC"],   # the shoji by day
    "hinoki": ["#46331E", "#6A4F31", "#8F6E48", "#B38F63", "#C9AA7E", "#D9C49C", "#EADCBC"],  # its kumiko
    "washi": ["#08091A", "#0D0F24", "#11152D", "#151B35", "#1C2442", "#27315A", "#384676"],   # the paper by night
    "lacquer": ["#0B0606", "#150B0A", "#201210", "#2C1A16", "#3C2620", "#523A30", "#6E5244"],  # black lacquer
    "gold": ["#3E2706", "#6A470F", "#98701D", "#C49C33", "#E0BE55", "#F1D98B", "#FCF0C6"],    # gold leaf
    "tatami": ["#2E3214", "#454B20", "#60672F", "#7C8441", "#98A058", "#B4BA78", "#D2D6A2"],   # the rush, green-gold
    "straw": ["#4A3A18", "#6D5829", "#91793D", "#B39A56", "#CCB473", "#DFCB93", "#EFE2BC"],    # the shimenawa
    "shide": ["#5C6070", "#80869A", "#A6ACBE", "#C8CCD8", "#E2E4EA", "#F2F3F5", "#FFFFFF"],    # paper streamers
    "gi": ["#0B0C11", "#13151C", "#1C1F28", "#282C37", "#373C49", "#4B515F", "#666D7C"],       # a dark training gi
    "indigo": ["#0A0D1C", "#10162C", "#18213E", "#222E53", "#2F3E6A", "#435485", "#5F72A3"],   # the opponent's
    "hair": ["#0A0807", "#130F0C", "#1D1712", "#29211A", "#372C23", "#47392E", "#5A493B"],
    "stone": ["#25282B", "#383C40", "#4F5458", "#686D70", "#83888A", "#A0A4A3", "#C0C3BF"],    # the lantern's granite
    "wood": ["#1C110B", "#2C1B11", "#3F2819", "#553722", "#6E4A2F", "#8B6141", "#AA7D58"],     # the window's frame
    "sakura": ["#561F33", "#82334B", "#AD5068", "#D07C8C", "#E7A3AE", "#F4C8CE", "#FDE6E8"],   # cherry petals
    "red": ["#420C09", "#6C1610", "#99241A", "#C23623", "#DE5639", "#EF8866", "#F9BFA4"],      # the painted sun
    "sky": ["#4C627A", "#66809A", "#86A0B6", "#A8C0D0", "#C4D8E2", "#DCE8EC", "#EEF4F2"],      # through the window
    "kaki": ["#3F1A06", "#67290A", "#91390E", "#BA4E14", "#DB6A23", "#EE9150", "#F8BC8A"],     # persimmon
    "fuji": ["#1E1230", "#311D4C", "#472B6B", "#5F3D8A", "#7A55A6", "#9776BF", "#B9A0D8"],     # wisteria
    "moss": ["#0D1F14", "#153120", "#1F4830", "#2A6141", "#3A7C55", "#54986D", "#7CB58E"],     # moss on stone
    "flame": MATRIX.ramp("flame"),                                                             # every light
    "moon": MATRIX.ramp("moon"),
    "skin0": MATRIX.ramp("skin0"), "skin1": MATRIX.ramp("skin1"), "skin2": MATRIX.ramp("skin2"),
}

C = dict(
    white="#FFFFFF",
    paper=RAMP["paper"][5],                                 # the shoji's paper by day
    kumiko=RAMP["hinoki"][5],                               # and the lattice laid over it
    ink=MATRIX.body[0], body_night=MATRIX.body[1],          # the words by day and by night: the hand's
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses is a
# token here, in C, in a ramp or in the night (see TOKENS).
X = dict(
    muted_day=MATRIX.muted[0],         # small labels on the paper: the hand's
    muted_night=MATRIX.muted[1],       # and by night
    rule_day="#A08A62", rule_night="#3A4366",
    dim_day="#D6C6A2", dim_night="#1F2747",
    kumiko_night="#090B1C",            # the lattice by night, a silhouette against the lit paper
    shade_ink="#070509",               # see-through shadow
)

# --------------------------------------------------------------------------- the night
# The paper by night from the top of a sheet to its foot: darkest under the beam, and paling toward the floor as the
# city's light comes up behind it. Every text colour of the night clears 4.5:1 on each band.
NIGHT_SKY = ["#0D0F24", "#0F1228", "#11152D", "#131831", "#151B35", "#171F39"]
PANE_W, PANE_H = 26, 18     # a pane of the shoji between its kumiko, in units
PANE_X, PANE_Y = 9, 4       # where the first kumiko lies, across and down
GLOW = (2, 2, 0.08)         # by night, how far in from its kumiko a pane's glow begins, across and down, and how strong


def _blend(a: str, b: str, t: float) -> str:
    """Colour `a` with `b` laid over it at opacity `t`, as a browser lays it."""
    ca, cb = (tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in (a, b))
    return "#%02X%02X%02X" % tuple(round(u + (v - u) * t) for u, v in zip(ca, cb))


# Each band of the night across the middle of a pane, the city's glow through the paper: what a word's backing is
# painted in there, so it matches the paper round it.
NIGHT_GLOW = [_blend(c, RAMP["washi"][6], GLOW[2]) for c in NIGHT_SKY]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY + NIGHT_GLOW} | {c.upper() for c in X.values()})

step, ramp_for = tones(RAMP)
