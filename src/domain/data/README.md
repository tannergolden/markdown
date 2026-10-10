<!--
title: '🗃️ DATA'
description: 'The kit''s data: the glyph outlines and their licences, the print catalogue, and the repository population the trophies are calibrated against.'
tags: [source, domain, data, fonts]
category: docs
-->

<div align="center">

# 🗃️ DATA

<a name="top"></a>

**What the kit draws with, kept as data rather than code.**

_Read once. Handed in._

</div>

---

## 💡 What This Folder Is For

The files the kit draws with: the outlines of every glyph it letters in, with
each font's licence beside them, in [`fonts/`](fonts/); the catalogue of prints,
in [`prints.json`](prints.json); and the population of real repositories the
trophies' thresholds are calibrated against, in [`calibration/`](calibration/).

The domain never opens them. [`resources.py`](../../infra/resources.py) reads
each one by name and hands it to the domain, so a drawing is the same bytes
wherever it is made.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                          | Purpose                                                                                                  |
| :----------------------------- | :------------------------------------------------------------------------------------------------------- |
| [`calibration/`](calibration/) | The repository population the trophies' thresholds are calibrated against, measured by `make calibrate`. |
| [`fonts/`](fonts/)             | The glyph outlines the kit letters in, a table per face, with each font's licence beside it.             |
| [`prints.json`](prints.json)   | The print catalogue: each print's label, and the colour tokens of its line, its ink and its sheet.       |
| [`README.md`](README.md)       | This file.                                                                                               |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself.

---

<div align="center">

**Data in, drawings out.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
