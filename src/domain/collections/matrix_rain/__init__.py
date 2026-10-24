# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Rain set: the code itself, January's design in the Matrix collection, drawn in the collection's hand.

By night every sheet is the glass of a terminal in a dark room, scanned in lines and held in the moulded case of the
monitor, its power light burning at a header's foot, and the code falls down it in streams of phosphor wherever no
word stands, each led by a white-hot glyph with its trail fading behind it, passing dim behind the titles. By day the
same code comes off a line printer onto greenbar paper, punched down its sides for the tractor's pins, and falls in the
ribbon's ink. Titles are lit on the glass, scanned, their upper and left edges burning white and their light blooming
round them; by day they are struck in the dots of a printer's head; and in a moving header the terminal's beam passes
down them on the hand's period.

An H1 opens on the room the code is watched from, a 90s terminal on its desk with the code falling down its glass and
a hacker asleep over his folded arms beside it, and on the city the code is the world of, its towers traced in phosphor
and windowed in glyphs, a mast's light blinking on the tallest. An H2 is the world seen as the code that writes it: a
corridor drawn in the code's own lines, its ribs of phosphor stepping away to a door blazing white at its far end, the
code falling down its walls, and a man in a long coat standing in it, seen from behind as he looks to the door, his
outline lit by it and his coat stirring. An H3's hero is the great tower of the city, rising the strip's full height,
stepping back as it climbs to its crown and its spire, its light blinking after dark, lesser towers at its feet and
the code passing dimmed behind it. On a phone the H1's room and city stand across the width under its words, the H2's
corridor and the H3's tower under theirs whatever they say, the code falling behind them.

