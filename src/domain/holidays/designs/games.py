# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The games on @tannergolden's profile as every pixel set draws them: the four boards, and the Hall of Fame of all four.

A set restyles a game the way it restyles every other part of the page, and never changes what it is. Each board
keeps the sheet every game shares, as the standard theme and the prints draw it: the board where chess's stands, at
its size, and beside it, under it on a phone, the same panel a section at a time: the two sides with the turn
ringed, the turn's plate and when the move is due, the last move in its notation and in words, what the game counts,
and the score sheet. It keeps its words, its files and its README block. What changes is its world: it stands on the
set's own paper inside the set's own frame, by night under the set's sky, named on the set's own tag with the set's
touch along its rule; its words are lettered in the set's two faces and its inks, the move in the set's own title
lettering; its plates are the set's tags; and the board is built of the set's own world.

  the board    its squares of what the set says they are made of (`game_squares`), each a `materials.Stuff`, a
               ramp of the set's own tones, the tone it stands at and its grain: planks, ashlar, slate, tesserae,
               weave, glass in its lead; no two squares alike and a wooden board's dark ones turned across the grain.
               Its frame of what the set frames it in and how (`game_frame`): oak mitred, gilt beaded, ashlar in
               courses, iron riveted, a chart's neatline. A set that names no squares has them picked from its
               closed palette, the dark in its tag's hue at a lightness every piece holds on and the light near its
               paper (`game_board`), so a board is in no colour the set does not have; lit from the upper left
  the pieces   ivory and ebony in every set (`pieces`), as the trophies are struck in one set of metals: the house's
               always ivory, GitHub's ebony, whoever moves first
  the marks    the last move's two squares in the set's accent; what the side to move must answer (a king in check,
               a cell or a column to block, a man that must jump) glowing in the set's red; either, where it would
               be lost on a square of its colour, in the first of the set's inks that stands clear of both
  the motion   the last move is played again as the file opens, in the engine's discrete steps: a chessman steps
               from its square, a knight hopping; a man hops each man it takes; a disc drops down its column and
               bounces; a mark is drawn in stroke by stroke. The square it lands on flashes, what must be answered
               pulses, the panel appears a section at a time on chess's beats, the side to move's ring is drawn in,
               and a glint crosses the turn's plate every eight seconds. A still file holds it all at rest

The Hall of Fame is drawn on the same sheet (`hall`): the series of every game, each named by its two pieces, and
the podium, the set's own avatars standing on blocks cut from what the set says its podium is made of and worked as
its world works it (`game_podium`, a `materials.Podium`), a plaque of the trophies' gold, silver and bronze on each.

