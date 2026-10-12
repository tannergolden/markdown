<!--
title: '⚫ CONNECT FOUR'
description: 'The Connect Four element: the second tier of the games on @tannergolden''s profile, one layout in every theme.'
tags: [source, domain, elements, games, connectfour, svg]
category: docs
-->

<div align="center">

# ⚫ CONNECT FOUR

<a name="top"></a>

**The second tier of the games on @tannergolden's profile.**

_About 4.5 trillion positions, drawn by chess's hand._

</div>

---

## 💡 What This Folder Is For

The game of Connect Four played on @tannergolden's profile, and only there:
`connectfour`, the frame as it stands with the state of play beside it. The
profile's own engine plays the game and writes what it draws into the page's
settings after every move ([`game.py`](game.py) checks every field of it).

The house always drops the White discs and GitHub always the Black. The Arbiter
opens every game for a side drawn at random, with a random first move, and
`opens` says which side that was, so a game opens with a White disc when it was
opened for the house and a Black one when for GitHub. Nothing here assumes which
side opened. The board's letters stay as they were: `L` is a White disc, the
house's, and `D` a Black one, GitHub's.

Its sheet is chess's ([`../games/`](../games/README.md)): the same card or
drafting sheet, band and panel, around a frame of its own
([`layout.py`](layout.py)) as wide as chess's board, drawn in elevation: seven
columns numbered under it and six rows up its side, on two legs on the ground. A
move is written as its column, `4`, the score sheet adding a `#` to the drop
that connected four, with the disc that dropped it before it on the sheet. In
place of chess's taken pieces the panel counts each side's discs left, a rack of
twenty-one emptying as the frame fills, the house's White on top. Nothing on the
sheet helps a player choose: no column a side could connect four down next, and
no call to block. Every word on the sheet says White
and Black. The frame and the discs ([`shapes.py`](shapes.py)) come in the two
materials ([`skins.py`](skins.py)): the theme's cobalt enamel and discs lit as
chess's pieces are, in the standard theme; section lining and ink on a print.

As the file opens ([`motion.py`](motion.py)) the last disc is held over its
column, let go, glimpsed through each hole it passes behind, and lands with a
bounce, its hole ringed; and a won game's four are ringed one after another and
joined. A finished game's frame stays up for two days, and the README's words
under the sheet ([`readme.py`](readme.py)) are every open column as a move, each
named for the disc, its column and the row it lands on, never for what it does.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                        | Purpose                                                                                                                                                                                    |
| :--------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`__init__.py`](__init__.py) | The Connect Four element: the second tier of the games on @tannergolden's profile, drawn as chess is drawn.                                                                                |
| [`game.py`](game.py)         | What the Connect Four sheet is drawn from: the game as the profile's own engine hands it over, checked and read.                                                                           |
| [`layout.py`](layout.py)     | The Connect Four sheet's layout: its frame, and what its panel counts, inside the sheet every game shares.                                                                                 |
| [`motion.py`](motion.py)     | Connect Four's motion: chess's choreography (`chess.motion`), and a disc that falls.                                                                                                       |
| [`README.md`](README.md)     | This file.                                                                                                                                                                                 |
| [`readme.py`](readme.py)     | What the README carries under the Connect Four sheet: every open column as a move, folded, then the note.                                                                                  |
| [`shapes.py`](shapes.py)     | The frame's and the discs' shapes, shared by every theme, each in proportion to the frame's pitch.                                                                                         |
| [`skins.py`](skins.py)       | What the Connect Four sheet is made of, per theme: the standard theme's enamel and a print's drawing, as chess's sheets are (`games.skin`), with the frame's and the discs' own materials. |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself.

---

<div align="center">

**Four in a row, wherever the page is drawn.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
