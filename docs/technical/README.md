<!--
title: '🛠️ TECHNICAL'
description: 'How the kit is built: where each piece of its source lives, the stack and the Makefile targets CI runs, how a run works end to end, every kind of theme it draws, and how a collection is drawn.'
type: index
keywords: [architecture, tooling, themes, collections]
-->

<div align="center">

# 🛠️ TECHNICAL

<a name="top"></a>

**How the kit is built, written down where the code cannot say it.**

_Filled in from the seeds, for this kit._

</div>

---

## 💡 What This Folder Is For

The technical documents this project filled in from the seeds in
[`../templates/technical/`](../templates/technical/README.md), and the guide
every collection is drawn from. [Source Code](Source-Code.md) says where each
piece of the kit lives and the rules its layers are held to, [Technology Stack &
Tooling](Technology-Stack-&-Tooling.md) gives the stack and the Makefile targets
CI runs, [How A Run Works](How-A-Run-Works.md) follows one run from the stub to
its commit, [Themes and Sets](Themes.md) defines every kind of theme and set the
kit draws and how to add or remove each, and
[Drawing a Collection](Collections.md) is read before a collection is started or
changed.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                                                            | Purpose                                                                                                                                                                                                                               |
| :--------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [`Collections.md`](Collections.md)                               | How a collection is drawn: its hand first, then twelve designs in that hand, each reviewed beside the others until the year reads as one artist's work.                                                                               |
| [`How-A-Run-Works.md`](How-A-Run-Works.md)                       | One run of the kit from the stub to the commit: how the workflow fetches the kit, and how the page is settled, measured, planned, written, locked and committed. Read it before changing src/app/, the lock or the reusable workflow. |
| [`README.md`](README.md)                                         | This file.                                                                                                                                                                                                                            |
| [`Source-Code.md`](Source-Code.md)                               | Architecture and standards for the application source code.                                                                                                                                                                           |
| [`Technology-Stack-&-Tooling.md`](Technology-Stack-&-Tooling.md) | Declares the technology stack and maps it to the universal make interface.                                                                                                                                                            |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself.

---

<div align="center">

**Written down once, where the next change will look.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