The footers stand on the keyboard the code is typed on, its keys along their foot and its upper row rising where the
cells leave it room, the terminal standing after the last cell with the code on its glass, or a small one where it
has less room; a prompt waits in the corner of the notes. The links are keys of glass in the monitor's case by night
and strips torn off the printout by day; the badges carry a stream of the code along their tops; and the elements are
the code's world: cards as windows on the terminal with status lights on their lids and the terminal itself in a free
corner, wires carrying the code, bars lit and scanned on the glass or struck in rows of dots, a dial traced as a scope
draws, file types as the media the code was kept on, digits in cells of glass, the releases as cells lit on a line of
the code with the cursor at today, contributors as the floppy disks their code was kept on with their initials on the
labels, and a ring of lit cells round the seal. The games are played on a board of the printout in a frame of beige
plastic, and the Hall's winners stand on the terminal's beige case.
"""
from __future__ import annotations

from ...holidays.designs.badges import inside
from ...holidays.designs.materials import Podium, Stuff
from ...holidays.pixel import measure, tube
from ..hand import CollectionSet
from .. import rain
from . import art as A
from .palette import C, RAMP, TOKENS, X, step

FLAME, GLASS, PAPER, RIBBON = RAMP["flame"], RAMP["glass"], RAMP["paper"], RAMP["ribbon"]
CASE, RED, MANILA = RAMP["case"], RAMP["red"], RAMP["manila"]


class Rain(CollectionSet):
    key = "matrix-rain"
    name = "Rain"
    collection = "matrix"
    tagline = ("The code itself, falling down a terminal's glass in the dark and printed on greenbar by day, the world "
               "drawn in its lines.")
    about = (
        "By night every sheet is the glass of a terminal in a dark room, scanned in lines and held in the moulded "
        "case of the monitor, and the code falls down it in streams of phosphor wherever no word stands, each led "
        "by a white-hot glyph with its trail fading behind it. By day the same code comes off a line printer onto "
        "greenbar paper punched for the tractor's pins. Titles are lit on the glass, their edges burning white and "
        "their light blooming round them, and by day they are struck in the dots of a printer's head. The first "
        "header opens on the room the code is watched from, a terminal on its desk with a hacker asleep beside it, "
        "and on the city the code is the world of, its towers traced in phosphor and windowed in glyphs. A "
        "section's header is the world seen as the code that writes it, a corridor drawn in its lines with the code "
        "falling down its walls, a door blazing at its end and a man in a long coat standing in it; a strip's is the "
        "city's great tower, stepping back to its spire. On a phone each scene stands under the words. The footers "
        "stand on a keyboard, its upper row rising where there is room, with the terminal after the last cell. The "
        "links are keys of glass by night and strips of printout by day, the badges carry a stream of the code, and "
        "the elements are the code's own: windows on the terminal, wires carrying the code, scanned bars, a scope's "
        "dial, file types as cards, floppies and tape, digits in glass, the releases lit on a line of the code with "
        "the cursor at today, contributors as floppy disks and a ring of lit cells round the seal; the games are "
        "played on a board of the printout.")
    tokens = frozenset(TOKENS)

    # ---- colour and paper
    def ink(self, night):
        """The words in the hand's two inks; the titles in phosphor by night and in the ribbon's ink by day."""
        return dict(
            title=FLAME[4] if night else RIBBON[0], shadow=GLASS[0] if night else PAPER[3],
            body=self.hand.body[night], muted=self.hand.muted[night],
            rule=X["rule_night"] if night else X["rule_day"], accent=FLAME[4] if night else RIBBON[2],
            tag=FLAME[2] if night else RIBBON[2], tag_ink=GLASS[0] if night else PAPER[6],
            fill=GLASS[3] if night else PAPER[6], dim=X["dim_night"] if night else X["dim_day"],
        )

    def paper(self, p, night, uid="p"):
        p.sheet = uid
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        return A.bg_at(p, night, y)

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The glass or the paper alone: the code that falls down it is laid by the scene, once the words are
        set, so it can find the columns they leave clear."""
        self.paper(p, night)

    _foot = False     # set while a footer is drawn, whose keyboard takes the frame's foot (see `art.footing`)

    def frame(self, p, night, webs=False):
        A.frame(p, night, header=webs, foot=not self._foot)

    def tag(self, p, x, y, w, h, night):
        """A block of phosphor by night, of the ribbon's ink by day, a note's number knocked out of it."""
        p.rect(x, y, w, h, FLAME[2] if night else RIBBON[2])
        p.hline(x, x + w, y, FLAME[3] if night else RIBBON[3])

    def title_text(self, p, x, y, s, night, scale):
        """Lit on the glass by night, struck in dots by day (see `art.phosphor_title` and `art.printed_title`). The
        drawing keeps each line, for the scan that passes down it in a moving header."""
        w = A.phosphor_title(p, x, y, s, scale) if night else A.printed_title(p, x, y, s, scale)
        p.titles = getattr(p, "titles", []) + [(x, y, s, scale, w)]
        return w

    # ---- the headers' scenes
    def scene(self, design, p, rule, night, motion):
        """The code falling wherever no word stands; on H1 the terminal at the left and the city at the right; and in
        a moving header the beam passing down each line of the title on the hand's period."""
        if motion:
            for n, (x, y, s, scale, w) in enumerate(getattr(p, "titles", ())):
                rain.scan(p, x, y, s, scale, w, n, self.hand.glint, C["white"])
        g = rule - 1
        titles = [(x - 1, y - 1, x + w + 1, y + 7 * scale + 1) for x, y, s, scale, w in getattr(p, "titles", ())]
        keep = [self.mark_box(p)]
        hero = self._hero(design, p, g)
        if hero and design == "H2":
            keep.append((hero[0] - 2, 0, p.w, p.h))      # the corridor's own code falls down its walls
        veiled = titles + ([hero] if hero and design == "H3" else [])     # the code passes the tower dimmed
        A.falling(p, night, A.EDGE + 1, g, seed=3, keep=keep, titles=veiled)
        spans = []
        if hero:
            spans.append(self._draw_hero(design, p, g, hero, night, motion))
        if design == "H1":
            if p.clear_of_words(4, g - 40, 58, g + 2):
                spans.append(A.terminal(p, 7, g, night, motion))
            room = next((r for r in range(g - 14, 30, -2) if p.clear_of_words(354, g - r - 2, 411, g + 2)), 0)
            if room:
                spans.append(A.city(p, 356, g, night, motion, room=room))
        return spans

    @staticmethod
    def _hero(design, p, g):
        """The box an H2's or an H3's hero takes at the right, from the first column the words leave it two units clear
        to the frame, from under the top band down to the floor at row g; None on an H1, or where the words leave
        too little room."""
        if design == "H1":
            return None
        least = 96 if design == "H2" else 54
        x0 = next((x for x in range(300 if design == "H2" else 340, p.w - A.EDGE - least)
                   if p.clear_of_words(x - 2, 14, p.w, g + 2)), None)
        if x0 is None or g - 16 < 50:
            return None
        return (x0, 16, p.w - A.EDGE - 1, g)

    def _draw_hero(self, design, p, g, box, night, motion):
        """An H2's hero, the corridor of code with the man in the long coat standing in it (see `art.corridor`); an
        H3's, the great tower of the city (see `art.tower`). Returns the span it covers."""
        x0, y0, x1, _ = box
        if design == "H2":
            room = A.corridor(p, x0, y0, x1, g, night, motion)
            cx = room["vanish"][0]
            A.stranger(p, round(cx) - 14, g - 3, night, motion)
        else:
            A.tower(p, x0, x1, y0 + 2, g, night, motion)
        return (x0 - 1, x1 + 1)

    def section_mark(self, p, x, y, night):
        """The terminal, its glass lit with a prompt, after SECTION A-A."""
        p.sprite(x, y - 1, A.ICONS["terminal"], A.icon_pal(night, FLAME[4] if night else RIBBON[0]))

    def strip_mark(self, p, x, y, night):
        """A floppy disk beside the strip's title."""
        p.sprite(x, y - 6, A.ICONS["floppy"], A.icon_pal(night, FLAME[4] if night else RIBBON[0]))

    def rule_decor(self, p, x0, x1, y, seed, night):
        """The rule as a line of the terminal's cells where no scene stands on it: a dash of phosphor every sixth
        unit by night, of the ribbon's ink by day, as the code runs along a line."""
        A.ruled(p, x0, x1, y, night, seed)

    # ---- a phone's scenes: the H1's under its words in the rows it keeps there, the H2's and H3's in rows asked for
    PHONE_H1 = 56     # the rows a phone's H1 room and city stand in, the city's tallest tower the tallest of it
    UNDER = {"H2": 64, "H3": 64}      # the rows a phone's H2 and H3 ask for under their words for their heroes
    _h1_rows = 0      # the rows a phone's H1 is drawn with, while it is

    @property
    def phone_scene_rows(self):
        """The rows a phone's H1 asks for between its words and its rule (see `h1_narrow`)."""
        return self._h1_rows

    def h1_narrow(self, h, night):
        """A phone's H1, the room the code is watched from and the city it is the world of standing across it under
        the words, in the rows the city's towers rise through, the notes set under the words, however many there
        are."""
        self._h1_rows = self.PHONE_H1 + 4 + 10 * len(self.said(h))
        try:
            return super().h1_narrow(h, night)
        finally:
            self._h1_rows = 0

    def phone_rows(self, design, title_w):
        """The rows a phone's H2 or H3 asks for under its words, whatever its title: those its hero takes, two clear
        of the last words at least."""
        return self.UNDER.get(design, 0)

    def scene_narrow(self, design, p, y, night):
        """A phone's H1 scene, standing on the rule at `y` in the rows asked for under its words (see `h1_narrow`):
        the code falling down the glass behind the terminal on its desk with the hacker asleep beside it at the left,
        and the city of code at the right. A phone's H2 and H3 stand their heroes under their words instead (see
        `scene_under`)."""
        if design != "H1":
            return
        g = y - 1
        top = g - self.PHONE_H1 + 1
        A.falling(p, night, top, g, seed=8, keep=[self.mark_box(p)])
        A.terminal(p, 7, g, night, False)
        A.city(p, 122, g, night, False, room=self.PHONE_H1 - 6)      # its spire's light the scene's topmost unit

    def scene_under(self, design, p, y0, y1, night):
        """The scene in the rows a phone's H2 or H3 asked for under its words, standing on the rule at `y1`: the
        corridor of code with the man in the long coat on an H2, and on an H3 the great tower of the city, the code
        falling behind it."""
        g = y1 - 1
        top = g - self.UNDER[design] + 3
        if design == "H2":
            x0, x1 = 38, p.w - 38
            A.falling(p, night, top, g, seed=10, keep=[self.mark_box(p), (x0 - 2, top, x1 + 2, g + 1)])
            room = A.corridor(p, x0, top, x1, g, night, False)
            A.stranger(p, round(room["vanish"][0]) - 14, g - 2, night, False)
            return
        x0, x1 = 30, p.w - A.EDGE - 26
        A.falling(p, night, top, g, seed=9, keep=[self.mark_box(p)], titles=[(x0, top, x1, g)])
        A.tower(p, x0, x1, top + 2, g, night, False)

    def _finish(self, p, night):
        """The last pass, which a drawing made lighter keeps too: the design's last light at full weight only (see
        `finish`), then the file written as lightly as it can be, the same drawing unit for unit, the month's mark
        left as it is drawn (see `Pix.compact`)."""
        if not p.lite:
            self.finish(p, night)
        p.compact(keep=("mark",))

    # ---- the footers and links
    def footer_mark(self, p, x, y, night):
        """The prompt and its cursor lit in the corner of the closing notes, as the terminal waits for the next line."""
        A.prompt(p, x + 3, y - 2, night)

    def _footed(self, p, night, last=False):
        """A footer once its cells are laid: the keyboard along its foot, its upper row rising where the cells leave it
        room, and the terminal behind it where they leave it free (see `art.footing`): on a title block only after its
        `last` cell, the way back up."""
        after = max((b[2] for b in p.words), default=0) + 4 if last else 0
        A.footing(p, night, after=after)
        return p

    def _tread(self, draw, ft, night, last=False):
        """A footer drawn with its frame's foot left to its footing, then footed (see `_footed`)."""
        self._foot = True
        try:
            p = draw(ft, night)
        finally:
            self._foot = False
        return self._footed(p, night, last=last)

    def f1(self, ft, night):
        return self._tread(super().f1, ft, night, last=True)

    def f2(self, ft, night):
        return self._tread(super().f2, ft, night)

    def f1_narrow(self, ft, night):
        return self._tread(super().f1_narrow, ft, night, last=True)

    def f2_narrow(self, ft, night):
        return self._tread(super().f2_narrow, ft, night)

    def heart(self, p, x, y):
        A.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        """A line of the terminal's cells, lit and dark by turns (see `art.scale_bar`)."""
        A.scale_bar(p, x0, y0, w, h, period)

    def link_colours(self, night):
        """A key of the terminal by night, its glass dark in its case and its letters lit in phosphor; by day a
        strip torn off the printout, its letters struck in the ribbon's ink."""
        if night:
            return GLASS[3], CASE[0], FLAME[5], GLASS[0]
        return C["paper"], RIBBON[2], RIBBON[0], PAPER[3]

    def link_top(self, p, x0, x1, y, seed, night):
        """By night the button as a slot of glass let into the monitor's case: the case's lip lit over it, the glass
        scanned in a dark line along its top, and the power light burning at its right; by day a strip torn off the
        printout, perforated along its top where it tore and punched for the tractor at its ends."""
        w = p.w
        if night:
            p.hline(1, w - 1, y - 1, CASE[4])
            p.hline(2, w - 2, y + 1, GLASS[0])
            p.px(w - 4, y - 1, FLAME[4])
            p.px(w - 5, y - 1, FLAME[2])
            return
        for x in range(2, w - 2, 2):
            p.px(x, y, PAPER[6])
        for hx in (2, w - 3):
            p.px(hx, y + 4, PAPER[2])
            p.px(hx, y + 6, PAPER[2])

    def link_icon(self, index, night, ink):
        return A.ICONS[A.LINK_SPRITES[index % len(A.LINK_SPRITES)]], A.icon_pal(night, ink)

    # ---- the elements
    def card_bevel(self, night):
        return (GLASS[5], GLASS[0]) if night else (C["white"], PAPER[2])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A card as a window on the terminal, its icon's cell glass and its status lights on its lid (see
        `art.card_screen`)."""
        A.card_screen(p, night, x, y, w, h, lid)

    def wire_ink(self, night):
        return FLAME[1] if night else RIBBON[3]

    def wire_lights(self, p, cells, night, seed):
        """The code running along the wire (see `art.wire_code`)."""
        A.wire_code(p, cells, night)

    def dashes(self, night):
        return [FLAME[3], FLAME[1]] if night else [RIBBON[1], RIBBON[4]]

    def ornament(self, kind, p, x, y, night):
        """The terminal in a free corner of the schematic, the code falling down its glass and the prompt waiting
        on it, its glass lighting the sheet round it after dark (see `art.screen`)."""
        if kind == "schematic":
            if p is not None:
                p.sprite(x, y, A.MONITOR, A._tones(night))
                A.screen(p, x + A.GLASS_AT[0], y + A.GLASS_AT[1], *A.GLASS_SIZE, night, False, seed=5)
            return (len(A.MONITOR[0]), len(A.MONITOR))
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as a bar lit on the glass, scanned, its head white-hot; by day struck in rows of dots
        (see `art.code_bar`)."""
        A.code_bar(p, bx, base, bw, v, night)

    def peak_mark(self, p, x, y, night):
        A.cursor(p, x, y + 1, night)

    def dial_ring(self, p, arc, night):
        """The dial's half ring traced in phosphor on the glass by night, as a scope draws its sweep; struck in the
        ribbon's ink by day."""
        R = FLAME if night else RIBBON

        def colour(s, o, lam, x, y):
            if night:
                return R[max(1, min(5, round(1 + 4 * lam)))]
            return R[max(0, min(3, round(3 - 3 * lam)))]
        tube(p, arc, 1.5, colour, outline=GLASS[0] if night else RIBBON[0])

    def dial_tick(self, p, x, y, night):
        p.rect(x - 1, y, 2, 1, FLAME[5] if night else RIBBON[0])

    def dial_hub(self, p, cx, cy, night):
        """The hub as a cell burning white-hot by night, the hand's pivot; by day a dot of the ribbon's ink."""
        p.rect(cx - 1, cy - 1, 3, 3, FLAME[4] if night else RIBBON[1])
        p.px(cx, cy, FLAME[6] if night else RIBBON[0])

    def material(self, i, xx, yy, y0, y1, lift, night):
        """Each file type as the media the code was kept on, by turns (see `art.media`), lit along its top and in
        shade along its foot."""
        return step(A.media(i, xx, yy, y0, y1, night), lift)

    def counter_cell(self, q, ox, oy, night):
        """A counter's digit in a cell of glass, or by day printed (see `art.glass_cell`)."""
        A.glass_cell(q, ox, oy, night)

    def counter_ink(self, night, dim):
        """The digit lit in phosphor by night, struck in the ribbon's ink by day, a leading nought dimmer."""
        if night:
            return FLAME[2] if dim else FLAME[5]
        return RIBBON[3] if dim else RIBBON[0]

    def timeline_line(self, p, x0, x1, y, night):
        """The releases' line as a line of the code (see `art.code_line`)."""
        A.code_line(p, x0, x1, y, night)

    def release(self, p, x, gy, kind, night, i=0):
        """A release as a cell lit on the line (see `art.lit_cell`)."""
        A.lit_cell(p, x, gy, kind, night)

    def today_mark(self, p, x, y, night):
        """The cursor at today's end of the line, waiting for the next release."""
        A.cursor(p, x + 1, y - 4, night, w=2, h=5)

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor as the floppy disk their code was kept on, their initials written on its label in the
        ribbon's ink; a bot's label carries one of the code's glyphs (see `art.floppy`)."""
        lx, ly, lw, lh = A.floppy(p, cx, cy, i, night)
        ini = str(person.get("initials") or "")[:2]
        if ini:
            p.text(lx + (lw - measure(ini, "35")) // 2, ly + 1, ini, RIBBON[0], "35")
        else:
            rain.write(p, lx + (lw - rain.W) // 2, ly, "ki", RIBBON[0])

    def commit_bar(self, p, x, y, w, fill, night):
        """A contributor's share as a terminal's progress bar: lit cells two units wide in a ruled box."""
        p.box(x, y, w + 2, 4, CASE[3] if night else RIBBON[2])
        for xx in range(fill):
            if xx % 3 != 2:
                c = (FLAME[4] if night else RIBBON[1])
                p.px(x + 1 + xx, y + 1, c)
                p.px(x + 1 + xx, y + 2, FLAME[2] if night else RIBBON[3])

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """A ring of the code's cells round the seal (see `art.lit_ring`)."""
        A.lit_ring(p, cx, cy, r0, r1, night)

    def seal_mark(self, p, x, y, night):
        p.sprite(x + 3, y, A.ICONS["floppy"], A.icon_pal(night, FLAME[4] if night else RIBBON[0]))

    def placard_board(self, p, night):
        """The placard as the terminal's glass in its case by night, a strip of the printout by day."""
        A.paper(p, night, uid="pl")
        A.frame(p, night)

    def placard_mark(self, p, x, y, night):
        A.prompt(p, x + 1, y - 3, night)

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """The lit edge of the glass along a badge's top two rows, kept inside its shape: a stream of the code running
        along it in phosphor, heads white-hot and trails fading, over a dark scan line, the letters under it."""
        h = s["h"]
        trail = (FLAME[6], FLAME[4], FLAME[3], FLAME[2], FLAME[1], FLAME[1], FLAME[0])
        for x in range(w):
            if inside(x, 0, w, h, s["corner"]):
                p.px(x, 0, trail[(x + seed) % len(trail)])
            if inside(x, 1, w, h, s["corner"]):
                p.px(x, 1, GLASS[0])

    def badge_label(self):
        return (CASE[2], FLAME[5])

    def badge_gold(self):
        """A live badge's label lit in phosphor, the code's own gold, its letters dark on it."""
        return (FLAME[3], GLASS[0])

    def badge_states(self):
        """Green in the phosphor, yellow in a punched card's manila, red in the ribbon's red half, and slate in the
        terminal's case."""
        return {"green": (FLAME[1], C["white"]), "yellow": (MANILA[4], GLASS[0]),
                "red": (RED[3], C["white"]), "slate": (CASE[4], C["white"])}

    def badge_swatches(self):
        return {"phosphor": (FLAME[3], GLASS[0], None), "ribbon": (RIBBON[2], C["white"], None),
                "red": (RED[3], C["white"], None), "manila": (MANILA[4], GLASS[0], None),
                "denim": (RAMP["denim"][3], C["white"], None), "wood": (RAMP["wood"][2], C["white"], None),
                "beige": (RAMP["beige"][4], GLASS[0], None), "case": (CASE[2], FLAME[5], "scan"),
                "paper": (C["paper"], RIBBON[0], "printed"), "glass": (GLASS[3], FLAME[4], "scan"),
                "desk": (RAMP["desk"][3], C["white"], None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        """A swatch of glass scanned in lines, every other row a step darker, above and below its letters."""
        if pattern == "scan" and y % 2 == 1 and y not in text_rows:
            return step(c, -1)
        return c

    def badge_outline(self, pattern):
        return RIBBON[2] if pattern == "printed" else None

    def badge_shine(self, c, y, h):
        try:
            return step(c, 1) if y == 2 else step(c, -1) if y == h - 1 else c
        except KeyError:
            return c

    def plate_edge(self, block):
        try:
            return step(block, -1)
        except KeyError:
            return block

    def plate_colours(self, mode):
        """A plate's colours: by day the printout, its label on the white band and its value struck in the
        ribbon; by night the glass, its value lit in phosphor; live, the label lit in phosphor."""
        if mode == "day":
            return dict(paper=C["paper"], dot=C["bar"], frame=RIBBON[2], block=RIBBON[1], ink=C["ink"],
                        letters=PAPER[6])
        if mode == "night":
            return dict(paper=GLASS[3], dot=GLASS[5], frame=FLAME[1], block=FLAME[3], ink=C["body_night"],
                        letters=GLASS[0])
        return dict(paper=FLAME[3], dot=FLAME[3], frame=GLASS[0], edge=FLAME[1], ink=GLASS[0])

    # ---- the games
    def game_squares(self, night):
        """A board of the printout, its light squares the paper's white band, mottled as paper is, and its dark the
        ribbon's green with the sheen of ink fresh on it; a tone down by night, as every board of the year is dimmer
        after dark."""
        return (Stuff(PAPER, 4 if night else 5, "vellum"), Stuff(RIBBON, 4 if night else 5, "satin"))

    def game_frame(self, night):
        """A frame of the terminal's beige plastic, plain."""
        return Stuff(RAMP["beige"], 3), "plain"

    def game_podium(self, night):
        """A podium of the terminal's beige case, brushed and screwed at its corners, its blocks plain."""
        return Podium(Stuff(RAMP["beige"], 4, "metal"))


SET = Rain()
