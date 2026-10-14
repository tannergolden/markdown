# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: LicenseRef-Proprietary
"""The four boards as a pixel set draws them: each game answers what the sheet every game shares asks of it.

Each is a `Game`: its kind and name and the mark on its tag, what its state is read with (the game's own, the same
the standard theme and the prints read), its board, the medallion each side stands in, how its moves are written and
what its panel counts. Every board stands where chess's does, at its size, in the set's colours (`game_board`), and
plays its last move again as the file opens, in the engine's discrete steps:

  Chess         eight ranks of the set's squares, framed; ivory and ebony chessmen; the last move's piece steps
                from its square, a knight hopping over what stands between, a castling king's rook a beat behind;
                what it took is gone as it lands; a king in check glows in the set's red. The panel counts what
                each side has taken, on a tray, and the side ahead by the pieces' worth
  Checkers      chess's board, each dark square's number on a tab as checkers writes its moves, White at the foot;
                the last man hops each man it takes, which is gone as it passes, its path dotted behind it, and is
                crowned as it lands on the far row; a man that must jump glows. The panel counts the men each side
                has taken and the kings each has made
  Pentago       four quarter plates of the set's dark stuff, three holes a side, lying in a bed of the frame's
                stuff in the set's frame, as chess's board is framed; the marbles seen through them, an empty hole's
                floor the light stuff in shadow with the plate's edge shading it, so it reads as cut through and no
                empty hole as a White marble; the last marble comes down in its hole with a flash, its hole ringed,
                and its quarter turns its quarter turn a step at a time, everything on it turning with it, a ghost
                too, an arrow along its outer edges the way it went; a won five are ringed one after another and
                joined in the trophies' gold. A ghost is a marble of the dark stuff ringed in dashes of the light.
                The panel counts each side's marbles left on a rack of seventeen, the house's on the board's dark,
                and where the ghosts stand
  Tic-Tac       nine boards of nine squares, a chequer as chess's squares are, the four edge boards in the dark stuff
                and the corners and the centre in the light, each a plate raised off the bars of the dark stuff; the
                marks cast their shadows, the house's ivory X bevelled; the last mark draws itself stroke by stroke;
                a board closed is washed back as the medallions set the pieces off, one the house won under the
                board's dark and any other under its light, a won one under its winner's mark drawn as large as the
                board, a drawn one lined; the board the next mark is sent to is bracketed in gilt fittings, and three
                boards in a row are struck through with a rod of the trophies' gold. A ghost's square is the stuff its
                board is not, ringed in dashes of the other. The panel counts the boards each side has won

Nothing on a board helps a player choose a move, as on every look's: no hole or square a side could win on next, no
call to block, no word of what perfect play makes of a game. A king in check and a man that must jump glow in the
set's red, and the board a Tic-Tac mark is sent to is bracketed, since those are the rules, not hints. What the
rules point to and what wins is drawn in the trophies' gold in every set, the same in all of them.
"""
from __future__ import annotations

import math

from ...elements.checkers import game as CK
from ...elements.chess import game as CG
from ...elements.chess.layout import castled, finished, outcome, passed
from ...elements.games import data as GD
from ...elements.games.sides import GITHUB, HOUSE, name, other, playing
from ...elements.pentago import game as PG
from ...elements.tictac import game as TC
from ..pixel import GLYPHS, LX, LY, fold, measure
from . import materials as MT
from . import pieces as PC
from .games import LAND, _nothing, appear, brief, gone, lab, pulse, steps
from .trophies import METALS

# The marks on each game's tag, seven pixels high, in the tag's ink.
MARKS = {
    "chess": ["..#..", ".###.", ".###.", "..#..", ".###.", ".###.", "#####"],
    "checkers": ["#.#.#", "#####", ".....", "#####", "#...#", "#####", "....."],
    "pentago": ["###.###", "#.#.#.#", "###.###", ".......", "###.###", "#.#.###", "###.###"],
    "tictac": ["#.#.###", ".#..#.#", "#.#.###", ".......", "###.#.#", "#.#..#.", "###.#.#"],
}


def put(p, drawing: tuple, key: tuple, x: int, y: int, L: str = "base") -> None:
    """A piece's drawing with its top-left at (x, y): drawn once in the file's defs and used wherever it stands."""
    k = ("piece",) + key
    if k not in p.syms:
        p.symbol(k, dict(drawing[0]))
    p.use(k, x, y, L)


def ring_cells(cx: float, cy: float, r: float) -> list:
    """The pixels of a ring a pixel thick round (cx, cy)."""
    out = []
    for y in range(math.floor(cy - r) - 1, math.ceil(cy + r) + 2):
        for x in range(math.floor(cx - r) - 1, math.ceil(cx + r) + 2):
            if r - .5 <= math.hypot(x + .5 - cx, y + .5 - cy) < r + .5:
                out.append((x, y))
    return out


def within(cells, box: tuple) -> dict:
    """The cells inside the box (x0, y0, x1, y1), ends excluded."""
    x0, y0, x1, y1 = box
    return {xy: c for xy, c in cells.items() if x0 <= xy[0] < x1 and y0 <= xy[1] < y1}


def glow(h, p, x: int, y: int, w: int, ht: int, night: bool, L: str, colour: str | None = None) -> None:
    """What the side to move must answer: the square, cell or hole glowing in the set's red, stepped stronger to its
    middle, a ring round it."""
    c = colour or h.game_marks(night)["alert"]
    cx, cy = x + w / 2, y + ht / 2
    for yy in range(y, y + ht):
        for xx in range(x, x + w):
            d = max(abs(xx + .5 - cx) / (w / 2), abs(yy + .5 - cy) / (ht / 2))
            p.px(xx, yy, f"{c}:{(.18, .32, .46)[min(2, int((1 - d) * 3))]}", L)
    p.box(x + 1, y + 1, w - 2, ht - 2, c, L)


