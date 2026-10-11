<!--
title: '♟️ CHESS'
description: 'The chess elements: the game on @tannergolden''s profile and its Hall of Fame, one layout in every theme.'
tags: [source, domain, elements, chess, svg]
category: docs
-->

<div align="center">

# ♟️ CHESS

<a name="top"></a>

**The game on @tannergolden's profile, drawn in every theme.**

_One layout, two materials._

</div>

---

## 💡 What This Folder Is For

The game played on @tannergolden's profile, and only there: `chess`, the board
as it stands with the state of play beside it, and `chess-hall`, the series
between the house and GitHub with its podium and everyone who has won. The
profile's own engine plays the game and writes what both draw into the page's
settings after every move ([`game.py`](game.py) checks every field of it).

Both are one layout ([`layout.py`](layout.py)) in two materials
([`skins.py`](skins.py)): the standard theme's enamel and lit pieces, and a
print's drawing on drafting paper, so the sheets stand the same in every theme
and only what they are made of changes. The pieces are one set of silhouettes
([`shapes.py`](shapes.py)), and the motion one choreography
([`motion.py`](motion.py)), with a still file of each sheet for anyone who asks
for reduced motion. Round the pictures the README carries the game's words
([`readme.py`](readme.py)): the turn's banner, every legal move named, and a
badge linking each winner's profile.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                        | Purpose                                                                                                         |
| :--------------------------- | :-------------------------------------------------------------------------------------------------------------- |
| [`__init__.py`](__init__.py) | The chess elements: the game on @tannergolden's profile and its Hall of Fame, drawn in every theme.             |
| [`game.py`](game.py)         | What the chess sheets are drawn from: the game as the profile's own engine hands it over, checked and read.     |
| [`layout.py`](layout.py)     | The chess sheets' one layout, which every theme draws: the board and its panel, and the Hall of Fame.           |
| [`motion.py`](motion.py)     | The motion every theme shares: one choreography, so a board moves the same way in every skin.                   |
| [`readme.py`](readme.py)     | What the README carries round the chess sheets: the turn's banner, every legal move, and a badge per winner.    |
| [`README.md`](README.md)     | This file.                                                                                                      |
| [`shapes.py`](shapes.py)     | The pieces' shapes, shared by every theme: one set of silhouettes, so a knight is the same knight in each skin. |
| [`skins.py`](skins.py)       | What the chess sheets are made of, per theme: the standard theme's skin and the prints'.                        |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself.

---

<div align="center">

**The board, wherever the page is drawn.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
