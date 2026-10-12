<!--
title: '📄 ADR-0009: THE GAMES WEAR THE PAGE''S THEME'
description: 'The games on @tannergolden''s profile and their Hall of Fame are drawn in the page''s theme, as the trophy case is: while a holiday''s set or a collection''s design is up, in its pixels, every file of a game or none.'
tags: [adr, architecture, decisions, themes, games]
category: docs
status: 'Accepted'
date: '2026-10-12'
evidence: 'N/A'
-->

<div align="center">

# 📄 ADR-0009: THE GAMES WEAR THE PAGE'S THEME

<a name="top"></a>

**The games on @tannergolden's profile and their Hall of Fame are drawn in the page's theme, as the trophy case is: while a holiday's set or a collection's design is up, in its pixels, every file of a game or none.**

_Formalized rationale. Transparent intent. Auditable evolution._

</div>

---

## 📋 Meta Information

| Attribute     | Specification                      |
| :------------ | :--------------------------------- |
| **Deciders**  | Tanner Golden                      |
| **Consulted** | Claude Code                        |
| **Informed**  | Everyone who plays on that profile |

---

## 🎯 Context & Problem Statement

[ADR-0008](ADR-0008-The-Trophy-Case-Wears-The-Pages-Theme.md) dressed the trophy case in the page's theme, and with it every part of a page wore one theme but the games. Chess, Checkers, Connect Four and Tic-Tac-Toe, and the Hall of Fame of all four, are drawn in two materials, the standard theme's enamel and a print's drawing on drafting paper. A holiday's set or a collection's design left them as they were, so in October the Halloween set drew the profile's every header and footer in pixels by moonlight while its four boards and its Hall stood in blackprint between them.

The owner asked for the games in every theme. The question was how a pixel set draws a game: what each set brings, what stays the same in every set, how a collection's hand holds, and what happens when a set cannot draw one.

---

## 🚦 Decision Drivers

- **One theme, one page**: the setting that colours the banners, the badges, the elements and the trophy case colours the games.
- **The same game in every look**: the board, the panel beside it, the README's words, the files and their sizes, so a set coming or going moves no row and changes no move.
- **Every set, now and to come**: every holiday's set and every collection's design, without drawing each game by hand in each.
- **Each set's rules**: its closed palette, its budget and its lint, nothing on its frame, and a collection's design its hand.
- **Never half and half**: a board is in one look, its files and its still twins alike.

---

## 🏗️ Considered Options

1. **The page's look in every set**, as it was.
2. **A pixel game per set**, each set drawing its own boards.
3. **The games follow the page's theme**: one pixel layout of each game, shared by every set and drawn from the hooks a set already has, its pieces drawn once for all of them.

---

## ✅ Decision Outcome

**Chosen Option**: The games follow the page's theme

### Rationale for Selection

