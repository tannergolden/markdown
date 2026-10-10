<!--
title: '🚀 APPLICATION LAYER'
description: 'The application layer: entry points and use cases that orchestrate the domain and receive infrastructure through injection.'
tags: [source, application-layer, use-cases, architecture]
category: docs
-->

<div align="center">

# 🚀 APPLICATION LAYER

<a name="top"></a>

**Entry points and use cases: the code that turns a request into domain work.**

_Orchestrate here. Decide in the domain._

</div>

---

## 💡 What This Folder Is For

The application layer is where the project starts and where each use case is
carried out: a command, a request handler, a scheduled job. It calls into
[`../domain/`](../domain/README.md) for every rule, and receives what it needs
from [`../infra/`](../infra/README.md) through injection, so swapping a database
or a transport never means rewriting a use case.

It may import `domain`. It never imports `infra` directly, except in the
composition root that wires the two together at startup.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                          | Purpose                                                                                                         |
| :----------------------------- | :-------------------------------------------------------------------------------------------------------------- |
| [`parts/`](parts/README.md)    | Each part of a page measured and planned on its own: the banners, the badges, the elements and the trophy case. |
| [`__init__.py`](__init__.py)   | The application: the command line and what each command does, start to finish.                                  |
| [`calibrate.py`](calibrate.py) | Measure the repository population the repository-mode tiers are set against: `markdown-kit calibrate`.          |
| [`cli.py`](cli.py)             | The command line: `markdown-kit &lt;command&gt;`.                                                               |
| [`config.py`](config.py)       | Reading a repository's settings: the file, the stub's inputs, and the defaults under both.                      |
| [`page.py`](page.py)           | One run's page: whose it is, which mode, what day, where its files go, and which theme it is drawn in.          |
| [`ports.py`](ports.py)         | Everything the application is handed to reach outside itself.                                                   |
| [`README.md`](README.md)       | This file.                                                                                                      |
| [`run.py`](run.py)             | A run, start to finish: measure the page, draw every part, write what changed, and say what moved.              |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself. A subfolder appears as one row, so give it a README of its own and
its row links to that.

---

<div align="center">

**Thin use cases over a thick domain.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
