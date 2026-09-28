# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The standard theme's elements: the six drawings in a badge's language.

Every sheet opens with the masthead's band: the element's kind in the
label's black beside its icon, and its subject in a block of the accent, as
a badge carries a label and a message; its caption stands in the band before
the block, or under the band when there is no room. Boxes are badges with a
black tab for their icon, figures are flat bars and gauges in the palette's
colours, and every label is set in the bold capitals a badge uses. A
placard, a card that links elsewhere, is itself a badge that goes somewhere:
a band with the repository's name, and an arrow in the accent.

Each is drawn from the same data as the prints' elements and placed by the
same layout, in the same variants, so a page changes theme without changing
a line of its settings.
"""
from __future__ import annotations

import datetime as dt
import math

from ..canvas import BUDGET, DARK, DAY, c, lint
from ..elements import draw as E
from ..elements.layout import Box, layers, route, snake, timeline
from ..lettering import cap_height, f1, width
from . import pieces as P
from .pieces import Chip

THEMES = {"day": DAY, "dark": DARK}
WIDE, NARROW, HALF = 830, 360, 404
BAND = 40
PAD = 20
# The kind each element's band names, and its icon.
KIND = {"schematic": ("schematic", "grid"), "instruments": ("instruments", "pulse"),
        "milestones": ("milestones", "flag"), "roster": ("contributors", "users"),
        "certificate": ("conformance", "medal")}
# Colours for the parts of a whole, in turn; the part a measurement calls OTHER is gray.
PARTS = ("cobalt", "tangerine", "forest", "magenta", "purple")
# A person's medallion, in turn; a bot's is slate.
PEOPLE = ("crimson", "tangerine", "ocean", "forest", "purple", "magenta")
# The counters' message panels, in turn.
COUNTERS = ("ocean", "magenta", "forest")


def ok(th: dict, passed: bool = True) -> str:
    """The colour of a check that is met, or not: green by night, forest by day; rose and crimson."""
    if passed:
        return "green" if th["dark"] else "forest"
    return "rose" if th["dark"] else "crimson"


def say(cv, s, *, x: float, y: float, size: float, fill: str, ground: str, face: str = "sans-bold",
        anchor: str = "start", ls: float = 0.0, what: str = "label") -> str:
    """A run of letters, each character one the face can draw or its plainest spelling."""
    return P.text(cv, E.plain(str(s), face), x=x, y=y, size=size, fill=fill, ground=ground, face=face,
                  anchor=anchor, ls=ls, what=what)


def caps(cv, s, x: float, y: float, th: dict, size: float = 8.5, fill: str | None = None, anchor: str = "start",
         ls: float = .8, what: str = "label") -> str:
    """Small capitals on the paper, in the muted ink unless told otherwise."""
    return say(cv, str(s).upper(), x=x, y=y, size=size, fill=fill or th["muted"], ground=th["paper"], anchor=anchor,
               ls=ls, what=what)


def cap(size: float) -> float:
    return cap_height("sans-bold", size)


def number(cv, n, x: float, y: float, size: float = 16) -> str:
    """A note's number: a square of the accent with the number in its letters, a badge's idea of a callout."""
    return (P.rect(x, y, size, size, P.ACCENT)
            + say(cv, str(n), x=x + size / 2, y=y + size / 2 + cap(size * .62) / 2, size=size * .62,
                  fill=P.letters_on(P.ACCENT), ground=P.ACCENT, anchor="middle", what="note number"))


def _svg(cv) -> str:
    return cv.svg()


# --- the band -----------------------------------------------------------------------------------

def _band(W: float, kind: str, subject: str, caption: str) -> tuple[str, float, float, bool]:
    """(the subject as the block carries it, its size, the block's width, whether the caption fits the band)."""
    kw = PAD + 26 + width(kind.upper(), "sans-bold", 10.5, 1.1) + 18
    text, size = "", 10.0
    if subject:
        for text in (subject.upper(), subject.upper().rsplit("/", 1)[-1]):
            size = P.fitted(text, "sans-bold", 10, 7.5, W - kw - 36, .1)
            if kw + 36 + width(text, "sans-bold", size, size * .1) <= W:
                break
    mw = (36 + width(text, "sans-bold", size, size * .1)) if text else 0
    inside = bool(caption) and kw + width(caption.upper(), "sans-bold", 8.5, .9) + 18 <= W - mw
    return text, size, mw, inside


def top_of(W: float, kind: str, subject: str, caption: str) -> float:
    """Where a sheet's content starts: under the band, and under its caption when the band had no room for it."""
    *_, inside = _band(W, kind, subject, caption)
    return BAND + (26 if caption and not inside else 0)


def frame(cv, th: dict, W: float, H: float, element: str, subject: str, caption: str = "") -> None:
    """The card, the band across its top, and the caption."""
    kind, glyph = KIND[element]
    text, size, mw, inside = _band(W, kind, subject, caption)
    cid = P.card(cv, th, W, H)
    lab = th["label"]
    on = P.letters_on(lab)
    m = [P.rect(0, 0, W - mw, BAND, lab), P.icon(glyph, PAD, BAND / 2 - 8, 16, on, 2.1),
         say(cv, kind.upper(), x=PAD + 26, y=BAND / 2 + cap(10.5) / 2, size=10.5, ls=1.1, fill=on, ground=lab,
             what="element kind")]
    if mw:
        m += [P.rect(W - mw, 0, mw, BAND, P.ACCENT),
              say(cv, text, x=W - mw / 2, y=BAND / 2 + cap(size) / 2, size=size, ls=size * .1,
                  fill=P.letters_on(P.ACCENT), ground=P.ACCENT, anchor="middle", what="element subject")]
    if caption and inside:
        m.append(say(cv, caption.upper(), x=W - mw - 18, y=BAND / 2 + cap(8.5) / 2, size=8.5, ls=.9, fill="ash",
                     ground=lab, anchor="end", what="caption"))
    cv.add(f'<g clip-path="url(#{cid})">' + "".join(m) + "</g>")
    if caption and not inside:
        cv.add(caps(cv, caption, PAD, BAND + 19, th, 8.5, ls=.9, what="caption"))


def heading(cv, s, x: float, y: float, th: dict, anchor: str = "start") -> str:
    return caps(cv, s, x, y, th, 9, th["muted"], anchor, .9, what="heading")


# --- schematic ----------------------------------------------------------------------------------

def _rounded(pts: list, r: float = 8) -> str:
    """A polyline's path with its corners rounded."""
    d = f"M{f1(pts[0][0])} {f1(pts[0][1])}"
    for i in range(1, len(pts)):
        (ax, ay), (bx, by) = pts[i - 1], pts[i]
        if i < len(pts) - 1:
            cx, cy = pts[i + 1]
            n1 = max(1e-9, math.hypot(bx - ax, by - ay))
            n2 = max(1e-9, math.hypot(cx - bx, cy - by))
            rr = min(r, n1 / 2, n2 / 2)
            p1 = (bx - (bx - ax) / n1 * rr, by - (by - ay) / n1 * rr)
            p2 = (bx + (cx - bx) / n2 * rr, by + (cy - by) / n2 * rr)
            d += f"L{f1(p1[0])} {f1(p1[1])}Q{f1(bx)} {f1(by)} {f1(p2[0])} {f1(p2[1])}"
        else:
            d += f"L{f1(bx)} {f1(by)}"
    return d


def _arrowhead(x: float, y: float, dx: float, dy: float, colour: str, length: float = 8, wide: float = 7) -> str:
    n = math.hypot(dx, dy) or 1
    ux, uy = dx / n, dy / n
    bx, by = x - ux * length, y - uy * length
    px, py = -uy * wide / 2, ux * wide / 2
    return (f'<path d="M{f1(x)} {f1(y)}L{f1(bx + px)} {f1(by + py)}L{f1(bx - px)} {f1(by - py)}z" '
            f'fill="{c(colour)}"/>')


def _clear(box: tuple, taken: list) -> bool:
    return all(box[2] < a - 3 or box[0] > b + 3 or box[3] < t - 3 or box[1] > u + 3 for a, t, b, u in taken)


def _wire(cv, th: dict, W: float, pts: list, label: str | None, *, taken: list, avoid: list,
          along: bool = False) -> str:
    """A wire in the muted ink ending in an arrowhead just short of the box it enters, its label in small
    capitals beside its longest run, slid along the run until clear of every box, label and other wire."""
    col = th["muted"]
    (x0, y0), (x1, y1) = pts[-2], pts[-1]
    n = math.hypot(x1 - x0, y1 - y0) or 1
    tip = (x1 - (x1 - x0) / n * 2, y1 - (y1 - y0) / n * 2)
    pts = pts[:-1] + [tip]
    out = [f'<path d="{_rounded(pts)}" fill="none" stroke="{c(col)}" stroke-width="1.8" stroke-linejoin="round"/>',
           _arrowhead(tip[0], tip[1], x1 - x0, y1 - y0, col)]
    if not label:
        return "".join(out)
    text = E.plain(str(label).upper(), "sans-bold")
    tw = width(text, "sans-bold", 8, .8)
    segs = list(zip(pts, pts[1:]))
    i = max(range(len(segs)), key=lambda k: abs(segs[k][1][0] - segs[k][0][0]) + abs(segs[k][1][1] - segs[k][0][1]))
    (ax, ay), (bx, by) = segs[i]
    flat = abs(by - ay) < 1
    first = None
    for k in (0, 1, -1, 2, -2, 3, -3):
        t = .5 + k * .14
        if not .15 <= t <= .85:
            continue
        px, py = ax + (bx - ax) * t, ay + (by - ay) * t
        if flat:
            box, spot = (px - tw / 2, py - 15, px + tw / 2, py - 4), (px, py - 6, "middle", False)
        elif along:
            box, spot = (px + 3, py - tw / 2, px + 13, py + tw / 2), (px + 11, py, "middle", True)
        elif px + 10 + tw > W - 12:
            box, spot = (px - 10 - tw, py - 6, px - 10, py + 4), (px - 10, py + 3, "end", False)
        else:
            box, spot = (px + 10, py - 6, px + 10 + tw, py + 4), (px + 10, py + 3, "start", False)
        first = first or (box, spot)
        if _clear(box, taken + avoid):
            break
    else:
        box, spot = first
    taken.append(box)
    x, y, anchor, turned = spot
    mark = caps(cv, text, x, y, th, 8, th["ink"], anchor, .8, what="wire label")
    if turned:
        mark = f'<g transform="rotate(90 {f1(x)} {f1(y)})">' + caps(cv, text, x, y + 3, th, 8, th["ink"], "middle", .8,
                                                                    what="wire label") + "</g>"
    out.append(mark)
    return "".join(out)


def _node(cv, th: dict, b: Box, spec: dict) -> str:
    """A step as a badge: a black tab with its icon, and beside it a card with its name and where it lives,
    outlined in the tab's black so the two read as one."""
    tab = 44
    lab = th["label"]
    x, y, w, h = b.x, b.y, b.w, b.h
    out = [f'<rect x="{f1(x + tab - 1)}" y="{f1(y + .75)}" width="{f1(w - tab + .25)}" height="{f1(h - 1.5)}" '
           f'fill="{c(th["paper"])}" stroke="{c(lab)}" stroke-width="1.5"/>',
           P.rect(x, y, tab, h, lab),
           P.icon(spec.get("icon") or "grid", x + (tab - 20) / 2, y + (h - 20) / 2, 20, P.letters_on(lab), 2)]
    room = w - tab - 24
    title = E.plain(str(spec.get("title", b.key)).upper(), "sans-bold")
    ts = P.fitted(title, "sans-bold", 11, 8, room, .08)
    path = E.plain(str(spec.get("path", "")), "sans")
    base = y + 24 if path else y + h / 2 + cap(ts) / 2
    out.append(say(cv, title, x=x + tab + 12, y=base, size=ts, ls=ts * .08, fill=th["ink"], ground=th["paper"],
                   what="box title"))
    if path:
        ps = P.fitted(path, "sans", 9, 7, room)
        out.append(say(cv, path, x=x + tab + 12, y=y + 41, size=ps, face="sans", fill=th["muted"],
                       ground=th["paper"], what="box place"))
    if spec.get("note"):
        out.append(number(cv, spec["note"], x + w - 8, y - 8))
    return "".join(out)


def _group(cv, th: dict, x0: float, y0: float, x1: float, y1: float, label: str) -> str:
    """A dashed box round the steps that run in one place, its caption set in a gap in its top edge."""
    text = E.plain(str(label).upper(), "sans-bold")
    tw = width(text, "sans-bold", 8, .8)
    cx = (x0 + x1) / 2
    return (f'<rect x="{f1(x0)}" y="{f1(y0)}" width="{f1(x1 - x0)}" height="{f1(y1 - y0)}" rx="6" fill="none" '
            f'stroke="{c(th["muted"])}" stroke-width="1.2" stroke-dasharray="5 4"/>'
            + P.rect(cx - tw / 2 - 8, y0 - 6, tw + 16, 12, th["paper"])
            + caps(cv, text, cx, y0 + cap(8) / 2, th, 8, anchor="middle", what="group caption"))


def _notes(cv, th: dict, items, *, x: float, y: float, right: float, measure: bool = False):
    """Numbered notes in rows, each a number chip and its words in small capitals. With `measure`, only the
    height they take."""
    xx, yy, out = x, y, []
    for num, text in items:
        text = E.plain(str(text).upper(), "sans-bold")
        w = 24 + width(text, "sans-bold", 8.5, .8)
        if xx + w > right and xx > x:
            xx, yy = x, yy + 24
        if not measure:
            out.append(number(cv, num, xx, yy) + caps(cv, text, xx + 24, yy + 8 + cap(8.5) / 2, th, 8.5, th["ink"],
                                                       what="note"))
        xx += w + 24
    if measure:
        return (yy + 16 - y) if items else 0
    return "".join(out)


def schematic(d: dict, th: dict, variant: str = "wide") -> str:
    """Boxes and the wires between them, layered along the wires and snaked across the sheet; a phone
    gets one box to a row, in wire order, with any wire that skips a row carried down a channel at the right."""
    std = P.theme(th)
    narrow = variant == "narrow"
    W = NARROW if narrow else WIDE
    keys = list(d["boxes"])
    edges = [(a, b) for a, b, *_ in d["wires"]]
    boxes = [Box(k) for k in keys]
    by = {b.key: b for b in boxes}
    groups = d.get("groups", {})
    caption = d.get("caption", "")
    top = top_of(W, "schematic", d.get("subject", ""), caption) + (30 if narrow else 34)
    bh = 56
    wires: list[tuple] = []
    if narrow:
        left, bw, gap_y = PAD, 250, 42
        lay = layers(keys, edges)
        order = sorted(keys, key=lambda k: (lay[k], keys.index(k)))
        y, prev = top, None
        for k in order:
            grp = d["boxes"][k].get("in")
            if grp != prev:
                y += (24 if grp else 0) + (10 if prev else 0)
            b = by[k]
            b.x, b.y, b.w, b.h = left, y, bw, bh
            y += bh + gap_y
            prev = grp
        bottom = y - gap_y + (12 if prev else 0)
        row = {k: i for i, k in enumerate(order)}
        channel = 0
        for a, b, *rest in d["wires"]:
            A, B = by[a], by[b]
            label = str(rest[0]) if rest else None
            if row[b] == row[a] + 1:
                wires.append(([(left + 22, A.y + A.h), (left + 22, B.y)], label, False))
            else:
                chx = left + bw + 16 + 9 * channel
                channel += 1
                wires.append(([(A.x + A.w, A.cy), (chx, A.cy), (chx, B.cy), (B.x + B.w, B.cy)], label, True))
    else:
        left, gap_x = 26, 72
        used = snake(boxes, edges, left=left, top=top, width=W - 2 * left, per_row=3, box_w=212, box_h=bh,
                     gap_x=gap_x, gap_y=64)
        # A group round a box in the first row needs the room above it for its caption.
        lift = 18 if any(d["boxes"][b.key].get("in") and b.y == top for b in boxes) else 0
        for b in boxes:
            b.y += lift
        grouped_last = any(d["boxes"][b.key].get("in") and b.y + b.h >= top + lift + used - 1 for b in boxes)
        bottom = top + lift + used + (12 if grouped_last else 0)
        # Wires that would share a channel take lanes in it, 8 px apart, centred on the channel.
        first: dict = {}
        for a, b, *rest in d["wires"]:
            pts = route(by[a], by[b], gap_x, boxes)
            key = None if len(pts) < 4 else (round(pts[1][0]) if pts[1][0] == pts[2][0] else ("y", round(pts[1][1])))
            first.setdefault(key, []).append((a, b, str(rest[0]) if rest else None))
        for key, grouped in first.items():
            n = len(grouped) if key is not None else 1
            for i, (a, b, label) in enumerate(grouped):
                lane = (i - (n - 1) / 2) * 8 if key is not None else 0
                wires.append((route(by[a], by[b], gap_x, boxes, lane), label, False))
    ns = list(d.get("notes", ()))
    notes_h = _notes(None, std, ns, x=PAD, y=0, right=W - PAD, measure=True)
    H = round(bottom + (26 + notes_h if ns else 0) + PAD + 4)
    cv = P.new(W, H, d.get("title", "Schematic"), d.get("desc", ""), f"elements schematic {variant} {th['name']}")
    frame(cv, std, W, H, "schematic", d.get("subject", ""), caption)
    taken = [(b.x, b.y - 8, b.x + b.w + 8, b.y + b.h) for b in boxes]
    for gk, label in groups.items():
        members = [by[k] for k in keys if d["boxes"][k].get("in") == gk]
        if members:
            x0, y0 = min(b.x for b in members) - 12, min(b.y for b in members) - 22
            x1, y1 = max(b.x + b.w for b in members) + 12, max(b.y + b.h for b in members) + 12
            if narrow:
                x0, x1 = 10, W - 10
            cv.add(_group(cv, std, x0, y0, x1, y1, label))
            tw = width(E.plain(str(label).upper(), "sans-bold"), "sans-bold", 8, .8)
            taken += [((x0 + x1) / 2 - tw / 2 - 8, y0 - 6, (x0 + x1) / 2 + tw / 2 + 8, y0 + 6),
                      (x0 - 1, y0, x0 + 1, y1), (x1 - 1, y0, x1 + 1, y1)]
    runs = [[(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])) for a, b in zip(pts, pts[1:])]
            for pts, _, _ in wires]
    marks = []
    for i, (pts, label, along) in enumerate(wires):
        others = [seg for j, segs in enumerate(runs) if j != i for seg in segs]
        marks.append(_wire(cv, std, W, pts, label, taken=taken, avoid=others, along=along))
    cv.add(*marks)
    for k in keys:
        cv.add(_node(cv, std, by[k], d["boxes"][k]))
    if ns:
        cv.add(_notes(cv, std, ns, x=PAD, y=bottom + 26, right=W - PAD))
    return _svg(cv)


