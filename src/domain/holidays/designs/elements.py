# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The six elements every holiday set draws, laid out from the kit's own element data.

The same data a print draws from, with the same rules: a schematic lays its
boxes out along its wires and routes each wire round them; instruments show
the weeks' commits, the days since the last release, the bytes by file type
and up to three counts; milestones set every release on a calendar with its
quiet stretches cut out; a roster, a certificate and a placard carry what the
settings and the measurement say. Nothing here knows the sample project.

A set decorates: its sheet frame and tag, the cards and the lights on the
wires, the histogram's bars, the dial's ring, the materials' wrappers, the
counters' cells, the releases on the time line, the contributors' avatars,
the seal's rosette and the placard's board. Every wide sheet is 415 units (830
px) wide; a phone's sheet is 180 (360 px); a roster, a certificate or a
placard on half a page is 202 (404 px), the kit's half width.
"""
from __future__ import annotations

import datetime as dt
import math

from ...elements.layout import Box, layers, route, snake, timeline
from ..pixel import GLYPHS, Pix, clip, fold, measure, wrap
from .banners import NARROW, WIDE

HALF = 202
CHECK = ["......#", ".....##", "#...##.", "##.##..", ".###...", "..#...."]
CROSS = ["#.....#", ".#...#.", "..#.#..", "...#...", "..#.#..", ".#...#.", "#.....#"]
MONTHS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")

# How far inside the canvas's edge a schematic's wire keeps: the set's frame, 4 px, and 6 more, so a label
# set upright beside a wire by the frame takes its other side.
ROOM = 10


def _date(s) -> dt.date:
    return s if isinstance(s, dt.date) else dt.date.fromisoformat(str(s))


def _when(d: dt.date, year: bool = False) -> str:
    return f"{d.day} {MONTHS[d.month - 1]}" + (f" {d.year}" if year else "")


def balanced(s: str, room: int, font: str = "35") -> list[str]:
    """`s` on one line if it fits, else on two lines as even as its words allow, neither starting or
    ending on a lone separator; each line clipped to `room` if even that is too wide."""
    s = fold(" ".join(str(s).split()), font)
    if measure(s, font) <= room:
        return [s] if s else []
    words = s.split()
    best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        if words[i - 1] in "·-|/" or words[i] in "·-|/":
            continue
        worst = max(measure(a, font), measure(b, font))
        if best is None or worst < best[0]:
            best = (worst, [a, b])
    lines = best[1] if best else wrap(s, room, font)[:2]
    return [clip(line, room, font) for line in lines]


def _phone_order(keys, edges):
    """Boxes one to a row on a phone: by layer, and within a layer the box whose wire goes on to the next
    layer last, so that wire meets its box directly under it rather than taking the channel."""
    lay = layers(keys, edges)
    onward = {a for a, b in edges if lay.get(b) == lay.get(a, -2) + 1}
    return sorted(keys, key=lambda k: (lay[k], k in onward, keys.index(k)))


class Elements:
    """The element layouts. Every drawing hook a set overrides is listed first, with its default."""

    # ------------------------------------------------------------------------------------------ hooks
    def node_deco(self, p: Pix, night, x, y, w, h, seed, lid):
        """A schematic card's own touch: a band down its icon cell's edge, something on its lid."""

    def wire_lights(self, p: Pix, cells, night, seed):
        """What hangs on a wire: `cells` are its (x, y, 'h' or 'v') pixels, start to end."""

    def dashes(self, night) -> list:
        """The colours a group's dashed border cycles through."""
        k = self.ink(night)
        return [k["accent"], k["muted"]]

    def ornament(self, kind: str, p: Pix, x, y, night) -> tuple:
        """A sheet's ornament in a free corner, `kind` the element. Returns the (w, h) it takes; (0, 0)
        for none. Called first with p=None to learn its size."""
        return (0, 0)

    def hist_bar(self, p: Pix, bx, base, bw, v, night):
        """One week's bar, `v` pixels tall, standing on `base`."""
        k = self.ink(night)
        p.rect(bx, base - v, bw, v, k["accent"])

    def peak_mark(self, p: Pix, x, y, night):
        """The mark beside the busiest week's count."""

    def dial_ring(self, p: Pix, arc, night):
        """The dial's half ring, along `arc`'s points, left to right over the top."""
        k = self.ink(night)
        for (x, y) in arc:
            p.px(round(x), round(y), k["rule"])

    def dial_tick(self, p: Pix, x, y, night):
        """A tick on the dial's ring, (x, y) its centre."""
        p.px(x, y, self.ink(night)["body"])

    def dial_hub(self, p: Pix, cx, cy, night):
        """The hub the hand turns on."""
        p.rect(cx - 1, cy - 1, 3, 3, self.ink(night)["body"])

    def material(self, i: int, xx, yy, y0, y1, lift, night) -> str:
        """The colour of the `i`-th file type's wrapper at (xx, yy), in a bar from y0 to y1, `lift` +1 on
        its lit top row and -1, -2 on its shaded foot."""
        return self.ink(night)["accent"]

    def counter_cell(self, q: Pix, ox, oy, night):
        """The 11 by 15 cell a counter's digit is cut into, drawn at (ox, oy)."""
        q.box(ox, oy, 11, 15, self.ink(night)["rule"])

    def counter_ink(self, night, dim: bool) -> str:
        """A counter digit's colour; `dim` for a leading nought."""
        k = self.ink(night)
        return k["muted"] if dim else k["body"]

    def timeline_line(self, p: Pix, x0, x1, y, night):
        """The line the releases hang from, up to today."""
        p.hline(x0, x1, y, self.ink(night)["body"])

    def release(self, p: Pix, x, gy, kind, night, i=0):
        """A release on the line at x: kind 'big', 'major', 'minor', 'next' or 'made'."""
        k = self.ink(night)
        p.rect(x - 1, gy + 1, 3, 3, k["accent"] if kind != "next" else k["muted"])

    def today_mark(self, p: Pix, x, y, night):
        """The mark at today's end of the line."""
        p.px(x, y - 1, self.ink(night)["accent"])

    def avatar(self, p: Pix, cx, cy, i, person, night):
        """A contributor's avatar centred on (cx, cy): initials, or a bot's icon."""
        k = self.ink(night)
        p.rect(cx - 7, cy - 7, 15, 15, k["accent"])
        p.text(cx - 3, cy - 2, person.get("initials", "?")[:2], k["tag_ink"], "35")

    def commit_bar(self, p: Pix, x, y, w, fill, night):
        """A contributor's share of the most commits: a bar `w` wide, `fill` of it full."""
        k = self.ink(night)
        p.box(x, y, w + 2, 4, k["body"])
        p.hline(x + 1, x + 1 + fill, y + 1, k["accent"])
        p.hline(x + 1, x + 1 + fill, y + 2, k["accent"])

    def rosette(self, p: Pix, cx, cy, r0, r1, n, night):
        """The ring of points round the certificate's seal."""

    def seal_mark(self, p: Pix, x, y, night):
        """The small sprite at the seal's foot."""

    def placard_board(self, p: Pix, night):
        """The placard's frame and ground, over the whole canvas."""
        self.paper(p, night, uid="pl")
        self.frame(p, night)

    def placard_mark(self, p: Pix, x, y, night):
        """An ornament beside the placard's title."""

    # ------------------------------------------------------------------------------------ shared pieces
    def frame_element(self, p: Pix, night, tag, title, note=None, seed=1):
        """A sheet's frame: the paper, the set's border, a tag naming the element, the subject beside it,
        a note at the right, and a rule under them."""
        k = self.ink(night)
        self.paper(p, night, uid=f"e{seed}")
        if night:
            self.stars(p, 6, 22, p.w - 6, p.h - 8, p.w // 7, seed=seed, twinkling=False, faint=True)
        self.frame(p, night)
        tw = measure(tag, "35")
        self.tag(p, 9, 8, tw + 8, 9, night)
        p.text(13, 10, tag, k["tag_ink"], "35")
        right = p.w - 10
        if note:
            note = clip(note, max(40, p.w // 2 - 20), "35")
            nw = measure(note, "35")
            p.text(p.w - 10 - nw, 10, note, k["muted"], "35")
            right -= nw + 8
        if title:
            x = 9 + tw + 14
            title = str(title)
            if measure(title, "57") > right - x and "/" in title:
                title = title.rsplit("/", 1)[1]
            p.text(x, 9, clip(title, right - x), k["body"])
        p.hline(4, p.w - 4, 20, k["rule"])
        self.rule_decor(p, 5, p.w - 5, 20, seed, night)

    def _free(self, p: Pix, x0, y0, x1, y1, taken) -> bool:
        """Whether the box (x0, y0, x1, y1) touches no text and none of `taken`."""
        return p.clear_of_words(x0, y0, x1, y1) and all(x1 <= a or x0 >= c or y1 <= b or y0 >= d for a, b, c, d in taken)

    def place_ornament(self, kind, p: Pix, night, spots, taken):
        """Set the ornament in the first of `spots` (its top-left) where it is free."""
        w, h = self.ornament(kind, None, 0, 0, night)
        if not w:
            return
        for (x, y) in spots:
            if 4 < x and x + w < p.w - 4 and 21 < y and y + h < p.h - 4 and self._free(p, x, y, x + w, y + h, taken):
                self.ornament(kind, p, x, y, night)
                return

    def notes_block(self, p: Pix, notes, x0, x1, y, night, col_w=190):
        """A schematic's numbered notes, in columns as wide as `col_w`, a row every 10 units. Returns the
        height they take."""
        if not notes:
            return 0
        cols = max(1, (x1 - x0) // col_w)
        rows = math.ceil(len(notes) / cols)
        for i, (n, text) in enumerate(notes):
            c, r = divmod(i, rows)
            self.numbered(p, x0 + c * col_w, y + r * 10, n, str(text), night, room=col_w - 8)
        return rows * 10

    # ------------------------------------------------------------------------------------- schematic
    def node(self, p: Pix, night, x, y, w, h, spec, seed=0, lid=True):
        """A step of the flow as a card: its icon in its own cell, the set's touch on its edge and lid,
        its title, its path (wrapped at a slash when it is long) and its note's number."""
        k = self.ink(night)
        p.rect(x, y, w, h, k["fill"])
        light, dark = self.card_bevel(night)
        p.bevel(x + 1, y + 1, w - 2, h - 2, light, dark)
        p.box(x, y, w, h, k["rule"])
        icon = spec.get("icon") or "grid"
        p.sprite(x + 2, y + (h - 7) // 2, GLYPHS[7].get(icon, GLYPHS[7]["grid"]), {"#": k["body"]})
        self.node_deco(p, night, x, y, w, h, seed, lid)
        tx = x + 16
        room = w - 16 - (12 if spec.get("note") else 3)
        title = fold(str(spec.get("title", "")), "57")
        tfont = "57" if measure(title, "57") <= room else "35"
        title = clip(title, room, tfont)
        path = fold(str(spec.get("path", "")), "35")
        lines = [path] if measure(path, "35") <= room else wrap(path.replace("/", "/ "), room, "35")[:2]
        lines = [clip(line.replace("/ ", "/"), room, "35") for line in lines if line]
        ty = y + (6 if len(lines) <= 1 else 4)
        p.text(tx, ty + (1 if tfont == "35" else 0), title, k["body"], tfont)
        for i, line in enumerate(lines):
            p.text(tx, ty + 10 + i * 7, line, k["muted"], "35")
        if spec.get("note"):
            self.tag(p, x + w - 10, y + 3, 7, 7, night)
            p.text(x + w - 8, y + 4, str(spec["note"])[:1], k["tag_ink"], "35")

    def card_bevel(self, night) -> tuple:
        k = self.ink(night)
        return (k["fill"], k["dim"])

    def wire(self, p: Pix, night, pts, label=None, seed=0, taken=()):
        """A wire between steps, the set's lights on it, an arrow at its end, and its label on a backing,
        set where it is clear of the cards and of every word already set."""
        k = self.ink(night)
        col = self.wire_ink(night)
        pts = [(int(round(x)), int(round(y))) for x, y in pts]
        cells = []
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if x0 == x1:
                rng = range(y0, y1 + 1) if y1 >= y0 else range(y0, y1 - 1, -1)
                cells += [(x0, yy, "v") for yy in rng]
            else:
                rng = range(x0, x1 + 1) if x1 >= x0 else range(x0, x1 - 1, -1)
                cells += [(xx, y0, "h") for xx in rng]
        for (x, y, _) in cells:
            p.px(x, y, col)
        self.wire_lights(p, cells, night, seed)
        (xa, ya), (xb, yb) = pts[-2], pts[-1]
        if ya == yb:
            dd = 1 if xb > xa else -1
            for i in range(3):
                p.vline(xb - dd * (i + 1), yb - i, yb + i + 1, col)
        else:
            dd = 1 if yb > ya else -1
            for i in range(3):
                p.hline(xb - i, xb + i + 1, yb - dd * (i + 1), col)
        if not label:
            return
        label = clip(fold(str(label), "35"), 120, "35")
        lw = measure(label, "35")
        segs = sorted(zip(pts, pts[1:]), key=lambda s: -(abs(s[1][0] - s[0][0]) + abs(s[1][1] - s[0][1])))
        for (x0, y0), (x1, y1) in segs:
            if y0 == y1 and abs(x1 - x0) >= lw + 8:
                mx = (x0 + x1) // 2 - lw // 2
                for lx, ly in ((mx, y0 - 7), (mx, y0 + 3)):
                    if self._free(p, lx - 2, ly - 1, lx + lw + 2, ly + 6, taken):
                        p.rect(lx - 2, ly - 1, lw + 4, 7, self.bg_at(p, night, ly))
                        p.text(lx, ly, label, k["muted"], "35")
                        return
            if x0 == x1 and abs(y1 - y0) >= 12:
                my = (y0 + y1) // 2 - 3
                for lx in (x0 + 4, x0 - 4 - lw):
                    if self._free(p, lx - 2, my - 1, lx + lw + 2, my + 6, taken) and 4 < lx and lx + lw < p.w - 4:
                        p.rect(lx - 2, my - 1, lw + 4, 7, self.bg_at(p, night, my))
                        p.text(lx, my, label, k["muted"], "35")
                        return
                if abs(y1 - y0) >= lw + 6:
                    vy = (y0 + y1) // 2 - lw // 2
                    for bx in (x0 + 2, x0 - 9):
                        if 4 < bx and bx + 7 < p.w - 4 and self._free(p, bx, vy - 2, bx + 7, vy + lw + 2, taken):
                            p.rect(bx, vy - 2, 7, lw + 4, self.bg_at(p, night, vy))
                            p.vtext(bx + 1, vy, label, k["muted"])
                            return

    def wire_ink(self, night) -> str:
        return self.ink(night)["body"]

    def _group_boxes(self, d, by):
        out = []
        for gk, label in (d.get("groups") or {}).items():
            members = [by[k] for k in by if d["boxes"][k].get("in") == gk]
            if members:
                out.append((str(label), members))
        return out

    def _routes(self, d: dict, by: dict, boxes: list) -> list:
        """Each wire's route, in the order the data gives them: wires that would share a channel take lanes
        in it, 4 px apart, centred on the channel."""
        lanes: dict = {}
        found = []
        for i, (a, b, *rest) in enumerate(d["wires"]):
            if a not in by or b not in by:
                continue
            pts = route(by[a], by[b], 34, boxes)
            key = None if len(pts) < 4 else ("x", round(pts[1][0])) if pts[1][0] == pts[2][0] else ("y", round(pts[1][1]))
            lanes.setdefault(key, []).append(i)
            found.append((i, a, b, rest[0] if rest else None))
        out = []
        for i, a, b, label in found:
            key = next(kk for kk, v in lanes.items() if i in v)
            group = lanes[key]
            lane = (group.index(i) - (len(group) - 1) / 2) * 4 if key is not None and len(group) > 1 else 0
            out.append((i, route(by[a], by[b], 34, boxes, lane), label))
        return out

    def schematic(self, d: dict, night: bool) -> Pix:
        """Boxes and the wires between them, layered along the wires and snaked across the sheet, three
        layers a row; a group's boxes inside a dashed line with its label; the notes at the foot."""
        keys = list(d["boxes"])
        edges = [(a, b) for a, b, *_ in d["wires"]]
        boxes = [Box(k) for k in keys]
        by = {b.key: b for b in boxes}
        top = 40
        grouped_top = any(d["boxes"][k].get("in") for k in keys)
        # A wire that goes round a box in the last column runs down a channel beyond it. The placement gives
        # up width until that channel, and a label set upright beside it, stays inside the set's frame.
        span = 383
        while True:
            placed = snake(boxes, edges, left=16, top=top + (4 if grouped_top else 0), width=span, per_row=3,
                           box_w=106, box_h=28, gap_x=34, gap_y=30, stack_gap=14)
            for b in boxes:
                b.x, b.y, b.w, b.h = round(b.x), round(b.y), round(b.w), round(b.h)
            over = max((x for _, pts, _ in self._routes(d, by, boxes) for x, _ in pts), default=0) - (WIDE - ROOM)
            if over <= 0 or span <= WIDE // 2:
                break
            span -= math.ceil(over)
        notes = [(n, t) for n, t in d.get("notes", ())]
        ow, oh = self.ornament("schematic", None, 0, 0, night)
        n_rows = math.ceil(len(notes) / 2) if notes else 0
        H = top + (4 if grouped_top else 0) + round(placed) + 16 + n_rows * 10 + 8
        p = self.canvas(WIDE, H)
        k = self.ink(night)
        self.frame_element(p, night, "SCHEMATIC", d.get("subject", ""), d.get("caption") or "NOT TO SCALE", seed=21)
        taken = [(b.x - 2, b.y - 2, b.x + b.w + 2, b.y + b.h + 2) for b in boxes]
        for label, members in self._group_boxes(d, by):
            x0, y0 = min(b.x for b in members) - 10, min(b.y for b in members) - 11
            x1, y1 = max(b.x + b.w for b in members) + 10, max(b.y + b.h for b in members) + 9
            others = [b for b in boxes if b not in members and b.y < y1 and b.y + b.h > y0]
            lo = max([6] + [b.x + b.w + 4 for b in others if b.x + b.w <= x0])
            hi = min([p.w - 6] + [b.x - 4 for b in others if b.x >= x1])
            label = fold(label, "35")
            want = measure(label, "35") + 12
            if x1 - x0 < want:
                grow = want - (x1 - x0)
                x0, x1 = x0 - grow // 2, x1 + grow - grow // 2
                if x0 < lo:
                    x0, x1 = lo, x1 + lo - x0
                if x1 > hi:
                    x0, x1 = max(lo, x0 - (x1 - hi)), hi
            x0, x1 = max(x0, 6), min(x1, p.w - 6)
            p.dashed(x0, y0, x1, y1, self.dashes(night), 3)
            label = clip(label, x1 - x0 - 8, "35")
            lw = measure(label, "35")
            lx = (x0 + x1) // 2 - lw // 2
            p.rect(lx - 2, y0 - 1, lw + 4, 3, self.bg_at(p, night, y0))
            p.text(lx, y0 + 3, label, k["muted"], "35")
        for i, pts, label in self._routes(d, by, boxes):
            self.wire(p, night, pts, label, seed=i, taken=taken)
        for i, b in enumerate(boxes):
            self.node(p, night, b.x, b.y, b.w, b.h, d["boxes"][b.key], seed=i, lid=i % 3 != 2)
        ny = H - 8 - n_rows * 10
        self.notes_block(p, notes, 12, WIDE - 12, ny, night)
        if ow:
            spots = [(x, y) for y in range(ny - oh - 4, 24, -6) for x in (20, WIDE - ow - 20, WIDE // 2 - ow // 2)]
            self.place_ornament("schematic", p, night, spots, taken)
        self._finish(p, night)
        return p

    def schematic_narrow(self, d: dict, night: bool) -> Pix:
        """The schematic on a phone: the boxes stacked one to a row in the order the data flows, a wire
        that skips a row carried down the right-hand side, the notes at the foot."""
        keys = list(d["boxes"])
        edges = [(a, b) for a, b, *_ in d["wires"]]
        order = _phone_order(keys, edges)
        row = {key: i for i, key in enumerate(order)}
        step_y, x0, top = 46, 12, 34
        # A wire that skips a row runs down a channel of its own at the right, each 7 px past the last. The
        # boxes give up width until every channel, and a label set upright beside it, stays inside the
        # set's frame; past the narrowest a box can read at, the channels close up instead.
        skips = sum(1 for a, b, *_ in d["wires"] if a in row and b in row and row[b] != row[a] + 1)
        room, step = NARROW - ROOM - x0 - 10, 7
        w = min(138, room - step * max(skips - 1, 0))
        if w < 100:
            w, step = 100, (room - 100) / max(skips - 1, 1)
        groups = d.get("groups") or {}
        gaps = {}
        prev = None
        for key in order:
            g = d["boxes"][key].get("in")
            gaps[key] = 10 if g and g != prev else 0
            prev = g
        ys, y = {}, top
        for key in order:
            y += gaps[key]
            ys[key] = y + 8
            y += step_y
        notes = [(n, t) for n, t in d.get("notes", ())]
        note_lines = [wrap(str(t), NARROW - 32, "35") for _, t in notes]
        H = y + 6 + sum(7 * len(ls) + 3 for ls in note_lines) + 6
        p = self.canvas(NARROW, H)
        k = self.ink(night)
        self.frame_element(p, night, "SCHEMATIC", d.get("subject", ""), seed=31)
        taken = [(x0 - 2, ys[key] - 2, x0 + w + 2, ys[key] + 30) for key in order]
        for gk, label in groups.items():
            members = [key for key in order if d["boxes"][key].get("in") == gk]
            if not members:
                continue
            gy0, gy1 = min(ys[m] for m in members) - 12, max(ys[m] for m in members) + 36
            p.dashed(6, gy0, NARROW - 6, gy1, self.dashes(night), 3)
        channel = 0
        cx = x0 + 30
        for i, (a, b, *rest) in enumerate(d["wires"]):
            if a not in row or b not in row:
                continue
            label = rest[0] if rest else None
            if row[b] == row[a] + 1:
                self.wire(p, night, [(cx, ys[a] + 28), (cx, ys[b] - 1)], label, seed=i, taken=taken)
            else:
                ch = round(x0 + w + 10 + step * channel)
                channel += 1
                ya, yb = ys[a] + 20, ys[b] + 14
                self.wire(p, night, [(x0 + w, ya), (ch, ya), (ch, yb), (x0 + w + 1, yb)], label, seed=i, taken=taken)
        for i, key in enumerate(order):
            self.node(p, night, x0, ys[key], w, 28, d["boxes"][key], seed=i, lid=i % 3 != 2)
        for gk, label in groups.items():
            members = [key for key in order if d["boxes"][key].get("in") == gk]
            if not members:
                continue
            gy0 = min(ys[m] for m in members) - 12
            label = clip(fold(str(label), "35"), NARROW - 24, "35")
            lw = measure(label, "35")
            p.rect(NARROW // 2 - lw // 2 - 2, gy0 - 1, lw + 4, 8, self.bg_at(p, night, gy0))
            p.text(NARROW // 2 - lw // 2, gy0 + 1, label, k["muted"], "35")
        y = H - 6 - sum(7 * len(ls) + 3 for ls in note_lines)
        for (n, _), lines in zip(notes, note_lines):
            self.numbered(p, 10, y, n, lines[0] if lines else "", night, room=NARROW - 24)
            for extra in lines[1:]:
                y += 7
                p.text(20, y + 1, extra, k["muted"], "35")
            y += 10
        self._finish(p, night)
        return p

    # ----------------------------------------------------------------------------------- instruments
    def histogram(self, p: Pix, hist, x0, x1, base, night, top=45, labels=True):
        """Commits per week as bars on dotted guides, each week's count over its bar, the busiest marked."""
        k = self.ink(night)
        bars = [(str(lbl), int(v)) for lbl, v in hist["bars"]] or [("", 0)]
        peak = max(max(v for _, v in bars), 1)
        span = max(10, math.ceil(peak / 3 / 5) * 5 * 3)
        ticks = [span // 3, 2 * span // 3, span]
        for t in ticks:
            yy = base - round(t * top / span)
            for xx in range(x0 + 12, x1, 3):
                p.px(xx, yy, k["dim"])
            p.text(x0, yy - 2, str(t), k["muted"], "35")
        p.text(x0 + 4, base - 2, "0", k["muted"], "35")
        p.hline(x0 + 12, x1, base, k["rule"])
        n = len(bars)
        gap = (x1 - x0 - 16) // n
        bw = max(4, min(14, gap - 6))
        widest = max(measure(fold(week, "35"), "35") for week, _ in bars)
        every = next(s for s in range(1, n + 2) if widest + 4 <= s * gap or s > n)
        for i, (week, v) in enumerate(bars):
            bx = x0 + 16 + i * gap + (gap - bw) // 2
            h = round(v * top / span)
            if h:
                self.hist_bar(p, bx, base, bw, h, night)
            vw = measure(str(v), "35")
            p.text(bx + bw // 2 - vw // 2, base - h - 7, str(v), k["body"], "35")
            if v == peak and v:
                self.peak_mark(p, bx + bw // 2 + vw // 2 + 3, base - h - 9, night)
            if labels and (n - 1 - i) % every == 0:
                ww = measure(week, "35")
                p.text(min(max(x0 + 12, bx + bw // 2 - ww // 2), x1 - ww), base + 3, week, k["muted"], "35")

    def dial(self, p: Pix, dial, cx, cy, r, night):
        """Days since the last release on a half dial: the set's ring with a tick every major step and
        its figure inside, the hand at the count, the count over the hub and what it was under it."""
        k = self.ink(night)
        span = max(1, int(dial.get("span", 30)))
        value = max(0, min(span, int(dial.get("value", 0))))
        major = int(dial.get("major") or max(1, span // 3))
        arc = [(cx + (r - 1.5) * math.cos(math.radians(180 + a)), cy + (r - 1.5) * math.sin(math.radians(180 + a)))
               for a in range(0, 181, 3)]
        self.dial_ring(p, arc, night)
        for a in range(0, 181, 18):
            ang = math.radians(180 + a)
            self.dial_tick(p, cx + round((r - 1.5) * math.cos(ang)), cy + round((r - 1.5) * math.sin(ang)), night)
        for v in range(0, span + 1, major):
            ang = math.radians(180 + v * 180 / span)
            tx, ty = cx + round((r - 10) * math.cos(ang)), cy + round((r - 10) * math.sin(ang))
            lw = measure(str(v), "35")
            p.text(tx - lw // 2, ty - 2, str(v), k["muted"], "35")
        ang = math.radians(180 + value * 180 / span)
        for i in range(0, r - 11):
            p.px(cx + round(i * math.cos(ang)), cy + round(i * math.sin(ang)), k["accent"])
        self.dial_hub(p, cx, cy, night)
        shown = str(dial.get("value", 0))
        p.text(cx - measure(shown, "57", 2) // 2, cy - r + 8, shown, k["body"], "57", 2)
        sub = clip(fold(str(dial.get("sub", "")), "35"), 2 * r, "35")
        p.text(cx - measure(sub, "35") // 2, cy + 6, sub, k["muted"], "35")

    def materials(self, p: Pix, mat, x0, x1, y0, night):
        """Tracked bytes by file type as a ribbon of the set's wrappers, each named with its share, the
        total under it between two arrows."""
        k = self.ink(night)
        parts = [(str(n), int(v)) for n, v in mat["parts"] if int(v) > 0] or [("NONE", 1)]
        total = sum(v for _, v in parts)
        y1 = y0 + 12
        x = x0
        spots = []
        edge = self.wire_ink(night)
        for i, (name, n) in enumerate(parts):
            w = round(n / total * (x1 - x0)) if i < len(parts) - 1 else x1 - x
            for xx in range(x, x + w):
                for yy in range(y0, y1):
                    lift = 1 if yy == y0 else (-1 if yy == y1 - 2 else (-2 if yy == y1 - 1 else 0))
                    p.px(xx, yy, self.material(i, xx, yy, y0, y1, lift, night))
            if i:
                p.vline(x, y0, y1, edge)
            spots.append((f"{name} {round(n / total * 100)}%", x, w))
            x += w
        p.box(x0 - 1, y0 - 1, x1 - x0 + 2, y1 - y0 + 2, edge)
        placed = {0: [], 1: [], 2: []}
        for i, (lbl, x, w) in enumerate(spots):
            lbl = fold(lbl, "35")
            lw = measure(lbl, "35")
            sx = min(max(x0, x + w // 2 - lw // 2), x1 - lw)
            for level, sy in ((0, y0 - 8), (1, y1 + 4), (2, y1 + 12)):
                if all(sx + lw + 3 < a or sx > b + 3 for a, b in placed[level]):
                    placed[level].append((sx, sx + lw))
                    p.text(sx, sy, lbl, k["muted"], "35")
                    break
        mid = (x0 + x1) // 2
        size = mat.get("total", "")
        tw = measure(size, "57")
        y = y1 + 23
        p.hline(x0 + 6, mid - tw // 2 - 4, y, k["muted"])
        p.hline(mid + tw // 2 + 4, x1 - 6, y, k["muted"])
        p.sprite(x0, y - 2, ["..#", ".##", "###", ".##", "..#"], {"#": k["muted"]})
        p.sprite(x1 - 3, y - 2, ["#..", "##.", "###", "##.", "#.."], {"#": k["muted"]})
        p.text(mid - tw // 2, y - 3, size, k["body"], "57")

    @staticmethod
    def _digits(n: int) -> str:
        """A count as its digits, at least three, and a five-digit count in thousands."""
        return f"{n // 1000}K" if n >= 10000 else f"{n:03d}"

    def counters(self, p: Pix, counters, x, y, room, night):
        """Up to three counts, each digit cut into the set's cell, a leading nought cut shallower."""
        k = self.ink(night)
        items = [(str(lbl), int(n)) for lbl, n in list(counters)[:3]]
        if not items:
            return
        vals = [self._digits(n) for _, n in items]
        step = min(12, max(10, (room - 6 * (len(items) - 1)) // max(1, sum(len(v) for v in vals))))
        gap = max(4, (room - step * sum(len(v) for v in vals)) // max(1, len(items)))
        bx = x
        for (lbl, _), val in zip(items, vals):
            lead = len(val) - len(val.lstrip("0")) if val[-1] != "K" else 0
            for d, ch in enumerate(val):
                dx = bx + d * step
                p.stamp(("cell", night), lambda q, ox, oy: self.counter_cell(q, ox, oy, night), dx, y)
                p.text(dx + 3, y + 5, ch, self.counter_ink(night, d < lead and d < len(val) - 1), "57")
            cw = step * len(val)
            lbl = clip(fold(lbl, "35"), cw + gap - 2, "35")
            lw = measure(lbl, "35")
            p.text(bx + cw // 2 - lw // 2, y + 20, lbl, k["muted"], "35")
            bx += cw + gap

    def instruments(self, d: dict, night: bool) -> Pix:
        """Four panels: commits per week, days since the last release, bytes by file type, and counts."""
        hist, dial, mat = d["histogram"], d["dial"], d["materials"]
        p = self.canvas(WIDE, 173)
        k = self.ink(night)
        self.frame_element(p, night, "INSTRUMENTS", d.get("subject", ""), d.get("caption", ""), seed=22)
        p.vline(270, 21, 168, k["rule"])
        p.hline(4, 411, 100, k["rule"])
        p.text(14, 27, clip(fold(hist.get("label", "COMMITS PER WEEK"), "35"), 150, "35"), k["muted"], "35")
        s = fold(hist.get("sum", ""), "35")
        tw_ = measure(s, "35")
        p.text(260 - tw_, 28, s, k["muted"], "35")
        total = f"{sum(int(v) for _, v in hist['bars']):,}"
        p.text(260 - tw_ - 4 - measure(total), 26, total, k["body"], "57")
        self.histogram(p, hist, 14, 262, 88, night)
        p.text(278, 27, clip(fold(dial.get("label", ""), "35"), 130, "35"), k["muted"], "35")
        self.dial(p, dial, 340, 84, 38, night)
        p.text(14, 106, clip(fold(mat.get("label", ""), "35"), 240, "35"), k["muted"], "35")
        self.materials(p, mat, 16, 258, 126, night)
        p.text(278, 106, "COUNTED", k["muted"], "35")
        self.counters(p, d.get("counters", ()), 280, 120, 128, night)
        self._finish(p, night)
        return p

    def instruments_narrow(self, d: dict, night: bool) -> Pix:
        """The instruments on a phone: the four panels stacked, each full width."""
        hist, dial, mat = d["histogram"], d["dial"], d["materials"]
        p = self.canvas(NARROW, 276)
        k = self.ink(night)
        self.frame_element(p, night, "INSTRUMENTS", d.get("subject", ""), seed=32)
        p.text(10, 27, clip(fold(hist.get("label", ""), "35"), 90, "35"), k["muted"], "35")
        total = f"{sum(int(v) for _, v in hist['bars']):,} {fold(hist.get('sum', ''), '35')}".strip()
        total = clip(total, 70, "35")
        p.text(NARROW - 10 - measure(total, "35"), 27, total, k["muted"], "35")
        self.histogram(p, hist, 8, NARROW - 8, 84, night, labels=False)
        bars = list(hist["bars"])
        n = len(bars)
        if n:
            gap = (NARROW - 16 - 16) // n
            for i in sorted({0, n // 3, (2 * n) // 3, n - 1}):
                week = fold(str(bars[i][0]), "35")
                p.text(8 + 16 + i * gap + gap // 2 - measure(week, "35") // 2, 87, week, k["muted"], "35")
        p.hline(4, NARROW - 4, 96, k["rule"])
        p.text(10, 101, clip(fold(dial.get("label", ""), "35"), 160, "35"), k["muted"], "35")
        self.dial(p, dial, NARROW // 2, 150, 34, night)
        p.hline(4, NARROW - 4, 166, k["rule"])
        p.text(10, 171, clip(fold(mat.get("label", ""), "35"), 160, "35"), k["muted"], "35")
        self.materials(p, mat, 12, NARROW - 12, 190, night)
        p.hline(4, NARROW - 4, 234, k["rule"])
        p.text(10, 238, "COUNTED", k["muted"], "35")
        self.counters(p, d.get("counters", ()), 20, 246, NARROW - 40, night)
        self._finish(p, night)
        return p

    # ----------------------------------------------------------------------------------- milestones
    @staticmethod
    def _events(d: dict):
        events = sorted(d.get("events", ()), key=lambda e: _date(e["date"]))
        today = _date(d.get("today") or dt.date.today())
        if not events:
            events = [{"date": str(today), "tag": "NO RELEASE YET", "major": True}]
        return events, today

    @staticmethod
    def _kind(e: dict) -> str:
        if e.get("made"):
            return "made"
        if e.get("next"):
            return "next"
        if e.get("big"):
            return "big"
        return "major" if e.get("major", True) else "minor"

    def milestones(self, d: dict, night: bool) -> Pix:
        """Every release on a calendar with its quiet stretches cut out: the line burns up to today and is
        dotted beyond it, what each release brought above it, its version and day under it, the patches
        as small lights, and a key at the foot."""
        events, today = self._events(d)
        start = _date(d["start"]) if d.get("start") else _date(events[0]["date"]) - dt.timedelta(days=14)
        end = _date(d["end"]) if d.get("end") else max(_date(events[-1]["date"]), today) + dt.timedelta(days=21)
        p = self.canvas(WIDE, 141)
        k = self.ink(night)
        n = sum(1 for e in events if not e.get("next") and not e.get("made"))
        self.frame_element(p, night, "MILESTONES", d.get("subject", ""),
                           d.get("caption") or f"{n} RELEASE{'S' if n != 1 else ''}", seed=23)
        x0, x1, gy = 22, 396, 72
        scale = timeline(start, end, [_date(e["date"]) for e in events] + [today], x0, x1, cut=22)
        X = lambda day: round(scale.x(day))  # noqa: E731
        tx = X(today)
        self.timeline_line(p, x0, tx, gy, night)
        for x in range(tx + 5, x1):
            if (x // 3) % 2 == 0:
                p.px(x, gy + 1, k["rule"])
        for bx0, bx1, days in scale.breaks:
            bx0, bx1 = round(bx0), round(bx1)
            p.rect(bx0 + 1, gy - 3, bx1 - bx0 - 2, 7, self.bg_at(p, night, gy))
            zx = (bx0 + bx1) // 2
            p.sprite(zx - 3, gy - 2, ["#.....", ".#...#", "..#.#.", "...#.."][::1], {"#": k["muted"]})
            lbl = f"{days}D"
            p.text(zx - measure(lbl, "35") // 2, gy + 6, lbl, k["muted"], "35")
        for d0, d1, _, _ in scale.segments:
            m = dt.date(d0.year, d0.month, 1)
            while m <= d1:
                if m >= d0 and (m.month in (1, 4, 7, 10)):
                    x = X(m)
                    lbl = MONTHS[m.month - 1] + (f" {m.year}" if m.month == 1 else "")
                    p.vline(x, gy - 4, gy - 1, k["muted"])
                    p.text(x - measure(lbl, "35") // 2, gy + 29, lbl, k["muted"], "35")
                m = dt.date(m.year + (m.month == 12), m.month % 12 + 1, 1)
        placed = {0: [], 1: [], 2: []}
        for e in events:
            above = [fold(str(t), "35") for t in e.get("above", ())][:3]
            if not above or not e.get("major", True):
                continue
            x = X(_date(e["date"]))
            bw = max(measure(t, "35") for t in above)
            a = min(max(8, x - bw // 2), p.w - 8 - bw)
            level = next((lv for lv in (0, 1, 2) if all(a + bw + 3 < s or a > t + 3 for s, t in placed[lv])), None)
            if level is None:
                continue
            placed[level].append((a, a + bw))
            base_y = gy - 12 - level * (7 * len(above) + 3)
            for j, line in enumerate(reversed(above)):
                if base_y - j * 7 > 22:
                    p.text(a + (bw - measure(line, "35")) // 2, base_y - j * 7, line, k["muted"], "35")
        taken = []
        first = True
        for j, e in enumerate(events):
            kind = self._kind(e)
            if kind == "minor":
                continue
            x = X(_date(e["date"]))
            self.release(p, x, gy, kind, night, j)
            tag = clip(fold(str(e["tag"]), "35"), 60, "35")
            vw = measure(tag, "35")
            a = min(max(6, x - vw // 2), p.w - 6 - vw)
            level = 0 if all(a + vw + 3 < s or a > t + 3 for s, t in taken) else 1
            taken.append((a, a + vw))
            p.text(a, gy + 14 + level * 15, tag, k["body"], "35")
            day = _date(e["date"])
            when = fold(str(e.get("when") or _when(day, first or day.month == 1)), "35")
            first = False
            ww = measure(when, "35")
            p.text(min(max(6, x - ww // 2), p.w - 6 - ww), gy + 21 + level * 15, when, k["muted"], "35")
        for i, e in enumerate(e for e in events if self._kind(e) == "minor"):
            x = X(_date(e["date"]))
            self.release(p, x, gy, "minor", night, i)
            tag = fold(str(e["tag"]), "35")
            vw = measure(tag, "35")
            a = x - vw // 2
            if all(a + vw + 2 < s or a > t + 2 for s, t in taken) and 6 < a and a + vw < p.w - 6:
                taken.append((a, a + vw))
                p.text(a, gy + 14, tag, k["muted"], "35")
        self.today_mark(p, tx, gy, night)
        lx, ly = 14, 124
        key = [("major", "RELEASED")]
        if any(self._kind(e) == "made" for e in events):
            key.append(("made", "CREATED"))
        if any(self._kind(e) == "minor" for e in events):
            key.append(("minor", "PATCH"))
        if any(self._kind(e) == "next" for e in events):
            key.append(("next", "PLANNED"))
        for kind, word in key:
            self.release(p, lx + 3, ly - 3, kind, night, 0)
            lx += 10 + p.text(lx + 10, ly + 2, word, k["muted"], "35") + 10
        self.timeline_line(p, lx - 1, lx + 3, ly + 5, night)
        self.today_mark(p, lx + 2, ly + 5, night)
        p.text(lx + 10, ly + 2, f"TODAY, {_when(today)}", k["muted"], "35")
        self._finish(p, night)
        return p

    def milestones_narrow(self, d: dict, night: bool) -> Pix:
        """The milestones on a phone: the line hangs down the left, each release worth a name on it with
        its version and notes beside it and its date at the right, the planned ones last."""
        events, _ = self._events(d)
        entries = ([e for e in events if e.get("major", True) or e.get("made")]
                   or [e for e in events if not e.get("next")][-1:] or events[-1:])
        rows = [(e, [fold(str(t), "35") for t in e.get("above", ())][:3]) for e in entries]
        heights = [26 + 7 * max(0, len(ab) - 1) for _, ab in rows]
        p = self.canvas(NARROW, 30 + sum(heights) + 8)
        k = self.ink(night)
        self.frame_element(p, night, "MILESTONES", d.get("subject", ""), seed=33)
        gx, top = 16, 26
        ys, y = [], top
        for h in heights:
            ys.append(y)
            y += h
        self.timeline_line(p, gx + 1, gx + 2, top, night)
        for yy in range(top, ys[-1] + 4):
            p.px(gx + 1, yy, self.wire_ink(night))
        for i, ((e, above), y) in enumerate(zip(rows, ys)):
            for xx in range(gx + 3, gx + 6):
                p.px(xx, y - 1, k["rule"])
            self.release(p, gx + 8, y - 1, self._kind(e), night, i)
            day = _date(e["date"])
            when = fold(str(e.get("when") or _when(day, True)), "35")
            ww = measure(when, "35")
            p.text(NARROW - 10 - ww, y + 2, when, k["muted"], "35")
            tag = clip(fold(str(e["tag"]), "57"), NARROW - 36 - ww)
            p.text(gx + 16, y + 1, tag, k["body"], "57")
            for j, line in enumerate(above):
                p.text(gx + 16, y + 10 + j * 7, clip(line, NARROW - 36, "35"), k["muted"], "35")
        self._finish(p, night)
        return p

    # ------------------------------------------------------------------------------------ roster
    def _person(self, p: Pix, x, y, i, person, most, night, colw):
        k = self.ink(night)
        self.avatar(p, x + 8, y + 16, i, person, night)
        room = colw - 26
        p.text(x + 20, y + 4, clip(fold(str(person["name"]), "35"), room, "35"), k["body"], "35")
        p.text(x + 20, y + 11, clip(fold(str(person.get("handle", "")), "35"), room, "35"), k["muted"], "35")
        nw = p.text(x + 20, y + 19, f"{int(person['n']):,}", k["body"], "57")
        p.text(x + 20 + nw + 3, y + 21, "COMMITS", k["muted"], "35")
        bw = min(64, room - 2)
        self.commit_bar(p, x + 20, y + 30, bw, max(2, round(bw * int(person["n"]) / max(1, most))), night)

    def roster(self, d: dict, night: bool, half: bool = False, height: int | None = None) -> Pix:
        """The people who made it: on a wide sheet all in a row, each with their first and last; on half
        a page, and a phone, two to a row."""
        people = list(d["people"])
        most = max((int(q["n"]) for q in people), default=1)
        k = self.ink(night)
        if not half:
            p = self.canvas(WIDE, 113)
            self.frame_element(p, night, "DRAWN BY", d.get("subject", ""), d.get("caption", ""), seed=24)
            n = max(1, len(people))
            colw = (WIDE - 8) // n
            for i, person in enumerate(people):
                x = 4 + i * colw
                if i:
                    p.vline(x, 24, 108, k["rule"])
                self._person(p, x + 6, 29, i, person, most, night, colw - 8)
                if person.get("first") or person.get("last"):
                    p.hline(x + 4, x + colw - 4, 76, k["rule"])
                    for j, (lab, val) in enumerate((("FIRST", person.get("first", "")), ("LAST", person.get("last", "")))):
                        p.text(x + 8, 82 + j * 10, lab, k["muted"], "35")
                        p.text(x + 32, 82 + j * 10, clip(fold(str(val), "35"), colw - 40, "35"), k["body"], "35")
            self._finish(p, night)
            return p
        rows = math.ceil(len(people) / 2) or 1
        own = 24 + rows * 42 + 5
        H = max(own, height or 0)
        pad = (H - own) // 2
        p = self.canvas(HALF, H)
        self.frame_element(p, night, "DRAWN BY", d.get("subject", ""), seed=24)
        p.vline(101, 24, H - 5, k["rule"])
        for r in range(1, rows):
            p.hline(6, HALF - 6, 24 + pad + r * 42 - 3, k["rule"])
        for i, person in enumerate(people):
            x, y = (10 if i % 2 == 0 else 106), 29 + pad + (i // 2) * 42
            self._person(p, x, y, i, person, most, night, 92)
        self._finish(p, night)
        return p

    def roster_height(self, d: dict) -> int:
        return 24 + (math.ceil(len(d["people"]) / 2) or 1) * 42 + 5

    # ------------------------------------------------------------------------------------ certificate
    SEAL = 22   # the disc's radius; its rosette reaches 9 further

    def seal(self, p: Pix, d: dict, cx, cy, night):
        """The seal: the set's rosette round a disc, a check, the name and the commit in it (a long name
        on two lines in the commit's place), and a mark at its foot."""
        k = self.ink(night)
        R = self.SEAL
        self.rosette(p, cx, cy, R + 1, R + 9, 16, night)
        light, dark = self.card_bevel(night)
        for y in range(cy - R, cy + R + 1):
            for x in range(cx - R, cx + R + 1):
                dd = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
                if dd <= R:
                    c = k["fill"]
                    if dd > R - 1.4:
                        c = dark if (x + 0.5 - cx) * -0.63 + (y + 0.5 - cy) * -0.78 < 0 else light
                    p.px(x, y, c)
        p.sprite(cx - 6, cy - 14, CHECK, {"#": k["shadow"]}, 2)
        p.sprite(cx - 7, cy - 15, CHECK, {"#": k["accent"]}, 2)
        room = 2 * int(math.sqrt((R - 1.4) ** 2 - 49)) - 1
        name = fold(str(d.get("name", "")), "35")
        if measure(name, "35") <= room:
            lines = [(name, k["body"]), (clip(str(d.get("commit", "")), room - 6, "35"), k["muted"])]
        elif any(ch in name for ch in " -_./"):
            lines = [(clip(line, room - 6 * j, "35"), k["body"]) for j, line in enumerate(wrap(name, room, "35")[:2])]
        else:
            lines = [(clip(name, room, "35"), k["body"])]
        for j, (line, ink) in enumerate(lines):
            p.text(cx - measure(line, "35") // 2, cy + 2 + 7 * j, line, ink, "35")
        self.seal_mark(p, cx - 7, cy + R + 2, night)

    def ribbon(self, p: Pix, cx, y, lines, night):
        """The ribbon under the seal, with the ring's lower words on it."""
        if not lines:
            return
        k = self.ink(night)
        rw = max(measure(line, "35") for line in lines)
        self.tag(p, cx - rw // 2 - 3, y, rw + 6, 2 + 7 * len(lines), night)
        for j, line in enumerate(lines):
            p.text(cx - measure(line, "35") // 2, y + 2 + 7 * j, line, k["tag_ink"], "35")

    def _seal_column(self, p: Pix, d: dict, cx, y0, y1, room, night):
        """The seal and its ribbon, together in the middle of the column from y0 to y1."""
        below = balanced(str(d.get("ring_bottom") or ""), room)
        tall = 2 * (self.SEAL + 9) + 1 + (4 + 2 + 7 * len(below) if below else 0)
        top = y0 + max(0, (y1 - y0 - tall) // 2)
        cy = top + self.SEAL + 9
        self.seal(p, d, cx, cy, night)
        self.ribbon(p, cx, cy + self.SEAL + 13, below, night)

    def _check_rows(self, p: Pix, checks, x, y, room, night, evidence_right=None):
        """Each check with its mark, met or not, and its evidence under it (or at the right)."""
        k = self.ink(night)
        for row in checks:
            label, evidence = str(row[0]), str(row[1]) if len(row) > 1 else ""
            met = row[2] if len(row) > 2 else True
            if met:
                p.sprite(x + 1, y + 1, CHECK, {"#": k["shadow"]})
                p.sprite(x, y, CHECK, {"#": k["accent"]})
            else:
                p.sprite(x, y - 1, CROSS, {"#": k["muted"]})
            if evidence_right is not None:
                ev = clip(fold(evidence, "35"), 130, "35")
                ew = measure(ev, "35")
                p.text(x + 10, y, clip(fold(label, "35"), evidence_right - ew - 8 - x - 10, "35"), k["body"], "35")
                p.text(evidence_right - ew, y, ev, k["muted"], "35")
                y += 11
                continue
            lines = wrap(label, room, "35")[:2]
            for j, line in enumerate(lines):
                p.text(x + 10, y + j * 7, line, k["body"], "35")
            p.text(x + 10, y + len(lines) * 7, clip(fold(evidence, "35"), room, "35"), k["muted"], "35")
            y += (len(lines) + 1) * 7 + 1
        return y

    @staticmethod
    def _heading(d: dict, room: int) -> list:
        """The ring's upper words, the standard the checks are from, over the checks."""
        return [clip(line, room, "35") for line in wrap(str(d.get("ring_top") or ""), room, "35")][:2]

    def certificate(self, d: dict, night: bool, half: bool = False, height: int | None = None) -> Pix:
        """The checks a repository passes: its seal and ribbon on the left; on the right the standard
        they are from over each check, with its evidence."""
        checks = list(d["checks"])
        k = self.ink(night)
        if not half:
            head = self._heading(d, WIDE - 12 - 110 - 60)
            y = 27 + (9 * len(head) + 4 if head else 0)
            H = max(113, y + 11 * len(checks) + 6)
            p = self.canvas(WIDE, H)
            self.frame_element(p, night, "CONFORMANCE", d.get("subject", ""), d.get("caption", ""), seed=25)
            p.vline(100, 21, H - 5, k["rule"])
            self._seal_column(p, d, 50, 22, H - 6, 88, night)
            for j, line in enumerate(head):
                p.text(110, 27 + 9 * j, line, k["muted"], "35")
            if head:
                p.text(WIDE - 12 - measure("EVIDENCE", "35"), 27, "EVIDENCE", k["muted"], "35")
            self._check_rows(p, checks, 110, y, 0, night, evidence_right=WIDE - 12)
            self._finish(p, night)
            return p
        own = self.certificate_height(d)
        H = max(own, height or 0)
        p = self.canvas(HALF, H)
        self.frame_element(p, night, "CONFORMANCE", d.get("subject", ""), seed=25)
        p.vline(88, 21, H - 5, k["rule"])
        self._seal_column(p, d, 45, 22, H - 6, 78, night)
        head = self._heading(d, HALF - 10 - 94)
        y = 25 + (H - own) // 2
        for j, line in enumerate(head):
            p.text(94, y + 8 * j, line, k["muted"], "35")
        y += 8 * len(head) + 4 if head else 0
        self._check_rows(p, checks, 94, y, 92, night)
        self._finish(p, night)
        return p

    def certificate_height(self, d: dict) -> int:
        head = self._heading(d, HALF - 10 - 94)
        y = 25 + (8 * len(head) + 4 if head else 0)
        for row in d["checks"]:
            y += (len(wrap(str(row[0]), 92, "35")[:2]) + 1) * 7 + 1
        return max(113, y + 6)

    # ------------------------------------------------------------------------------------ placard
    def placard(self, d: dict, night: bool) -> Pix:
        """A card that links to another repository: its owner, its name as a title, its description, and
        three facts along its foot."""
        p = self.canvas(HALF, 92)
        k = self.ink(night)
        self.placard_board(p, night)
        icon = d.get("icon") or "book"
        p.sprite(10, 11, GLYPHS[7].get(icon, GLYPHS[7]["book"]), {"#": k["body"]})
        owner = clip(fold(str(d.get("owner", "")).upper(), "35"), 120, "35")
        tw = measure(owner, "35")
        self.tag(p, 20, 10, tw + 8, 9, night)
        p.text(24, 12, owner, k["tag_ink"], "35")
        self.tag(p, 180, 9, 12, 12, night)
        p.sprite(183, 12, ["..###", "...##", "..#.#", ".#...", "#...."], {"#": k["tag_ink"]})
        name = fold(str(d.get("name", "")).upper(), "57")
        nw = measure(name, "57", 2)
        x, scale = (10, 2) if nw <= 180 else (7, 2) if nw <= p.w - 16 else (10, 1)
        name = clip(name, 180 if x == 10 else p.w - 16, "57", scale)
        self.title_text(p, x, 22 + (0 if scale == 2 else 3), name, night, scale)
        if p.clear_of_words(156, 6, 172, 25):
            self.placard_mark(p, 158, 15, night)
        lines = wrap(str(d.get("desc", "")), 182)
        if len(lines) > 3:
            lines = lines[:2] + [clip(f"{lines[2]} {lines[3]}", 182)]
        for i, line in enumerate(lines):
            p.text(10, 40 + i * 9, line, k["body"])
        p.hline(4, 198, 69, k["rule"])
        cells = list(d.get("cells", ()))[:3]
        cw = 194 // max(1, len(cells))
        for i, (a, b) in enumerate(cells):
            x = 4 + i * cw
            if i:
                p.vline(x, 70, 86, k["rule"])
            p.text(x + 5, 72, clip(fold(str(a), "35"), cw - 8, "35"), k["muted"], "35")
            if measure(str(b), "57") <= cw - 8:
                p.text(x + 5, 78, fold(str(b), "57"), k["body"], "57")
            else:
                p.text(x + 5, 80, clip(fold(str(b), "35"), cw - 8, "35"), k["body"], "35")
        return p

    # ------------------------------------------------------------------------------------ the entry point
    KINDS = ("schematic", "instruments", "milestones", "roster", "certificate", "placard")

    def element_height(self, kind: str, d: dict) -> int | None:
        """How tall a half-page roster or certificate is on its own, for the page's shared half height."""
        if kind == "roster":
            return self.roster_height(d)
        if kind == "certificate":
            return self.certificate_height(d)
        return None

    def draw_element(self, kind: str, d: dict, night: bool, variant: str, height: int | None = None) -> Pix:
        """One element's drawing, in the kit's variants: wide, narrow (a phone) or half."""
        if kind == "placard":
            return self.placard(d, night)
        if kind in ("roster", "certificate"):
            fn = self.roster if kind == "roster" else self.certificate
            return fn(d, night, half=variant != "wide", height=height if variant == "half" else None)
        wide = {"schematic": self.schematic, "instruments": self.instruments, "milestones": self.milestones}
        narrow = {"schematic": self.schematic_narrow, "instruments": self.instruments_narrow,
                  "milestones": self.milestones_narrow}
        return (wide if variant == "wide" else narrow)[kind](d, night)
