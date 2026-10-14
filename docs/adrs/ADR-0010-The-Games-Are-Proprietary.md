<!--
title: '📄 ADR-0010: THE GAMES ARE PROPRIETARY'
description: 'The Game Materials, everything in this repository about the games on the owner''s profile, are proprietary to the owner, under LICENSE-GAMES; the rest of the kit stays MIT.'
tags: [adr, licence, legal, proprietary, ai]
category: docs
status: 'Accepted'
date: '2026-10-14'
evidence: 'N/A'
-->

<div align="center">

# 📄 ADR-0010: THE GAMES ARE PROPRIETARY

<a name="top"></a>

**The Game Materials, everything in this repository about the games on the owner's profile, are proprietary to the owner, under LICENSE-GAMES; the rest of the kit stays MIT.**

_All rights reserved. No permission given. No AI reproduction._

</div>

---

## 📋 Meta Information

> [!NOTE]
> **Status**, **Date**, and **Evidence** live in the frontmatter above - they feed the generated [ADR index](README.md), so they are recorded once. This table records who was involved.

| Attribute     | Specification                                   |
| :------------ | :---------------------------------------------- |
| **Deciders**  | Tanner Golden (owner)                           |
| **Consulted** | Claude Code                                     |
| **Informed**  | Everyone who uses the kit                       |

---

## 🎯 Context & Problem Statement

This repository was published under the MIT License as a whole: the kit
anyone may use, and with it everything that draws the games on the owner's
profile, their boards, pieces, Hall of Fame, replays and designs. The owner
asked that everything about the games, here and in tannergolden/cheat and
tannergolden/play, be for the owner alone: never reusable or resellable, with
no permission ever given to anyone, and never reproduced by an AI, in a
licence that reads as one. The kit itself is not about the games.

## 🚦 Decision Drivers

- **Ownership**: the games' engine, designs and everything about them are the
  owner's alone, for the owner's use alone.
- **No reuse, no resale**: no one may copy, adapt, sell or resell them, and no
  permission will ever be given.
- **No AI**: no AI system may train on them or reproduce them.
- **Legitimacy**: the licence must hold up as a licence: defined terms, the
  rights the hosting platform requires kept, third parties' rights left alone.

## 🏗️ Considered Options

1. **Keep a permissive licence** such as MIT.
2. **A published source-available licence**, such as PolyForm Strict.
3. **A proprietary licence of the owner's own**, reserving every right, with
   an AI and text-and-data-mining reservation.
4. **Option 3 over the whole repository**, kit and all.

## ✅ Decision Outcome

**Chosen Option**: Option 3.

### Rationale for Selection

- **Nothing is granted.** Every right is reserved; no licence arises by
  implication, estoppel or availability on GitHub, and no request for
  permission will be granted.
- **No AI.** No AI system may train on, take as input, retrieve from or
  reproduce the materials, and every right against text and data mining is
  reserved, under Article 4(3) of the EU's Digital Single Market Directive
  among others.
- **The owner's own tools keep working.** Use by the owner, or by a person,
  service or AI acting solely on the owner's instruction and for the owner's
  benefit, such as the workflows, the apps and Claude Code, is not
  restricted, and gives the tool and its provider no right of its own.
- **Third parties keep their rights.** Shared workflows, actions and any
  component under its own licence stay under it.
- **The games alone.** LICENSE-GAMES lists every path that is about the
  games, and covers any passage about them elsewhere; LICENSE prefaces the
  MIT License with a notice that it grants no right in them. The kit, which
  is not about the games, stays MIT, so **Option 4** would take from its users
  more than the owner asked.
- **Earlier versions.** Versions released under the MIT License before
  14 October 2026 stay under it as to those versions only, as the law
  requires; everything from that day on is under LICENSE-GAMES alone.
- **Kept current.** A new or moved game file joins LICENSE-GAMES' paths in the
  same commit, and a game source file says `LicenseRef-Proprietary`.
- **Option 1** grants everyone the very rights the owner withholds, and
  **Option 2** still permits some uses, and says nothing of AI.

## 📈 Consequence Matrix

| Category         | Impact / Consequence                                                                 |
| :--------------- | :----------------------------------------------------------------------------------- |
| **Positive (+)** | The games are reserved, and the kit stays free to use                                 |
| **Negative (-)** | Releases already published stay MIT as to those versions; GitHub shows the licence as "Other" |
| **Neutral (~)**  | The page's header and footer drop the licence GitHub can no longer name as one         |

## 🔗 Traceability & Links

- The licence itself, at the root of this repository
- The same licence in tannergolden/cheat, tannergolden/play and
  tannergolden/markdown, each over its own games' materials

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
