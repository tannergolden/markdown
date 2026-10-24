# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Exit set's palette: a city street in the March rain, its wall overcast grey-blue by day and navy-black and
wet by night, the El's riveted iron, the tenement's brick, the booth's steel and glass, the neon's glass tubes, and
the closed set of every colour one of its files may use. The words' inks, the phosphor every light burns on, the moon
and the people's skin are the Matrix hand's (see `collections.hand`)."""
from __future__ import annotations

from ...holidays.pixel.shade import tones
from ..hand import MATRIX

# Hand-set ramps, dark to light, shadows leaning purple and lights leaning gold: the street wall by day and by night,
# the elevated railway's painted iron and the rust weeping from its rivets, the tenement's brick and mortar, the
# booth's steel and glass, the neon's tubes unlit, the sign's dark board, the kerb's granite, a long dark coat and
# dark hair, and the green enamel of a street sign; and the hand's own: one phosphor for every light, one moon, and
# three skins.
RAMP = {
    "wall": ["#4B5664", "#626E7C", "#7B8796", "#95A1AF", "#AAB6C3", "#BCC8D4", "#D2DCE5"],      # the wall by day
    "street": ["#05080F", "#080C16", "#0B111E", "#0E1626", "#141E33", "#1B2842", "#253555"],    # and by night
    "iron": ["#0D1412", "#151F1C", "#1F2C28", "#2B3B36", "#3A4E47", "#4D645C", "#667D74"],      # the El's iron
    "rust": ["#2A1206", "#47200C", "#6A3214", "#8E471E", "#B0602C", "#CB7F45", "#E0A46C"],
    "brick": ["#2B0E0C", "#461912", "#64251B", "#843524", "#A14731", "#BB6146", "#D28662"],
    "mortar": ["#38343A", "#524D52", "#6E6A6C", "#8B8786", "#A7A39F", "#C1BDB6", "#D9D5CD"],
    "steel": ["#1A2027", "#2A333C", "#3F4A55", "#58656F", "#76838D", "#98A4AD", "#C2CBD1"],     # the booth
    "glass": ["#16232C", "#243844", "#36525F", "#4F6F7D", "#6F8F9C", "#94B0BB", "#C2D6DC"],
    "tube": ["#56655F", "#73827C", "#93A19A", "#B1BDB7", "#CAD4CE", "#DEE6E1", "#F0F5F2"],      # the neon unlit
    "board": ["#06080B", "#0B0F14", "#12171E", "#1A2129", "#232C36", "#2E3946", "#3C4957"],     # the sign's board
    "granite": ["#25252B", "#36363E", "#4B4B54", "#62626B", "#7B7B84", "#96969E", "#B4B4BB"],   # the kerb
    "coat": ["#06070A", "#0C0E12", "#13161B", "#1B1F25", "#252A31", "#30373F", "#3F4750"],      # a long dark coat
    "hair": ["#0A0806", "#130F0B", "#1C1611", "#271F18", "#33291F", "#413428", "#524333"],
    "enamel": ["#0A2014", "#10301E", "#164229", "#1E5635", "#286C43", "#368453", "#4C9D68"],   # a street sign's
    "flame": MATRIX.ramp("flame"),                                                            # every light
    "moon": MATRIX.ramp("moon"),
    "skin0": MATRIX.ramp("skin0"), "skin1": MATRIX.ramp("skin1"), "skin2": MATRIX.ramp("skin2"),
}

C = dict(
    white="#FFFFFF",
    paper=RAMP["wall"][5],                                  # the street wall's ground by day
    paper_n=RAMP["street"][3],                              # and by night
    ink=MATRIX.body[0], body_night=MATRIX.body[1],          # the words by day and by night: the hand's
)

# The few colours that belong to no ramp, each named, so the palette stays closed: every colour a file uses is a
# token here, in C, in a ramp or in the night (see TOKENS).
X = dict(
    muted_day=MATRIX.muted[0],         # the quieter words: the hand's
    muted_night=MATRIX.muted[1],
    rule_day="#6E7A88", rule_night="#2A3A52",
    dim_day="#A3AFBC", dim_night="#1A2538",
    shade="#0A0F18",                   # a shadow on the wall, laid see-through
    rain_day="#E8EEF3", rain_night="#5C7394",
)

# --------------------------------------------------------------------------- the night
# The street wall from the top of a sheet to its foot by night: darkest overhead, a shade lighter toward the wet
# pavement, where the street's lights lie in the water. Every text colour of the night clears 4.5:1 on each band.
NIGHT_SKY = ["#0B111E", "#0C1322", "#0E1626", "#0E1626", "#0F1829", "#101A2C"]
# Every colour a file may use. The audit fails a file that paints anything else.
TOKENS = ({c.upper() for c in C.values()} | {c.upper() for r in RAMP.values() for c in r}
          | {c.upper() for c in NIGHT_SKY} | {c.upper() for c in X.values()})

step, ramp_for = tones(RAMP)
