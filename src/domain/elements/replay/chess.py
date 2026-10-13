# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Chess's replay board: the profile's board, every move played with the README's own last-move motion.

As the README's board brings in its last move, so every move here: the piece comes in from its square, a knight
leaping and anything else gliding, lifted and swelling a little on the way, its shadow sliding along the board under
it and thinning as it lifts; a castling king's rook hops round it a beat behind; what it takes fades as it lands; the
square it left is marked with its phantom, the square it lands on marked as it lands, a flash on it and a ring
running out from it; and a king in check is clouded, the cloud blooming as the move lands. The mate's cloud stays
through the finale, as the finished board keeps it.
"""
from __future__ import annotations

from ...canvas import c
from ...lettering import f1, fx
from ..chess import layout as CL
from ..chess.game import NAMES
from ..chess.layout import sq_xy
from ..chess.shapes import FOOT
from .sheet import N, X0, Y0, Plan

S = N / 8
START = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
LEAP, GO, MID, LAND = 1.6, .25, .48, .72          # the README's last move: its length, and its three beats
GLIDE = {"lift": .12, "swell": "1.07"}
LEAPT = {"lift": .62, "swell": "1.16"}
UP, DOWN = ".3 0 .6 1", ".4 0 .25 1"              # the README's piece, rising to its midpoint and setting down


def move_time(k: float) -> float:
    """From setting off to landing, in seconds at tempo `k`: the README's, from its first beat to its third."""
    return (LAND - GO) * LEAP * k


class Piece:
    def __init__(self, letter: str, square: str):
        self.letter = letter
        self.kind, self.side = NAMES[letter.lower()], "white" if letter.isupper() else "black"
        self.hx, self.hy = sq_xy(square, X0, Y0, S)
        self.path = [(0.0, "0 0")]
        self.swell = [(0.0, "1")]
        self.shadow = [(0.0, "0 0")]
        self.thin = [(0.0, "1")]
        self.fade: list = []
        self.born: float | None = None
        self.moved = False

    def offset(self, square: str) -> tuple[float, float]:
        x, y = sq_xy(square, X0, Y0, S)
        return x - self.hx, y - self.hy

    def arrive(self, frm: str, to: str, t0: float, t1: float, style: dict) -> None:
        """The README's `arrive`: set off at t0, the midpoint lifted and swollen, landed at t1."""
        (ax, ay), (bx, by) = self.offset(frm), self.offset(to)
        tm = t0 + (t1 - t0) * (MID - GO) / (LAND - GO)
        a, b = f"{f1(ax)} {f1(ay)}", f"{f1(bx)} {f1(by)}"
        m = f"{f1((ax + bx) / 2)} {f1((ay + by) / 2 - S * style['lift'])}"
        self.path += [(t0, a, UP), (tm, m, DOWN), (t1, b)]
        self.swell += [(t0, "1", UP), (tm, style["swell"], DOWN), (t1, "1")]
        self.shadow += [(t0, a, ".35 0 .35 1"), (t1, b)]
        self.thin += [(t0, "1"), (tm, ".35"), (t1, "1")]
        self.moved = True


def placement(fen: str = START) -> dict[str, str]:
    out = {}
    for row, text in enumerate(fen.split("/")):
        f = 0
        for ch in text:
            if ch.isdigit():
                f += int(ch)
            else:
                out["abcdefgh"[f] + str(8 - row)] = ch
                f += 1
    return out


def fading(clk, pc) -> str:
    """A piece taken, faded as the README fades it; a promoted piece shown from the moment it sets off."""
    if pc.born is not None:
        return clk.anim("opacity", [(0, 0), (pc.born, 0), (pc.born + .01, 1)])
    return clk.anim("opacity", pc.fade)


