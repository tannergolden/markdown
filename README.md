<!--
title: '📝 MARKDOWN'
description: 'A README''s header, footer, badges, body and trophy case, measured on a schedule and drawn as committed SVGs from one stub.'
tags: [readme, svg, banners, badges, trophies, github-actions]
category: docs
-->

<!-- markdown:header:start -->
<!-- markdownlint-disable MD041 -->

<div align="center">

<a name="top"></a>

<picture>
  <source media="(max-width: 585px) and (prefers-color-scheme: dark)" srcset="assets/banners/header-narrow-dark.svg">
  <source media="(max-width: 585px)" srcset="assets/banners/header-narrow-day.svg">
  <source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" srcset="assets/banners/header-still-dark.svg">
  <source media="(prefers-reduced-motion: reduce)" srcset="assets/banners/header-still-day.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/banners/header-dark.svg">
  <img alt="markdown: Automated SVG generator for README headers, badges, trophies, and footers, rendered locally from a single stub to bypass API rate limits. Measured nightly, never fetched. Project: tannergolden/markdown. Release: v1.16.1. Stars: 0. Forks: 0. Open issues: 0. Language: Python." src="assets/banners/header-day.svg">
</picture>

</div>
<!-- markdown:header:end -->

<!-- markdown:badges:start -->
<div align="center">

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/badges/static/status-dark.svg"><img alt="Status: Active" src="assets/badges/static/status.svg"></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="assets/badges/static/python-dark.svg"><img alt="Python: Standard library only" src="assets/badges/static/python.svg"></picture>
<a href="LICENSE"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/badges/static/license-dark.svg"><img alt="License: MIT, games proprietary" src="assets/badges/static/license.svg"></picture></a>

<img alt="CI: Passing" src="assets/badges/dynamic/ci.svg">
<img alt="Release: v1.16.1" src="assets/badges/dynamic/release.svg">
<img alt="Last Commit: This Week" src="assets/badges/dynamic/last-commit.svg">

</div>
<!-- markdown:badges:end -->

