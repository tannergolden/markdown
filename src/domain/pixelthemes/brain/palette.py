# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The brain theme's palette: the lab's sage tiles, petrol enamel, brass and steel, the brain's tissue, the jar's
fluid, the nixie tubes' amber and the lightning's violet, and the closed set of every colour one of its files may
use."""
from __future__ import annotations

from ...holidays.pixel.shade import tones

# Hand-set ramps, dark to light. By day the lab is lit by its lamps from the upper left; by night its lamps are out,
# and the jar's fluid, the nixie tubes and the lightning light it.
RAMP = {
    "tissue": ["#34081C", "#651335", "#98244B", "#C93E63", "#E86E86", "#F7A2AE", "#FFD7DB"],    # the brain
    "fluid": ["#04282A", "#08474A", "#0D6C6C", "#169591", "#2FBFB2", "#74E2D2", "#C9FAF1"],     # the jar's fluid
    "enamel": ["#08192A", "#0E2A43", "#163E5E", "#21557B", "#336F98", "#5791B5", "#98C0D8"],    # the machines' paint
    "brass": ["#3A2306", "#6B420D", "#9C6516", "#CB8D25", "#E9B649", "#F7DA86", "#FFF4CC"],     # caps, rivets, reels
    "steel": ["#111619", "#222B30", "#364249", "#4F5D65", "#73828A", "#A0ADB3", "#D6DEE1"],     # frames, glass edges
    "nixie": ["#2B0C02", "#5C1E05", "#93390A", "#CC5C12", "#F48526", "#FFB45E", "#FFE4B5"],     # tubes, lamps at night
    "arc": ["#160D38", "#2A1C66", "#432F9C", "#6248CC", "#8F7BEA", "#C2B7FA", "#F0EDFF"],       # lightning
    "sage": ["#5E6B5F", "#7E8C7F", "#A0AD9F", "#BFCABD", "#D6DED3", "#E7ECE3", "#F5F7F1"],      # the lab's tiles
    "room": ["#030606", "#070D0D", "#0B1515", "#101E1E", "#162828", "#1E3535", "#284645"],      # the lab at night
}

C = dict(
    white="#FFFFFF",
    ink="#10211F", ink_n="#E4F4EE",                  # the words by day and by night
    fill="#FBFCF8", fill_n="#081010",                # a card's face
)

# The few colours that belong to no ramp, each named, so the palette stays closed (see TOKENS).
X = dict(
    title_day="#0B1622",       # a title's edge by day, the enamel's darkest
    title_night="#FFB45E",     # a title of nixie light
    muted_day="#3D5653", muted_night="#9DBDB3",        # small labels by day and by night
    accent_day="#A3253F", accent_night="#FF9A5A",      # SECTION A-A, arrows and checks
    rule_day="#A9B8AA", rule_night="#24403C",          # the rules
    dim_day="#DCE4D8", dim_night="#0F1D1C",            # a chart's dotted guides
    tag_ink_day="#1A0806", tag_ink_night="#160700",    # a tag's letters
    shade_ink="#020404",                               # see-through shadow
)

# --------------------------------------------------------------------------- the walls
# The lab's wall from the top of a sheet to its foot: pale sage tiles by day, a little deeper toward the floor; by
# night the dark of the room, the jar's light rising from below. Every text colour clears 4.5:1 on each band.
DAY_SKY = ["#EEF1E9", "#E8EDE4", "#E2E9DF", "#DBE4D8", "#D3DED1"]
NIGHT_SKY = ["#030707", "#050C0C", "#071111", "#0A1717", "#0E1E1D"]

# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in DAY_SKY} | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})

step, ramp_for = tones(RAMP)
