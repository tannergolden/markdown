# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The standard theme's banners: the masthead, a badge the width of the page.

A header opens with a band in the label's black carrying the title plate's
icon and the title in bold capitals, and at its right end a block of the
accent carrying the release, or a person's account, the way a badge's
message closes it; over the title, inside the band, a kicker names the
repository's path or a person's site. Under the band run the tagline and
the description, then the motto and any further notes as outlined badges,
and along the foot, under a hairline, the figures GitHub gives, each as the
badge a README would carry for it.

A footer ends in the same band: the closing words in the black and the way
back up in the accent. Each link under it is a badge that goes somewhere:
an icon and a word in the black, and an arrow in the accent.

  H1 Sheet        everything centred, the badges in centred rows
  H2 Section      the default: set from the left, the badges spread along the foot
  H3 Strip        a slimmer band and smaller badges
  F1 Title block  the badges for who built it, its licence and its last change, over the band
  F2 Scale bar    the band alone, the attribution in small capitals under the closing words

A field a header or footer switches off is neither drawn nor spoken, and
everything drawn is in the alt text, as in every other theme.
"""
from __future__ import annotations

from ..banners.content import Footer, Header
from ..banners.layout import NARROW, WIDE
from ..lettering import cap_height, width, wrap
from . import pieces as P
from .pieces import Action, Chip, Outline, rise, wipe

# What the band's accent block carries, the first found: a repository's release, a person's account.
BLOCK = ("RELEASE", "ACCOUNT")
# What the kicker over the title carries, the first found, and its icon: a repository's path, a person's site.
KICKER = {"PROJECT": "book", "SITE": "globe"}
# The icon on a link under the footer, by its label; any other link carries the link icon.
LINKS = {"issues": "target", "pull requests": "branch", "releases": "tag", "actions": "play", "docs": "book",
         "documentation": "book", "wiki": "book", "discussions": "chat", "security": "shield", "packages": "package",
         "projects": "grid", "repositories": "book", "website": "globe", "site": "globe", "sponsor": "heart",
         "changelog": "sync", "contributing": "users"}
# The capitals every small label is set in: the kicker's size and its spacing, in ems.
KICK, KICK_LS = 9.5, 1.3 / 9.5


def heart(th: dict) -> str:
    """The heart in "built with": crimson on the day's black label, rose on the night's charcoal."""
    return "rose" if th["dark"] else "crimson"


def parts(h: Header, kicker: bool = True) -> tuple[str, tuple | None, list]:
    """(the accent block's message, the kicker as (text, icon) or None, the figures left for the badges)."""
    msg, kick, rest = "", None, []
    for label, value in h.shown_figures:
        if not msg and label in BLOCK:
            msg = value
        elif kicker and kick is None and label in KICKER:
            kick = (value.replace("/", " / ").upper(), KICKER[label])
        else:
            rest.append((label, value))
    return msg, kick, rest


def plate_icon(h: Header) -> str:
    return "users" if any(label == "ACCOUNT" for label, _ in h.shown_figures) else "book"


def figures(rest: list, th: dict, size: float) -> list[Chip]:
    out = []
    for label, value in rest:
        glyph, colour = P.figure(label)
        out.append(Chip(label, value, icon=glyph, size=size, lab=th["label"], msg=colour))
    return out


def said(h: Header, size: float) -> list[Outline]:
    """The motto and the general notes after it, each an outlined badge: a flag for the motto, a pin for a note."""
    out = [Outline(h.get("motto"), icon="flag", size=size)] if h.on("motto") else []
    return out + [Outline(n, icon="pin", size=size) for n in h.shown_notes]


def _title(title: str, room: float, size: float, floor: float) -> tuple[float, list[str]]:
    """The title beside its icon: on one line at the largest size down to `floor` that fits `room`, else on two."""
    def fits(rows: list[str], s: float) -> bool:
        return s + max(8, s * .4) + max(width(row, "sans-bold", s, s * .12) for row in rows) <= room
    s = size
    while s > floor and not fits([title], s):
        s -= .5
    words = title.split()
    if fits([title], s) or len(words) < 2:
        return s, [title]
    best = None
    for cut in range(1, len(words)):
        pair = [" ".join(words[:cut]), " ".join(words[cut:])]
        t = size * .8
        while t > 11 and not fits(pair, t):
            t -= .5
        balance = abs(width(pair[0], "sans-bold", t) - width(pair[1], "sans-bold", t))
        if best is None or (t, -balance) > (best[0], -best[2]):
            best = (t, pair, balance)
    return (best[0], best[1]) if best and best[0] > s else (s, [title])


def _band(cv, th: dict, W: float, bh: float, title: str, msg: str, glyph: str, *, kick: tuple | None,
          tsize: float, centre: bool, pad: float) -> tuple[str, float]:
    """The masthead band and its accent block. Returns (markup, its height), grown for a title on two lines."""
    lab = th["label"]
    on = P.letters_on(lab)
    msize = max(11.0, tsize * .62)
    while msg and msize > 9 and 52 + width(msg.upper(), "sans-bold", msize, msize * .1) > W * .42:
        msize -= .5
    mw = (52 + width(msg.upper(), "sans-bold", msize, msize * .1)) if msg else 0
    room = W - mw - 2 * pad
    size, rows = _title(title, room, tsize, max(12.0, tsize * .6))
    lead = size * 1.15
    cap = cap_height("sans-bold", size)
    bh = round(bh + lead * (len(rows) - 1))
    out = [P.rect(0, 0, W - mw, bh, lab)]
    if msg:
        out.append(P.rect(W - mw, 0, mw, bh, P.ACCENT))
    gap = max(8, size * .4)
    ls = size * .12
    run = size + gap + max(width(row, "sans-bold", size, ls) for row in rows)
    gx = (W - mw - run) / 2 if centre else pad
    if kick:
        ks = P.fitted(kick[0], "sans-bold", KICK, 6.5, room - 19, KICK_LS)
        kx = (W - mw - 19 - width(kick[0], "sans-bold", ks, ks * KICK_LS)) / 2 if centre else pad
        out.append(P.icon(kick[1], kx, 16, 12, "ash", 2.2)
                   + P.text(cv, kick[0], x=kx + 19, y=26, size=ks, face="sans-bold", ls=ks * KICK_LS, fill="ash",
                            ground=lab, what="kicker"))
        last = bh - 22
    else:
        last = (bh + cap + lead * (len(rows) - 1)) / 2
    first = last - lead * (len(rows) - 1)
    if title:
        out.append(P.icon(glyph, gx, first - cap / 2 - size / 2, size, on, 2.2))
    for i, row in enumerate(rows):
        out.append(P.text(cv, row, x=gx + size + gap, y=first + i * lead, size=size, face="sans-bold", ls=ls,
                          fill=on, ground=lab, what="title"))
    if msg:
        base = last if kick else (bh + cap_height("sans-bold", msize)) / 2
        out.append(P.text(cv, msg.upper(), x=W - mw / 2, y=base, size=msize, face="sans-bold", ls=msize * .1,
                          fill=P.letters_on(P.ACCENT), ground=P.ACCENT, anchor="middle", what="release"))
    return "".join(out), bh


def _place(items: list, draw, *, x0: float, x1: float, y: float, gap: float, centre: bool, spread: bool,
           motion: bool, begin: float, lift: float) -> tuple[str, float]:
    """Badges in rows from `y`: centred, spread across a single row, or set from the left.

    A row is spread only when it already fills most of the width: two
    badges at either end of a page read as two things, not one row.
    `draw(item, x, y)` draws one. Returns (markup, the height they took).
    """
    lines = P.rows(items, x1 - x0, gap)
    out, yy, n = [], y, 0
    for row in lines:
        step = gap
        if spread and len(lines) == 1 and len(row) > 1 and P.row_width(row, gap) >= .7 * (x1 - x0):
            step = (x1 - x0 - sum(it.w for it in row)) / (len(row) - 1)
        xx = (x0 + x1 - P.row_width(row, gap)) / 2 if centre else x0
        for it in row:
            m = draw(it, xx, yy)
            out.append(rise(m, begin + n * .08, lift=lift) if motion else m)
            xx += it.w + step
            n += 1
        yy += row[0].h + gap
    return "".join(out), (yy - gap - y if lines else 0)


def header(h: Header, th: dict, wide: bool = True, motion: bool = True, *, code: str = "H2") -> str:
    """A masthead header: H1 centred, H2 from the left, H3 slim."""
    std = P.theme(th)
    centre, slim = code == "H1", code == "H3"
    W = WIDE if wide else NARROW
    pad = 32 if wide else 20
    inner = W - 2 * pad
    msg, kick, rest = parts(h, kicker=not slim)
    title = h.caps
    if not title and kick:
        title, kick = kick[0], None   # no title: the path or the site takes its place
    bh = (60 if wide else 52) if slim else ((96 if wide else 74) if kick else 70)
    tsize = (22 if wide else 16) if slim else (34 if wide else 17)
    room = min(inner, 660 if centre else 640)
    tsz, tlines = P.prose(h.get("tagline"), (15 if slim else 18) if wide else 15, room, rows=3)
    dsz, dlines = P.prose(h.get("description"), (12.5 if slim else 13.5) if wide else 12.5, room, rows=3)
    notes = said(h, (9.5 if slim else 10.5) if wide else 9.5)
    size = (9.5 if slim else 10.5) if wide else 10
    chips = figures(rest, std, size)
    if wide and not centre and P.row_width(chips) > inner:
        # One row when a point smaller makes it one, a quarter point at a time; else the full size, wrapped.
        for smaller in (size - .25 * k for k in range(1, 5)):
            fewer = figures(rest, std, smaller)
            if P.row_width(fewer) <= inner:
                chips = fewer
                break

    cv = P.new(W, 0, h.spoken_title(), h.spoken(),
               f"{code} {th['name']}" + ("" if wide else " narrow") + ("" if motion else " still"))
    band, bh = _band(cv, std, W, bh, title, msg, plate_icon(h), kick=kick, tsize=tsize, centre=centre, pad=pad)
    x, anchor = (W / 2, "middle") if centre else (pad, "start")
    body = []
    y = bh + (20 if slim else 28)
    if tlines:
        lead = tsz * 1.45
        m = P.lines(cv, tlines, std, x=x, top=y, size=tsz, lead=lead, anchor=anchor, what="tagline")
        body.append(rise(m, .5) if motion else m)
        y += lead * (len(tlines) - 1) + tsz
    if dlines:
        y += 10 if tlines else 0
        lead = dsz * 1.45
        m = P.lines(cv, dlines, std, x=x, top=y, size=dsz, lead=lead, anchor=anchor, fill=std["muted"],
                    what="description")
        body.append(rise(m, .56) if motion else m)
        y += lead * (len(dlines) - 1) + dsz
    if notes:
        y += (14 if slim else 18) if (tlines or dlines) else 0
        m, used = _place(notes, lambda o, xx, yy: o.draw(cv, xx, yy, std, what="motto"), x0=pad, x1=W - pad, y=y,
                         gap=8, centre=centre, spread=False, motion=motion, begin=.62, lift=6)
        body.append(m)
        y += used
    if chips:
        y += 20 if slim else 26
        body.append(P.rule(pad, W - pad, y - 13, std))
        m, used = _place(chips, lambda ch, xx, yy: ch.draw(cv, xx, yy, "figure"), x0=pad, x1=W - pad, y=y, gap=8,
                         centre=centre, spread=not centre, motion=motion, begin=.75, lift=4)
        body.append(m)
        y += used
    H = round(y + (22 if slim else pad)) if body else round(bh)
    cv.h = H
    cid = P.card(cv, std, W, H)
    cv.add(f'<g clip-path="url(#{cid})">' + (wipe(cv, band, 0, 0, W, bh, 0.0, .8) if motion else band) + "</g>")
    cv.add(*body)
    return cv.svg()


def sheet(h: Header, th: dict, wide: bool = True, motion: bool = True) -> str:
    return header(h, th, wide, motion, code="H1")


def section(h: Header, th: dict, wide: bool = True, motion: bool = True) -> str:
    return header(h, th, wide, motion, code="H2")


def strip(h: Header, th: dict, wide: bool = True, motion: bool = True) -> str:
    return header(h, th, wide, motion, code="H3")


# --- footers ----------------------------------------------------------------------------------

def _runs(ft: Footer) -> list[tuple[str, bool, str]]:
    """The attribution as runs of small capitals, (words, a heart after them, words after the heart)."""
    out = []
    if ft.on("built"):
        out.append(("BUILT WITH", True, f"BY {ft.handle.upper()}"))
    if ft.on("license"):
        out.append((f"{ft.license.upper()} LICENSE", False, ""))
    if ft.on("updated"):
        out.append((f"UPDATED {ft.updated}", False, ""))
    return out


SEP = "  ·  "


def _run_width(run: tuple, size: float, ls: float) -> float:
    words, love, after = run
    return (width(words, "sans-bold", size, ls) + (size + 8 if love else 0)
            + (width(" " + after, "sans-bold", size, ls) if after else 0))


def _band_foot(cv, th: dict, W: float, bh: float, ft: Footer, *, attribution: bool, pad: float) -> tuple[str, float]:
    """The footer's band: the closing words in the black, the attribution under them in small capitals when
    asked, and the way back up in the accent. Returns (markup, its height).

    On a page the way up is a block at the band's right end; on a phone,
    where the words need the width, it is a strip along the band's foot.
    """
    lab = th["label"]
    on = P.letters_on(lab)
    stacked = W < 400
    top = ft.get("top")
    tsz, tls = 10.5, 1.05
    tw = (48 + width(top.upper(), "sans-bold", tsz, tls) + 26) if top else 0
    strip = 32 if top and stacked else 0
    room = W - 2 * pad - (0 if stacked else tw)
    words = ft.get("closing")
    csz = P.fitted(words, "sans", 15 if W > 400 else 13, 10.5, room) if words else 0
    closing = ([words] if width(words, "sans", csz) <= room else (wrap(words, "sans", csz, room, rows=3) or [words])
               ) if words else []
    runs = _runs(ft) if attribution else []
    asz, als = 8.5, .9
    sep = width(SEP, "sans-bold", asz, als)
    while runs and asz > 6.5 and not stacked and \
            sum(_run_width(r, asz, als) for r in runs) + width(SEP, "sans-bold", asz, als) * (len(runs) - 1) > room:
        asz -= .25
    lines: list[list] = []
    line, used = [], 0.0
    for r in runs:
        sep = width(SEP, "sans-bold", asz, als)
        need = _run_width(r, asz, als) + (sep if line else 0)
        if line and used + need > room:
            lines.append(line)
            line, used, need = [], 0.0, _run_width(r, asz, als)
        line.append(r)
        used += need
    if line:
        lines.append(line)
    ccap, acap = cap_height("sans", csz), cap_height("sans-bold", asz)
    clead, alead = csz * 1.3, asz * 1.9
    content = (ccap + clead * (len(closing) - 1) if closing else 0) + \
        ((10 if closing else 0) + acap + alead * (len(lines) - 1) if lines else 0)
    black = round(max(bh - strip, content + 28))
    bh = black + strip
    out = [P.rect(0, 0, W - (0 if stacked else tw), black, lab)]
    if top:
        af = P.letters_on(P.ACCENT)
        label = width(top.upper(), "sans-bold", tsz, tls)
        if stacked:
            bx, by, bw, bhh = 0, black, W, strip
            ax = (W - 22 - label) / 2
        else:
            bx, by, bw, bhh = W - tw, 0, tw, black
            ax = W - tw + 26
        out.append(P.rect(bx, by, bw, bhh, P.ACCENT))
        out.append(P.up_arrow(ax, by + bhh / 2 - 7, 14, af, 2.3))
        out.append(P.text(cv, top.upper(), x=ax + 22, y=by + bhh / 2 + cap_height("sans-bold", tsz) / 2, size=tsz,
                          face="sans-bold", ls=tls, fill=af, ground=P.ACCENT, what="back to top"))
    y = (black - content) / 2
    for i, row in enumerate(closing):
        out.append(P.text(cv, row, x=pad, y=y + ccap + i * clead, size=csz, fill=on, ground=lab, what="closing"))
    if closing:
        y += ccap + clead * (len(closing) - 1) + 10
    for i, line in enumerate(lines):
        base = y + acap + i * alead
        x = pad
        for j, (said_, love, after) in enumerate(line):
            if j:
                out.append(P.text(cv, SEP, x=x, y=base, size=asz, face="sans-bold", ls=als, fill="ash", ground=lab,
                                  what="attribution"))
                x += width(SEP, "sans-bold", asz, als)
            out.append(P.text(cv, said_, x=x, y=base, size=asz, face="sans-bold", ls=als, fill="ash", ground=lab,
                              what="attribution"))
            x += width(said_, "sans-bold", asz, als)
            if love:
                out.append(P.solid("heart", x + 4, base - asz * .95, asz, heart(th)))
                x += asz + 8
            if after:
                out.append(P.text(cv, " " + after, x=x, y=base, size=asz, face="sans-bold", ls=als, fill="ash",
                                  ground=lab, what="attribution"))
                x += width(" " + after, "sans-bold", asz, als)
    return "".join(out), bh


def _foot_chips(ft: Footer, th: dict, size: float) -> list[Chip]:
    out = []
    if ft.on("built"):
        out.append(Chip("built with", ft.handle, icon="heart", heart=heart(th), size=size, lab=th["label"],
                        msg="magenta"))
    if ft.on("license"):
        out.append(Chip("license", ft.license, icon="scale", size=size, lab=th["label"], msg="yellow"))
    if ft.on("updated"):
        out.append(Chip("updated", ft.updated, icon="calendar", size=size, lab=th["label"], msg="slate"))
    return out


def _footer_canvas(ft: Footer, code: str, th: dict, wide: bool):
    return P.new(WIDE if wide else NARROW, 0, ft.get("closing") or "Footer", ft.spoken(),
                 f"{code} {th['name']}" + ("" if wide else " narrow"))


def title_block(ft: Footer, th: dict, wide: bool = True, motion: bool = True) -> str:
    """F1: the badges for who built it, its licence and its last change, over the band.

    Without closing words there is nothing for the band to say, so the way
    up joins the badges as a badge of its own, at the row's right end on a
    page, and the band narrows to a rule along the foot, split where the way
    up's arrow begins, as a badge divides its label from its message.
    """
    std = P.theme(th)
    W = WIDE if wide else NARROW
    pad = 26 if wide else 20
    size = 11 if wide else 10
    cv = _footer_canvas(ft, "F1", th, wide)
    chips = _foot_chips(ft, std, size)
    m, used = _place(chips, lambda ch, xx, yy: ch.draw(cv, xx, yy, "footer"), x0=pad, x1=W - pad, y=pad, gap=8,
                     centre=False, spread=False, motion=False, begin=0, lift=0)
    if ft.get("closing"):
        band, bh = _band_foot(cv, std, W, 50, ft, attribution=False, pad=pad)
        top = round(pad + used + pad) if chips else 0
        cv.h = top + bh
        cid = P.card(cv, std, W, cv.h)
        cv.add(m, f'<g clip-path="url(#{cid})"><g transform="translate(0 {top})">{band}</g></g>')
        return cv.svg()
    up = ft.get("top")
    way = Action(up, size=size, lab=std["label"], up=True) if up else None
    lines = P.rows(chips, W - 2 * pad)
    y = pad + used
    if way:
        last = P.row_width(lines[-1]) if lines else 0
        if lines and wide and last + 24 + way.w <= W - 2 * pad:
            wy = y - way.h
        else:
            wy = y + 8 if lines else pad
            y = wy + way.h
        wx = W - pad - way.w if wide else pad
    cv.h = round(y + pad + 5)
    cid = P.card(cv, std, W, cv.h)
    split = (wx + way.chip.w) if way else W
    cv.add(m)
    if way:
        cv.add(way.draw(cv, wx, wy, "back to top"))
    cv.add(f'<g clip-path="url(#{cid})">' + P.rect(0, cv.h - 5, split, 5, std["label"])
           + (P.rect(split, cv.h - 5, W - split, 5, P.ACCENT) if way else "") + "</g>")
    return cv.svg()


def scale_bar(ft: Footer, th: dict, wide: bool = True, motion: bool = True) -> str:
    """F2: the band alone, the attribution in small capitals under the closing words."""
    std = P.theme(th)
    W = WIDE if wide else NARROW
    cv = _footer_canvas(ft, "F2", th, wide)
    band, bh = _band_foot(cv, std, W, 64 if wide else 72, ft, attribution=True, pad=24 if wide else 18)
    cv.h = bh
    cid = P.card(cv, std, W, cv.h)
    cv.add(f'<g clip-path="url(#{cid})">{band}</g>')
    return cv.svg()


def link(label: str, th: dict, tone: str = "") -> str:
    """A link under the footer, as a badge that goes somewhere: its icon and word, then an arrow in the accent."""
    std = P.theme(th)
    a = Action(label, icon_name=LINKS.get(label.lower(), "link"), size=11, lab=std["label"])
    cv = P.new(a.w, a.h, label, f"Link: {label}", f"link {th['name']}")
    cv.add(a.draw(cv, 0, 0, "link"))
    return cv.svg()


# The designs by code, drawn as `designs.render` draws a print's.
DRAW = {"H1": sheet, "H2": section, "H3": strip, "F1": title_block, "F2": scale_bar}
