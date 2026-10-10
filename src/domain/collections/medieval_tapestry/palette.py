# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Tapestry set's palette: the wools of the embroidery, the linen they are stitched on by day and by
torchlight, the hand's torchlight and skin, and the closed set of every colour one of its files may use."""
from __future__ import annotations

from ...holidays.pixel.shade import tones
from ..hand import MEDIEVAL

# Hand-set ramps, dark to light. The wools are the embroiderers' own, dyed with madder, weld and woad: a
# terracotta, a mustard, an olive, a blue grey and a dark umber, with a sage and a madder red beside them,
# and an indigo and a mulberry for what a badge may be written in. The linen is unbleached cream; the gold
# is the thread that catches the torchlight by night. The torches burn on the collection's flame, and the
# faces and hands are stitched in the wools of its three skins (see `hand`). Every colour a sprite takes is a
# tone on one of these.
RAMP = {
    "linen": ["#6B5A44", "#8C7858", "#AE9A74", "#CBB893", "#E0D2B0", "#EEE3C8", "#F8F1DE"],
    "terracotta": ["#3A1A10", "#5E2A18", "#8A4026", "#B45A33", "#CF7A4C", "#E39E73", "#F2C9A8"],
    "mustard": ["#3F2E08", "#6B4E10", "#94711A", "#BD9426", "#D9B33F", "#E9CB6E", "#F6E4AA"],
    "olive": ["#1F2A12", "#36461F", "#4F652E", "#6B8540", "#88A356", "#A9C07A", "#CEDBA8"],
    "woad": ["#1B2630", "#2E3F4E", "#45596B", "#5E7589", "#7B92A5", "#9FB2C1", "#C8D5DF"],
    "umber": ["#120C08", "#241810", "#38261A", "#4E3726", "#664B36", "#80634A", "#9C8066"],
    "sage": ["#2A3A2E", "#3F5745", "#577560", "#71927A", "#8EAD95", "#AECAB3", "#D2E3D5"],
    "madder": ["#2E0A0C", "#4E1216", "#741C22", "#9A2A30", "#B9474A", "#D2726F", "#E8A8A3"],
    "indigo": ["#141C3A", "#22305C", "#2F4580", "#3E5CA3", "#5A7BC0", "#8AA2D6", "#BCCBE8"],
    "mulberry": ["#2A1430", "#45214D", "#5F2F6B", "#7B4288", "#9A62A6", "#B98DC2", "#D9BEDE"],
    "gold": ["#4A3008", "#7A520E", "#A87518", "#CF9A28", "#E8B93F", "#F3D46F", "#FBEBB4"],
    "flame": MEDIEVAL.ramp("flame"),
    "iron": ["#0E0F12", "#1C1E24", "#2C2F38", "#3E424D", "#555A66", "#737985", "#9AA0AB"],
    "steel": ["#3A3F4A", "#555C6A", "#737B8A", "#929AA8", "#B1B8C4", "#CED4DD", "#EAEDF2"],
    **{f"skin{i}": MEDIEVAL.ramp(f"skin{i}") for i in range(3)},
}

C = dict(
    white="#FFFFFF",
    paper="#E8D8B0", weft="#D3BE90", warp="#F4E9CA", slub="#BFA77A",          # the linen by day and its weave
    paper_n="#251912", weft_n="#1B120C", warp_n="#33251A", slub_n="#130D08",  # the linen by torchlight
    ink=MEDIEVAL.body[0], ink_n=MEDIEVAL.body[1],                             # the words, in the hand's ink
    fill="#F3EAD3", fill_n="#3B2A1C",
    terracotta=RAMP["terracotta"][3], mustard=RAMP["mustard"][4], olive=RAMP["olive"][3], woad=RAMP["woad"][3],
    umber=RAMP["umber"][2],
)
# The wools a letter, a horse or a figure's tunic comes in, by turns.
WOOLS = ("terracotta", "mustard", "olive", "woad")

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses
# is a token here, in C, in a ramp or in the night (see TOKENS).
X = dict(
    muted_day=MEDIEVAL.muted[0],      # small labels on the day linen, in the hand's quieter ink
    muted_night=MEDIEVAL.muted[1],    # and on the night linen
    rule_day="#A08A66",       # a hairline of thread on the day linen
    rule_night="#7A5E44",     # and on the night linen
    dim_day="#D3C5A3", dim_night="#45321F",    # a chart's dotted guides
    shade_ink="#1A1008",      # see-through shadow
)

# --------------------------------------------------------------------------- the night
# The linen by torchlight from the top of a sheet to its foot: a little warmer under the torches, falling to a
# deep umber below, so that the pools of their light read on it.
NIGHT_SKY = ["#2E2017", "#271B13", "#21170F", "#1B130C", "#170F0A"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})

step, ramp_for = tones(RAMP)
