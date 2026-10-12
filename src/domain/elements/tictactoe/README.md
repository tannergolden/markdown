<!--
title: '❌ TIC-TAC-TOE'
description: 'The Tic-Tac-Toe element: the first tier of the games on @tannergolden''s profile, one layout in every theme.'
tags: [source, domain, elements, games, tictactoe, svg]
category: docs
-->

<div align="center">

# ❌ TIC-TAC-TOE

<a name="top"></a>

**The first tier of the games on @tannergolden's profile.**

_765 positions, drawn by chess's hand._

</div>

---

## 💡 What This Folder Is For

The game of Tic-Tac-Toe played on @tannergolden's profile, and only there:
`tictactoe`, the board as it stands with the state of play beside it. The
profile's own engine plays the game and writes what it draws into the page's
settings after every move ([`game.py`](game.py) checks every field of it).

Tic-Tac-Toe is a draw with perfect play, but its first player wins far more
often whenever anyone slips: of the 255,168 possible games, X wins 131,184
(about 51%), O wins 77,904 (about 31%) and 46,080 are drawn. So the Arbiter
opens every game, for a side drawn at random, with a random move: that side
plays X, the other O, and `x` says which it was. Nothing here assumes which.

Its sheet is chess's ([`../games/`](../games/README.md)): the same card or
drafting sheet, band and panel, around a board of its own
([`layout.py`](layout.py)): three cells a side as wide as chess's board, named
as chess names squares, a1 to c3, with the eight lines a game is won on drawn
faint through them while a side can still win on them. A move is written as
the mark and its cell, `Xb2`, `+` for a threat and `#` for a win. In place of
chess's taken pieces the panel says what perfect play says from here, and where
each side would win next. The marks are pen strokes ([`shapes.py`](shapes.py))
in the two materials ([`skins.py`](skins.py)): enamel on chess's board, its
cells the light squares and its bars the dark, in the standard theme; ink and
line shading on a print. X is always drawn light and O always dark, whoever
plays them, since a game's colours never change: only who plays which side.

As the file opens ([`motion.py`](motion.py)) the last mark draws itself stroke
by stroke as a pen would, its cell is marked as the pen lifts, a cell the side
to move must block blooms as chess's check does, with the threatening mark in
phantom lines inside it, and a won line is struck through. A finished game's
board stays up for two days with its line struck and its plate saying who won,
and the README's words round the sheet ([`readme.py`](readme.py)) are the
turn's banner and every open cell as a move, named as a call across a duel.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                        | Purpose                                                                                                                                                                   |
| :--------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [`__init__.py`](__init__.py) | The Tic-Tac-Toe element: the first tier of the games on @tannergolden's profile, drawn as chess is drawn.                                                                 |
| [`game.py`](game.py)         | What the Tic-Tac-Toe sheet is drawn from: the game as the profile's own engine hands it over, checked and read.                                                           |
| [`layout.py`](layout.py)     | The Tic-Tac-Toe sheet's layout: its board, and what its panel counts, inside the sheet every game shares.                                                                 |
| [`motion.py`](motion.py)     | Tic-Tac-Toe's motion: chess's choreography (`chess.motion`), and the beats of a mark drawn by hand.                                                                       |
| [`README.md`](README.md)     | This file.                                                                                                                                                                |
| [`readme.py`](readme.py)     | What the README carries round the Tic-Tac-Toe sheet: the turn's banner, and every open cell as a move, folded.                                                            |
| [`shapes.py`](shapes.py)     | The marks' shapes, shared by every theme: an X and an O as a pen draws them, each in a 100-unit box.                                                                      |
| [`skins.py`](skins.py)       | What the Tic-Tac-Toe sheet is made of, per theme: the standard theme's enamel and a print's drawing, as chess's sheets are (`games.skin`), with the marks' own materials. |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself.

---

<div align="center">

**Three in a row, wherever the page is drawn.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
