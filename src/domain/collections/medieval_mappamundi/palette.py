# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Mappa Mundi set's palette: its ramps of ink, parchment and the map's washes, the gilt and brass of the
navigator's table, its day and its night, and the closed set of every colour one of its files may use. The words'
inks, the wind heads' skin and the lantern's flame are the medieval hand's (see `collections.hand`)."""
from __future__ import annotations

from ...holidays.pixel.shade import tones
from ..hand import MEDIEVAL

# Ramps, dark to light: iron gall ink, the parchment, the map's washes (the sea in verdigris, the land in ochre,
# vermilion and the blues and violets of the legend), gilt and brass, the beasts' greens and slates, the wind
# heads' skin and the lantern's flame, both the hand's, and the same chart by night: the parchment, the sea and
# the land fallen dark round the lantern's light. Every colour a sprite takes is a tone on one of these.
RAMP = {
    "ink": ["#100B07", "#1C130B", "#2C2015", "#433122", "#5B4731", "#7A644B", "#9C8669"],
    "parch": ["#5E4628", "#806339", "#A3844F", "#C2A46C", "#D8C08A", "#E8D6A8", "#F5EBCD"],
    "sea": ["#1C3F38", "#2C5A4F", "#417766", "#5E9480", "#84B09C", "#B6CFB4", "#D3E3CF"],
    "land": ["#5A3F12", "#84601E", "#A9812E", "#C9A048", "#DDBA68", "#E6CD8E", "#F2E2B4"],
    "verm": ["#3E0C06", "#6A170C", "#962614", "#BC3A22", "#D65C3C", "#E88C6E", "#F4BEA8"],
    "gold": ["#3E2A06", "#6B4A0E", "#98701A", "#C0962A", "#DCB846", "#EDD47C", "#F9EDBA"],
    "green": ["#12260F", "#1D3B17", "#2B5321", "#3E6E2D", "#58893C", "#82A960", "#B3CC93"],
    "slate": ["#12171E", "#1F2731", "#313B47", "#485461", "#66727E", "#8D97A0", "#B9C0C6"],
    "skin": MEDIEVAL.ramp("skin0"),            # the hand's lightest skin, the wind heads' faces
    "blue": ["#0E1A3A", "#152A5E", "#1E3F86", "#2D58B0", "#4A78C8", "#7F9FDA", "#B8CBEE"],
    "violet": ["#22102E", "#381C4A", "#502A68", "#6B3D86", "#8A5CA2", "#AE88C0", "#D3BEDD"],
    "flame": MEDIEVAL.ramp("flame"),           # the hand's one flame, the lantern's
    "night": ["#0A0705", "#120D08", "#1B140C", "#251B10", "#312315", "#3F2D1A", "#4F3920"],
    "deep": ["#050B0A", "#08110F", "#0D1916", "#12221E", "#192D28", "#213A33", "#2C4A41"],
    "dusk": ["#0C0904", "#151007", "#1F180B", "#2A2010", "#372A15", "#46361B", "#574423"],
}

C = dict(
    white="#FFFFFF",
    paper=RAMP["parch"][5],          # the parchment by day
    sea="#C9D5B6",                   # the sea's verdigris wash, faded on the parchment
    land=RAMP["land"][5],            # the land's ochre wash
    ink=MEDIEVAL.body[0], body_night=MEDIEVAL.body[1],      # the hand's ink for the words, by day and by night
    sea_night=RAMP["deep"][3], land_night=RAMP["dusk"][3],
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses
# is a token here, in C, in a ramp or in the night (see TOKENS).
X = dict(
    muted_day=MEDIEVAL.muted[0],      # small labels on the parchment and the washes, in the hand's quieter ink
    muted_night=MEDIEVAL.muted[1],    # and by lantern light
    accent_day="#8C2614",      # the vermilion a day's accents are written in
    rule_day="#7A644B", rule_night="#6E5A3E",
    dim_day="#A8946E", dim_night="#3A2C1C",      # a chart's dotted guides
    shade_ink="#060403",       # see-through shadow
    grain="#5E4628",           # the parchment's grain and foxing, see-through
    wave="#6E8F78",            # the sea's fine wave lines, drawn in ink gone green
)

# --------------------------------------------------------------------------- the night
# The chart on the navigator's table from the top of a sheet to its foot: dark at the top and the foot where
# the lantern's light falls off, warmer through the middle. Every text colour of the night clears 4.5:1 on each
# band, on the sea and the land by night, and on the brightest of the lantern's pool.
NIGHT_SKY = ["#0C0805", "#130D08", "#1A130B", "#1F160D", "#1A130B", "#130D08"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})

step, ramp_for = tones(RAMP)