# --- instruments --------------------------------------------------------------------------------

def _histogram(cv, th: dict, hist: dict, *, x0: float, x1: float, top: float, base: float, small: bool) -> str:
    """Counts per period as flat bars in the accent, the busiest in tangerine with a star over it; guides as
    dashed hairlines, each count over its bar and each period under it."""
    bars = [(str(label), int(v)) for label, v in hist["bars"]]
    peak = hist.get("peak") or max(10, math.ceil(max(v for _, v in bars) / 10) * 10 + 5)
    ticks = hist.get("ticks") or [round(peak * k / 3) for k in range(4)]
    step = (x1 - x0) / len(bars)
    bw = step * .62
    out = []
    for v in ticks[1:]:
        gy = base - (base - top) * v / peak
        out.append(f'<path d="M{f1(x0 - 4)} {f1(gy)}H{f1(x1 + 4)}" stroke="{c(th["rule"])}" stroke-dasharray="2 3"/>')
        out.append(caps(cv, str(v), x0 - 10, gy + 3, th, 7.5, anchor="end", what="guide"))
    busiest = max(range(len(bars)), key=lambda i: bars[i][1])
    lsz = 7 if small else 7.5
    widest = max(width(label.upper(), "sans-bold", lsz, .5) for label, _ in bars)
    every = 1 if widest <= step - 3 else 2
    for i, (label, v) in enumerate(bars):
        cx = x0 + step * i + step / 2
        hh = (base - top) * v / peak
        colour = "tangerine" if i == busiest and v else P.ACCENT
        if v:
            out.append(P.rect(cx - bw / 2, base - hh, bw, hh, colour))
        out.append(say(cv, str(v), x=cx, y=base - hh - 6, size=8 if small else 9.5, fill=th["ink"],
                       ground=th["paper"], anchor="middle", what="bar value"))
        if i == busiest and v:
            out.append(P.solid("star", cx - 6, base - hh - 29, 12, "tangerine"))
        if (len(bars) - 1 - i) % every == 0:
            out.append(caps(cv, label, cx, base + 15, th, lsz, anchor="middle", ls=.5, what="period"))
    out.append(f'<path d="M{f1(x0 - 4)} {f1(base)}H{f1(x1 + 4)}" stroke="{c(th["ink"])}" stroke-width="1.5"/>')
    return "".join(out)


