# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Illuminated set's palette: the pigments of a scriptorium, its vellum by day and by candlelight, and
the closed set of every colour one of its files may use. Its words, its flames and its people's skin are the
collection's hand's (`collections.hand`)."""
from __future__ import annotations

from ...holidays.pixel.shade import make_ramp, tones
from ..hand import MEDIEVAL as HAND

# Hand-set ramps, dark to light: the illuminator's pigments and gold leaf, the vellum they are laid on, the
# iron-gall ink the text is written in, and the wood and wool of the scriptorium; and the hand's, the candle's
# flame and the three skins its people are painted in, light to dark. Every colour a sprite takes is a tone on
# one of these.
RAMP = {
    "gold": ["#3E2606", "#6B4309", "#98650F", "#C68A1A", "#E3AE38", "#F2D06E", "#FAECC0"],
    "oxblood": ["#2A0608", "#4C0A0E", "#731117", "#9A1A1F", "#BF3A33", "#DB6D5C", "#F0B09B"],
    "lapis": ["#070E2E", "#0E1B52", "#162B78", "#1F3F9E", "#3A62C0", "#6E93DB", "#B3C8F0"],
    "verdigris": ["#06231F", "#0C3B35", "#15564D", "#1F7366", "#3A9484", "#6DB8A6", "#B0DBCF"],
    "redlead": ["#4A1604", "#7A2608", "#A83B0E", "#D0561A", "#E97A33", "#F5A269", "#FBCDA8"],
    "tyrian": ["#1E0A26", "#361344", "#4F1D63", "#6A2B83", "#8A4AA3", "#AC78C2", "#D3B0DF"],
    "vellum": ["#5A4426", "#86683E", "#B08F5C", "#D1B682", "#E8D4A8", "#F3E6C8", "#FBF3E0"],
    "ink": ["#120C08", "#1F150E", "#2E2016", "#423023", "#5B4635", "#7A6250", "#9C8572"],
    "wood": ["#1C100A", "#36200F", "#553318", "#744923", "#956434", "#B4844E", "#D4A978"],
    "habit": ["#1A120C", "#2E2117", "#453324", "#5E4734", "#785E48", "#937961", "#B49C83"],
    "ash": ["#1E1B1A", "#38332F", "#544D47", "#726A62", "#938A80", "#B5ACA2", "#D8D0C6"],
}
RAMP["slate"] = make_ramp("#566273")
RAMP.update({name: HAND.ramp(name) for name in ("flame", "skin0", "skin1", "skin2")})

C = dict(
    white="#FFFFFF", paper="#EBDFC2", ruling="#E0D0AD", prick="#C6B188", ruling_n="#342316",
    ink=HAND.body[0], gold=RAMP["gold"][4], red=RAMP["oxblood"][3], blue=RAMP["lapis"][3], green=RAMP["verdigris"][3],
    slate="#566273",
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses
# is a token here, in C, in a ramp or in the night's vellum (see TOKENS).
X = dict(
    muted_day=HAND.muted[0],  # small labels on the day vellum, the hand's quieter ink
    muted_night=HAND.muted[1],  # and on the vellum by night
    body_night=HAND.body[1],  # text by night, the hand's
    accent_day="#8E1A1F",     # the rubric red, letters on the day vellum
    accent_night="#F2D06E",   # gold letters on the candlelit vellum
    rule_day="#B0523A",       # a rubric line by day
    rule_night="#C9775A",     # a rubric line by night
    dim_day="#E0D3B4", dim_night="#4A3320",    # a chart's dotted guides
    node_night="#3A2614",     # a card's face by night
    shade_ink="#1A0E06",      # see-through shadow
    yellow="#E8C53A",         # a live badge's yellow, an orpiment ink, so it stands apart from the gold label
)

# --------------------------------------------------------------------------- the vellum by night
# The scriptorium after dark, in bands from the top of a drawing to its foot: near black at the edges and a
# deep warm brown toward the middle, CIELAB lightness 5 at the edges to 13, where the candles' light reaches;
# each candle lays its own pool of light round it (see `art.candlelight`).
NIGHT_SKY = ["#170F09", "#1B120A", "#1F150C", "#23180D", "#271A0F", "#2D1E10", "#271A0F", "#23180D", "#1F150C",
             "#1B120A", "#170F09"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})

step, ramp_for = tones(RAMP)
