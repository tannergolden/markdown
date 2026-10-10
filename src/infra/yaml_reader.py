# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The YAML the settings file is written in, read with the standard library alone.

The kit installs nothing, so it cannot count on PyYAML, and it does not use it
when it happens to be there either: a file must read the same on every machine,
and PyYAML reads `on`, `no` and `2026-09-28` as things this reader does not.
This is the part of YAML 1.2 a settings file uses, and every other part is
refused with its line named rather than guessed at:

  - maps and lists in blocks, nested as deep as a file goes, a list's dashes
    either under its key or indented from it
  - `[a, b]` and `{a: 1}` inline, nested, across lines too
  - plain, 'single' and "double" quoted text, with the escapes YAML defines
  - `|` and `>` blocks of text, with `-` and `+` to say what happens to the
    last line break
  - true and false, null and ~, whole numbers and decimals; everything else
    is text, so `on`, `no` and a date stay the words they are

Refused: anchors and aliases, tags, `?` keys, a second document, a key given
twice in one map, and a tab in the indentation.
"""
from __future__ import annotations

import re


class YamlError(ValueError):
    """What is wrong, and on which line."""

    def __init__(self, message: str, line: int | None = None):
        self.line = line
        super().__init__(f"line {line}: {message}" if line else message)


class _Unclosed(YamlError):
    """Quoted text whose closing quote is not on this line: it may run on to the next."""


_INT = re.compile(r"[-+]?(?:0|[1-9][0-9]*)")
_FLOAT = re.compile(r"[-+]?(?:[0-9]+\.[0-9]*|\.[0-9]+)(?:[eE][-+]?[0-9]+)?|[-+]?[0-9]+[eE][-+]?[0-9]+")
_ESCAPES = {"0": "\0", "a": "\a", "b": "\b", "t": "\t", "\t": "\t", "n": "\n", "v": "\v", "f": "\f", "r": "\r",
            "e": "\x1b", " ": " ", '"': '"', "/": "/", "\\": "\\", "N": "\x85", "_": "\xa0", "L": " ",
            "P": " "}
_HEXLEN = {"x": 2, "u": 4, "U": 8}
_BLOCK = re.compile(r"([|>])([-+]?)([1-9]?)|([|>])([1-9])([-+])")


def resolve(s: str):
    """A plain scalar as the value it stands for: null, a boolean, a number, or the text itself."""
    if s in ("", "~", "null", "Null", "NULL"):
        return None
    if s in ("true", "True", "TRUE"):
        return True
    if s in ("false", "False", "FALSE"):
        return False
    if _INT.fullmatch(s):
        return int(s)
    if _FLOAT.fullmatch(s):
        return float(s)
    return s


def _double(body: str, line: int) -> str:
    out, i = [], 0
    while i < len(body):
        ch = body[i]
        if ch != "\\":
            out.append(ch)
            i += 1
            continue
        if i + 1 >= len(body):
            raise YamlError("a backslash ends the quoted text", line)
        e = body[i + 1]
        if e in _HEXLEN:
            digits = body[i + 2:i + 2 + _HEXLEN[e]]
            if len(digits) != _HEXLEN[e] or not re.fullmatch(r"[0-9A-Fa-f]+", digits):
                raise YamlError(f"\\{e} wants {_HEXLEN[e]} hex digits", line)
            out.append(chr(int(digits, 16)))
            i += 2 + _HEXLEN[e]
        elif e in _ESCAPES:
            out.append(_ESCAPES[e])
            i += 2
        else:
            raise YamlError(f"\\{e} is not an escape YAML has", line)
    return "".join(out)


def _quoted(s: str, i: int, line: int) -> tuple[str, int]:
    """The quoted text starting at s[i], and the index just past its closing quote."""
    q = s[i]
    j = i + 1
    buf = []
    while j < len(s):
        ch = s[j]
        if q == "'" and ch == "'":
            if s[j + 1:j + 2] == "'":
                buf.append("'")
                j += 2
                continue
            return _fold_flow("".join(buf), False), j + 1
        if q == '"' and ch == "\\":
            buf.append(s[j:j + 2])
            j += 2
            continue
        if q == '"' and ch == '"':
            return _double(_fold_flow("".join(buf), True), line), j + 1
        buf.append(ch)
        j += 1
    raise _Unclosed(f"the text opened with {q} is never closed", line)


def _fold_flow(content: str, double: bool) -> str:
    """Quoted text that runs over lines, folded as YAML folds it: a break between two lines becomes a space, an
    empty line a break, the indentation of each line after the first goes, and in double quotes a backslash at
    the end of a line joins it to the next with nothing between."""
    lines = content.split("\n")
    if len(lines) == 1:
        return content
    parts, empties = [lines[0].rstrip(" \t")], 0
    for k, raw in enumerate(lines[1:], 1):
        last = k == len(lines) - 1
        text = raw.lstrip(" \t") if last else raw.strip(" \t")
        if not text and not last:
            empties += 1
            continue
        prev = parts[-1]
        escaped = double and (len(prev) - len(prev.rstrip("\\"))) % 2 == 1
        if escaped:
            parts[-1] = prev[:-1]
        parts.append(("\n" * empties) if empties else ("" if escaped else " "))
        parts.append(text)
        empties = 0
    return "".join(parts)


def _uncomment(raw: str, line: int) -> str:
    """The line without its comment, quotes respected, and without trailing space."""
    i, n = 0, len(raw)
    while i < n:
        ch = raw[i]
        if ch in "'\"" and (i == 0 or raw[i - 1] in " \t[{,:-"):
            try:
                _, i = _quoted(raw, i, line)
            except YamlError:
                return raw.rstrip()
            continue
        if ch == "#" and (i == 0 or raw[i - 1] in " \t"):
            return raw[:i].rstrip()
        i += 1
    return raw.rstrip()


def _refuse(text: str, line: int) -> None:
    head = text.lstrip()[:1]
    if head == "&" or head == "*":
        raise YamlError("anchors and aliases are not read here; write the value out", line)
    if head == "!":
        raise YamlError("tags are not read here", line)
    if head == "?":
        raise YamlError("`?` keys are not read here", line)
    if head in "@`":
        raise YamlError(f"a plain value cannot start with {head}; quote it", line)


class _Flow:
    """An inline `[...]` or `{...}`, read character by character."""

    def __init__(self, s: str, line: int):
        self.s, self.i, self.line = s, 0, line

    def _space(self) -> None:
        while self.i < len(self.s) and self.s[self.i] in " \t\n":
            self.i += 1

    def value(self):
        self._space()
        if self.i >= len(self.s):
            raise YamlError("an inline list or map ends too soon", self.line)
        ch = self.s[self.i]
        if ch == "[":
            return self._seq()
        if ch == "{":
            return self._map()
        if ch in "'\"":
            v, self.i = _quoted(self.s, self.i, self.line)
            return v
        _refuse(ch, self.line)
        j = self.i
        while j < len(self.s) and self.s[j] not in ",]}" and not (self.s[j] == ":" and self.s[j + 1:j + 2] in (" ", "")):
            j += 1
        text = self.s[self.i:j].strip()
        self.i = j
        return resolve(text)

    def _seq(self) -> list:
        self.i += 1
        out = []
        while True:
            self._space()
            if self.i < len(self.s) and self.s[self.i] == "]":
                self.i += 1
                return out
            out.append(self.value())
            self._space()
            if self.i < len(self.s) and self.s[self.i] == ",":
                self.i += 1
            elif self.i < len(self.s) and self.s[self.i] == "]":
                continue
            else:
                raise YamlError("expected , or ] in an inline list", self.line)

    def _map(self) -> dict:
        self.i += 1
        out: dict = {}
        while True:
            self._space()
            if self.i < len(self.s) and self.s[self.i] == "}":
                self.i += 1
                return out
            key = self.value()
            self._space()
            value = None
            if self.i < len(self.s) and self.s[self.i] == ":":
                self.i += 1
                self._space()
                if self.i < len(self.s) and self.s[self.i] not in ",}":
                    value = self.value()
            if not isinstance(key, (str, int, float, bool)) and key is not None:
                raise YamlError("a map's key must be a plain value", self.line)
            if key in out:
                raise YamlError(f"{key!r} is given twice", self.line)
            out[key] = value
            self._space()
            if self.i < len(self.s) and self.s[self.i] == ",":
                self.i += 1
            elif self.i < len(self.s) and self.s[self.i] == "}":
                continue
            else:
                raise YamlError("expected , or } in an inline map", self.line)

    def whole(self):
        v = self.value()
        self._space()
        if self.i != len(self.s):
            raise YamlError(f"unexpected {self.s[self.i:].strip()!r} after an inline value", self.line)
        return v


def _key_split(text: str, line: int) -> tuple[object, str] | None:
    """A map entry's key and the rest of its line, or None when the line is not a map entry."""
    if text[:1] in "'\"":
        try:
            key, j = _quoted(text, 0, line)
        except _Unclosed:
            return None   # quoted text that runs on: a value, never a key
        rest = text[j:]
        if rest.startswith(":") and (len(rest) == 1 or rest[1] in " \t"):
            return key, rest[1:].strip()
        return None
    m = re.search(r":(?:[ \t]|$)", text)
    if not m:
        return None
    key = text[:m.start()].strip()
    if not key or key[0] in "[{":
        return None
    _refuse(key, line)
    return resolve(key), text[m.end():].strip()


