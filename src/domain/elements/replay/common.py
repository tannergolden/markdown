# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What the four replay boards share: what each answers for the sheet, and the README's landing ring.

Each game's replay board (`chess`, `checkers`, `pentago`, `tictac`) answers the same questions for the sheet: its
label and band mark, how long each turn's motion takes and the rest after it (`durations`), its board played through
on the replay's clock (`board`), a move set in its own notation (`notation`, `token`), the score as a sheet copies
it out (`score_tokens`), what each side is called (`side_word`), and the matchup across the panel's top (`matchup`).
"""
from __future__ import annotations

from ...lettering import f1
from ..games import panel as GP


def captured(cv, fn, *args, **kw) -> str:
    """What a skin method adds to the canvas, as markup, so it can be set in motion."""
    before = len(cv.body)
    fn(cv, *args, **kw)
    out = "".join(cv.body[before:])
    del cv.body[before:]
    return out


def ripples(clk, sk, clip, points, r0, r1, after=0.0) -> str:
    """The README's ring running out from where a move lands: one ring stepping to each landing, `after` seconds
    after it, growing from r0 to r1 as `ripple_at` grows it. Each point is (cx, cy, landed, started, tempo)."""
    cx_, cy_, rr, op = [(0, f1(points[0][0]))], [(0, f1(points[0][1]))], [(0, f1(r0))], [(0, 0)]
    for (cx, cy, at, start, k) in points:
        t0, d = at + after * k, .85 * k
        cx_.append((start, f1(cx)))
        cy_.append((start, f1(cy)))
        rr += [(t0, f1(r0)), (t0 + d, f1(r1)), (t0 + d + .01, f1(r0))]
        op += [(t0, 0), (t0 + .03 * k, .9), (t0 + d, 0)]
    g = f'<g clip-path="url(#{clip})">' if clip else "<g>"
    return (f'{g}<circle cx="{cx_[0][1]}" cy="{cy_[0][1]}" r="{f1(r0)}" fill="none" {sk.ripple} opacity="0">'
            + clk.anim("cx", cx_, discrete=True) + clk.anim("cy", cy_, discrete=True) + clk.anim("r", rr)
            + clk.anim("opacity", op) + "</circle></g>")


class GameReplay:
    """A game beside chess, as the sheet asks it: its layout's band mark and medallions, and its moves in words."""

    layout = None
    SIDE_WORD = {"house": "white", "github": "black"}

    @classmethod
    def band(cls, sk):
        return cls.layout.band_mark

    @classmethod
    def matchup(cls, f: dict):
        st = {"to_move": None, "result": True, "players": len(f["players"])}

        def draw(cv, sk, x0, x1, y):
            return GP.matchup(cv, sk, cls.layout, st, x0, x1, y)
        return draw

    @classmethod
    def side_word(cls, side) -> str:
        return cls.SIDE_WORD[side]

    @classmethod
    def token(cls, cv, sk, text, x, y, size, *, role="ink", ls=.4) -> tuple[str, float]:
        return sk.say(cv, text, x, y, size, ls=ls, role=role), sk.width(text, "bold", size, ls)

    @classmethod
    def notation(cls, cv, sk, p, x, y, size) -> str:
        return cls.token(cv, sk, p["notation"], x, y, size)[0]

    @staticmethod
    def score_tokens(plies) -> list[str]:
        """The score as a sheet copies it out: each opening move with its number, the reply after it alone, and the
        ghosts' row as the sheet writes it, G and then the two."""
        out = []
        for p in plies:
            num, move = p["notation"].split(" ", 1)
            out.append(move if num.endswith("...") else f"{num} {move}")
        return out
