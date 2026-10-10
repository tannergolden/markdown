<!--
title: '💻 APPLICATION SOURCE'
description: 'The application source, split into three layers whose dependencies point inward.'
tags: [source, architecture, layers, scaffold]
category: docs
-->

<div align="center">

# 💻 APPLICATION SOURCE

<a name="top"></a>

**Where the kit draws a page: the drawing at the centre, the run around it.**

_Dependencies point inward._

</div>

---

## 💡 What This Folder Is For

This is the Markdown Kit: Python and its standard library, with nothing to
install. Its one executable is [`markdown-kit.py`](markdown-kit.py), the
composition root, which hands the kit's data to the domain, builds the real
ports from `infra`, and runs the command line.

The three layers keep what a page **looks like** apart from how a run is
**delivered** and what it **talks to**. `domain` decides every pixel and does no
I/O, so a drawing is the same bytes wherever it is made. `app` settles the page
and runs each part. `infra` reaches git, GitHub, the disk and the clock.

This directory is **yours from the first commit**. Nothing here syncs, and
nothing upstream will ever write to it or delete from it: 🔄 Template Sync
leaves this whole folder to you, this README included.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                                | Purpose                                                                                                                     |
| :----------------------------------- | :-------------------------------------------------------------------------------------------------------------------------- |
| [`app/`](app/README.md)              | The application layer: entry points and use cases that orchestrate the domain and receive infrastructure through injection. |
| [`domain/`](domain/README.md)        | The domain layer: entities, business rules, and pure logic that import nothing outside themselves.                          |
| [`infra/`](infra/README.md)          | The infrastructure layer: adapters that implement the domain interfaces against databases, networks, and outside services.  |
| [`markdown-kit.py`](markdown-kit.py) | Markdown-kit: the composition root.                                                                                         |
| [`README.md`](README.md)             | This file.                                                                                                                  |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push. Each layer logs its own
files.

---

## 🧱 The One Rule Between Them

Dependencies point inward. `domain` imports nothing outside itself, `app`
orchestrates the domain and receives `infra` through injection, and `infra`
implements interfaces the other two declare. Only a composition root imports
`infra` directly.

The full rules, and what each module holds, are in
[Source Code](../docs/technical/Source-Code.md); the stack and the Makefile
targets CI runs are in
[Technology Stack & Tooling](../docs/technical/Technology-Stack-&-Tooling.md).
`make lint` reads every module's imports and fails a change that breaks them.

---

<div align="center">

**The domain at the centre, and everything else pointing at it.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
