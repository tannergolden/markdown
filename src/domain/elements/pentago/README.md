<!--
title: '🌀 PENTAGO'
description: 'The Pentago element: the second tier of the games on @tannergolden''s profile, one layout in every theme.'
tags: [source, domain, elements, games, pentago, svg]
category: docs
-->

<div align="center">

# 🌀 PENTAGO

<a name="top"></a>

**The second tier of the games on @tannergolden's profile.**

_Thirty-six holes in four quarters that turn, drawn by chess's hand._

</div>

---

## 💡 What This Folder Is For

The game of Pentago played on @tannergolden's profile, and only there:
`pentago`, the board as it stands with the state of play beside it. The
profile's own engine plays the game and writes what it draws into the page's
settings after every move ([`game.py`](game.py) checks every field of it).

A move sets a marble in an empty hole and then turns one of the four quarters a
quarter turn, clockwise or anticlockwise, everything on it turning with it.
Five in a row wins: the mover's, or the other side's if the turn makes five for
it alone. Five for both, or a full board without five, is a draw.

The house always plays White and GitHub always Black. Under the Ghost Rule each
side first sets a ghost, a marble that is nobody's, the side the Arbiter drew
setting first (`places`), and once both ghosts are down the Arbiter draws the
side that sets the first marble (`opens`). A ghost turns with its quarter and no
five runs through it. Nothing here assumes which side set or opened.

Its sheet is chess's ([`../games/`](../games/README.md)): the same card or
drafting sheet, band and panel, around a board of its own
([`layout.py`](layout.py)) as wide as chess's: four quarter plates of three
holes a side with a gap between them so each can turn, the holes named as chess
names squares, a1 to f6. A move is written as its hole, its quarter and the way
it turned, `e4-ur-cw`, and the sheet draws it as `e4 ↻ UR`, the score sheet
adding a `#` to the move that won; a marble that makes five on its own wins
before any quarter turns and is written as its hole alone, `e4#`. A ghost's
hole is written alone on the score sheet's G row. In place of chess's taken
pieces the panel counts each side's marbles left, a rack of seventeen, and says
where the ghosts stand now. Nothing on the sheet helps a player choose: no hole
or turn that would make five, and no call to block. The plates and the marbles
([`shapes.py`](shapes.py)) come in the two materials ([`skins.py`](skins.py)):
the theme's cobalt enamel and marbles lit as chess's pieces are, in the standard
theme; section lining and ink on a print. A ghost is a marble of the plate's own
material, ringed in phantom lines.

As the file opens ([`motion.py`](motion.py)) the last marble is set in its hole,
which is ringed, with a ripple; then its quarter turns its quarter turn from
where it stood, and an arrow round the quarter's outer corner is drawn the way
it went. A won game's five are ringed one after another and joined. A finished
game's board stays up for two days, and the README's words under the sheet
([`readme.py`](readme.py))
are every empty hole as a move, each named for where it is and never for what it
does, with its eight turns after it, each a link of its own.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                        | Purpose                                                                                                                                                                                   |
| :--------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`__init__.py`](__init__.py) | The Pentago element: the second tier of the games on @tannergolden's profile, drawn as chess is drawn.                                                                                    |
| [`game.py`](game.py)         | What the Pentago sheet is drawn from: the game as the profile's own engine hands it over, checked and read.                                                                               |
| [`layout.py`](layout.py)     | The Pentago sheet's layout: its four quarters, and what its panel counts, inside the sheet every game shares.                                                                             |
| [`motion.py`](motion.py)     | Pentago's motion: chess's choreography (`chess.motion`), and a marble set and a quarter turned.                                                                                           |
| [`README.md`](README.md)     | This file.                                                                                                                                                                                |
| [`readme.py`](readme.py)     | What the README carries under the Pentago sheet: every empty hole as a move with its eight turns, folded, then the note.                                                                  |
| [`shapes.py`](shapes.py)     | The quarters' and the marbles' shapes, shared by every theme, each in proportion to a quarter's pitch.                                                                                    |
| [`skins.py`](skins.py)       | What the Pentago sheet is made of, per theme: the standard theme's enamel and a print's drawing, as chess's sheets are (`games.skin`), with the quarters' and the marbles' own materials. |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself.

---

<div align="center">

**Five in a row, wherever the page is drawn.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
