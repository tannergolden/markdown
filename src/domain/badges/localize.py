# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""shields.io links in a repository's Markdown, drawn once as classic badges and committed.

A badge served from img.shields.io is fetched on every view, from a service
the repository does not control. With `localize: true` under `badges`, every
run finds each static shields.io badge in the repository's tracked Markdown,
draws it once in the same style, and points the link at the committed file:

  1. Read each URL's label, message, colours and style, the way shields does,
     and give the four classification badges (Status, Role, Context, License)
     the icons the standards' headers use.
  2. Draw each distinct badge once into `static/localized/`, inside the
     static badges' folder, since a shields.io badge says what its link says:
     one file per badge, however many documents show it, named for its label
     and message, with a short hash only where two different badges would
     share a name. The folder is theirs alone, so none can take the name of a
     badge the settings draw.
  3. Point every reference at the file's absolute raw.githubusercontent.com
     URL on the default branch. GitHub resolves a relative image only in its
     main file views; a pull request's rich diff, the security-policy tab and
     a soft navigation leave it broken, and an absolute URL shows everywhere.
     The README the page is drawn into keeps any reference it has, since its
     own view resolves them.

The lock keeps each drawn badge's fields, so a later run can redraw it with
the kit that runs then, and a file no document refers to any more is removed.
A badge drawn before into a folder the kit has since left, `badges/localized/`
or `markdown/badges/localized/`, is drawn again in `static/localized/` and
every link to it is moved there, so no document shows a missing image. A
shields.io endpoint that is not a static badge, like a live GitHub one, is
left as it is, with a note.
"""
from __future__ import annotations

import hashlib
import re
import urllib.parse

from .classic import render

FOLDER = "localized"
SHIELDS = re.compile(r"https?://img\.shields\.io/badge/[^\s)\"'>]+")

# The icons the standards' headers give the four classification badges, and a few badges common in templates.
# A label not listed is drawn with no icon.
LABEL_ICON = {
    "status": "pulse",
    "role": "book",
    "context": "layers",
    "license": "scale",
    "package": "package",
    "code style": "code",
    "code_style": "code",
    "conventional commits": "commit",
    "speed": "flame",
    "chat": "chat",
}
# shields' colours as palette tokens: the brand hexes map straight through, and anything else stays a #hex.
HEX_TO_TOKEN = {
    "2EA043": "green", "F1E05A": "yellow", "FE5196": "pink",
    "9C27B0": "purple", "D73A49": "red", "3366FF": "blue",
    "C0A062": "gold", "8A8B2C": "olive", "1F9E8F": "teal",
    "E36209": "orange", "57606A": "slate", "8B6CFF": "violet",
}
NAME_TO_TOKEN = {
    "green": "green", "brightgreen": "green", "success": "green",
    "yellow": "yellow", "yellowgreen": "olive", "important": "orange",
    "orange": "orange", "red": "red", "critical": "red", "blue": "blue",
    "informational": "blue", "lightgrey": "slate", "gray": "slate",
    "grey": "slate", "blueviolet": "violet", "purple": "purple",
    "ff69b4": "pink", "pink": "pink",
}
# shields' styles as the kit's. `social` is another object altogether, not another chip, so it lands on flat.
STYLE_MAP = {"for-the-badge": "for-the-badge", "flat": "flat", "flat-square": "flat-square", "plastic": "plastic",
             "social": "flat"}
SPEC = ("label", "message", "label_color", "message_color", "icon", "style")


def _unescape_field(field: str) -> str:
    """Undo shields' path escaping for one field: `__` is an underscore, `_` a space, then percent-escapes."""
    field = field.replace("__", "\x01").replace("_", " ").replace("\x01", "_")
    return urllib.parse.unquote(field)


def _colour(raw: str, default: str) -> str:
    raw = raw.strip()
    if not raw:
        return default
    up = raw.upper()
    if re.fullmatch(r"[0-9A-F]{6}", up):
        return HEX_TO_TOKEN.get(up, f"#{up}")
    if re.fullmatch(r"[0-9A-F]{3}", up):
        full = "".join(ch * 2 for ch in up)
        return HEX_TO_TOKEN.get(full, f"#{up}")
    return NAME_TO_TOKEN.get(raw.lower(), "slate")


