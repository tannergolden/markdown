<!--
title: '🎬 REPLAY'
description: 'Replays: a finished game on @tannergolden''s profile played again move by move on its own board, looping, for tannergolden/play.'
type: index
-->

<div align="center">

# 🎬 REPLAY

<a name="top"></a>

**A won game, played again on its own board.**

_Every move, the finale, and the loop, drawn by chess's hand._

</div>

---

## 💡 What This Folder Is For

A game on @tannergolden's profile won by a person's own move gets a replay:
the kit's `replay` command draws it from the facts the profile's engine writes
beside the game's record, and tannergolden/play keeps each game's newest 25 and
posts each on its winning move's issue. A draw gets none, and neither does a win
the Arbiter's move made.

The facts ([`__init__.py`](__init__.py) checks every field of them) are the
engine's, which knows the rules: every turn's side, its notation as the score
sheet numbers it, its words, who played it and the day, and what it did in its
game's own terms. The kit only draws them. The board stands where the profile's
board stands, the same size in the same frame, and every turn plays with the
README's own last-move motion, each game's own: a chess piece coming in from its
square ([`chess.py`](chess.py)), a checkers man sliding or hopping and crowned
([`checkers.py`](checkers.py)), a Pentago marble set and its quarter turned,
the quarter drawn once for every stretch between its turns
([`pentago.py`](pentago.py)), and a Tic-Tac mark drawn by its pen, a board it
wins struck and claimed and the board the next mark is sent to bracketed
([`tictac.py`](tictac.py)). The ghosts come first, where a game has them.

Beside the board the panel follows the game ([`sheet.py`](sheet.py)): the move
being played in notation and in words, each move's lines taking the last one's
place the moment it is played; everyone who played, the mover ringed by the
turn ring; and the score sheet's newest rows. Then the finale: the winner ringed
with the Hall of Fame's glint and the finished board's plate, the losing side
fading as a taken piece fades, and the whole game's score with the winning move
boxed. Every motion runs on one loop of keyTimes ([`clock.py`](clock.py)), so
the file plays the game, holds the finale and plays it again, and nothing in it
is the README's opening motion.

Each player is a halftone of their GitHub avatar
([`portrait.py`](portrait.py)): dots in the print's ink, made from a small grey
bitmap of the avatar that whoever runs the replay hands over as a PGM, so no
image goes into the file. A player with no bitmap is their initials in the
print's dial, the Arbiter is its scales, and an account that is gone is an
empty dashed dial with no name. A replay is drawn in the page's print, and in
blackprint when the page's theme has no replay look of its own: the standard
theme, a holiday's set, a pixel theme or a collection's design. A word the replay says on
many moves is drawn once in the file and set wherever it stands, which keeps a
long game's file small.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                        | Purpose                                                                                                                |
| :--------------------------- | :--------------------------------------------------------------------------------------------------------------------- |
| [`__init__.py`](__init__.py) | Replays: a finished game on @tannergolden's profile, played again move by move on its own board, looping.              |
| [`checkers.py`](checkers.py) | Checkers' replay board: the profile's board, every move played with the README's own last-move motion.                 |
| [`chess.py`](chess.py)       | Chess's replay board: the profile's board, every move played with the README's own last-move motion.                   |
| [`clock.py`](clock.py)       | A replay's one timeline: every animated attribute in the file runs the whole loop and repeats forever.                 |
| [`common.py`](common.py)     | What the four replay boards share: what each answers for the sheet, and the README's landing ring.                     |
| [`pentago.py`](pentago.py)   | Pentago's replay board: the profile's four quarters, every turn played with the README's own last-move motion.         |
| [`portrait.py`](portrait.py) | A player as a replay draws them: their GitHub avatar as a print draws a portrait, a halftone of dots in its ink.       |
| [`README.md`](README.md)     | This file.                                                                                                             |
| [`sheet.py`](sheet.py)       | What every replay shares, whatever the game: its timing, the panel that follows the game move by move, and the finale. |
| [`tictac.py`](tictac.py)     | Tic-Tac's replay board: the profile's nine boards, every turn played with the README's own last-move motion.           |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself.

---

<div align="center">

**Won once, played forever.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Proprietary; all rights reserved under [LICENSE-GAMES](../../../../LICENSE-GAMES).

</div>
