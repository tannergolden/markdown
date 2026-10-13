# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""What every replay shares, whatever the game: its timing, the panel that follows the game move by move, and the
finale.

Every motion in a replay is one the profile's own boards already make, nothing new:

  a move              the game's own last-move motion, the same as the README's board plays as it opens
  the panel           risen into place once as the sheet opens, as the README's panel rises; from then on each
                      move's words take the last one's place the moment it is played, and nothing in it rises again
  the mover           ringed by the turn ring, drawn in as the turn arrives, as the README rings the side to move
  the result          the finished board's own plate, risen, its second panel sliding open, a glint crossing it
  the winner          the turn ring drawn in round their portrait, and the glint the Hall of Fame's gold medal runs
  everyone who lost   their section risen, each of them fading as a taken piece fades

The board stands where the profile's board stands, the same size in the same frame, so a replay reads as the board
the page showed come to life. Long games are played at a quicker tempo, the same motions faster, so none runs long:
the moves take TARGET seconds at most, the last two always at the README's own tempo.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from ...canvas import c
from ...lettering import f1
from ..chess.game import OWNER
from ..chess.skins import ring_ticks
from .clock import EASE, OUT, Clock

W = 830
BAND, PAD = 40, 20
X0, Y0, N = PAD + 18, BAND + 22, 368     # the board's corner and size, the profile's
PX0, PX1 = X0 + N + 32, W - PAD           # the panel
H = Y0 + N + 22 + PAD
INTRO = 1.6                               # the sheet settles before the first move
HOLD = 9.5                                # the finale, held before the loop starts again
CURTAIN = .7                              # the fade the loop closes on
TARGET = 38.0                             # the most a game's moves take, played at their quickest tempo
RING = ".3 0 .2 1"                        # the turn ring's draw, as the skins' turn_ring eases it
STEP = 100                                # how far apart the moves' lines are stacked behind the panel's clip


@dataclass
class Beat:
    """When a turn is played: it sets off, lands, and gives way to the next; `k`, its tempo against the README's."""
    ply: int
    start: float
    land: float
    end: float
    k: float


@dataclass
class Plan:
    beats: list[Beat]
    finale: float
    total: float
    clock: Clock = field(init=False)

    def __post_init__(self):
        self.clock = Clock(self.total)

    def after(self, i: int) -> float:
        """When the turn after turn `i` (from 0) starts, or for the last, when the loop starts to close."""
        return self.beats[i + 1].start if i + 1 < len(self.beats) else self.total - CURTAIN


def plan(durations: list[tuple[float, float]]) -> Plan:
    """The game's beats from each turn's own motion and the rest after it, in the README's seconds: played at the
    README's tempo, or quicker when the game would run past TARGET; the last two always at the README's."""
    raw = sum(m + r for m, r in durations)
    k = min(1.0, TARGET / raw) if raw else 1.0
    beats, t = [], INTRO
    n = len(durations)
    for i, (m, r) in enumerate(durations, 1):
        kk = 1.0 if i > n - 2 else k
        beats.append(Beat(i, t, t + m * kk, t + (m + r) * kk, kk))
        t += (m + r) * kk
    return Plan(beats, t, t + HOLD + CURTAIN)


def curtain(pl: Plan) -> str:
    """The layers that play the game fade in as the loop opens and out as it closes."""
    D = pl.total
    return pl.clock.anim("opacity", [(0, 0, EASE), (.5, 1), (D - CURTAIN, 1, EASE), (D, 0)])


def rise(clk: Clock, spans: list[tuple[float, float]], dur: float = .45, lift: float = 6.0) -> str:
    """Risen into place at the start of each span and gone at its end: the README's rise, once a span."""
    op, tr = [(0, 0)], [(0, f"0 {f1(lift)}")]
    for a, b in sorted(spans):
        d = min(dur, (b - a) * .7)
        op += [(a, 0), (a + d, 1), (b, 1), (b, 0)]
        tr += [(a, f"0 {f1(lift)}", OUT), (a + d, "0 0"), (b, "0 0"), (b, f"0 {f1(lift)}")]
    return clk.anim("opacity", op) + clk.anim("transform", tr, transform="translate")


