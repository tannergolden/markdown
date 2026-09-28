# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The `badges:` section of a page's settings, and the files and README block the badges make.

The section is the list of badges, in the order they stand under the header:

  badges:
    - name: status              # the file's name: kebab-case, and unique
      label: Status
      message: Active
      icon: pulse               # one of the 64
      link: ./
    - name: build
      label: Build
      icon: check
      measure:                  # the kit measures its message and its state
        workflow: checks.yml

or a map with that list under `list` and the options beside it:
`localize: true` also turns every shields.io link in the repository's
Markdown into a committed badge (see `localize`).

A badge with a black label is STATIC: it says what the settings say, in any
colour, or in `rotate`, a colour that changes each week. A badge with the gold
label is LIVE: its colour is a state, so its message colour is green, yellow
or red, or slate for no data yet, and one that measures takes both its message
and its state from what the kit measured. A badge that measures is live unless
it names another label, and then only its message is measured.

The page's theme decides how the badges are drawn. In `standard` each is drawn
as written: a classic style in its colours, a plate as a plate. In a print
every badge becomes the plate of its style in that print, a live one on its
gold sheet with its value in the state's print, so one theme colours the page.

A static badge's file is `static/NAME.svg`, a live one's `dynamic/NAME.svg`,
and a static plate adds `static/NAME-dark.svg` for the night theme. In the
README the static badges make one row and the live ones a row beneath it, as
the standards lay them out.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import re
from html import escape

from .. import KIT, KIT_VERSION, readme
from ..canvas import BUDGET, hazards
from ..palette import ICONS, PALETTE
from ..prints import PRINTS, RAINBOW, SPECTRUM
from . import classic, live, plates
from .classic import DEFAULT_STYLE, HEALTH_COLORS, HEALTH_NEUTRAL, STATIC_RANDOM_POOL, STYLES
from .plates import BLUEPRINT, BLUEPRINT_STYLES, DEFAULT_PRINT

FIELDS = ("name", "label", "message", "label_color", "message_color", "icon", "style", "print", "reserve", "link",
          "measure")
OPTIONS = ("list", "localize")
ROTATE = "rotate"
BLOCK = "badges"
STAMP = f"<!--{KIT} v{KIT_VERSION} badge-->"
_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
_HEX = re.compile(r"#[0-9a-fA-F]{6}")


class BadgesError(ValueError):
    pass


def _text(v: object) -> str:
    """A field's value as text, the way it reads in the file: a list joined with commas, and none as nothing."""
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, list):
        return ", ".join(_text(x) for x in v)
    return str(v)


def _badge(i: int, entry: object) -> dict:
    where = f"badges[{i}]"
    if not isinstance(entry, dict):
        raise BadgesError(f"{where}: expected a map of the badge's fields")
    b: dict = {}
    for k, v in entry.items():
        key = str(k).replace("-", "_")
        if key not in FIELDS:
            raise BadgesError(f"{where}: unknown field {str(k)!r} (one of {', '.join(FIELDS)})")
        b[key] = v if key == "measure" else _text(v)
    if "measure" in b:
        if b["measure"] in (None, "", False):
            del b["measure"]
        else:
            try:
                b["measure"] = live.parse(b["measure"])
            except live.MeasureError as exc:
                name = b.get("name", "")
                raise BadgesError(f"{where}{f' ({name})' if name else ''}: {exc}") from exc
    return b


def check(section: object) -> dict:
    """The section in full, `{"list": [...], "localize": bool}`, with every badge's fields checked."""
    if section in (None, True):
        section = {}
    if isinstance(section, list):
        section = {"list": section}
    if not isinstance(section, dict):
        raise BadgesError("badges: expected false, a list of badges, or a map with them under list")
    given = {}
    for k, v in section.items():
        key = str(k).replace("-", "_")
        if key not in OPTIONS:
            raise BadgesError(f"badges: unknown key {str(k)!r} (one of {', '.join(OPTIONS)})")
        given[key] = v
    items = given.get("list")
    items = [] if items is None else items
    if not isinstance(items, list):
        raise BadgesError("badges: list: expected a list of badges")
    localize = given.get("localize")
    if localize is None:
        localize = False
    if isinstance(localize, str) and localize.strip().lower() in ("true", "false"):
        localize = localize.strip().lower() == "true"
    if not isinstance(localize, bool):
        raise BadgesError(f"badges: localize: expected true or false, not {localize!r}")
    badges = [_badge(i, entry) for i, entry in enumerate(items)]
    problems = validate(badges)
    if problems:
        raise BadgesError("badges: " + "; ".join(problems))
    return {"list": badges, "localize": localize}


