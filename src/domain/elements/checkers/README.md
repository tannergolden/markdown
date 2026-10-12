<!--
title: '⛂ CHECKERS'
description: 'The Checkers element: the third tier of the games on @tannergolden''s profile, one layout in every theme.'
tags: [source, domain, elements, games, checkers, svg]
category: docs
-->

<div align="center">

# ⛂ CHECKERS

<a name="top"></a>

**The third tier of the games on @tannergolden's profile.**

_About 500 billion billion positions, on chess's own board._

</div>

---

## 💡 What This Folder Is For

The game of Checkers played on @tannergolden's profile, and only there:
`checkers`, the board as it stands with the state of play beside it. The
profile's own engine plays the game and writes what it draws into the page's
settings after every move ([`game.py`](game.py) checks every field of it).

Checkers was weakly solved as a draw in 2007, and its first move's edge is
small, so the house opens every game, with the dark men, as chess's house opens
with White. The position arrives as checkers writes one, PDN, its thirty-two
dark squares numbered 1 to 32, and a move as checkers writes it, `11-15` for a
step and `22x15x8` for a jump, a square for every landing.

Its sheet is chess's ([`../games/`](../games/README.md)): the same card or
drafting sheet, band and panel, around chess's own board drawn by chess's own
skins, each dark square's number on a tab in its corner
([`layout.py`](layout.py)), the house's men on the near side as chess's White
is. In place of chess's taken pieces the panel counts the men each side has
taken and the kings each has made. The men and kings ([`shapes.py`](shapes.py))
come in the two materials ([`skins.py`](skins.py)): enamel lit as chess's
pieces are, in the standard theme; ink and line shading on a print.

As the file opens ([`motion.py`](motion.py)) the last move's man slides, or
hops over each man it takes, those men fading as it passes and the jump's path
drawn in behind it; a man reaching the far row is crowned as it lands, a
second man dropped onto it; and a man that must jump is marked as chess marks a
king in check. A finished game's board stays up for two days, and the README's
words round the sheet ([`readme.py`](readme.py)) are the turn's banner and
every legal move, each an order to a fleet at sea, grouped by men and kings
when there are more than ten, as chess groups its moves by piece.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                        | Purpose                                                                                                                                                               |
| :--------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`__init__.py`](__init__.py) | The Checkers element: the third tier of the games on @tannergolden's profile, drawn as chess is drawn.                                                                |
| [`game.py`](game.py)         | What the Checkers sheet is drawn from: the game as the profile's own engine hands it over, checked and read.                                                          |
| [`layout.py`](layout.py)     | The Checkers sheet's layout: its board, and what its panel counts, inside the sheet every game shares.                                                                |
| [`motion.py`](motion.py)     | Checkers' motion: chess's choreography (`chess.motion`), and a man that slides, hops and is crowned.                                                                  |
| [`README.md`](README.md)     | This file.                                                                                                                                                            |
| [`readme.py`](readme.py)     | What the README carries round the Checkers sheet: the turn's banner, and every legal move, folded.                                                                    |
| [`shapes.py`](shapes.py)     | The men's shapes, shared by every theme: a man and a crowned king, each in chess's 45-unit box.                                                                       |
| [`skins.py`](skins.py)       | What the Checkers sheet is made of, per theme: the standard theme's enamel and a print's drawing, as chess's sheets are (`games.skin`), with the men's own materials. |

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
