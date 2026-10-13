# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Pentago's replay board: the profile's four quarters, every turn played with the README's own last-move motion.

The two ghosts are set in their holes first. Then each marble is set in its hole, which is ringed as it settles,
with a ripple; and its quarter turns its quarter turn, everything on it turning with it, ghosts too, an arrow drawn
round the quarter's outer corner the way it went, as the README turns it: the quarter as it stands after the turn,
turned back to where it stood, turning into place. A marble that makes five on its own wins before any quarter
turns. A won game's five are ringed one after another and joined. Nothing moves here that the README's board does
not move.

Each quarter is drawn once for every stretch between its turns, as it stands through that stretch, and shown for
that stretch alone: its marbles under its plate, set in as each is played, and each empty hole's centre mark until
a marble fills it. Its plate is one drawing, defined once and set in every stretch.
"""
from __future__ import annotations

from ...drafting import hair
from ...lettering import f1
from ..chess import motion as CM
from ..pentago import layout as PL
from ..pentago.game import QUARTERS, landed, material_of, quarter_cells, quarter_of
from ..pentago.motion import DROP, LAND, TURN_EASE, TWIST, TWIST_AT
from ..pentago.shapes import DISC, HOLE
from .common import GameReplay, captured, ripples
from .sheet import N, X0, Y0, Plan

SET = .2                                        # a marble set in, as the README sets it
RING = LAND - DROP                              # its hole ringed, from the moment it is set
TURN = TWIST_AT - DROP                          # its quarter turning, from the moment it is set


class Marble:
    def __init__(self, kind: str, cell: str, at: float, k: float):
        self.kind, self.cell, self.at, self.k = kind, cell, at, k


class Pentago(GameReplay):
    KEY, LABEL = "pentago", PL.LABEL
    layout = PL

    @staticmethod
    def durations(plies) -> list[tuple[float, float]]:
        out = []
        for p in plies:
            if p.get("ghost") or p.get("unturned"):
                out.append((RING, .8))
            else:
                out.append((TURN + TWIST, .8))
        return out

    # --- the moves in words: the marble, its hole and the turn, as the sheet writes them
    @classmethod
    def written(cls, cv, sk, num: str, move: str, side: str, x, y, size, role="ink") -> tuple[str, float]:
        out, w = "", 0.0
        if num:
            out += sk.say(cv, num + " ", x, y, size, role=role)
            w += sk.width(num + " ", "bold", size)
        before = len(cv.body)
        w += PL.write(cv, sk, {}, side, move, x + w, y, size, role)
        drawn = "".join(cv.body[before:])
        del cv.body[before:]
        return out + drawn, w

    @classmethod
    def notation(cls, cv, sk, p, x, y, size) -> str:
        num, move = p["notation"].split(" ", 1)
        return cls.written(cv, sk, num, move, p["side"], x, y, size)[0]

    @staticmethod
    def score_tokens(plies) -> list:
        out = []
        for p in plies:
            num, move = p["notation"].split(" ", 1)
            out.append(("" if num.endswith("...") else num, move, p["side"]))
        return out

    @classmethod
    def token(cls, cv, sk, tok, x, y, size, *, role="ink", ls=.4) -> tuple[str, float]:
        num, move, side = tok
        return cls.written(cv, sk, num, move, side, x, y, size, role)

    # --- the board
    @classmethod
    def board(cls, cv, sk, pl: Plan, f: dict, layer: str) -> None:
        clk = pl.clock
        plies, beats = f["plies"], pl.beats
        nxt = [pl.after(i) for i in range(len(beats))]
        _, q, p, m = PL.geometry(N, False)
        rh = HOLE * p
        for qk in QUARTERS:
            X, Y, _ = PL.quarter_box(qk, X0, Y0, N, False)
            sk.frame_shadow(cv, X, Y, q, q)
        # every quarter's stretches between its turns, each with its marbles where they stand through it
        stretches = {qk: [{"from": 0.0, "turn": None, "marbles": []}] for qk in QUARTERS}
        board: dict[str, Marble] = {}
        rings, turns = [], []
        for i, (pp, b) in enumerate(zip(plies, beats)):
            k = b.k
            kind = "ghost" if pp.get("ghost") else material_of(pp["side"])
            marble = Marble(kind, pp["cell"], b.start, k)
            board[pp["cell"]] = marble
            stretches[quarter_of(pp["cell"])][-1]["marbles"].append((marble, pp["cell"]))
            set_at = b.start + RING * k
            turned = not pp.get("ghost") and not pp.get("unturned")
            moves_it = turned and quarter_of(pp["cell"]) == pp["quarter"]
            t0, t1 = b.start + TURN * k, b.start + (TURN + TWIST) * k
            rings.append((pp["cell"], set_at, t0 if moves_it else nxt[i], k))
            if turned:
                if moves_it:
                    rings.append((landed(pp["cell"], pp["quarter"], pp["way"]), t1, nxt[i], 0))
                qk, way = pp["quarter"], pp["way"]
                X, Y, _ = PL.quarter_box(qk, X0, Y0, N, False)
                shown = clk.anim("opacity", [(0, 0), (t0, 0), (t0 + .2 * k, 1), (nxt[i], 1), (nxt[i], 0)])
                turns.append(f'<g opacity="0">{shown}' + sk.turn_mark(X, Y, q, qk, way, m * .55) + "</g>")
                inside = {cell: mb for cell, mb in board.items() if quarter_of(cell) == qk}
                for cell in inside:
                    del board[cell]
                for cell, mb in inside.items():
                    board[landed(cell, qk, way)] = mb
                stretches[qk].append({"from": t0, "turn": (t0, t1, way),
                                      "marbles": [(mb, cell) for cell, mb in board.items() if quarter_of(cell) == qk]})
        cv.add(f"<g>{layer}" + "".join(cls.quarter(cv, sk, clk, qk, stretches[qk], q, p) for qk in QUARTERS) + "</g>")
        # each hole a marble is set in, ringed as it settles, with a ripple; ringed again where its quarter took it
        marks, points = [], []
        for cell, at, until, k in rings:
            cx, cy = PL.centre(cell, X0, Y0, N, False)
            fade = .12 * k if k else 0
            shown = clk.anim("opacity", [(0, 0), (at, 0), (at + fade, 1), (until, 1), (until, 0)])
            marks.append(f'<g opacity="0">{shown}' + sk.hole_ring(cv, cx, cy, rh + 2.6) + "</g>")
        for pp, b in zip(plies, beats):
            cx, cy = PL.centre(pp["cell"], X0, Y0, N, False)
            points.append((cx, cy, b.start + RING * b.k, b.start, b.k))
        cv.add(f"<g>{layer}" + "".join(marks) + ripples(clk, sk, "", points, rh, p * .95) + "".join(turns) + "</g>")
        # a won game's five, ringed one after another and joined once the last turn is done
        if f.get("line"):
            land = beats[-1].land
            pts = [PL.centre(cl, X0, Y0, N, False) for cl in f["line"]]
            out = []
            for i, (cx, cy) in enumerate(pts):
                at = land + .3 + i * .14
                out.append(f'<g opacity="0">{clk.anim("opacity", [(0, 0), (at, 0), (at + .1, 1)])}'
                           + sk.hole_ring(cv, cx, cy, rh + 2.6, "", 2.4) + "</g>")
            (ax, ay), (bx, by) = pts[0], pts[-1]
            n = ((bx - ax) ** 2 + (by - ay) ** 2) ** .5 + 2
            extra = f' stroke-dasharray="{f1(n)} {f1(n)}" stroke-dashoffset="{f1(n)}"'
            anim = clk.anim("stroke-dashoffset", [(0, f1(n)), (land + 1.05, f1(n), ".45 0 .25 1"), (land + 1.5, "0")])
            cv.add(f"<g>{layer}" + "".join(out) + sk.connect(f"M{f1(ax)} {f1(ay)}L{f1(bx)} {f1(by)}", 5, extra, anim)
                   + "</g>")
        size = 9
        for fl in "abcdef":
            cx, _ = PL.centre(f"{fl}1", X0, Y0, N, False)
            cv.add(sk.say(cv, fl, cx, Y0 + N + 15, size, role="muted", anchor="middle"))
        for r in range(1, 7):
            _, cy = PL.centre(f"a{r}", X0, Y0, N, False)
            cv.add(sk.say(cv, str(r), X0 - 11, cy + sk.cap(size) / 2, size, role="muted", anchor="middle"))

    @classmethod
    def quarter(cls, cv, sk, clk, qk, stretches, q, p) -> str:
        """One quarter through the game: each stretch between its turns shown for that stretch alone, its marbles
        under the plate set in as each is played, each empty hole's centre mark until it is filled, and a stretch
        that a turn opens turning into place, as the README turns its last quarter."""
        X, Y, _ = PL.quarter_box(qk, X0, Y0, N, False)
        cx, cy = X + q / 2, Y + q / 2
        holes = [PL.centre(cl, X0, Y0, N, False) for cl in quarter_cells(qk)]
        cache = cv.__dict__.setdefault("_plates", {})
        if qk not in cache:
            with CM.at_rest(True):
                plate = captured(cv, sk.plate, X, Y, q, q, holes, p, [])
            pid = cv.uid("qp")
            cv.defs.append(f'<g id="{pid}">{plate}</g>')
            cache[qk] = pid
        k = HOLE * p * .42
        out = []
        for j, st in enumerate(stretches):
            until = stretches[j + 1]["from"] if j + 1 < len(stretches) else None
            shown = clk.windows([(st["from"], until if until is not None else clk.D)]) if (j or until) else ""
            body = []
            filled = {}
            for mb, cell in st["marbles"]:
                hx, hy = PL.centre(cell, X0, Y0, N, False)
                drawn = (sk.ghost_marble(cv, hx, hy, DISC * p) if mb.kind == "ghost"
                         else sk.disc(cv, mb.kind, hx, hy, p))
                if mb.at > st["from"]:
                    drawn = f"<g>{clk.appear(mb.at, SET * mb.k)}{drawn}</g>"
                    filled[cell] = mb.at
                else:
                    filled[cell] = None
                body.append(drawn)
            body.append(f'<use href="#{cache[qk]}"/>')
            for cell in quarter_cells(qk):
                if cell in filled and filled[cell] is None:
                    continue
                hx, hy = PL.centre(cell, X0, Y0, N, False)
                mark = (f'<path d="M{f1(hx - k)} {f1(hy)}H{f1(hx + k)}M{f1(hx)} {f1(hy - k)}V{f1(hy + k)}" '
                        f'fill="none" {hair(sk.col, .4)} stroke-width=".7"/>')
                if cell in filled:
                    mark = f'<g>{clk.windows([(0, filled[cell])])}{mark}</g>'
                body.append(mark)
            turn = ""
            if st["turn"]:
                t0, t1, way = st["turn"]
                back = -90 if way == "cw" else 90
                turn = clk.anim("transform", [(0, f"{back} {f1(cx)} {f1(cy)}"),
                                              (t0, f"{back} {f1(cx)} {f1(cy)}", TURN_EASE),
                                              (t1, f"0 {f1(cx)} {f1(cy)}")], transform="rotate")
            group = f"<g>{turn}" + "".join(body) + "</g>"
            out.append(f'<g visibility="{"hidden" if j else "visible"}">{shown}{group}</g>' if shown else group)
        return "".join(out)