def _dial(cv, th: dict, dial: dict, cx: float, cy: float, r: float) -> str:
    """A count against its span as a gauge: a half ring in the rule, the part that has passed in the accent,
    the count large in the middle and what it counts from under it."""
    span = max(1, int(dial["span"]))
    value = int(dial["value"])
    frac = min(max(value, 0), span) / span

    def arc(a0: float, a1: float) -> str:
        xa, ya = cx + r * math.cos(a0), cy - r * math.sin(a0)
        xb, yb = cx + r * math.cos(a1), cy - r * math.sin(a1)
        return f"M{f1(xa)} {f1(ya)}A{f1(r)} {f1(r)} 0 0 1 {f1(xb)} {f1(yb)}"

    out = [f'<path d="{arc(math.pi, 0)}" fill="none" stroke="{c(th["rule"])}" stroke-width="12"/>']
    if frac:
        out.append(f'<path d="{arc(math.pi, math.pi * (1 - frac))}" fill="none" stroke="{c(P.ACCENT)}" '
                   f'stroke-width="12"/>')
    major = int(dial.get("major") or max(1, span // 3))
    for v in range(0, span + 1, major):
        a = math.pi * (1 - v / span)
        out.append(caps(cv, str(v), cx + (r + 18) * math.cos(a), cy - (r + 18) * math.sin(a) + 3, th, 7.5,
                        anchor="middle", what="dial tick"))
    out.append(say(cv, str(value), x=cx, y=cy - 8, size=36 if r >= 60 else 30, fill=th["strong"],
                   ground=th["paper"], anchor="middle", what="dial value"))
    if dial.get("sub"):
        out.append(caps(cv, dial["sub"], cx, cy + 20, th, 8.5, th["ink"], "middle", .8, what="dial release"))
    return "".join(out)


def _parts(mat: dict) -> list[tuple[float, str, str]]:
    """Each part of a whole as (its share, its colour, its legend's words); the part called OTHER is gray."""
    parts = [(str(k), float(v)) for k, v in mat["parts"][:5]]
    total = sum(v for _, v in parts) or 1
    return [(v / total, "gray" if name.upper() == "OTHER" else PARTS[i % len(PARTS)],
             E.plain(f"{name} {round(100 * v / total)}%".upper(), "sans-bold")) for i, (name, v) in enumerate(parts)]


def _legend(parts: list, x: float, y: float, w: float) -> list[tuple[float, float]]:
    """Where each part's legend goes, (x, baseline), in rows no wider than `w` from the baseline `y`."""
    lx, ly, out = x, y, []
    for _, _, text in parts:
        tw = width(text, "sans-bold", 8, .8)
        if lx + 14 + tw > x + w and lx > x:
            lx, ly = x, ly + 16
        out.append((lx, ly))
        lx += 14 + tw + 18
    return out


def _materials(cv, th: dict, mat: dict, x: float, y: float, w: float, h: float = 18) -> str:
    """A whole as a bar of flat parts, and under it a legend of each part's swatch, name and share."""
    parts = _parts(mat)
    out, xx = [], x
    for share, colour, _ in parts:
        out.append(P.rect(xx, y, w * share, h, colour))
        xx += w * share
    for (_, colour, text), (lx, ly) in zip(parts, _legend(parts, x, y + h + 18, w)):
        out.append(P.rect(lx, ly - 8, 9, 9, colour) + caps(cv, text, lx + 14, ly, th, 8, th["ink"], what="material"))
    return "".join(out)


def _counters(counters: list, th: dict, size: float) -> list[Chip]:
    return [Chip(str(label), f"{int(value):,}", size=size, lab=th["label"], msg=COUNTERS[i % len(COUNTERS)])
            for i, (label, value) in enumerate(counters[:3])]


def instruments(d: dict, th: dict, variant: str = "wide") -> str:
    """Counts per week, a gauge, a bar of materials and a row of counters: a project's vitals."""
    std = P.theme(th)
    hist, dial, mat = d["histogram"], d["dial"], d["materials"]
    total = sum(int(v) for _, v in hist["bars"])
    counters = list(d.get("counters", ()))
    caption = d.get("caption", "")
    if variant == "narrow":
        W = NARROW
        top = top_of(W, "instruments", d.get("subject", ""), caption)
        y = top + 28
        hist_y = y
        y += 26 + 96 + 40
        dial_y = y
        y += 150
        mat_y = y
        ly = max(b for _, b in _legend(_parts(mat), PAD, mat_y + 12 + 18 + 18, W - 2 * PAD))
        count_y = ly + 26
        chips = next(cs for cs in (_counters(counters, std, s) for s in (10, 9.5, 9, 8.5, 8))
                     if P.row_width(cs, 6) <= W - 2 * PAD or cs[0].size == 8) if counters else []
        H = round((count_y + 12 + chips[0].h if chips else ly) + PAD)
        cv = P.new(W, H, d.get("title", "Instruments"), d.get("desc", ""), f"elements instruments narrow {th['name']}")
        frame(cv, std, W, H, "instruments", d.get("subject", ""), caption)
        cv.add(heading(cv, hist["label"], PAD, hist_y, std))
        cv.add(caps(cv, f"{total:,} {hist.get('sum', '')}".strip(), W - PAD, hist_y, std, 8.5, std["ink"], "end",
                    what="total"))
        cv.add(_histogram(cv, std, hist, x0=46, x1=W - PAD, top=hist_y + 26, base=hist_y + 122, small=True))
        cv.add(P.rule(PAD, W - PAD, dial_y - 12, std))
        cv.add(heading(cv, dial["label"], W / 2, dial_y + 8, std, "middle"))
        cv.add(_dial(cv, std, dial, W / 2, dial_y + 104, 58))
        cv.add(P.rule(PAD, W - PAD, mat_y - 16, std))
        cv.add(heading(cv, mat["label"], PAD, mat_y, std))
        cv.add(caps(cv, mat.get("total", ""), W - PAD, mat_y, std, 9, std["ink"], "end", .9, what="total bytes"))
        cv.add(_materials(cv, std, mat, PAD, mat_y + 12, W - 2 * PAD))
        if chips:
            cv.add(heading(cv, "COUNTED", PAD, count_y, std))
            xx = PAD
            for ch in chips:
                cv.add(ch.draw(cv, xx, count_y + 12, "counter"))
                xx += ch.w + 6
        return _svg(cv)
    W = WIDE
    top = top_of(W, "instruments", d.get("subject", ""), caption)
    y0 = top + 38
    chips = next(cs for cs in (_counters(counters, std, s) for s in (10, 9.5, 9, 8.5, 8))
                 if P.row_width(cs, 6) <= W - 486 - PAD or cs[0].size == 8) if counters else []
    ly = max(b for _, b in _legend(_parts(mat), 44, y0 + 208 + 18 + 18, 390))
    H = round(max(ly, y0 + 212 + (chips[0].h if chips else 0)) + PAD + 2)
    cv = P.new(W, H, d.get("title", "Instruments"), d.get("desc", ""), f"elements instruments wide {th['name']}")
    frame(cv, std, W, H, "instruments", d.get("subject", ""), caption)
    cv.add(heading(cv, hist["label"], 44, y0, std))
    unit = str(hist.get("sum", "")).upper()
    uw = width(unit, "sans-bold", 8.5, .8) if unit else 0
    cv.add(say(cv, f"{total:,}", x=548 - uw - (6 if unit else 0), y=y0 + 2, size=15, fill=std["strong"],
               ground=std["paper"], anchor="end", what="total"))
    if unit:
        cv.add(caps(cv, unit, 548 - uw, y0, std, 8.5, what="total label"))
    cv.add(_histogram(cv, std, hist, x0=70, x1=548, top=y0 + 30, base=y0 + 134, small=False))
    cv.add(f'<path d="M588 {f1(y0 - 8)}V{f1(y0 + 158)}M20 {f1(y0 + 170)}H810" stroke="{c(std["rule"])}"/>')
    cv.add(heading(cv, dial["label"], 700, y0, std, "middle"))
    cv.add(_dial(cv, std, dial, 700, y0 + 106, 62))
    cv.add(heading(cv, mat["label"], 44, y0 + 196, std))
    cv.add(caps(cv, mat.get("total", ""), 434, y0 + 196, std, 9, std["ink"], "end", .9, what="total bytes"))
    cv.add(_materials(cv, std, mat, 44, y0 + 208, 390))
    cv.add(f'<path d="M462 {f1(y0 + 184)}V{f1(H - 20)}" stroke="{c(std["rule"])}"/>')
    if chips:
        cv.add(heading(cv, "COUNTED", 486, y0 + 196, std))
        xx = 486
        for ch in chips:
            cv.add(ch.draw(cv, xx, y0 + 212, "counter"))
            xx += ch.w + 6
    return _svg(cv)


# --- milestones ---------------------------------------------------------------------------------

def _events(d: dict) -> tuple[list, dt.date, dt.date, dt.date]:
    events = sorted(d.get("events", ()), key=lambda e: E._date(e["date"]))
    today = E._date(d.get("today") or dt.date.today())
    if not events:
        events = [{"date": str(today), "tag": "NO RELEASE YET", "major": True}]
    start = E._date(d["start"]) if d.get("start") else E._date(events[0]["date"]) - dt.timedelta(days=14)
    end = (E._date(d["end"]) if d.get("end") else
           max(E._date(events[-1]["date"]), today) + dt.timedelta(days=21))
    return events, today, start, end


def _release(e: dict, th: dict, size: float) -> Chip:
    """A release as a badge: its tag beside the tag icon, forest for a major version, black for the rest."""
    return Chip(E.plain(str(e["tag"]), "sans-bold"), "", icon="tag", size=size,
                lab="forest" if e.get("big") else th["label"])


def _planned(cv, th: dict, chip: Chip, x: float, y: float) -> str:
    """A release not made yet: the badge drawn in a dashed outline, in the ink, on the paper."""
    ink = th["ink"]
    return (f'<rect x="{f1(x + .6)}" y="{f1(y + .6)}" width="{f1(chip.w - 1.2)}" height="{f1(chip.h - 1.2)}" '
            f'fill="{c(th["paper"])}" stroke="{c(th["muted"])}" stroke-width="1.2" stroke-dasharray="3 2"/>'
            + P.icon("tag", x + chip.pad, y + (chip.h - chip.isz) / 2, chip.isz, ink, 2.1)
            + say(cv, chip.label, x=x + chip.pad + chip.isz + chip.gap, y=y + chip.h / 2 + cap(chip.size) / 2,
                  size=chip.size, ls=chip.ls, fill=ink, ground=th["paper"], what="planned release"))


def _level(spans: list, x: float, w: float, h: float, gap: float) -> float:
    """How far from the line a new block sits: clear of every block it overlaps sideways."""
    lift = 0.0
    for px, pw, plift, ph in spans:
        if abs(x - px) < (w + pw) / 2 + 8:
            lift = max(lift, plift + ph + gap)
    spans.append((x, w, lift, h))
    return lift


def milestones(d: dict, th: dict, variant: str = "wide") -> str:
    """A project's history on a time line: its releases as badges on stems above the line, patches as beads
    on it, what is planned in a dashed outline, and today marked under it."""
    std = P.theme(th)
    events, today, start, end = _events(d)
    caption = d.get("caption", "")
    ink, muted = c(std["ink"]), c(std["muted"])
    if variant == "narrow":
        W = NARROW
        rows = ([e for e in events if e.get("major", True) or e.get("made") or e.get("next")]
                or [e for e in events if not e.get("next")][-1:] or events[-1:])
        top = top_of(W, "milestones", d.get("subject", ""), caption) + 30
        lx = 118
        ys, y = [], top
        for e in rows:
            ys.append(y)
            y += 34 + 11 * len(e.get("above", ()))
        H = round(y + PAD - 12)
        cv = P.new(W, H, d.get("title", "Milestones"), d.get("desc", ""), f"elements milestones narrow {th['name']}")
        frame(cv, std, W, H, "milestones", d.get("subject", ""), caption)
        past = [i for i, e in enumerate(rows) if E._date(e["date"]) <= today and not e.get("next")]
        last = ys[past[-1]] + 10 if past else ys[0] + 10
        cv.add(f'<path d="M{lx} {f1(ys[0] + 10)}V{f1(last)}" stroke="{ink}" stroke-width="2.5"/>')
        if ys[-1] + 10 > last:
            cv.add(f'<path d="M{lx} {f1(last)}V{f1(ys[-1] + 10)}" stroke="{muted}" stroke-width="2" '
                   f'stroke-dasharray="4 4"/>')
        for e, yy in zip(rows, ys):
            yy += 10
            day = E._date(e["date"])
            cv.add(caps(cv, e.get("when") or E._when(day, True), lx - 16, yy + 3, std, 8, anchor="end", what="date"))
            if e.get("made"):
                cv.add(f'<circle cx="{lx}" cy="{f1(yy)}" r="5" fill="{c(std["paper"])}" stroke="{ink}" '
                       f'stroke-width="1.6"/>')
                for j, text in enumerate(e.get("above") or [e["tag"]]):
                    cv.add(caps(cv, text, lx + 16, yy + 3 + 11 * j, std, 8, std["ink"], what="created"))
                continue
            fill = c(std["paper"] if e.get("next") else P.ACCENT)
            cv.add(f'<circle cx="{lx}" cy="{f1(yy)}" r="5" fill="{fill}" stroke="{muted if e.get("next") else ink}" '
                   f'stroke-width="1.6"/>')
            chip = _release(e, std, 8.5)
            cv.add(_planned(cv, std, chip, lx + 14, yy - chip.h / 2) if e.get("next") else
                   chip.draw(cv, lx + 14, yy - chip.h / 2, "release"))
            for j, text in enumerate(e.get("above", ())):
                cv.add(caps(cv, text, lx + 16, yy + chip.h / 2 + 11 + j * 11, std, 7.5, ls=.7, what="release note"))
        return _svg(cv)

    W = WIDE
    x0, x1 = 34, W - 34
    scale = timeline(start, end, [E._date(e["date"]) for e in events] + [today], x0, x1)
    X = scale.x
    # The blocks above the line, laid out first so the line sits under the tallest of them.
    spans: list = []
    blocks = []
    for e in events:
        if not e.get("made") and not e.get("major", True):
            continue
        x = X(E._date(e["date"]))
        notes = [E.plain(str(t).upper(), "sans-bold") for t in (e.get("above") or ([e["tag"]] if e.get("made") else []))]
        chip = None if e.get("made") else _release(e, std, 9.5 if e.get("big") else 8.5)
        w = max([chip.w if chip else 0] + [width(t, "sans-bold", 7.5, .7) for t in notes])
        h = (chip.h if chip else 0) + 11 * len(notes) + (4 if chip and notes else 0)
        bx = min(max(x, PAD + w / 2), W - PAD - w / 2)
        lift = _level(spans, bx, w, h, 10)
        blocks.append((e, x, bx, chip, notes, h, lift))
    up = max((lift + h for *_, h, lift in blocks), default=0)
    top = top_of(W, "milestones", d.get("subject", ""), caption)
    axis = round(top + 24 + up + 18)
    tchip = Chip("today", E._when(today, False), size=8, lab=std["label"], msg=P.ACCENT)
    H = round(axis + 36 + tchip.h + PAD)
    cv = P.new(W, H, d.get("title", "Milestones"), d.get("desc", ""), f"elements milestones wide {th['name']}")
    frame(cv, std, W, H, "milestones", d.get("subject", ""), caption)
    xt = min(max(X(today), x0), x1)
    cv.add(f'<path d="M{x0} {axis}H{f1(xt)}" stroke="{ink}" stroke-width="2.5"/>')
    if xt < x1:
        cv.add(f'<path d="M{f1(xt)} {axis}H{x1}" stroke="{muted}" stroke-width="2" stroke-dasharray="4 4"/>')
    for bx0, bx1, days in scale.breaks:
        mid = (bx0 + bx1) / 2
        cv.add(P.rect(bx0 + 4, axis - 6, bx1 - bx0 - 8, 12, std["paper"])
               + f'<path d="M{f1(mid - 8)} {axis + 5}l5 -10M{f1(mid + 3)} {axis + 5}l5 -10" stroke="{muted}" '
                 f'stroke-width="1.5"/>'
               + caps(cv, f"{days} DAYS", mid, axis + 24, std, 7, anchor="middle", what="break"))
    tw = tchip.w / 2 + 6
    placed = [(xt - tw, xt + tw)]
    for d0, d1, _, _ in scale.segments:
        m = dt.date(d0.year, d0.month, 1)
        while m <= d1:
            if m >= d0:
                x = X(m)
                big = m.month in (1, 4, 7, 10)
                cv.add(f'<path d="M{f1(x)} {axis + 3}V{axis + (10 if big else 6)}" stroke="{muted}"/>')
                if big:
                    label = m.strftime("%b").upper() + (f" {m.year}" if m.month == 1 else "")
                    half = width(label, "sans-bold", 7.5, .8) / 2 + 4
                    if all(x + half < a or x - half > b for a, b in placed):
                        placed.append((x - half, x + half))
                        cv.add(caps(cv, label, x, axis + 24, std, 7.5, anchor="middle", what="month"))
            m = dt.date(m.year + (m.month == 12), m.month % 12 + 1, 1)
    for e in events:
        if not e.get("made") and not e.get("major", True):
            cv.add(f'<circle cx="{f1(X(E._date(e["date"])))}" cy="{axis}" r="3.6" fill="{c(std["paper"])}" '
                   f'stroke="{ink}" stroke-width="1.6"/>')
    for e, x, bx, chip, notes, h, lift in blocks:
        bottom = axis - 18 - lift
        blk = bottom - h
        planned = e.get("next")
        stem = f' stroke-dasharray="3 3"' if planned else ""
        cv.add(f'<path d="M{f1(x)} {f1(bottom + 4)}V{axis - 5}" stroke="{muted if planned or e.get("made") else ink}" '
               f'stroke-width="1.2"{stem}/>')
        if e.get("made"):
            cv.add(f'<circle cx="{f1(x)}" cy="{axis}" r="5" fill="{c(std["paper"])}" stroke="{ink}" stroke-width="1.6"/>')
        else:
            dot = c(std["paper"] if planned else P.ACCENT)
            cv.add(f'<circle cx="{f1(x)}" cy="{axis}" r="{6 if e.get("big") else 5}" fill="{dot}" '
                   f'stroke="{muted if planned else ink}" stroke-width="1.6"/>')
        y = blk
        if chip:
            cv.add(_planned(cv, std, chip, bx - chip.w / 2, y) if planned else chip.draw(cv, bx - chip.w / 2, y, "release"))
            y += chip.h + 4
        for j, text in enumerate(notes):
            cv.add(caps(cv, text, bx, y + 7 + 11 * j, std, 7.5, std["ink"] if e.get("made") else std["muted"],
                        "middle", .7, what="release note"))
    cv.add(f'<path d="M{f1(xt)} {axis + 4}V{axis + 36}" stroke="{c(P.ACCENT)}" stroke-width="1.5"/>')
    tx = min(max(xt - tchip.w / 2, PAD), W - PAD - tchip.w)
    cv.add(tchip.draw(cv, tx, axis + 36, "today"))
    return _svg(cv)


# --- roster -------------------------------------------------------------------------------------

def _avatar(cv, th: dict, cx: float, cy: float, r: float, p: dict, i: int) -> str:
    """A person's medallion: their initials on a colour of their own; a bot's icon on slate."""
    colour = PEOPLE[i % len(PEOPLE)] if p.get("initials") and not p.get("icon") else "slate"
    on = P.letters_on(colour)
    out = [f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="{c(colour)}"/>']
    if p.get("initials") and not p.get("icon"):
        size = r * .72
        out.append(say(cv, str(p["initials"]).upper()[:3], x=cx, y=cy + cap(size) / 2, size=size, ls=.8, fill=on,
                       ground=colour, anchor="middle", what="initials"))
    else:
        s = r * 1.15
        out.append(P.icon(p.get("icon") or "package", cx - s / 2, cy - s / 2, s, on, 2))
    return "".join(out)


def roster_height(d: dict) -> float:
    """How tall the half-page roster is on its own: two people to a row of 80 under the band."""
    return top_of(HALF, "roster", d.get("subject", ""), "") + 18 + math.ceil(len(d["people"]) / 2) * 80 + 6


def roster(d: dict, th: dict, variant: str = "wide", height: float | None = None) -> str:
    """The people who made it, each with a medallion, their count and its share of the most."""
    std = P.theme(th)
    people = d["people"]
    most = max(int(p["n"]) for p in people) or 1
    if variant != "wide":
        W = HALF
        natural = roster_height(d)
        H = round(max(natural, height or 0))
        pad = (H - natural) / 2
        cv = P.new(W, H, d.get("title", "Contributors"), d.get("desc", ""), f"elements roster narrow {th['name']}")
        frame(cv, std, W, H, "roster", d.get("subject", ""))
        top = top_of(W, "roster", d.get("subject", ""), "") + 18 + pad
        colw = (W - 2 * PAD) / 2
        rows = math.ceil(len(people) / 2)
        if len(people) > 1:
            cv.add(f'<path d="M{f1(W / 2)} {f1(top - 4)}V{f1(top + rows * 80 - 16)}" stroke="{c(std["rule"])}"/>')
        for r in range(1, rows):
            cv.add(P.rule(PAD, W - PAD, top + r * 80 - 10, std))
        for i, p in enumerate(people):
            row, col = divmod(i, 2)
            x, y = PAD + col * (colw + (6 if col else 0)), top + row * 80
            cv.add(_avatar(cv, std, x + 18, y + 20, 17, p, i))
            room = colw - 52
            name = E.plain(str(p["name"]).upper(), "sans-bold")
            ns = P.fitted(name, "sans-bold", 9.5, 7, room, .07)
            cv.add(say(cv, name, x=x + 44, y=y + 14, size=ns, ls=ns * .07, fill=std["ink"], ground=std["paper"],
                       what="name"))
            handle = E.plain(str(p.get("handle", "")).upper(), "sans-bold")
            hs = P.fitted(handle, "sans-bold", 7.5, 6, room, .08)
            cv.add(caps(cv, handle, x + 44, y + 27, std, hs, ls=hs * .08, what="handle"))
            count = f"{int(p['n']):,}"
            cw = width(count, "sans-bold", 14)
            cv.add(say(cv, count, x=x + 44, y=y + 47, size=14, fill=std["strong"], ground=std["paper"],
                       what="commits")
                   + caps(cv, "COMMITS", x + 48 + cw, y + 47, std, 7.5, what="commits label"))
            bar = room - 4
            cv.add(P.rect(x + 44, y + 54, bar, 5, std["rule"])
                   + P.rect(x + 44, y + 54, max(3, bar * int(p["n"]) / most), 5, P.ACCENT))
        return _svg(cv)
    W = WIDE
    top = top_of(W, "roster", d.get("subject", ""), d.get("caption", "")) + 22
    H = round(top + 142)
    cv = P.new(W, H, d.get("title", "Contributors"), d.get("desc", ""), f"elements roster wide {th['name']}")
    frame(cv, std, W, H, "roster", d.get("subject", ""), d.get("caption", ""))
    colw = (W - 2 * PAD) / len(people)
    for i, p in enumerate(people):
        x = PAD + colw * i
        if i:
            cv.add(f'<path d="M{f1(x - 4)} {f1(top - 4)}V{f1(H - PAD)}" stroke="{c(std["rule"])}"/>')
        cv.add(_avatar(cv, std, x + 26, top + 24, 22, p, i))
        tx = x + 58
        room = colw - 66
        name = E.plain(str(p["name"]).upper(), "sans-bold")
        ns = P.fitted(name, "sans-bold", 11, 7.5, room, .07)
        cv.add(say(cv, name, x=tx, y=top + 16, size=ns, ls=ns * .07, fill=std["ink"], ground=std["paper"], what="name"))
        handle = E.plain(str(p.get("handle", "")).upper(), "sans-bold")
        hs = P.fitted(handle, "sans-bold", 7.5, 6, room, .08)
        cv.add(caps(cv, handle, tx, top + 30, std, hs, ls=hs * .08, what="handle"))
        count = f"{int(p['n']):,}"
        cw = width(count, "sans-bold", 18)
        cv.add(say(cv, count, x=tx, y=top + 58, size=18, fill=std["strong"], ground=std["paper"], what="commits")
               + caps(cv, "COMMITS", tx + cw + 5, top + 58, std, 7.5, what="commits label"))
        cv.add(P.rect(tx, top + 66, room, 6, std["rule"])
               + P.rect(tx, top + 66, max(3, room * int(p["n"]) / most), 6, P.ACCENT))
        chips = [Chip("first", str(p.get("first", "")), size=7.5, lab=std["label"], msg="slate"),
                 Chip("last", str(p.get("last", "")), size=7.5, lab=std["label"], msg="slate")]
        if chips[0].w + 6 + chips[1].w <= colw - 16:
            cv.add(chips[0].draw(cv, x + 4, top + 92, "first"), chips[1].draw(cv, x + 10 + chips[0].w, top + 92, "last"))
        else:
            cv.add(chips[0].draw(cv, x + 4, top + 84, "first"), chips[1].draw(cv, x + 4, top + 108, "last"))
    return _svg(cv)


# --- certificate --------------------------------------------------------------------------------

def _met(d: dict) -> tuple[int, int]:
    rows = d["checks"]
    return sum(1 for row in rows if (row[2] if len(row) > 2 else True)), len(rows)


def _seal(cv, th: dict, cx: float, cy: float, r: float, d: dict) -> str:
    """The certificate's seal: a ring of the accent round a check, or a cross when a check is not met, the
    name, and how many checks are met of how many."""
    met, n = _met(d)
    passed = met == n
    acc = c(P.ACCENT)
    out = [f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="{acc}"/>'
           f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r - 7)}" fill="{c(th["paper"])}"/>'
           f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r - 11)}" fill="none" stroke="{acc}" stroke-dasharray="2 3"/>']
    s = r * .56
    out.append(P.icon("check" if passed else "cross", cx - s / 2, cy - r * .66, s, ok(th, passed), 3))
    name = E.plain(str(d.get("name", "")).upper(), "sans-bold")
    ns = P.fitted(name, "sans-bold", 11, 6.5, (r - 14) * 1.75, .08)
    out.append(say(cv, name, x=cx, y=cy + r * .1, size=ns, ls=ns * .08, fill=th["strong"], ground=th["paper"],
                   anchor="middle", what="seal name"))
    out.append(caps(cv, f"{met} OF {n} MET", cx, cy + r * .1 + 12, th, 7, anchor="middle", ls=.6, what="seal count"))
    return "".join(out)


