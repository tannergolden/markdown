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
and the tests draw in every design. [`tictac.yaml`](tictac.yaml),
[`pentago.yaml`](pentago.yaml), [`checkers.yaml`](checkers.yaml) and
[`chess.yaml`](chess.yaml) are a sample game of each of @tannergolden's four,
and [`hall-of-fame.yaml`](hall-of-fame.yaml) a sample of their Hall of Fame,
which the theme-sets page draws the games' sheets from in every tone, each
checked as a run checks it. [`replays/`](replays/) holds the facts of one won
game of each, as the profile's engine writes them, which the replay tests draw.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                                    | Purpose                                                                                                                                                                                                              |
| :--------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`badges/`](badges/)                     | The golden file every badge style is checked against.                                                                                                                                                                |
| [`driftmark/`](driftmark/README.md)      | The specimen: driftmark's page and settings, which `make lint` lints in every design and the tests draw from.                                                                                                        |
| [`replays/`](replays/)                   | The facts each game's sample replay is drawn from, as the profile's engine wrote them: one won game of each.                                                                                                         |
| [`sample/`](sample/)                     | The settings `make draw` draws its sample profile and repository pages from.                                                                                                                                         |
| [`trophies/`](trophies/)                 | The golden file every trophy card and style is checked against.                                                                                                                                                      |
| [`checkers.yaml`](checkers.yaml)         | The sample game the theme-sets page draws the Checkers sheets from: game 6 of @tannergolden against GitHub, played as American checkers, so GitHub's Black moved first and the house plays White, as it always does. |
| [`chess.yaml`](chess.yaml)               | The sample game the theme-sets page draws the chess sheets from: game 13 of @tannergolden against GitHub, on its 21st move, with GitHub's king in check, and a Hall of Fame of twelve games.                         |
| [`hall-of-fame.yaml`](hall-of-fame.yaml) | A sample Hall of Fame of the four games on @tannergolden's profile, for the theme-sets page.                                                                                                                         |
| [`pentago.yaml`](pentago.yaml)           | The sample game the theme-sets page draws the Pentago sheets from: game 4 of @tannergolden against GitHub, under the Ghost Rule.                                                                                     |
| [`README.md`](README.md)                 | This file.                                                                                                                                                                                                           |
| [`tictac.yaml`](tictac.yaml)             | The sample game the theme-sets page draws the Tic-Tac sheets from: game 9 of @tannergolden against GitHub, under the Ghost Rule.                                                                                     |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself.

---

<div align="center">

**Change a drawing on purpose, or not at all.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the terms in [LICENSE](/LICENSE).

</div>