class Chess:
    KEY, LABEL = "chess", "chess"

    @staticmethod
    def band(sk):
        return "pawn"

    @staticmethod
    def durations(plies) -> list[tuple[float, float]]:
        """Each move: the README's leap from setting off to landing, and the rest after it while the ring runs out
        and the panel settles."""
        return [(move_time(1), .75) for _ in plies]

    @staticmethod
    def token(cv, sk, text, x, y, size, *, role="ink", ls=.4) -> tuple[str, float]:
        return sk.say(cv, text, x, y, size, ls=ls, role=role), sk.width(text, "bold", size, ls)

    @staticmethod
    def notation(cv, sk, p, x, y, size) -> str:
        return sk.say(cv, p["notation"], x, y, size, ls=.4)

    @staticmethod
    def score_tokens(plies) -> list[str]:
        """The score as a sheet copies it out: White's move with its number, Black's after it."""
        out = []
        for p in plies:
            num, san = p["notation"].split(" ", 1)
            out.append(san if num.endswith("...") else f"{num} {san}")
        return out

    @staticmethod
    def side_word(side) -> str:
        return "white" if side == "house" else "black"

    @staticmethod
    def matchup(f: dict):
        def draw(cv, sk, x0, x1, y):
            return CL.matchup(cv, sk, {"players": len(f["players"]), "to_move": None, "result": True}, x0, x1, y)
        return draw

    @staticmethod
    def board(cv, sk, pl: Plan, f: dict, layer) -> None:
        clk = pl.clock
        plies, beats = f["plies"], pl.beats
        k45 = S / 45
        sk.board_base(cv, X0, Y0, S)
        nxt = [pl.after(i) for i in range(len(beats))]
        # the square each move left: the README's mark, its phantom the piece that left it
        col = sk.col
        steps = [(0, "0 0")]
        for p, b in zip(plies, beats):
            fx0, fy0 = sq_xy(p["from"], X0, Y0, S)
            steps.append((b.start, f"{f1(fx0 - X0)} {f1(fy0 - Y0)}"))
        box = (f'<rect x="{f1(X0)}" y="{f1(Y0)}" width="{f1(S)}" height="{f1(S)}" fill="{c(col["paper"])}"/>'
               f'<rect x="{f1(X0 + 3)}" y="{f1(Y0 + 3)}" width="{f1(S - 6)}" height="{f1(S - 6)}" fill="none" '
               f'stroke="{c(sk.mark)}" stroke-opacity=".8" stroke-dasharray="6 2 1.5 2"/>')
        kinds: dict[str, list] = {}
        for i, (p, b) in enumerate(zip(plies, beats)):
            kinds.setdefault(NAMES[p["piece"].lower()], []).append((b.start, nxt[i]))
        phantoms = "".join(f'<g visibility="hidden">{clk.windows(sp)}{sk.phantom(cv, kind, X0, Y0, S)}</g>'
                           for kind, sp in kinds.items())
        # the square each move lands on, marked as it lands, with the README's flash on it
        tsteps, top, flash = [(0, "0 0")], [(0, 0)], [(0, 0)]
        for i, (p, b) in enumerate(zip(plies, beats)):
            tx0, ty0 = sq_xy(p["to"], X0, Y0, S)
            lead = (b.land - b.start) / (LAND - GO) / LEAP     # the move's tempo, against the README's
            tsteps.append((b.start, f"{f1(tx0 - X0)} {f1(ty0 - Y0)}"))
            top += [(b.start, 0), (b.land - .064 * lead, 0), (b.land + .096 * lead, 1), (nxt[i], 1), (nxt[i], 0)]
            flash += [(b.land - .032 * lead, 0), (b.land + .048 * lead, .7), (b.land + .37 * lead, 0)]
        to = (f'<rect x="{f1(X0)}" y="{f1(Y0)}" width="{f1(S)}" height="{f1(S)}" fill="{c(col["paper"])}"/>'
              f'<rect x="{f1(X0 + 2.2)}" y="{f1(Y0 + 2.2)}" width="{f1(S - 4.4)}" height="{f1(S - 4.4)}" '
              f'fill="none" stroke="{c(sk.mark)}" stroke-width="2.2"/>')
        cv.add(f'<g>{layer}'
               f'<g visibility="hidden">{clk.windows([(beats[0].start, pl.total)])}<g>'
               f'{clk.anim("transform", steps, transform="translate", discrete=True)}{box}{phantoms}</g></g>'
               f'<g opacity="0">{clk.anim("opacity", top)}<g>'
               f'{clk.anim("transform", tsteps, transform="translate", discrete=True)}{to}</g></g></g>')
        clip = cv.uid("b")
        cv.defs.append(f'<clipPath id="{clip}"><rect x="{f1(X0)}" y="{f1(Y0)}" width="{f1(N)}" height="{f1(N)}"/>'
                       "</clipPath>")
        sk.board_over(cv, clip, X0, Y0, S, None, "")
        sk.bevel(cv, X0, Y0, N)
        # the pieces, played through
        board = {sq: Piece(pc, sq) for sq, pc in placement().items()}
        every = list(board.values())
        for p, b in zip(plies, beats):
            mover = board.pop(p["from"])
            span = b.land - b.start
            if p["taken_at"]:
                victim = board.pop(p["taken_at"])
                victim.fade = [(0, 1), (b.land - .106 * span, 1), (b.land + .106 * span, 0)]
            style = LEAPT if mover.kind == "knight" else GLIDE
            if p["promotion"]:
                # the README brings the promoted piece in from the pawn's square, so the pawn gives way to it there
                mover.fade = [(0, 1), (b.start, 1), (b.start + .01, 0)]
                letter = p["promotion"].upper() if mover.side == "white" else p["promotion"]
                mover = Piece(letter, p["from"])
                mover.born = b.start
                every.append(mover)
                style = GLIDE
            mover.arrive(p["from"], p["to"], b.start, b.land, style)
            board[p["to"]] = mover
            if p["rook"]:
                rook = board.pop(p["rook"][0])
                r0 = b.start + span * (.36 - GO) / (LAND - GO)
                r1 = b.start + span * (.84 - GO) / (LAND - GO)
                rook.arrive(p["rook"][0], p["rook"][1], r0, r1, {"lift": .4, "swell": "1.07"})
                board[p["rook"][1]] = rook
        shadows, drawn = [], []
        for pc in sorted(every, key=lambda pc: (pc.moved, pc.hy)):
            if not pc.moved:
                body = sk.put(cv, pc.kind, pc.side, pc.hx, pc.hy, S)
            else:
                sx, sy, rx, ry = pc.hx + FOOT[0] * k45, pc.hy + FOOT[1] * k45, FOOT[2] * k45, FOOT[3] * k45
                thin_rx = [(t, f1(rx * float(v))) for t, v, *_ in pc.thin]
                thin_op = [(t, v if v == "1" else ".35") for t, v, *_ in pc.thin]
                shadow = (f'<g>{clk.anim("transform", pc.shadow, transform="translate")}'
                          + sk.foot(cv, sx, sy, rx, ry, clk.anim("rx", thin_rx) + clk.anim("opacity", thin_op))
                          + "</g>")
                pid = sk.piece_def(cv, pc.kind, pc.side, shadow=False)
                cx, cy = pc.hx + S / 2, pc.hy + S / 2
                body = (f'<g>{clk.anim("transform", pc.path, transform="translate")}'
                        f'<g transform="translate({f1(cx)} {f1(cy)})"><g>'
                        + clk.anim("transform", pc.swell, transform="scale")
                        + f'<use href="#{pid}" transform="translate({f1(-S / 2)} {f1(-S / 2)}) scale({fx(k45, 4)})"/>'
                        + "</g></g></g>")
                shadows.append(f'<g>{fading(clk, pc)}{shadow}</g>' if (pc.fade or pc.born is not None) else shadow)
            if pc.fade or pc.born is not None:
                body = f"<g>{fading(clk, pc)}{body}</g>"
            drawn.append(body)
        cv.add(f'<g>{layer}' + "".join(shadows) + "".join(drawn) + "</g>")
        # the README's landing: a flash on the square, and a ring running out from it a beat after
        ring_x, ring_y, ring_r, ring_o = [(0, f1(X0))], [(0, f1(Y0))], [(0, f1(S * .3))], [(0, 0)]
        for i, (p, b) in enumerate(zip(plies, beats)):
            tx0, ty0 = sq_xy(p["to"], X0, Y0, S)
            lead = (b.land - b.start) / (LAND - GO) / LEAP
            t0, t1 = b.land + .36 * lead, b.land + .9 * lead
            ring_x.append((b.start, f1(tx0 + S / 2)))
            ring_y.append((b.start, f1(ty0 + S / 2)))
            ring_r += [(t0, f1(S * .3)), (t1, f1(S * 1.15)), (t1 + .01, f1(S * .3))]
            ring_o += [(t0 - .01, 0), (t0 + .04, .9), (t1, 0)]
        flash_rect = (f'<rect x="{f1(X0)}" y="{f1(Y0)}" width="{f1(S)}" height="{f1(S)}" fill="{sk.flash}" '
                      f'opacity="0">' + clk.anim("opacity", flash) + "</rect>")
        cv.add(f'<g>{layer}<g>{clk.anim("transform", tsteps, transform="translate", discrete=True)}{flash_rect}</g>'
               f'<g clip-path="url(#{clip})"><circle cx="{f1(X0)}" cy="{f1(Y0)}" r="{f1(S * .3)}" fill="none" '
               f'{sk.ripple} opacity="0">'
               + clk.anim("cx", ring_x, discrete=True) + clk.anim("cy", ring_y, discrete=True)
               + clk.anim("r", ring_r) + clk.anim("opacity", ring_o) + "</circle></g></g>")
        # a king in check, clouded, the cloud blooming as the move lands; the mate's stays through the finale
        clouds = []
        for i, (p, b) in enumerate(zip(plies, beats)):
            if not p["check"]:
                continue
            lead = (b.land - b.start) / (LAND - GO) / LEAP
            kx, ky = sq_xy(p["check"], X0, Y0, S)
            last = i + 1 == len(beats)
            until = pl.total if last else nxt[i]
            bloom = [(0, 0), (b.land + .2 * lead, 0), (b.land + .76 * lead, 1), (b.land + 1.46 * lead, .5),
                     (b.land + 2.16 * lead, 1), (b.land + 2.87 * lead, .5), (b.land + 3.87 * lead, 1)]
            bloom = [fr for fr in bloom if fr[0] < until]
            if not last:
                bloom.append((until, bloom[-1][1]))
                bloom.append((until, 0))
            clouds.append(f'<g clip-path="url(#{clip})" opacity="0">{clk.anim("opacity", bloom)}'
                          f'<path d="{sk.cloud(kx, ky, S)}" fill="none" stroke="{c(sk.mark)}" stroke-width="1.5" '
                          f'stroke-linejoin="round"/></g>')
        cv.add(f'<g>{layer}' + "".join(clouds) + "</g>")
        size = 9
        for i in range(8):
            cv.add(sk.say(cv, "abcdefgh"[i], X0 + i * S + S / 2, Y0 + N + 16, size, role="muted", anchor="middle"),
                   sk.say(cv, str(8 - i), X0 - 11, Y0 + i * S + S / 2 + sk.cap(size) / 2, size, role="muted",
                          anchor="middle"))
