<!--
title: '⚙️ SETTINGS'
description: 'Every key .github/markdown.yaml can hold, what each does, and the default a page that says nothing gets.'
type: reference
keywords: [configuration]
-->

<div align="center">

# ⚙️ SETTINGS

<a name="top"></a>

**Every key a page can set, and what it gets without one.**

_Optional, all of it. Checked, every key of it._

</div>

---

## 📄 The File

A page's settings live in **`.github/markdown.yaml`** (`.github/markdown.yml`
is read too; keep one). A page with no file at all is drawn from what GitHub
says about it, in the `standard` theme, with the holidays and a repository's
birthday on: a header, a footer and a trophy case, and nothing else until the
settings ask.

The file holds the page as a whole at the top, then one section per part:
`banners`, `badges`, `elements` and `trophies`. A part set to `false` is not
drawn, and its files and README block are taken away on the next run.

Each part draws into a folder of its own under `assets/`: `assets/banners/`,
`assets/badges/`, `assets/trophies/` and `assets/elements/`. Every run keeps
the repository clean: a file the kit drew and draws no longer is taken away,
with any folder that leaves empty, and so are the files of the banners,
badges and trophies kits it replaced. A page first drawn into
`assets/markdown/` moves into the parts' folders on its next run. Only files
the kit stamped are ever taken away, so anything made by hand stays.

Every key is checked. An unknown key or value fails the run with the key named,
rather than being quietly ignored. A key may be written with hyphens or with
underscores: `holiday-days` and `holiday_days` are the same key.

```yaml
# .github/markdown.yaml
theme: standard
holiday-days: 5

banners:
  motto: Built to be rebuilt.
  closing: Drawn at both ends. Fetched at neither.

badges:
  - name: build
    label: Build
    icon: check
    measure:
      workflow: checks.yml

trophies:
  style: crest
```

`markdown-kit settings --root .` prints a repository's settings in full, every
default filled in, which is the quickest way to see what a run will do.

---

## 🧭 The Page

