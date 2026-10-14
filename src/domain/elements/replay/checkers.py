# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: LicenseRef-Proprietary
"""Checkers' replay board: the profile's board, every move played with the README's own last-move motion.

A step slides the man across, lifted a little; a jump hops it over each man it takes, each fading as it passes, the
jump's path drawn in behind it and the squares it took from crossed out; it lands with a flash and a ring; a man
reaching the far row has a second man dropped onto it with a bounce. The square each move left is marked with its
phantom, and the square it lands on as it lands. Nothing moves here that the README's board does not move.
"""
from __future__ import annotations

import math

from ...canvas import c
from ...lettering import f1, fx
from ..checkers import layout as KL
from ..checkers.shapes import SHADOW
from .clock import FALL, LIN, RISE
from .common import GameReplay, captured, ripples
from .sheet import N, X0, Y0, Plan

G = 2100.0                                  # gravity, pixels a second a second, as the README's crowns fall
SLIDE, HOP, REST = .75, .5, .1              # the README's step, each hop, and the pause on each landing
LIFT = {"slide": .12, "hop": .58}
SWELL = {"slide": "1.07", "hop": "1.12"}
CROWN_DROP, CROWN_H = .22, .55
UP, DOWN = ".3 0 .6 1", ".4 0 .25 1"


class Man:
    def __init__(self, piece: str, square: int):
        self.material = "dark" if piece.lower() == "d" else "light"
        self.side = "github" if self.material == "dark" else "house"
        self.hx, self.hy = KL.xy(None, square, X0, Y0, N / 8)
        self.path, self.swell, self.ground = [(0.0, "0 0")], [(0.0, "1")], [(0.0, "0 0")]
        self.fade: list = []
        self.crowned: float | None = None
        self.moved = False

    def offset(self, square: int) -> tuple[float, float]:
        x, y = KL.xy(None, square, X0, Y0, N / 8)
        return x - self.hx, y - self.hy