def parse(url: str) -> dict | None:
    """A static shields.io badge's fields, or None for any other shields endpoint."""
    m = re.match(r"https?://img\.shields\.io/badge/(.+)$", url)
    if not m:
        return None
    path, _, query = m.group(1).partition("?")
    if path.endswith(".svg"):
        path = path[:-4]
    # Three dash-separated fields, `--` being a dash within one.
    parts = [p.replace("\x00", "-") for p in path.replace("--", "\x00").split("-")]
    if len(parts) < 2:
        return None
    colour_raw, message_raw = parts[-1], parts[-2]
    label = _unescape_field("-".join(parts[:-2]) if len(parts) >= 3 else "")
    message = _unescape_field(message_raw)
    params = urllib.parse.parse_qs(query)
    style = STYLE_MAP.get((params.get("style") or ["flat"])[0], "flat")
    label_hex = (params.get("labelColor") or params.get("labelcolor") or [""])[0]
    # A bare shields badge has a grey label; the house style is black.
    label_colour = _colour(label_hex, "black") if label_hex else "black"
    return {"label": label, "message": message, "label_color": label_colour,
            "message_color": _colour(colour_raw, "slate"), "icon": LABEL_ICON.get(label.lower()), "style": style}


def signature(spec: dict) -> tuple:
    return tuple(spec.get(k) for k in SPEC)


def _kebab(s: str) -> str:
    return re.sub(r"[^0-9a-zA-Z]+", "-", s.strip().lower()).strip("-") or "x"


def base_name(spec: dict) -> str:
    return f"{_kebab(spec['label'])}-{_kebab(spec['message'])}".strip("-") or "badge"


def _hash(sig: tuple) -> str:
    return hashlib.md5("|".join(str(x) for x in sig).encode()).hexdigest()[:6]


def names(specs: list[dict], taken: dict[str, dict] | None = None) -> dict[tuple, str]:
    """Each distinct badge's file name: its label and message, plus a short hash where two would share one.

    `taken` is the files already drawn, by name, with the badge each holds: a
    new badge never takes a name that holds a different one.
    """
    taken = taken or {}
    by_sig = {signature(s): s for s in specs}
    held = {signature(spec): name for name, spec in taken.items()}
    groups: dict[str, list[tuple]] = {}
    for sig, spec in by_sig.items():
        groups.setdefault(base_name(spec), []).append(sig)
    out = {}
    for base, sigs in groups.items():
        for sig in sigs:
            if sig in held:
                out[sig] = held[sig]
                continue
            name = f"{base}.svg"
            if len(sigs) > 1 or (name in taken and signature(taken[name]) != sig):
                name = f"{base}-{_hash(sig)}.svg"
            out[sig] = name
    return out


def references(*folders: str) -> re.Pattern:
    """Every way a document can point at a localized badge in one of `folders` (each from the repository's root):
    relative with any number of ../, from the root with /, or a raw URL for any owner, repository and branch.
    The group `folder` is the folder it names and `name` the file's name."""
    either = "|".join(re.escape(f) for f in sorted(folders, key=len, reverse=True))
    return re.compile(r"(?:https?://raw\.githubusercontent\.com/[^/\s)\"']+/[^/\s)\"']+/[^\s)\"']+?/)?"
                      r"(?:(?:\.\./)+|/|\./)?(?P<folder>" + either + r")/(?P<name>[a-z0-9][a-z0-9.-]*\.svg)")


def draw(spec: dict) -> str:
    return render(spec["label"], spec["message"], spec["label_color"], spec["message_color"], spec["icon"],
                  spec["style"]) + "\n"


def rewrite(text: str, files: dict[str, str], base: str, pattern: re.Pattern, keep: bool,
            moved: re.Pattern | None = None, drawn=()) -> str:
    """`text` with each shields.io URL in `files` pointing at its drawn file under `base`; each link `moved`
    finds, to a badge in a folder the kit has left, pointing at the same badge under `base` when it is `drawn`
    there; and, unless it is the README that `keep`s its references, every other reference to a localized badge
    pointing there too."""
    # Whole URLs only: one link can be the start of another, with a query after it.
    text = SHIELDS.sub(lambda m: base + files[m.group(0)] if m.group(0) in files else m.group(0), text)
    if moved is not None:
        text = moved.sub(lambda m: base + m["name"] if m["name"] in drawn else m.group(0), text)
    if keep:
        return text
    return pattern.sub(lambda m: base + m["name"], text)
