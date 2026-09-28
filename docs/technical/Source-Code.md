<!--
title: '💻 SOURCE CODE'
description: 'Architecture and standards for the application source code.'
tags: [architecture, code, technical, structure]
category: docs
-->


<div align="center">

# 💻 SOURCE CODE

<a name="top"></a>

**The primary directory for all application logic, business rules, and architectural components.**

_Logic-first. Clean architecture. Testable by design._

</div>

---

## 🎯 Purpose & Intent

This directory houses the foundational code of the project. It is structured to separate concerns and ensure that the core logic is isolated from external frameworks or delivery mechanisms.

For this kit, "the core logic" is everything that decides what a README page looks like: the palette, the lettering, the SVG canvas and its lint, the themes, the holiday calendar and the README's blocks. None of it reads a file, calls GitHub or asks the clock, so a drawing is the same bytes wherever it is made, and every rule can be tested in isolation.

### Source Root

- **Location**: `src/`
- **Language**: Python 3.10 or later, standard library only (see [ADR-0002](../adrs/ADR-0002-Standard-Library-Only.md))
- **Module system**: Python packages, with `src/` put on the import path by the composition root `src/markdown-kit.py` (and by `tests/support.py` for the tests)

### Recommended Sub-structure

- **`/app`**: Application-specific logic and entry points. Here: the command line (`cli.py`); reading a repository's settings (`config.py`); settling one run's page, its mode, subject, day and theme (`page.py`); the run itself, with render, check and preview (`run.py`); each part's measuring and planning (`parts/banners.py`, `parts/badges.py`, `parts/elements.py`); and `Ports`, everything the application is handed to reach outside itself (`ports.py`).
- **`/lib`**: Sharable libraries and utility functions. This kit has none: every helper it has knows the kit's rules, so it belongs in `domain`.
- **`/domain`**: Core business entities and logic (framework-agnostic). Here: `palette`, `lettering`, `canvas`, `draw`, `prints`, `drafting` (the paper a print is drawn on), `holidays`, `readme`, `settings`, `lock` and `history`; the parts' drawings, `banners/` (the header, the footer and the links under it), `badges/` (the classic styles and their blueprint plates, the live badges' states, and localizing shields.io links) and `elements/` (the schematic, instruments, milestones, roster, certificate and placard); and their data under `domain/data/` (the glyph outlines and their licences, and the print catalogue).
- **`/infra`**: Implementation details (database, external APIs). Here: `files`, `git`, `github`, `clock`, `resources` (which reads `domain/data/` and hands it in) and `yaml_reader`.

The one executable is `src/markdown-kit.py`, the composition root: it reads the kit's data into the domain, builds the real `Ports` from `infra`, and runs the command line.

---

## 🧱 Layering Rules

Dependencies must point inward - the domain never imports from delivery or infrastructure:

1. **`domain` imports nothing** outside itself (and the standard library), and does no I/O at all: no `open`, `os`, `pathlib`, `subprocess`, `urllib` or `zoneinfo`. What it draws with arrives through `lettering.use()` and `prints.use()`.
2. **`app` orchestrates**: it may import `domain`, and receives `infra` via injection, as the functions and values of a `Ports`. It never imports `infra`.
3. **`infra` implements** what `domain` and `app` need, and may import `domain`; nothing imports `infra` directly except the composition root, `src/markdown-kit.py`, and the tests, which stand where it stands.
4. **There is no `lib`**: a helper that knows the kit's rules belongs in `domain`.

`tests/unit/test_layering.py` reads every module's imports and holds each layer to these rules, and `make lint` runs it, so a change that breaks them fails CI.

> [!IMPORTANT]
> Every module must be reachable by this project's unified lint, test, and build commands - the ones CI is configured to run. Wire new tooling into those entry points rather than into bespoke scripts nobody else invokes.

---

## 📏 Quality Bar

- **Naming & style**: kebab-case files, formatter-enforced layout - see [Repository Hygiene](https://github.com/tannergolden/standards/blob/Development/docs/operations/Repository-Hygiene.md). The executable is kebab-case (`markdown-kit.py`); every module that is imported is snake_case (`yaml_reader.py`), the interpreter exception Repository Hygiene makes, because a module name cannot contain a hyphen.
- **Tests live beside the layer they verify** and follow the canonical [Testing Strategy](https://github.com/tannergolden/standards/blob/Development/docs/distribution/Testing-Strategy.md): the rules in `tests/unit/`, git and files on real temporary repositories in `tests/integration/`, and the command line as a person runs it in `tests/e2e/`.
- **Comments explain _why_**, decisions get an [ADR](../adrs/Architecture-Decision-Records.md).

### 🔗 See also

> [!TIP]
> Every canonical guide is indexed in the [&#x1F4DA; Standards Index](https://github.com/tannergolden/standards/blob/Development/docs/README.md). If you rename or move a file, update every reference to it across the repository to prevent link drift.

---

<div align="center">

**Structured for logic. Built for scale.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