> [!TIP]
> **This page is the kit drawing itself.** Its header, the badge row, the
> schematic, the trophy case and the footer are files the kit drew, in the
> `blueprint`, from the [same stub](#-one-stub) it asks you to copy, and around
> each holiday the page wears that holiday's set. **To see profile mode, check
> out my profile, [@tannergolden](https://github.com/tannergolden).**

---

## 💡 What This Is

A README's images usually come from someone else's server: a stats card, a
badge service, a banner generator. Every one is a request on every page view,
and a dependency on that server's uptime for your page to render. A header
typed by hand is out of date the day your description changes.

This kit draws them instead, and keeps them current. One scheduled run
measures the page over GitHub's API and git, draws every image as an SVG,
writes the README's blocks, and commits the lot once:

| Part         | What it draws                                                                           |
| :----------- | :-------------------------------------------------------------------------------------- |
| **Banners**  | The header and the footer, and the links under the footer.                              |
| **Badges**   | A row of static badges, and a row of live ones whose value and colour the run measures. |
| **Elements** | The body: a schematic, instruments, milestones, a roster, a certificate, placards.      |
| **Trophies** | The trophy case: eight core trophies with their tiers, and a hundred achievements.      |

Every image is a **committed file**, served by GitHub with the rest of the
repository: up as long as the repository is, with nothing to rate-limit and no
third party in the path. The only thing on a schedule is the refresh, and a
refresh that is late or skipped changes nothing a reader sees.

A page is a person's profile or a repository. Organization pages are next.

---

## 👤 The Example: A Profile

**To see how profile mode looks, check out my profile,
[@tannergolden](https://github.com/tannergolden).** Its repository,
[**tannergolden/tannergolden**](https://github.com/tannergolden/tannergolden),
is the example of all of it on a profile repository. Its README is drawn by
this kit every night at midnight EST, in profile mode, in the medieval
collection's Illuminated all year with Capricorn's roundel on every header,
with the holidays on, from one stub and one settings file:

| Part         | On the profile                                                                                                                                                                                                                |
| :----------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Banners**  | A header read from GitHub, the name and the bio, with a motto, a note and six figures; a footer with its closing words, and four buttons under it.                                                                            |
| **Badges**   | Three static badges, and two live ones the run measures: whether the standards pass their own checks, and how long ago the last commit was.                                                                                   |
| **Elements** | A schematic of how its repositories fit together, written by hand, and placards for the two latest releases and two good first issues, which its own scripts rewrite weekly.                                                  |
| **Games**    | Chess, Checkers, Pentago and Tic-Tac, @tannergolden against GitHub, played live: each board after every move, every legal move a link that plays it, and the Hall of Fame with its leaderboard, drawn for this profile alone. |
| **Trophies** | The case in profile mode: five core trophies in one row, the level and next-up cards over them, and the achievements under them.                                                                                              |

Its stub is the one below with `mode: profile`, `theme: medieval-illuminated`,
`sign: capricorn` and `holidays: 'true'`, and
[its settings](https://github.com/tannergolden/tannergolden/blob/Development/.github/markdown.yaml)
set up every part, with a comment on each. This README is the other example:
this repository's own page, in repository mode, in the `blueprint`, with the
holidays on and its trophy case over the footer, drawn every night by the
[stub below](#-one-stub), exactly as yours would be.

---

## 🚀 One Stub

Your repository holds one small workflow that names the schedule. The
checkout, the measurement, the drawing and the commit all happen here, so a fix
lands once and reaches every README pinned to `v1`.

```yaml
# .github/workflows/markdown.yml
name: '📝 Markdown'

on:
  schedule:
    - cron: '0 0 * * *'   # every night at midnight UTC
  workflow_dispatch:

concurrency:              # one drawing at a time; the next waits its turn
  group: markdown-${{ github.ref }}
  cancel-in-progress: false

permissions: {}

jobs:
  markdown:
    permissions:
      contents: write        # the images, the README's blocks and the lock
      pull-requests: write   # only used with commit: pr
    uses: tannergolden/markdown/.github/workflows/markdown.yml@v1
    secrets:
      MARKDOWN_TOKEN: ${{ secrets.MARKDOWN_TOKEN }}   # the one secret the kit reads
```

That is the whole setup. With no settings at all, the page gets a header and a
footer read from GitHub and a trophy case, in the `standard` theme, with the
holidays on. Two runs never draw at once: one that starts while another is
drawing waits for it, then draws the page as it stands by then, so a redraw
started straight after another is queued rather than failing to push. And the
kit is handed `MARKDOWN_TOKEN` alone, never the repository's other secrets. The
stub can set the choices made most often:

| Input           | Default          | What it does                                                                |
| :-------------- | :--------------- | :-------------------------------------------------------------------------- |
| `mode`          | (guessed)        | `profile` or `repository`. A repository named after its owner is a profile. |
| `theme`         | `standard`       | `standard`, a print, `rainbowprint`, a print of your own, or a collection.  |
| `sign`          | (the month's)    | The sign of the zodiac a collection's headers carry all year, as `leo`.     |
| `holidays`      | `true`           | `'false'` keeps the holiday sets away.                                      |
| `holiday-days`  | `3`              | How long each holiday's set is up, 3 to 7 days.                             |
| `check`         | `false`          | Only check that the committed page is current. See below.                   |
| `commit`        | `push`           | `pr` opens or updates one pull request instead of pushing.                  |
| `commit-branch` | `chore/markdown` | The branch that pull request rides on.                                      |

Everything else a page can set lives in `.github/markdown.yaml`, and
[`docs/Settings.md`](docs/Settings.md) has every key.

> [!TIP]
> **`MARKDOWN_TOKEN` is optional.** `GITHUB_TOKEN` reads everything public, so
> a public page needs nothing. A read-only personal token saved as
> `MARKDOWN_TOKEN` is read instead when it is there, which also lets a profile
> count private contributions (`trophies: private: true`). The stub hands the
> kit that one secret by name; where it is not set, the run uses `GITHUB_TOKEN`.

---

## 🧭 How A Run Draws A Page

<!-- markdown:element:how-it-runs:start -->
<picture>
  <source media="(max-width: 585px) and (prefers-color-scheme: dark)" srcset="assets/elements/how-it-runs-narrow-dark.svg">
  <source media="(max-width: 585px)" srcset="assets/elements/how-it-runs-narrow-day.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/elements/how-it-runs-dark.svg">
  <img alt="How a run draws a page. A repository&#x27;s stub calls the kit&#x27;s workflow, which reads the settings, measures the page over GitHub&#x27;s API and git, draws every file, keeps what it measured in the lock, and commits the page once." src="assets/elements/how-it-runs-day.svg">
</picture>
<!-- markdown:element:how-it-runs:end -->

Each run measures everything again, so a run GitHub delays or drops loses
nothing: the next one catches up. A day on which nothing the page shows has
moved writes nothing at all. When something did move, the commit says what:

```text
chore(markdown): 🪧 redraw with release v1.4.0 and 212 stars

Measured octo/drift on 2026-10-03. The header reads DRIFT, with project
octo/drift, release v1.4.0, 212 stars, 18 forks, 3 open issues, language
Rust and license MIT. The footer dates the last change 2026-10-01.

Changed since the last drawing: release v1.4.0 (was v1.3.2) and 212
stars (was 198).
```

The kit owns only what sits between its markers in the README, so every word
of yours around them stays yours. On a first run the header goes at the top,
the badges under it, the trophy case over the footer and the footer at the
foot; an element goes where you put its markers.

---

## 🎨 One Theme For The Whole Page

One setting colours everything, so the header, the badges, the body and the
trophy case read as one family:

- **`standard`**, the default: the original badges' own look at the size of a
  header. Its header opens with one badge the width of the page, the title in
  its black and the release in its accent, and its figures stand along the foot
  as the badges a README would carry for them. Every letter holds 4.5:1 against
  its ground.
- **Eleven prints**, the colours a drawing is reproduced in: `redprint`
  through `pinkprint` along the spectrum, `blueprint` among them, then
  `brownprint` and `blackprint`. Each draws the page as a drafting sheet, its
  lines on white by day and its sheet by night.
- **`rainbowprint`** moves to the next colour of the spectrum each time
  something the page shows changes.
- **Your own prints**, a name and three colours in the settings.
- **Collections**, one subject drawn as pixel art twelve ways, a design for
  each month. `medieval` draws the page in the month's design and changes on
  the first of every month: a longship under the northern lights in January,
  stained glass at Easter, the jousts of May, the Bayeux charge in October,
  a dragon on its hoard in December. Naming one design, like
  `medieval-forge`, keeps it all year. See
  [Collections](docs/Settings.md#-collections).

The header, the footer and the body each come as a **day** file and a
**dark** file, and the README shows one through a `<picture>` that follows the
reader's theme, with a still file for reduced motion and a narrow one for a
phone.

Around each holiday its own set takes over the page, then hands it back: New
Year's Day, Valentine's Day, Juneteenth, Independence Day, Halloween,
Thanksgiving and Christmas. A set redraws the banners, the badges, the
elements and the trophy case as pixel art, in the same files.

The trophy case wears the theme too, and keeps its style, its sizes and its
words: `standard` strikes its cups, crests, medallions, crystals and plaques
in metal and enamel, a print draws each card as a sheet on its drafting paper,
drawn further as the tier rises, and a holiday's set or a collection's design
strikes it in pixels, on its own paper and in its own frame.
`look: standard` under [`trophies:`](docs/Settings.md#-trophies) keeps the
standard look in every theme.

<table>
  <tr>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/themes/index.html#standard"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/themes/standard/h2-still-dark.svg"><img src="docs/themes/standard/h2-still-day.svg" alt="The H2 header in standard, the default theme" width="100%"></picture></a>
      <br /><sub><code>standard</code>, the default</sub>
    </td>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/themes/index.html#blueprint"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/themes/blueprint/h2-still-dark.svg"><img src="docs/themes/blueprint/h2-still-day.svg" alt="The H2 header in blueprint, this page's print" width="100%"></picture></a>
      <br /><sub><code>blueprint</code>, this page's print</sub>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/themes/index.html#halloween"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/themes/halloween/h2-still-dark.svg"><img src="docs/themes/halloween/h2-still-day.svg" alt="The H2 header in Halloween's set" width="100%"></picture></a>
      <br /><sub>Halloween's set, October 30 to November 1</sub>
    </td>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/themes/index.html#christmas"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/themes/christmas/h2-still-dark.svg"><img src="docs/themes/christmas/h2-still-day.svg" alt="The H2 header in Christmas's set" width="100%"></picture></a>
      <br /><sub>Christmas's set, December 24 to 26</sub>
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="25%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/themes/index.html#standard"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/themes/standard/trophy-trophy-3-dark.svg"><img src="docs/themes/standard/trophy-trophy-3-day.svg" alt="A gold trophy card in standard, the default theme" width="100%"></picture></a>
      <br /><sub><code>standard</code></sub>
    </td>
    <td width="25%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/themes/index.html#blueprint"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/themes/blueprint/trophy-trophy-3-dark.svg"><img src="docs/themes/blueprint/trophy-trophy-3-day.svg" alt="A gold trophy card in blueprint, drawn on its drafting paper" width="100%"></picture></a>
      <br /><sub><code>blueprint</code></sub>
    </td>
    <td width="25%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/themes/index.html#halloween"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/themes/halloween/trophy-trophy-3-dark.svg"><img src="docs/themes/halloween/trophy-trophy-3-day.svg" alt="A gold trophy card in Halloween's set, in pixels" width="100%"></picture></a>
      <br /><sub>Halloween's set</sub>
    </td>
    <td width="25%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/themes/medieval/index.html"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/themes/medieval/medieval-forge/trophy-trophy-3-dark.svg"><img src="docs/themes/medieval/medieval-forge/trophy-trophy-3-day.svg" alt="A gold trophy card in Forge, the medieval collection's November design" width="100%"></picture></a>
      <br /><sub><code>medieval</code> in November</sub>
    </td>
  </tr>
</table>

**[See every theme, drawn by the kit](https://raw.githack.com/tannergolden/markdown/Development/docs/themes/index.html)**:
the theme-sets page shows each theme's headers, phone files, footers, elements,
badges and trophy case on GitHub's light and dark grounds, at the size a README
shows them.
The page is [`docs/themes/index.html`](docs/themes/index.html) in this
repository, and the link opens it through raw.githack.com, because GitHub
shows an HTML file as its source.

---

## ♟️ The Games On @tannergolden's Profile

> [!IMPORTANT]
> **The games' designs are exclusive to
> [@tannergolden's profile README](https://github.com/tannergolden).** The kit
> draws them for that one page and nowhere else: any other page whose settings
> name them is told so. **[See the games live on @tannergolden's
> profile](https://github.com/tannergolden)**, where anyone on GitHub can play
> the next move.

The kit draws four games for one page, @tannergolden, the house, against
everyone else on GitHub, from the deepest to the quickest:

| Game     | Board                                                            | The house plays | GitHub plays | Who opens                                            |
| :------- | :--------------------------------------------------------------- | :-------------- | :----------- | :--------------------------------------------------- |
| Chess    | 8 × 8 squares, about 10⁴³ to 10⁵⁰ positions                      | White           | Black        | The house                                            |
| Checkers | The 32 dark squares of 8 × 8, about 5 × 10²⁰ positions           | White           | Black        | GitHub, as Black moves first                         |
| Pentago  | 6 × 6 holes in four quarters that turn, about 3 × 10¹⁵ positions | White           | Black        | The side the Arbiter draws once both ghosts are down |
| Tic-Tac  | Nine boards of 3 × 3 squares, three a side                       | X               | O            | The side the Arbiter draws once both ghosts are down |

A player picks a move under a board on the profile, its link opens a
ready-made issue in [tannergolden/play](https://github.com/tannergolden/play),
and the profile's own engine plays it and has the kit draw the page again.

**Who plays what, and who opens.** Each player's colour is fixed: the house
always plays White in Chess, Checkers and Pentago, and X in Tic-Tac, and GitHub
the other side. Only who moves first can change. The house opens Chess, as
White does. Checkers follows American checkers, where Black moves first, so
GitHub opens it. In the other two the first player has a far higher chance of
winning, so **Pentago and Tic-Tac are played under the Ghost Rule**: before the
first move each side places one ghost, a hole or a square that is nobody's, the
Arbiter drawing the side that places first, and once both ghosts are down the
Arbiter draws the side that moves first, so neither side is favoured. A side
that goes a week without placing its ghost gets one at random.

- **Pentago is solved**: the side that sets the first marble wins with perfect
  play (Geoffrey Irving, 2014).
- **Tic-Tac is Ultimate Tic-Tac-Toe**, nine games of Tic-Tac-Toe as one, and it
  favours its first player heavily too.
- **Checkers** was weakly solved as a draw in 2007, and its first move's edge is
  small; **in Chess**, White scores about 55% in master play. Neither needs the
  Ghost Rule.

These reasons belong to the kit's documentation and the play repository's ADR
alone: a board and its note say only who places and who opens.

**The winning board.** Every finished game, chess's included, keeps its final
board up for two days before a fresh one comes by itself: the final position,
who won and how on the turn's plate, or that it was drawn, the winning line
where the game has one, and in place of the count a countdown to the moment the
fresh board comes, its dial drawn in as the file opens. A README runs nothing,
so the countdown says how long was left as of its drawing, and it is redrawn
only when the page is drawn for something else, never in a commit of its own.
Nothing can be played on a finished board, so its README block is the board and
the note, with no move under it.

**The replay.** A game won by a person's own move is played again: the kit's
`replay` command draws, from the facts the profile's engine writes, the board
in its frame playing every move with the README's own motion, the panel
following the game move by move, and a finale of the winner ringed and the
losing side faded, all on one loop, by day and by dark. Each player is a
halftone of their avatar, dots in the print's ink and no image in the file, or
their initials, and an account that is gone is an empty dial with no name. A
replay is drawn in the page's print, and in blackprint when the page's theme
has no replay look of its own. tannergolden/play keeps each game's newest 25
and posts each on its winning move's issue.

**Nothing on a board helps a player choose.** A sheet and its README say what
has happened and what the rules make the side to move do, a king in check or a
jump to take, and never what a move would do: no square or hole a side could win
on next, no word of what perfect play makes of a game, no call to block, and no
`+` or `#` on a move still to play. Every move is named for what it is, never
for whether it is any good.

Like a theme, each game is a design of its own, drawn in every look the page
can take, and the four are one family: the same sheet and band, the same panel
beside the board a section at a time (the two sides, whose turn it is and
until when, the last move in notation and in words, what the game keeps count
of, and the score sheet), and the same motion as each file opens:

| Game         | A move is written                                                                                                                                         | The panel counts                                                              | As the file opens                                                                                                                                              |
| :----------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Chess**    | In SAN: `Nf3`, `exd5`, `O-O`, and `Qxf7#` once played                                                                                                     | What each side has taken, and the lead                                        | The last piece comes in from its square, a knight leaping and a castling king bringing its rook round, and a king in check is marked                           |
| **Checkers** | As checkers writes it, its 32 dark squares numbered: `11-15` a step, `22x15x8` a jump                                                                     | The men each side has taken, and the kings each has made                      | The last man slides, or hops each man it takes, its path drawn in behind it, and is crowned if it lands on the far row                                         |
| **Pentago**  | Its hole, the quarter it turned and which way: `e4-ur-cw`, drawn `e4 ↻ UR`; a marble that makes five on its own, its hole alone: `e4#`; a ghost, its hole | Each side's marbles left, a rack of seventeen, and where the ghosts stand now | The last marble is set in its hole and its quarter turns its quarter turn, an arrow drawn round it the way it went, and a won five are ringed and joined       |
| **Tic-Tac**  | Its mark and its square, named as chess names squares: `Xe5`, and `Xe5#` once it has won; a ghost, its square                                             | The boards each side has won, and where the ghosts stand                      | The last mark draws itself stroke by stroke, a board it wins is struck and its winner's mark drawn across it, and the board the next mark goes to is bracketed |

- **Every tone**: the standard theme's enamel, chess's own board and lit pieces
  under one lamp, the last move marked amber and whatever the rules make the
  side to move answer (a king in check, a man that must jump) glowing red; the
  house's pieces are the light ones in every game, White's men and marbles and
  the X, and GitHub's the dark, Black's and the O; Tic-Tac's squares and bars
  are chess's light and dark squares, Pentago's quarters are the theme's cobalt,
  and Checkers plays on chess's own board, White at the foot as chess's White
  is; a ghost is the board's own material, ringed or edged in phantom lines. Or
  a print's drawing on drafting paper: poché for the dark squares, the bars and
  the quarters, line shading for the light pieces, phantom lines where a piece
  stood and a revision cloud round whatever must be answered. Or, while a
  holiday's set or a collection's design is up, its pixels: its paper, frame and
  lettering, a board built of its own world's stuff, a ship's planks, a
  cathedral's leaded glass or a mosaic's tesserae, in a frame of its own,
  Tic-Tac's nine boards a chequer of it and Pentago's plates lying in a bed
  inside the frame, and the Hall's podium cut from it too, crenellated for a
  castle or tied with ribbon for Christmas; the same hand-drawn ivory and ebony
  pieces in every set, what the rules point to and what wins in the trophies'
  gold, and a collection's words in its hand's two inks. A set draws a game
  whole, or leaves it in the page's own look.
- **The Hall of Fame** of all four games: the series between the house and
  GitHub, each game on its own row under the four together, in the README's
  order and each named by its two pieces, the house's first; then a podium of
  the three leading winners across all four and two more beside it, each with
  their wins by game and named as their GitHub profile names them. Under it in
  the README, a badge for each winner, the leader's glinting, and the
  leaderboard folded shut: a column of wins for each game, then moves, then
  wins in all. A win counts only for the player who makes the winning move,
  and nothing the Arbiter plays counts for anyone.

Each sheet comes as a **day** file and a **dark** file, wide and on a phone,
moving as it opens and still for reduced motion, like a header. Round the
pictures the README carries each game's words, since an image cannot be
clicked square by square: every legal move with a link that opens its
ready-made issue, folded shut under one line saying whose turn it is, signed
with what that side plays (♔ or ♚, ⛀ or ⛂, ⚪ or ⚫, ❌ or ⭕), and past ten
moves sorted into groups, each folded shut too. Chess's board is never folded,
and each of the other three games is folded shut under its name.

<table>
  <tr>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/themes/index.html#chess"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/themes/chess/chess-wide-blackprint-still-dark.svg"><img src="docs/themes/chess/chess-wide-blackprint-still-day.svg" alt="The chess board in blackprint, from a sample game" width="100%"></picture></a>
      <br /><sub>Chess, in <code>blackprint</code></sub>
    </td>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/themes/index.html#checkers"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/themes/checkers/checkers-wide-blackprint-still-dark.svg"><img src="docs/themes/checkers/checkers-wide-blackprint-still-day.svg" alt="The Checkers board in blackprint, from a sample game" width="100%"></picture></a>
      <br /><sub>Checkers, in <code>blackprint</code></sub>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/themes/index.html#pentago"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/themes/pentago/pentago-wide-blackprint-still-dark.svg"><img src="docs/themes/pentago/pentago-wide-blackprint-still-day.svg" alt="The Pentago board in blackprint, from a sample game under the Ghost Rule" width="100%"></picture></a>
      <br /><sub>Pentago, in <code>blackprint</code></sub>
    </td>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/themes/index.html#tictac"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/themes/tictac/tictac-wide-blackprint-still-dark.svg"><img src="docs/themes/tictac/tictac-wide-blackprint-still-day.svg" alt="The Tic-Tac board in blackprint, from a sample game under the Ghost Rule" width="100%"></picture></a>
      <br /><sub>Tic-Tac, in <code>blackprint</code></sub>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/themes/index.html#chess"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/themes/chess/chess-wide-standard-still-dark.svg"><img src="docs/themes/chess/chess-wide-standard-still-day.svg" alt="The chess board in standard, from a sample game" width="100%"></picture></a>
      <br /><sub>Chess, in <code>standard</code></sub>
    </td>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/themes/index.html#checkers"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/themes/checkers/checkers-wide-standard-still-dark.svg"><img src="docs/themes/checkers/checkers-wide-standard-still-day.svg" alt="The Checkers board in standard, from a sample game" width="100%"></picture></a>
      <br /><sub>Checkers, in <code>standard</code></sub>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/themes/index.html#pentago"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/themes/pentago/pentago-wide-standard-still-dark.svg"><img src="docs/themes/pentago/pentago-wide-standard-still-day.svg" alt="The Pentago board in standard, from a sample game under the Ghost Rule" width="100%"></picture></a>
      <br /><sub>Pentago, in <code>standard</code></sub>
    </td>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/themes/index.html#tictac"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/themes/tictac/tictac-wide-standard-still-dark.svg"><img src="docs/themes/tictac/tictac-wide-standard-still-day.svg" alt="The Tic-Tac board in standard, from a sample game under the Ghost Rule" width="100%"></picture></a>
      <br /><sub>Tic-Tac, in <code>standard</code></sub>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/themes/index.html#hall-of-fame"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/themes/hall-of-fame/hall-of-fame-wide-blackprint-still-dark.svg"><img src="docs/themes/hall-of-fame/hall-of-fame-wide-blackprint-still-day.svg" alt="The Hall of Fame of all four games in blackprint, from a sample of fictional winners" width="100%"></picture></a>
      <br /><sub>The Hall of Fame, in <code>blackprint</code></sub>
    </td>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/themes/index.html#hall-of-fame"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/themes/hall-of-fame/hall-of-fame-wide-standard-still-dark.svg"><img src="docs/themes/hall-of-fame/hall-of-fame-wide-standard-still-day.svg" alt="The Hall of Fame of all four games in standard, from a sample of fictional winners" width="100%"></picture></a>
      <br /><sub>The Hall of Fame, in <code>standard</code></sub>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/themes/index.html#chess"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/themes/chess/chess-wide-halloween-still-dark.svg"><img src="docs/themes/chess/chess-wide-halloween-still-day.svg" alt="The chess board in the Halloween set's pixels, from a sample game" width="100%"></picture></a>
      <br /><sub>Chess, in the <code>halloween</code> set</sub>
    </td>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/themes/index.html#hall-of-fame"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/themes/hall-of-fame/hall-of-fame-wide-medieval-hoard-still-dark.svg"><img src="docs/themes/hall-of-fame/hall-of-fame-wide-medieval-hoard-still-day.svg" alt="The Hall of Fame of all four games in the Hoard, December's design of the Medieval collection, from a sample of fictional winners" width="100%"></picture></a>
      <br /><sub>The Hall of Fame, in <code>medieval-hoard</code>, December's design</sub>
    </td>
  </tr>
</table>

**[See the games in every tone, drawn by the kit](https://raw.githack.com/tannergolden/markdown/Development/docs/themes/index.html#chess)**:
the theme-sets page shows each game's board and its phone files, and the Hall
of Fame of all four with its phone files and the winners' badges, in the
standard theme and every print, every holiday's set and every month of the
Medieval collection, each from a sample whose players are as fictional as
driftmark's contributors. What the games' settings hold is in
[Settings](docs/Settings.md#-elements); the games themselves are
[live on @tannergolden's profile](https://github.com/tannergolden).

---

## 🔍 Checking A Page

The lock, `.github/markdown.lock.json`, keeps what each run measured. So the
committed page can be drawn again with no token and no network, and compared
with what is committed: a hand-edited image, a missing one, a README block that
drifted, or settings changed without a run all show up. For pull-request CI:

```yaml
on: pull_request

jobs:
  page:
    permissions:
      contents: write
      pull-requests: write
    uses: tannergolden/markdown/.github/workflows/markdown.yml@v1
    with:
      check: true
```

---

## 🖥️ On Your Own Machine

The kit is standard-library Python, 3.10 or later, with nothing to install:

```bash
python3 src/markdown-kit.py preview --root /tmp/page       # a sample page, the way a run draws it
python3 src/markdown-kit.py settings --root .              # a repository's settings, every default filled in
python3 src/markdown-kit.py check --root .                 # is the committed page current?
python3 src/markdown-kit.py set --root . status=Paused     # write a badge's value into the settings
python3 src/markdown-kit.py holidays --year 2026 --days 5  # every holiday's window
python3 src/markdown-kit.py collections                    # each collection's design for every month
```

`python3 src/markdown-kit.py --help` lists the rest: `run`, `render`,
`measure`, `lint`, `catalogue`, `calibrate`, `palette`, `icons`, `version`, and
`replay`, which draws a finished game's replay for @tannergolden's profile.

---

## 📦 What's Inside

| Path                             | Purpose                                                                                                      |
| :------------------------------- | :----------------------------------------------------------------------------------------------------------- |
| `.github/workflows/markdown.yml` | **The workflow** every stub calls: checkout, the kit, the commit                                             |
| `actions/markdown/`              | **The action** the workflow runs: one run of the kit on the checkout                                         |
| `src/markdown-kit.py`            | **The kit's** command line, and the one place its layers meet                                                |
| `src/domain/`                    | What a page looks like: the palette, the lettering, the themes and every drawing                             |
| `src/app/`                       | What a run does: the settings, the measurement, the plan and the commit                                      |
| `src/infra/`                     | Files, git, GitHub's API, the clock, and the kit's data files                                                |
| `docs/`                          | [Settings](docs/Settings.md), the trophies' [catalogue](docs/Catalogue.md), and the decisions behind the kit |
| `docs/themes/`                   | The theme-sets page: every theme as the kit draws it, from `make themes`                                     |
| `tests/`                         | Unit, integration and end-to-end suites, and the fixtures they check against                                 |

`make lint test` runs everything CI runs, and `make draw` draws a sample profile
and a sample repository page into `preview/`, which git leaves alone.
`make themes` draws every theme into `docs/themes`, which is committed, so run
it after changing a theme.
[`docs/technical/Source-Code.md`](docs/technical/Source-Code.md) lays out the
layers and the rules between them.

---

## 🌿 How The Workflows Work

Most workflows here are **triggers**. Their logic lives in
[`tannergolden/standards`](https://github.com/tannergolden/standards) and is
pulled in by `uses:`. GitHub only runs a workflow that lives in the repository
being pushed to, which is why these small files exist here at all. They are
grouped by what they do, so one push produces one run with every check in it.
Four are the kit's own: the workflow every page calls, this repository's own
page, the release, and the calibration.

| Workflow                   | Gives you                                                                |
| :------------------------- | :----------------------------------------------------------------------- |
| `markdown.yml`             | The reusable workflow every page's stub calls                            |
| `own-page.yml`             | This README, drawn every night by the stub above, at `v1`                |
| `cut-release.yml`          | Cuts `vX.Y.Z` and moves `v1`, by calling the standards                   |
| `calibrate.yml`            | Measures, each quarter, the repositories the trophies are set against    |
| `checks.yml`               | The gates: lint/test/build, secret scan, CodeQL, workflow lint           |
| `governance.yml`           | PR title and DCO checks, onboarding, triage, stale sweep, slash commands |
| `release.yml`              | Draft notes, publish assets, registries, prune superseded releases       |
| `maintenance.yml`          | Prunes stale deployments; deletes draft releases on request              |
| `prune-runs.yml`           | Prunes workflow run history, with its logs and artifacts                 |
| `lifecycle.yml`            | Claims this repository once; tells you when a new major exists           |
| `dependabot-automerge.yml` | Approves and queues Dependabot's patch and minor updates                 |
| `ci-failure-alert.yml`     | Opens an issue when a watched workflow fails, closes it on green         |
| `apply-standards.yml`      | Dispatch-only. The label taxonomy and branch protection                  |
| `template-sync.yml`        | Dispatch-only. The template's later fixes, as one pull request           |
| `auto-format.yml`          | Formats what a push touched                                              |
| `auto-index.yml`           | Redraws every folder's log after a push, as one pull request             |
| `preview-deploy.yml`       | Deploys pushes to a preview target, once one is configured               |
| `verify-stubs.yml`         | Proves every job's permission ceiling matches its called workflow        |

**Do not rename the job ids** `ci` and `secrets` (in `checks.yml`) or `pr`
(in `governance.yml`). A called workflow reports its checks as
`<job id> / <job name>`, so branch protection depends on them - the file a
job lives in does not matter, but its id does.

> [!IMPORTANT]
> **🎯 Apply Standards needs a token for two of its three jobs.** Applying the
> label taxonomy needs nothing. **Writing the settings and the rulesets** each
> need a token with administration write as `ADMIN_TOKEN`. Without it, those
> jobs stop with a sentence naming the missing token instead of a bare `403`.
>
> A fine-grained token scoped to your repositories generated from the
> templates, with **Administration: Read and write** and nothing else, is all
> it needs. Step-by-step:
> [Creating the ADMIN_TOKEN](https://github.com/tannergolden/standards/blob/Development/docs/operations/Branch-Protection.md#-creating-the-admin_token).
> You can skip it entirely by applying the settings and rulesets yourself,
> where your own rights are already enough.

### Staying current takes no effort

`@v1` is a **moving major tag**, both ways. Every fix in the kit's v1 line
reaches every README whose stub pins `v1` the next time it runs, and every fix
in the standards' v1 line reaches the workflows here the moment it is
published. Breaking changes never arrive that way, because a new major is a
different tag.

The stubs themselves came from the
[`tannergolden/path`](https://github.com/tannergolden/path) template, and its
later fixes arrive whenever you run 🔄 Template Sync, as one pull request
merged with whatever changed here. [`.github/template-sync`](.github/template-sync)
lists what it keeps current, and
[`.github/template-sync.md`](.github/template-sync.md) says how.

---

## 📚 The Standards

Everything about how to branch, review, release, and secure a repository lives
in the [Standards Index](https://github.com/tannergolden/standards/blob/Development/docs/README.md).
This repository follows it **by link**.

---

<!-- markdown:trophies:start -->
<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/level.svg"><img src="assets/trophies/level-day.svg" alt="tannergolden/markdown: level 21, 7,070 XP, case 27% complete, released 0 days ago"></picture>
  <picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/next-up.svg"><img src="assets/trophies/next-up-day.svg" alt="Next up: Signed I 90%, Issues Resolved to Bronze 40%, Same-Day Fix 40%"></picture>
</p>

<p align="center">
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-stars"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/stars.svg"><img src="assets/trophies/stars-day.svg" alt="Stars trophy: Unranked, 0, 0% to Bronze"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-forks"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/forks.svg"><img src="assets/trophies/forks-day.svg" alt="Forks trophy: Unranked, 0, 0% to Bronze"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-contributors"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/contributors.svg"><img src="assets/trophies/contributors-day.svg" alt="Contributors trophy: Bronze, 2, 0% to Silver, top 43%, up 1 this week, newly reached"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-commits"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/commits.svg"><img src="assets/trophies/commits-day.svg" alt="Commits trophy: Bronze, 119, 4% to Silver, top 6.3%, up 80 this week, newly reached"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-releases"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/releases.svg"><img src="assets/trophies/releases-day.svg" alt="Releases trophy: Bronze, 2, 25% to Silver, top 7.3%, up 1 this week"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-merged"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/merged.svg"><img src="assets/trophies/merged-day.svg" alt="Merged PRs trophy: Unranked, 0, 0% to Bronze"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-resolved"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/resolved.svg"><img src="assets/trophies/resolved-day.svg" alt="Issues Resolved trophy: Unranked, 4, 40% to Bronze, up 3 this week"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-active"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/active.svg"><img src="assets/trophies/active-day.svg" alt="Active Days trophy: Unranked, 6 days, 20% to Bronze, up 4 this week"></picture></a>
</p>

<details>
<summary><b>Achievements</b> · 28 of 100 earned · next: Signed I, 90%</summary>

<p align="center"><b>Launch</b></p>
<p align="center">
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-first-release"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/first-release.svg"><img src="assets/trophies/achievements/first-release-day.svg" alt="First Release: earned, Rare"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-first-tag"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/first-tag.svg"><img src="assets/trophies/achievements/first-tag-day.svg" alt="First Tag: earned, Uncommon"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-stranger-report"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/stranger-report.svg"><img src="assets/trophies/achievements/stranger-report-day.svg" alt="Stranger Report: earned, Uncommon"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-named"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/named.svg"><img src="assets/trophies/achievements/named-day.svg" alt="Named: earned, Common"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-filed"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/filed.svg"><img src="assets/trophies/achievements/filed-day.svg" alt="Filed: 0% (0 of 3)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-first-fork"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/first-fork.svg"><img src="assets/trophies/achievements/first-fork-day.svg" alt="First Fork: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-first-merge"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/first-merge.svg"><img src="assets/trophies/achievements/first-merge-day.svg" alt="First Merge: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-first-star"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/first-star.svg"><img src="assets/trophies/achievements/first-star-day.svg" alt="First Star: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-first-watcher"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/first-watcher.svg"><img src="assets/trophies/achievements/first-watcher-day.svg" alt="First Watcher: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-front-door"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/front-door.svg"><img src="assets/trophies/achievements/front-door-day.svg" alt="Front Door: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-outside-help"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/outside-help.svg"><img src="assets/trophies/achievements/outside-help-day.svg" alt="Outside Help: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-poster"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/poster.svg"><img src="assets/trophies/achievements/poster-day.svg" alt="Poster: 0% (0 of 1)"></picture></a>
</p>

<p align="center"><b>Health</b></p>
<p align="center">
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-gatekeeper"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/gatekeeper.svg"><img src="assets/trophies/achievements/gatekeeper-day.svg" alt="Gatekeeper: earned, Epic"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-locksmith"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/locksmith.svg"><img src="assets/trophies/achievements/locksmith-day.svg" alt="Locksmith: earned, Epic"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-paperwork"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/paperwork.svg"><img src="assets/trophies/achievements/paperwork-day.svg" alt="Paperwork: earned, Epic"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-support-line"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/support-line.svg"><img src="assets/trophies/achievements/support-line-day.svg" alt="Support Line: earned, Epic"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-town-hall"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/town-hall.svg"><img src="assets/trophies/achievements/town-hall-day.svg" alt="Town Hall: earned, Epic"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-auto-pilot"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/auto-pilot.svg"><img src="assets/trophies/achievements/auto-pilot-day.svg" alt="Auto-pilot: earned, Rare"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-form-filler"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/form-filler.svg"><img src="assets/trophies/achievements/form-filler-day.svg" alt="Form Filler: earned, Rare"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-house-rules"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/house-rules.svg"><img src="assets/trophies/achievements/house-rules-day.svg" alt="House Rules: earned, Rare"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-label-maker"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/label-maker.svg"><img src="assets/trophies/achievements/label-maker-day.svg" alt="Label Maker: earned, Rare"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-welcome-mat"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/welcome-mat.svg"><img src="assets/trophies/achievements/welcome-mat-day.svg" alt="Welcome Mat: earned, Rare"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-well-formed"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/well-formed.svg"><img src="assets/trophies/achievements/well-formed-day.svg" alt="Well-Formed: earned, Uncommon"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-clean-bill"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/clean-bill.svg"><img src="assets/trophies/achievements/clean-bill-day.svg" alt="Clean Bill: earned, Common"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-documented"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/documented.svg"><img src="assets/trophies/achievements/documented-day.svg" alt="Documented: earned, Common"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-licensed"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/licensed.svg"><img src="assets/trophies/achievements/licensed-day.svg" alt="Licensed: earned, Common"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-changelog"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/changelog.svg"><img src="assets/trophies/achievements/changelog-day.svg" alt="Changelog: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-open-hand"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/open-hand.svg"><img src="assets/trophies/achievements/open-hand-day.svg" alt="Open Hand: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-protected"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/protected.svg"><img src="assets/trophies/achievements/protected-day.svg" alt="Protected: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-roadmap"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/roadmap.svg"><img src="assets/trophies/achievements/roadmap-day.svg" alt="Roadmap: 0% (0 of 5)"></picture></a>
</p>

<p align="center"><b>Craft</b></p>
<p align="center">
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-follows-the-standards"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/follows-the-standards.svg"><img src="assets/trophies/achievements/follows-the-standards-day.svg" alt="Follows the Standards: earned, Legendary"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-golden-path"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/golden-path.svg"><img src="assets/trophies/achievements/golden-path-day.svg" alt="Golden Path: earned, Legendary"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-ready-room"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/ready-room.svg"><img src="assets/trophies/achievements/ready-room-day.svg" alt="Ready Room: earned, Epic"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-by-the-book"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/by-the-book.svg"><img src="assets/trophies/achievements/by-the-book-day.svg" alt="By the Book I: earned, Rare, 23% to By the Book II"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-green-machine"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/green-machine.svg"><img src="assets/trophies/achievements/green-machine-day.svg" alt="Green Machine I: earned, Rare, 20% to Green Machine II"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-test-suite"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/test-suite.svg"><img src="assets/trophies/achievements/test-suite-day.svg" alt="Test Suite: earned, Uncommon"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-wired"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/wired.svg"><img src="assets/trophies/achievements/wired-day.svg" alt="Wired: earned, Uncommon"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-squeaky"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/squeaky.svg"><img src="assets/trophies/achievements/squeaky-day.svg" alt="Squeaky: earned, Common"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-signed"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/signed.svg"><img src="assets/trophies/achievements/signed-day.svg" alt="Signed: 90% (90 of 100)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-release-notes"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/release-notes.svg"><img src="assets/trophies/achievements/release-notes-day.svg" alt="Release Notes: 20% (2 of 10)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-semver"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/semver.svg"><img src="assets/trophies/achievements/semver-day.svg" alt="Semver: 20% (2 of 10)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-containerized"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/containerized.svg"><img src="assets/trophies/achievements/containerized-day.svg" alt="Containerized: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-gitmoji"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/gitmoji.svg"><img src="assets/trophies/achievements/gitmoji-day.svg" alt="Gitmoji: 0% (0 of 100)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-packager"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/packager.svg"><img src="assets/trophies/achievements/packager-day.svg" alt="Packager: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-prerelease"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/prerelease.svg"><img src="assets/trophies/achievements/prerelease-day.svg" alt="Prerelease: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-small-steps"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/small-steps.svg"><img src="assets/trophies/achievements/small-steps-day.svg" alt="Small Steps: 0% (0 of 1)"></picture></a>
</p>

<p align="center"><b>Community</b></p>
<p align="center">
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-triage"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/triage.svg"><img src="assets/trophies/achievements/triage-day.svg" alt="Triage: earned, Rare"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-crew"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/crew.svg"><img src="assets/trophies/achievements/crew-day.svg" alt="Crew: 20% (1 of 5)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-regulars"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/regulars.svg"><img src="assets/trophies/achievements/regulars-day.svg" alt="Regulars: 20% (1 of 5)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-ten-strong"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/ten-strong.svg"><img src="assets/trophies/achievements/ten-strong-day.svg" alt="Ten Strong: 20% (2 of 10)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-long-thread"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/long-thread.svg"><img src="assets/trophies/achievements/long-thread-day.svg" alt="Long Thread: 5% (5 of 100)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-talkative"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/talkative.svg"><img src="assets/trophies/achievements/talkative-day.svg" alt="Talkative: 0% (9 of 1,000)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-answered"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/answered.svg"><img src="assets/trophies/achievements/answered-day.svg" alt="Answered: 0% (0 of 10)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-fast-reply"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/fast-reply.svg"><img src="assets/trophies/achievements/fast-reply-day.svg" alt="Fast Reply: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-good-first-issues"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/good-first-issues.svg"><img src="assets/trophies/achievements/good-first-issues-day.svg" alt="Good First Issues: 0% (0 of 5)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-help-wanted"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/help-wanted.svg"><img src="assets/trophies/achievements/help-wanted-day.svg" alt="Help Wanted: 0% (0 of 5)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-mentor"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/mentor.svg"><img src="assets/trophies/achievements/mentor-day.svg" alt="Mentor: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-org-backed"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/org-backed.svg"><img src="assets/trophies/achievements/org-backed-day.svg" alt="Org Backed: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-outside-merges"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/outside-merges.svg"><img src="assets/trophies/achievements/outside-merges-day.svg" alt="Outside Merges: 0% (0 of 10)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-popular-opinion"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/popular-opinion.svg"><img src="assets/trophies/achievements/popular-opinion-day.svg" alt="Popular Opinion: 0% (0 of 50)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-reviewed"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/reviewed.svg"><img src="assets/trophies/achievements/reviewed-day.svg" alt="Reviewed: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-well-maintained"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/well-maintained.svg"><img src="assets/trophies/achievements/well-maintained-day.svg" alt="Well Maintained: 0% (0 of 25)"></picture></a>
</p>

<p align="center"><b>Reach</b></p>
<p align="center">
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-big-name"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/big-name.svg"><img src="assets/trophies/achievements/big-name-day.svg" alt="Big Name: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-cloned"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/cloned.svg"><img src="assets/trophies/achievements/cloned-day.svg" alt="Cloned: not measured yet"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-downloaded"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/downloaded.svg"><img src="assets/trophies/achievements/downloaded-day.svg" alt="Downloaded: 0% (0 of 1,000)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-fork-magnet"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/fork-magnet.svg"><img src="assets/trophies/achievements/fork-magnet-day.svg" alt="Fork Magnet: 0% (0 of 10)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-forked-far"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/forked-far.svg"><img src="assets/trophies/achievements/forked-far-day.svg" alt="Forked Far: 0% (0 of 100)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-living-forks"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/living-forks.svg"><img src="assets/trophies/achievements/living-forks-day.svg" alt="Living Forks: 0% (0 of 10)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-referred"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/referred.svg"><img src="assets/trophies/achievements/referred-day.svg" alt="Referred: not measured yet"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-registry"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/registry.svg"><img src="assets/trophies/achievements/registry-day.svg" alt="Registry: not measured yet"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-star-of-the-week"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/star-of-the-week.svg"><img src="assets/trophies/achievements/star-of-the-week-day.svg" alt="Star of the Week: 0% (0 of 50)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-stargazer-streak"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/stargazer-streak.svg"><img src="assets/trophies/achievements/stargazer-streak-day.svg" alt="Stargazer Streak: 0% (0 of 12)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-trending"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/trending.svg"><img src="assets/trophies/achievements/trending-day.svg" alt="Trending: 0% (0 of 100)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-used-by"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/used-by.svg"><img src="assets/trophies/achievements/used-by-day.svg" alt="Used By: not measured yet"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-visited"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/visited.svg"><img src="assets/trophies/achievements/visited-day.svg" alt="Visited: not measured yet"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-watched"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/watched.svg"><img src="assets/trophies/achievements/watched-day.svg" alt="Watched: 0% (0 of 25)"></picture></a>
</p>

<p align="center"><b>Rhythm</b></p>
<p align="center">
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-alive"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/alive.svg"><img src="assets/trophies/achievements/alive-day.svg" alt="Alive: earned, Uncommon"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-same-day-fix"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/same-day-fix.svg"><img src="assets/trophies/achievements/same-day-fix-day.svg" alt="Same-Day Fix: 40% (4 of 10)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-night-shift"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/night-shift.svg"><img src="assets/trophies/achievements/night-shift-day.svg" alt="Night Shift: 38% (19 of 50)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-long-game"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/long-game.svg"><img src="assets/trophies/achievements/long-game-day.svg" alt="Long Game: 33% (1 of 3)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-streak"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/streak.svg"><img src="assets/trophies/achievements/streak-day.svg" alt="Streak: 20% (6 of 30)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-monthly-release"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/monthly-release.svg"><img src="assets/trophies/achievements/monthly-release-day.svg" alt="Monthly Release: 8% (1 of 12)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-big-week"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/big-week.svg"><img src="assets/trophies/achievements/big-week-day.svg" alt="Big Week: 4% (4 of 100)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-weekend-project"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/weekend-project.svg"><img src="assets/trophies/achievements/weekend-project-day.svg" alt="Weekend Project: 3% (1 of 26)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-weekly-beat"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/weekly-beat.svg"><img src="assets/trophies/achievements/weekly-beat-day.svg" alt="Weekly Beat: 3% (2 of 52)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-marathon-day"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/marathon-day.svg"><img src="assets/trophies/achievements/marathon-day-day.svg" alt="Marathon Day: 2% (1 of 50)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-comeback"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/comeback.svg"><img src="assets/trophies/achievements/comeback-day.svg" alt="Comeback: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-friday-deploy"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/friday-deploy.svg"><img src="assets/trophies/achievements/friday-deploy-day.svg" alt="Friday Deploy: 0% (0 of 1)"></picture></a>
</p>

<p align="center"><b>Secret</b></p>
<p align="center">
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-birthday"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/birthday.svg"><img src="assets/trophies/achievements/birthday-day.svg" alt="Secret achievement"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-constellation"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/constellation.svg"><img src="assets/trophies/achievements/constellation-day.svg" alt="Secret achievement"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-friday-the-13th"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/friday-the-13th.svg"><img src="assets/trophies/achievements/friday-the-13th-day.svg" alt="Secret achievement"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-full-house"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/full-house.svg"><img src="assets/trophies/achievements/full-house-day.svg" alt="Secret achievement"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-ghost"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/ghost.svg"><img src="assets/trophies/achievements/ghost-day.svg" alt="Secret achievement"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-green-wall"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/green-wall.svg"><img src="assets/trophies/achievements/green-wall-day.svg" alt="Secret achievement"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-leap-day"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/leap-day.svg"><img src="assets/trophies/achievements/leap-day-day.svg" alt="Secret achievement"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-midnight-oil"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/midnight-oil.svg"><img src="assets/trophies/achievements/midnight-oil-day.svg" alt="Secret achievement"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-new-year"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/new-year.svg"><img src="assets/trophies/achievements/new-year-day.svg" alt="Secret achievement"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-palindrome"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/palindrome.svg"><img src="assets/trophies/achievements/palindrome-day.svg" alt="Secret achievement"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-round-number"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/round-number.svg"><img src="assets/trophies/achievements/round-number-day.svg" alt="Secret achievement"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-the-answer"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/the-answer.svg"><img src="assets/trophies/achievements/the-answer-day.svg" alt="Secret achievement"></picture></a>
</p>

</details>

<p align="center"><sub>Refreshed daily by <a href="https://github.com/tannergolden/markdown">tannergolden/markdown</a> · Every trophy and achievement, what it is for and how to earn it: <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository">the catalogue</a>. Click any card for its entry.</sub></p>
<!-- markdown:trophies:end -->

<!-- markdown:footer:start -->
<div align="center">

<a href="#top">
<picture>
  <source media="(max-width: 585px) and (prefers-color-scheme: dark)" srcset="assets/banners/footer-narrow-dark.svg">
  <source media="(max-width: 585px)" srcset="assets/banners/footer-narrow-day.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/banners/footer-dark.svg">
  <img alt="Drawn at both ends. Fetched at neither. Back to Top. Built with love by @tannergolden. Last updated October 15, 2026." src="assets/banners/footer-day.svg">
</picture>
</a>

<a href="https://github.com/tannergolden/markdown/issues"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/banners/link-issues-dark.svg"><img alt="Issues" src="assets/banners/link-issues-day.svg"></picture></a>
<a href="https://github.com/tannergolden/markdown/pulls"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/banners/link-pull-requests-dark.svg"><img alt="Pull Requests" src="assets/banners/link-pull-requests-day.svg"></picture></a>
<a href="https://github.com/tannergolden/markdown/releases"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/banners/link-releases-dark.svg"><img alt="Releases" src="assets/banners/link-releases-day.svg"></picture></a>
<a href="https://github.com/tannergolden/markdown/actions"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/banners/link-actions-dark.svg"><img alt="Actions" src="assets/banners/link-actions-day.svg"></picture></a>

</div>
<!-- markdown:footer:end -->