def _wrapped(text: str, size: float, room: float) -> list[str]:
    words, rows, cur = E.plain(str(text).upper(), "sans-bold").split(), [], ""
    for word in words:
        cand = (cur + " " + word).strip()
        if cur and width(cand, "sans-bold", size, .8) > room:
            rows.append(cur)
            cur = word
        else:
            cur = cand
    return rows + ([cur] if cur else [])


def certificate_height(d: dict) -> float:
    """How tall the half-page certificate is on its own: room for the seal, or 32 a check."""
    top = top_of(HALF, "certificate", d.get("subject", ""), "")
    heading = len(_wrapped(d.get("ring_top", ""), 8, HALF - 150 - PAD)) * 11
    return max(top + 196, top + 20 + heading + 10 + 32 * len(d["checks"]) + 6)


def certificate(d: dict, th: dict, variant: str = "wide", height: float | None = None) -> str:
    """The checks a repository passes, each with its evidence, beside a seal counting them."""
    std = P.theme(th)
    checks = d["checks"]
    if variant != "wide":
        W, x0 = HALF, 150
        natural = certificate_height(d)
        H = round(max(natural, height or 0))
        cv = P.new(W, H, d.get("title", "Conformance"), d.get("desc", ""), f"elements certificate narrow {th['name']}")
        frame(cv, std, W, H, "certificate", d.get("subject", ""))
        top = top_of(W, "certificate", d.get("subject", ""), "")
        below = _wrapped(d.get("ring_bottom", ""), 7, x0 - 2 * PAD)
        cy = top + (H - top) / 2 - 6 * len(below)
        cv.add(_seal(cv, std, PAD + (x0 - PAD) / 2 - 4, cy, 48, d))
        for j, text in enumerate(below):
            cv.add(caps(cv, text, PAD + (x0 - PAD) / 2 - 4, cy + 66 + 11 * j, std, 7, anchor="middle", what="verified"))
        cv.add(f'<path d="M{x0} {top + 16}V{H - PAD}" stroke="{c(std["rule"])}"/>')
        head = _wrapped(d.get("ring_top", ""), 8, W - x0 - 14 - PAD)
        rows_h = len(head) * 11 + (10 if head else 0) + 32 * len(checks) - 8
        y = top + (H - top - rows_h) / 2 + 4
        for text in head:
            cv.add(caps(cv, text, x0 + 14, y + 4, std, 8, what="standard"))
            y += 11
        y += 10 if head else 0
        for label, evidence, *met in checks:
            passed = met[0] if met else True
            cv.add(P.icon("check-circle" if passed else "cross", x0 + 14, y - 2, 16, ok(std, passed), 2.2))
            text = E.plain(str(label).upper(), "sans-bold")
            ts = P.fitted(text, "sans-bold", 8.5, 6.5, W - x0 - 38 - PAD, .07)
            cv.add(say(cv, text, x=x0 + 38, y=y + 9, size=ts, ls=ts * .07, fill=std["ink"], ground=std["paper"],
                       what="check"))
            ev = E.plain(str(evidence), "sans")
            es = P.fitted(ev, "sans", 8, 6.5, W - x0 - 38 - PAD)
            cv.add(say(cv, ev, x=x0 + 38, y=y + 21, size=es, face="sans", fill=std["muted"], ground=std["paper"],
                       what="evidence"))
            y += 32
        return _svg(cv)
    W, x0 = WIDE, 236
    top = top_of(W, "certificate", d.get("subject", ""), d.get("caption", ""))
    head = _wrapped(d.get("ring_top", ""), 9, W - x0 - 24 - PAD)
    below = _wrapped(d.get("ring_bottom", ""), 7.5, x0 - 2 * PAD)
    H = round(max(top + 214 + 11 * max(0, len(below) - 1), top + 26 + len(head) * 12 + 12 + 30 * len(checks) + PAD))
    cv = P.new(W, H, d.get("title", "Conformance"), d.get("desc", ""), f"elements certificate wide {th['name']}")
    frame(cv, std, W, H, "certificate", d.get("subject", ""), d.get("caption", ""))
    cx = x0 / 2 + 4
    cy = top + (H - top) / 2 - 8 - 5.5 * len(below)
    cv.add(_seal(cv, std, cx, cy, 58, d))
    for j, text in enumerate(below):
        cv.add(caps(cv, text, cx, cy + 78 + 11 * j, std, 7.5, anchor="middle", what="verified"))
    cv.add(f'<path d="M{x0} {top + 18}V{H - PAD}" stroke="{c(std["rule"])}"/>')
    y = top + 30
    for text in head:
        cv.add(caps(cv, text, x0 + 24, y, std, 9, ls=.9, what="standard"))
        y += 12
    y += 14
    for i, (label, evidence, *met) in enumerate(checks):
        passed = met[0] if met else True
        cv.add(P.icon("check-circle" if passed else "cross", x0 + 24, y - 12, 16, ok(std, passed), 2.2))
        cv.add(say(cv, E.plain(str(label).upper(), "sans-bold"), x=x0 + 48, y=y, size=9.5, ls=.8, fill=std["ink"],
                   ground=std["paper"], what="check"))
        ev = E.plain(str(evidence), "sans")
        cv.add(say(cv, ev, x=W - PAD - 4, y=y, size=P.fitted(ev, "sans", 9.5, 7, 240), face="sans", fill=std["muted"],
                   ground=std["paper"], anchor="end", what="evidence"))
        if i < len(checks) - 1:
            cv.add(P.rule(x0 + 24, W - PAD - 4, y + 12, std))
        y += 30
    return _svg(cv)


