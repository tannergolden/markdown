# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Halloween set's palette: its ramps, its named colours and its sky, and the closed set of every
colour one of its files may use."""
from __future__ import annotations

from ..pixel.shade import make_ramp, tones  # noqa: F401  (make_ramp: a ramp built from one colour)

# Hand-set ramps, dark to light: shadows lean purple, lights lean gold, as everything is lit by
# candle and moon. Every colour a sprite takes is a tone on one of these.
RAMP = {
    "pumpkin": ["#3D1106", "#6E2107", "#A8390A", "#DB5F0E", "#F28C28", "#FFB35C", "#FFE2A8"],
    "purple": ["#140A24", "#2A1447", "#43206B", "#5E2F91", "#7F48B8", "#A777DB", "#D6B8F5"],
    "slime": ["#0E2A0C", "#1E4F14", "#2F7A1F", "#48A82A", "#6FD23A", "#A6F05E", "#E0FFB0"],
    "ghost": ["#2E2440", "#564A6E", "#8479A0", "#B3A9C8", "#DCD5E8", "#F1EDF7", "#FFFFFF"],
    "bone": ["#3B2F2A", "#6B5A4C", "#9C8A74", "#C8B89C", "#E6DBC4", "#F6F0E2", "#FFFFFF"],
    "flame": ["#4A2A06", "#7D4E0A", "#B37D10", "#E2A91A", "#FFD23F", "#FFE98C", "#FFFBE3"],
    "stone": ["#16141D", "#2A2735", "#413E4F", "#5C596C", "#7C798C", "#A3A0B3", "#CECCD9"],
    "wood": ["#170D09", "#2B1911", "#452A1B", "#654028", "#8A5A38", "#B07E55", "#D6AB82"],
    "coal": ["#07050C", "#120C1C", "#1F1630", "#2F2445", "#45385F", "#63557F", "#8B7DA6"],
    "blood": ["#2E0610", "#560A1C", "#8A0F26", "#B8162F", "#E0344A", "#FF6B6B", "#FFB3AE"],
    "moon": ["#4A4552", "#7A7166", "#AEA386", "#D9CDA3", "#F1E6BF", "#FFF7DC", "#FFFFFF"],
    "earth": ["#0E0A10", "#1B1320", "#2A1E2D", "#3B2B3B", "#524050", "#6F5A68", "#94808A"],
}
RAMP["slate"] = make_ramp("#566273")

C = dict(
    white="#FFFFFF", fog="#F4F0F8", grid="#DDD3EA", grid_n="#23143A",
    ink="#1B0E2B", coal="#140A24", witch="#3B1A63", violet="#7446AE", lilac="#8E66CC",
    orange=RAMP["pumpkin"][4], purple=RAMP["purple"][3], green=RAMP["slime"][2], red=RAMP["blood"][3],
    gold=RAMP["flame"][4], slate="#566273",
)
# Lights that hang on a string or a wire: a candle's orange, a witch's purple, a potion's green.
BULBS = [RAMP["pumpkin"][4], RAMP["purple"][5], RAMP["slime"][4], RAMP["flame"][4], RAMP["blood"][4]]

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a
# file uses is a token here, in C, in a ramp or in the night sky (see TOKENS).
X = dict(
    muted_day="#66507F",      # small labels on the day paper
    muted_night="#A898C6",    # small labels on the night sky
    body_night="#EFE8F7",     # text by night
    accent_day="#B03F08",     # orange letters on the day paper
    accent_night="#FF9A45",   # orange letters on the night sky
    title_night="#FF9A2E",    # a title lit from inside, like a lantern
    dim_day="#E4DBEF", dim_night="#2C1B45",    # a chart's dotted guides
    star_faint="#3A2C55", star_dim="#5A4A7A", star_pale="#E9E0FF",
    web_day="#B4A8C9", web_night="#7A6E9E",    # cobweb threads
    fog_day="#B7A8CE", fog_night="#8C7EB6",
    moonlit="#8F84BF",        # moonlight along a silhouette's edge
    shade_ink="#0A0612",      # see-through shadow
    node_night="#231238",     # a card's face by night
)

# --------------------------------------------------------------------------- scenery
NIGHT_SKY = ["#07040D", "#0B0615", "#10091E", "#160C28", "#1D1033"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})
GROUND = {RAMP["earth"][2], RAMP["earth"][3], RAMP["earth"][4]}

step, ramp_for = tones(RAMP)
