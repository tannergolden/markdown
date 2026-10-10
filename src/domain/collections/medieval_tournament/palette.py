# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Tournament set's palette: its ramps of canvas, silk, gold and steel, the hand's flame and skins, its day and
its night, and the closed set of every colour one of its files may use."""
from __future__ import annotations

from ...holidays.pixel.shade import tones
from ..hand import MEDIEVAL

# Hand-set ramps, dark to light. The silks are the tinctures of heraldry, each from the tone it takes in the
# fold to the sheen where the light runs across it; the canvas is a pavilion's, unbleached and sunlit by day,
# and by night the same canvas warm where a lantern hangs and deep blue where its light gives out. Every flame
# burns on the collection's one flame and every face and hand is drawn on its three skins, light to dark (see
# `collections.hand`). Every colour a sprite takes is a tone on one of these.
RAMP = {
    "canvas": ["#4B4130", "#6F634B", "#948769", "#B9AC8C", "#D6CBAE", "#EAE2CB", "#F7F2E4"],    # unbleached
    "dusk": ["#1A120C", "#271B12", "#352519", "#453121", "#583E2A", "#6E4F35", "#8A6644"],      # lantern-lit
    "night": ["#060A16", "#0A1020", "#0F172C", "#152039", "#1D2A47", "#283757", "#36476A"],     # beyond it
    "vert": ["#0B2B19", "#11432A", "#195E3A", "#22794A", "#33975E", "#62BA80", "#A8DDB8"],
    "argent": ["#5F5B54", "#86817A", "#AAA59C", "#CBC6BC", "#E3DFD6", "#F2EFE8", "#FFFFFF"],
    "or": ["#4A2F06", "#7A540B", "#A97B14", "#D3A425", "#ECC347", "#F8DD7E", "#FFF3C2"],
    "gules": ["#3B060C", "#650D17", "#931725", "#BC2334", "#DC414B", "#EF7B79", "#FAB9B0"],
    "azure": ["#0A163F", "#112A69", "#1A4194", "#285BBD", "#467FD9", "#83A9EC", "#C3D6F7"],
    "purpure": ["#22092E", "#3A1350", "#551E71", "#713193", "#8F51B1", "#B585CF", "#DEC3EA"],
    "sable": ["#07070A", "#111116", "#1B1B22", "#282832", "#393945", "#51515E", "#71717E"],
    "tenne": ["#3D1904", "#692D08", "#97440E", "#C15F16", "#DF7E28", "#F1A65A", "#FAD1A0"],
    "steel": ["#14171D", "#262B34", "#3B424E", "#57606E", "#7A8493", "#A5AEBB", "#D8DEE6"],     # plate armour
    "wood": ["#2A190D", "#452A15", "#64401F", "#86592C", "#A6773F", "#C49A5E", "#DEC090"],      # lances, rails
    "horse": ["#22110A", "#3B1E11", "#58301B", "#774426", "#965C35", "#B6804F", "#D4A97A"],     # a bay
    "turf": ["#15250D", "#213A15", "#30531D", "#426E28", "#5A8A35", "#7DAA52", "#AFD088"],      # the lists
    "flame": MEDIEVAL.ramp("flame"),                                                            # torch, lantern
    **{f"skin{i}": MEDIEVAL.ramp(f"skin{i}") for i in range(3)},                               # faces, hands
}

C = dict(
    white="#FFFFFF",
    ink=MEDIEVAL.body[0], ink_n=MEDIEVAL.body[1],      # the words, in the hand's ink
    fill="#F6F1E3", fill_n="#2A2219",                  # a card's face
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses is a
# token here, in C, in a ramp or in the night (see TOKENS).
X = dict(
    panel_a="#E7E0CC",         # the canvas's unbleached panels by day
    panel_b="#DAE0C9",         # and its panels dyed a pale green, the livery's
    key="#E6DFCB",             # what a label's backing is laid in by day: lifted off the canvas when the drawing ends
    seam_a="#D0C6AB", seam_b="#C3CAB1",                # the fold of each seam, in shade
    stitch_a="#A69C7E", stitch_b="#9BA388",            # the stitches along it
    muted_day=MEDIEVAL.muted[0],                       # small labels by day, in the hand's quieter ink
    muted_night=MEDIEVAL.muted[1],                     # and by night
    accent_day="#5A1E73",      # SECTION A-A, arrows and checks by day: purpure
    rule_day="#A99F84", rule_night="#5A5246",
    dim_day="#CFC6AB", dim_night="#3B3A44",            # a chart's dotted guides
    shade_ink="#07060A",       # see-through shadow
    glint="#FFFBEA",           # the sheen running across silk
)

# --------------------------------------------------------------------------- the night
# The canvas by night from the top of a sheet to its foot: warmest under the lanterns hung along the ridge, and
# falling to deep blue toward the hem, every band within the hand's night. Every text colour of the night clears
# 4.5:1 on each band and on the glow.
NIGHT_SKY = ["#322115", "#2D2017", "#271E1A", "#1E1B20", "#181A26", "#13182A", "#10162B"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})
# The skins a face or a hand is drawn in, light to dark.
SKINS = tuple(RAMP[f"skin{i}"] for i in range(3))
# The pixels a torch's or a lantern's light falls on: wood, canvas, steel, turf, the silks and faces.
LIT = set(RAMP["wood"]) | set(RAMP["canvas"]) | set(RAMP["steel"]) | set(RAMP["turf"]) | set(RAMP["argent"]) \
    | set(RAMP["horse"]) | set(RAMP["dusk"]) | {c for skin in SKINS for c in skin}

step, ramp_for = tones(RAMP)