| Key            | Default       | What it does                                                                                                                                                                         |
| :------------- | :------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `mode`         | `auto`        | `profile`, `repository` or `organization`. `auto` reads a profile repository (`name/name`) as a profile, an organization's `.github` as its page, and anything else as a repository. |
| `subject`      | (the repo)    | Whose page it is: a login, an organization, or `owner/name`. Empty: this repository, or its owner on a profile.                                                                      |
| `theme`        | `standard`    | `standard`, a print, `rainbowprint`, a print of your own, a pixel theme, or a collection. See [Themes](#-themes), [Pixel Themes](#-pixel-themes) and [Collections](#-collections).   |
| `sign`         | (the month's) | The sign of the zodiac a collection's headers carry all year, as `leo`, in place of the month's. See [Collections](#-collections).                                                   |
| `holidays`     | `true`        | `false` keeps the holiday sets away. See [Holidays](#-holidays).                                                                                                                     |
| `holiday-days` | `3`           | How long each holiday's set is up: 3 to 7 days. New Year's Day is always 3.                                                                                                          |
| `birthday`     | `true`        | `false` keeps the Birthday set away. On a profile, the person's birthday: `03-14`, or `1990-03-14` for their age. See [Birthday](#-birthday).                                        |
| `timezone`     | `UTC`         | The zone the page's day changes in, so a holiday starts at its own midnight. An IANA name: `America/New_York`.                                                                       |
| `readme`       | `README.md`   | The README the blocks are written into; `profile/README.md` for an organization.                                                                                                     |
| `out`          | `assets`      | Where the drawings go, each part in a folder of its own: `banners`, `badges`, `trophies` and `elements`. `profile/assets` for an organization.                                       |
| `lock`         | `true`        | Keep `.github/markdown.lock.json`: what was measured, so `check` can draw the page again with no token.                                                                              |
| `prints`       | none          | Your own prints, each a name and its colours. See [Your own prints](#your-own-prints).                                                                                               |

The stub can set `mode`, `theme`, `sign`, `holidays`, `holiday-days` and
`birthday` too, as inputs of the reusable workflow. A value the stub sets wins
over the file's.

---

## 🎨 Themes

| Theme                      | What it draws                                                                                             |
| :------------------------- | :-------------------------------------------------------------------------------------------------------- |
| `standard`                 | The default: the original badges' look at the size of a header, laid out as a masthead.                   |
| `blueprint`                | A print: blue lines on white by day, a blueprint by night, with a drafting sheet's grid and title block.  |
| `redprint` to `pinkprint`  | The spectrum, one print per colour: red, orange, yellow, green, teal, blue, indigo, purple, pink.         |
| `brownprint`, `blackprint` | The two prints the trade named first after the blueprint.                                                 |
| `rainbowprint`             | The next colour of the spectrum each time something the page shows moves. The lock remembers where it is. |
| `heaven-and-hell`          | A pixel theme: angels by day and demons by night, all year. See [Pixel Themes](#-pixel-themes).           |
| `medieval`                 | A collection: a pixel design for each month, changing on the first. See [Collections](#-collections).     |

The theme reaches every part at once. The banners and the elements are drawn in
it. The badges are drawn as written in `standard`, and in a print each becomes
its plate in that print. The trophy case is drawn in it too: its five styles
are the standard theme's own, a print draws each one on its drafting paper, and
a pixel theme or a collection's design strikes each one in its pixels, at the
same sizes and in the same words. `look: standard` under
[`trophies:`](#-trophies) keeps the standard look in every theme.

[Themes and Sets](../technical/Themes.md) defines every kind of theme, and
`markdown-kit themes` lists every theme a page can pick, by kind.

### Your own prints

A print is data: a name, and a colour for its lines, its lettering and its
night sheet, each a palette token or `#RRGGBB`. `label` and `night` are
optional.

```yaml
prints:
  goldprint:
    label: Goldprint
    line: '#B8860B'
    ink: '#5C4400'
    sheet: '#7A5B00'
theme: goldprint
```

`markdown-kit palette` lists the 64 tokens. A print may not take the name of a
theme the kit already draws, a pixel theme's or a collection's included.

---

## 🌗 Pixel Themes

A pixel theme is one world drawn as pixel art, and a page that names it wears it
every day of the year. It draws the header, the footer and its buttons, the
badges, the elements and the trophy case in its pixels, at the same sizes and in
the same files, as a holiday's set does. It never changes with the month, and
its headers carry no month's mark and no sign: `sign:` belongs to a collection.
With holidays on, a holiday's set still takes over around its day and hands the
page back, and on the page's birthday the Birthday set takes it for the day.

| Theme             | What it draws                                                                                                                                                                                                                                                                                     |
| :---------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `heaven-and-hell` | Heaven & Hell: in GitHub's light mode the page is heaven, the pearly gates, the archangel and its herald over a sea of cloud; in its dark mode the same page is hell, the gates of hell, the demon and its herald over a river of lava, each thing of heaven with its fallen twin where it stood. |

```yaml
theme: heaven-and-hell
```

A pixel theme draws a page as a collection's design kept all year does, and is
no collection's: see [ADR-0012](../adrs/ADR-0012-A-Pixel-Theme-Is-Kept-All-Year.md).

---

## 📅 Collections

A collection is one subject drawn twelve ways, as pixel art: a design for each
month of the year. `theme: medieval` draws the page in the medieval
collection's design for the month it is in, and the next design takes over at
the page's midnight on the first of every month, in its `timezone`. Nothing is
remembered to make it happen, so a late or missed run is put right by the next
one, and a page that picks a collection mid-month gets that month's design at
once.

| Month     | Design      | Theme to keep it all year | Its sign      |
| :-------- | :---------- | :------------------------ | :------------ |
| January   | Longship    | `medieval-longship`       | `aquarius`    |
| February  | Chessmen    | `medieval-chessmen`       | `pisces`      |
| March     | Illuminated | `medieval-illuminated`    | `aries`       |
| April     | Cathedral   | `medieval-cathedral`      | `taurus`      |
| May       | Tournament  | `medieval-tournament`     | `gemini`      |
| June      | Mappa Mundi | `medieval-mappamundi`     | `cancer`      |
| July      | Stronghold  | `medieval-stronghold`     | `leo`         |
| August    | Mosaic      | `medieval-mosaic`         | `virgo`       |
| September | Alchemist   | `medieval-alchemist`      | `libra`       |
| October   | Tapestry    | `medieval-tapestry`       | `scorpio`     |
| November  | Forge       | `medieval-forge`          | `sagittarius` |
| December  | Hoard       | `medieval-hoard`          | `capricorn`   |

A design redraws the header, the footer and its buttons, the badges, the
elements and the trophy case, at the same sizes and in the same files, as a
holiday's set does. With holidays on, a holiday's set still takes over around
its day and hands the page back to the month's design.
Naming one design, `theme: medieval-forge`, keeps it all year. The commit on
the first of a month says which design took over.

Every collection is drawn by one hand: its twelve designs keep their own
subjects and share the light, the ink of their words, the band their grounds
fall in, their firelight, their people and their timing, so the year reads as
one artist's work. A page that follows the collection's calendar carries the
month's mark at the top centre of every header: the medieval collection's is
the month's sign of the zodiac in a gold roundel, as medieval calendars marked
their months. The mark belongs to the calendar, so a page that keeps one
design all year, `theme: medieval-forge`, is drawn without it. See
[Drawing a Collection](../technical/Collections.md).

A page can choose its own sign instead, one of the twelve in the table, and
every header then carries that sign in the roundel all year: on a design kept
all year, and on the collection's calendar in place of the month's.

```yaml
theme: medieval-forge
sign: leo
```

Every collection has exactly twelve designs, and a page can pick a collection,
or one of its designs, only once all twelve are drawn.
`markdown-kit collections` prints each collection's year and the design up
today.

---

## 🎃 Holidays

Around each holiday its set takes over the whole page and then hands it back
to the page's theme, or to a collection's design for the month: New Year's Day, Valentine's Day, Juneteenth, Independence
Day, Halloween, Thanksgiving and Christmas. A set is up for `holiday-days`,
centred on the day with the odd day before it; New Year's Day always runs from
December 31 to January 2. There is no switch per holiday: `holidays: false`
keeps them all away.

`markdown-kit holidays --year 2026 --days 5` prints every window of a year.
On the page's birthday the [Birthday](#-birthday) set takes the page from a
holiday's set for the day, and hands it back the day after.

A set redraws the header, the footer and its buttons, the badges, the elements
and the trophy case as pixel art in its own palette, at the same sizes and in
the same files, so the README's blocks never change. A badge keeps its style,
its icon and its files: a plate still has a day file and a night file, and a
live badge still shows its state, in the set's colours. A trophy keeps its
style, a cup still a cup and a crest a crest, struck in the set's pixels on the
set's own paper. A file a set cannot draw, like a title in letters its pixels
lack, is drawn in the page's own theme; a trophy case is drawn whole, in the
page's own theme, if any word of it cannot be. A `rainbowprint` holds its colour while
a set is up and picks up where it was. The commit says when a set goes up and
when it comes down.

---

## 🎂 Birthday

On the page's birthday the Birthday set takes the whole page for the day,
from midnight to midnight in its `timezone`, then hands it back. It wins over
whatever else would draw the page that day: the theme, a collection's design,
and a holiday's set too, which comes back the day after if its window is still
open. Like a holiday's set, it redraws the header, the footer and its buttons,
the badges, the elements and the trophy case as pixel art, in the same files:
piped icing round every sheet, bunting along the top that spells HAPPY
BIRTHDAY, and on every header a drip cake on a glass stand with its candles
lit and presents beside it, H1 and H2 with a piñata and a paper fan hung over
them. In a moving file a breath blows the candles out once a loop: the flames
bend and go out, smoke curls up from the wicks, and they light again.

Whose birthday it is follows the page's mode:

| Mode         | The birthday                                                                                | The cake carries                                       |
| :----------- | :------------------------------------------------------------------------------------------ | :----------------------------------------------------- |
| `repository` | The day GitHub created the repository, in the page's `timezone`, from its first anniversary | Its age, in gold number candles                        |
| `profile`    | The day the settings give: `birthday: 03-14`, or `birthday: 1990-03-14`                     | Its age when the year is given, else five slim candles |

```yaml
# a person's page, the month and the day
birthday: 03-14

# or with the year, so the cake carries their age
birthday: 1990-03-14
```

A repository's birthday is on by default and is always the day GitHub created
it: the settings can turn it off, but never name another day. GitHub keeps no
birthday for a person, so a profile has one only once its settings give it.
The year is up to the person: the settings file is as public as the page, so
a year written there, and the age the page draws from it, can be read by
anyone. The cake holds an age up to 999 in three number candles, so a whole
date's year may go back that far, and a year that would make the page older
fails the run. A February 29 birthday is kept on February 28 in a common year.

`birthday: false` keeps the set away, and it has a switch of its own:
`holidays: false` leaves the birthday on. The commit says when the set goes up,
and which birthday it is when the age is known, and when it comes down.

---

## ♟️ The Games

> [!IMPORTANT]
> **The games' designs are exclusive to
> [@tannergolden's profile README](https://github.com/tannergolden).** The kit
> draws them for that one page and nowhere else: a page anywhere else whose
> settings name them is told so. **[See the games live on @tannergolden's
> profile](https://github.com/tannergolden)**, where anyone on GitHub can play
> the next move.

The games are four, @tannergolden, the house, against everyone else on GitHub,
each drawn as an element of its own, which the profile's own engine writes into
its settings after every move (see [`elements:`](#-elements)): `chess`,
`checkers`, `pentago` and `tictac`, with the Hall of Fame of all four as
`hall-of-fame`. They come from the deepest to the quickest:

| Element    | Board                                                            | The house plays | GitHub plays | Who opens                                            |
| :--------- | :--------------------------------------------------------------- | :-------------- | :----------- | :--------------------------------------------------- |
| `chess`    | 8 × 8 squares, about 10⁴³ to 10⁵⁰ positions                      | White           | Black        | The house                                            |
| `checkers` | The 32 dark squares of 8 × 8, about 5 × 10²⁰ positions           | White           | Black        | GitHub, as Black moves first                         |
| `pentago`  | 6 × 6 holes in four quarters that turn, about 3 × 10¹⁵ positions | White           | Black        | The side the Arbiter draws once both ghosts are down |
| `tictac`   | Nine boards of 3 × 3 squares, three a side                       | X               | O            | The side the Arbiter draws once both ghosts are down |

**Who plays what, and who opens.** Each player's colour is fixed: the house
always plays White in Chess, Checkers and Pentago, and X in Tic-Tac, and GitHub
the other side. Only who moves first can change. The house opens Chess.
Checkers follows American checkers, where Black moves first, so GitHub opens it.
**Pentago and Tic-Tac are played under the Ghost Rule**, since in both the first
player has a far higher chance of winning: before the first move each side
places one ghost, a hole or a square that is nobody's, the Arbiter drawing the
side that places first (`places`), and once both ghosts are down the Arbiter
draws the side that moves first (`opens`), so neither side is favoured. A side
that goes a week without placing its ghost gets one at random from the Arbiter.
Pentago is solved: the side that sets the first marble wins with perfect play
(Geoffrey Irving, 2014). Tic-Tac is Ultimate Tic-Tac-Toe, which favours the
first player heavily too. Checkers was weakly solved as a draw in 2007, with a
small edge for the first move, and in Chess White scores about 55% in master
play. Every sheet and move reads right whichever side places or opens. These
reasons are given here and in the play repository's ADR alone: a board and its
note say only who places and who opens.

**The winning board.** A finished game, in all four, keeps its final board up
for two days before the fresh one comes by itself: the final position, who won
and how on the turn's plate (or that it was drawn), the winning line where the
game has one, and in place of the count, a countdown to the moment the fresh
board comes, its dial the share of the two days still to go, drawn in as the
file opens. A README runs nothing, so the countdown says how long was left as of
its drawing, and it is drawn again only when the page is drawn for something
else: it never makes a commit of its own. Nothing can be played on a finished
board, so its README block is the board and the note, with no move under it.

**The replay.** A game won by a person's own move gets a replay, which the
kit's `replay` command draws from the facts the profile's engine writes beside
the game's record, `games/game-<N>.replay.json`: the board playing every move
with the README's own motion, the panel following the game, and the finale, on
one loop, by day and by dark. It is no setting of a page's: tannergolden/play's
Replay workflow runs it, keeps each game's newest 25, and posts each on its
winning move's issue, where the final board's note links it. A draw gets none,
and neither does a win the Arbiter's move made.

| Sheet            | What it draws                                                                                                                                                                                                                                                                 | Files                                                              |
| :--------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------- |
| A game's board   | The position, with the state of play beside it: the sides, the turn and when it is due, the last move in notation and in words, what the game keeps count of and the score sheet's latest rows; once the game is over, who won and how, and the countdown to the fresh board. | Wide and a phone's, each moving and still, by day and dark.        |
| The Hall of Fame | All four games': the series between the house and GitHub, each game on its own row under the four together, and a podium of the leading winners across them with their wins by game, each named as their GitHub profile names them.                                           | Wide and a phone's, each moving and still, by day and dark.        |
| A winner's badge | One for each winner under the Hall in the README, each a link to that player's profile.                                                                                                                                                                                       | A day file and a dark one; the leader's glints, with a still twin. |

**Nothing on a board helps a player choose.** A sheet and its README say what
has happened and what the rules make the side to move do, a king in check or a
jump to take, and never what a move would do: no square or hole a side could
win on next, no word of what perfect play makes of a game, no call to block,
and no `+` or `#` on a move still to play, which only the score sheet writes,
once the move is made. Every move's name says what the move is, never whether
it is any good.

A board's files are named for its game, never for its position, so every move,
finished game and fresh board redraws the same files in place, and nothing an
old board drew is left behind. A Hall that shows fewer winners takes their
badges away, as every run takes away whatever the kit drew and draws no longer.

| Game         | A move is written                                                                                                                                         | The panel counts                                                              | As the file opens                                                                                                                                              |
| :----------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Chess**    | In SAN: `Nf3`, `exd5`, `O-O`, and `Qxf7#` once played                                                                                                     | What each side has taken, and the lead                                        | The last piece comes in from its square, a knight leaping and a castling king bringing its rook round, and a king in check is marked                           |
| **Checkers** | As checkers writes it, its 32 dark squares numbered: `11-15` a step, `22x15x8` a jump                                                                     | The men each side has taken, and the kings each has made                      | The last man slides, or hops each man it takes, its path drawn in behind it, and is crowned if it lands on the far row                                         |
| **Pentago**  | Its hole, the quarter it turned and which way: `e4-ur-cw`, drawn `e4 ↻ UR`; a marble that makes five on its own, its hole alone: `e4#`; a ghost, its hole | Each side's marbles left, a rack of seventeen, and where the ghosts stand now | The last marble is set in its hole and its quarter turns its quarter turn, an arrow drawn round it the way it went, and a won five are ringed and joined       |
| **Tic-Tac**  | Its mark and its square, named as chess names squares: `Xe5`, and `Xe5#` once it has won; a ghost, its square                                             | The boards each side has won, and where the ghosts stand                      | The last mark draws itself stroke by stroke, a board it wins is struck and its winner's mark drawn across it, and the board the next mark goes to is bracketed |

| Theme                | How the games are drawn                                                                                                                                                                                                                                                                                                                                                                                                                       |
| :------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `standard`           | Enamel and lit pieces under one lamp, in chess's colours: the dark squares, Tic-Tac's bars and Pentago's quarters in the theme's blue, the last move amber, and whatever the rules make the side to move answer (a king in check, a man that must jump) glowing red.                                                                                                                                                                          |
| A print              | A drawing on drafting paper in the print's colour: poché for the dark squares, the bars and the quarters, line shading for the light pieces, phantom lines where a piece stood and a revision cloud round whatever must be answered.                                                                                                                                                                                                          |
| A set                | The set's pixels, a holiday's, a pixel theme's or a month's, as it draws every part of the page: its paper, frame and lettering, a board built of its own world's stuff in a frame of its own and the Hall's podium cut from it, the same hand-drawn ivory and ebony pieces in every set, what the rules point to and what wins in the trophies' gold, and a collection's words in its hand's two inks. A set draws a game whole, every file of it, or leaves it in the page's own look. |

Round the pictures the README carries each game's words, since an image cannot
be clicked square by square: Chess's board never folded, always in view, and
each of the other three folded shut under its name; under each board every legal
move with a link that opens its ready-made issue, folded shut and signed with
what the side to move plays (♔ or ♚, ⛀ or ⛂, ⚪ or ⚫, ❌ or ⭕), and past ten
moves sorted into groups, each folded shut under its own line; and under the
Hall, the winners' badges and the leaderboard. No banner stands over a game: its
sheet says whose turn it is and by when, and how a finished game ended, so the
README says nothing twice. The
[theme-sets page](https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html#chess)
shows every sheet in every tone, every holiday's set, every pixel theme and
every month of the Medieval collection, each drawn from a sample game.

---

## 🪧 `banners:`

A text field left empty is read from GitHub: the title is the repository's
name or the person's, the tagline its description or their bio. Setting one
keeps it; listing a field under `hide` leaves it out of the drawing, and out of
the alt text with it.

| Key           | Default       | What it does                                                                                                                                |
| :------------ | :------------ | :------------------------------------------------------------------------------------------------------------------------------------------ |
| `header`      | `section`     | `sheet` (H1), `section` (H2), `strip` (H3), or `none`.                                                                                      |
| `footer`      | (the pair)    | `title-block` (F1) or `scale-bar` (F2), or `none`. Empty: the one made for the header.                                                      |
| `title`       | (from GitHub) | The title, drawn in capitals.                                                                                                               |
| `tagline`     | (from GitHub) | The line under the title.                                                                                                                   |
| `motto`       | none          | The first note. On a profile, empty reads the person's status message.                                                                      |
| `notes`       | none          | Up to two more notes after the motto.                                                                                                       |
| `description` | none          | A longer line under the tagline.                                                                                                            |
| `figures`     | (the mode's)  | Which figures, in order. See below.                                                                                                         |
| `closing`     | none          | The footer's closing words.                                                                                                                 |
| `top`         | `Back to Top` | The footer's way back up. The whole footer links to the top either way.                                                                     |
| `links`       | (GitHub's)    | Up to four buttons under the footer: a map of `Label: URL`, or a list of `Label \| URL`.                                                    |
| `hide`        | none          | Fields not drawn: `title`, `tagline`, `motto`, `notes`, `description`, `figures`, `closing`, `top`, `built`, `license`, `updated`, `links`. |

**Figures.** A repository's are `project`, `release`, `stars`, `forks`,
`watchers`, `issues`, `pulls`, `language`, `license`, `updated`, `created` and
`site`; by default `project`, `release`, `stars`, `forks`, `issues`,
`language` and `license`. A profile's are `account`, `followers`, `following`,
`repositories`, `stars`, `contributions`, `language`, `since`, `location`,
`company` and `site`; by default `account`, `followers`, `repositories`,
`stars`, `contributions`, `language` and `since`. A figure GitHub has no value
for is left out rather than drawn empty.

In `standard`, the release (or a person's account) stands in the header's
accent block, and the project's path (or a person's site) over the title; the
rest are the badges along its foot.

---

## 🏷️ `badges:`

The list of badges, in the order they stand under the header. Badges with a
black label make one row and those with the gold label a row beneath it.

The kit files each badge by what it is, and no setting names a folder. A live
badge, one with a `measure`, is drawn into `assets/badges/dynamic/`. A static
badge, which says what its author wrote, is drawn into `assets/badges/static/`,
and so is every shields.io badge `localize` draws, in `static/localized/`.
Only a live badge may wear the gold label.

```yaml
badges:
  localize: true          # optional: also turn shields.io links in the repository's Markdown into files
  list:
    - name: status        # the file's name: kebab-case, and unique
      label: Status
      message: Active
      icon: pulse         # one of the 64: markdown-kit icons
      message_color: green
      link: ./
    - name: build
      label: Build
      icon: check
      measure:
        workflow: checks.yml
    - name: coverage      # a workflow measures it: markdown-kit set coverage=87%:green
      label: Coverage
      icon: pulse
      measure: set
```

A plain list works too when `localize` is not wanted.

| Field           | What it holds                                                                                                                               |
| :-------------- | :------------------------------------------------------------------------------------------------------------------------------------------ |
| `name`          | The file's name, kebab-case and unique.                                                                                                     |
| `label`         | The left panel's word.                                                                                                                      |
| `message`       | The right panel's word. A badge the kit measures leaves it out; one a workflow sets holds what it last wrote.                               |
| `label_color`   | A token or `#RRGGBB`. Gold, the live label, by default for a live badge and black for a static one. Only a live badge may be gold.          |
| `message_color` | A token, `#RRGGBB`, or `rotate` for a colour that changes each week. A live badge's is a state.                                             |
| `icon`          | One of the 64 icons.                                                                                                                        |
| `style`         | `for-the-badge` (the default), `flat`, `flat-square`, `plastic`, `pill`, `compact`, or any as a plate: `blueprint-for-the-badge` and so on. |
| `print`         | A plate's print, when the style is a plate.                                                                                                 |
| `reserve`       | Values a plate keeps room for, so it never changes width.                                                                                   |
| `link`          | Where the badge goes when it is clicked.                                                                                                    |
| `measure`       | What makes it live: what the kit measures for it, or `set` for a value a workflow writes. See below.                                        |

**Live badges.** A badge with a `measure:` is live, and wears the gold label
unless it names another: its colour is then a state, green, yellow or red, or
slate for no data. The kit measures the first three kinds itself, every run,
and takes both the message and the state from what it measured. The fourth,
`set`, is a value a workflow measures and writes with `markdown-kit set`:

| `measure:`                                   | Message and state                                                                      |
| :------------------------------------------- | :------------------------------------------------------------------------------------- |
| `workflow: checks.yml`                       | Passing (green), Failing (red), No Data (slate). `repository:` and `branch:` optional. |
| `last-commit` (or `last-commit: owner/name`) | This Week (green), This Month (yellow), Over a Month (red).                            |
| `release` (or `release: owner/name`)         | The tag: green within 90 days, yellow within a year, red after; No Release (slate).    |
| `set`                                        | What a workflow last wrote with `markdown-kit set`; No Data (slate) until then.        |

A person's commit is what counts: the kit's own refreshes, the old kits' and
anything a bot committed never do.

**Letters.** A badge's letters are white where white holds 4.5:1 against the
panel and dark where the dark ink does, so every badge reads at the contrast
WCAG asks of text.

**From the command line.** `markdown-kit set status=Paused coverage=87%:green`
writes a badge's value into the settings, keeping every comment, and the next
run draws it: a static badge's, or a live one's that names `measure: set`. A
badge the kit measures refuses it, since the next run would measure it again.

---

## 🧩 `elements:`

The body of the page. Each element has an id, which names its files and its
README block, and a `kind`. An element is drawn only where the README carries
its markers, because only the README's author knows which section it belongs in:

```html
<!-- markdown:element:how-it-runs:start -->
<!-- markdown:element:how-it-runs:end -->
```

| Kind           | What it draws                                                                | `measure:` fills it from                                                                        |
| :------------- | :--------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------- |
| `schematic`    | Boxes and the wires between them, laid out by the kit.                       | Nothing: it is written by hand.                                                                 |
| `instruments`  | Commits per week, days since the last release, bytes by file type, counters. | git: `weeks` (10), and `count:` a map of `LABEL: glob` counted in the tree.                     |
| `milestones`   | Every version tag on a time line.                                            | git: `notable` (a map of `tag: [notes]`) and `planned` releases.                                |
| `roster`       | The people who made it, by commit count.                                     | git: `most` (4), `bots` (true), and `rename` to correct a name.                                 |
| `certificate`  | The checks a repository passes, with the evidence for each.                  | git and GitHub: licence, security policy, pinned actions, Conventional Commits, and `ci: main`. |
| `placard`      | A card that links to another repository.                                     | GitHub: `measure: owner/name`.                                                                  |
| `chess`        | Chess on @tannergolden's profile, with every legal move named under it.      | Nothing: the profile's own workflow writes it after every move.                                 |
| `checkers`     | Checkers on @tannergolden's profile, with every legal move named under it.   | Nothing: the profile's own workflow writes it after every move.                                 |
| `pentago`      | Pentago on @tannergolden's profile, with every legal move named under it.    | Nothing: the profile's own workflow writes it after every move.                                 |
| `tictac`       | Tic-Tac on @tannergolden's profile, with every legal move named under it.    | Nothing: the profile's own workflow writes it after every move.                                 |
| `chess-hall`   | Chess's Hall of Fame, a badge for each winner and the leaderboard.           | GitHub: each winner's name, and each player's login now, read by their account's ID.            |
| `hall-of-fame` | The four games' Hall of Fame, a badge for each winner and the leaderboard.   | GitHub: each winner's name, and each player's login now, read by their account's ID.            |

What the settings write wins over what was measured, so any element can carry
a `title`, a `caption` or a `desc` of its own, and a roster or a certificate
takes `size: half` to stand beside the other at half the page's width. The
fields each kind draws from are in
[`tests/fixtures/driftmark`](../../tests/fixtures/driftmark/.github/markdown.yaml),
a made-up project that writes every one of them by hand, and the games', drawn
for one profile alone, in a sample game of each beside it:
[`chess.yaml`](../../tests/fixtures/chess.yaml),
[`checkers.yaml`](../../tests/fixtures/checkers.yaml),
[`pentago.yaml`](../../tests/fixtures/pentago.yaml) and
[`tictac.yaml`](../../tests/fixtures/tictac.yaml).

**The game elements, `chess`, `checkers`, `pentago`, `tictac` and
`chess-hall`, are @tannergolden's own.** They are drawn on that profile alone,
and a page anywhere else that names them is told so. The games are played by the
profile's own workflows, which write what each draws after every move. The chess
board takes the position as `fen`, the `game` and `move` (without a `move`, the
one the position is on), the `last` move with its words and who played it when,
any `check` (the square of the king to move), the day the move is `due` by, how
many `players` have moved for GitHub, what each side has `taken`, and the score
sheet's latest rows as `history`. Its README block wraps the picture in the
game's words, since an image cannot be clicked square by square: the picture,
never folded, and under it every legal move in `moves`, each with an emoji, a
title of its own, its notation, the move in plain words and a link to its
ready-made issue, folded shut, and past ten grouped by piece, each group folded
shut too, then a `note`. No banner goes over
the board, whose sheet says whose turn it is, so a `prompt` is turned away. The
`note` is one line of text, with links at most: nothing that would open a block
of its own in the README, such as a heading, a list, a rule or a fence, and no
image. The Hall of Fame takes the `games` played and the wins of the `house`, of
GitHub (`world`) and the `draws`, and its leading winners as `people`, ranked by
their wins, each `[login, wins, last, games]`; the sheet shows five. `measure:
{}` reads each winner's name from their profile, where the sheet can letter it
in every theme (a name it cannot, or one with an `@` in it, leaves the winner
named by their login), and its README block adds a badge for each, linking to
it. Under the badges it folds shut the `leaders`: @tannergolden's own moves,
wins and games on top, then GitHub's ten leading players by their wins and then
their moves, each `[login, moves, wins, games]` and linking to their profile.
All of them are drawn in the standard theme or the page's print, as one layout,
whatever holiday, pixel theme or collection is up.

The other three boards take what chess's does wherever a game shares it: the
`game` and `move`, the `players`, the day the move is `due` by, the `last` move
as its `move` in the game's notation, its `words`, who played it (`by`) and
`when`, the score sheet's latest rows as `history`, each `[number, the opening
side's move, the reply, who chose it]`, under the Ghost Rule the first of them
the ghosts', `["G", the first ghost, the second, who chose it]`, and the
README's `note` and `moves`,
each move `[emoji, title, notation, words, link]` in one list, a title up to 100
letters and its words up to 80, its link opening that move's ready-made issue
and nothing else (a turn of Checkers with more than ten is grouped into men and
kings in the README, as chess's are by piece), and its notation never with a `+`
or `#`. In place of chess's `check`, Checkers' turn plate can say what the rules
make the side to move do as its `alert`, `must jump`; Tic-Tac's says where the
rules send the side to move, and Pentago's only that a ghost is to be set,
since a call to block would tell a player where to go. Each game's own board:

- **`checkers`**: the position as a PDN `fen`, whose turn and then White's and
  Black's men's squares, a `K` before a king's (`B:W21,22,K30:B1,2,9`): GitHub
  plays Black, whose men start on 1 to 12 and move first, and the house plays
  White, drawn at the foot; the `kings` each side has made; and whether the
  `last` move `crowned` its man. A fresh board is GitHub's turn and has a `due`.
- **`pentago`**: the `board` as six rows of six `W`, a White marble (the
  house's), `B`, a Black one (GitHub's), `G`, a ghost, or a dot, the top row
  first; `places`, the side the Arbiter drew to set the first ghost, `house` or
  `github`; once both ghosts are down, `opens`, the side it drew to set the
  first marble; and once a side has won, the `line`'s five holes, such as
  `[a3, b3, c3, d3, e3]`. Its `alert` is `set a ghost` while the ghosts go down,
  and nothing after. A move is two choices, a hole and then a turn, so each row
  of `moves` is an empty hole, and in place of its link a list of its eight
  turns, each `[quarter, way, link]`: `ul`, `ur`, `ll` or `lr`, then `cw` or
  `acw`. A ghost's hole is one choice, and its row one link.
- **`tictac`**: the `board` as nine rows of nine X, O, `G` (a ghost) or a dot,
  the top row first: the house always plays X, drawn light, and GitHub O, drawn
  dark; `places` and `opens` as Pentago's, for the first ghost and the first
  mark; and once a side has won, the winning `line`, its three boards, each
  named as Tic-Tac-Toe names a cell, such as `[a3, b2, c1]`. Its `alert` names
  the board the rules send the side to move to, by its place, such as
  `upper right board`, or says `any board` when it may play any open board, or
  `place a ghost` while the ghosts go down.

**A finished game**, in all four, takes its `result`, `{winner, how}`: the
winner, `house` or `github`, or null for a draw, and how it ended, as the game
can end. Tic-Tac is won by `three boards in a row` and drawn when there is `no
line left`; Pentago is won by `five in a row` and drawn by `five for both` or `a
full board`; Checkers is won when the side to move has `no move left` and drawn
by `repetition` or `forty moves`; Chess is won by `checkmate` and drawn by
`stalemate`, `insufficient material`, `fivefold repetition`, `seventy-five
moves` or a `dead position`. The winner is the side that made the last move,
but in Pentago either side, since a quarter's turn can make five for the side
that did not move, a win that counts in the series and for no player. A won
game of Tic-Tac or Pentago names its `line`. `next` is the day the fresh board
comes and `next_at` its moment, such as `2026-10-15T01:00:00Z`, which the
countdown counts down to and only a finished board has. A finished board lists no `moves` and says no `alert`, and
its README block is its board and its `note`, which can say what the picture
cannot, a link and all.

A row of `people` or of `leaders` may carry its player's account ID as a fifth
field, `[login, wins, last, games, id]` and `[login, moves, wins, games, id]`,
since a login can be given up and then taken by someone else. `measure: {}`
reads each such account by its ID and keeps the login it has now in `logins`,
beside the names, as `{"id": "login"}`: the sheet, the badges and the
leaderboard show and link the player by that login. An ID GitHub finds no
account for any more, a deleted account, is kept as `""`, and its player is left
off the page: the sheet, the badges and the leaderboard drop them, and the
players under them move up. So that the places stay full, `people` may carry up
to ten winners and `leaders` up to twenty of GitHub's players, twice the places
the page shows. Only GitHub's 404 says an account is gone: one it does not
answer for, refused, rate-limited or failing, stands as the last run read it. A
row without an ID is read by its login.

Every number has a ceiling the sheets have room to letter: the `game`, the
`move`, the `players`, a leader's moves, wins and games, and each `history`
row's of the three newer games up to 999,999,999; the move chess's `fen` is on
and each of chess's `history` rows up to 99,999; the kings a side has made in
Checkers up to twelve, its men; the Hall's `games`, `house`, `world` and
`draws`, and a winner's wins and games, up to 999,999; and an account's ID up to
sixteen digits. A number is a number, and text is text: a field YAML reads as
something else is turned away.

**The `hall-of-fame` element is @tannergolden's own too**: the Hall of Fame of
all four games played on that profile, shown to a reader as Chess, Checkers,
Pentago and Tic-Tac, in that order, while its data keeps the order Tic-Tac,
Pentago, Checkers and Chess. Each game's own workflow
writes it after every move, from all four games' state, as chess's writes
`chess-hall`:

```yaml
hall-of-fame:
  kind: "hall-of-fame"
  series: {"tictac": [9, 4, 2, 3], "pentago": [3, 1, 2, 0], "checkers": [5, 2, 2, 1], "chess": [12, 5, 6, 1]}
  people:
    - ["tannergolden", [4, 1, 2, 5], "2 Oct", 29, 24684994]
    - ["imvale", [0, 1, 0, 2], "19 Sep", 7, 1001]
  leaders:
    - ["tannergolden", 1240, 29, [4, 1, 2, 5], 24684994]
    - ["imvale", 40, 7, [0, 1, 0, 2], 1001]
  measure: {}
```

The `series` gives each of the four games, by its key,
`[games, house, github, draws]`: the games finished, the house's wins, GitHub's
and the draws, the three adding up to the first. The `people` are its leading
winners across all four, the house among them, each
`[login, [wins by game], last, games, id]`: their wins in each game in the
data's order, one at least in all, the day of their last and the games they
played, ranked by their wins in all four games; the sheet stands the first three
on its podium, each with their wins in every game beside that game's own mark,
and two more after it. A game's mark is its two pieces, the house's first, as
the house plays White in three games and X in the fourth: the white king then
the black, the white man then the black, the white marble then the black, X
then O. The `leaders` are @tannergolden's own row, then GitHub's leading players by
their wins in all four games and then their moves, each
`[login, moves, games, [wins by game], id]`, with no more wins in all than
games, nor games than moves; a player without a move is not on it. The account
ID is the fifth field of either and optional: `measure: {}` reads each winner's
name and each player's login now by it, exactly as it reads chess-hall's, and a
player whose account is gone leaves the sheet, the badges and the leaderboard,
the players under them moving up; `people` may carry ten winners for the sheet's
five places and `leaders` twenty of GitHub's players for the leaderboard's ten.
Its README block adds a badge for each winner shown, linking to their profile,
and the leaderboard folded shut: a column of wins for every game, headed by its
two side signs, the house's first, then the moves, then the wins in all, and a
rule that a win counts only for the player who makes the winning move. Its
counts, each game's series and a player's wins in a game and games, go up to
999,999, and its moves up to 999,999,999. It is drawn to the board's budget, in
the standard theme and every print, whatever holiday, pixel theme or collection is up.

---

## 🏆 `trophies:`

The trophy case: the core trophies with their tiers, and the achievements. A
profile's case counts a person's work; a repository's counts the repository's.
Every trophy and achievement is listed with its threshold and rarity in the
[catalogue](Catalogue.md).

| Key            | Default             | What it does                                                                  |
| :------------- | :------------------ | :---------------------------------------------------------------------------- |
| `style`        | `trophy`            | `trophy`, `crest`, `medallion`, `crystal` or `plaque`.                        |
| `look`         | `theme`             | `theme` follows the page's theme; `standard` keeps the standard look.         |
| `case`         | `both`              | `both`, or only `night` or only `day`.                                        |
| `embed`        | `picture`           | `picture` follows the reader's theme; `fragment` writes GitHub's older links. |
| `banner`       | `true`              | The level and next-up cards above the trophies.                               |
| `streak`       | `current`           | Which streak a profile's level card leads with: `current` or `longest`.       |
| `core`         | (all eight)         | A subset of the core trophies, in order.                                      |
| `enamel`       | none                | A core trophy's colour, as a token: `stars: amber`.                           |
| `achievements` | `all`               | `all`, `none`, or a list of their slugs.                                      |
| `card`         | `rank, weekly, new` | What a trophy card shows besides its tier.                                    |
| `private`      | `false`             | Count private contributions too. Needs `MARKDOWN_TOKEN`.                      |
| `scan-pages`   | `30`                | How many pages of commits, a hundred each, a run reads at most.               |
| `block`        | `true`              | `false` draws the files and leaves the README to its author.                  |

The case is drawn in the page's theme, as every part is: in `standard` in its
own styles, struck in metal and enamel; in a print as drawings on the print's
drafting paper, each card a sheet from the set, drawn further as its tier
rises; and in a holiday's set, a pixel theme or a collection's design in the
set's pixels, on its paper and in its frame. Every look keeps the style, the sizes and the
words, so the README's block reads the same in all of them.

The lock keeps the case's history: the day each tier was first reached, which
dates a NEW ribbon, and the values each card's weekly change is read from. A
page that ran the trophies kit before keeps its history: the first run takes
over `.github/trophies.lock.json`.

---

## 🔗 Traceability & Links

- [README](../../README.md): the stub, and what a run does.
- [Catalogue](Catalogue.md): every trophy and achievement.
- [ADR-0003](../adrs/ADR-0003-Holiday-Windows.md): the holiday windows.
- [ADR-0004](../adrs/ADR-0004-Standard-As-The-Default-Theme.md): `standard` as the default theme.
- [ADR-0005](../adrs/ADR-0005-The-Kit-Measures-Live-Badges.md): the live badges.
- [ADR-0006](../adrs/ADR-0006-A-Collection-Changes-With-The-Month.md): the collections.
- [ADR-0007](../adrs/ADR-0007-A-Collection-Is-Drawn-By-One-Hand.md): one hand for a collection's twelve designs.
- [ADR-0008](../adrs/ADR-0008-The-Trophy-Case-Wears-The-Pages-Theme.md): the trophy case drawn in the page's theme.
- [ADR-0009](../adrs/ADR-0009-The-Games-Wear-The-Pages-Theme.md): the games and their Hall of Fame drawn in the page's theme.
- [ADR-0011](../adrs/ADR-0011-A-Page-Has-A-Birthday.md): the page's birthday.
- [ADR-0012](../adrs/ADR-0012-A-Pixel-Theme-Is-Kept-All-Year.md): a pixel theme, kept all year.
- [Themes and Sets](../technical/Themes.md): every kind of theme and set, defined once.

### 🔗 See also

> [!TIP]
> Every canonical guide is indexed in the [&#x1F4DA; Standards Index](https://github.com/tannergolden/standards/blob/Development/docs/README.md). If you rename or move a file, update every reference to it across the repository to prevent link drift.

---

<div align="center">

**One file. Every key checked. Nothing required.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by [@tannergolden](https://github.com/tannergolden). Distributed under the MIT License.

</div>