def ring_in(clk: Clock, sk, cx, cy, r, spans, width=2.2) -> str:
    """The turn ring round (cx, cy), drawn in at the start of each span as the README draws it for the side to
    move, and gone at the span's end."""
    C = 2 * math.pi * r
    fr = [(0, f1(C))]
    for a, b in sorted(spans):
        fr += [(a, f1(C), RING), (min(a + .6, b), "0"), (b, "0"), (b, f1(C))]
    return (f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="none" stroke="{c(sk.mark)}" '
            f'stroke-width="{width:g}" stroke-dasharray="{f1(C)}" stroke-dashoffset="{f1(C)}" '
            f'transform="rotate(-90 {f1(cx)} {f1(cy)})">' + clk.anim("stroke-dashoffset", fr) + "</circle>")


def medal_glint(clk: Clock, sk, cx, cy, rr, runs: list[float]) -> str:
    """The glint the Hall of Fame runs round its gold medal, once at each of `runs`: the same band, the same sweep,
    on the replay's own clock."""
    C = 2 * math.pi * rr
    off, op = [(0, "0")], [(0, 0)]
    for g in runs:
        off += [(g, "0", EASE), (g + .98, f1(-C * .32)), (g + .99, "0")]
        op += [(g, 0), (g + .21, .95), (g + .7, .95), (g + .98, 0)]
    return (f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(rr)}" fill="none" stroke="{c(sk.flash)}" stroke-width="3.4" '
            f'stroke-linecap="round" stroke-dasharray="6 {f1(C)}" stroke-dashoffset="0" opacity="0" '
            f'transform="rotate(-150 {f1(cx)} {f1(cy)})">' + clk.anim("stroke-dashoffset", off)
            + clk.anim("opacity", op) + "</circle>")


def heading(cv, sk, text, x, y, anchor="start"):
    return sk.caps(cv, text, x, y, 8.5, ls=.9, anchor=anchor)


def fitted(cv, sk, text, x, y, size, room, *, ls=.5, floor=6.0, anchor="start", role=None) -> str:
    """Capitals set as large as `size`, smaller to fit `room`, as a sheet fits its words."""
    while size > floor and sk.width(text.upper(), "caps", size, ls) > room:
        size -= .25
    return worded(cv, sk, text, x, y, size, ls=ls, anchor=anchor, role=role)


def worded(cv, sk, text, x, y, size, *, ls=.5, anchor="start", role=None) -> str:
    """Capitals set word by word, each word drawn once in the file and set wherever it stands: a replay says "the",
    "board" and "takes" on every move, and each word costs one reference where its letters would cost one each. A
    word stands where the whole line would have set it: after everything before it and one letter's spacing."""
    text = str(text).upper()
    cache = cv.__dict__.setdefault("_words", {})
    gap = ls * 1.6                                     # the capitals' spacing between letters, as `caps` sets it
    total = sk.width(text, "caps", size, ls)
    at = x - total if anchor == "end" else x - total / 2 if anchor == "middle" else x
    out, done = [], ""
    for word in text.split(" "):
        if word:
            key = (word, size, ls, role)
            if key not in cache:
                wid = cv.uid("w")
                cv.defs.append(f'<g id="{wid}">{sk.caps(cv, word, 0, 0, size, ls=ls, role=role)}</g>')
                cache[key] = wid
            dx = at if not done else at + sk.width(done, "caps", size, ls) + gap
            out.append(f'<use href="#{cache[key]}" x="{f1(dx)}" y="{f1(y)}"/>')
        done += word + " "
    return "".join(out)


