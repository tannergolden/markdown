# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Heaven & Hell theme's palette: heaven's gold, pearl, cloud and linen by day, hell's lava, fire, basalt, iron
and the demons' hide by night, and the closed set of every colour one of its files may use."""
from __future__ import annotations

from ...holidays.pixel.shade import tones

# Hand-set ramps, dark to light: shadows lean purple and lights lean gold, as the engine shades. By day everything is
# lit from heaven's upper left; by night only by the fires of hell, from below.
RAMP = {
    # ---- heaven
    "gold": ["#4A2E05", "#7A4D08", "#A8700E", "#D19A1C", "#EDBF3A", "#FADE7A", "#FFF5CF"],       # gilt, halos
    "pearl": ["#4C4866", "#77738F", "#A29EB8", "#C9C6D8", "#E4E2EE", "#F4F3F9", "#FFFFFF"],      # marble, pearls
    "cloud": ["#585E9C", "#7D84BE", "#A3A9D8", "#C6CAEB", "#E2E4F6", "#F6F4F4", "#FFFFFF"],      # cumulus
    "linen": ["#4F4A64", "#7C7692", "#A8A3BE", "#CFCBDF", "#E9E7F2", "#F8F7FB", "#FFFFFF"],      # robes, feathers
    "azure": ["#16306B", "#21478F", "#3163B3", "#4A84D1", "#73A6E6", "#A8CBF3", "#DCEBFC"],      # cloaks, sashes
    "rose": ["#3E0A1C", "#6A1430", "#9A2244", "#C8385E", "#E46684", "#F49AB0", "#FDD3DE"],       # hearts, roses
    "skin0": ["#5A2E24", "#7F4A38", "#A86E55", "#D49B7A", "#EDBD98", "#F8D9BC", "#FFF0DE"],      # skin, light
    "skin1": ["#43231A", "#64382A", "#8A553E", "#B47755", "#D39A72", "#E8BC96", "#F7DCC0"],      # skin, mid
    "skin2": ["#24130E", "#3A2117", "#553222", "#744733", "#956249", "#B58267", "#D4A88D"],      # skin, dark
    "blond": ["#3E2306", "#6A3F0B", "#9A6414", "#C98E25", "#E4B447", "#F3D47E", "#FCEDBE"],      # golden hair
    "brown": ["#120A07", "#22140D", "#352015", "#4B2E1E", "#634029", "#7F5638", "#9E714D"],      # dark hair
    "steel": ["#2C3040", "#464C60", "#666E85", "#8C94A8", "#B3BAC9", "#D6DBE4", "#F2F5F9"],      # a sword of light
    "laurel": ["#0E2A14", "#174222", "#205C30", "#2A7A40", "#3D9C55", "#6FBF7F", "#B3E2B9"],     # a victor's laurel
    # ---- hell
    "lava": ["#2B0503", "#5E0A04", "#9C1A05", "#DA3A07", "#FF6B17", "#FFA23D", "#FFE38C"],       # lava, embers
    "fire": ["#4A0E03", "#8F2004", "#D44006", "#FF7A10", "#FFB02A", "#FFE15C", "#FFFBD8"],       # flames
    "basalt": ["#060407", "#100B11", "#1B141C", "#281E29", "#382B38", "#4D3C4C", "#685265"],     # hell's rock
    "iron": ["#09080C", "#151318", "#222026", "#333037", "#47434D", "#615C67", "#837D88"],       # gates, chains
    "hide": ["#2B0306", "#52060D", "#820C18", "#B31626", "#DB2F3C", "#F5626A", "#FFA59E"],       # a demon's skin
    "horn": ["#1E140E", "#3D2B1F", "#655040", "#8E7660", "#B79E82", "#DBC9AE", "#F4EAD8"],       # horns, claws
    "membrane": ["#120406", "#25080C", "#3D0E14", "#58151D", "#752029", "#953238", "#B84E4E"],   # bat wings
    "smoke": ["#0B0808", "#181212", "#272020", "#3A302E", "#504441", "#6B5D58", "#8C7C75"],      # smoke, ash
    "bone": ["#2A211B", "#524438", "#7C6C5B", "#A69683", "#CFC1AB", "#ECE2D0", "#FFF9EE"],       # skulls
    "scorch": ["#1A0605", "#2E0B08", "#4A120B", "#6B1C0F", "#8E2A14", "#B53D1A", "#D85A22"],     # rock in firelight
}

C = dict(
    white="#FFFFFF",
    ink="#1C2148", ink_n="#F7E8DD",                    # the words by day and by night
    fill="#FCFAF5", fill_n="#1A0A0B",                  # a card's face
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses is a
# token here, in C, in a ramp or in a sky (see TOKENS).
X = dict(
    title_day="#3A2406",       # the gilt title's edge, the darkest of its gold
    title_night="#FF8E2B",     # a title of fire
    muted_day="#4A4F75", muted_night="#D2B5A8",        # small labels by day and by night
    accent_day="#8A4B00", accent_night="#FF8A4A",      # SECTION A-A, arrows and checks
    rule_day="#B8964E", rule_night="#7A2A1A",          # the rules: a gilt line by day, a hot one by night
    dim_day="#E3DCEB", dim_night="#3A1412",            # a chart's dotted guides
    shade_ink="#0A0612",                               # see-through shadow
    glint="#FFFDF2",                                   # light on gold
    ray="#FFF8E1",                                     # heaven's light falling through the sky
    glory="#FFE9A6",                                   # the light round a halo and through the gates
    heat="#FF5A1F",                                    # hell's glow
    tag_ink_day="#2A1A03", tag_ink_night="#1A0403",    # a tag's letters
)

# --------------------------------------------------------------------------- the skies
# Heaven from the top of a sheet to its foot: a pale celestial blue warming through pearl to the gold of the light
# below the clouds. Hell: black smoke at the top, reddening toward the fires at the foot. Every text colour clears
# 4.5:1 on each band.
DAY_SKY = ["#C8DBF6", "#D8E4F8", "#EAEDF6", "#F7EEE0", "#FCE7C7"]
NIGHT_SKY = ["#0A0405", "#150607", "#220909", "#330D0C", "#4A1510"]

# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in DAY_SKY} | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})

step, ramp_for = tones(RAMP)
