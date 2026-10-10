<!--
title: '📄 ADR-0002: STANDARD LIBRARY ONLY'
description: 'The kit is Python and its standard library, with nothing to install, and reads its own YAML.'
tags: [adr, architecture, decisions, dependencies]
category: docs
status: 'Accepted'
date: '2026-09-28'
evidence: 'N/A'
-->

<div align="center">

# 📄 ADR-0002: STANDARD LIBRARY ONLY

<a name="top"></a>

**The kit is Python and its standard library, with nothing to install, and reads its own YAML.**

_Formalized rationale. Transparent intent. Auditable evolution._

</div>

---

## 📋 Meta Information

| Attribute     | Specification                                         |
| :------------ | :---------------------------------------------------- |
| **Deciders**  | Tanner Golden                                         |
| **Consulted** | Claude Code                                           |
| **Informed**  | Anyone contributing to the kit or running it locally  |

---

## 🎯 Context & Problem Statement

The kit runs inside other people's workflows, every day, on hosted runners. Anything it installs is a download on every run, a version to pin and keep current, and a way for a run to fail that has nothing to do with the page. The three kits it replaced were standard-library Python already, with one exception: YAML. The badges and banners kits used PyYAML when it happened to be installed and a small reader of their own when it was not, and the elements kit needed PyYAML outright. The same file could read differently depending on the machine, because PyYAML reads `on`, `no` and a date as a boolean and a date, where the small readers read them as text.

One settings file with a section per part is deeper than those small readers could read.

---

## 🚦 Decision Drivers

- **Nothing to install**: a run should need `python3` and `git`, which every runner has.
- **The same answer everywhere**: a settings file must read the same on every machine.
- **Errors a person can act on**: a mistake in the settings is named with its line.

---

## 🏗️ Considered Options

1. **Depend on PyYAML**: install it on every run.
2. **Use PyYAML when present, a small reader otherwise**: what the old kits did.
3. **Read YAML ourselves, always**: a reader of the part of YAML 1.2 a settings file uses, refusing the rest by line.

---

## ✅ Decision Outcome

**Chosen Option**: Read YAML ourselves, always

### Rationale for Selection

`src/infra/yaml_reader.py` reads block maps and lists at any depth, inline lists and maps, quoted text (including text that runs over lines), `|` and `>` blocks, and the YAML 1.2 core schema's booleans, nulls and numbers. It refuses anchors, aliases, tags, `?` keys, a second document, a key given twice and a tab in the indentation, naming the line. It never uses PyYAML, even when it is there, so a file reads the same everywhere. Read with PyYAML set to the same core schema, every one of the 225 YAML files in the family's repositories comes out the same.

The rest follows the same rule: glyphs are drawn as paths from outlines shipped as data, time zones come from the standard `zoneinfo`, and GitHub is called with `urllib`.

---

## 📈 Consequence Matrix

| Category         | Impact / Consequence                                                                         |
| :--------------- | :------------------------------------------------------------------------------------------- |
| **Positive (+)** | No install step, no dependency to update, and one reading of every settings file.            |
| **Negative (-)** | The kit owns a YAML reader and its tests; YAML's rarer features are refused, not read.       |
| **Neutral (~)**  | Dependabot has no ecosystem to watch in the kit itself; the workflows are still watched.     |

---

## ⚖️ Trade-off Comparative

### Option A: PyYAML

- ✅ All of YAML, maintained by others.
- ❌ An install on every run, and YAML 1.1's `on`, `no` and dates.

### Option B: PyYAML when present

- ✅ No install.
- ❌ The same file reads two ways depending on the machine.

### Option C: Our own reader

- ✅ No install, one reading, errors by line.
- ❌ A module to own, and a subset of YAML.

---

## 🔗 Traceability & Links

- [Technology Stack & Tooling](../technical/Technology-Stack-&-Tooling.md)
- [ADR-0001](ADR-0001-One-Kit-One-Stub.md): why there is one settings file.

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