- **One setting.** The theme, or the holiday's set that is up, decides the games as it decides every other part: nothing new in the settings, nothing to keep in step.
- **One layout, every set.** The layouts live with the sets' others, in `holidays/designs/` (`games.py`, `boards.py` and `hall.py`), the same sheet, panel and sections as the standard theme's and the prints', and each set brings what it already has: its paper and sky, its frame, its tags, its inks and its lettering.
- **Built of each set's world.** A set names what its games are made of (`materials.py`): its board's squares (`game_squares`) and its frame (`game_frame`), each a ramp of its own tones with a grain, and what its Hall's podium is cut from and how it is worked (`game_podium`). So the Longship's board is painted planks in an oak frame and its podium tarred timber with her shields along its rail, the Cathedral's board violet glass in its lead and its podium the rose window's blue, and the Stronghold's podium crenellated ashlar; a plaque of the trophies' metals is set in every block. A set that names none has its squares picked from its palette, near its tags' hue and its paper's. The last move's mark and what must be answered take the set's accent and red, or, where one would be lost on its board, the first of its inks that stands clear of both squares.
- **The same pieces in every world.** Every piece is drawn once, in pixels, at each size a sheet needs (`pieces.py`): chessmen, stacked checkers men, discs and a pen's marks, the house's in ivory and GitHub's in ebony in every set, so a knight is the same knight by moonlight and in a scriptorium, and the house's pieces are the light ones, as they are in every look.
- **A collection's hand holds.** A design letters every word in its hand's two inks and glints on its hand's period. Its title lettering sets the counts and the moves, and a design whose titles stand in a box of their own, an illuminated initial or a banderole, letters them for a panel instead (`game_title`).
- **Motion as pixel art moves.** Each file opens as it does in every look, a board playing its last move again and the Hall filling its series and raising its podium, in discrete steps as the sets' scenes move, and holds where it lands; its still twin is drawn at rest for a reader who asks for reduced motion.
- **Nothing moves.** Every file keeps its name and its width, the winners' badges their height, and the README's banner, moves, badges and leaderboard are the same words in every look.
- **Each set's rules.** The sides' ivory and ebony and the trophies' metals join a set's closed palette for its game files alone, as the metals join it for the trophy case, and every file is held to its lint, its budget and the room its frame leaves, at the limits the data may reach.
- **Never half and half.** A set draws a game whole or not at all: a game with a word it cannot letter, a winner's name in a script its faces lack, or a file it cannot draw within its budget, is drawn whole in the page's own look.
- **Chess's own Hall stays.** `chess-hall`, whose place the four games' Hall of Fame took, keeps the page's own look whatever set is up.

`src/domain/elements/data.py` hands a game to the set that is up and takes every file of it or none (`held_game`), and the tests hold every game in every set to its lint, its palette, its budget, its sizes and its room.

---

## 📈 Consequence Matrix

| Category         | Impact / Consequence                                                                                                              |
| :--------------- | :-------------------------------------------------------------------------------------------------------------------------------- |
| **Positive (+)** | The profile reads as one theme through every holiday and every month, and every set to come draws the games with nothing added.   |
| **Negative (-)** | More drawings to keep: every game is drawn and linted in every set, and the tests, the lint and the theme-sets page grow with it. |
| **Neutral (~)**  | The boards change their look when a set comes up and change back when it goes, as every other part of the page does.              |

---

## ⚖️ Trade-off Comparative

### Option A: The page's look in every set

- ✅ Nothing to draw.
- ❌ The games stand apart from the page they are played on for every holiday and every month.

### Option B: A pixel game per set

- ✅ Each set could shape its boards to its own world.
- ❌ Nineteen sets of four boards and a Hall to draw and keep, and every set to come has to draw them again.

### Option C: The games follow the page's theme

- ✅ One layout per game, every set, the same game in every look, each set's board and podium of its own world.
- ❌ The shared layout has to suit every set's paper, frame and lettering, and every set's palette has to give a board.

---

## 🔗 Traceability & Links

- [ADR-0001](ADR-0001-One-Kit-One-Stub.md): one theme sets the whole page.
- [ADR-0003](ADR-0003-Holiday-Windows.md): the holiday windows, whose sets now draw the games too.
- [ADR-0006](ADR-0006-A-Collection-Changes-With-The-Month.md): the collection whose designs draw the games month by month.
- [ADR-0007](ADR-0007-A-Collection-Is-Drawn-By-One-Hand.md): the hand a design's games are lettered in.
- [ADR-0008](ADR-0008-The-Trophy-Case-Wears-The-Pages-Theme.md): the trophy case, the part drawn in the page's theme before them, whose metals the plaques on the Hall's podium are struck in.

### 🔗 See also

> [!TIP]
> Every canonical guide is indexed in the [&#x1F4DA; Standards Index](https://github.com/tannergolden/standards/blob/Development/docs/README.md). If you rename or move a file, update every reference to it across the repository to prevent link drift.

---

<div align="center">

**One decision. One record. Zero ambiguity.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
