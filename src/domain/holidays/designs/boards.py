# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
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
  Connect Four  a frame of the set's dark colour on two legs, seven columns of holes, the discs behind it; the last
                disc is held over its column and drops down it, glimpsed through each hole, bouncing as it lands;
                a won four are ringed and joined. The panel counts each side's discs left on a rack of twenty-one
  Tic-Tac-Toe   three cells a side, the bars between them the board's dark colour, all eight lines a game is won on
                dotted faint while it goes on, whatever stands on them; the last mark draws itself stroke by stroke;
                a won line is struck through. The panel counts each side's marks left, a rack of five for the side
                that moved first and four for the other

Nothing on a board helps a player choose a move, as on every look's: no hole or cell a side could win on next, no
call to block, no word of what perfect play makes of a game. A king in check and a man that must jump glow in the
set's red, since those are the rules, not hints.
"""
from __future__ import annotations

import math

from ...elements.checkers import game as CK
from ...elements.chess import game as CG
from ...elements.chess.layout import castled, finished, outcome, passed
from ...elements.connectfour import game as C4
from ...elements.games import data as GD
from ...elements.games.sides import GITHUB, HOUSE, name, other, playing
from ...elements.tictactoe import game as TT
from ..pixel import GLYPHS, fold, measure
from . import materials as MT
from . import pieces as PC
from .games import LAND, _nothing, appear, brief, gone, pulse, steps

# The marks on each game's tag, seven pixels high, in the tag's ink.
MARKS = {
    "chess": ["..#..", ".###.", ".###.", "..#..", ".###.", ".###.", "#####"],
    "checkers": ["#.#.#", "#####", ".....", "#####", "#...#", "#####", "....."],
    "connectfour": ["#######", "#.#.#.#", "#######", "#.#.#.#", "#######", ".#...#.", ".#...#."],
    "tictactoe": ["#.#.###", ".#..#.#", "#.#.###", ".......", "###.#.#", "#.#..#.", "###.#.#"],
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


def dotted(p, cells, colour: str, L: str) -> None:
    """An outline round `cells`, every other pixel: where a piece would stand, or where it stood."""
    ring = {(x + dx, y + dy) for (x, y) in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - set(cells)
    for (x, y) in ring:
        if (x + y) % 2 == 0:
            p.px(x, y, colour, L)


def landing(h, p, cx: float, cy: float, s: int, box: tuple, night: bool) -> None:
    """The landing, as a move comes down: a flash on its square, and a ring running out from it in three steps."""
    marks = h.game_marks(night)
    flash = {(x, y): f"{PC.IVORY[6]}:0.55" for y in range(int(cy - s / 2), int(cy + s / 2))
             for x in range(int(cx - s / 2), int(cx + s / 2))}
    p.raw(.9, brief(within(flash, box), LAND, .12), "")
    for i, r in enumerate((s * .45, s * .7, s * .95)):
        cells = {xy: marks["last"] for xy in ring_cells(cx, cy, r)}
        p.raw(.9, brief(within(cells, box), LAND + .06 + i * .07, .07), "")


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


# =========================================================================== connect four
class ConnectFour(Game):
    KIND, LABEL = "connectfour", "connect four"

    def state(self, d: dict) -> dict:
        return C4.state(d)

    def side_name(self, side: str) -> str:
        return C4.COLOUR[side]

    def first(self, st: dict) -> str:
        return f"{C4.COLOUR[st['opens']]} drops first"

    def glyph(self, h, p, st, side, x, y, scale, night) -> int:
        """The disc a move is dropped with, set before its column's number."""
        r = 3.5 if scale > 1 else 2.5
        d = PC.disc(C4.material_of(side), r)
        put(p, d, ("c4", "glyph", r, side), x, y + (7 * scale - d[2]) // 2)
        return d[1] + 2

    def glyph_width(self, scale: int) -> int:
        return (9 if scale > 1 else 7) + 2

    def medallion(self, h, p, st, cx, cy, r, side, night) -> None:
        d = PC.disc(C4.material_of(side), r * .66)
        put(p, d, ("c4", "medal", r, side), cx - d[1] // 2, cy - d[2] // 2)

    @staticmethod
    def geometry(box: tuple, small: bool) -> dict:
        x0, y0, n = box
        pitch = 19 if small else 23
        m = 4 if small else 5
        w, ht = C4.COLS * pitch + 2 * m, C4.ROWS * pitch + 2 * m
        top = 16 if small else 20
        fx0, fy0 = x0 + (n - w) // 2, y0 + top
        legs = 6 if small else 8
        return {"p": pitch, "m": m, "x": fx0, "y": fy0, "w": w, "h": ht, "top": top, "legs": legs,
                "ground": fy0 + ht + legs, "r": pitch * .37}

    def height(self, n: int, small: bool = False) -> int:
        g = self.geometry((0, 0, n), small)
        return g["ground"] + 8

    @staticmethod
    def centre(g: dict, col: int, row: int) -> tuple:
        return (g["x"] + g["m"] + (col - .5) * g["p"], g["y"] + g["m"] + (C4.ROWS - row + .5) * g["p"])

    def board(self, h, p, st, box, night, moving, small) -> None:
        g = self.geometry(box, small)
        b = h.game_board(night)
        marks = h.game_marks(night)
        k = h.ink(night)
        last = st["last"]
        # the legs and the ground they stand on, behind the frame
        ly = g["y"] + g["h"]
        lw = g["m"] + 4
        for lx in (g["x"] + 2, g["x"] + g["w"] - 2 - lw):
            for i in range(g["legs"]):
                p.hline(lx - i // 3, lx + lw + i // 3, ly + i, b["edge"])
            p.vline(lx - g["legs"] // 3, ly, ly + g["legs"], b["dark"])
        p.hline(g["x"] - 6, g["x"] + g["w"] + 6, g["ground"], b["shade"])
        # the discs, behind the plate
        holes = {(col, row): self.centre(g, col, row) for col in range(1, C4.COLS + 1) for row in range(1, C4.ROWS + 1)}
        rd = g["r"] - .2
        for (col, row), v in sorted(st["board"].items()):
            cx, cy = holes[(col, row)]
            mat = "light" if v == "L" else "dark"
            d = PC.disc(mat, rd)
            x, y = round(cx - d[1] / 2), round(cy - d[2] / 2)
            if last and moving and (col, row) == (last["column"], last["row"]):
                hold = g["y"] - g["top"] // 2 - d[2] // 2 - 1
                drop = y - hold
                offsets, times = [(0, -drop), (0, -drop)], [0, .5]
                n = max(2, round(drop / g["p"] * 1.5))
                for i in range(1, n + 1):
                    f = (i / n) ** 2
                    offsets.append((0, round(-drop * (1 - f))))
                    times.append(.5 + .45 * i / n)
                land = times[-1]
                offsets += [(0, -3), (0, 0), (0, -1), (0, 0)]
                times += [land + .08, land + .16, land + .22, land + .28]
                L = p.once("mover", steps(offsets, times, land + .33) + appear(.2), z=.3)
                put(p, d, ("c4", "disc", rd, mat), x, y, L)
                continue
            put(p, d, ("c4", "disc", rd, mat), x, y, p.layer("discs", z=.2))
        # the plate: the frame's face in the dark stuff, every hole cut through it, its wall shaded where it faces
        # away from the lamp and lit where it faces it, the plate lit along its top and left
        plate = p.layer("plate", z=.5)
        r = g["r"]
        self.face(p, b["dark_stuff"], g, plate)
        p.hline(g["x"], g["x"] + g["w"], g["y"], b["dark_stuff"].tone(1), plate)
        p.vline(g["x"], g["y"], g["y"] + g["h"], b["dark_stuff"].tone(1), plate)
        p.hline(g["x"], g["x"] + g["w"], g["y"] + g["h"] - 1, b["shade"], plate)
        p.vline(g["x"] + g["w"] - 1, g["y"], g["y"] + g["h"], b["shade"], plate)
        p.box(g["x"] - 1, g["y"] - 1, g["w"] + 2, g["h"] + 2, b["shade"], plate)
        if last:
            cx, cy = holes[(last["column"], last["row"])]
            for (x, y) in ring_cells(cx, cy, r + 1.2):
                p.px(x, y, marks["last"], p.once("lastring", appear(1.3), z=.55) if moving else plate)
        if st["line"]:
            pts = [holes[(col, row)] for col, row in st["line"]]
            L = p.once("four", appear(1.7), z=.56) if moving else plate
            for (cx, cy) in pts:
                for (x, y) in ring_cells(cx, cy, r + 1.2):
                    p.px(x, y, marks["last"], L)
            (ax, ay), (bx, by) = pts[0], pts[-1]
            n = int(max(abs(bx - ax), abs(by - ay)))
            for i in range(n + 1):
                x, y = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
                p.rect(round(x) - 1, round(y) - 1, 2, 2, marks["last"], L)
        under = g["ground"] + 3
        for col in range(1, C4.COLS + 1):
            cx = round(holes[(col, 1)][0])
            if last and col == last["column"]:
                w = measure(str(col), "35") + 6
                L = p.once("colmark", appear(.2), z=.55) if moving else "base"
                with p.onto(L) if L != "base" else _nothing():
                    h.tag(p, cx - w // 2, under - 2, w, 9, night)
                p.text(cx - w // 2 + 3, under, str(col), k["tag_ink"], "35", L=L)
                p.sprite(cx - 1, g["y"] - 5, ["###", ".#."], {"#": marks["last"]}, L=L)
                continue
            h.say(p, cx, under, str(col), k["muted"], anchor="middle")
        for row in range(1, C4.ROWS + 1):
            h.say(p, g["x"] - 6, round(holes[(1, row)][1]) - 2, str(row), k["muted"], anchor="middle")

    @staticmethod
    def face(p, stuff: MT.Stuff, g: dict, L: str) -> None:
        """The frame's face: a cell of the stuff round each hole, drawn once in each of three variants and set at
        every hole, and the margins round them laid in the stuff."""
        P, m, r = g["p"], g["m"], g["r"]
        for v in range(3):
            key = ("c4cell", stuff.key, P, v)
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
        for col in range(C4.COLS):
            for row in range(C4.ROWS):
                p.use(("c4cell", stuff.key, P, (col * 2 + row) % 3), g["x"] + m + col * P, g["y"] + m + row * P, L)
        x0, y0, w, ht = g["x"], g["y"], g["w"], g["h"]
        for (x, y, ww, hh, turned) in ((x0, y0, w, m, False), (x0, y0 + ht - m, w, m, False),
                                       (x0, y0 + m, m, ht - 2 * m, True), (x0 + w - m, y0 + m, m, ht - 2 * m, True)):
            MT.lay(p, stuff, x, y, ww, hh, turned=turned and stuff.grain == "wood", L=L)

    def count(self, h, p, st, x0, x1, y, night, small) -> int:
        """Each side's discs left, a rack of twenty-one emptying as the frame fills, the house's White first."""
        k = h.ink(night)
        h.heading(p, x0, y, "discs left", night)
        y += 9
        b = h.game_board(night)
        label_w = max(measure(f"{C4.COLOUR[s]} · {'house' if s == HOUSE else 'github'}".upper(), "35")
                      for s in (HOUSE, GITHUB)) + 6
        for side in (HOUSE, GITHUB):
            mat = C4.material_of(side)
            h.say(p, x0, y + 4, f"{C4.COLOUR[side]} · {'house' if side == HOUSE else 'github'}".upper(), k["muted"])
            px_ = x0 + label_w
            left = st["left"][side]
            chip = measure(str(left), "35") + 8
            room = x1 - px_ - chip - 6
            pitch = max(3, min(6, (room - 4) // C4.EACH))
            h.tray(p, px_ - 2, y - 1, C4.EACH * pitch + 4, 13, night)
            d = PC.disc(mat, 2.5 if pitch >= 6 else 2)
            for i in range(C4.EACH):
                cx = px_ + i * pitch
                if i < left:
                    put(p, d, ("c4", "rack", pitch, mat), cx, y + 5 - d[2] // 2 + 1)
                else:
                    p.px(cx + d[1] // 2, y + 5, b["edge"])
            h.chip(p, px_ + C4.EACH * pitch + 6, y + 1, str(left), night)
            y += 15
        return y - 3


# =========================================================================== tic-tac-toe
class TicTacToe(Game):
    KIND, LABEL = "tictactoe", "tic-tac-toe"

    def state(self, d: dict) -> dict:
        return TT.state(d)

    def side_name(self, side: str) -> str:
        return TT.mark_of(side)

    def first(self, st: dict) -> str:
        return f"{TT.mark_of(st['opens'])} moves first"

    def medallion(self, h, p, st, cx, cy, r, side, night) -> None:
        mark = TT.mark_of(side)
        size = 2 * r - 6
        d = PC.pen(mark, "light" if mark == "X" else "dark", size)
        put(p, d, ("ttt", "medal", size, mark), cx - d[1] // 2, cy - d[2] // 2)

    @staticmethod
    def geometry(n: int, small: bool) -> tuple:
        bar = 4 if small else 5
        c = (n - 2 * bar) // 3
        return c, bar

    def board(self, h, p, st, box, night, moving, small) -> None:
        x0, y0, n = box
        c, bar = self.geometry(n, small)
        b = h.game_board(night)
        marks = h.game_marks(night)
        framed(h, p, x0, y0, n, n, night, small)
        dark, light = b["dark_stuff"], b["light_stuff"]
        for i in (1, 2):         # the bars, in the dark stuff, the uprights' grain turned
            MT.lay(p, dark, x0 + i * c + (i - 1) * bar, y0, bar, n, turned=True)
            MT.lay(p, dark, x0, y0 + i * c + (i - 1) * bar, n, bar)

        def cell(name: str) -> tuple:
            i, j = TT.FILES.index(name[0]), 3 - int(name[1])
            return x0 + i * (c + bar), y0 + j * (c + bar)

        for row in (1, 2, 3):
            for f in TT.FILES:
                x, y = cell(f"{f}{row}")
                MT.lay(p, light, x, y, c, c, L="cells", z=-.9)
        last = st["last"]
        if last:
            x, y = cell(last["cell"])
            for yy in range(y, y + c):
                for xx in range(x, x + c):
                    p.px(xx, yy, f"{marks['glow']}:0.45")
            p.box(x + 1, y + 1, c - 2, c - 2, marks["last"])
        if not st["result"]:
            # the eight lines a game is won on, dotted faint as a drawing draws its centre lines: all eight, whatever
            # stands on them, so the board never singles out a line a side could still win on, or one no side can
            for line in TT.LINES:
                (ax, ay), (bx, by) = [(cell(q)[0] + c / 2, cell(q)[1] + c / 2) for q in (line[0], line[-1])]
                steps_ = int(max(abs(bx - ax), abs(by - ay)))
                for i in range(-int(c * .4), steps_ + int(c * .4), 4):
                    p.px(ax + (bx - ax) * i / steps_, ay + (by - ay) * i / steps_, f"{b['edge']}:0.5")
        size = c - 12
        men = p.layer("men", z=.7)
        for name_, mark in st["board"].items():
            x, y = cell(name_)
            d = PC.pen(mark, "light" if mark == "X" else "dark", size)
            px_, py_ = x + (c - d[1]) // 2, y + (c - d[2]) // 2
            if last and moving and name_ == last["cell"]:
                self.drawn_in(p, d, mark, px_, py_)
                continue
            put(p, d, ("ttt", mark, size), px_, py_, men)
        if st["line"]:
            (ax, ay), (bx, by) = [(cell(q)[0] + c / 2, cell(q)[1] + c / 2) for q in (st["line"][0], st["line"][-1])]
            ext = c * .3
            span = max(abs(bx - ax), abs(by - ay))
            ux, uy = (bx - ax) / span, (by - ay) / span
            ax, ay, bx, by = ax - ux * ext, ay - uy * ext, bx + ux * ext, by + uy * ext
            n = int(max(abs(bx - ax), abs(by - ay)))
            w = 2 if small else 3
            cells = {}
            for i in range(n + 1):
                x, y = round(ax + (bx - ax) * i / n), round(ay + (by - ay) * i / n)
                for dx in range(-w, w):
                    for dy in range(-w, w):
                        cells[(x + dx, y + dy)] = marks["last"]
            edge = {(x + dx, y + dy) for (x, y) in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - set(cells)
            L = p.once("strike", appear(1.6), z=.9) if moving else p.layer("strike", z=.9)
            for (x, y) in edge:
                p.px(x, y, b["shade"], L)
            for (x, y), col in cells.items():
                p.px(x, y, col, L)
        if last and moving:
            x, y = cell(last["cell"])
            landing(h, p, x + c / 2, y + c / 2, c, (x0, y0, x0 + n, y0 + n), night)
        self.labels(h, p, x0, y0, c + bar, c, TT.FILES, 3, night, small)

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
        """Each side's marks left, where chess counts what each side took: a rack of five for the side that moved
        first and four for the other, emptying as the board fills, a used place keeping an empty cell's dot, the
        house's X on top. It counts and says nothing more: no cell a side could win on next, and no word of what
        perfect play makes of the game."""
        k = h.ink(night)
        h.heading(p, x0, y, "marks left", night)
        y += 9
        b = h.game_board(night)
        label_w = max(measure(f"{TT.mark_of(s)} · {'house' if s == HOUSE else 'github'}".upper(), "35")
                      for s in (HOUSE, GITHUB)) + 6
        most, pitch = max(st["each"].values()), 12
        for side in (HOUSE, GITHUB):
            mark = TT.mark_of(side)
            h.say(p, x0, y + 4, f"{mark} · {'house' if side == HOUSE else 'github'}".upper(), k["muted"])
            px_ = x0 + label_w
            left = st["left"][side]
            h.tray(p, px_ - 2, y - 1, st["each"][side] * pitch + 2, 13, night)
            d = PC.pen(mark, "light" if mark == "X" else "dark", 9)
            for i in range(st["each"][side]):
                cx = px_ + i * pitch
                if i < left:
                    put(p, d, ("ttt", "mini", mark), cx, y + 1)
                else:
                    p.px(cx + d[1] // 2, y + 5, b["edge"])
            h.chip(p, px_ + most * pitch + 6, y + 1, str(left), night)
            y += 15
        return y - 3


GAMES = {"chess": Chess(), "checkers": Checkers(), "connectfour": ConnectFour(), "tictactoe": TicTacToe()}
