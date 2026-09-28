<!--
title: '📄 ADR-0004: STANDARD AS THE DEFAULT THEME'
description: 'A page that names no theme is drawn in standard, the original badges'' own look.'
tags: [adr, architecture, decisions, themes]
category: docs
status: 'Accepted'
date: '2026-09-28'
evidence: 'N/A'
-->

<div align="center">

# 📄 ADR-0004: STANDARD AS THE DEFAULT THEME

<a name="top"></a>

**A page that names no theme is drawn in `standard`, the original badges' own look.**

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

The banners kit drew every page in a print, the blueprint unless told otherwise: a drafting sheet with a grid, a border and a title block. The badges kit's default badges are something else: flat panels, a black label beside a coloured message, bold capitals and line icons. A page drawn by one kit with its defaults mixed the two looks. The kit needs one default theme, and it has to be settled before v1.0: the standards count a changed default as a breaking change, so changing it later would mean a v2.

---

## 🚦 Decision Drivers

- **One look out of the box**: the header, the footer and the badges should match on a page that sets nothing.
- **Stable**: the default is settled before the first release.

---

## 🏗️ Considered Options

1. **`blueprint`**, the banners kit's default.
2. **`standard`**, a new theme drawn from the original badges.

---

## ✅ Decision Outcome

**Chosen Option**: `standard`

### Rationale for Selection

`standard` matches the badges a README already carries, so a page that sets nothing reads as one family: flat panels, a black label with a coloured accent, bold letter-spaced capitals and the badges' 64 icons. Its lettering is drawn as outlines, like every other theme's, so it looks the same on every screen. The prints stay one line away (`theme: blueprint`, or any other), `rainbowprint` walks the spectrum, and a repository can add prints of its own. The holiday sets take over from whichever theme a page is in and hand it back.

---

## 📈 Consequence Matrix

| Category         | Impact / Consequence                                                                  |
| :--------------- | :------------------------------------------------------------------------------------ |
| **Positive (+)** | A page that sets nothing matches its badges.                                          |
| **Negative (-)** | A page that relied on the blueprint default names it once: `theme: blueprint`.        |
| **Neutral (~)**  | Every print is still drawn, and each keeps its name.                                  |

---

## ⚖️ Trade-off Comparative

### Option A: `blueprint`

- ✅ What banners pages look like today.
- ❌ Does not match the default badges beside it.

### Option B: `standard`

- ✅ One look, matching the badges, out of the box.
- ❌ A new theme to draw and keep.

---

## 🔗 Traceability & Links

- [ADR-0001](ADR-0001-One-Kit-One-Stub.md): one theme sets the whole page.
- [ADR-0003](ADR-0003-Holiday-Windows.md): the holiday sets hand back to the page's theme.

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
