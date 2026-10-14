# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: LicenseRef-Proprietary
"""The Checkers sheet's layout: its board, and what its panel counts, inside the sheet every game shares.

The board is chess's, in chess's place at chess's size, drawn by chess's own skins, with each of its thirty-two dark
squares carrying its number, since that is how checkers writes its moves. It is drawn from the house's side, White
at the foot as chess draws White, so it reads as American checkers' diagrams print it: Black's squares 1 to 4 at the
head and White's 29 to 32 along the foot. GitHub plays Black and moves first; the house plays White. As the file
opens the last move's man slides, or hops over each man it takes, those men fading on their squares as it passes,
the jump's path drawn in behind it; a man reaching the far row is crowned as it lands; a man that must jump is
marked as chess marks a king in check. In place of chess's taken pieces the panel counts the men each side has taken
and the kings each has made.
"""
from __future__ import annotations

import sys

from ...canvas import c
from ...lettering import f1, fx
from ..games import sheet as S
from ..games.sides import HOUSE, other
from . import motion as M
from .game import COLOUR, KIND, OPENS, material_of, rc  # noqa: F401  (KIND: the sheet's stamp)
from .shapes import SHADOW

LABEL = "checkers"
glyph = glyph_width = None              # Black moves first: the score sheet's columns say whose each move is


def xy(st, n: int, x0, y0, s) -> tuple[float, float]:
    """A square's top-left corner on the board, as American checkers' diagrams print it: White, the house's, at the
    foot, and Black's back row at the head."""
    r, col = rc(n)
    return x0 + col * s, y0 + r * s


def material(st, piece: str) -> str:
    return "dark" if piece.lower() == "d" else "light"


# --------------------------------------------------------------------------- the sheet's questions
def band_mark(x, y, size, paper, block="") -> str:
    """The band's mark: a crowned king, two men stacked with the seam between them cut, a crown standing on top."""
    return (f'<g transform="translate({f1(x)} {f1(y)}) scale({fx(size / 20, 4)})">'
            f'<path d="M2 10.8V16.6A8 2.7 0 0 0 18 16.6V10.8A8 2.7 0 0 0 2 10.8Z" fill="{paper}"/>'
            f'<path d="M2 13.7A8 2.7 0 0 0 18 13.7" fill="none" stroke="{block or paper}" stroke-width="1"/>'
            f'<path d="M5.6 10.4 4.9 4.4 7.7 6.9 10 2.6 12.3 6.9 15.1 4.4 14.4 10.4Z" fill="{paper}" '
            f'stroke="{block or paper}" stroke-width="1.1" stroke-linejoin="round" paint-order="stroke"/></g>')


def room(x0, y0, n) -> tuple:
    return (x0 - 2, y0 - 2, n + 10, n + 10)


def height(n, small=False) -> float:
    return n


def side_name(side, st) -> str:
    return COLOUR[side]


def first(st) -> str:
    """Before the first move, which colour moves first: Black, GitHub's, as American checkers has it."""
    return f"{COLOUR[OPENS]} moves first"


def medallion(cv, sk, st, cx, cy, r, side) -> str:
    """A side's medallion, holding a king of its own: White for the house, Black for GitHub."""
    k = 2 * r * 1.02
    colour = material_of(side)
    return sk.medal(cv, cx, cy, r, colour) + sk.man(cv, colour, True, cx - k / 2, cy - k / 2 - r * .02, k,
                                                    shadow=False)