# --- what each badge is ----------------------------------------------------------------------------

def _is_colour(token: str) -> bool:
    return token in PALETTE or bool(_HEX.fullmatch(token))


def _hex(token: str) -> str:
    return PALETTE.get(token, token).upper()


def is_gold(token: str) -> bool:
    """True for the live label, whether written as the palette token or as its hex."""
    return _hex(token) == PALETTE["gold"].upper()


def health(token: str) -> str | None:
    """The state a message colour names, written as its token or its hex, or None for a colour that is no state."""
    want = _hex(token)
    for tok in sorted(HEALTH_COLORS | HEALTH_NEUTRAL):
        if PALETTE[tok].upper() == want:
            return tok
    return None


def label_colour(b: dict) -> str:
    """The label's colour: as written, else gold for a badge that measures and black for any other."""
    return b.get("label_color") or ("gold" if b.get("measure") else "black")


def is_live(b: dict) -> bool:
    return is_gold(label_colour(b))


def reserve(b: dict) -> tuple[str, ...]:
    """The values a plate keeps room for: its own `reserve`, and every value what it measures can show."""
    raw = str(b.get("reserve") or "").strip()
    if raw[:1] == "[" and raw[-1:] == "]":
        raw = raw[1:-1]
    out = [v.strip().strip("'\"") for v in raw.split(",") if v.strip()]
    measure = b.get("measure")
    if measure:
        out += [v for v in live.VALUES[measure["kind"]] if v not in out]
    return tuple(out)


def _errors(b: dict) -> list[str]:
    """What one badge gets wrong, apart from its name, each said precisely."""
    out = []
    measure = b.get("measure")
    label, message = b.get("label", ""), b.get("message", "")
    if measure and message:
        out.append("the kit measures this badge's message; drop message")
    if not measure and not label and not message:
        out.append("needs a label or a message")
    style = b.get("style") or DEFAULT_STYLE
    if style not in STYLES and style not in BLUEPRINT_STYLES:
        out.append(f"unknown style {style!r} (one of {', '.join([*STYLES, *BLUEPRINT_STYLES])})")
    icon = b.get("icon", "")
    if icon and icon not in ICONS:
        out.append(f"unknown icon {icon!r} (see markdown-kit icons)")
    lc, mc = label_colour(b), b.get("message_color", "")
    if not _is_colour(lc):
        out.append(f"unknown color {lc!r} for label_color (a palette token or #RRGGBB)")
    if mc and mc != ROTATE and not _is_colour(mc):
        out.append(f"unknown color {mc!r} for message_color (a palette token, #RRGGBB, or rotate)")
    if is_live(b):
        # The standards' rule for a live badge: its colour is a state, never a hue of its own.
        if measure and mc:
            out.append("a badge that measures takes its colour from what it measured; drop message_color")
        elif mc == ROTATE:
            out.append("a live badge's colour is its state, so it cannot rotate")
        elif not measure and _is_colour(mc or "blue") and health(mc or "blue") is None:
            out.append(f"a live badge (gold label) paints its message in a state - "
                       f"{', '.join(sorted(HEALTH_COLORS))} (or slate for no status yet) - not {mc or 'blue'!r}")
    tone = b.get("print", "")
    if style in BLUEPRINT_STYLES:
        if is_live(b):
            if tone:
                out.append("a live plate (gold label) is drawn in its state's print; drop print")
        else:
            if _hex(lc) != PALETTE["black"].upper():
                out.append(f"a blueprint plate's label is black (static) or gold (live), not {lc!r}")
            if mc:
                out.append(f"a static blueprint plate is drawn in its print; drop message_color and name one "
                           f"with print ({', '.join(PRINTS)})")
            if tone and tone != RAINBOW and tone not in PRINTS:
                out.append(f"unknown print {tone!r} (one of {', '.join(PRINTS)}, or {RAINBOW}; a repository "
                           "adds its own under prints)")
    elif tone:
        out.append(f"print is for a blueprint style, not {style!r}; in a print theme every badge is a plate")
    return out


