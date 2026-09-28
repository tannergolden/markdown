# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Every GraphQL document the kit sends, checked before GitHub finds a typo one run at a time.

Braces balance, every variable used is declared, and with a schema every
selected field exists on its parent type and every argument is one the field
takes. The schema is the `@octokit/graphql-schema` npm package's
`schema.json`, pointed at by GITHUB_GRAPHQL_SCHEMA; without it only the
structural checks run.

    npm pack @octokit/graphql-schema && tar xzf octokit-graphql-schema-*.tgz
    GITHUB_GRAPHQL_SCHEMA=package/schema.json python3 tests/gql_check.py
"""
from __future__ import annotations

import importlib
import json
import os
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tests import support  # noqa: E402,F401  (puts src/ on the path)

TOKEN = re.compile(r"\.\.\.|[A-Za-z_][A-Za-z0-9_]*|\$[A-Za-z_][A-Za-z0-9_]*|[{}():\[\]!,=]|\"(?:[^\"\\]|\\.)*\"|-?\d+(?:\.\d+)?")
# Every module that talks to GitHub's GraphQL API.
MODULES = ("app.parts.banners", "app.parts.elements", "app.parts.trophies.profile", "app.parts.trophies.repository",
           "app.parts.trophies.scan")


def documents() -> dict:
    """Every GraphQL document in MODULES, by module and name."""
    out = {}
    for name in MODULES:
        mod = importlib.import_module(name)
        for attr in dir(mod):
            v = getattr(mod, attr)
            if isinstance(v, str) and re.match(r"\s*query\b", v):
                out[f"{name.rsplit('.', 1)[-1]}.{attr}"] = v
    return out


class Schema:
    def __init__(self, path: Path):
        data = json.loads(path.read_text(encoding="utf-8"))
        s = data.get("data", data)["__schema"]
        self.types = {t["name"]: t for t in s["types"]}
        self.query = s["queryType"]["name"]

    @staticmethod
    def unwrap(t):
        while t.get("ofType"):
            t = t["ofType"]
        return t["name"]

    def field(self, type_name: str, field: str):
        t = self.types.get(type_name) or {}
        for f in t.get("fields") or []:
            if f["name"] == field:
                return f
        return None

    def possible(self, type_name: str) -> list:
        t = self.types.get(type_name) or {}
        return [p["name"] for p in t.get("possibleTypes") or []]


def parse(doc: str) -> list:
    return TOKEN.findall(doc)


def check(name: str, doc: str, schema: Schema | None) -> list:
    problems = []
    depth = 0
    for ch in doc:
        depth += ch == "{"
        depth -= ch == "}"
        if depth < 0:
            break
    if depth != 0:
        problems.append(f"{name}: braces unbalanced ({depth:+d})")
        return problems
    toks = parse(doc)
    declared = set()
    used = set()
    i = 0
    # variables
    if toks[0] == "query":
        i = 1
        if toks[i] == "(":
            j = toks.index(")", i)
            declared = {t for t in toks[i:j] if t.startswith("$")}
            i = j + 1
    if not schema:
        used = {t for t in toks[i:] if t.startswith("$")}
        problems += [f"{name}: variable {v} used but not declared" for v in used - declared]
        return problems

    def walk(pos: int, parent: str) -> int:
        """pos is at '{'; returns the position after the matching '}'."""
        assert toks[pos] == "{", (name, pos, toks[pos])
        pos += 1
        while toks[pos] != "}":
            t = toks[pos]
            if t == "...":
                # ... on Type { ... }
                assert toks[pos + 1] == "on"
                sub = toks[pos + 2]
                if sub not in schema.possible(parent) and sub != parent:
                    problems.append(f"{name}: '... on {sub}' is not a possible type of {parent}")
                pos = walk(pos + 3, sub)
                continue
            fname = t
            pos += 1
            if toks[pos] == ":":  # alias
                fname = toks[pos + 1]
                pos += 2
            if fname == "__typename":
                f = {"type": {"name": "String"}, "args": []}
            else:
                f = schema.field(parent, fname)
            if f is None:
                problems.append(f"{name}: {parent} has no field '{fname}'")
                f = {"type": {"name": "?"}, "args": []}
            if toks[pos] == "(":
                j = pos + 1
                argnames = {a["name"] for a in f.get("args") or []}
                nest = 0  # inside an object literal such as orderBy:{field:..., direction:...}
                while toks[j] != ")":
                    if toks[j] == "{":
                        nest += 1
                    elif toks[j] == "}":
                        nest -= 1
                    elif nest == 0 and toks[j + 1] == ":" and not toks[j].startswith("$"):
                        if f["type"]["name"] != "?" and toks[j] not in argnames:
                            problems.append(f"{name}: {parent}.{fname} takes no argument '{toks[j]}'")
                    if toks[j].startswith("$"):
                        used.add(toks[j])
                    j += 1
                pos = j + 1
            if toks[pos] == "{":
                pos = walk(pos, schema.unwrap(f["type"]))
        return pos + 1

    walk(i, schema.query)
    problems += [f"{name}: variable {v} used but not declared" for v in used - declared]
    return problems


def main() -> int:
    path = os.environ.get("GITHUB_GRAPHQL_SCHEMA")
    schema = Schema(Path(path)) if path and Path(path).exists() else None
    problems = []
    docs = documents()
    for name, doc in docs.items():
        problems += check(name, doc, schema)
    mode = "against the schema" if schema else "structurally (no schema)"
    if problems:
        print(f"{len(problems)} problems in {len(docs)} documents, checked {mode}:\n  " + "\n  ".join(problems))
        return 1
    print(f"{len(docs)} GraphQL documents valid, checked {mode}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