def edged(p, cells, colour: str, edge: str, L: str) -> None:
    """`cells` in `colour`, edged a pixel all round in `edge`, so a mark reads on any stuff it crosses."""
    cells = set(cells)
    for (x, y) in {(x + dx, y + dy) for (x, y) in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - cells:
        p.px(x, y, edge, L)
    for (x, y) in cells:
        p.px(x, y, colour, L)


def fallen(d: tuple, off: int, colour: str) -> tuple:
    """A drawing's shadow on what it stands on, cast `off` units down and to the right, away from the lamp, where
    the drawing itself does not cover it: a drawing of its own, in `colour`, to set with the drawing's own corner."""
    body = {xy for xy, _ in d[0]}
    cells = {(x + off, y + off): colour for (x, y) in body if (x + off, y + off) not in body}
    return tuple(sorted(cells.items())), d[1] + off, d[2] + off


def gilt(p, cells, L: str) -> None:
    """`cells` in the trophies' gold, as a binding's fittings are: lit where the lamp finds them, along the top and
    left of each run, outlined in the gold's darkest, so they hold on any stuff by day and by night."""
    G = METALS[3]
    cells = set(cells)
    for (x, y) in {(x + dx, y + dy) for (x, y) in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - cells:
        p.px(x, y, G[0], L)
    for (x, y) in cells:
        p.px(x, y, G[4] if (x, y - 1) not in cells or (x - 1, y) not in cells else G[3], L)


def dotted(p, cells, colour: str, L: str) -> None:
    """An outline round `cells`, every other pixel: where a piece would stand, or where it stood."""
    ring = {(x + dx, y + dy) for (x, y) in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - set(cells)
    for (x, y) in ring:
        if (x + y) % 2 == 0:
            p.px(x, y, colour, L)


def landing(h, p, cx: float, cy: float, s: int, box: tuple, night: bool, at: float = LAND) -> None:
    """The landing, as a move comes down at `at`: a flash on its square, and a ring running out from it in three
    steps."""
    marks = h.game_marks(night)
    flash = {(x, y): f"{PC.IVORY[6]}:0.55" for y in range(int(cy - s / 2), int(cy + s / 2))
             for x in range(int(cx - s / 2), int(cx + s / 2))}
    p.raw(.9, brief(within(flash, box), at, .12), "")
    for i, r in enumerate((s * .45, s * .7, s * .95)):
        cells = {xy: marks["last"] for xy in ring_cells(cx, cy, r)}
        p.raw(.9, brief(within(cells, box), at + .06 + i * .07, .07), "")


FRAME = {False: 4, True: 3}     # how wide a board's frame is, wide and on a phone


def framed(h, p, x0: int, y0: int, w: int, ht: int, night: bool, small: bool = False) -> None:
    """A board's frame, in what the set makes it of and worked in its style (`game_frame`): its shadow cast down and
    to the right, away from the lamp, lit along its top and left, shaded along its foot and right, and outlined."""
    b = h.game_board(night)
    MT.frame(p, b["frame"], b["style"], x0, y0, w, ht, FRAME[small], night)


def squares(h, p, x0: int, y0: int, s: int, files: int, ranks: int, night: bool) -> None:
    """A chequered board of `files` by `ranks` squares `s` wide from (x0, y0), its light and dark squares in what the
    set makes them of, each laid in one of a few variants of its grain so no two neighbours are alike; wood laid as
    parquet, the dark squares' grain turned across the light's."""
    b = h.game_board(night)
    for r in range(ranks):
        for f in range(files):
            dark = (f + r) % 2 == 1
            stuff = b["dark_stuff"] if dark else b["light_stuff"]
            MT.lay(p, stuff, x0 + f * s, y0 + r * s, s, s, variant=(f * 7 + r * 3) % 3,
                   turned=dark and stuff.grain == "wood")


class Game:
    """What every game answers the shared sheet, the same for all four unless a game says otherwise."""

    KIND = LABEL = ""
    HOUSE, GITHUB = HOUSE, GITHUB          # the sides as the game's state names them
    OWNER = CG.OWNER
    glyph = None                           # a mark set before a move whose notation cannot say whose it is

    def glyph_width(self, scale: int) -> int:
        return 0

    def mark(self, p, x: int, y: int, ink: str) -> None:
        art = MARKS[self.KIND]
        p.sprite(x + (7 - len(art[0])) // 2, y, art, {"#": ink})

    def material(self, side: str) -> str:
        return "light" if side == self.HOUSE else "dark"

    def side_name(self, side: str) -> str:
        raise NotImplementedError

    def role(self, side: str, st: dict) -> str:
        who = "the house" if side == self.HOUSE else playing(st["players"])
        return f"{self.side_name(side)}  ·  {who}".upper()

    def plate(self, st: dict) -> tuple:
        """The turn's plate: (label, message, icon, under GitHub's side, the notes across the row, longest first)."""
        if st.get("result"):
            return finished(st)
        notes = (f"due by {st['due']}", f"by {st['due']}") if st["due"] else ("", "")
        return f"{name(st['to_move'])}'s turn", st["alert"], "play", st["to_move"] == GITHUB, notes

    def notation(self, st: dict) -> tuple:
        """The last move: its number as a score sheet writes it, the move, whose it was and its words; before the
        first move, who opens."""
        last = st["last"]
        if last:
            return GD.numbered(st), last["move"], last["side"], last["words"]
        return "1.", "?", st["opens"], f"{name(st['opens'])} opens game {st['game']}"

    def outcome(self, st: dict) -> str:
        return outcome(st)

    def due_word(self, st: dict) -> str:
        return f"{name(st['to_move'])}'s turn"

    def rows(self, st: dict) -> list:
        return [tuple(r[:4]) for r in st["history"]] or [(1, "", "", "")]

    def latest(self, st: dict):
        return st["last"]["number"] if st["last"] else None

    def sides_in_order(self, st: dict) -> tuple:
        return st["opens"], other(st["opens"])

    def height(self, n: int, small: bool = False) -> int:
        return n

    def first(self, st: dict) -> str:
        raise NotImplementedError

    @staticmethod
    def labels(h, p, x0: int, y0: int, step: int, cell: int, files: str, ranks: int, night: bool,
               small: bool = False) -> None:
        """The files under a board, lower case as chess writes them, and the ranks up its left, quietly: each
        centred on its square, `step` apart, `cell` wide, a unit clear of the board's frame, or the files close under
        it where the sheet's own frame leaves no more room."""
        k = h.ink(night)
        t = FRAME[small]
        foot = y0 + (ranks - 1) * step + cell
        y = min(foot + t + 2, h._trophy_room(p).y1 - 10)     # a descender's nine rows, a unit clear of the room
        for i, f in enumerate(files):
            h.say(p, x0 + i * step + cell // 2 + 1, y, f, k["muted"], "57", anchor="middle")
        for i in range(ranks):
            h.say(p, x0 - t - 2, y0 + i * step + cell // 2 - 2, str(ranks - i), k["muted"], anchor="end")


def started(p, x: int, y: int, s: int, colour: str) -> None:
    """The square a move set out from: a dotted line just inside it."""
    for i, (xx, yy) in enumerate([(xx, y + 1) for xx in range(x + 1, x + s - 1)]
                                 + [(x + s - 2, yy) for yy in range(y + 2, y + s - 1)]
                                 + [(xx, y + s - 2) for xx in range(x + s - 3, x, -1)]
                                 + [(x + 1, yy) for yy in range(y + s - 3, y + 1, -1)]):
        if i % 2 == 0:
            p.px(xx, yy, colour)


# =========================================================================== chess
class Chess(Game):
    KIND, LABEL = "chess", "chess"
    HOUSE, GITHUB = "white", "black"

    def state(self, d: dict) -> dict:
        return CG.board_state(d)

    def side_name(self, side: str) -> str:
        return side

    def plate(self, st: dict) -> tuple:
        if st.get("result"):
            return finished(st)
        notes = ((f"due by {st['due']}", f"by {st['due']}") if st["due"]
                 else ("no clock until the first move", "no clock yet"))
        return (f"{CG.turn_name(st)}'s turn", "in check" if st["check"] else "", "play", st["to_move"] == "black",
                notes)

    def notation(self, st: dict) -> tuple:
        last = st["last"]
        if last:
            n = f"{last['number']}." if last["side"] == "white" else f"{last['number']}..."
            return n, last["san"], last["side"], last["words"]
        return "1.", "?", "white", f"@{CG.OWNER} opens game {st['game']}"

    def due_word(self, st: dict) -> str:
        return f"{CG.turn_name(st)}'s turn"

    def sides_in_order(self, st: dict) -> tuple:
        return "white", "black"

    def first(self, st: dict) -> str:
        return "white moves first"

    def medallion(self, h, p, st, cx, cy, r, side, night) -> None:
        size = "narrow" if r >= 9 else "mini"
        d = PC.chessman("king", size, self.material(side))
        put(p, d, ("chess", "king", size, side), cx - d[1] // 2, cy - d[2] // 2)

    def board(self, h, p, st, box, night, moving, small) -> None:
        x0, y0, n = box
        s = n // 8
        size = "narrow" if small else "wide"
        marks = h.game_marks(night)
        framed(h, p, x0, y0, n, n, night, small)
        squares(h, p, x0, y0, s, 8, 8, night)

        def at(sq: str) -> tuple:
            return x0 + CG.FILES.index(sq[0]) * s, y0 + (8 - int(sq[1])) * s

        last, placed = st["last"], st["placement"]
        if last:
            started(p, *at(last["from"]), s, marks["last"])
            tx_, ty_ = at(last["to"])
            for y in range(ty_, ty_ + s):
                for x in range(tx_, tx_ + s):
                    p.px(x, y, f"{marks['glow']}:0.5")
            p.box(tx_ + 1, ty_ + 1, s - 2, s - 2, marks["last"])
        if st["check"]:
            kx, ky = at(st["check"])
            L = p.once("check", pulse(LAND + .05), z=.65) if moving and last else "base"
            glow(h, p, kx, ky, s, s, night, L)
        rook = castled(last, placed) if last and moving else None
        men = p.layer("men", z=.7)
        for sq in sorted(placed, key=lambda q: (-int(q[1]), CG.FILES.index(q[0]))):
            letter = placed[sq]
            kind, side = CG.NAMES[letter.lower()], "white" if letter.isupper() else "black"
            d = PC.chessman(kind, size, self.material(side))
            x, y = at(sq)
            px_, py_ = x + (s - d[1]) // 2, y + s - d[2] - 1
            key = ("chess", kind, size, side)
            if moving and last and sq == last["to"]:
                self.arrive(p, d, key, px_, py_, at(last["from"]), (x, y), kind == "knight", s, .4, LAND, "mover")
                continue
            if rook and sq == rook[1]:
                self.arrive(p, d, key, px_, py_, at(rook[0]), (x, y), True, s, .55, LAND + .15, "rook")
                continue
            put(p, d, key, px_, py_, men)
        if moving and last:
            if last.get("captured"):
                lost = "black" if last["side"] == "white" else "white"
                d = PC.chessman(last["captured"], size, self.material(lost))
                gx, gy = at(passed(last, placed))
                p.raw(.75, gone(PC.placed(d, gx + (s - d[1]) // 2, gy + s - d[2] - 1), LAND), "")
            tx_, ty_ = at(last["to"])
            landing(h, p, tx_ + s / 2, ty_ + s / 2, s, (x0, y0, x0 + n, y0 + n), night)
        self.labels(h, p, x0, y0, s, s, CG.FILES, 8, night, small)

    @staticmethod
    def arrive(p, d, key, px_, py_, frm, to, leap, s, start, end, name) -> None:
        """A piece coming in to its square from another, in discrete steps from `start` to `end` seconds, lifting
        as it goes: a knight high, over whatever stands between, anything else just off the board."""
        dx, dy = frm[0] - to[0], frm[1] - to[1]
        n = 7
        lift = s * (.55 if leap else .14)
        offsets = [(dx, dy)]
        for i in range(n + 1):
            t = i / n
            offsets.append((round(dx * (1 - t)), round(dy * (1 - t) - lift * math.sin(math.pi * t))))
        times = [0] + [start + (end - start) * i / n for i in range(n + 1)]
        L = p.once(name, steps(offsets, times, end + .05), z=.8)
        put(p, d, key, px_, py_, L)

    def count(self, h, p, st, x0, x1, y, night, small) -> int:
        """What each side has taken, on a tray, and the side ahead by the pieces' worth."""
        k = h.ink(night)
        h.heading(p, x0, y, "taken", night)
        y += 9
        t = st["taken"]
        worth = {side: sum(CG.VALUE[q] for q in t[side]) for side in t}
        lead = worth["white"] - worth["black"]
        for side, label, of in (("white", "WHITE TOOK", "black"), ("black", "BLACK TOOK", "white")):
            h.say(p, x0, y + 4, label, k["muted"])
            px_ = x0 + 50
            ahead = lead if side == "white" else -lead
            chip = measure(f"+{ahead}", "35") + 8 if ahead > 0 else 0
            took = t[side]
            step = min(10, (x1 - px_ - chip - 12) // max(1, len(took)))
            h.tray(p, px_ - 2, y - 1, max(len(took) * step + 4, 14), 13, night)
            for i, kind in enumerate(took):
                d = PC.chessman(kind, "mini", self.material(of))
                put(p, d, ("chess", kind, "mini", of), px_ + i * step + (step - d[1]) // 2, y + 11 - d[2])
            if ahead > 0:
                h.chip(p, px_ + max(len(took) * step + 4, 14) + 4, y + 1, f"+{ahead}", night)
            y += 15
        return y - 3


# =========================================================================== checkers
class Checkers(Game):
    KIND, LABEL = "checkers", "checkers"
    SIZES = {"wide": (8, 4, 3), "narrow": (7, 3, 2), "mini": (4, 2, 2)}

    def state(self, d: dict) -> dict:
        return CK.state(d)

    def side_name(self, side: str) -> str:
        return CK.COLOUR[side]

    def first(self, st: dict) -> str:
        return f"{CK.COLOUR[CK.OPENS]} moves first"

    def man(self, size: str, material: str, king: bool) -> tuple:
        rx, ry, t = self.SIZES[size]
        return PC.man(material, rx, ry, t, king)

    def medallion(self, h, p, st, cx, cy, r, side, night) -> None:
        d = self.man("narrow" if r >= 9 else "mini", self.material(side), True)
        put(p, d, ("checkers", "medal", r, side), cx - d[1] // 2, cy - d[2] // 2)

    def board(self, h, p, st, box, night, moving, small) -> None:
        x0, y0, n = box
        s = n // 8
        size = "narrow" if small else "wide"
        b = h.game_board(night)
        marks = h.game_marks(night)
        framed(h, p, x0, y0, n, n, night, small)
        squares(h, p, x0, y0, s, 8, 8, night)

        def at(sq: int) -> tuple:
            r, col = CK.rc(sq)
            return x0 + col * s, y0 + r * s

        last, pieces = st["last"], st["pieces"]
        passes: list = []
        if last:
            started(p, *at(last["path"][0]), s, marks["last"])
            tx_, ty_ = at(last["path"][-1])
            for y in range(ty_, ty_ + s):
                for x in range(tx_, tx_ + s):
                    p.px(x, y, f"{marks['glow']}:0.5")
            p.box(tx_ + 1, ty_ + 1, s - 2, s - 2, marks["last"])
            if last["jumped"]:
                # the jump's path, dotted from landing to landing, and where each man it took stood
                pts = [(at(q)[0] + s / 2, at(q)[1] + s / 2) for q in last["path"]]
                for (ax, ay), (bx, by) in zip(pts, pts[1:]):
                    steps_ = int(max(abs(bx - ax), abs(by - ay)))
                    for i in range(0, steps_, 3):
                        p.px(ax + (bx - ax) * i / steps_, ay + (by - ay) * i / steps_, marks["last"])
                for (cx, cy) in pts[1:-1]:
                    p.rect(cx - 1, cy - 1, 2, 2, marks["last"])
        k = h.ink(night)
        for sq in range(1, 33):
            x, y = at(sq)
            label = fold(str(sq), "35")
            w = measure(label, "35") + 3
            p.rect(x, y, w, 7, b["light"])
            p.text(x + 2, y + 1, label, b["shade"], "35")
        for sq in st["jumpers"]:
            x, y = at(sq)
            L = p.once(f"jump{sq}", pulse(LAND + .05), z=.65) if moving and last else "base"
            glow(h, p, x, y, s, s, night, L)
        men = p.layer("men", z=.7)
        mover = last["path"][-1] if last and moving else None
        for sq in sorted(pieces, key=lambda q: at(q)[::-1]):
            piece = pieces[sq]
            mat = "dark" if piece.lower() == "d" else "light"
            king = piece.isupper()
            x, y = at(sq)
            if sq == mover:
                passes = self.journey(h, p, st, piece, at, s, size)
                continue
            d = self.man(size, mat, king)
            put(p, d, ("checkers", size, mat, king), x + (s - d[1]) // 2, y + s - d[2] - 1, men)
        if last and last["jumped"]:
            lost = "light" if pieces[last["path"][-1]].lower() == "d" else "dark"
            d = self.man(size, lost, False)
            for i, sq in enumerate(last["jumped"]):
                x, y = at(sq)
                cells = PC.placed(d, x + (s - d[1]) // 2, y + s - d[2] - 1)
                dotted(p, cells, marks["last"], "base")
                if moving and i < len(passes):
                    p.raw(.75, gone(cells, passes[i]), "")
        if last and moving:
            tx_, ty_ = at(last["path"][-1])
            landing(h, p, tx_ + s / 2, ty_ + s / 2, s, (x0, y0, x0 + n, y0 + n), night)

    def journey(self, h, p, st, piece, at, s, size) -> list:
        """The last move's man on its way: from the square it set out from, a hop over each man it takes, or a
        slide, landing where it rests; crowned there, the crown's man dropped onto it. Returns when it passes over
        each man it takes."""
        last = st["last"]
        mat = "dark" if piece.lower() == "d" else "light"
        crowned = last["crowned"]
        king = piece.isupper() and not crowned
        d = self.man(size, mat, king)
        end = last["path"][-1]
        tx, ty = at(end)
        hops = list(zip(last["path"], last["path"][1:]))
        jump = bool(last["jumped"])
        per = .42 if jump else .7
        start = .4
        offsets, times, t = [], [], start
        offsets.append((at(last["path"][0])[0] - tx, at(last["path"][0])[1] - ty))
        times.append(0)
        passes = []
        for a, b_ in hops:
            (ax, ay), (bx, by) = at(a), at(b_)
            n = 5
            for i in range(n + 1):
                f = i / n
                lift = s * (.45 if jump else .12) * math.sin(math.pi * f)
                offsets.append((round(ax - tx + (bx - ax) * f), round(ay - ty + (by - ay) * f - lift)))
                times.append(t + per * f)
            passes.append(t + per / 2)
            t += per + .06
        land = times[-1]
        L = p.once("mover", steps(offsets, times, land + .05), z=.8)
        put(p, d, ("checkers", size, mat, king), tx + (s - d[1]) // 2, ty + s - d[2] - 1, L)
        if crowned:
            top = self.man(size, mat, True)
            drop = [(0, -s), (0, -s), (0, -s // 2), (0, 0)]
            when = [0, land + .12, land + .2, land + .28]
            C = p.once("crown", steps(drop, when, land + .33) + appear(land + .12), z=.85)
            base = PC.placed(d, 0, 0)
            cells = {xy: c for xy, c in PC.placed(top, 0, 0).items() if xy not in base or xy[1] < 6}
            k = ("piece", "checkers", "crown", size, mat)
            if k not in p.syms:
                p.symbol(k, cells)
            p.use(k, tx + (s - top[1]) // 2, ty + s - top[2] - 1, C)
        return passes

    def count(self, h, p, st, x0, x1, y, night, small) -> int:
        """The men each side has taken, on a tray in their own colour, the side ahead marked, and the kings each
        has made at the row's end."""
        k = h.ink(night)
        h.heading(p, x0, y, "taken", night)
        y += 9
        lead = st["took"][HOUSE] - st["took"][GITHUB]
        for side in (HOUSE, GITHUB):
            mat, lost = CK.material_of(side), CK.material_of(other(side))
            h.say(p, x0, y + 4, f"{CK.COLOUR[side]} took".upper(), k["muted"])
            px_ = x0 + 50
            took, kings = st["took"][side], st["kings"][side]
            kw = measure("KINGS", "35") + 4 + (min(kings, 3) * 9 if kings else measure("NONE", "35")) + \
                (measure(f"X{kings}", "35") + 3 if kings > 3 else 0)
            room = x1 - px_ - kw - 22
            step = min(9, max(3, (room - 4) // max(took, 1)))
            tw = max(took * step + 4, 14)
            h.tray(p, px_ - 2, y - 1, tw, 13, night)
            d = self.man("mini", lost, False)
            for i in range(took):
                put(p, d, ("checkers", "mini", lost, False), px_ + i * step - 1, y + 11 - d[2])
            ahead = lead if side == HOUSE else -lead
            if ahead > 0:
                h.chip(p, px_ + tw + 2, y + 1, f"+{ahead}", night)
            kx = x1
            if kings:
                if kings > 3:
                    kx -= h.say(p, kx, y + 4, f"X{kings}", k["body"], anchor="end") + 3
                kd = self.man("mini", mat, True)
                for _ in range(min(kings, 3) if kings <= 3 else 1):
                    kx -= 9
                    put(p, kd, ("checkers", "mini", mat, True), kx - 1, y + 12 - kd[2])
            else:
                kx -= h.say(p, kx, y + 4, "NONE", k["muted"], anchor="end")
            h.say(p, kx - 4, y + 4, "KINGS", k["muted"], anchor="end")
            y += 15
        return y - 3


# =========================================================================== tic-tac
class TicTac(Game):
    KIND, LABEL = "tictac", "tic-tac"

    def state(self, d: dict) -> dict:
        return TC.state(d)

    def side_name(self, side: str) -> str:
        return TC.mark_of(side)

    def first(self, st: dict) -> str:
        return "drawn by the Arbiter"

    def notation(self, st: dict) -> tuple:
        if st["last"]:
            return super().notation(st)
        return f"{TC.GHOST}.", "?", st["places"], f"{name(st['places'])} places the first ghost"

    def medallion(self, h, p, st, cx, cy, r, side, night) -> None:
        mark = TC.mark_of(side)
        size = 2 * r - 6
        d = PC.pen(mark, "light" if mark == "X" else "dark", size)
        put(p, d, ("ttt", "medal", size, mark), cx - d[1] // 2, cy - d[2] // 2)

    @staticmethod
    def geometry(n: int, small: bool) -> tuple:
        """The board's measures in pixels, `n` wide: a square's width, the gutter between a board's squares, the bar
        between the boards, a board's width, and the margin round them all inside the frame."""
        gut, bar = 1, 3 if small else 4
        q = (n - 2 * bar - 6 * gut) // 9
        s = 3 * q + 2 * gut
        return q, gut, bar, s, (n - 3 * s - 2 * bar) // 2

    def board(self, h, p, st, box, night, moving, small) -> None:
        x0, y0, n = box
        q, gut, bar, s, off = self.geometry(n, small)
        b = h.game_board(night)
        marks = h.game_marks(night)
        framed(h, p, x0, y0, n, n, night, small)
        dark, light = b["dark_stuff"], b["light_stuff"]

        def board_at(bx: int, by: int) -> tuple:
            return x0 + off + bx * (s + bar), y0 + off + (2 - by) * (s + bar)

        def cell(name_: str) -> tuple:
            fx, fy = TC.xy(name_)
            X, Y = board_at(fx // 3, fy // 3)
            return X + (fx % 3) * (q + gut), Y + (2 - fy % 3) * (q + gut)

        # the bars between the boards and the margin round them in the board's dark stuff, its grain run along each,
        # laid only where it shows; each board's face a tone up from it, seen only in the gutters between its squares
        inner = n - 2 * off
        strips = [(x0, y0, n, off, False), (x0, y0 + n - off, n, off, False), (x0, y0 + off, off, inner, True),
                  (x0 + n - off, y0 + off, off, inner, True)] if off else []
        for i in (1, 2):
            strips += [(x0 + off + i * s + (i - 1) * bar, y0 + off, bar, inner, True),
                       (x0 + off, y0 + off + i * s + (i - 1) * bar, inner, bar, False)]
        for (x, y, w, ht, turned) in strips:
            MT.lay(p, dark, x, y, w, ht, turned=turned and dark.grain == "wood")
        # the nine boards a chequer, as chess's squares are: the four edge boards in the dark stuff a tone up, the
        # corners and the centre in the light, each a plate raised off the bars as a Pentago quarter is, its shadow
        # cast down and to the right and its edge in the board's shade
        deep = MT.Stuff(dark.ramp, min(len(dark.ramp) - 1, dark.at + 1), dark.grain, dark.fleck)

        def odd(name_: str) -> bool:
            fx, fy = TC.xy(name_)
            return (fx // 3 + fy // 3) % 2 == 1
        fall = p.layer("boardfall", z=-.97)
        for bx in range(3):
            for by in range(3):
                X, Y = board_at(bx, by)
                p.rect(X, Y, s, s, dark.tone(-1) if (bx + by) % 2 else dark.tone(1), p.layer("faces", z=-.95))
                for yy in range(Y + 2, Y + s + 2):
                    for xx in range(X + 2, X + s + 2):
                        if xx >= X + s or yy >= Y + s:
                            p.px(xx, yy, f"{b['shade']}:{'0.55' if night else '0.4'}", fall)
                p.box(X - 1, Y - 1, s + 2, s + 2, b["shade"], p.layer("rims", z=-.85))
        for name_ in (f"{f}{r}" for r in range(9, 0, -1) for f in TC.FILES):
            x, y = cell(name_)
            fx, fy = TC.xy(name_)
            MT.lay(p, deep if odd(name_) else light, x, y, q, q, variant=(fx * 7 + fy * 3) % 3, L="cells", z=-.9,
                   quiet=True)
        last = st["last"]
        for name_ in st["ghosts"]:
            # a ghost's square: a part of the board nobody can use, in the stuff its board is not, the bars' own on a
            # light board and the light on a dark one, ringed in dashes of the other
            x, y = cell(name_)
            now = moving and last and last["ghost"] and last["cell"] == name_
            fill = p.once(f"ghost{name_}", appear(.45), z=.4) if now else p.layer("ghosts", z=.4)
            dash = p.once(f"ghostd{name_}", appear(.45), z=.45) if now else p.layer("ghostd", z=.45)
            MT.lay(p, light if odd(name_) else dark, x, y, q, q, L=fill, z=.4)
            for i in range(2, q - 2):
                for (gx, gy) in ((x + i, y + 2), (x + i, y + q - 3), (x + 2, y + i), (x + q - 3, y + i)):
                    if (gx + gy) % 3 != 0:
                        p.px(gx, gy, b["dark"] if odd(name_) else b["light"], dash)
        if last:
            x, y = cell(last["cell"])
            for yy in range(y, y + q):
                for xx in range(x, x + q):
                    p.px(xx, yy, f"{marks['glow']}:0.45")
            # boxed over a ghost just placed, which covers its square
            p.box(x + 1, y + 1, q - 2, q - 2, marks["last"], p.layer("lastbox", z=.46) if last["ghost"] else "base")
        size = q - 6
        men = p.layer("men", z=.7)
        shade = f"{b['shade']}:{'0.6' if night else '0.42'}"     # a mark's shadow, as a frame's and a quarter's

        def cast(d: tuple, mark: str, x: int, y: int, off: int, L: str) -> None:
            put(p, fallen(d, off, shade), ("ttt", "fall", mark, d[1], off, shade), x, y, L)
        for name_, mark in st["cells"].items():
            x, y = cell(name_)
            d = PC.pen(mark, "light" if mark == "X" else "dark", size)
            px_, py_ = x + (q - d[1]) // 2, y + (q - d[2]) // 2
            if last and moving and name_ == last["cell"]:
                cast(d, mark, px_, py_, 1, p.once("penfall", appear(LAND), z=.68))
                self.drawn_in(p, d, mark, px_, py_)
                continue
            cast(d, mark, px_, py_, 1, p.layer("falls", z=.68))
            put(p, d, ("ttt", mark, size), px_, py_, men)
        # the boards that are closed, washed back as the medallions set the pieces off: a board the house won under
        # the board's dark, so its ivory X glows, and one GitHub won or nobody did under the light; a won one under
        # its winner's mark drawn as large as the board, a drawn one lined across
        claimed = last["claimed"] if last and not last["ghost"] else None
        for (bx, by), who in st["boards"].items():
            if not who:
                continue
            X, Y = board_at(bx, by)
            now = bool(claimed and last["board"] == (bx, by))
            L = p.once(f"closed{bx}{by}", appear(1.75), z=.85) if now and moving else p.layer("closed", z=.85)
            wash = f"{b['dark']}:0.78" if who == "X" else f"{b['light']}:0.75"
            for yy in range(Y, Y + s):
                for xx in range(X, X + s):
                    p.px(xx, yy, wash, L)
            if now:
                # the move that closed it stays clear of the wash, over the board's own mark
                kL = p.once(f"kept{bx}{by}", appear(1.75), z=.92) if moving else p.layer("kept", z=.92)
                lx, ly = cell(last["cell"])
                for yy in range(ly, ly + q):
                    for xx in range(lx, lx + q):
                        p.px(xx, yy, marks["glow"], kL)
                p.box(lx + 1, ly + 1, q - 2, q - 2, marks["last"], kL)
                d = PC.pen(last["mark"], "light" if last["mark"] == "X" else "dark", size)
                cast(d, last["mark"], lx + (q - d[1]) // 2, ly + (q - d[2]) // 2, 1, kL)
                put(p, d, ("ttt", last["mark"], size), lx + (q - d[1]) // 2, ly + (q - d[2]) // 2, kL)
            if who == "draw":
                for k in range(-s, s, 5):
                    for i in range(s):
                        xx, yy = X + k + i, Y + s - 1 - i
                        if X + 2 <= xx < X + s - 2 and Y + 2 <= yy < Y + s - 2:
                            p.px(xx, yy, b["edge"], L)
                continue
            big = s - 8
            d = PC.pen(who, "light" if who == "X" else "dark", big)
            bL = p.once(f"claim{bx}{by}", appear(2.05), z=.9) if now and moving else p.layer("claims", z=.9)
            cast(d, who, X + (s - d[1]) // 2, Y + (s - d[2]) // 2, 2, bL)
            put(p, d, ("ttt", "board", who, big), X + (s - d[1]) // 2, Y + (s - d[2]) // 2, bL)
        if last and not last["ghost"] and last["small_line"] and not st["line"]:
            # the three that closed the board, while the game goes on: the game's own line, once it is won, says it
            pts = [(cell(c)[0] + q / 2, cell(c)[1] + q / 2) for c in last["small_line"]]
            self.struck(p, b, pts, q * .3, 1, p.once("strike3", appear(1.5), z=.88) if moving
                        else p.layer("strike3", z=.88))
        if not st["result"] and st["target"] is not None:
            # the board the rules send the next mark to, its corners in gilt fittings as a binding's are
            X, Y = board_at(*st["target"])
            at = 2.6 if claimed else 1.3
            L = p.once("sent", appear(at), z=.95) if moving and last else p.layer("sent", z=.95)
            arm = s // 3
            corners = set()
            for (cx, cy, sx, sy) in ((X - 2, Y - 2, 1, 1), (X + s + 1, Y - 2, -1, 1), (X - 2, Y + s + 1, 1, -1),
                                     (X + s + 1, Y + s + 1, -1, -1)):
                for i in range(arm):
                    for t in (0, 1):
                        corners |= {(cx + sx * i, cy + sy * t), (cx + sx * t, cy + sy * i)}
            gilt(p, corners, L)
        if st["line"]:
            pts = [(board_at(bx, by)[0] + s / 2, board_at(bx, by)[1] + s / 2) for bx, by in st["line"]]
            self.struck(p, b, pts, s * .3, 2 if small else 3,
                        p.once("strike", appear(3.0), z=.97) if moving else p.layer("strike", z=.97))
        if last and moving:
            x, y = cell(last["cell"])
            landing(h, p, x + q / 2, y + q / 2, q, (x0, y0, x0 + n, y0 + n), night)
        k = h.ink(night)
        t = FRAME[small]
        foot = y0 + n
        ly = min(foot + t + 2, h._trophy_room(p).y1 - 10)
        for i, f in enumerate(TC.FILES):
            x, _ = cell(f"{f}1")
            h.say(p, x + q // 2 + 1, ly, f, k["muted"], "57", anchor="middle")
        for r in range(1, 10):
            _, y = cell(f"a{r}")
            h.say(p, x0 - t - 2, y + q // 2 - 2, str(r), k["muted"], anchor="end")

    @staticmethod
    def struck(p, b, pts, ext, w, L) -> None:
        """A line struck through the centres of `pts`, run on by `ext` past each end, `w` either side of its middle:
        a rod of the trophies' gold, as the rules' fittings are, each pixel lit by how far it lies toward the lamp
        from the rod's axis, outlined in the gold's darkest, its shadow cast down and to the right on the boards."""
        G = METALS[3]
        (ax, ay), (bx, by) = pts[0], pts[-1]
        span = max(abs(bx - ax), abs(by - ay))
        ux, uy = (bx - ax) / span, (by - ay) / span
        ax, ay, bx, by = ax - ux * ext, ay - uy * ext, bx + ux * ext, by + uy * ext
        n = int(max(abs(bx - ax), abs(by - ay)))
        cells = set()
        for i in range(n + 1):
            x, y = round(ax + (bx - ax) * i / n), round(ay + (by - ay) * i / n)
            for dx in range(-w, w):
                for dy in range(-w, w):
                    cells.add((x + dx, y + dy))
        edge = {(x + dx, y + dy) for (x, y) in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - cells
        fall = 2 if w > 1 else 1
        for (x, y) in {(x + fall, y + fall) for (x, y) in cells | edge} - cells - edge:
            p.px(x, y, f"{b['shade']}:0.4", L)
        for (x, y) in edge:
            p.px(x, y, G[0], L)
        k = math.hypot(ux, uy)
        nx, ny = -uy / k, ux / k                        # across the rod
        for (x, y) in cells:
            lit = ((x + .5 - ax) * nx + (y + .5 - ay) * ny) / max(w, 1) * (nx * LX + ny * LY)
            p.px(x, y, G[5] if lit > .55 else G[4] if lit > .05 else G[3] if lit > -.6 else G[2], L)

    @staticmethod
    def drawn_in(p, d: tuple, mark: str, x: int, y: int) -> None:
        """The last mark drawn in as the pen draws it, a stroke at a time in eight steps: the X's falling stroke
        and then its rising one, the O round from its top."""
        cells = dict(d[0])
        w = d[1]
        n = 8
        groups: list = [dict() for _ in range(n)]
        for (cx, cy), col in cells.items():
            if mark == "X":
                falling = abs(cx - cy) <= abs((w - 1 - cx) - cy)
                t = (cx + cy) / (2 * w) if falling else ((w - 1 - cx) + cy) / (2 * w)
                i = min(n // 2 - 1, int(t * n / 2)) + (0 if falling else n // 2)
            else:
                a = (math.atan2(cx - w / 2, -(cy - w / 2)) / (2 * math.pi)) % 1
                i = min(n - 1, int(((1 - a) % 1) * n))
            groups[i][(cx, cy)] = col
        for i, group in enumerate(groups):
            if group:
                L = p.once(f"pen{i}", appear(.45 + i * .1), z=.8)
                for (cx, cy), col in group.items():
                    p.px(x + cx, y + cy, col, L)

    def count(self, h, p, st, x0, x1, y, night, small) -> int:
        """The boards each side has won, where chess counts what each side took: each won board's mark on its side's
        tray, both trays as long, three places at the least, the three in a row that win, the house's X on top on a
        tray of the board's dark, as its medallion sets it; and across the heading where the ghosts stand and how
        many boards were drawn. It counts and says nothing more."""
        k = h.ink(night)
        h.heading(p, x0, y, "boards won", night)
        said = ([f"ghost{'s' if len(st['ghosts']) > 1 else ''} " + " · ".join(st["ghosts"])] if st["ghosts"] else [])
        said += [f"{st['drawn']} drawn"] if st["drawn"] else []
        if said:
            h.say(p, x1, y, "  ·  ".join(said).upper(), k["muted"], anchor="end", room=(x1 - x0) // 2)
        y += 9
        b = h.game_board(night)
        label_w = max(measure(f"{TC.mark_of(s)} · {'house' if s == HOUSE else 'github'}".upper(), "35")
                      for s in (HOUSE, GITHUB)) + 6
        most, pitch = max(3, *st["won"].values()), 12
        for side in (HOUSE, GITHUB):
            mark = TC.mark_of(side)
            h.say(p, x0, y + 4, f"{mark} · {'house' if side == HOUSE else 'github'}".upper(), k["muted"])
            px_ = x0 + label_w
            won = st["won"][side]
            h.tray(p, px_ - 2, y - 1, most * pitch + 2, 13, night, stuff=b["dark_stuff"] if side == HOUSE else None)
            d = PC.pen(mark, "light" if mark == "X" else "dark", 9)
            for i in range(most):
                cx = px_ + i * pitch
                if i < won:
                    put(p, d, ("ttt", "mini", mark), cx, y + 1)
                else:
                    p.px(cx + d[1] // 2, y + 5, b["light"] if side == HOUSE else b["edge"])
            h.chip(p, px_ + most * pitch + 6, y + 1, str(won), night)
            y += 15
        return y - 3


# =========================================================================== pentago
# A quarter turn written small, seven pixels high: a circular arrow, its head the way the quarter went, open below
# its head so it never reads as a C.
TURNS = {"cw": ["..###..", ".#...#.", "#...###", "#....#.", "#......", ".#.....", "..##..."],
         "acw": ["..###..", ".#...#.", "###...#", ".#....#", "......#", ".....#.", "...##.."]}


def turning(cx: float, cy: float, way: str, at: float, steps_: int = 6) -> str:
    """A quarter turning its quarter turn about (cx, cy) in discrete steps from `at` seconds, from where it stood when
    its marble went in to where it rests, which is where it stands without SMIL and in the still file."""
    back = -90 if way == "cw" else 90
    angles = [back] + [round(back * (1 - i / steps_)) for i in range(steps_ + 1)]
    times = [0] + [at + .075 * i for i in range(steps_ + 1)]
    dur = times[-1] + .05
    values = ";".join(f"{a} {_n(cx)} {_n(cy)}" for a in angles)
    keys = ";".join(_n(round(t / dur, 3)) for t in times)
    return (f'<animateTransform attributeName="transform" type="rotate" values="{values}" keyTimes="{keys}" '
            f'dur="{_n(round(dur, 3))}s" calcMode="discrete" fill="freeze"/>')


def _n(v: float) -> str:
    return f"{v:g}"


class Pentago(Game):
    KIND, LABEL = "pentago", "pentago"

    def state(self, d: dict) -> dict:
        return PG.state(d)

    def side_name(self, side: str) -> str:
        return PG.COLOUR[side]

    def first(self, st: dict) -> str:
        return "drawn by the Arbiter"

    def notation(self, st: dict) -> tuple:
        if st["last"]:
            return super().notation(st)
        return f"{PG.GHOST}.", "?", st["places"], f"{name(st['places'])} sets the first ghost"

    def medallion(self, h, p, st, cx, cy, r, side, night) -> None:
        d = PC.disc(PG.material_of(side), r * .66)
        put(p, d, ("pg", "medal", r, side), cx - d[1] // 2, cy - d[2] // 2)

    @staticmethod
    def geometry(box: tuple, small: bool) -> dict:
        """The board's measures in units: a hole's pitch, a plate's margin and width, the gap between the plates,
        where the first plate stands, and a marble's radius. The plates stop a few units short of the box, so they
        lie in a bed inside the frame that shows all round them and between them, and a quarter turns clear of it."""
        x0, y0, n = box
        gap = 5 if small else 6
        pitch = 19 if small else 24
        m = 6 if small else 7
        q = 3 * pitch + 2 * m
        off = (n - 2 * q - gap) // 2
        return {"p": pitch, "m": m, "q": q, "gap": gap, "x": x0 + off, "y": y0 + off, "r": pitch * .37}

    @staticmethod
    def quarter_at(g: dict, qk: str) -> tuple:
        qx, qy = PG.QUARTERS[qk]
        return g["x"] + (0 if qx == 0 else g["q"] + g["gap"]), g["y"] + (0 if qy == 3 else g["q"] + g["gap"])

    def centre(self, g: dict, cell: str) -> tuple:
        x, y = PG.xy(cell)
        qk = PG.quarter_of(cell)
        qx, qy = PG.QUARTERS[qk]
        X, Y = self.quarter_at(g, qk)
        return X + g["m"] + (x - qx + .5) * g["p"], Y + g["m"] + (2 - (y - qy) + .5) * g["p"]

    @staticmethod
    def floor(b: dict, night: bool) -> MT.Stuff:
        """An empty hole's floor: the light stuff in the hole's shadow, flat, at the tone of its ramp nearest a middling
        lightness and below its own, far darker than a White marble's lit face, so an empty hole never reads as one."""
        ls = b["light_stuff"]
        want = 50 if night else 56
        nearest = min(range(len(ls.ramp)), key=lambda j: abs(lab(ls.ramp[j])[0] - want))
        return MT.Stuff(ls.ramp, min(nearest, max(0, ls.at - 1)), "flat")

    @staticmethod
    def hollow(p, floor: MT.Stuff, r: float, shade: str, night: bool) -> tuple:
        """An empty hole of radius `r`: its floor, and the plate's edge casting its shadow down and to the right across
        it, deepest along the hole's upper left, as the standard theme sinks an empty hole, so it reads as cut through
        the plate and never as a piece. Drawn once in the file, the shadow laid over the floor. Its key and size."""
        n = math.ceil(2 * r) + 2
        k = ("pghollow", floor.key, n, shade, night)
        if k not in p.syms:
            c = n / 2
            under, over = {}, {}
            for y in range(n):
                for x in range(n):
                    dx, dy = x + .5 - c, y + .5 - c
                    d = math.hypot(dx, dy)
                    if d >= r + .4:
                        continue
                    under[(x, y)] = floor.base
                    if d >= r - .3:
                        continue
                    if math.hypot(dx - 2.6, dy - 2.6) >= r:
                        over[(x, y)] = f"{shade}:{'0.7' if night else '0.55'}"
                    elif math.hypot(dx - 4.2, dy - 4.2) >= r and (x + y) % 2 == 0:
                        over[(x, y)] = f"{shade}:{'0.45' if night else '0.3'}"
            p.symbol(k, over, shapes=p._paths(under))
        return k, n

    def ghost(self, p, b, r: float, key: str) -> tuple:
        """A ghost marble of radius `r`, nobody's: the board's dark stuff lit as a coin is, its rim rolling off into
        shade, a ring of dashes of the light stuff round its face, outlined in the board's shade. Drawn once in the
        file. Its key and size."""
        n = math.ceil(2 * r)
        k = ("pgghost", key, n)
        if k not in p.syms:
            dark = b["dark_stuff"]
            c = n / 2
            body = {}
            for y in range(n):
                for x in range(n):
                    dx, dy = (x + .5 - c) / r, (y + .5 - c) / r
                    d = math.hypot(dx, dy)
                    if d > 1:
                        continue
                    lit = -(dx + dy) * .7
                    tone = (dark.tone(-2) if d > .86 and lit < 0 else dark.tone(1) if d > .86
                            else dark.tone(1) if lit > .35 else dark.base)
                    if abs(d - .62) < .1 and (x + y) % 3 != 0:
                        tone = b["light"]
                    body[(x + 1, y + 1)] = tone
            rim = {(x + dx, y + dy) for (x, y) in body for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - set(body)
            p.symbol(k, {**{xy: b["shade"] for xy in rim}, **body})
        return k, n + 2

    def board(self, h, p, st, box, night, moving, small) -> None:
        g = self.geometry(box, small)
        b = h.game_board(night)
        marks = h.game_marks(night)
        q, P, m, r = g["q"], g["p"], g["m"], g["r"]
        last = st["last"]
        played = bool(last and not last["ghost"])
        tq = last["quarter"] if played and last["turned"] else None
        rd = r - .2
        gk, gn = self.ghost(p, b, rd, f"{b['dark']}{b['light']}")
        # the board framed as chess's is, its quarters lying in a bed of the frame's stuff two tones down, worked in
        # its grain, laid where it shows, round the plates and between them; a neatline's bed is the chart's own
        # parchment, the light stuff a tone down
        x0, y0, n = box
        framed(h, p, x0, y0, n, n, night, small)
        fs, ls = b["frame"], b["light_stuff"]
        bed = (MT.Stuff(ls.ramp, max(0, ls.at - 1), ls.grain, ls.fleck) if b["style"] == "ink"
               else MT.Stuff(fs.ramp, max(0, fs.at - 2), "wood" if b["style"] == "wood" else fs.grain, fs.fleck))
        o, gap = g["x"] - x0, g["gap"]
        inner = n - 2 * o
        for (bx, by, bw, bh, along) in ((x0, y0, n, o, False), (x0, y0 + n - o, n, o, False),
                                        (x0, y0 + o, o, inner, True), (x0 + n - o, y0 + o, o, inner, True),
                                        (g["x"] + q, y0 + o, gap, inner, True), (x0 + o, g["y"] + q, inner, gap, False)):
            MT.lay(p, bed, bx, by, bw, bh, turned=along and bed.grain == "wood", L="bed", z=-1.2)
        hk, hn = self.hollow(p, self.floor(b, night), r, b["shade"], night)
        # the last move's ring and arrow edged in the board's light by day, when the set's accent is dark and may be
        # the plate's own tone, and in its shade by night, when the accent is light: either way they read on it
        rim = b["shade"] if night else b["light"]
        for qk in PG.QUARTERS:
            X, Y = self.quarter_at(g, qk)
            turn = turning(X + q / 2, Y + q / 2, last["way"], 1.05) if qk == tq and moving else ""

            def L(name_: str, z: float, also: str = "") -> str:
                if turn or also:
                    return p.once(f"{name_}{qk}", also + turn, z=z)
                return p.layer(f"{name_}", z=z)
            # its shadow, cast down and to the right, holding still while the quarter turns over it
            for yy in range(Y + 2, Y + q + 3):
                for xx in range(X + 2, X + q + 3):
                    if xx >= X + q or yy >= Y + q:
                        p.px(xx, yy, f"{b['shade']}:{'0.5' if night else '0.3'}")
            for cell in PG.quarter_cells(qk):
                v = st["cells"].get(cell)
                cx, cy = self.centre(g, cell)
                if not v:          # an empty hole, its floor in the shadow of the plate's edge, turning with it
                    p.use(hk, round(cx - hn / 2), round(cy - hn / 2), L("marbles", .2))
                    continue
                new = moving and last and cell == last["landed"]
                layer = L("new", .25, appear(.45)) if new else L("marbles", .2)
                if v == PG.GHOST:
                    p.use(gk, round(cx - gn / 2), round(cy - gn / 2), layer)
                    continue
                d = PC.disc("light" if v == "W" else "dark", rd)
                put(p, d, ("pg", "marble", rd, v), round(cx - d[1] / 2), round(cy - d[2] / 2), layer)
            self.face(p, b["dark_stuff"], g, X, Y, L("plate", .5))
            plate = L("edge", .52)             # its edge over its face: lit along its top and left, shaded below
            p.hline(X, X + q, Y, b["dark_stuff"].tone(1), plate)
            p.vline(X, Y, Y + q, b["dark_stuff"].tone(1), plate)
            p.hline(X, X + q, Y + q - 1, b["shade"], plate)
            p.vline(X + q - 1, Y, Y + q, b["shade"], plate)
            p.box(X - 1, Y - 1, q + 2, q + 2, b["shade"], plate)
            if last and PG.quarter_of(last["landed"]) == qk:
                cx, cy = self.centre(g, last["landed"])
                ring = L("ring", .55, appear(.75)) if moving else L("ring", .55)
                edged(p, ring_cells(cx, cy, r + 1.2) + ring_cells(cx, cy, r + 2.2), marks["last"], rim, ring)
        if last and moving:
            cx, cy = self.centre(g, last["cell"])
            landing(h, p, cx, cy, P, (x0, y0, x0 + n, y0 + n), night, at=.5)
        if tq:
            X, Y = self.quarter_at(g, tq)
            self.arrow(p, marks["last"], rim, X, Y, q, tq, last["way"],
                       p.once("turned", appear(1.05), z=.6) if moving else p.layer("turned", z=.6))
        if st["line"]:
            # the five that won, ringed and joined in the trophies' gold, as Tic-Tac's winning line is drawn
            pts = [self.centre(g, c) for c in st["line"]]
            at = 1.6 if tq else 1.2
            joined = set()
            for i, (cx, cy) in enumerate(pts):
                ringed = ring_cells(cx, cy, r + 1.2) + ring_cells(cx, cy, r + 2.2)
                if moving:          # ringed one after another, and then the five joined over them as they rest
                    gilt(p, ringed, p.once(f"five{i}", appear(at + i * .14), z=.555))
                joined |= set(ringed)
            Lf = p.once("five", appear(at + .75), z=.56) if moving else p.layer("five", z=.56)
            (ax, ay), (bx, by) = pts[0], pts[-1]
            steps_ = int(max(abs(bx - ax), abs(by - ay)))
            for i in range(steps_ + 1):
                x, y = round(ax + (bx - ax) * i / steps_), round(ay + (by - ay) * i / steps_)
                joined |= {(x - 1, y - 1), (x, y - 1), (x - 1, y), (x, y)}
            gilt(p, joined, Lf)
        k = h.ink(night)
        t = FRAME[small]
        ly = min(y0 + n + t + 2, h._trophy_room(p).y1 - 10)      # under the frame, as chess's files are
        for f in PG.FILES:
            cx, _ = self.centre(g, f"{f}1")
            h.say(p, round(cx) + 1, ly, f, k["muted"], "57", anchor="middle")
        for row in range(1, 7):     # left of the frame, as chess's ranks are
            _, cy = self.centre(g, f"a{row}")
            h.say(p, x0 - t - 2, round(cy) - 2, str(row), k["muted"], anchor="end")

    @staticmethod
    def face(p, stuff: MT.Stuff, g: dict, X: int, Y: int, L: str) -> None:
        """A quarter's face: a cell of the stuff round each hole, drawn once in each of three variants and set at
        every hole, and the margins round them laid in the stuff."""
        P, m, r = g["p"], g["m"], g["r"]
        for v in range(3):
            key = ("pgcell", stuff.key, P, v)
            if key in p.syms:
                continue
            cells = {}
            c0 = P / 2
            for (x, y), col in MT.surface(stuff, P, P, v).items():
                d = math.hypot(x + .5 - c0, y + .5 - c0)
                if d < r:
                    continue
                if d < r + 1.2:
                    away = (x + .5 - c0) * -.7 + (y + .5 - c0) * -.7 > 0
                    col = stuff.tone(-3) if away else stuff.tone(1)
                cells[(x, y)] = col
            p.symbol(key, cells)
        for i in range(3):
            for j in range(3):
                p.use(("pgcell", stuff.key, P, (i * 2 + j) % 3), X + m + i * P, Y + m + j * P, L)
        q = g["q"]
        for (x, y, ww, hh, turned) in ((X, Y, q, m, False), (X, Y + q - m, q, m, False),
                                       (X, Y + m, m, q - 2 * m, True), (X + q - m, Y + m, m, q - 2 * m, True)):
            MT.lay(p, stuff, x, y, ww, hh, turned=turned and stuff.grain == "wood", L=L)

    @staticmethod
    def arrow(p, colour: str, edge: str, X: int, Y: int, q: int, qk: str, way: str, L: str) -> None:
        """The way the last quarter turned: an arrow two pixels wide round its outer corner, along the plate's very
        edge, clear of a ringed hole, from the middle of one outer edge round the corner to the middle of the other,
        its head the way the quarter went."""
        inset = 1
        sx = 1 if qk in ("ul", "ll") else -1
        sy = 1 if qk in ("ul", "ur") else -1
        cx = X + inset if sx > 0 else X + q - 2 - inset
        cy = Y + inset if sy > 0 else Y + q - 2 - inset
        half = q // 2 - inset
        down = [(cx, cy + sy * i) for i in range(half)]          # along the outer side edge
        across = [(cx + sx * i, cy) for i in range(half)]        # along the outer top or bottom edge
        path = (down[::-1] + across[1:]) if (qk in ("ul", "lr")) == (way == "cw") else (across[::-1] + down[1:])
        cells = {(x + dx, y + dy) for (x, y) in path[:-3] for dx in (0, 1) for dy in (0, 1)}
        (ex, ey), (fx_, fy_) = path[-1], path[-2]
        ux, uy = ex - fx_, ey - fy_
        for i in range(3):                       # the head, widest at its back, its tip at the path's end
            bx, by = ex - ux * (2 - i), ey - uy * (2 - i)
            w = 2 - i
            for s_ in range(-w, w + 2):          # across the shaft's two pixels, and as far again either side
                cells.add((bx + (s_ if uy else 0), by + (s_ if ux else 0)))
        edged(p, cells, colour, edge, L)

    def glyph(self, h, p, st, side, x, y, scale, night) -> int:
        """The marble a move is set with, set before its hole: Black ringed in the muted ink after dark, so it holds
        on the night sky as White does."""
        r = 3.5 if scale > 1 else 2.5
        d = PC.disc(PG.material_of(side), r)
        gy = y + (7 * scale - d[2]) // 2
        if night and PG.material_of(side) == "dark":
            for (cx, cy) in ring_cells(x + d[1] / 2, gy + d[2] / 2, d[1] / 2 + .6):
                p.px(cx, cy, h.ink(night)["muted"])
        put(p, d, ("pg", "glyph", r, side), x, gy)
        return d[1] + 2

    def opening_glyph(self, h, p, st, side, x, y, scale, night) -> int:
        """Before the first ghost, the move to come is a ghost, whoever sets it: a ghost before its hole, as the move
        will be written once it is set."""
        r = 3.5 if scale > 1 else 2.5
        b = h.game_board(night)
        gk, gn = self.ghost(p, b, r, f"{b['dark']}{b['light']}")
        p.use(gk, x, y + (7 * scale - gn) // 2)
        return gn + 2

    def glyph_width(self, scale: int) -> int:
        return (9 if scale > 1 else 7) + 2

    def write(self, h, p, st, side, move, x, y, scale, night, title=False) -> int:
        """A move as the sheet writes it: the marble's colour, its hole, and the quarter turn after it, a circular
        arrow and the quarter's initials; a ghost's, the ghost and its hole."""
        k = h.ink(night)
        x0 = x
        mv = PG.parse(move)
        if mv["quarter"] is None and not mv["won"]:
            b = h.game_board(night)
            rr = 3.5 if scale > 1 else 2.5
            gk, gn = self.ghost(p, b, rr, f"{b['dark']}{b['light']}")
            p.use(gk, x, y + (7 * scale - gn) // 2)
            x += gn + 2
        else:
            x += self.glyph(h, p, st, side, x, y, scale, night)

        def letters(s: str, at: int) -> int:
            if title:
                return h.game_title(p, at, y, fold(s, "57"), night, scale)
            return h.say(p, at, y, s, k["body"], "57")
        x += letters(mv["cell"] + ("#" if mv["won"] and not mv["quarter"] else ""), x)
        if mv["quarter"]:
            x += 2 * scale
            p.sprite(x, y, TURNS[mv["way"]], {"#": k["title"] if title else k["body"]}, s=scale)
            x += 7 * scale + 2 * scale
            x += letters(mv["quarter"].upper() + ("#" if mv["won"] else ""), x)
        return x - x0

    def written(self, move: str, scale: int) -> int:
        mv = PG.parse(move)
        w = self.glyph_width(scale) + measure(fold(mv["cell"] + ("#" if mv["won"] and not mv["quarter"] else ""),
                                                   "57"), "57", scale)
        if mv["quarter"]:
            w += 2 * scale + 9 * scale + measure(fold(mv["quarter"].upper() + ("#" if mv["won"] else ""), "57"),
                                                 "57", scale)
        return w

    def count(self, h, p, st, x0, x1, y, night, small) -> int:
        """Each side's marbles left, a rack of seventeen emptying as the board fills, the house's White first on a
        tray of the board's dark, as its medallion sets it; and across the heading where the ghosts stand now."""
        k = h.ink(night)
        h.heading(p, x0, y, "marbles left", night)
        if st["ghosts"]:
            said = f"ghost{'s' if len(st['ghosts']) > 1 else ''} " + " · ".join(st["ghosts"])
            h.say(p, x1, y, said.upper(), k["muted"], anchor="end", room=(x1 - x0) // 2)
        y += 9
        b = h.game_board(night)
        label_w = max(measure(f"{PG.COLOUR[s]} · {'house' if s == HOUSE else 'github'}".upper(), "35")
                      for s in (HOUSE, GITHUB)) + 6
        for side in (HOUSE, GITHUB):
            mat = PG.material_of(side)
            h.say(p, x0, y + 4, f"{PG.COLOUR[side]} · {'house' if side == HOUSE else 'github'}".upper(), k["muted"])
            px_ = x0 + label_w
            left = st["left"][side]
            chip = measure(str(left), "35") + 8
            room = x1 - px_ - chip - 6
            pitch = max(3, min(7, (room - 4) // PG.EACH))
            h.tray(p, px_ - 2, y - 1, PG.EACH * pitch + 4, 13, night, stuff=b["dark_stuff"] if side == HOUSE else None)
            d = PC.disc(mat, 2.5 if pitch >= 6 else 2)
            for i in range(PG.EACH):
                cx = px_ + i * pitch
                if i < left:
                    put(p, d, ("pg", "rack", pitch, mat), cx, y + 5 - d[2] // 2 + 1)
                else:
                    p.px(cx + d[1] // 2, y + 5, b["light"] if side == HOUSE else b["edge"])
            h.chip(p, px_ + PG.EACH * pitch + 6, y + 1, str(left), night)
            y += 15
        return y - 3


GAMES = {"chess": Chess(), "checkers": Checkers(), "pentago": Pentago(), "tictac": TicTac()}
