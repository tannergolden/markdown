# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Christmas set's palette: its ramps, its sheet colours, its snow and its sky, and the closed set of
every colour one of its files may use."""
from __future__ import annotations

from ..pixel.shade import make_ramp, tones

# The sheet's own colours: the ice paper and its grid, the pine the words and rules are inked in, the holly
# red, the gold, the snow and the winter sky, and the glass of the lights.
C = dict(
    white="#FFFFFF", snow="#F4F9FD", snow2="#DCE8F2", snow3="#A9BFD3",
    pine0="#05301B", pine1="#0B4A2A", pine2="#16703D", pine3="#24964F", pine4="#52C77B",
    red0="#5A0612", red1="#8C0D20", red2="#C8102E", red3="#EE3A4E", red4="#FF9AA5",
    gold0="#6B4C05", gold1="#A57A00", gold2="#DDA500", gold3="#FFD23F", gold4="#FFF1B8",
    wood0="#3A1F0C", wood1="#6A3C1A", wood2="#99612F",
    sky0="#060E1A", sky1="#0A182B", sky2="#10243D", sky3="#1A3656",
    slate="#566273", ice="#EEF5FB", grid="#D8E5F1", grid_n="#16304D",
    cyan="#5CD6FF", pink="#FF7AC8", green="#3DDC84", orange="#F28C28", coal="#1F2937",
)
# The lights on a string, a wire or a tree, by turns: red, gold, green, cyan and pink glass.
BULBS = [C["red3"], C["gold3"], C["green"], C["cyan"], C["pink"]]

# Hand-set ramps, dark to light, for the things drawn most; the glass is made from its one colour. Every
# colour a sprite takes is a tone on one of these.
RAMP = {
    "pine": ["#062A22", "#0B4331", "#11613B", "#1B8043", "#2FA04B", "#63C25A", "#A9E07E"],
    "red": ["#3A0620", "#680C28", "#9E1230", "#C8102E", "#EE3A4E", "#FF7C6B", "#FFC9B8"],
    "gold": ["#4A2A06", "#7D4E0A", "#B37D10", "#E2A91A", "#FFD23F", "#FFE98C", "#FFFBE3"],
    "snow": ["#51688A", "#7890B2", "#A3BAD4", "#C9D9EA", "#E4EDF7", "#F6FAFD", "#FFFFFF"],
    "wood": ["#241208", "#45230F", "#6B3C1B", "#945A2B", "#BE8248", "#DDA86A", "#F2D2A0"],
    "coal": ["#07090E", "#131722", "#222938", "#353F53", "#4F5B73", "#7A87A0", "#AEB9CC"],
    "carrot": ["#5C1D06", "#8E330C", "#C2521A", "#F28C28", "#FFB15C", "#FFD39A", "#FFF0D6"],
    "moon": ["#4A4A52", "#77735F", "#ABA37C", "#D6CB9C", "#F1E7BD", "#FFF7DC", "#FFFFFF"],
    "silver": ["#2E3A4E", "#4B5A73", "#71829E", "#9DAEC6", "#C8D5E6", "#E9F0F8", "#FFFFFF"],
}
RAMP["cyan"] = make_ramp(C["cyan"])
RAMP["pink"] = make_ramp(C["pink"])
RAMP["green"] = make_ramp(C["green"])
RAMP["orange"] = make_ramp(C["orange"])
RAMP["slate"] = make_ramp(C["slate"])

# The ramp a sheet colour on no ramp is shaded on: its lit edge or shaded foot is the nearest tone there,
# stepped (see `near`).
HOME = {**{C[f"red{i}"]: "red" for i in range(5)}, **{C[f"pine{i}"]: "pine" for i in range(5)},
        **{C[f"gold{i}"]: "gold" for i in range(5)}, **{C[n]: "silver" for n in ("snow", "snow2", "snow3")},
        C["wood1"]: "wood", C["wood2"]: "wood", C["coal"]: "coal"}

# Snow in daylight and by moonlight: the tops catch the light, the undersides go blue.
SNOW = {
    False: dict(top="#FFFFFF", body="#FFFFFF", shade="#D3E1EE", deep="#A9BFD3", line="#7F98B8",
                glint="#A8DDF7", ice=("#E2F2FC", "#B4DCF4", "#86C1EA")),
    True: dict(top="#EEF4FB", body="#CBDAEC", shade="#97AECD", deep="#6B85AB", line="#4B6286",
               glint="#FFFFFF", ice=("#B9D6F0", "#87AEDA", "#5F87B8")),
}

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file
# uses is a token here, in C, in a ramp, in the snow or in the night sky (see TOKENS).
X = dict(
    muted_day="#46705A",      # small labels on the day paper
    dim_night="#27456A",      # a chart's dotted guides by night
    frost_hi="#C3D3E6",       # the shaded white of a candy stripe
    shade_ink="#0A1020",      # see-through shadow
    earthshine="#16263F",     # the moon's unlit part by night
    moonlit_pine="#3E8F6E",   # moonlight along a tree's left edge
    star_faint="#3E5478", star_dim="#56709A", star_blue="#CFE3FF",
    flake_far_day="#C1D2E4",  # far snow by day
    frost_blue="#8FB0D2",     # near snow by day
    glint="#BFD6F5",          # a glint's arms by night
    icon_shade_day="#5F84AC",
)

# --------------------------------------------------------------------------- the sky
NIGHT_SKY = ["#040913", "#07101D", "#0A1628", "#0E1D34", "#122640"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for t in SNOW.values() for v in t.values() for c in ([v] if isinstance(v, str) else v)}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})

step, ramp_for = tones(RAMP)


def _rgb(h: str) -> tuple:
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def near(col: str, k: int) -> str:
    """The tone `k` steps lighter (or, negative, darker) than `col`: on its own ramp for a tone, and for a
    sheet colour on none, from the nearest tone of the ramp it is shaded on. A colour with no ramp at all,
    like the night sky's, is its own shade."""
    try:
        return step(col, k)
    except KeyError:
        if col not in HOME:
            return col
    ramp = RAMP[HOME[col]]
    i = min(range(len(ramp)), key=lambda j: sum((a - b) ** 2 for a, b in zip(_rgb(ramp[j]), _rgb(col))))
    return ramp[max(0, min(len(ramp) - 1, i + k))]
