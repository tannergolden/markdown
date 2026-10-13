# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Tic-Tac's replay board: the profile's nine boards, every turn played with the README's own last-move motion.

The two ghosts appear in their squares as the pen would touch down. Each mark draws itself stroke by stroke as the
pen would, its square boxed as the pen lifts and a ring running out from it. A mark that wins its board strikes the
board's three, the board is washed back and its winner's mark drawn across it as large as the board, the closing
square kept clear of the wash until the next turn; a drawn board is washed back and lined across. The board the next
mark is sent to is bracketed at its corners once the pen has done, as the README brackets it, and the mark that wins
the game strikes its three boards. Nothing moves here that the README's board does not move.
"""
from __future__ import annotations

from ...canvas import c
from ...lettering import f1, fx
from ..tictac import layout as TL
from ..tictac.game import GHOST, board_at, board_of, boards, target, won_line
from ..tictac.motion import CLAIM_AT, DRAW, DRAW_AT, LIFT, STRIKE, STRIKE_AT, WIN_AT
from ..tictac.shapes import LENGTH, strokes
from ..tictac.skins import geometry
from .common import GameReplay, captured, ripples
from .sheet import N, X0, Y0, Plan

GHOST_IN = .3                                   # a ghost appearing, as the README brings it in
BOX = LIFT - .05 - DRAW_AT                      # each beat below counts from the pen touching down
STRUCK = STRIKE_AT - DRAW_AT
WASHED = CLAIM_AT - .1 - DRAW_AT
CLAIMED = CLAIM_AT - DRAW_AT
DONE = CLAIMED + DRAW
WON = WIN_AT - DRAW_AT


def material(mark: str) -> str:
    return TL.material(mark)


class TicTac(GameReplay):
    KEY, LABEL = "tictac", TL.LABEL
    layout = TL
    SIDE_WORD = {"house": "x", "github": "o"}

    @staticmethod
    def story(plies) -> list[dict]:
        """Each turn with what it did to the boards: the squares after it, the board it closed and how, the three
        that won it, and the board the next mark is sent to."""
        squares: dict[str, str] = {}
        closed = boards(squares)
        out = []
        for p in plies:
            squares = {**squares, p["cell"]: p["mark"]}
            now = boards(squares)
            b = board_of(p["cell"])
            claimed = now[b] if p["mark"] != GHOST and closed[b] is None and now[b] else None
            line = won_line(squares, b, p["mark"]) if claimed in ("X", "O") else None
            out.append({"claimed": claimed, "board": b, "line": line,
                        "target": target(squares, now, p["cell"]) if p["mark"] != GHOST else None})
            closed = now
        return out

    @classmethod
    def durations(cls, plies) -> list[tuple[float, float]]:
        out = []
        for i, (p, s) in enumerate(zip(plies, cls.story(plies))):
            if p["mark"] == GHOST:
                out.append((GHOST_IN, .7))
            elif s["claimed"] == "draw":
                out.append((DRAW, WASHED + .25 - DRAW + .5))
            elif s["claimed"]:
                out.append((DRAW, (WON + STRIKE if i == len(plies) - 1 else DONE) - DRAW + .6))
            else:
                out.append((DRAW, .9))
        return out

    @classmethod
    def board(cls, cv, sk, pl: Plan, f: dict, layer: str) -> None:
        clk = pl.clock
        plies, beats = f["plies"], pl.beats
        story = cls.story(plies)
        nxt = [pl.after(i) for i in range(len(beats))]
        bar, gut, s, q = geometry(N, False)
        box = q * .86
        sk.board_base(cv, X0, Y0, N, False)
        # the square each mark goes in, boxed as the pen lifts, until the next turn starts
        x0, y0, q0 = TL.cell_box("a9", X0, Y0, N, False)
        cell = captured(cv, sk.cell_mark, x0, y0, q0, q0, "")
        steps, top = [(0, "0 0")], [(0, 0)]
        for i, (p, b) in enumerate(zip(plies, beats)):
            if p["mark"] == GHOST:
                continue
            x, y, _ = TL.cell_box(p["cell"], X0, Y0, N, False)
            steps.append((b.start, f"{f1(x - x0)} {f1(y - y0)}"))
            at = b.start + BOX * b.k
            top += [(b.start, 0), (at, 0), (at + .2 * b.k, 1), (nxt[i], 1), (nxt[i], 0)]
        cv.add(f'<g>{layer}<g opacity="0">{clk.anim("opacity", top)}<g>'
               f'{clk.anim("transform", steps, transform="translate", discrete=True)}{cell}</g></g></g>')
        clip = cv.uid("b")
        cv.defs.append(f'<clipPath id="{clip}"><rect x="{f1(X0)}" y="{f1(Y0)}" width="{f1(N)}" height="{f1(N)}"/>'
                       "</clipPath>")
        sk.board_over(cv, clip, X0, Y0, N / 8, None, "")
        # every square: its centre mark until a turn takes it, then its ghost or its mark drawn in by the pen
        taken = {p["cell"]: (p, b) for p, b in zip(plies, beats)}
        marks = []
        for cname in (f"{fl}{r}" for r in range(9, 0, -1) for fl in "abcdefghi"):
            cx, cy = TL.centre(cname, X0, Y0, N, False)
            dot = sk.centre_mark(cx, cy, q * .14)
            if cname not in taken:
                marks.append(dot)
                continue
            p, b = taken[cname]
            marks.append(f'<g>{clk.windows([(0, b.start)])}{dot}</g>')
            if p["mark"] == GHOST:
                gx, gy, gq = TL.cell_box(cname, X0, Y0, N, False)
                marks.append(sk.ghost(cv, gx, gy, gq, clk.appear(b.start, GHOST_IN * b.k)))
                continue
            drawn = sk.pen_mark(cv, p["mark"], material(p["mark"]), cx - box / 2, cy - box / 2, box, edge=1.05)
            marks.append(cls.pen(cv, clk, drawn, p["mark"], cx - box / 2, cy - box / 2, box, b.start,
                                 b.land - b.start))
        cv.add(f'<g>{layer}' + "".join(marks) + "</g>")
        # the pen lifts, or the ghost is down: a ring running out from it
        points = []
        for p, b in zip(plies, beats):
            cx, cy = TL.centre(p["cell"], X0, Y0, N, False)
            points.append((cx, cy, b.land, b.start, b.k))
        cv.add(f"<g>{layer}" + ripples(clk, sk, clip, points, q * .32, q * .7) + "</g>")
        # the boards each turn closed: struck, washed back and claimed, the closing square kept clear until the next
        closing = []
        for i, (p, b, st) in enumerate(zip(plies, beats, story)):
            if not st["claimed"]:
                continue
            k = b.k
            X, Y, _ = TL.board_box(st["board"], X0, Y0, N, False)
            if st["line"]:
                d, length = TL.struck([TL.centre(cl, X0, Y0, N, False) for cl in st["line"]], X0, Y0, N, False,
                                      q * .3)
                struck = sk.strike(d, 3.2, *cls.stroke(clk, length, b.start + STRUCK * k, STRIKE * k))
                closing.append(f'<g>{clk.windows([(0, nxt[i])])}{struck}</g>' if i < len(plies) - 1 else struck)
            lx, ly, lq = TL.cell_box(p["cell"], X0, Y0, N, False)
            lb = lq * .86
            keep = (f'<g visibility="hidden">{clk.windows([(b.start + WASHED * k, nxt[i])])}' + sk.kept(lx, ly, lq)
                    + sk.pen_mark(cv, p["mark"], material(p["mark"]), lx + (lq - lb) / 2, ly + (lq - lb) / 2, lb,
                                  edge=1.05) + "</g>")
            appear = clk.appear(b.start + WASHED * k, .25 * k)
            if st["claimed"] == "draw":
                closing.append(f"<g>{appear}{sk.wash(X, Y, s)}{sk.drawn(cv, X, Y, s)}</g>{keep}")
                continue
            B = s * .9
            big = sk.pen_mark(cv, st["claimed"], material(st["claimed"]), X + (s - B) / 2, Y + (s - B) / 2, B,
                              edge=1.7)
            closing.append(f"<g>{appear}{sk.wash(X, Y, s)}</g>{keep}"
                           + cls.pen(cv, clk, big, st["claimed"], X + (s - B) / 2, Y + (s - B) / 2, B,
                                     b.start + CLAIMED * k, DRAW * k))
        cv.add(f"<g>{layer}" + "".join(closing) + "</g>")
        # where the next mark must go, the rules' call: bracketed once the last turn has done, until the next starts;
        # each board's brackets drawn once, shown on every turn that sends a mark there
        sent: dict = {}
        for i, (p, b, st) in enumerate(zip(plies, beats, story)):
            if st["target"] is None or i == len(plies) - 1:
                continue
            at = b.start + (DONE if st["claimed"] in ("X", "O") else WASHED + .25 if st["claimed"] else
                            LIFT + .05 - DRAW_AT) * b.k
            sent.setdefault(st["target"], []).append((at, at + .25 * b.k, nxt[i]))
        brackets = []
        for sent_to, spans in sent.items():
            X, Y, _ = TL.board_box(sent_to, X0, Y0, N, False)
            fr = [(0, 0)]
            for at, full, until in spans:
                fr += [(at, 0), (full, 1), (until, 1), (until, 0)]
            brackets.append(f'<g opacity="0">{clk.anim("opacity", fr)}' + sk.brackets(X, Y, s, False) + "</g>")
        cv.add(f"<g>{layer}" + "".join(brackets) + "</g>")
        # the game's three boards, struck once the third board's mark is down
        if f.get("line"):
            b = beats[-1]
            pts = []
            for name in f["line"]:
                X, Y, _ = TL.board_box(board_at(name), X0, Y0, N, False)
                pts.append((X + s / 2, Y + s / 2))
            d, length = TL.struck(pts, X0, Y0, N, False, s * .3)
            cv.add(f"<g>{layer}" + sk.strike(d, 7, *cls.stroke(clk, length, b.start + WON * b.k, STRIKE * b.k))
                   + "</g>")
        size = 8
        for i in range(9):
            X, _, _ = TL.board_box((i // 3, 0), X0, Y0, N, False)
            cx = X + (i % 3) * (q + gut) + q / 2
            _, Yr, _ = TL.board_box((0, (8 - i) // 3), X0, Y0, N, False)
            cy = Yr + (i % 3) * (q + gut) + q / 2
            cv.add(sk.say(cv, "abcdefghi"[i], cx, Y0 + N + 15, size, role="muted", anchor="middle"),
                   sk.say(cv, str(9 - i), X0 - 11, cy + sk.cap(size) / 2, size, role="muted", anchor="middle"))
        sk.bevel(cv, X0, Y0, N)

    @staticmethod
    def stroke(clk, length: float, at: float, dur: float) -> tuple[str, str]:
        """A line drawn in from its start at `at` over `dur`, on the loop: the README's `stroke_in`."""
        n = length + 2
        return (f' stroke-dasharray="{f1(n)} {f1(n)}" stroke-dashoffset="{f1(n)}"',
                clk.anim("stroke-dashoffset", [(0, f1(n)), (at, f1(n), ".45 0 .25 1"), (at + dur, "0")]))

    @staticmethod
    def pen(cv, clk, drawn: str, mark: str, x, y, size, at: float, dur: float) -> str:
        """A mark drawn in by its own pen strokes from `at` over `dur`, on the loop: a mask following each stroke."""
        mid = cv.uid("m")
        paths, t = [], at
        total = sum(LENGTH[mark])
        for d, length in zip(strokes(mark), LENGTH[mark]):
            part = dur * length / total
            n = length + 2
            paths.append(f'<path d="{d}" fill="none" stroke="{c("white")}" stroke-width="24" stroke-linecap="round" '
                         f'stroke-dasharray="{f1(n)} {f1(n)}" stroke-dashoffset="{f1(n)}">'
                         + clk.anim("stroke-dashoffset", [(0, f1(n)), (t, f1(n), ".45 0 .25 1"), (t + part, "0")])
                         + "</path>")
            t += part
        cv.defs.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="{f1(x - 10)}" y="{f1(y - 10)}" '
                       f'width="{f1(size + 20)}" height="{f1(size + 20)}"><g transform="translate({f1(x)} {f1(y)}) '
                       f'scale({fx(size / 100, 4)})">' + "".join(paths) + "</g></mask>")
        return f'<g mask="url(#{mid})">{drawn}</g>'
