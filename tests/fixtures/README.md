<!--
title: '📎 FIXTURES'
description: 'What the tests compare against: the golden files of the badges and trophies, a sample page''s settings, the driftmark specimen and a sample of each game.'
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
and the tests draw in every design. [`tictactoe.yaml`](tictactoe.yaml),
[`connectfour.yaml`](connectfour.yaml), [`checkers.yaml`](checkers.yaml) and
[`chess.yaml`](chess.yaml) are a sample game of each of @tannergolden's four,
which the theme-sets page draws the games' sheets from in every tone, each
checked as a run checks it.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                                  | Purpose                                                                                                                                                                                                                              |
| :------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`badges/`](badges/)                   | The golden file every badge style is checked against.                                                                                                                                                                                |
| [`driftmark/`](driftmark/README.md)    | The specimen: driftmark's page and settings, which `make lint` lints in every design and the tests draw from.                                                                                                                        |
| [`sample/`](sample/)                   | The settings `make draw` draws its sample profile and repository pages from.                                                                                                                                                         |
| [`trophies/`](trophies/)               | The golden file every trophy card and style is checked against.                                                                                                                                                                      |
| [`checkers.yaml`](checkers.yaml)       | The sample game the theme-sets page draws the Checkers sheets from: game 6 of @tannergolden against GitHub, which the house opened with the dark men, on its tenth move: the house has just jumped a man, and GitHub must jump back. |
| [`chess.yaml`](chess.yaml)             | The sample game the theme-sets page draws the chess sheets from: game 13 of @tannergolden against GitHub, on its 21st move, with GitHub's king in check, and a Hall of Fame of twelve games.                                         |
| [`connectfour.yaml`](connectfour.yaml) | The sample game the theme-sets page draws the Connect Four sheets from: game 4 of @tannergolden against GitHub, which the Arbiter opened for GitHub, so GitHub drops the dark discs and the house the light.                         |
| [`README.md`](README.md)               | This file.                                                                                                                                                                                                                           |
| [`tictactoe.yaml`](tictactoe.yaml)     | The sample game the theme-sets page draws the Tic-Tac-Toe sheets from: game 9 of @tannergolden against GitHub, which the Arbiter opened for GitHub with the centre, so GitHub plays X and the house O.                               |

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
