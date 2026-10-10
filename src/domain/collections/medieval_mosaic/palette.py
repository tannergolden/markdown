# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Mosaic set's palette: its ramps of gold and lapis tesserae, the glass and stone of the mosaic's figures,
bronze, its day and its night, the hand's lamplight and skin, and the closed set of every colour one of its files may
use."""
from __future__ import annotations

from ...holidays.pixel.shade import tones
from ..hand import MEDIEVAL

# Hand-set ramps, dark to light. The gold ground is laid in tesserae of close burnished golds, each tile catching the
# light at its own angle, warmer in its shadows and paler in its lights as gold is; the night's vault is tesserae of
# deep lapis; the figures are laid in glass of the peacock's blues and greens, the jewels' red and green, imperial
# purple, and stones (white marble, porphyry, grey marble, serpentine), with bronze for the lamps that hang in the dark.
# The lamps burn on the collection's flame and the court's faces and hands are on its three skins (see `hand`). Every
# colour a sprite takes is a tone on one of these.
RAMP = {
    "tile": ["#A67842", "#C09658", "#D0A866", "#D7B26E", "#DEBB76", "#E5C681", "#EFD594"],      # the gold ground
    "gold": ["#4E3106", "#7C520C", "#A87816", "#CF9C28", "#E7BB42", "#F4D474", "#FDEDB8"],      # gold in figures
    "lapis": ["#060B22", "#0A1230", "#0E1A40", "#142356", "#1E3274", "#30509E", "#5E80C8"],     # vault, letters
    "azure": ["#0B2A55", "#13407A", "#1E5AA0", "#2F78C0", "#4F98D8", "#86BCE8", "#C6E0F6"],     # wave, water, neck
    "teal": ["#05302E", "#0A4A46", "#11665E", "#1C8478", "#36A393", "#6CC4B2", "#B4E6D8"],      # the peacock's train
    "green": ["#0A2A16", "#124226", "#1B5E36", "#257A46", "#389A5A", "#68BC80", "#AEDDBA"],     # emerald, leaves
    "red": ["#3A0A0C", "#641216", "#8E1C1F", "#B42A28", "#D3483C", "#EA7D6C", "#F8BCAE"],       # garnet, roof tiles
    "porphyry": ["#24101A", "#3E1A2C", "#5A2640", "#763252", "#93466A", "#B46E8C", "#DAA8BC"],  # the imperial stone
    "purple": ["#1E0A2C", "#341248", "#4E1C68", "#6A2A88", "#8A46A8", "#B07ACA", "#DCC0EA"],    # robes, grapes
    "pearl": ["#5E5A54", "#837E76", "#A6A097", "#C6C0B6", "#DFDAD0", "#EFEBE3", "#FBF9F4"],     # marble, pearls
    "stone": ["#2E2E33", "#48484F", "#66666D", "#86868C", "#A6A6AA", "#C6C6C8", "#E4E4E3"],     # grey marble
    "earth": ["#3A2410", "#5C3A1A", "#7E5226", "#A06C36", "#BE8A4E", "#D6AA72", "#EACCA0"],     # wood, ochre, wings
    "bronze": ["#2A1606", "#4A280C", "#6E3E14", "#93571E", "#B6752E", "#D39A4E", "#ECC488"],    # the lamp crowns
    # the tiles of the vault by night, a lapis quieter than the letters' so the sky behind the words stays calm
    "vault": ["#0B0D22", "#0F162F", "#141C3A", "#1A2345", "#232B50", "#2F3760", "#414976"],
    "flame": MEDIEVAL.ramp("flame"),                                                            # lamplight
    **{f"skin{i}": MEDIEVAL.ramp(f"skin{i}") for i in range(3)},                                # faces and hands
}

C = dict(
    white="#FFFFFF",
    ink=MEDIEVAL.body[0], ink_n=MEDIEVAL.body[1],     # the words by day and by night, in the hand's ink
    fill="#FBF6E8", fill_n="#141C3C",                  # a card's face
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses is a
# token here, in C, in a ramp or in the night (see TOKENS).
X = dict(
    outline=RAMP["lapis"][0],  # the row of dark tesserae every figure is set round with: the deepest lapis glass
    muted_day=MEDIEVAL.muted[0],      # small labels by day, in the hand's quieter ink
    muted_night=MEDIEVAL.muted[1],    # and by night
    accent_day="#1A2B6A",      # SECTION A-A, arrows and checks by day: lapis
    rule_day="#6E4A10", rule_night="#8A6A24",          # a rule: a line of dark tesserae, or of gold by night
    dim_day=RAMP["tile"][1], dim_night="#2A3A6A",      # a chart's dotted guides
    shade_ink="#0A0612",       # see-through shadow
    glint="#FFF8E0",           # the light a tile of gold throws back
)

# --------------------------------------------------------------------------- the night
# The vault by night from the top of a sheet to its foot: deep lapis, a shade deeper overhead, in the hand's band of the
# night. Every text colour of the night clears 4.5:1 on each band, on every tile laid over it and under the lamps'
# pools.
NIGHT_SKY = ["#0B122E", "#0D1430", "#0F1632", "#111733", "#121935"]
# The gold field the tiles calm to behind a word by day, so no grout and no glint lies under a letter.
CALM = RAMP["tile"][4]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})

step, ramp_for = tones(RAMP)