class Checkers(GameReplay):
    KEY, LABEL = "checkers", KL.LABEL
    layout = KL

    @staticmethod
    def durations(plies) -> list[tuple[float, float]]:
        out = []
        for p in plies:
            hops = len(p["path"]) - 1
            move = hops * HOP + (hops - 1) * REST if p["captures"] else SLIDE
            out.append((move, .8 + (.55 if p["crowns"] else 0)))
        return out

    @classmethod
    def board(cls, cv, sk, pl: Plan, f: dict, layer: str) -> None:
        clk, s = pl.clock, N / 8
        plies, beats = f["plies"], pl.beats

        def xy(q):
            return KL.xy(None, q, X0, Y0, s)
        nxt = [pl.after(i) for i in range(len(beats))]
        sk.board_base(cv, X0, Y0, s)
        # the square each move set out from, its man in phantom; the square it lands on, marked as it lands
        x1, y1 = xy(1)
        frm = {king: captured(cv, sk.from_square, x1, y1, s, king) for king in (False, True)}
        to = captured(cv, sk.mark_to, x1, y1, s, "")
        fsteps, tsteps, top = [(0, "0 0")], [(0, "0 0")], [(0, 0)]
        kinds: dict[bool, list] = {False: [], True: []}
        taken = []
        kings = set()
        for i, (p, b) in enumerate(zip(plies, beats)):
            ax, ay = xy(p["path"][0])
            bx, by = xy(p["path"][-1])
            king_before = p["piece"].isupper() or p["path"][0] in kings
            kinds[king_before].append((b.start, nxt[i]))
            if king_before or p["crowns"]:
                kings.discard(p["path"][0])
                kings.add(p["path"][-1])
            for q in p["captures"]:
                kings.discard(q)
            fsteps.append((b.start, f"{f1(ax - x1)} {f1(ay - y1)}"))
            tsteps.append((b.start, f"{f1(bx - x1)} {f1(by - y1)}"))
            top += [(b.start, 0), (b.land - .04, 0), (b.land + .06, 1), (nxt[i], 1), (nxt[i], 0)]
            if p["captures"]:
                marks = "".join(captured(cv, sk.taken_square, *xy(q), s) for q in p["captures"])
                taken.append(f'<g visibility="hidden">{clk.windows([(b.land, nxt[i])])}{marks}</g>')
        cv.add(f'<g>{layer}' + "".join(taken)
               + "".join(f'<g visibility="hidden">{clk.windows(sp)}<g>'
                         f'{clk.anim("transform", fsteps, transform="translate", discrete=True)}{frm[king]}</g></g>'
                         for king, sp in kinds.items() if sp)
               + f'<g opacity="0">{clk.anim("opacity", top)}<g>'
               f'{clk.anim("transform", tsteps, transform="translate", discrete=True)}{to}</g></g></g>')
        clip = cv.uid("b")
        cv.defs.append(f'<clipPath id="{clip}"><rect x="{f1(X0)}" y="{f1(Y0)}" width="{f1(N)}" height="{f1(N)}"/>'
                       "</clipPath>")
        sk.board_over(cv, clip, X0, Y0, s, None, "")
        cv.add("".join(sk.tab(cv, q, x + 1.6, y + 1.6, 7) for q in range(1, 33) for x, y in [xy(q)]))
        # the men, played through with the README's journey
        board = {q: Man("d", q) for q in range(1, 13)} | {q: Man("l", q) for q in range(21, 33)}
        every = list(board.values())
        chains = []
        for i, (p, b) in enumerate(zip(plies, beats)):
            man = board.pop(p["path"][0])
            jump = bool(p["captures"])
            hops = len(p["path"]) - 1
            kk = (b.land - b.start) / ((hops * HOP + (hops - 1) * REST) if jump else SLIDE)
            leg, rest = (HOP if jump else SLIDE) * kk, REST * kk
            lift = LIFT["hop" if jump else "slide"] * s
            sw = SWELL["hop" if jump else "slide"]
            t = b.start
            for h in range(hops):
                (ax, ay), (zx, zy) = man.offset(p["path"][h]), man.offset(p["path"][h + 1])
                a, z = f"{f1(ax)} {f1(ay)}", f"{f1(zx)} {f1(zy)}"
                mid = t + leg / 2
                man.path += [(t, a, UP), (mid, f"{f1((ax + zx) / 2)} {f1((ay + zy) / 2 - lift)}", DOWN), (t + leg, z)]
                man.swell += [(t, "1", UP), (mid, sw, DOWN), (t + leg, "1")]
                man.ground += [(t, a, UP), (mid, f"{f1((ax + zx) / 2)} {f1((ay + zy) / 2)}", DOWN), (t + leg, z)]
                if jump:
                    victim = board.pop(p["captures"][h])
                    victim.fade = [(0, 1), (mid, 1), (mid + .18, 0)]
                t += leg + (rest if h < hops - 1 else 0)
            man.moved = True
            if p["crowns"]:
                man.crowned = b.land
            board[p["path"][-1]] = man
            if jump:
                pts = [(x + s / 2, y + s / 2) for x, y in (xy(q) for q in p["path"])]
                d = "M" + "L".join(f"{f1(x)} {f1(y)}" for x, y in pts)
                L = sum(math.hypot(bx - ax, by - ay) for (ax, ay), (bx, by) in zip(pts, pts[1:]))
                mask = cv.uid("m")
                cv.defs.append(f'<mask id="{mask}" maskUnits="userSpaceOnUse" x="{f1(X0)}" y="{f1(Y0)}" '
                               f'width="{f1(N)}" height="{f1(N)}"><path d="{d}" fill="none" stroke="{c("white")}" '
                               f'stroke-width="9" stroke-linecap="round" stroke-linejoin="round" '
                               f'stroke-dasharray="{f1(L + 2)} {f1(L + 2)}" stroke-dashoffset="{f1(L + 2)}">'
                               + clk.anim("stroke-dashoffset", [(0, f1(L + 2)), (b.start, f1(L + 2), LIN),
                                                                (b.land, "0")])
                               + "</path></mask>")
                chains.append(f'<g visibility="hidden">{clk.windows([(b.start, nxt[i])])}{sk.chain(d, mask)}'
                              + "".join(sk.landing(x, y, 2.6) for x, y in pts[1:-1]) + "</g>")
        k = s / 45
        sx0, sy0, rx, ry = SHADOW[0] * k, SHADOW[1] * k, SHADOW[2] * k, SHADOW[3] * k
        drawn, grounds = [], []
        for m in sorted(every, key=lambda m: (m.moved, m.hy)):
            fade = clk.anim("opacity", m.fade) if m.fade else ""
            if not m.moved:
                drawn.append(f"<g>{fade}{sk.man(cv, m.material, False, m.hx, m.hy, s)}</g>" if fade
                             else sk.man(cv, m.material, False, m.hx, m.hy, s))
                continue
            king = m.crowned is not None
            grounds.append(f'<g>{fade}<g>{clk.anim("transform", m.ground, transform="translate")}'
                           + sk.foot(cv, m.hx + sx0, m.hy + sy0, rx, ry, "") + "</g></g>")
            cx, cy = m.hx + s / 2, m.hy + s / 2
            place = f'transform="translate({f1(-s / 2)} {f1(-s / 2)}) scale({fx(k, 4)})"'
            body = f'<use href="#{sk.man_def(cv, m.material, False, shadow=False)}" {place}/>'
            if king:
                # the crown's man, dropped onto the man that reached the far row, as the README drops it
                h, bnc = CROWN_H * s, .14 * s
                tf, tb = math.sqrt(2 * h / G), math.sqrt(2 * bnc / G)
                at = m.crowned + CROWN_DROP
                drop = clk.anim("transform", [(0, f"0 {f1(-h)}"), (at, f"0 {f1(-h)}", FALL), (at + tf, "0 0", RISE),
                                              (at + tf + tb, f"0 {f1(-bnc)}", FALL), (at + tf + 2 * tb, "0 0")],
                                transform="translate")
                show = clk.anim("opacity", [(0, 0), (at, 0), (at + .06, 1)])
                top_ = sk.man_def(cv, m.material, True, shadow=False, top_only=True)
                body += f'<g opacity="0">{show}<g>{drop}<use href="#{top_}" {place}/></g></g>'
            body = (f'<g>{clk.anim("transform", m.path, transform="translate")}'
                    f'<g transform="translate({f1(cx)} {f1(cy)})"><g>'
                    + clk.anim("transform", m.swell, transform="scale") + body + "</g></g></g>")
            drawn.append(f"<g>{fade}{body}</g>" if fade else body)
        cv.add(f"<g>{layer}" + "".join(chains) + "".join(grounds) + "".join(drawn) + "</g>")
        # the README's landing: a flash on the square, and a ring running out from it
        flash = [(0, 0)]
        points = []
        for i, (p, b) in enumerate(zip(plies, beats)):
            bx, by = xy(p["path"][-1])
            flash += [(b.land - .02 * b.k, 0), (b.land + .03 * b.k, .7), (b.land + .85 * b.k, 0)]
            points.append((bx + s / 2, by + s / 2, b.land, b.start, b.k))
        rect = (f'<rect x="{f1(x1)}" y="{f1(y1)}" width="{f1(s)}" height="{f1(s)}" fill="{sk.flash}" opacity="0">'
                + clk.anim("opacity", flash) + "</rect>")
        cv.add(f'<g>{layer}<g>{clk.anim("transform", tsteps, transform="translate", discrete=True)}{rect}</g>'
               + ripples(clk, sk, clip, points, s * .3, s * 1.15) + "</g>")
        sk.bevel(cv, X0, Y0, N)
