<!--
title: '🎲 GAMES'
description: 'What the four games on @tannergolden''s profile share: one sheet, one panel and one pair of materials, so they read as one hand.'
tags: [source, domain, elements, games, svg]
category: docs
-->

<div align="center">

# 🎲 GAMES

<a name="top"></a>

**Four games, drawn by one hand.**

_Chess's sheet, around each game's own board._

</div>

---

## 💡 What This Folder Is For

What the games beside chess on @tannergolden's profile share with it and with
one another, so Tic-Tac ([`tictac/`](../tictac/README.md)), Pentago
([`pentago/`](../pentago/README.md)), Checkers
([`checkers/`](../checkers/README.md)) and Chess
([`chess/`](../chess/README.md)) read as one family drawn by one hand.

Every game's sheet is chess's ([`sheet.py`](sheet.py)): the same card or
drafting sheet and its band, the board in the same place at the same size, and
beside it, or under it on a phone, the same panel a section at a time
([`panel.py`](panel.py)): the two sides with the turn ringed, the turn's plate
and when the move is due, the last move in notation and in words, what the game
keeps count of, and the score sheet. A finished game keeps its final board up
for two days, the same plate saying who won and how and the day the fresh board
comes. The two materials are chess's skins with what a game adds to both
([`skin.py`](skin.py)): words fitted to their room, the light and dark
materials, a side's medallion, and the mark on whatever the rules make the side
to move answer, a man that must jump, glowing red in the standard theme as
chess's king in check does, and clouded on a print.

What a game's data is checked for ([`data.py`](data.py)) is checked as strictly
as chess's: a number is a whole number within its ceiling, a day is a real day,
a line of the README opens no block of its own, a move's link opens its own
ready-made issue and nothing else, and a finished board offers nothing to play.
Nothing that would help a player choose is taken: no cell or column a side could
win on next, no call to block, and no `+` or `#` on a move still to play, which
only the score sheet writes, once the move is made. The sides are the house and
GitHub ([`sides.py`](sides.py)), and the README's words under each sheet
([`readme.py`](readme.py)) are every legal move, folded, as chess's are.

A game's own package draws its board and its pieces and says how its moves are
written; everything else is here or is chess's, imported rather than copied.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                        | Purpose                                                                                                                                                                                                                             |
| :--------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`__init__.py`](__init__.py) | What every game on @tannergolden's profile shares, so the four sheets read as one family drawn by one hand.                                                                                                                         |
| [`data.py`](data.py)         | What every game's data is checked for, and the state every sheet reads from it.                                                                                                                                                     |
| [`panel.py`](panel.py)       | The panel beside every game's board, a section at a time, as chess's is: the two sides, the turn, the last move and the score sheet, with the game's own count between them (`sheet` places them).                                  |
| [`README.md`](README.md)     | This file.                                                                                                                                                                                                                          |
| [`readme.py`](readme.py)     | What the README carries under a game's sheet, as it does under chess's: every legal move, folded shut under one line saying whose they are and how many, then the note.                                                             |
| [`sheet.py`](sheet.py)       | A game's board sheet, wide and a phone's, drawn as chess's is: the same card or drafting sheet and its band, the board in the same place at the same size, and beside it (under it, on a phone) the same panel a section at a time. |
| [`sides.py`](sides.py)       | The two sides of every game on the profile: the house, @tannergolden, and GitHub, everyone else.                                                                                                                                    |
| [`skin.py`](skin.py)         | The two materials every game's sheet is drawn in: chess's skins, and what a game beside chess adds to them.                                                                                                                         |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself.

---

<div align="center">

**Four boards, one hand.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
