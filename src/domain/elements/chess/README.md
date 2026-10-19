<!--
title: '♟️ CHESS'
description: 'The chess elements: the game on @tannergolden''s profile and its Hall of Fame, one layout in every theme.'
type: index
keywords: [source, domain, elements, svg]
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
A finished game keeps its final board up for two days, as every game on the
profile does: its `result`, who won and how, on the turn's plate, the day the
`next` game's fresh board comes, and nothing to play.

Both are one layout ([`layout.py`](layout.py)) in two materials
([`skins.py`](skins.py)): the standard theme's enamel and lit pieces, and a
print's drawing on drafting paper, so the sheets stand the same in every theme
and only what they are made of changes. The pieces are one set of silhouettes
([`shapes.py`](shapes.py)), and the motion one choreography
([`motion.py`](motion.py)), with a still file of each sheet for anyone who asks
for reduced motion. Round the pictures the README carries the game's words
([`readme.py`](readme.py)): every legal move named, a badge linking each
winner's profile, and the leaderboard, @tannergolden's own row on top of
GitHub's ten leading players. Tic-Tac, Pentago and Checkers are drawn
by the same hand, on this sheet, in these two materials and to this motion
([`games/`](../games/README.md)). While a holiday's set or a collection's design
is up, it draws the board in its own pixels instead
([`holidays/designs/`](../../holidays/designs/__init__.py)), and `chess-hall`
keeps the page's own theme.

A player is known by their account, not their login, since a login can be given
up and then taken by someone else. A row of the Hall of Fame may carry the
player's account ID after its counts, `[login, wins, last, games, id]` on the
podium and `[login, moves, wins, games, id]` on the leaderboard, and each run
reads that account as it is now
([`app/parts/elements.py`](../../../app/parts/elements.py)), keeping its login
in `logins` beside the winners' `names`. The sheet, the badges and the
leaderboard show and link the player by that login. A player whose account is
gone, which only GitHub's 404 for its ID says, is left off the page, and the
players under them move up: the engine hands over twice the rows the page has
places for, so the places stay full. Every field the engine hands over is
checked before it is drawn: text is text, every number stays under the ceiling
the sheets are drawn to fit, and nothing in the README's lines can open a block
of its own.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                        | Purpose                                                                                                         |
| :--------------------------- | :-------------------------------------------------------------------------------------------------------------- |
| [`__init__.py`](__init__.py) | The chess elements: the game on @tannergolden's profile and its Hall of Fame, drawn in every theme.             |
| [`game.py`](game.py)         | What the chess sheets are drawn from: the game as the profile's own engine hands it over, checked and read.     |
| [`layout.py`](layout.py)     | The chess sheets' one layout, which every theme draws: the board and its panel, and the Hall of Fame.           |
| [`motion.py`](motion.py)     | The motion every theme shares: one choreography, so a board moves the same way in every skin.                   |
| [`README.md`](README.md)     | This file.                                                                                                      |
| [`readme.py`](readme.py)     | What the README carries under the chess sheets: every legal move, the badges and the leaderboard.               |
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

Built with ❤️ by the Engineering Team. Proprietary; all rights reserved under [LICENSE-GAMES](../../../../LICENSE-GAMES).

</div>