# --------------------------------------------------------------------------- the board
def board(cv, sk, st, x0, y0, n, *, small=False) -> None:
    s = n / 8
    sk.board_base(cv, x0, y0, s)
    last = st["last"]
    pieces = st["pieces"]
    land, passes = 0.0, []
    if last:
        tx, ty = xy(st, last["path"][-1], x0, y0, s)
        offsets = [(x - tx, y - ty) for x, y in (xy(st, q, x0, y0, s) for q in last["path"])]
        if M.moving():
            _, _, land, passes = M.journey(offsets, bool(last["jumped"]), s)
        king_before = pieces[last["path"][-1]].isupper() and not last["crowned"]
        sk.from_square(cv, *xy(st, last["path"][0], x0, y0, s), s, king_before)
        for sq in last["jumped"]:
            sk.taken_square(cv, *xy(st, sq, x0, y0, s), s)
        sk.mark_to(cv, tx, ty, s, M.appear(land - .04, .1) if M.moving() else "")
    clip = cv.uid("b")
    cv.defs.append(f'<clipPath id="{clip}"><rect x="{f1(x0)}" y="{f1(y0)}" width="{f1(n)}" height="{f1(n)}"/>'
                   "</clipPath>")
    sk.board_over(cv, clip, x0, y0, s, None, "")      # the board's face catching the lamp, as chess's does
    size = 7 if not small else 6.5
    cv.add("".join(sk.tab(cv, sq, x + 1.6, y + 1.6, size) for sq in range(1, 33)
                   for x, y in [xy(st, sq, x0, y0, s)]))
    rest, mover = [], ""
    for sq in sorted(pieces, key=lambda q: (xy(st, q, x0, y0, s)[1], xy(st, q, x0, y0, s)[0])):
        piece = pieces[sq]
        x, y = xy(st, sq, x0, y0, s)
        if last and sq == last["path"][-1] and M.moving():
            mover = moving_man(cv, sk, st, piece, x0, y0, s)
            continue
        rest.append(sk.man(cv, material(st, piece), piece.isupper(), x, y, s))
    if last and last["jumped"]:
        # the men the jump took: phantoms on their squares, and in a moving file the men themselves, each fading
        # as the jumper passes over it
        lost = "light" if pieces[last["path"][-1]].lower() == "d" else "dark"
        for i, sq in enumerate(last["jumped"]):
            x, y = xy(st, sq, x0, y0, s)
            rest.append(sk.phantom_man(x, y, s))
            if M.moving():
                rest.append(f'<g>{M.fade_at(passes[i])}{sk.man(cv, lost, False, x, y, s)}</g>')
    cv.add("".join(rest))
    for sq in st["jumpers"]:
        # a man that must jump, marked as chess marks a king in check, blooming as the last move lands
        x, y = xy(st, sq, x0, y0, s)
        pulse = M.ani("opacity", "0;0;1;.5;1;.5;1", ".0;.27;.38;.52;.66;.8;1", ((land or 1.15) + .2) / .27)
        cv.add(sk.clouded(cv, x, y, s, pulse, clip=clip))
    if last and last["jumped"]:
        pts = [(x + s / 2, y + s / 2) for x, y in (xy(st, q, x0, y0, s) for q in last["path"])]
        d = "M" + "L".join(f"{f1(x)} {f1(y)}" for x, y in pts)
        length = sum(((bx - ax) ** 2 + (by - ay) ** 2) ** .5 for (ax, ay), (bx, by) in zip(pts, pts[1:]))
        mask = ""
        if M.moving():
            mask = cv.uid("m")
            extra, anim = M.stroke_in(length, M.START, land - M.START, eased=False)
            cv.defs.append(f'<mask id="{mask}" maskUnits="userSpaceOnUse" x="{f1(x0)}" y="{f1(y0)}" width="{f1(n)}" '
                           f'height="{f1(n)}"><path d="{d}" fill="none" stroke="{c("white")}" stroke-width="9" '
                           f'stroke-linecap="round" stroke-linejoin="round"{extra}>{anim}</path></mask>')
        cv.add(sk.chain(d, mask) + "".join(sk.landing(x, y, 2.6) for x, y in pts[1:-1]))
    cv.add(mover)
    if last and M.moving():
        cx, cy = xy(st, last["path"][-1], x0, y0, s)
        t = land + .9
        k = fx(land / t, 3)
        cv.add(f'<rect x="{f1(cx)}" y="{f1(cy)}" width="{f1(s)}" height="{f1(s)}" fill="{sk.flash}" opacity="0">'
               + M.ani("opacity", "0;0;.7;0;0", f"0;{fx(land / t - .02, 3)};{fx(land / t + .03, 3)};.95;1", t)
               + "</rect>"
               + sk.ripple_at(cx + s / 2, cy + s / 2, s * .3, s * 1.15, land, clip=clip))
    sk.bevel(cv, x0, y0, n)


