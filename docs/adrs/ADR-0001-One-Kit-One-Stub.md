<!--
title: '📄 ADR-0001: ONE KIT, ONE STUB'
description: 'Banners, badges, elements and trophies become one kit, run from one stub, in one daily run that makes one commit.'
tags: [adr, architecture, decisions, kit]
category: docs
status: 'Accepted'
date: '2026-09-28'
evidence: 'N/A'
-->

<div align="center">

# 📄 ADR-0001: ONE KIT, ONE STUB

<a name="top"></a>

**Banners, badges, elements and trophies become one kit, run from one stub, in one daily run that makes one commit.**

_Formalized rationale. Transparent intent. Auditable evolution._

</div>

---

## 📋 Meta Information

| Attribute     | Specification                                                              |
| :------------ | :------------------------------------------------------------------------- |
| **Deciders**  | Tanner Golden                                                              |
| **Consulted** | Claude Code, which surveyed the three kits and proposed the plan           |
| **Informed**  | Everyone whose README uses `tannergolden/banners`, `badges` or `trophies` |

---

## 🎯 Context & Problem Statement

A README drawn by the family took three kits in three repositories: banners (the header, the footer and, beside them, the elements), badges, and trophies. A page used them through a Markdown stub that fanned out to each kit's own workflow or action, on three schedules, with three config files, three lock files, three tokens and three marker schemes. Each kit carried its own copy of the palette, the icons, the print catalogue, the fonts, the lettering, the GitHub client, the YAML reader, the lock and the README writer, and some of those copies had nothing checking that they still matched.

A theme change or a holiday landed on the page in three commits, hours apart. And a person setting up a page had to learn three kits to use one.

---

## 🚦 Decision Drivers

- **One page, one change**: a theme, a holiday or a new release should reach the whole page at once.
- **One thing to learn**: a person adds one stub and, only if they want to, one settings file.
- **One copy of each shared piece**: the palette, the lettering, the client and the rest, each in one module with one set of tests.
- **Nothing lost**: everything the three kits do carries over.

---

## 🏗️ Considered Options

1. **Keep three kits, keep the fan-out stub**: each kit stays in its repository and the stub calls all three.
2. **Keep three kits, share a library**: the kits stay apart but import a common package for the shared pieces.
3. **One kit**: the three kits become one, in this repository, called from one stub, `tannergolden/markdown/.github/workflows/markdown.yml@v1`.

---

## ✅ Decision Outcome

**Chosen Option**: One kit

### Rationale for Selection

Only one kit gives a page one run and one commit, and removes the copies rather than keeping them in step. A shared library would still leave three workflows, three schedules and three commits, and the standards' own rule is to stay one package until a second consumer exists. The kit keeps three modes, profile, repository and organization, so everything the three kits covered is still covered, and organization pages are new.

What one kit means in practice:

- **One stub.** A page's workflow calls `markdown.yml@v1` once a day, with at most five inputs: `mode`, `theme`, `sign`, `holidays` and `holiday-days`.
- **One settings file.** Everything else is optional and lives in `.github/markdown.yaml`, a section per part, replacing the four config files and `themes.json`.
- **One lock.** `.github/markdown.lock.json` replaces the three.
- **One marker scheme.** `<!-- markdown:NAME:start -->` and its end. The old kits' markers are read and rewritten on the first run.
- **One commit a run**, drawn from one measurement.

---

## 📈 Consequence Matrix

| Category         | Impact / Consequence                                                                                   |
| :--------------- | :----------------------------------------------------------------------------------------------------- |
| **Positive (+)** | One run and one commit per page; one copy of every shared module; one place for issues and releases.   |
| **Negative (-)** | Every page moves to a new stub, settings file and lock, once; the old kits' repositories retire.       |
| **Neutral (~)**  | The files a page shows keep their names, widths and places in the README.                              |

---

## ⚖️ Trade-off Comparative

### Option A: Three kits and the fan-out stub

- ✅ Nothing moves.
- ❌ Three runs, three commits, three configs and three copies of every shared piece, drifting.

### Option B: Three kits and a shared library

- ✅ One copy of the shared code.
- ❌ Still three runs and three commits; a package with one real consumer.

### Option C: One kit

- ✅ One run, one commit, one settings file, one lock, one copy of everything.
- ❌ A one-time move for every page that uses the old kits.

---

## 🔗 Traceability & Links

- [Source Code](../technical/Source-Code.md): where each piece of the kit lives.
- [ADR-0002](ADR-0002-Standard-Library-Only.md): the kit installs nothing.
- [ADR-0003](ADR-0003-Holiday-Windows.md): how the holiday sets take over.
- [ADR-0004](ADR-0004-Standard-As-The-Default-Theme.md): the default theme.
- [ADR-0005](ADR-0005-The-Kit-Measures-Live-Badges.md): the live badges are measured in the same run.

### 🔗 See also

> [!TIP]
> Every canonical guide is indexed in the [&#x1F4DA; Standards Index](https://github.com/tannergolden/standards/blob/Development/docs/README.md). If you rename or move a file, update every reference to it across the repository to prevent link drift.

---

<div align="center">

**One decision. One record. Zero ambiguity.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
