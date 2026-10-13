<!--
title: '❌ TIC-TAC'
description: 'The Tic-Tac element: the first tier of the games on @tannergolden''s profile, one layout in every theme.'
tags: [source, domain, elements, games, tictac, svg]
category: docs
-->

<div align="center">

# ❌ TIC-TAC

<a name="top"></a>

**The first tier of the games on @tannergolden's profile.**

_Nine boards at once, drawn by chess's hand._

</div>

---

## 💡 What This Folder Is For

The game of Tic-Tac played on @tannergolden's profile, and only there:
`tictac`, the board as it stands with the state of play beside it. Tic-Tac is
Tic-Tac-Toe played on nine boards at once, three a side, the game also known as
Ultimate Tic-Tac-Toe. The profile's own engine plays the game and writes what
it draws into the page's settings after every move ([`game.py`](game.py) checks
every field of it).

The square a mark takes inside its board sends the other side to the board in
the same place on the big board: take a board's upper right corner, and the
reply goes in the upper right board. Three in a row inside a board wins it;
three boards won in a row wins the game. A side sent to a closed board plays in
any open one.

The house always plays X and GitHub always O. Under the Ghost Rule each side
first locks one square with a ghost, the side the Arbiter drew placing first
(`places`), and once both ghosts are down the Arbiter draws the side that makes
the first mark (`opens`). Nothing here assumes which side placed or opened.

Its sheet is chess's ([`../games/`](../games/README.md)): the same card or
drafting sheet, band and panel, around a board of its own
([`layout.py`](layout.py)) as wide as chess's: nine small boards with bars
between them, their squares named as chess names squares, a1 to i9, and the
boards as Tic-Tac-Toe names its cells, a1 the lower left board. A move is
written as the mark and its square, `Xe5`, the score sheet adding a `#` to the
move that won; a ghost's square is written alone on the score sheet's G row. The
board the next mark is sent to is bracketed at its four corners, since the
rules send it there, and the turn's plate says so: the board, any board, or a
ghost to place. In place of chess's taken pieces the panel counts the boards
each side has won. Nothing on the sheet helps a player choose: no square a side
could win a board on next, no board a side could win the game on, and no call
to block. The marks are pen strokes ([`shapes.py`](shapes.py)) in the two
materials ([`skins.py`](skins.py)): enamel on chess's board in the standard
theme; ink and line shading on a print. A ghost's square is filled as the bars
are and edged in phantom lines, long and short dashes.

As the file opens ([`motion.py`](motion.py)) the last mark draws itself stroke
by stroke as a pen would and its square is boxed as the pen lifts. A mark that
wins its board strikes the board's three, and the board's own mark is drawn
across it as large as the board; a mark that wins the game strikes the three
boards. A finished game's board stays up for two days with a countdown to the
next game in place of the count, and the README's words under the sheet
([`readme.py`](readme.py)) are every square the side to move can take as a
move, each named for where its mark goes, never for what it does.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                        | Purpose                                                                                                                                                               |
| :--------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`__init__.py`](__init__.py) | The Tic-Tac element: the first tier of the games on @tannergolden's profile, drawn as chess is drawn.                                                                 |
| [`game.py`](game.py)         | What the Tic-Tac sheet is drawn from: the game as the profile's own engine hands it over, checked and read.                                                           |
| [`layout.py`](layout.py)     | The Tic-Tac sheet's layout: its board of nine boards, and what its panel counts, inside the sheet every game shares.                                                  |
| [`motion.py`](motion.py)     | Tic-Tac's motion: chess's choreography (`chess.motion`), and the beats of a mark drawn by hand.                                                                       |
| [`README.md`](README.md)     | This file.                                                                                                                                                            |
| [`readme.py`](readme.py)     | What the README carries under the Tic-Tac sheet: every square the side to move can take as a move, folded, then the note.                                             |
| [`shapes.py`](shapes.py)     | The marks' shapes, shared by every theme: an X and an O as a pen draws them, each in a 100-unit box.                                                                  |
| [`skins.py`](skins.py)       | What the Tic-Tac sheet is made of, per theme: the standard theme's enamel and a print's drawing, as chess's sheets are (`games.skin`), with the marks' own materials. |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself.

---

<div align="center">

**Three boards in a row, wherever the page is drawn.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
