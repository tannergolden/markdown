<!--
title: '📄 ADR-0005: THE KIT MEASURES LIVE BADGES'
description: 'A live badge names what it measures, and every run measures it, instead of another workflow setting its value.'
tags: [adr, architecture, decisions, badges]
category: docs
status: 'Accepted'
date: '2026-09-28'
evidence: 'N/A'
-->

<div align="center">

# 📄 ADR-0005: THE KIT MEASURES LIVE BADGES

<a name="top"></a>

**A live badge names what it measures, and every run measures it, instead of another workflow setting its value.**

_Formalized rationale. Transparent intent. Auditable evolution._

</div>

---

## 📋 Meta Information

| Attribute     | Specification                        |
| :------------ | :----------------------------------- |
| **Deciders**  | Tanner Golden                        |
| **Consulted** | Claude Code                          |
| **Informed**  | Everyone whose page the kit draws    |

---

## 🎯 Context & Problem Statement

The badges kit drew what its data file said. A live badge, the gold label whose colour is a state, got its value from outside: a second workflow measured something with `gh`, then called the badges action with `set: NAME=MESSAGE:COLOR`, which rewrote the data file and redrew the badge. A profile with two live badges needed a workflow of its own for it, on its own schedule, making its own commits, and the badge said whatever that workflow last set, whether or not the page had been redrawn since. With one kit and one stub, that second workflow is the one piece left outside the run.

---

## 🚦 Decision Drivers

- **One run, one commit**: everything the page shows is measured and drawn by the same run.
- **True alt text**: the README's words for a badge are written with the badge.
- **Check offline**: `check` redraws without a token, so what was measured has to be kept.
- **Nothing lost**: a value the kit cannot measure can still be set from outside.

---

## 🏗️ Considered Options

1. **Keep setting values from outside**: other workflows measure, and the kit only draws.
2. **The kit measures**: a badge names what it reads under `measure:`, and every run reads it.
3. **Link to live services**: a shields.io endpoint that GitHub fetches on every view.

---

## ✅ Decision Outcome

**Chosen Option**: 2, the kit measures, with option 1 kept as a command.

### Rationale for Selection

The three values pages carry most are ones the kit can read with the token it already has: a workflow's last finished run, how long ago a person last committed, and the latest release. A badge names one under `measure:`, and the run reads it with everything else, draws it in the state the standards give each value, and writes the README's words for it in the same commit. The lock keeps each value, so `check` redraws the same files offline. Anything else a page wants to show is still set from outside with `markdown-kit set NAME=MESSAGE[:COLOR]`, which rewrites the settings file in place and leaves the next run to draw it. A live service was never an option: the kit's rule is that nothing is fetched when a README is viewed.

---

## 📈 Consequence Matrix

| Category         | Impact / Consequence                                                                                  |
| :--------------- | :---------------------------------------------------------------------------------------------------- |
| **Positive (+)** | The profile's Health workflow retires, and its two badges are drawn by the run that draws the page.  |
| **Negative (-)** | A badge is only as fresh as the page's schedule, once a day by default.                               |
| **Neutral (~)**  | Each measured value is kept in the lock beside the others.                                            |

---

## ⚖️ Trade-off Comparative

### Option A: Values set from outside

- ✅ Any value at all, measured however a workflow likes.
- ❌ A second workflow, schedule and commit for every page that wants one.

### Option B: The kit measures

- ✅ One run and one commit, and the alt text is always the badge's.
- ❌ Only what the kit knows how to read, which `set` covers for the rest.

### Option C: Live services

- ✅ Always current.
- ❌ Fetched on every view from a service the page does not control, which the kit exists to avoid.

---

## 🔗 Traceability & Links

- [ADR-0001](ADR-0001-One-Kit-One-Stub.md): one run draws the whole page.
- [ADR-0004](ADR-0004-Standard-As-The-Default-Theme.md): the badges' own look is the default theme.

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
