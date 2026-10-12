<!--
title: '📎 FIXTURES'
description: 'What the tests compare against: the golden files of the badges and trophies, a sample page''s settings, the driftmark specimen and a sample game.'
tags: [testing, fixtures, golden-files, specimens]
category: docs
-->

<div align="center">

# 📎 FIXTURES

<a name="top"></a>

**What the tests hold every drawing to.**

_A golden file changes only on purpose._

</div>

---

## 💡 What This Folder Is For

[`badges/`](badges/) and [`trophies/`](trophies/) hold the golden files the unit
tests compare every badge and trophy drawing against. [`sample/`](sample/) holds
the settings `make draw` draws its sample pages from, and
[`driftmark/`](driftmark/) is the specimen: a repository's page that `make lint`
and the tests draw in every design. [`chess.yaml`](chess.yaml) is a sample game
of @tannergolden's, which the theme-sets page draws the game's sheets from in
every tone.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                               | Purpose                                                                                                                                                                                      |
| :---------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`badges/`](badges/)                | The golden file every badge style is checked against.                                                                                                                                        |
| [`driftmark/`](driftmark/README.md) | The specimen: driftmark's page and settings, which `make lint` lints in every design and the tests draw from.                                                                                |
| [`sample/`](sample/)                | The settings `make draw` draws its sample profile and repository pages from.                                                                                                                 |
| [`trophies/`](trophies/)            | The golden file every trophy card and style is checked against.                                                                                                                              |
| [`chess.yaml`](chess.yaml)          | The sample game the theme-sets page draws the chess sheets from: game 13 of @tannergolden against GitHub, on its 21st move, with GitHub's king in check, and a Hall of Fame of twelve games. |
| [`README.md`](README.md)            | This file.                                                                                                                                                                                   |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself.

---

<div align="center">

**Change a drawing on purpose, or not at all.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