def validate(badges: list[dict]) -> list[str]:
    """What the list gets wrong: a name missing, repeated or not kebab-case, and each badge's own faults."""
    errors: list[str] = []
    seen: set[str] = set()
    for i, b in enumerate(badges):
        name = b.get("name", "")
        where = f"badges[{i}]" + (f" ({name})" if name else "")
        if not name:
            errors.append(f"{where}: missing name")
            continue
        if not _NAME.fullmatch(name):
            errors.append(f"{where}: name must be kebab-case ([a-z0-9-])")
        if name in seen:
            errors.append(f"{where}: duplicate name")
        seen.add(name)
        errors += [f"{where}: {e}" for e in _errors(b)]
    # A static badge drawn as a plate also writes NAME-dark.svg, which a badge of that name would claim too.
    static = [b["name"] for b in badges if b.get("name") and not is_live(b)]
    for name in static:
        if f"{name}-dark" in static:
            errors.append(f"{name} and {name}-dark both write static/{name}-dark.svg; rename one (a static "
                          "badge drawn as a plate also writes NAME-dark.svg)")
    return errors


# --- drawing ------------------------------------------------------------------------------------------

def week(day: dt.date) -> str:
    """The ISO week `day` is in, as 2026W40: the seed a rotating colour is picked with."""
    year, number, _ = day.isocalendar()
    return f"{year}W{number:02d}"


def rotate(name: str, seed: str) -> str:
    """The colour a rotating badge takes for `seed`: one of the palette's decorative tokens, the same all week.

    Never a state colour, so a static badge cannot pass for a live one, and
    never a colour the standards reserve for a header's slots.
    """
    return STATIC_RANDOM_POOL[int(hashlib.md5(f"{seed}:{name}".encode()).hexdigest(), 16) % len(STATIC_RANDOM_POOL)]


def form(b: dict, theme: str) -> str:
    """The style `b` is drawn in on a page in `theme`: as written in standard, and its plate in a print."""
    style = b.get("style") or DEFAULT_STYLE
    if theme not in PRINTS or style in BLUEPRINT_STYLES:
        return style
    return BLUEPRINT + style


def says(b: dict, measured: dict, seed: str) -> tuple[str, str]:
    """What `b` says and the colour it says it in: measured, with no data until it is, or as written."""
    if b.get("measure"):
        got = measured.get(b["name"]) or {}
        message = got.get("message") or live.NO_DATA[0]
        if is_live(b):
            return message, got.get("state") or live.NO_DATA[1]
    else:
        message = b.get("message", "")
    colour = b.get("message_color") or "blue"
    return message, rotate(b["name"], seed) if colour == ROTATE else colour


def paths(b: dict, theme: str) -> list[str]:
    """The files `b` writes on a page in `theme`, under the badges' folder: a static plate's two, else one."""
    name = b["name"]
    if is_live(b):
        return [f"dynamic/{name}.svg"]
    if form(b, theme) in BLUEPRINT_STYLES:
        return [f"static/{name}.svg", f"static/{name}-dark.svg"]
    return [f"static/{name}.svg"]


def unlettered(b: dict, style: str, message: str) -> list[str]:
    """Each field a plate in `style` cannot letter, with the characters it lacks."""
    caps = BLUEPRINT_STYLES[style]["caps"]
    out = []
    for field, face, text in (("label", "meta", b.get("label", "")), ("message", "num", message),
                              *(("reserve", "num", v) for v in reserve(b))):
        gap = plates.missing_glyphs(text.upper() if caps else text, face)
        if gap:
            out.append(f"{field} {text!r} has characters the plates' lettering cannot draw: {gap!r}")
    return out


