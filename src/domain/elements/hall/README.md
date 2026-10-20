<!--
title: '🏆 HALL OF FAME'
description: 'The Hall of Fame of all four games on @tannergolden''s profile: the series, the podium and the leaderboard, one layout in every theme.'
type: index
keywords: [source, domain, elements, chess, games, svg]
-->

<div align="center">

# 🏆 HALL OF FAME

<a name="top"></a>

**Every game on @tannergolden's profile, and everyone who has won one.**

_Four games, one podium._

</div>

---

## 💡 What This Folder Is For

The Hall of Fame of the four games played on @tannergolden's profile, and only
there: Chess, Checkers, Pentago and Tic-Tac, in that order wherever a reader
meets them. One element, `hall-of-fame`, draws the series of every game
and of all four together, the podium of the five leading winners across them
with each one's wins in every game, and a badge for each winner. The profile's
own engines write what it draws into the page's settings after every move
([`record.py`](record.py) checks every field of it), each player's wins one
count to a game in tier order, Tic-Tac first, as they always have.

It is chess-hall grown to four games, drawn in chess-hall's own materials
([`skins.py`](skins.py), chess's two skins with every game's pieces added): the
standard theme's enamel, and a print's drawing on drafting paper. The sheet
([`layout.py`](layout.py)) reads as a match card: the house and GitHub face each
other across the top, the series under them as a table, all four games first
and then each on a row of its own, and the podium under that, three blocks in
gold, silver and bronze, a winner standing on each. Each sheet comes wide and on
a phone, moving as it opens and still for anyone who asks for reduced motion.
While a holiday's set, a pixel theme or a collection's design is up, it draws the same match
card in its own pixels, as it draws the four boards
([`holidays/designs/hall.py`](../../holidays/designs/hall.py)), the blocks cut
from the set's own world, a plaque of the trophies' metals on each, and each
winner as the set draws a person.

Each game is named by its own mark ([`marks.py`](marks.py)): its two pieces, the
house's first, on the left. The white king then the black, the white man then
the black, the white marble then the black, X then O. Each player's side is
fixed: the house plays White in Chess, Checkers and Pentago and X in Tic-Tac,
GitHub Black and O. Only who moves first can change, where the Arbiter draws it
in Pentago and Tic-Tac once both ghosts are down. The same mark heads the
game's row of the series and stands beside every winner's wins in that game.

Round the picture the README carries ([`readme.py`](readme.py)) a badge linking
each winner's profile, the first three marked as their podium blocks are, in
gold, silver and bronze, or in a print solid, lined and open, then the
leaderboard folded shut: @tannergolden's own row on top, then GitHub's ten
leading players, each with a column of wins for every game, Chess first, headed
by that game's two side signs, the house's first (♔♚, ⛀⛂, ⚪⚫, ❌⭕), then their
moves and their wins in all four. A line under it says how a win counts: only
for the player who makes the winning move, never for a move the Arbiter plays,
and never in a draw.

A player is known by their account, not their login, as in chess-hall: a row
may carry the player's account ID as its fifth field, a run reads that account
as it is now and keeps its login in `logins`, and a player whose account is
gone, which only GitHub's 404 for its ID says, is left off the page, the players
under them moving up into the places the page has.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                        | Purpose                                                                                                              |
| :--------------------------- | :------------------------------------------------------------------------------------------------------------------- |
| [`__init__.py`](__init__.py) | The Hall of Fame of all four games on @tannergolden's profile: Chess, Checkers, Pentago and Tic-Tac.                 |
| [`layout.py`](layout.py)     | The Hall of Fame's one layout, which every theme draws: the series of all four games, and the podium.                |
| [`marks.py`](marks.py)       | Each game's pieces, as the Hall draws them, shared by every theme: one set of outlines in chess's 45-unit box.       |
| [`README.md`](README.md)     | This file.                                                                                                           |
| [`readme.py`](readme.py)     | What the README carries under the Hall of Fame's sheet: a badge for each winner, and the leaderboard.                |
| [`record.py`](record.py)     | What the Hall of Fame of all four games is drawn from: the record the profile's engines hand over, checked and read. |
| [`skins.py`](skins.py)       | What the Hall of Fame's sheets are made of, per theme: chess's two skins, and every game's pieces in each.           |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself.

---

<div align="center">

**Every winner, wherever the page is drawn.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Proprietary; all rights reserved under [LICENSE-GAMES](../../../../LICENSE-GAMES).

</div>