# --- placard ------------------------------------------------------------------------------------

def placard(d: dict, th: dict, variant: str = "wide") -> str:
    """A card that links to another repository, itself a badge that goes somewhere: a band with the owner over
    the name and an arrow in the accent, the description, and the facts as badges along the foot."""
    std = P.theme(th)
    W, H, bh, aw = HALF, 172, 48, 48
    owner = E.plain(str(d["owner"]).upper(), "sans-bold")
    name = E.plain(str(d["name"]).upper(), "sans-bold")
    cv = P.new(W, H, d.get("title") or f"{d['owner']}/{d['name']}", d["desc"], f"elements placard wide {th['name']}")
    cid = P.card(cv, std, W, H)
    lab = std["label"]
    on = P.letters_on(lab)
    room = W - aw - PAD - 30 - 12
    ns = P.fitted(name, "sans-bold", 15, 9, room, .1)
    osz = P.fitted(owner, "sans-bold", 8, 6, room, .1)
    arrow = P.letters_on(P.ACCENT)
    band = (P.rect(0, 0, W - aw, bh, lab) + P.rect(W - aw, 0, aw, bh, P.ACCENT)
            + P.icon(d.get("icon") or "book", PAD, (bh - 18) / 2, 18, on, 2.1)
            + say(cv, owner, x=PAD + 30, y=19, size=osz, ls=osz * .1, fill="ash", ground=lab, what="owner")
            + say(cv, name, x=PAD + 30, y=37, size=ns, ls=ns * .1, fill=on, ground=lab, what="name")
            + f'<g transform="rotate(-45 {f1(W - aw / 2)} {f1(bh / 2)})">'
            + P.icon("arrow", W - aw / 2 - 8, bh / 2 - 8, 16, arrow, 2.3) + "</g>")
    cv.add(f'<g clip-path="url(#{cid})">{band}</g>')
    size = 9.0
    while True:   # the facts on one row: the badges shrink a quarter point at a time until they fit
        cells = [Chip(str(a), str(b), size=size, lab=lab, msg=P.figure(str(a))[1]) for a, b in list(d["cells"])[:3]]
        if P.row_width(cells, 6) <= W - 2 * PAD or size <= 7:
            break
        size -= .25
    lines = P.rows(cells, W - 2 * PAD, 6)
    foot = H - PAD - (len(lines) * (cells[0].h + 6) - 6 if cells else 0)
    room = foot - bh - 16 - 12
    dsz, rows = 12.5, []
    while dsz >= 10:
        dsz, rows = P.prose(E.plain(str(d["desc"]), "sans"), dsz, W - 2 * PAD, rows=3)
        if dsz * .76 + dsz * 1.4 * (len(rows) - 1) + dsz * .3 <= room or dsz <= 10:
            break
        dsz -= .5
    cv.add(P.lines(cv, rows, std, x=PAD, top=bh + 16, size=dsz, lead=dsz * 1.4, what="description"))
    y = foot
    for line in lines:
        xx = PAD
        for ch in line:
            cv.add(ch.draw(cv, xx, y, "cell"))
            xx += ch.w + 6
        y += line[0].h + 6
    return _svg(cv)


# --- the registry -------------------------------------------------------------------------------

KINDS = {"schematic": schematic, "instruments": instruments, "milestones": milestones, "roster": roster,
         "certificate": certificate, "placard": placard}
HALF_HEIGHTS = {"roster": roster_height, "certificate": certificate_height}


def half_height(elements: dict[str, dict]) -> float | None:
    """The one height every half-page element on a page is drawn at, as `elements.draw.half_height` finds it."""
    heights = [HALF_HEIGHTS[d["kind"]](d) for d in elements.values() if E.variants(d["kind"], d) == ("half",)]
    return max(heights) if heights else None


def draw(kind: str, d: dict, theme: str, variant: str, height: float | None = None) -> str:
    """One finished file in the standard theme, checked against the lint and its kind's budget."""
    fn = KINDS[kind]
    d = E.describe(kind, d)
    th = THEMES[theme]
    svg = fn(d, th, "narrow", height=height) if variant == "half" else fn(d, th, variant)
    problems = lint(svg, budget=BUDGET[E.KINDS[kind][2]])
    if problems:
        raise ValueError(f"{kind} {variant} {theme}: " + "; ".join(problems))
    return svg