def lint(svg: str) -> list[str]:
    """Everything wrong with a badge as a README image, or an empty list.

    A badge is held to what every file the kit draws is held to, and to its
    own budget, but not to the banners' palette or their outlined letters: a
    classic badge is set in the reader's Verdana and shaded as shields shades.
    """
    problems = hazards(svg)
    if 'role="img"' not in svg:
        problems.append('no role="img"')
    if not re.search(r"<title>[^<]+</title>", svg):
        problems.append("no title")
    if STAMP not in svg:
        problems.append("no stamp")
    size = len(svg.encode("utf-8"))
    if size > BUDGET["badge"]:
        problems.append(f"{size:,} bytes, over the {BUDGET['badge']:,} budget")
    return problems


def draw(b: dict, measured: dict, *, theme: str, shade: str | None, seed: str) -> dict[str, str]:
    """{path under the badges' folder: svg} for one badge on a page in `theme`, every file linted.

    `shade` is the print a rainbowprint page is in, which a plate that names
    rainbowprint follows; `seed` picks a rotating badge's colour.
    """
    files = _draw(b, measured, theme=theme, shade=shade, seed=seed)
    for rel, svg in files.items():
        problems = lint(svg)
        if problems:
            raise BadgesError(f"badges: {b['name']}: {rel} fails the lint: {'; '.join(problems)}")
    return files


def _draw(b: dict, measured: dict, *, theme: str, shade: str | None, seed: str) -> dict[str, str]:
    style = form(b, theme)
    label, icon = b.get("label", ""), b.get("icon") or None
    message, colour = says(b, measured, seed)
    rels = paths(b, theme)
    if style not in BLUEPRINT_STYLES:
        return {rels[0]: classic.render(label, message, label_colour(b), colour, icon, style) + "\n"}
    gaps = unlettered(b, style, message)
    if gaps:
        why = "" if style == (b.get("style") or DEFAULT_STYLE) else " (a print theme draws every badge as a plate)"
        raise BadgesError(f"badges: {b['name']}: " + "; ".join(gaps) + why)
    if is_live(b):
        return {rels[0]: plates.render_live(label, message, icon, style, colour, reserve(b)) + "\n"}
    tone = theme if theme in PRINTS else (b.get("print") or DEFAULT_PRINT)
    if tone == RAINBOW:
        tone = shade or SPECTRUM[0]
    return {rel: plates.render_blueprint(label, message, icon, style, tone, dark, reserve(b)) + "\n"
            for rel, dark in zip(rels, (False, True))}


def alt(label: str, message: str) -> str:
    return f"{label}: {message}" if label and message else (label or message)


def snippet(b: dict, rels: list[str], text: str, base: str) -> str:
    """One badge as the README shows it: a <picture> for a static plate's pair, else an <img>, in its link."""
    if len(rels) == 2:
        pic = (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{base}/{rels[1]}">'
               f'<img alt="{escape(text)}" src="{base}/{rels[0]}"></picture>')
    else:
        pic = f'<img alt="{escape(text)}" src="{base}/{rels[0]}">'
    link = b.get("link", "")
    return f'<a href="{escape(link)}">{pic}</a>' if link else pic


def block(rows: list[list[str]]) -> str | None:
    """The README's badges block: each row centred, a blank line between rows. None when there are no badges."""
    rows = [row for row in rows if row]
    if not rows:
        return None
    body = "\n\n".join("\n".join(row) for row in rows)
    return readme.block(BLOCK, f'<div align="center">\n\n{body}\n\n</div>')


def plan(badges: list[dict], measured: dict, *, theme: str, shade: str | None, today: dt.date, folder: str,
         base: str, draw_files: bool = True) -> dict:
    """Every badge's files by path, the README's block, and what each badge says, for a page in `theme`.

    `folder` is where the files go, from the repository's root, and `base` the
    same folder as the README reaches it.
    """
    seed = week(today)
    files: dict[str, str] = {}
    rows: tuple[list[str], list[str]] = ([], [])
    said = {}
    for b in badges:
        drawn = draw(b, measured, theme=theme, shade=shade, seed=seed) if draw_files else \
            {rel: "" for rel in paths(b, theme)}
        files.update({f"{folder}/{rel}": svg for rel, svg in drawn.items()})
        message, _ = says(b, measured, seed)
        said[b["name"]] = message
        rows[is_live(b)].append(snippet(b, list(drawn), alt(b.get("label", ""), message), base))
    return {"files": files, "block": block(list(rows)), "names": [b["name"] for b in badges], "says": said,
            "notes": []}
