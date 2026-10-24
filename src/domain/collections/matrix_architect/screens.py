# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the Architect's screens show: the year in review, a picture from each month of the Matrix collection.

Each picture is twenty units by twelve, the size of a television's tube on the Architect's wall, drawn in the
phosphor the screens burn on: `.` is the dark glass, and `1` to `6` the hand's flame ramp from its dim green to its
white-hot. January's is the code falling; February's the two pills, one bright and one dim, offered in an open hand;
March's the telephone box on its street with its handset off the hook and ringing; April's the white rabbit running
with his pocket watch; May's a flying kick over the dojo's mats; June's the leap from one roof to the next across the
night city; July's a train's headlights blazing out of its tunnel; August's a cookie and the spoon that bends;
September's the hovercraft over the tunnel's black water on its glowing pads; October's the pods the machines grow
us in, a sleeper curled in each; November's the chateau's chandelier; and December's the room itself, its wall of
screens and its chair, the year looking at itself.

The big sets at the left of a header show three of them larger, forty units by twenty-four (`big`): the code falling,
the two pills held out on two open hands, and the white rabbit in his waistcoat with his watch.
"""
from __future__ import annotations

import random

W, H = 20, 12      # a picture's width and height, in units

PICTURES = {
    "rain": None,              # the code, drawn by `rain` below
    "choice": [
        "....................",
        "..356666653.........",
        ".35666666665........",
        ".35555555554........",
        "..344444443.........",
        "....................",
        ".........123333321..",
        "........12333333332.",
        "........12222222221.",
        ".........111111111..",
        "....................",
        "....................",
    ],
    "exit": [
        "....6666666.........",
        "....4444444.....3...",
        "....4.....4..3...3..",
        "....4.555.4...3...3.",
        "....4.5.5.4...3...3.",
        "....4.555.4..3...3..",
        "....4..5..4.....3...",
        "....4..5..4.........",
        "....4.55..4.........",
        "....4.....4.........",
        "..44444444444.......",
        "22222222222222222222",
    ],
    "rabbit": [
        "..........66.66.....",
        "..........56.56.....",
        "..........56.56.....",
        ".........666666.....",
        "........66666166....",
        "..666...6666666665..",
        ".66666666666666.....",
        "6666666666666666....",
        ".5666666666665.33...",
        "..55..555..55..333..",
        ".55...5.....55..3...",
        "....................",
    ],
    "dojo": [
        "...66...........66..",
        "...66..........66...",
        "..555.........66....",
        ".5555........66.....",
        "5.555.......66......",
        "...555....66........",
        "...2222266..........",
        "...555..............",
        "...55...............",
        "...55...............",
        "..555...............",
        "21212121212121212121",
    ],
    "rooftop": [
        "..........5.........",
        ".........556........",
        "........5.55........",
        "...........45.......",
        "..........4..5......",
        "333.................",
        "3.3.33........44444.",
        "333.3.3.......4.4.4.",
        "3.333.3...2...44444.",
        "333.333..222..4.4.4.",
        "3333333.22222.44444.",
        "3333333222222244444.",
    ],
    "subway": [
        "......2222222.......",
        "....22.......22.....",
        "...2..4444444..2....",
        "..2..433333334..2...",
        "..2..431111134..2...",
        ".2...433333334...2..",
        ".2...444444444...2..",
        ".2...466444664...2..",
        ".2...466444664...2..",
        ".2...444444444...2..",
        "2211111111111111112.",
        "1.1.1.1.1.1.1.1.1.1.",
    ],
    "oracle": [
        "....................",
        "...4444.........55..",
        "..455554.......5665.",
        ".45515554......5665.",
        ".45555154.......55..",
        ".45155554.......4...",
        "..455514.......4....",
        "...4444.......4.....",
        "..............4.....",
        "...............44...",
        ".................44.",
        "..................4.",
    ],
    "hovercraft": [
        "....................",
        "..........34........",
        "....333333443.......",
        "..3344444444443.....",
        ".34455455455444311..",
        ".3333333333333331122",
        "..3.....3.....3.1...",
        "..6.....6.....6.....",
        ".464...464...464....",
        "..1.....1.....1.....",
        "1.1.1.1.1.1.1.1.1.1.",
        ".1.1.1.1.1.1.1.1.1.1",
    ],
    "harvest": [
        "...2.....2.....2....",
        "..343...343...343...",
        ".34444.34444.34444..",
        ".41144.41144.41144..",
        ".41114.41114.41114..",
        ".44114.44114.44114..",
        "..444...444...444...",
        "...2.....2.....2....",
        "..343...343...343...",
        ".34444.34444.34444..",
        ".41144.41144.41144..",
        ".41114.41114.41114..",
    ],
    "chateau": [
        ".........3..........",
        "..6...6..3..6...6...",
        "..5...5.343.5...5...",
        "..4...4..4..4...4...",
        "..4444444444444444..",
        "...4...4.4.4...4....",
        "...3..34444443..3...",
        "...5...3.444.3..5...",
        ".......5..4..5......",
        "..........3.........",
        ".........353........",
        "..........5.........",
    ],
    "architect": [
        "....................",
        ".444.444.444.444....",
        ".464.454.464.444....",
        ".444.444.444.444....",
        ".454.464.444.464....",
        ".444.444.444.444....",
        "..............33....",
        "..............33....",
        "............3333....",
        "...........33333....",
        "...........3...3....",
        "22222222222222222222",
    ],
}
ORDER = ("rain", "choice", "exit", "rabbit", "dojo", "rooftop", "subway", "oracle", "hovercraft", "harvest",
         "chateau", "architect")


def rain(seed: int = 4) -> list:
    """January's picture: the code falling down the tube in streams a unit wide, each led by a white-hot head with
    its trail fading up the glass behind it, wrapping from the tube's foot to its top, so that it runs on without a
    seam."""
    rnd = random.Random(seed)
    grid = [["."] * W for _ in range(H)]
    for x in range(W):
        if rnd.random() < 0.35:
            continue
        head = rnd.randrange(H)
        for i in range(rnd.randint(3, 9)):
            y = (head - i) % H
            if i == 0 or rnd.random() < 0.85:
                grid[y][x] = "6" if i == 0 else str(max(1, 5 - i // 2))
    return ["".join(r) for r in grid]


def picture(name: str) -> list:
    """A month's picture as rows of `.` and the flame ramp's tones `1` to `6`."""
    return rain() if name == "rain" else PICTURES[name]


def cells(name: str) -> dict:
    """A picture's lit units, {(x, y): tone}, tone 1 to 6 on the flame ramp."""
    return {(x, y): int(ch) for y, row in enumerate(picture(name)) for x, ch in enumerate(row) if ch.isdigit()}


