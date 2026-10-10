# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Independence Day set's palette: its ramps, its named colours and its sky, and the closed set of every
colour one of its files may use."""
from __future__ import annotations

from ..pixel.shade import tones

# Hand-set ramps, dark to light: shadows lean toward the evening blue, lights toward the gold of a
# sparkler. The flag's own red and blue sit in the middle of theirs. Every colour a sprite takes is
# a tone on one of these.
RAMP = {
    "red": ["#3A0710", "#650C1A", "#8E1426", "#B22234", "#D8434F", "#F07C7F", "#FFC2BE"],
    "navy": ["#050A1C", "#0C1737", "#152759", "#1F3A7A", "#3358A3", "#5E84C7", "#A6C1EA"],
    "cloth": ["#232A3A", "#4E586F", "#838DA5", "#B6BFD1", "#DCE2EC", "#F1F4F8", "#FFFFFF"],
    "gold": ["#4A2F05", "#7D5409", "#B38310", "#E0AE1C", "#FFD447", "#FFE992", "#FFFBE5"],
    "ember": ["#3F1405", "#6E2508", "#A33C0C", "#D65A12", "#F27D2A", "#FFA95E", "#FFD9AE"],
    "green": ["#0B2210", "#143D1B", "#1E5A27", "#2B7A34", "#45A047", "#78C46A", "#BCE8A8"],
    "wood": ["#170D09", "#2B1911", "#452A1B", "#654028", "#8A5A38", "#B07E55", "#D6AB82"],
    "bronze": ["#1E150B", "#3A2A16", "#5A4222", "#7C5E33", "#A07F4B", "#C4A56F", "#E6D0A2"],
    "coal": ["#04060B", "#0A0F1A", "#141B2B", "#212A40", "#343F5A", "#4F5B7A", "#76819F"],
    # The kit's slate, its shadows leaning toward the evening blue like the rest.
    "slate": ["#17182B", "#24253C", "#383E53", "#566273", "#A5B6C3", "#E6F8FF", "#F0FDFF"],
}

C = dict(
    white="#FFFFFF", paper="#F4F6FA", grid="#D8DFEA", grid_n="#14203C",
    ink="#0E1A38", coal="#0A0F1A", navy=RAMP["navy"][3], red=RAMP["red"][3], gold=RAMP["gold"][4],
    green=RAMP["green"][2], ember=RAMP["ember"][4], slate="#566273",
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a
# file uses is a token here, in C, in a ramp or in the night sky (see TOKENS).
X = dict(
    muted_day="#4B5875",      # small labels on the day paper
    muted_night="#9DADCF",    # small labels on the night sky
    body_night="#EEF2FA",     # text by night
    accent_day="#B22234",     # red letters on the day paper: the flag's own red
    accent_night="#FF8A8A",   # red letters on the night sky
    dim_day="#E2E8F1", dim_night="#1B2746",    # a chart's dotted guides
    star_faint="#2A3658", star_dim="#46557E", star_pale="#E4ECFF",
    moonlit="#7C8FC4",        # the night's blue light along a silhouette's edge
    shade_ink="#030611",      # see-through shadow
    node_night="#101B38",     # a card's face by night
    night_rule="#7F9BD8",     # rules by night
    flag_red_night="#E4505B",  # a title's red stripes by night, light enough to read on the sky
    violet="#6A2C7E",         # a Purple Heart's violet: only a badge written in purple takes it
)

NIGHT_SKY = ["#03060F", "#060B1A", "#0A1124", "#0E1830", "#13203D"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})
# The lawn's greens: only these take a shadow, a sparkler's light pooled on the grass or a firework's.
GROUND = {RAMP["green"][1], RAMP["green"][2], RAMP["green"][3], RAMP["green"][4]}

step, ramp_for = tones(RAMP)
