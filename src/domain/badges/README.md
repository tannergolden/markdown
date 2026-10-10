<!--
title: '🏅 BADGES'
description: 'The badges: the classic styles and their blueprint plates, what a live badge measures, and the shields.io links a page localizes.'
tags: [source, domain, badges, svg]
category: docs
-->

<div align="center">

# 🏅 BADGES

<a name="top"></a>

**Rows of badges under the header, drawn from the settings.**

_Static by default. Live when measured._

</div>

---

## 💡 What This Folder Is For

The badges a page lists under `badges:` in `.github/markdown.yaml`, drawn as
committed SVGs: the six classic styles a README already knows, lettered in the
reader's Verdana, and their blueprint plates, drawn the way a banner is.

A badge that names a `measure:` is live: the kit measures it on every run, or a
workflow sets it with `markdown-kit set`, and only a live badge wears the gold
label. Live badges are drawn into `assets/badges/dynamic/` and every other badge
into `assets/badges/static/`, beside the shields.io links a page carries, drawn
once and localized.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                        | Purpose                                                                                                  |
| :--------------------------- | :------------------------------------------------------------------------------------------------------- |
| [`__init__.py`](__init__.py) | The badges: rows of them under the header, drawn from the settings, the live ones measured on every run. |
| [`classic.py`](classic.py)   | The classic badges: six styles a README already knows, lettered in the reader's Verdana.                 |
| [`data.py`](data.py)         | The `badges:` section of a page's settings, and the files and README block the badges make.              |
| [`live.py`](live.py)         | What a live badge measures, and the state each value is drawn in.                                        |
| [`localize.py`](localize.py) | Shields.io links in a repository's Markdown, drawn once as classic badges and committed.                 |
| [`plates.py`](plates.py)     | The blueprint plates: every badge style again, drawn the way a banner is drawn.                          |
| [`README.md`](README.md)     | This file.                                                                                               |
| [`settings.py`](settings.py) | A badge's value set from outside a run: `markdown-kit set NAME=MESSAGE[:COLOR]`.                         |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself.

---

<div align="center">

**Gold means live. Everything else is static.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