# --------------------------------------------------------------------------- the big sets' pictures
BW, BH = 40, 24    # a big set's picture, twice a small one's each way

RABBIT = [
    ".................5.5....................",
    "................565565..................",
    "................565565..................",
    "................565565..................",
    "................565565..................",
    "...............56666665.................",
    "..............5666666665................",
    "..............5666661665................",
    "..............56666666664...............",
    "...............5666666665...............",
    "................5336633.................",
    "...............533333336....444.........",
    "..............5333333336666445544.......",
    "..............53333333336..4566554......",
    "..............5533333335...4566554......",
    "...............553333355....45544.......",
    "................5666665......444........",
    "...............566..566.................",
    "..............566....566................",
    ".............566......566...............",
    "............566........566..............",
    "...........555..........555.............",
    "........................................",
    "1111111111111111111111111111111111111111",
]
HAND = [                # a hand reaching in from the left, palm up, its thumb raised
    "......11............",
    ".....1221...........",
    ".....1221......1111.",
    "22222222221..112222.",
    "22222222222222222221",
    "2222222222222222221.",
    "22222222222222221...",
    "2222222222221.......",
    "222222221...........",
]


def _capsule(grid, x0, y0, w, h, tones):
    """A pill lying on its side, `w` by `h`, its top-left at (x0, y0): its edge, the light along its top, its body,
    the shade under it and the seam between its halves, in `tones` (edge, shade, body, light, seam)."""
    edge, shade, body, light, seam = tones
    r = h / 2
    for y in range(h):
        for x in range(w):
            cx = min(max(x + 0.5, r), w - r)
            d = ((x + 0.5 - cx) ** 2 + (y + 0.5 - r) ** 2) ** 0.5
            if d > r:
                continue
            c = edge if d > r - 1 else light if y < h * 0.3 else shade if y > h * 0.68 else body
            grid[y0 + y][x0 + x] = seam if (x == w // 2 and 0 < y < h - 1) else c


def big(name: str) -> list:
    """A big set's picture as rows of `.` and the flame ramp's tones `1` to `6`: January's code falling, February's two
    pills, the bright and the dim, each offered on a hand reaching in from its side, and April's white rabbit in his
    waistcoat, running with his watch held out."""
    if name == "rabbit":
        return RABBIT
    grid = [["."] * BW for _ in range(BH)]
    if name == "rain":
        rnd = random.Random(4)
        for x in range(BW):
            if rnd.random() < 0.3:
                continue
            head = rnd.randrange(BH)
            for i in range(rnd.randint(4, 16)):
                if i == 0 or rnd.random() < 0.85:
                    grid[(head - i) % BH][x] = "6" if i == 0 else str(max(1, 5 - i // 3))
    elif name == "choice":
        for j, row in enumerate(HAND):
            for i, ch in enumerate(row):
                if ch != ".":
                    grid[13 + j][i] = grid[13 + j][BW - 1 - i] = ch
        _capsule(grid, 6, 9, 12, 6, ("4", "5", "5", "6", "4"))
        _capsule(grid, 22, 9, 12, 6, ("1", "2", "3", "4", "2"))
    return ["".join(r) for r in grid]


def big_cells(name: str) -> dict:
    """A big set's picture's lit units, {(x, y): tone}."""
    return {(x, y): int(ch) for y, row in enumerate(big(name)) for x, ch in enumerate(row) if ch.isdigit()}
