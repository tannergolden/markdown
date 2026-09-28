# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The headers, footers and link buttons every holiday set draws, laid out once for all seven.

A set only decorates: its paper and sky, its frame and the garland across the
top, how its titles are lettered, the scene its headers stand on and the
ornaments of its footers. Where everything goes is decided here, from what the
page says: the title fitted to its room (two lines at the smallest size when
it must), the tagline, the motto and any further notes, the description, and
the figures ruled along the foot in as many rows as they need. Every design is
at least as tall as the set's approved sample, so a scene always has the room
it was drawn for.

The canvas is 415 by its height in 2 px units: 830 px, and 360 px (180 units)
on a phone. A header moves (twinkling, flickering, bobbing, drifting) and has
a still twin; a footer, a link and a phone's file hold still.
"""
from __future__ import annotations

from ..pixel import Pix, clip, fit, fold, measure, wrap

WIDE, NARROW = 415, 180
ARROW = ["...#...", "..###..", ".#.#.#.", "#..#..#", "...#...", "...#...", "...#..."]
# The height of each design's rule on the approved sample: a header is never shorter, so its scene
# (a tree, a lamp post, a flag) always stands where it was drawn to.
MIN_RULE = {"H1": 91, "H2": 106, "H3": 71}


class Banners:
    """The layouts. Every drawing hook a set overrides is in `Holiday`."""

    # ---- drafting pieces, coloured by the set
    def dim_across(self, p: Pix, x0, x1, y, night):
        """A dimension over a title, the kits' drafting habit: extension marks at both ends, a line with
        arrows pointing out to them, and the length in px on a backing in the middle."""
        k = self.ink(night)
        p.hline(x0, x1, y, k["muted"])
        p.vline(x0, y - 3, y + 4, k["muted"])
        p.vline(x1 - 1, y - 3, y + 4, k["muted"])
        p.sprite(x0 + 1, y - 2, ["..#", ".##", "###", ".##", "..#"], {"#": k["muted"]})
        p.sprite(x1 - 4, y - 2, ["#..", "##.", "###", "##.", "#.."], {"#": k["muted"]})
        label = str((x1 - x0) * 2)
        lw = p.measure(label, "35")
        lx = x0 + (x1 - x0 - lw) // 2
        p.rect(lx - 2, y - 3, lw + 4, 7, self.bg_at(p, night, y))
        p.text(lx, y - 2, label, k["muted"], "35")

    def dim_down(self, p: Pix, x, y0, y1, night):
        """A dimension beside a title: a line from its top to its foot between extension marks, and its
        height in px turned to read upward, as a drawing sets it."""
        k = self.ink(night)
        p.vline(x, y0, y1, k["muted"])
        p.hline(x - 3, x + 4, y0, k["muted"])
        p.hline(x - 3, x + 4, y1 - 1, k["muted"])
        p.sprite(x - 2, y0 + 1, ["..#..", ".###.", "#####"], {"#": k["muted"]})
        p.sprite(x - 2, y1 - 4, ["#####", ".###.", "..#.."], {"#": k["muted"]})
        label = str((y1 - y0) * 2)
        lh = p.measure(label, "35")
        ly = y0 + (y1 - y0 - lh) // 2
        p.rect(x - 3, ly - 2, 7, lh + 4, self.bg_at(p, night, ly))
        p.vtext(x - 2, ly, label, k["muted"])

    def numbered(self, p: Pix, x, y, n, text, night, centre=False, room=None):
        """A numbered general note: the number on the set's tag, the note in small capitals beside it,
        cut to `room` when one is given. Returns its width."""
        k = self.ink(night)
        text = fold(text, "35")
        if room:
            text = clip(text, room - 10, "35")
        w = 10 + p.measure(text, "35")
        if centre:
            x = x - w // 2
        self.tag(p, x, y, 7, 7, night)
        p.text(x + 2, y + 1, str(n), k["tag_ink"], "35")
        p.text(x + 10, y + 1, text, k["muted"], "35")
        return w

    @staticmethod
    def _spans(a, b, skip):
        out, cur = [], a
        for s0, s1 in sorted(skip):
            if s0 > cur:
                out.append((cur, min(s0, b)))
            cur = max(cur, s1)
        if cur < b:
            out.append((cur, b))
        return out

    @staticmethod
    def _natural(items, pad=10):
        return [max(measure(lab, "35"), measure(val, "57")) + pad for lab, val in items]

    def fig_rows(self, items, width, most=3, pad=8):
        """The figures packed into rows, in order, at most `most` a row, each row within `width`."""
        rows, cur, used = [], [], 0
        for item, n in zip(items, self._natural(items, pad)):
            if cur and (used + n > width or len(cur) == most):
                rows.append(cur)
                cur, used = [], 0
            cur.append((item, min(n, width)))
            used += n
        if cur:
            rows.append(cur)
        return rows

    def _cells(self, p: Pix, x0, x1, ry, row_h, row, night, vy):
        """One row of figure cells, widened in proportion to fill x0 to x1, ruled between."""
        k = self.ink(night)
        total = sum(n for _, n in row)
        extra = (x1 - x0) - total
        cx = x0
        for i, ((label, value), n) in enumerate(row):
            w = n + extra * n // total if i < len(row) - 1 else x1 - cx
            if i:
                p.vline(cx, ry + 1, ry + row_h, k["rule"])
            p.text(cx + 4, ry + 4, clip(label, w - 6, "35"), k["muted"], "35")
            p.text(cx + 4, ry + vy, clip(value, w - 6), k["body"], "57")
            cx += w

    def figures_height(self, items, width, row_h, one_row_h):
        """How much room the figures take under the rule: one row when they fit, else rows of up to four."""
        if not items:
            return 0
        if sum(self._natural(items)) <= width:
            return one_row_h
        return len(self.fig_rows(items, width, most=4)) * row_h

    def figures(self, p: Pix, x0, x1, y, items, night, skip=(), vy=12, one_row_h=27, row_h=22):
        """The figures GitHub gives, ruled along the foot: one row when they fit, more when they do not,
        the set's own touch lying on the rule where no scene stands on it."""
        k = self.ink(night)
        p.hline(x0, x1, y, k["rule"])
        for a, b in self._spans(x0 + 1, x1 - 1, skip):
            self.rule_decor(p, a, b, y, y + a, night)
        if not items:
            return
        if sum(self._natural(items)) <= x1 - x0:
            self._cells(p, x0, x1, y, one_row_h, list(zip(items, self._natural(items))), night, vy)
            return
        for r, row in enumerate(self.fig_rows(items, x1 - x0, most=4)):
            ry = y + r * row_h
            if r:
                p.hline(x0, x1, ry, k["rule"])
            self._cells(p, x0, x1, ry, row_h, row, night, 11)

    def fig_grid(self, p: Pix, x0, x1, y, items, night, row_h=22, draw=True):
        """The figures as a grid of ruled cells, the way the kit sets them on a phone. Returns the height."""
        k = self.ink(night)
        rows = self.fig_rows(items, x1 - x0)
        if draw:
            for r, row in enumerate(rows):
                ry = y + r * row_h
                p.hline(x0, x1, ry, k["rule"])
                if r == 0:
                    self.rule_decor(p, x0 + 1, x1 - 1, ry, ry, night)
                self._cells(p, x0, x1, ry, row_h, row, night, 11)
        return len(rows) * row_h

    # ---- what a header says
    @staticmethod
    def said(h) -> list[str]:
        """The general notes a header draws, the motto first."""
        return ([h.get("motto")] if h.on("motto") else []) + list(h.shown_notes)

    def _title(self, h, room, scales, rows=2):
        """The title's scale, its lines and their height, within `room` (or a map of each scale to its room)."""
        title = h.caps if h.on("title") else ""
        if not title:
            return 0, [], 0
        scale, lines = fit(title, room, "57", scales, rows)
        return scale, lines, len(lines) * 7 * scale + (len(lines) - 1) * 2 * scale

    def _set_title(self, p, x, y, lines, night, scale, centre=None):
        """The title's lines from (x, y), or centred on `centre`, a line's height and two font pixels apart.
        Returns the widest line's (x, width)."""
        best = (x, 0)
        for i, line in enumerate(lines):
            lw = p.measure(line, "57", scale)
            lx = centre - lw // 2 if centre is not None else x
            self.title_text(p, lx, y + i * (9 * scale), line, night, scale)
            if lw > best[1]:
                best = (lx, lw)
        return best

    # ---- the three headers, wide
    def h1(self, h, night: bool, motion: bool) -> Pix:
        """H1 Sheet: the title centred and dimensioned with its own width, the tagline, the description
        and the general notes centred under it, the set's scene on both sides of the foot, and the
        figures ruled along it. Its height follows what it says."""
        W = WIDE
        scale, tl, title_h = self._title(h, 300, (4, 3, 2))
        y = 26
        ty = y + title_h + 6 if tl else 22
        lines = wrap(h.get("tagline"), 300) if h.on("tagline") else []
        desc = wrap(h.get("description"), 300, "35") if h.on("description") else []
        notes = self.said(h)
        cursor = ty + len(lines) * 10 + (len(desc) * 8 + 2 if desc else 0)
        rule = max(MIN_RULE["H1"], cursor + 10 * max(1, len(notes)) + 1)
        items = list(h.shown_figures)
        fh = self.figures_height(items, W - 8, 22, 27)
        p = self.canvas(W, rule + (fh + 4 if items else 8))
        k = self.ink(night)
        widths = [p.measure(t, "57", scale) for t in tl]
        tw = max(widths) if widths else 0
        tx = (W - tw) // 2
        self.sky(p, night, rule - 2, seed=2, motion=motion,
                 avoid=[(tx - 4, y - 10, tx + tw + 6, y + title_h + 4), (40, ty - 3, W - 40, rule)])
        self.frame(p, night, webs=True)
        self.garland(p, 5, W - 5, 5, night, seed=0, sag=3, span=41, spacing=10)
        if tl:
            self.dim_across(p, tx, tx + tw, 19, night)
            self._set_title(p, tx, y, tl, night, scale, centre=W // 2)
        for i, line in enumerate(lines):
            p.text((W - p.measure(line)) // 2, ty + i * 10, line, k["body"])
        dy = ty + len(lines) * 10 + (2 if desc else 0)
        for i, line in enumerate(desc):
            p.text((W - p.measure(line, "35")) // 2, dy + i * 8, line, k["muted"], "35")
        ny = rule - 10 * len(notes) - 1
        for i, text in enumerate(notes):
            self.numbered(p, W // 2, ny + i * 10, i + 1, text, night, centre=True, room=280)
        skip = self.scene("H1", p, rule, night, motion)
        self.figures(p, 4, W - 4, rule, items, night, skip=skip)
        self._finish(p, night)
        return p

    def h2(self, h, night: bool, motion: bool) -> Pix:
        """H2 Section, the default: the title dimensioned both ways, SECTION A-A under it with the set's
        mark, the tagline, the description and the general notes, the set's scene on the right, and
        the figures ruled along the foot. Its height follows what it says."""
        W = WIDE
        scale, tl, title_h = self._title(h, 270, (4, 3, 2))
        x, y = 24, 29
        lines = wrap(h.get("tagline"), 282) if h.on("tagline") else []
        desc = wrap(h.get("description"), 282, "35") if h.on("description") else []
        notes = self.said(h)
        top = y + title_h + 16 if tl else 24
        note_y = top + len(lines) * 11 + (len(desc) * 8 + 3 if desc else 0)
        rule = max(MIN_RULE["H2"], note_y + 11 * max(1, len(notes)))
        items = list(h.shown_figures)
        fh = self.figures_height(items, W - 8, 22, 30)
        p = self.canvas(W, rule + (fh + 4 if items else 8))
        k = self.ink(night)
        tw = max((p.measure(t, "57", scale) for t in tl), default=0)
        self.sky(p, night, rule - 1, seed=5, motion=motion,
                 avoid=[(x - 12, y - 11, x + tw + 6, y + title_h + 12), (x - 2, top - 2, x + 290, rule)])
        self.frame(p, night, webs=True)
        self.garland(p, 5, W - 5, 5, night, seed=1, sag=4, span=41, spacing=10)
        if tl:
            self.dim_across(p, x, x + tw, y - 7, night)
            self.dim_down(p, x - 9, y, y + title_h, night)
            self._set_title(p, x, y, tl, night, scale)
            sw = p.text(x, y + title_h + 5, "SECTION A-A", k["accent"], "35")
            self.section_mark(p, x + sw + 5, y + title_h + 4, night)
        for i, line in enumerate(lines):
            p.text(x, top + i * 11, line, k["body"])
        for i, line in enumerate(desc):
            p.text(x, top + len(lines) * 11 + 1 + i * 8, line, k["muted"], "35")
        for i, text in enumerate(notes):
            self.numbered(p, x, note_y + i * 11, i + 1, text, night, room=270)
        skip = self.scene("H2", p, rule, night, motion)
        self.figures(p, 4, W - 4, rule, items, night, skip=skip)
        self._finish(p, night)
        return p

    def h3(self, h, night: bool, motion: bool) -> Pix:
        """H3 Strip: the sheet at a smaller scale; the title dimensioned with the set's mark beside it,
        the tagline and notes under it, a small scene on the right, and slimmer figures."""
        W = WIDE
        scale, tl, title_h = self._title(h, 318, (3, 2))
        x, y = 20, 26
        lines = wrap(h.get("tagline"), 330) if h.on("tagline") else []
        notes = self.said(h)
        top = y + title_h + 4 if tl else 24
        after = top + len(lines) * 9
        rule = max(MIN_RULE["H3"], after + (10 * len(notes) + 1 if notes else 0) + 2)
        items = list(h.shown_figures)
        fh = self.figures_height(items, W - 8, 20, 20)
        p = self.canvas(W, rule + (fh + 4 if items else 8))
        k = self.ink(night)
        tw = max((p.measure(t, "57", scale) for t in tl), default=0)
        self.sky(p, night, rule - 1, seed=7, motion=motion,
                 avoid=[(x - 4, y - 10, x + tw + 22, y + title_h + 4), (x - 2, top - 3, x + 336, rule)])
        self.frame(p, night, webs=True)
        self.garland(p, 5, W - 5, 5, night, seed=1, sag=3, span=41, spacing=10)
        if tl:
            self.dim_across(p, x, x + tw, 19, night)
            self._set_title(p, x, y, tl, night, scale)
            if x + tw + 30 < 340:
                self.strip_mark(p, x + tw + 9, y + 9, night)
        for i, line in enumerate(lines):
            p.text(x, top + i * 9, line, k["body"])
        for i, text in enumerate(notes):
            self.numbered(p, x, after + 1 + i * 10, i + 1, text, night, room=320)
        skip = self.scene("H3", p, rule, night, motion)
        self.figures(p, 4, W - 4, rule, items, night, skip=skip, vy=11, one_row_h=20, row_h=20)
        self._finish(p, night)
        return p

    # ---- the three headers on a phone: laid out once to learn the height, then drawn
    def _two_pass(self, draw, h, night):
        return draw(draw(None, h, night), h, night)

    def h1_narrow(self, h, night: bool) -> Pix:
        return self._two_pass(self._h1n, h, night)

    def h2_narrow(self, h, night: bool) -> Pix:
        return self._two_pass(self._h2n, h, night)

    def h3_narrow(self, h, night: bool) -> Pix:
        return self._two_pass(self._h3n, h, night)

    def _h1n(self, size, h, night):
        H, grid = size or (None, None)
        p = self.canvas(NARROW, H or 400)
        k = self.ink(night)
        scale, tl, title_h = self._title(h, {3: 160, 2: 164}, (3, 2))
        tw = max((p.measure(t, "57", scale) for t in tl), default=0)
        x, y = (NARROW - tw) // 2, 26
        t0 = y + title_h + 7 if tl else 22
        lines = wrap(h.get("tagline"), 160) if h.on("tagline") else []
        desc = wrap(h.get("description"), 160, "35") if h.on("description") else []
        notes = self.said(h)
        t1 = t0 + 10 * len(lines) + (8 * len(desc) + 2 if desc else 0)
        banded = all(measure(fold(n, "35"), "35") + 10 <= 104 for n in notes)
        if not banded:
            t1 += 2 + 10 * len(notes)
        if H:
            self.sky(p, night, grid, seed=12, motion=False,
                     avoid=[(x - 4, 14, x + tw + 6, y + title_h + 4), (6, t0 - 3, NARROW - 6, t1 + 1)])
            self.frame(p, night, webs=True)
            self.garland(p, 5, NARROW - 5, 5, night, seed=3, sag=3, span=34, spacing=10)
            if tl:
                self.dim_across(p, x, x + tw, 19, night)
                self._set_title(p, x, y, tl, night, scale, centre=NARROW // 2)
            for i, line in enumerate(lines):
                p.text((NARROW - p.measure(line)) // 2, t0 + i * 10, line, k["body"])
            for i, line in enumerate(desc):
                p.text((NARROW - p.measure(line, "35")) // 2, t0 + 10 * len(lines) + 2 + i * 8, line, k["muted"], "35")
        ry = t1 + (10 * len(notes) + 20 if banded else 30)      # the figures' rule, which the scene stands on
        if H:
            # Short notes stand just above the rule, between the scene's two sides; longer ones above it.
            for i, text in enumerate(notes):
                if banded:
                    self.numbered(p, NARROW // 2, ry - 10 * (len(notes) - i), i + 1, text, night, centre=True, room=104)
                else:
                    self.numbered(p, NARROW // 2, t1 - 10 * (len(notes) - i), i + 1, text, night, centre=True, room=164)
            self.scene_narrow("H1", p, ry, night)
        gh = self.fig_grid(p, 4, NARROW - 4, ry, list(h.shown_figures), night, draw=bool(H))
        if H:
            if not h.shown_figures:
                p.hline(4, NARROW - 4, ry, k["rule"])
            self._finish(p, night)
        return p if H else (ry + (gh + 4 if gh else 8), ry)

    def _h2n(self, size, h, night):
        H, grid = size or (None, None)
        p = self.canvas(NARROW, H or 400)
        k = self.ink(night)
        scale, tl, title_h = self._title(h, {3: 124, 2: 152}, (3, 2))
        tw = max((p.measure(t, "57", scale) for t in tl), default=0)
        x, y = 22, 28
        lines = wrap(h.get("tagline"), 150) if h.on("tagline") else []
        desc = wrap(h.get("description"), 150, "35") if h.on("description") else []
        notes = self.said(h)
        yy = y + title_h + 5 if tl else 22
        t0 = yy + 12
        t1 = t0 + 10 * len(lines) + (8 * len(desc) + 2 if desc else 0) + 3 + 10 * len(notes)
        if H:
            self.sky(p, night, grid, seed=15, motion=False,
                     avoid=[(x - 12, 14, x + tw + 6, y + title_h + 12), (x - 2, t0 - 2, NARROW - 6, t1)])
            self.frame(p, night, webs=True)
            self.garland(p, 5, NARROW - 5, 5, night, seed=4, sag=3, span=34, spacing=10)
            if tl:
                self.dim_across(p, x, x + tw, y - 7, night)
                self.dim_down(p, x - 9, y, y + title_h, night)
                self._set_title(p, x, y, tl, night, scale)
                sw = p.text(x, yy, "SECTION A-A", k["accent"], "35")
                self.section_mark(p, x + sw + 4, yy - 1, night)
            self.scene_narrow("H2", p, yy, night)
            for i, line in enumerate(lines):
                p.text(x, t0 + i * 10, line, k["body"])
            for i, line in enumerate(desc):
                p.text(x, t0 + 10 * len(lines) + 2 + i * 8, line, k["muted"], "35")
            ny = t0 + 10 * len(lines) + (8 * len(desc) + 2 if desc else 0) + 3
            for i, text in enumerate(notes):
                self.numbered(p, x, ny + i * 10, i + 1, text, night, room=150)
        ry = t1 + 4
        gh = self.fig_grid(p, 4, NARROW - 4, ry, list(h.shown_figures), night, draw=bool(H))
        if H:
            if not h.shown_figures:
                p.hline(4, NARROW - 4, ry, k["rule"])
            self._finish(p, night)
        return p if H else (ry + (gh + 4 if gh else 8), ry)

    def _h3n(self, size, h, night):
        H, grid = size or (None, None)
        p = self.canvas(NARROW, H or 400)
        k = self.ink(night)
        scale, tl, title_h = self._title(h, {3: 124, 2: 156}, (3, 2))
        tw = max((p.measure(t, "57", scale) for t in tl), default=0)
        x, y = 12, 26
        t0 = y + title_h + 7 if tl else 22
        lines = wrap(h.get("tagline"), 156) if h.on("tagline") else []
        notes = self.said(h)
        t1 = t0 + 10 * len(lines) + 10 * len(notes)
        if H:
            self.sky(p, night, grid, seed=17, motion=False,
                     avoid=[(x - 4, 14, x + tw + 6, y + title_h + 4), (x - 2, t0 - 3, NARROW - 6, t1 + 1)])
            self.frame(p, night, webs=True)
            self.garland(p, 5, NARROW - 5, 5, night, seed=5, sag=3, span=34, spacing=10)
            if tl:
                self.dim_across(p, x, x + tw, 19, night)
                self._set_title(p, x, y, tl, night, scale)
                if x + tw + 8 < 150:
                    self.scene_narrow("H3", p, y + title_h + 1, night)
            for i, line in enumerate(lines):
                p.text(x, t0 + i * 10, line, k["body"])
            for i, text in enumerate(notes):
                self.numbered(p, x, t0 + 10 * len(lines) + i * 10, i + 1, text, night, room=156)
        ry = t1 + (6 if notes else 4)
        gh = self.fig_grid(p, 4, NARROW - 4, ry, list(h.shown_figures), night, draw=bool(H))
        if H:
            if not h.shown_figures:
                p.hline(4, NARROW - 4, ry, k["rule"])
            self._finish(p, night)
        return p if H else (ry + (gh + 4 if gh else 8), ry)

    # ---- footers
    @staticmethod
    def sentences(text: str, maxw: int, font: str = "57") -> list[str]:
        """A closing phrase a sentence a line when every sentence fits on one, else wrapped to the width."""
        text = fold(text, font)
        parts, cur = [], ""
        for word in text.split():
            cur = f"{cur} {word}".strip()
            if cur.endswith((".", "!", "?")):
                parts.append(cur)
                cur = ""
        if cur:
            parts.append(cur)
        if len(parts) > 1 and all(measure(s_, font) <= maxw for s_ in parts):
            return parts
        return wrap(text, maxw, font)

    @staticmethod
    def _foot_cells(ft) -> list[tuple[str, str, str]]:
        """The title block's cells after its notes: who built it, the licence, the last change, the way up."""
        cells = []
        if ft.on("built"):
            cells.append(("BUILT WITH", ft.handle, "heart"))
        if ft.on("license"):
            cells.append(("LICENSE", ft.license, ""))
        if ft.on("updated"):
            cells.append(("UPDATED", ft.updated, ""))
        if ft.on("top"):
            cells.append(("RETURN TO", ft.get("top"), "up"))
        return cells

    def _cell_width(self, label, value, mark):
        lw = measure(label, "35") + (21 if mark == "heart" else 0)
        vw = measure(value) + (10 if mark == "up" else 0)
        return max(lw, vw) + 12

    def _cell(self, p: Pix, x, y, label, value, mark, night, room, gap=10):
        """One cell of a title block: its label in small capitals, its value `gap` under it."""
        k = self.ink(night)
        lw = p.text(x, y, label, k["muted"], "35")
        if mark == "heart":
            self.heart(p, x + lw + 2, y - 1)
            p.text(x + lw + 11, y, "BY", k["muted"], "35")
        vx = x
        if mark == "up":
            p.sprite(vx, y + gap, ARROW, {"#": k["accent"]})
            vx += 10
        p.text(vx, y + gap, clip(value, room - (vx - x)), k["body"])

    def f1(self, ft, night: bool) -> Pix:
        """F1 Title block: one ruled row of the closing notes, built by, licence, the last change and the
        way back up, each cell as wide as it needs and the notes taking the rest."""
        W = WIDE
        cells = self._foot_cells(ft)
        widths = [self._cell_width(*c) for c in cells]
        closing = ft.get("closing")
        notes_w = (W - 6) - sum(widths) if closing else 0
        if closing and notes_w < 120:
            widths = [max(40, w * ((W - 6 - 120) // max(1, sum(widths)))) for w in widths] if sum(widths) else []
            notes_w = (W - 6) - sum(widths)
        lines = self.sentences(closing, notes_w - 26)[:3] if closing else []
        h = max(35, 14 + 9 * len(lines) + 5)
        p = self.canvas(W, h)
        k = self.ink(night)
        self.paper(p, night, uid="p")
        if night:
            self.stars(p, 6, 5, W - 6, h - 5, 30, seed=4, twinkling=False, faint=True)
        self.frame(p, night)
        x = 3
        if closing:
            p.text(8, 7, "NOTES", k["muted"], "35")
            for i, line in enumerate(lines):
                p.text(8, 14 + i * 9, line, k["body"])
            self.footer_mark(p, 3 + notes_w - 18, 11, night)
            x += notes_w
        elif not cells:
            p.text(8, 14, "Footer", k["body"])
        for (label, value, mark), w in zip(cells, widths):
            if x > 3:
                p.vline(x, 4, h - 4, k["rule"])
            self._cell(p, x + 5, 7, label, value, mark, night, w - 8)
            x += w
        return p

    def scale_bar(self, p: Pix, x0, y0, night):
        """The graphic scale, true to size: 100 px of the set's bar, a colour every 10 px, labelled every 20."""
        k = self.ink(night)
        for i in range(6):
            p.vline(x0 + i * 10, y0 - 2, y0, k["body"])
            lbl = str(i * 20)
            lw = p.measure(lbl, "35")
            lx = x0 + i * 10 - lw // 2 if i < 5 else x0 + 47
            p.text(lx, y0 - 8, lbl, k["muted"], "35")
        self.bar(p, x0, y0, 50, 4, 5)
        p.box(x0 - 1, y0 - 1, 52, 6, k["body"])
        p.text(x0, y0 + 9, "SCALE 1:1 · PX", k["muted"], "35")

    def _attribution(self, ft) -> tuple[bool, str]:
        """The line under the closing phrase: built with love by, the licence, the date."""
        parts = []
        if ft.on("built"):
            parts.append(f"BY {ft.handle.upper()}")
        if ft.on("license"):
            parts.append(f"{ft.license} LICENSE")
        if ft.on("updated"):
            parts.append(ft.updated)
        return ft.on("built"), " · ".join(parts)

    def f2(self, ft, night: bool) -> Pix:
        """F2 Scale bar: a graphic scale, the closing phrase over the attribution, and the way back up."""
        W = WIDE
        mid0, mid1 = 96, 330 if ft.on("top") else 412
        closing = ft.get("closing")
        lines = self.sentences(closing, mid1 - mid0 - 8)[:2] if closing else []
        if len(lines) == 2 and measure(" ".join(lines)) <= mid1 - mid0 - 8:
            lines = [" ".join(lines)]
        h = 43 + (9 if len(lines) > 1 else 0)
        p = self.canvas(W, h)
        k = self.ink(night)
        self.paper(p, night, uid="p")
        if night:
            self.stars(p, 6, 5, W - 6, h - 7, 36, seed=6, twinkling=False, faint=True)
        self.frame(p, night)
        p.vline(95, 4, h - 4, k["rule"])
        if ft.on("top"):
            p.vline(330, 4, h - 4, k["rule"])
        self.scale_bar(p, 18, 17, night)
        room = mid1 - mid0
        for i, line in enumerate(lines):
            p.text(mid0 + (room - p.measure(line)) // 2, 11 + i * 9, line, k["body"])
        heart, rest = self._attribution(ft)
        ay = 25 + (9 if len(lines) > 1 else 0)
        if heart:
            first = "BUILT WITH"
            rest = clip(rest, room - 16 - p.measure(first, "35"), "35")
            total = p.measure(first, "35") + 12 + p.measure(rest, "35")
            sx = mid0 + (room - total) // 2
            w1 = p.text(sx, ay, first, k["muted"], "35")
            self.heart(p, sx + w1 + 2, ay - 1)
            p.text(sx + w1 + 12, ay, rest, k["muted"], "35")
        elif rest:
            rest = clip(rest, room - 8, "35")
            p.text(mid0 + (room - p.measure(rest, "35")) // 2, ay, rest, k["muted"], "35")
        if ft.on("top"):
            lw = p.measure("RETURN TO", "35")
            p.text(330 + (82 - lw) // 2, 11, "RETURN TO", k["muted"], "35")
            top = clip(ft.get("top"), 70)
            bw = p.measure(top) + 10
            bx = 330 + (82 - bw) // 2
            p.sprite(bx, 21, ARROW, {"#": k["accent"]})
            p.text(bx + 10, 21, top, k["body"])
        return p

    def _f1n(self, H, ft, night):
        p = self.canvas(NARROW, H or 300)
        k = self.ink(night)
        closing = ft.get("closing")
        if H:
            self.paper(p, night, uid="p")
            if night:
                self.stars(p, 6, 5, NARROW - 6, H - 8, 16, seed=5, twinkling=False, faint=True)
            self.frame(p, night)
            if closing:
                p.text(8, 7, "NOTES", k["muted"], "35")
                self.footer_mark(p, NARROW - 24, 10, night)
        y = 14
        for line in (self.sentences(closing, 150) if closing else []):
            if H:
                p.text(8, y, line, k["body"])
            y += 9
        y += 2 if closing else -8
        cells = self._foot_cells(ft)
        half = NARROW // 2 - 4
        for r in range(0, len(cells), 2):
            row = cells[r:r + 2]
            if H:
                p.hline(4, NARROW - 4, y, k["rule"])
                if len(row) > 1:
                    p.vline(NARROW // 2, y + 1, y + 20, k["rule"])
                for i, (label, value, mark) in enumerate(row):
                    self._cell(p, 8 + i * half, y + 4, label, value, mark, night, half - 8, gap=7)
            y += 20
        return p if H else y + 4

    def _f2n(self, H, ft, night):
        p = self.canvas(NARROW, H or 300)
        k = self.ink(night)
        if H:
            self.paper(p, night, uid="p")
            if night:
                self.stars(p, 6, 5, NARROW - 6, H - 8, 16, seed=7, twinkling=False, faint=True)
            self.frame(p, night)
            self.scale_bar(p, 12, 15, night)
            if ft.on("top"):
                top = clip(ft.get("top"), 60)
                bw = p.measure(top) + 10
                p.sprite(NARROW - 10 - bw, 13, ARROW, {"#": k["accent"]})
                p.text(NARROW - bw, 13, top, k["body"])
        y = 34
        if H:
            p.hline(4, NARROW - 4, y, k["rule"])
        y += 5
        closing = ft.get("closing")
        for line in (self.sentences(closing, 164) if closing else []):
            if H:
                p.text((NARROW - p.measure(line)) // 2, y, line, k["body"])
            y += 9
        y += 1
        heart, rest = self._attribution(ft)
        parts = rest.split(" · ")
        first_line = parts[0] if heart and parts and parts[0].startswith("BY ") else ""
        second = " · ".join(parts[1:] if first_line else parts)
        if heart and first_line:
            if H:
                label = "BUILT WITH"
                first_line = clip(first_line, 160 - p.measure(label, "35") - 12, "35")
                tot = p.measure(label, "35") + 12 + p.measure(first_line, "35")
                sx = (NARROW - tot) // 2
                w1 = p.text(sx, y, label, k["muted"], "35")
                self.heart(p, sx + w1 + 2, y - 1)
                p.text(sx + w1 + 12, y, first_line, k["muted"], "35")
            y += 8
        if second:
            if H:
                second = clip(second, 164, "35")
                p.text((NARROW - p.measure(second, "35")) // 2, y, second, k["muted"], "35")
            y += 8
        return p if H else y + 6

    def f1_narrow(self, ft, night: bool) -> Pix:
        return self._f1n(self._f1n(None, ft, night), ft, night)

    def f2_narrow(self, ft, night: bool) -> Pix:
        return self._f2n(self._f2n(None, ft, night), ft, night)

    # ---- a link under the footer
    def link_button(self, label: str, index: int, night: bool) -> Pix:
        """A link under the footer, 26 px tall like the kit's: its label in capitals and, since a set
        cannot know what an arbitrary link is for, the next of its icons in the row's order."""
        text = clip(fold(label, "57").upper(), 360)
        w = 15 + Pix.measure(text) + 6
        p = self.canvas(w, 13)
        fill, edge, ink, shade = self.link_colours(night)
        p.rect(1, 3, w - 2, 9, fill)
        p.hline(1, w - 1, 11, shade)
        p.box(0, 2, w, 11, edge, notch=True)
        self.link_top(p, 2, w - 2, 2, len(label) + 3, night)
        art, pal = self.link_icon(index, night, ink)
        p.sprite(5, 4, art, pal)
        p.text(15, 4, text, ink)
        return p