class Panel:
    """The panel beside the board, from the matchup down, played move by move and handed to the finale."""

    def __init__(self, cv, sk, pl: Plan, facts: dict, game, faces, matchup):
        self.cv, self.sk, self.pl, self.f, self.g, self.faces = cv, sk, pl, facts, game, faces
        self.matchup = matchup

    def spans(self):
        """Each turn's time on the panel: from the moment it is played to the next one, the last into the finale."""
        pl = self.pl
        return [(b.start, pl.beats[i + 1].start if i + 1 < len(pl.beats) else pl.finale + .6)
                for i, b in enumerate(pl.beats)]

    def draw(self, layer: str) -> None:
        cv, sk, pl = self.cv, self.sk, self.pl
        clk = pl.clock
        y = self.matchup(cv, sk, PX0, PX1, Y0 + 1)
        cv.add(sk.rule(PX0, PX1, y + 12))
        top = y + 12
        playing = [f'<g>{layer}<g>{clk.windows([(0, pl.finale + .6)])}']
        playing.append(self.now_playing(top + 24))
        playing.append(sk.rule(PX0, PX1, top + 112))
        playing.append(self.roster(top + 134))
        playing.append(sk.rule(PX0, PX1, top + 214))
        playing.append(self.ticker(top + 236))
        playing.append("</g></g>")
        cv.add("".join(playing))
        cv.add(f"<g>{layer}" + self.finale(top + 16) + "</g>")

    # --- the move being played: each move's words take the last one's place the moment it is played
    def now_playing(self, y) -> str:
        cv, sk, pl, f, faces = self.cv, self.sk, self.pl, self.f, self.faces
        clk, n = pl.clock, len(f["plies"])
        spans = self.spans()
        out = [heading(cv, sk, "replay", PX0, y)]
        out.append(f'<g>{rise(clk, [(.3, pl.beats[0].start)])}'
                   + sk.say(cv, f"Game {f['game']}", PX0, y + 30, 22, ls=.4)
                   + sk.caps(cv, f"{n} moves, from the first to the last", PX0, y + 48, 8.5, ls=.5)
                   + "</g>")
        # each move's lines, stacked a STEP apart behind one clip and stepped into view as it is played: one
        # animation for the whole game, where a window for each move would cost one each
        clip = cv.uid("np")
        cv.defs.append(f'<clipPath id="{clip}"><rect x="{f1(PX0 - 4)}" y="{f1(y - 12)}" width="{f1(PX1 - PX0 + 8)}" '
                       f'height="68"/></clipPath>')
        lines = []
        for i, p in enumerate(f["plies"]):
            at = y + i * STEP
            lines.append(worded(cv, sk, f"move {i + 1} of {n}", PX1, at, 8.5, ls=.9, anchor="end")
                         + self.g.notation(cv, sk, p, PX0, at + 30, 22)
                         + fitted(cv, sk, p["words"], PX0, at + 48, 8.5, PX1 - PX0))
        steps = [(0, "0 0")] + [(b.start, f"0 {-i * STEP}") for i, b in enumerate(pl.beats)]
        shown = clk.windows([(pl.beats[0].start, spans[-1][1])])
        out.append(f'<g clip-path="url(#{clip})"><g visibility="hidden">{shown}'
                   f'<g>{clk.anim("transform", steps, transform="translate", discrete=True)}' + "".join(lines)
                   + "</g></g></g>")
        out.append("<g>")
        # who played it: each player's line drawn once and shown on their moves; the side and the day likewise
        by_player: dict = {}
        by_note: dict = {}
        for (a, b), p in zip(spans, f["plies"]):
            by_player.setdefault((p["by"], p.get("by_id")), []).append((a, b))
            by_note.setdefault(f"{self.g.side_word(p['side'])}  ·  {p['when']}", []).append((a, b))
        for (login, pid), sp in by_player.items():
            out.append(f'<g visibility="hidden">{clk.windows(sp)}'
                       + faces.face(login, pid, PX0 + 9, y + 74, 9, ring=1.1)
                       + sk.say(cv, faces.named(login, pid), PX0 + 24, y + 77.5, 9.5, ls=.6) + "</g>")
        for note, sp in by_note.items():
            out.append(f'<g visibility="hidden">{clk.windows(sp)}'
                       + sk.caps(cv, note, PX1, y + 77.5, 7.5, ls=.5, anchor="end") + "</g>")
        out.append("</g>")
        return "".join(out)

    # --- everyone who played, the mover ringed by the turn ring
    def roster(self, y) -> str:
        cv, sk, pl, f, faces = self.cv, self.sk, self.pl, self.f, self.faces
        clk = pl.clock
        out = [heading(cv, sk, "the house", PX0, y), heading(cv, sk, "github", PX1, y, anchor="end")]
        r, cy = 15, y + 28
        spans: dict = {}
        for (a, b), p in zip(self.spans(), f["plies"]):
            spans.setdefault((p["by"], p.get("by_id")), []).append((a, b))
        seats = [((OWNER, owner_id(f)), PX0 + r + 2)]
        x = PX1 - r - 2
        for player in reversed(f["players"][:5]):
            seats.append(((player["player"], player["player_id"]), x))
            x -= 2 * r + 24
        if (None, None) in spans:
            sides = {p["side"] for p in f["plies"] if p["by"] is None}
            seats.append(((None, None), PX0 + 3 * r + 30 if "house" in sides else x))
        for (login, pid), cx in seats:
            out.append(faces.face(login, pid, cx, cy, r))
            out.append(fitted(cv, sk, faces.label(login, pid), cx, cy + r + 13, 7, 2 * r + 20, ls=.4,
                              anchor="middle"))
            if (login, pid) in spans:
                out.append(ring_in(clk, sk, cx, cy, r + 3.4, spans[(login, pid)]))
        return "".join(out)

    # --- the score sheet: the newest move written into the last row as it is played, the rows above moved up one
    def ticker(self, y) -> str:
        cv, sk, pl, f, faces = self.cv, self.sk, self.pl, self.f, self.faces
        clk = pl.clock
        rows, lead = 4, 17
        top = y + 10
        clip = cv.uid("tk")
        cv.defs.append(f'<clipPath id="{clip}"><rect x="{f1(PX0 - 4)}" y="{f1(top)}" width="{f1(PX1 - PX0 + 8)}" '
                       f'height="{f1(rows * lead + 2)}"/></clipPath>')
        out = [heading(cv, sk, "moves", PX0, y)]
        mark_y = top + (rows - 1) * lead
        out.append(f'<g>{clk.windows([(pl.beats[0].start, pl.finale + .6)])}'
                   + sk.row_mark(PX0 - 2, mark_y + 1, PX1 - PX0 + 4, lead) + "</g>")
        lines = []
        for i, p in enumerate(f["plies"]):
            ly = top + (rows - 1) * lead + i * lead + 12.5
            lines.append(self.g.notation(cv, sk, p, PX0 + 6, ly, 10)
                         + faces.face(p["by"], p.get("by_id"), PX1 - 12, ly - 3.6, 6.4, ring=.8))
        fr = [(0, "0 0")]
        for i, b in enumerate(pl.beats):
            fr.append((b.start, f"0 {f1(-i * lead)}"))
        out.append(f'<g clip-path="url(#{clip})"><g>{clk.windows([(pl.beats[0].start, pl.finale + .6)])}'
                   + clk.anim("transform", fr, transform="translate", discrete=True)
                   + "".join(lines) + "</g></g>")
        return "".join(out)

    # --- the finale
    def finale(self, y) -> str:
        cv, sk, pl, f, faces = self.cv, self.sk, self.pl, self.f, self.faces
        clk, F, D = pl.clock, pl.finale, pl.total
        won_house = f["winner"] == "house"
        winner, wid = (OWNER, owner_id(f)) if won_house else (f["by"], f["by_id"])
        out = [f'<g opacity="0">{rise(clk, [(F + .7, D)])}']
        out.append(heading(cv, sk, "winner", PX0, y + 8))
        out.append(heading(cv, sk, f"game {f['game']}  ·  {f['ended_day']}", PX1, y + 8, anchor="end"))
        R, cx, cy = 36, PX0 + 44, y + 64
        out.append(f'<path d="{ring_ticks(cx, cy, R + 7, R + 11, 48)}" fill="none" stroke="{c(sk.col["line"])}" '
                   f'stroke-width="1.1" opacity=".8"/>')
        out.append(faces.face(winner, wid, cx, cy, R, ring=2.2))
        out.append(ring_in(clk, sk, cx, cy, R + 3.6, [(F + 1.2, D)], width=2.6))
        out.append(medal_glint(clk, sk, cx, cy, R + 3.6, [F + 2.6, F + 9.6] if F + 10.6 < D else [F + 2.6]))
        tx = PX0 + 100
        name = faces.named(winner, wid)
        size = 22.0
        while size > 12 and sk.width(name, "bold", size, .6) > PX1 - tx:
            size -= .5
        out.append(sk.say(cv, name, tx, cy - 14, size, ls=.6))
        out.append(self.plate(tx, cy - 3, won_house))
        mates = [(p["player"], p["player_id"]) for p in f["players"] if p["player_id"] != wid] if not won_house else []
        if mates:
            mx = tx
            out.append(sk.caps(cv, "with", mx, cy + 42, 7.5, ls=.5))
            mx += 26
            for login, pid in mates:
                label = f"@{faces.label(login, pid)}" if pid not in faces.gone else faces.label(login, pid)
                w = sk.width(label.upper(), "caps", 7.5, .5)
                if mx + 18 + w > PX1:
                    break
                out.append(faces.face(login, pid, mx + 7, cy + 39.4, 7, ring=.9))
                out.append(sk.caps(cv, label, mx + 18, cy + 42, 7.5, ls=.5))
                mx += 18 + w + 12
        out.append("</g>")
        # everyone who lost: their section risen, and each fading after it as a taken piece fades
        ly = y + 132
        out.append(f'<g opacity="0">{rise(clk, [(F + 2.4, D)])}')
        out.append(sk.rule(PX0, PX1, ly - 12))
        out.append(heading(cv, sk, "defeated", PX0, ly + 8))
        losers = [(OWNER, owner_id(f))] if not won_house else [(p["player"], p["player_id"]) for p in f["players"]]
        out.append(sk.caps(cv, f"{'the house' if not won_house else 'github'}  ·  {f['loser_moves']} moves", PX1,
                           ly + 8, 7.5, ls=.5, anchor="end"))
        r = 16
        x = PX0 + r + 2
        for i, (login, pid) in enumerate(losers):
            label = f"@{faces.label(login, pid)}" if pid not in faces.gone else faces.label(login, pid)
            w = max(2 * r, sk.width(label.upper(), "caps", 7.5, .5))
            if x + w / 2 > PX1:
                break
            cy2 = ly + 36
            at = F + 3.3 + i * .25
            fade = clk.anim("opacity", [(0, 1), (at, 1), (at + .18, .4)])
            out.append(f"<g>{fade}" + faces.face(login, pid, x, cy2, r, ring=1.3)
                       + sk.caps(cv, label, x, cy2 + r + 15, 7.5, ls=.5, anchor="middle") + "</g>")
            x += 2 * r + 34 + max(0, w - 2 * r)
        out.append("</g>")
        # the whole game's score, the deciding move marked
        gy = ly + 88
        out.append(f'<g opacity="0">{rise(clk, [(F + 4.2, D)])}')
        out.append(sk.rule(PX0, PX1, gy - 12))
        out.append(heading(cv, sk, "the game", PX0, gy + 8))
        out.append(sk.caps(cv, f"{len(f['plies'])} moves  ·  {f['span']}", PX1, gy + 8, 7.5, ls=.5, anchor="end"))
        out.append(self.score(gy + 24))
        out.append("</g>")
        return "".join(out)

    def plate(self, x, y, won_house) -> str:
        """The finished board's own plate: who won, with how in its second panel sliding open out of it, and a
        glint crossing it, as the README's finished board sets it in the turn's place."""
        cv, sk, pl, f = self.cv, self.sk, self.pl, self.f
        clk, F = pl.clock, pl.finale
        label = f"@{OWNER} wins" if won_house else "github wins"
        plate = sk.chip(label, f["reason"], icon="trophy", size=9.5, lab="turn", msg="alert")
        out = [plate.draw_label(cv, x, y, "turn")]
        paint, peak = sk.glint(cv, solid=False)
        clip = cv.uid("b")
        cv.defs.append(f'<clipPath id="{clip}"><rect x="{f1(x)}" y="{f1(y)}" width="{f1(plate.lw)}" '
                       f'height="{f1(plate.h)}"/></clipPath>')
        runs = [F + 3.2] + ([F + 8.2] if F + 9.3 < pl.total else [])
        xs, ops = [(0, f1(x - 40))], [(0, 0)]
        for g in runs:
            xs += [(g, f1(x - 40), EASE), (g + 1.04, f1(x + plate.lw + 40)), (g + 1.05, f1(x - 40))]
            ops += [(g, 0), (g + .08, float(peak)), (g + 1.04, float(peak)), (g + 1.05, 0)]
        out.append(f'<g clip-path="url(#{clip})"><rect x="{f1(x - 40)}" y="{f1(y - 4)}" width="30" '
                   f'height="{f1(plate.h + 8)}" fill="{paint}" opacity="0" transform="skewX(-20)">'
                   + clk.anim("x", xs) + clk.anim("opacity", ops) + "</rect></g>")
        msg = plate.draw_message(cv, x + plate.lw, y, f["reason"])
        wid = cv.uid("c")
        cv.defs.append(f'<clipPath id="{wid}"><rect x="{f1(x + plate.lw)}" y="{f1(y)}" width="0" '
                       f'height="{f1(plate.h)}">'
                       + clk.anim("width", [(0, "0"), (F + 1.7, "0", ".2 .7 .2 1"), (F + 2.12, f1(plate.mw))])
                       + "</rect></clipPath>")
        out.append(f'<g clip-path="url(#{wid})">{msg}</g>')
        return "".join(out)

    def score(self, y) -> str:
        """Every move of the game in one flowing score, as a score sheet is copied out, the deciding move ringed. A
        game too long for six lines shows its last six, as a sheet's last page does."""
        cv, sk, f = self.cv, self.sk, self.f
        size, ls, lead = 8.4, .3, 13
        tokens = self.g.score_tokens(f["plies"])
        room = PX1 - PX0
        lines, cur, width_cur = [], [], 0.0
        space = sk.width(" ", "bold", size, ls) + 2
        for tok in tokens:
            w = self.g.token(cv, sk, tok, 0, 0, size, ls=ls)[1]
            if cur and width_cur + space + w > room:
                lines.append(cur)
                cur, width_cur = [], 0.0
            cur.append((tok, w))
            width_cur += (space if len(cur) > 1 else 0) + w
        if cur:
            lines.append(cur)
        lines = lines[-6:]
        out = []
        for row, items in enumerate(lines):
            x = PX0
            for tok, w in items:
                out.append(self.g.token(cv, sk, tok, x, y + row * lead + 8, size, role="muted", ls=ls)[0])
                x += w + space
        last_row = len(lines) - 1
        items = lines[last_row]
        x = PX0 + sum(w for _, w in items[:-1]) + space * (len(items) - 1)
        w = items[-1][1]
        out.append(f'<rect x="{f1(x - 3)}" y="{f1(y + last_row * lead - 2.4)}" width="{f1(w + 6)}" '
                   f'height="{f1(lead + .4)}" fill="none" stroke="{c(sk.mark)}" stroke-width="1.3"/>')
        return "".join(out)


def owner_id(f: dict) -> int | None:
    """The house's account ID, from the first turn the house played itself."""
    for p in f["plies"]:
        if p["side"] == "house" and p["by"] == OWNER:
            return p.get("by_id")
    return None