Every colour a game file of the set paints is the set's or the pieces' and metals' (`game_tokens`), and every word
is set in the set's inks, so a collection's design draws its games in its hand. A file the set cannot letter, a
winner's name in a script its faces lack, is not drawn here: the kit draws the whole element in the page's own look.
"""
from __future__ import annotations

import math

from ... import KIT, KIT_VERSION
from ...canvas import BUDGET
from ..pixel import GLYPHS, MISSING, Pix, clip, fold, measure, num, wrap
from . import pieces as PC
from .badges import _lab
from .materials import Podium, Stuff, surface
from .banners import NARROW, WIDE
from .trophies import METAL_TOKENS

TAG = 9                 # a tag's height, as every set draws one
LEAD = 9                # from one line of a move's words to the next, in the 5x7 face with its descenders
GAP = 4                 # what keeps a run of lettering off the next thing along
# The beats, chess's: the panel's sections appear in turn, and the last move lands.
SECTIONS = (.15, .3, .45, .6)
LAND = 1.15             # when the last move lands, chess's: 0.72 of its 1.6 seconds
GLINT = 8.0             # seconds between the glints across the turn's plate


# --------------------------------------------------------------------------- motion
def _t(v: float) -> str:
    return num(round(v, 3))


def appear(at: float) -> str:
    """Opacity from nothing to whole in one step, `at` seconds in, and held: a part that appears as the file opens."""
    dur = at + .1
    return (f'<animate attributeName="opacity" values="0;1" keyTimes="0;{_t(at / dur)}" dur="{_t(dur)}s" '
            'calcMode="discrete" fill="freeze"/>')


def steps(offsets: list, times: list, dur: float) -> str:
    """A translate through each of `offsets` (dx, dy) at each of `times`, in discrete steps, held at the last."""
    values = ";".join(f"{_t(dx)} {_t(dy)}" for dx, dy in offsets)
    keys = ";".join(_t(t / dur) for t in times)
    return (f'<animateTransform attributeName="transform" type="translate" values="{values}" keyTimes="{keys}" '
            f'dur="{_t(dur)}s" calcMode="discrete" fill="freeze"/>')


def blinks(values: str, times: list, dur: float, *, repeat: bool = False, begin: float = 0) -> str:
    """Opacity through `values` at `times`, in discrete steps: held at the last, or round again for `repeat`."""
    keys = ";".join(_t(t / dur) for t in times)
    tail = ' repeatCount="indefinite"' if repeat else ' fill="freeze"'
    b = f' begin="{_t(begin)}s"' if begin else ""
    return (f'<animate attributeName="opacity" values="{values}" keyTimes="{keys}" dur="{_t(dur)}s"{b} '
            f'calcMode="discrete"{tail}/>')


def pulse(at: float) -> str:
    """What must be answered, blooming as the move lands and pulsing three times before it holds."""
    times = [0, at, at + .25, at + .5, at + .75, at + 1.0, at + 1.25]
    dur = at + 1.35
    return blinks("0;1;.45;1;.45;1;1", times, dur)


def brief(cells: dict, at: float, hold: float = .3) -> str:
    """Pixels shown for a moment, `at` seconds in: a flash as a move lands, gone again. Moving markup only."""
    dur = at + hold + .1
    return (f'<g opacity="0">{_paths(cells)}<animate attributeName="opacity" values="0;1;0" '
            f'keyTimes="0;{_t(at / dur)};{_t((at + hold) / dur)}" dur="{_t(dur)}s" calcMode="discrete" '
            'fill="freeze"/></g>')


def gone(cells: dict, at: float) -> str:
    """Pixels there as the file opens and gone `at` seconds in: what a move takes, as it lands. Moving markup only."""
    dur = at + .1
    return (f'<g opacity="0">{_paths(cells)}<animate attributeName="opacity" values="1;0" '
            f'keyTimes="0;{_t(at / dur)}" dur="{_t(dur)}s" calcMode="discrete" fill="freeze"/></g>')


def _paths(cells: dict) -> str:
    return Pix(1, 1).markup(cells)


# --------------------------------------------------------------------------- colour
def lab(colour: str) -> tuple[float, float, float]:
    """A colour's CIELAB lightness L*, its chroma C* and its hue angle in degrees."""
    L, a, b = _lab(colour)
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def _hue_gap(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


def nearest_tone(tokens, hue: float, light: float, *, least: float = 0, most: float = 200, span: float = 180,
                 avoid=()) -> str | None:
    """The colour of `tokens` nearest lightness `light` with a chroma from `least` to `most` within `span` degrees
    of `hue`, the nearer in hue preferred; None when there is none."""
    best = None
    for t in tokens:
        if t in avoid:
            continue
        L, C, h = lab(t)
        if not least <= C <= most or _hue_gap(h, hue) > span:
            continue
        score = abs(L - light) + _hue_gap(h, hue) * .12
        if best is None or score < best[0]:
            best = (score, t)
    return best[1] if best else None


def _delta(a: str, b: str) -> float:
    """How far apart two colours are, CIELAB's distance."""
    return math.dist(_lab(a), _lab(b))


def _clear_of(colour: str, grounds: tuple, others: tuple, least: float = 28) -> str:
    """`colour`, or when it lies within `least` of any of `grounds`, the first of `others` that does not; failing
    that, whichever of them stands furthest from the nearest ground."""
    def gap(c):
        return min(_delta(c, g) for g in grounds)
    if gap(colour) >= least:
        return colour
    others = tuple(c for c in others if c)
    return next((c for c in others if gap(c) >= least), max((colour, *others), key=gap))


def _hued(tokens, hue: float, avoid: tuple, light: float, least: float = 28) -> str | None:
    """The colour of `tokens` of hue near `hue`, strong, near lightness `light`, standing clear of every one of
    `avoid`: an amber for the last move, a red for what must be answered, when the set's own is lost on its board."""
    best = None
    for t in tokens:
        L, C, h = lab(t)
        if C < 35 or _hue_gap(h, hue) > 40 or min(_delta(t, a) for a in avoid) < least:
            continue
        score = _hue_gap(h, hue) + abs(L - light) * .5
        if best is None or score < best[0]:
            best = (score, t)
    return best[1] if best else None


def _ramped(colour: str, tokens) -> Stuff:
    """A bare colour as a stuff with no grain, its ramp the set's tones of its family, darkest first: so a frame
    worked in it can still be lit and shaded."""
    L0, C0, h0 = lab(colour)
    kin = {t for t in tokens if (lab(t)[1] < 8) == (C0 < 8) and (C0 < 8 or _hue_gap(lab(t)[2], h0) <= 25)}
    ramp = tuple(sorted(kin | {colour}, key=lambda t: lab(t)[0]))
    return Stuff(ramp, ramp.index(colour))


# --------------------------------------------------------------------------- the mixin
class Games:
    """The games' layouts. Every drawing hook a set overrides is listed first, with its default."""

    # ------------------------------------------------------------------------------------------ hooks
    def game_squares(self, night: bool) -> tuple | None:
        """What the board's light and dark squares are made of, when the set names them from its own world: (light,
        dark), each a `materials.Stuff`, a ramp of the set's tones with the tone it stands at and its grain, or a
        bare colour; None has the board picked from the set's palette, in flat colour (see `game_board`)."""
        return None

    def game_frame(self, night: bool) -> tuple | None:
        """What the board's frame is made of and how it is worked: (stuff, style), the style one of
        `materials.FRAMES`; None frames the board plainly, in a darker tone of its dark squares."""
        return None

    def game_podium(self, night: bool) -> Podium:
        """What the Hall's podium is cut from and how it is worked, a `materials.Podium`: by default plainly, of what
        the board's dark squares are. Each block carries a plaque of its place's metal, so a podium of gold should
        not be asked for."""
        return Podium(self.game_board(night)["dark_stuff"])

    def game_board(self, night: bool) -> dict:
        """The board's colours, picked from the set's own palette, so a board is in no colour the set does not
        have: its dark squares (`dark`) in the family of the set's tag, the colour that names every element, at a
        middling lightness every piece holds on; its light squares (`light`) in the family of its paper; and the
        edge it is framed in (`edge`, and `shade`, darker). By night the board stands a little dimmer. With them,
        what each is made of: the squares' stuffs (`light_stuff`, `dark_stuff`), and the frame's (`frame`) and how
        it is worked (`style`)."""
        kept = self.__dict__.setdefault("_game_boards", {})
        if night not in kept:
            kept[night] = self._board_colours(night)
        return kept[night]

    def _board_colours(self, night: bool) -> dict:
        # A collection's design builds its board of its own materials, never of the colours its hand lends every
        # design alike, its people's skin, its flames and its moon, so no two designs share a board by way of them.
        hand = getattr(self, "hand", None)
        tokens = sorted(set(self.tokens) - set(hand.tokens if hand else ())) or sorted(self.tokens)
        chosen = self.game_squares(night)
        if chosen:
            light, dark = chosen
            if isinstance(light, Stuff):
                light, dark, stuffs = light.base, dark.base, (light, dark)
            else:
                stuffs = (_ramped(light, tokens), _ramped(dark, tokens))
        else:
            tag = self._tag_colour(night)
            hue = lab(tag)[2]
            q = Pix(60, 60)
            self.paper(q, False, uid="gb")
            paper = self.bg_at(q, False, 30)
            lo, hi = (44, 74) if night else (52, 86)
            dark = (nearest_tone(tokens, hue, lo, least=10, span=16)
                    or nearest_tone(tokens, hue, lo, least=6, span=40) or tag)
            light = (nearest_tone(tokens, lab(paper)[2], hi, most=40, span=40, avoid={paper})
                     or nearest_tone(tokens, hue, hi, most=36) or self.ink(False)["fill"])
            stuffs = (_ramped(light, tokens), _ramped(dark, tokens))
        L, _, h = lab(dark)
        edge = nearest_tone(tokens, h, L - 18, least=6, span=40, avoid={dark}) or self.ink(night)["body"]
        shade = nearest_tone(tokens, h, L - 32, least=4, span=60, avoid={dark, edge}) or edge
        framed = self.game_frame(night)
        frame, style = framed if framed else (Stuff(stuffs[1].ramp, max(0, stuffs[1].at - 2)), "plain")
        return {"light": light, "dark": dark, "edge": edge, "shade": shade, "light_stuff": stuffs[0],
                "dark_stuff": stuffs[1], "frame": frame, "style": style}

    def game_title(self, p: Pix, x: int, y: int, s: str, night: bool, scale: int) -> int:
        """The last move's notation, and the Hall's totals, lettered as the set letters its titles. A set whose titles
        stand on a ground of their own, a panel or a scroll, letters a move without it: a move is one of the sheet's
        words, not its title. Returns the width."""
        return self.title_text(p, x, y, s, night, scale)

    def game_marks(self, night: bool) -> dict:
        """The marks a board carries: the last move's (`last`, the set's accent), and what the side to move must
        answer (`alert`, the set's red). A mark too near the colour of either square for its square to show it, as a
        red accent on a red board, takes instead the first of the set's inks that stands clear of both."""
        b = self.game_board(night)
        k = self.ink(night)
        squares = (b["light"], b["dark"])
        tokens = sorted(self.game_tokens)
        last = _clear_of(k["accent"], squares, (_hued(tokens, 75, squares, 62 if night else 52), k["title"]))
        red = self.badge_states()["red"][0]
        alert = _clear_of(red, squares + (last,), (_hued(tokens, 25, squares + (last,), 60 if night else 45),
                                                   k["title"], k["body"]))
        return {"last": last, "alert": alert}

    @property
    def game_tokens(self) -> frozenset:
        """Every colour a game file of the set may paint: the set's closed palette, the pieces' two materials and
        the trophies' metals the podium is struck in."""
        return frozenset(self.tokens) | PC.TOKENS | METAL_TOKENS

    # ------------------------------------------------------------------------------------- lettering
    def _tag_colour(self, night: bool) -> str:
        """The colour the set's tag is mostly made of: what names every element, the set's own."""
        kept = self.__dict__.setdefault("_game_tags", {})
        if night not in kept:
            kept[night] = self._tag_mostly(night)
        return kept[night]

    def _tag_mostly(self, night: bool) -> str:
        q = Pix(40, 20)
        self.tag(q, 2, 2, 30, TAG, night)
        counts: dict = {}
        for c in q.layers["base"].values():
            counts[c] = counts.get(c, 0) + 1
        return max(sorted(counts), key=lambda c: counts[c]) if counts else self.ink(night)["accent"]

    @staticmethod
    def fitted(s: str, room: int, font: str = "35", scale: int = 1) -> str:
        """`s` as it fits `room` in `font`: whole, or cut short with an ellipsis."""
        return clip(str(s), room, font, scale)

    def say(self, p: Pix, x: int, y: int, s: str, ink: str, font: str = "35", *, room: int | None = None,
            anchor: str = "start", scale: int = 1) -> int:
        """A line of letters in one of the set's inks, fitted to `room` if one is given: set tighter, its letters
        touching as a word too wide for its line is set, and cut short with an ellipsis only if even that is too
        wide. Set from `x`, or ending at it (`anchor` end), or centred on it (middle). Returns its width."""
        s = fold(str(s), font)
        track = 1
        if room is not None and measure(s, font, scale) > room:
            track = 0
            if measure(s, font, scale, 0) > room:
                s = clip(s, room, font, scale, 0)
        w = measure(s, font, scale, track)
        if anchor == "end":
            x -= w
        elif anchor == "middle":
            x -= w // 2
        p.text(x, y, s, ink, font, scale, track=track)
        return w

    def fits(self, s: str, room: int, font: str = "35") -> bool:
        """Whether `s` fits `room`, set tighter if it must be."""
        return measure(fold(str(s), font), font, 1, 0) <= room

    def heading(self, p: Pix, x: int, y: int, s: str, night: bool, key: str | None = None) -> None:
        """A section's heading in small capitals, quietly, after a swatch of the colour it keys when it has one."""
        k = self.ink(night)
        if key:
            p.rect(x, y, 5, 5, key)
            x += 8
        p.text(x, y, fold(s.upper(), "35"), k["muted"], "35")

    # ------------------------------------------------------------------------------------- the parts
    def plate(self, p: Pix, x: int, y: int, label: str, message: str, icon: str | None, night: bool,
              track: int = 1) -> tuple:
        """The turn's plate: the label on the set's tag after its icon, and what it adds on a block of the set's red
        beside it, set tighter (`track` 0) where the row is short. Returns the label's block and the message's, as
        (x, w) each, the message's w 0 without one."""
        k = self.ink(night)
        lab_ = fold(label.upper(), "35")
        iw = 7 if icon else 0
        lw = 4 + (iw + 3 if icon else 0) + measure(lab_, "35", 1, track) + 4
        self.tag(p, x, y, lw, TAG, night)
        tx = x + 4
        if icon:
            p.sprite(tx, y + 1, GLYPHS[7].get(icon, GLYPHS[7]["star"]), {"#": k["tag_ink"]})
            tx += iw + 3
        p.text(tx, y + 2, lab_, k["tag_ink"], "35", track=track)
        mw = 0
        if message:
            block, letters = self.badge_states()["red"]
            msg = fold(message.upper(), "35")
            mw = 4 + measure(msg, "35", 1, track) + 4
            p.rect(x + lw, y, mw, TAG, block)
            p.text(x + lw + 4, y + 2, msg, letters, "35", track=track)
        return (x, lw), (x + lw, mw)

    @staticmethod
    def plate_width(label: str, message: str, icon: str | None, track: int = 1) -> int:
        w = 4 + (10 if icon else 0) + measure(fold(label.upper(), "35"), "35", 1, track) + 4
        return w + (8 + measure(fold(message.upper(), "35"), "35", 1, track) if message else 0)

    def medal(self, p: Pix, cx: int, cy: int, r: int, material: str, night: bool, L: str = "base") -> None:
        """A side's medallion before anything is set in it: a disc of the board's colour that sets its pieces off,
        the house's ivory on the board's dark, GitHub's ebony on its light, lit from the upper left and edged."""
        b = self.game_board(night)
        face = b["dark"] if material == "light" else b["light"]
        edge = b["shade"]
        for y in range(cy - r - 1, cy + r + 2):
            for x in range(cx - r - 1, cx + r + 2):
                d = math.hypot(x + .5 - cx, y + .5 - cy)
                if d <= r - .5:
                    p.px(x, y, face, L)
                    if d > r - 1.6 and (x + .5 - cx) + (y + .5 - cy) < -r * .5:
                        p.px(x, y, f"{PC.IVORY[6]}:0.35", L)
                elif d <= r + .6:
                    p.px(x, y, edge, L)

    def ring(self, p: Pix, cx: int, cy: int, r: float, colour: str, L: str = "base", arcs: int = 0,
             moving: bool = False, at: float = 1.1) -> None:
        """A ring round a medallion, a pixel thick: the side whose turn it is, drawn in from the top as the turn
        arrives, an arc at a time, when the file moves."""
        cells = []
        for y in range(math.floor(cy - r) - 2, math.ceil(cy + r) + 2):
            for x in range(math.floor(cx - r) - 2, math.ceil(cx + r) + 2):
                d = math.hypot(x + .5 - cx, y + .5 - cy)
                if r - .5 <= d < r + .5:
                    cells.append((x, y))
        if not moving:
            for (x, y) in cells:
                p.px(x, y, colour, L)
            return
        n = 8
        for i in range(n):
            arc = [(x, y) for (x, y) in cells
                   if int(((math.atan2(x + .5 - cx, -(y + .5 - cy)) / (2 * math.pi)) % 1) * n) == i]
            name = p.once(f"ring{i}", appear(at + i * .06), z=1.2)
            for (x, y) in arc:
                p.px(x, y, colour, name)

    def tray(self, p: Pix, x: int, y: int, w: int, h: int, night: bool, L: str = "base") -> None:
        """The strip a game's count stands on: the board's light square, in its grain, edged, so both sides' pieces
        hold on it. Laid pixel by pixel, under whatever is set on it in the same layer."""
        b = self.game_board(night)
        for (dx, dy), c in surface(b["light_stuff"], w, h).items():
            p.px(x + dx, y + dy, c, L)
        p.box(x, y, w, h, b["edge"], L, notch=True)

    def chip(self, p: Pix, x: int, y: int, s: str, night: bool, L: str = "base") -> int:
        """A count on one of the set's tags, its letters in the tag's ink. Returns its width."""
        k = self.ink(night)
        s = fold(str(s).upper(), "35")
        w = measure(s, "35") + 8
        with p.onto(L) if L != "base" else _nothing():
            self.tag(p, x, y, w, TAG, night)
        p.text(x + 4, y + 2, s, k["tag_ink"], "35", L=L)
        return w

    # --------------------------------------------------------------------------- the panel's sections
    def matchup(self, p: Pix, g, st: dict, x0: int, x1: int, y: int, night: bool, small: bool, moving: bool) -> int:
        """The two sides across one row, the house on the left and GitHub on the right, each on its medallion with
        what it plays, the side to move ringed; once the game is over, neither."""
        k = self.ink(night)
        r = 9 if not small else 8
        cy = y + r + 1
        half = (x1 - x0) // 2
        for side, who in ((g.HOUSE, "@" + g.OWNER.upper()), (g.GITHUB, "GITHUB")):
            left = side == g.HOUSE
            cx = x0 + r + 1 if left else x1 - r - 1
            self.medal(p, cx, cy, r, g.material(side), night)
            g.medallion(self, p, st, cx, cy, r, side, night)
            if st["to_move"] == side and not st.get("result"):
                self.ring(p, cx, cy, r + 2.5, k["accent"], moving=moving)
            room = half - (2 * r + 6) - 1
            tx = cx + r + 5 if left else cx - r - 5
            anchor = "start" if left else "end"
            self.say(p, tx, cy - 6, who, k["body"], room=room - (6 if not small else 0), anchor=anchor)
            self.say(p, tx, cy + 2, g.role(side, st), k["muted"], room=room, anchor=anchor)
        if not small:      # between the two names, over the halfway line; a phone's row has no room for it
            self.say(p, (x0 + x1) // 2, cy - 6, "VS", k["muted"], anchor="middle")
        return y + 2 * r + 4

    def turn(self, p: Pix, g, st: dict, x0: int, x1: int, y: int, night: bool, small: bool, moving: bool) -> int:
        """Whose turn it is, on a plate under that side, with what it must do on a block of red beside it, and the
        day the move is due by across the row; once the game is over, who won and how, and the day the fresh board
        comes. A glint crosses the plate every eight seconds."""
        k = self.ink(night)
        label, message, icon, right, notes = g.plate(st)
        track = 1 if self.plate_width(label, message, icon) <= x1 - x0 else 0
        w = self.plate_width(label, message, icon, track)
        bx = x1 - w if right else x0
        (lx, lw), _ = self.plate(p, bx, y, label, message, icon, night, track)
        if moving:
            self.glint(p, lx, y, lw, TAG)
        room = x1 - x0 - w - GAP * 2
        note = next((n for n in notes if n and self.fits(n.upper(), room)), "")
        if note:
            self.say(p, x0 if right else x1, y + 2, note.upper(), k["muted"], anchor="start" if right else "end",
                     room=room)
            return y + TAG
        if notes and notes[0]:                  # no room beside the plate: the note under it, never left out
            self.say(p, x1 if right else x0, y + TAG + 3, notes[0].upper(), k["muted"],
                     anchor="end" if right else "start", room=x1 - x0)
            return y + TAG + 8
        return y + TAG

    def glint(self, p: Pix, x: int, y: int, w: int, h: int) -> None:
        """A band of light two pixels wide stepping across a plate every `GLINT` seconds, kept to the plate."""
        cid = f"gpg{x}x{y}"                     # a prefix no set's own ids take
        p.defs.append(f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>')
        band = {(x - 4 + (h - 1 - j) // 2 + i, y + j): PC.IVORY[6] for j in range(h) for i in range(2)}
        travel = w + 8
        n = 12
        values = ";".join(f"{_t(travel * i / (n - 1))} 0" for i in range(n)) + f";{_t(travel)} 0"
        keys = ";".join(_t(.8 + .12 * i / (n - 1)) for i in range(n)) + ";1"
        moving = (f'<g clip-path="url(#{cid})"><g opacity=".55">{_paths(band)}<animateTransform '
                  f'attributeName="transform" type="translate" values="0 0;{values}" keyTimes="0;{keys}" '
                  f'dur="{_t(GLINT)}s" begin="2.4s" calcMode="discrete" repeatCount="indefinite"/></g></g>')
        p.raw(25, moving, "")

    def last_move(self, p: Pix, g, st: dict, x0: int, x1: int, y: int, night: bool, small: bool) -> int:
        """The last move in the game's notation, lettered as the set letters its titles, its words on a line or two
        under it, and who played it when; before the first move, who opens the game."""
        k = self.ink(night)
        last = st["last"]
        self.heading(p, x0, y, "last move" if last else "first move", night, key=self.game_marks(night)["last"])
        number, move, side, words = g.notation(st)
        head = f"{number} "
        room = x1 - x0
        y += 9
        scale = 2 if measure(fold(head + move, "57"), "57", 2) + (g.glyph_width(2) if g.glyph else 0) <= room else 1
        w = self.game_title(p, x0, y, fold(head, "57"), night, scale) + 3 * scale
        x = x0 + w
        if g.glyph:
            x += g.glyph(self, p, st, side, x, y, scale, night)
        self.game_title(p, x, y, clip(fold(move, "57"), x1 - x, "57", scale), night, scale)
        y += 7 * scale + 5
        lines = wrap(words, room, "57")
        if len(lines) > 2:
            lines = [lines[0], clip(" ".join(lines[1:]), room, "57")]
        for line in lines:
            p.text(x0, y, line, k["body"], "57")
            y += LEAD
        y += 1
        if last:
            when = f"  ·  {last['when']}"
            by = fold(f"BY {last['by'].upper()}", "35")
            room_by = room - measure(fold(when.upper(), "35"), "35")
            self.say(p, x0, y, clip(by, room_by, "35") + when.upper(), k["muted"])
        else:
            self.say(p, x0, y, g.first(st).upper(), k["muted"], room=room)
        return y + 5

    def history(self, p: Pix, g, st: dict, x0: int, x1: int, y: int, night: bool, rows: int) -> int:
        """The latest moves, each side's under the side that played it, who chose each of GitHub's, the latest
        marked, and whose turn the next is; once the game is over, who won in that place."""
        k = self.ink(night)
        self.heading(p, x0, y, "moves", night)
        y += 10
        due = g.outcome(st) if st.get("result") else g.due_word(st)
        due_ink = k["body"] if st.get("result") else k["accent"]
        shown = g.rows(st)[-rows:]
        latest = g.latest(st)
        nw = max(14, max(measure(f"{n}.", "35") for n, *_ in shown) + 6)
        widths = [measure(fold(m, "57"), "57") + (g.glyph_width(1) if g.glyph else 0)
                  for _, a, b, _ in shown for m in (a, b) if m]
        col = max(34, (max(widths) if widths else 0) + 8)
        if x0 + nw + 2 * col + 36 > x1:
            col = max(28, (x1 - x0 - nw - 36) // 2)
        ax, bx = x0 + nw, x0 + nw + col
        first, reply = g.sides_in_order(st)
        for n, a, b, who in shown:
            if n == latest:
                p.rect(x0 - 2, y - 2, x1 - x0 + 2, 11, self.ink(night)["dim"])
            p.text(x0, y + 1, fold(f"{n}.", "35"), k["muted"], "35")
            wx = bx + col
            for text, side, cx in ((a, first, ax), (b, reply, bx)):
                if not text:
                    wdt = self.say(p, cx, y + 1, due.upper(), due_ink, room=x1 - cx - (40 if who else 0))
                    wx = max(wx if cx == bx else 0, cx + wdt + 6)
                    break
                if g.glyph:
                    cx += g.glyph(self, p, st, side, cx, y, 1, night)
                self.say(p, cx, y - 1 if any(ch in text for ch in "gjpqy") else y, text, k["body"], "57",
                         room=col - 6)
            if who:
                self.say(p, wx, y + 1, who.upper(), k["muted"], room=x1 - wx)
            y += 11
        return y

    # --------------------------------------------------------------------------- the sheet
    def head(self, p: Pix, night: bool, g, title: str, note: str | None) -> None:
        """The sheet's head, as every element of the set is headed: its kind on the set's tag, after the game's own
        mark, what it is beside it, a note at the right, and the set's rule under them."""
        k = self.ink(night)
        self.paper(p, night, uid="gs")
        if night:
            self.stars(p, 6, 22, p.w - 6, p.h - 8, p.w // 7, seed=27, twinkling=False, faint=True)
        self.frame(p, night)
        word = fold(g.LABEL.upper(), "35")
        tw = measure(word, "35")
        self.tag(p, 9, 8, tw + 18, TAG, night)
        g.mark(p, 13, 9, k["tag_ink"])
        p.text(23, 10, word, k["tag_ink"], "35")
        right = p.w - 10
        if note:
            note = clip(note, max(40, p.w // 2 - 20), "35")
            nw = measure(note, "35")
            p.text(p.w - 10 - nw, 10, note, k["muted"], "35")
            right -= nw + 8
        x = 9 + tw + 18 + 8
        if title:
            p.text(x, 9, clip(str(title), right - x), k["body"])
        p.hline(4, p.w - 4, 20, k["rule"])
        self.rule_decor(p, 5, p.w - 5, 20, 29, night)

    def panel(self, p: Pix, g, st: dict, x0: int, x1: int, y: int, night: bool, small: bool, moving: bool) -> int:
        """The panel, a section at a time, each appearing in turn on chess's beats as the file opens."""
        k = self.ink(night)

        def section(i: int):
            return p.onto(p.once(f"sec{i}", appear(SECTIONS[i]), z=.6)) if moving else _nothing()

        with section(0):
            y = self.matchup(p, g, st, x0, x1, y, night, small, moving)
            y = self.turn(p, g, st, x0, x1, y + (4 if small else 5), night, small, moving)
        y += 6
        p.hline(x0, x1, y, k["rule"])
        y += 6
        with section(1):
            y = self.last_move(p, g, st, x0, x1, y, night, small)
        y += 4
        p.hline(x0, x1, y, k["rule"])
        y += 6
        with section(2):
            y = g.count(self, p, st, x0, x1, y, night, small)
        y += 3
        p.hline(x0, x1, y, k["rule"])
        y += 6
        with section(3):
            y = self.history(p, g, st, x0, x1, y, night, 2 if small else 3)
        return y

    def board_sheet(self, g, st: dict, night: bool, wide: bool, moving: bool) -> Pix:
        """One game's board sheet, wide or a phone's: its head, its board where chess's stands, and its panel beside
        it or under it."""
        if wide:
            box = (19, 31, 184)
            px0, px1, py = 219, WIDE - 10, 31
            end = self.panel(Pix(WIDE, 400), g, st, px0, px1, py, night, False, False)
            H = max(236, end + 10)
            p = self.canvas(WIDE, H)
            self.head(p, night, g, f"game {st['game']}  ·  move {st['move']}", f"@{g.OWNER.upper()} VS. GITHUB")
            g.board(self, p, st, box, night, moving, small=False)
            p.vline(px0 - 8, py, py + box[2], self.ink(night)["rule"])
            self.panel(p, g, st, px0, px1, py, night, False, moving)
        else:
            box = (16, 29, 152)
            top = box[1] + g.height(box[2], True) + 19
            px0, px1 = 10, NARROW - 10
            end = self.panel(Pix(NARROW, 800), g, st, px0, px1, top, night, True, False)
            H = end + 10
            p = self.canvas(NARROW, H)
            self.head(p, night, g, f"move {st['move']}", None)
            g.board(self, p, st, box, night, moving, small=True)
            self.panel(p, g, st, px0, px1, top, night, True, moving)
        self._finish(p, night)
        return p

    # ------------------------------------------------------------------------------------ the entry point
    GAME_KINDS = ("chess", "checkers", "connectfour", "tictactoe", "hall-of-fame")

    def game(self, kind: str, d: dict, theme: dict, variant: str) -> str | None:
        """One file of a game on @tannergolden's profile, or of the Hall of Fame of all four, in a kit variant (wide,
        narrow, still, narrow-still, or a winner's badge), from data whose title and description the kit has filled
        in; None when the set cannot letter every word of it, and the kit draws the element in the page's own
        look."""
        night = bool(theme["dark"])
        moving = not variant.endswith("still")
        wide = not variant.startswith("narrow")
        title = str(d.get("title") or kind)
        desc = str(d.get("desc") or title)
        stamp = f"{KIT} v{KIT_VERSION} {self.key} elements {kind} {variant} {theme['name']}"
        if kind == "hall-of-fame":
            from . import hall
            h = hall.state(d)
            if variant.startswith("badge-"):
                i = int(variant.split("-")[1]) - 1
                return self._lettered(lambda: hall.badge(self, h, i, night, moving, stamp))

            def draw() -> str:
                p = hall.sheet(self, h, night, wide, moving)
                return p.svg(title, desc, still=not moving, stamp=stamp)
        else:
            from . import boards
            g = boards.GAMES[kind]
            st = g.state(d)

            def draw() -> str:
                p = self.board_sheet(g, st, night, wide, moving)
                return p.svg(title, desc, still=not moving, stamp=stamp)
        return self._lettered(lambda: self._fitted(draw, BUDGET["board"]))

    @staticmethod
    def _lettered(draw) -> str | None:
        """`draw()`'s file, or None when it set a character the set's faces lack."""
        MISSING.clear()
        try:
            svg = draw()
        finally:
            lacked = bool(MISSING)
            MISSING.clear()
        return None if lacked else svg


class _nothing:
    """A context that does nothing: a part drawn where it stands, in a still file."""

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False