def moving_man(cv, sk, st, piece, x0, y0, s) -> str:
    """The last move's man on its way, from the square it set out from through every landing to where it rests,
    its shadow going along the board under it; crowned, the crown's man dropped onto it once it lands."""
    last = st["last"]
    tx, ty = xy(st, last["path"][-1], x0, y0, s)
    offsets = []
    for q in last["path"]:
        x, y = xy(st, q, x0, y0, s)
        offsets.append((x - tx, y - ty))
    jump = bool(last["jumped"])
    move, grow, land, _ = M.journey(offsets, jump, s)
    ground, _, _, _ = M.journey(offsets, jump, s, lifted=False)
    mat = material(st, piece)
    k = s / 45
    king = piece.isupper() and not last["crowned"]
    sx, sy, rx, ry = tx + SHADOW[0] * k, ty + SHADOW[1] * k, SHADOW[2] * k, SHADOW[3] * k
    shadow = f'<g>{ground}' + sk.foot(cv, sx, sy, rx, ry, "") + "</g>"
    cx, cy = tx + s / 2, ty + s / 2
    place = f'transform="translate({f1(-s / 2)} {f1(-s / 2)}) scale({fx(k, 4)})"'
    body = f'<use href="#{sk.man_def(cv, mat, king, shadow=False)}" {place}/>'
    if last["crowned"]:
        top = sk.man_def(cv, mat, True, shadow=False, top_only=True)
        body += f'<g>{M.crowned(land, s)}<use href="#{top}" {place}/></g>'
    return shadow + f'<g>{move}<g transform="translate({f1(cx)} {f1(cy)})"><g>{grow}{body}</g></g></g>'


# --------------------------------------------------------------------------- the panel's count
def count(cv, sk, st, x0, x1, y, *, small=False) -> float:
    """The men each side has taken and the kings each has made, where chess counts what each side took: the taken
    men on a tray in their own colour, the side ahead marked as chess marks a lead, and the kings at the row's end;
    the house's White first, as every pair of sides is listed."""
    cv.add(sk.heading(cv, "taken", x0, y))
    mini = 20 if not small else 18
    yy, px = y + 10, x0 + 72
    lead = st["took"][HOUSE] - st["took"][other(HOUSE)]
    for side in (HOUSE, other(HOUSE)):
        colour = material_of(side)
        lost = material_of(other(side))
        cv.add(sk.caps(cv, f"{COLOUR[side]} took", x0, yy + mini / 2 + 3, 7.5, ls=.6, role="muted"))
        took = st["took"][side]
        kings = st["kings"][side]
        shown = kings if kings <= 3 else 1
        many = f"x{kings}" if kings > 3 else ""
        kw = sk.width("KINGS", "caps", 7, .5) + 6 + max(shown, 1) * mini * .62 + 6 + (sk.width(many, "bold", 9) + 4
                                                                                       if many else 0)
        room = x1 - px - kw - 34
        pitch = min(mini * .78, (room - 8) / max(took, 1))
        sk.tray(cv, px - 4, yy - 1, max(took, 1) * pitch + 9 if took else 20, mini + 2)
        tx = px
        for _ in range(took):
            cv.add(sk.man(cv, lost, False, tx - mini * .08, yy + mini * .02, mini, shadow=False))
            tx += pitch
        ahead = lead if side == HOUSE else -lead
        if ahead > 0:
            chip = sk.chip(f"+{ahead}", "", size=7.5, lab="accent")
            cv.add(chip.draw(cv, (tx if took else px + 16) + 10, yy + (mini - chip.h) / 2, "men"))
        # the kings this side has made, at the row's end
        kx = x1
        if kings:
            if many:
                cv.add(sk.say(cv, many, kx, yy + mini / 2 + sk.cap(9) / 2, 9, anchor="end"))
                kx -= sk.width(many, "bold", 9) + 4
            for _ in range(shown):
                kx -= mini * .62
                cv.add(sk.man(cv, colour, True, kx - mini * .2, yy - mini * .02, mini, shadow=False))
        else:
            kx -= 4
            cv.add(sk.caps(cv, "none", kx, yy + mini / 2 + 3, 7, ls=.5, anchor="end"))
            kx -= sk.width("NONE", "caps", 7, .5)
        cv.add(sk.caps(cv, "kings", kx - 6, yy + mini / 2 + 3, 7, ls=.5, anchor="end"))
        yy += mini + 7
    return yy


def board_sheet(sk, st, title, desc, variant="wide") -> str:
    return S.board_sheet(sk, sys.modules[__name__], st, title, desc, variant)
