<!--
title: '🧭 ARCHITECTURE DECISIONS'
description: 'Architecture decision records, one file per decision, each logged with its status, date and evidence.'
tags: [adr, architecture, decisions, index]
category: docs
-->

<div align="center">

# 🧭 ARCHITECTURE DECISIONS

<a name="top"></a>

**Every significant decision this project has made, and why, one record each.**

_One decision per record. One row per decision._

</div>

---

## 💡 What This Folder Is For

An architecture decision record (ADR) captures one significant decision: the
context it was made in, the options weighed, and the consequences accepted.
Every record lives in this folder, one file per decision, and the log below is
their index.

The folder is a living record, not a fill-in form, and its records are **yours
from the first commit**: nothing upstream ever writes, moves or removes one. It
arrives with no decisions in it and gains a row each time a record is written.
Only this README is ever updated from the template - when you run
🔄 Template Sync - merged with the rows your records add.

---

## 🎯 Why Decisions Are Recorded

The _why_ matters as much as the _what_. An auditable record of how the system
evolved lets every later contributor, human or AI, see the constraints and
trade-offs that shaped it before changing it.

- **Traceability**: every major architectural pivot is documented and numbered.
- **Context**: each decision is recorded with the situation it was made in.
- **Consequences**: the benefits and the technical debt are both written down.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log fields=status,date,evidence -->

| Entry                                                                                                | Status   | Date       | Evidence | Purpose                                                                                                                                                                                          |
| :--------------------------------------------------------------------------------------------------- | :------- | :--------- | :------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`ADR-0001-One-Kit-One-Stub.md`](ADR-0001-One-Kit-One-Stub.md)                                       | Accepted | 2026-09-28 | N/A      | Banners, badges, elements and trophies become one kit, run from one stub, in one daily run that makes one commit.                                                                                |
| [`ADR-0002-Standard-Library-Only.md`](ADR-0002-Standard-Library-Only.md)                             | Accepted | 2026-09-28 | N/A      | The kit is Python and its standard library, with nothing to install, and reads its own YAML.                                                                                                     |
| [`ADR-0003-Holiday-Windows.md`](ADR-0003-Holiday-Windows.md)                                         | Accepted | 2026-09-28 | N/A      | The holiday sets are on by default and take over for 3 to 7 days centred on each holiday; New Year's Day always runs 3.                                                                          |
| [`ADR-0004-Standard-As-The-Default-Theme.md`](ADR-0004-Standard-As-The-Default-Theme.md)             | Accepted | 2026-09-28 | N/A      | A page that names no theme is drawn in standard, the original badges' own look.                                                                                                                  |
| [`ADR-0005-The-Kit-Measures-Live-Badges.md`](ADR-0005-The-Kit-Measures-Live-Badges.md)               | Accepted | 2026-09-28 | N/A      | A live badge names what it measures, and every run measures it, instead of another workflow setting its value.                                                                                   |
| [`ADR-0006-A-Collection-Changes-With-The-Month.md`](ADR-0006-A-Collection-Changes-With-The-Month.md) | Accepted | 2026-10-07 | N/A      | A collection is twelve pixel designs on one subject; a page that picks it is drawn in the month's design, which changes on the first of every month.                                             |
| [`ADR-0007-A-Collection-Is-Drawn-By-One-Hand.md`](ADR-0007-A-Collection-Is-Drawn-By-One-Hand.md)     | Accepted | 2026-10-08 | N/A      | The twelve designs of a collection keep their own subjects and share one hand: the same light, inks, ground, flame, people, motion and the month's mark, so the year reads as one artist's work. |
| [`README.md`](README.md)                                                                             | -        | -          | -        | This file.                                                                                                                                                                                       |

<!-- AUTO-INDEX:END -->

**This log is the decision index, and nobody types its rows.** 🗂️ Machined
Indexes redraws it after every push from each record's own frontmatter.
**Status** is Proposed, Accepted, Superseded, or Deprecated; **Date** is when
the decision was made; **Evidence** links the research report(s) that informed
it, or reads N/A.

---

## 🌿 Adding A Decision

- [ ] Copy the [ADR template](../templates/ADR.md) into this folder as
      `ADR-NNNN-Short-Slug.md`, taking the next number.
- [ ] Set `status`, `date`, and `evidence` in its frontmatter, and write every
      section.
- [ ] Propose it in a pull request. Once merged, it is **Accepted**.

A later decision supersedes an earlier one rather than rewriting it: mark the
old record **Superseded** and link the new one.

---

## 🔗 See also

- [Documentation index](../README.md) - every document this project keeps
- [Standards Index](https://github.com/tannergolden/standards/blob/Development/docs/README.md) - the canonical engineering standards

---

<div align="center">

**Write the decision down while the reasons are still fresh.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