class _Reader:
    def __init__(self, text: str):
        self.raw = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        # Each meaningful line as (its number, its indent, its text without the comment).
        self.lines: list[tuple[int, int, str]] = []
        started = False
        for n, raw in enumerate(self.raw, 1):
            body = _uncomment(raw, n)
            if not body.strip():
                continue
            lead = body[:len(body) - len(body.lstrip(" \t"))]
            if "\t" in lead:
                raise YamlError("a tab in the indentation; indent with spaces", n)
            stripped = body.strip()
            if stripped == "---":
                if started:
                    raise YamlError("a second document; a settings file holds one", n)
                started = True
                continue
            if stripped == "...":
                break
            if stripped.startswith("%"):
                raise YamlError("directives are not read here", n)
            started = True
            self.lines.append((n, len(lead), stripped))
        self.at = 0

    # -- the pieces ----------------------------------------------------------------------
    def peek(self):
        return self.lines[self.at] if self.at < len(self.lines) else None

    def node(self, indent: int):
        """The block value whose lines start at `indent` or deeper."""
        head = self.peek()
        if head is None or head[1] < indent:
            return None
        n, ind, text = head
        if text == "-" or text.startswith("- "):
            return self.seq(ind)
        if _key_split(text, n) is not None:
            return self.map(ind)
        self.at += 1
        value = self.inline(text, n)
        nxt = self.peek()
        if nxt is not None and nxt[1] >= ind:
            raise YamlError("a value runs on to a line it cannot be joined to; quote it", nxt[0])
        return value

    def inline(self, text: str, n: int):
        """A value written on its key's line (or its dash's): a scalar, or an inline list or map."""
        _refuse(text, n)
        if text[:1] in "[{":
            depth, joined, at = 0, text, self.at
            while True:
                depth = self._depth(joined, n)
                if depth <= 0 or at >= len(self.lines):
                    break
                joined += " " + self.lines[at][2]
                at += 1
            if depth > 0:
                raise YamlError("an inline list or map is never closed", n)
            self.at = at
            return _Flow(joined, n).whole()
        if text[:1] in "'\"":
            value, rest = self._quoted_value(text, n)
            if rest.strip():
                raise YamlError(f"unexpected {rest.strip()!r} after quoted text", n)
            return value
        return resolve(text)

    def _quoted_value(self, text: str, n: int) -> tuple[object, str]:
        """A quoted value starting `text` on line `n`, read on across the raw lines after it when it runs on,
        and what follows its closing quote, without the comment."""
        try:
            value, j = _quoted(text, 0, n)
            return value, _uncomment(text[j:], n)
        except _Unclosed:
            pass
        joined, last = text, n
        while last < len(self.raw):
            joined += "\n" + self.raw[last]
            last += 1
            try:
                value, j = _quoted(joined, 0, n)
            except _Unclosed:
                continue
            # The meaningful lines this value swallowed are its own, not the document's.
            while self.at < len(self.lines) and self.lines[self.at][0] <= last:
                self.at += 1
            return value, _uncomment(joined[j:], last)
        raise YamlError(f"the text opened with {text[0]} is never closed", n)

    @staticmethod
    def _depth(s: str, n: int) -> int:
        depth, i = 0, 0
        while i < len(s):
            ch = s[i]
            if ch in "'\"":
                _, i = _quoted(s, i, n)
                continue
            depth += ch in "[{"
            depth -= ch in "]}"
            i += 1
        return depth

    def text_block(self, header: str, n: int, parent: int) -> str:
        """A `|` or `>` block: the raw lines under the key, deeper than it."""
        m = _BLOCK.fullmatch(header)
        if not m:
            raise YamlError(f"{header!r} is not a block of text", n)
        style = m.group(1) or m.group(4)
        chomp = m.group(2) if m.group(1) else m.group(6)
        given = m.group(3) if m.group(1) else m.group(5)
        # Read the raw lines after line n, as they are, until one is shallower than the block.
        raw_lines, k = [], n
        while k < len(self.raw):
            raw = self.raw[k]
            if raw.strip() and len(raw) - len(raw.lstrip(" ")) <= parent:
                break
            raw_lines.append(raw)
            k += 1
        while raw_lines and not raw_lines[-1].strip() and chomp != "+":
            raw_lines.pop()
        content = [r for r in raw_lines if r.strip()]
        width = int(given) + parent if given else (min(len(r) - len(r.lstrip(" ")) for r in content) if content else 0)
        body = [r[width:] if r.strip() else "" for r in raw_lines]
        # Skip the meaningful lines this block swallowed.
        while self.at < len(self.lines) and self.lines[self.at][0] <= k:
            self.at += 1
        trail = 0
        while body and body[-1] == "":
            body.pop()
            trail += 1
        text = "\n".join(body) if style == "|" else self._fold(body)
        if chomp == "-" or not text:
            return text
        return text + "\n" + ("\n" * trail if chomp == "+" else "")

    @staticmethod
    def _fold(body: list[str]) -> str:
        """A `>` block's lines folded: a break between two lines of prose becomes a space, an empty line a break,
        and a more-indented line keeps the breaks around it."""
        out, pending, started, prev_more = [], 0, False, False
        for line in body:
            if line == "":
                pending += 1
                continue
            more = line[:1] == " "
            if not started:
                out.append("\n" * pending)
                started = True
            elif pending:
                out.append("\n" * (pending + (1 if more or prev_more else 0)))
            else:
                out.append("\n" if more or prev_more else " ")
            out.append(line)
            pending, prev_more = 0, more
        return "".join(out)

    def map(self, indent: int) -> dict:
        out: dict = {}
        while True:
            head = self.peek()
            if head is None or head[1] < indent:
                return out
            n, ind, text = head
            if ind > indent:
                raise YamlError("this line is indented deeper than the map it sits in", n)
            if text == "-" or text.startswith("- "):
                raise YamlError("a list item where the map expects a key", n)
            split = _key_split(text, n)
            if split is None:
                raise YamlError(f"expected `key: value`, not {text!r}", n)
            key, rest = split
            if key in out:
                raise YamlError(f"{key!r} is given twice", n)
            self.at += 1
            if rest[:1] in "|>" and _BLOCK.fullmatch(rest):
                out[key] = self.text_block(rest, n, indent)
            elif rest:
                out[key] = self.inline(rest, n)
                nxt = self.peek()
                if nxt is not None and nxt[1] > indent:
                    raise YamlError("a value runs on to a line it cannot be joined to; quote it", nxt[0])
            else:
                nxt = self.peek()
                if nxt is not None and nxt[1] > indent:
                    out[key] = self.node(nxt[1])
                elif nxt is not None and nxt[1] == indent and (nxt[2] == "-" or nxt[2].startswith("- ")):
                    out[key] = self.seq(indent)
                else:
                    out[key] = None

    def seq(self, indent: int) -> list:
        out: list = []
        while True:
            head = self.peek()
            if head is None or head[1] < indent:
                return out
            n, ind, text = head
            if ind > indent:
                raise YamlError("this line is indented deeper than the list it sits in", n)
            if not (text == "-" or text.startswith("- ")):
                return out
            rest = text[1:].lstrip(" ")
            if not rest:
                self.at += 1
                nxt = self.peek()
                out.append(self.node(nxt[1]) if nxt is not None and nxt[1] > indent else None)
                continue
            # The item starts on the dash's line: read it as if it began there, at its own indent.
            inner = ind + len(text) - len(rest)
            self.lines[self.at] = (n, inner, rest)
            if rest[:1] in "|>" and _BLOCK.fullmatch(rest):
                self.at += 1
                out.append(self.text_block(rest, n, indent))
            elif rest == "-" or rest.startswith("- ") or _key_split(rest, n) is not None:
                out.append(self.node(inner))
            else:
                self.at += 1
                out.append(self.inline(rest, n))
                nxt = self.peek()
                if nxt is not None and nxt[1] > indent:
                    raise YamlError("a value runs on to a line it cannot be joined to; quote it", nxt[0])

    def document(self):
        if not self.lines:
            return None
        value = self.node(self.lines[0][1])
        if self.at < len(self.lines):
            n, _, text = self.lines[self.at]
            raise YamlError(f"cannot place {text!r} in the document", n)
        return value


def loads(text: str):
    """The value a YAML document holds: a map, a list, a scalar, or None for an empty file."""
    return _Reader(text).document()
