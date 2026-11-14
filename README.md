<!--
title: '📝 MARKDOWN'
description: 'A README''s header, footer, badges, body and trophy case, measured on a schedule and drawn as committed SVGs from one stub.'
type: index
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
  <img alt="markdown: Automated SVG generator for README headers, badges, trophies, and footers, rendered locally from a single stub to bypass API rate limits. Measured nightly, never fetched. Project: tannergolden/markdown. Release: v1.17.0. Stars: 0. Forks: 0. Open issues: 0. Language: Python." src="assets/banners/header-day.svg">
</picture>

</div>
<!-- markdown:header:end -->

<!-- markdown:badges:start -->
<div align="center">

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/badges/static/status-dark.svg"><img alt="Status: Active" src="assets/badges/static/status.svg"></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="assets/badges/static/python-dark.svg"><img alt="Python: Standard library only" src="assets/badges/static/python.svg"></picture>
<a href="LICENSE"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/badges/static/license-dark.svg"><img alt="License: MIT, games proprietary" src="assets/badges/static/license.svg"></picture></a>

<img alt="CI: Passing" src="assets/badges/dynamic/ci.svg">
<img alt="Release: v1.17.0" src="assets/badges/dynamic/release.svg">
<img alt="Last Commit: This Week" src="assets/badges/dynamic/last-commit.svg">

</div>
<!-- markdown:badges:end -->

> [!TIP]
> **This page is the kit drawing itself.** Its header, the badge row, the
> schematic, the trophy case and the footer are files the kit drew, in the
> `blueprint`, from the [same stub](#-one-stub) it asks you to copy. **To see
> profile mode, check out my profile, [@tannergolden](https://github.com/tannergolden).**

---

## 💡 What It Is

A README's images usually come from someone else's server, one request on
every page view, and a header typed by hand is out of date the day your
description changes. This kit draws them instead, and keeps them current: one
scheduled run measures the page over GitHub's API and git, draws every image
as an SVG, writes the README's blocks, and commits the lot once.

| Part         | What it draws                                                                           |
| :----------- | :-------------------------------------------------------------------------------------- |
| **Banners**  | The header and the footer, and the links under the footer.                              |
| **Badges**   | A row of static badges, and a row of live ones whose value and colour the run measures. |
| **Elements** | The body: a schematic, instruments, milestones, a roster, a certificate, placards.      |
| **Trophies** | The trophy case: eight core trophies with their tiers, and a hundred achievements.      |

Every image is a **committed file**, served by GitHub with the rest of the
repository, so nothing rate-limits it and no third party sits in the path. A
page is a person's profile or a repository.

- **Status**: Active, on the `v1` line.

---

## 🚀 Quick Start

### 📄 One Stub

Your repository holds one small workflow that names the schedule. The
checkout, the measurement, the drawing and the commit all happen here, so a fix
lands once and reaches every README pinned to `v1`.

<details>
<summary>The whole stub, <code>.github/workflows/markdown.yml</code></summary>

```yaml
# .github/workflows/markdown.yml
name: '📝 Markdown'

on:
  schedule:
    - cron: '0 0 * * *' # every night at midnight UTC
  workflow_dispatch:

concurrency: # one drawing at a time; the next waits its turn
  group: markdown-${{ github.ref }}
  cancel-in-progress: false

permissions: {}

jobs:
  markdown:
    permissions:
      contents: write # the images, the README's blocks and the lock
      pull-requests: write # only used with commit: pr
    uses: tannergolden/markdown/.github/workflows/markdown.yml@v1
    secrets:
      MARKDOWN_TOKEN: ${{ secrets.MARKDOWN_TOKEN }} # the one secret the kit reads
```

</details>

With no settings at all, the page gets a header and a footer read from GitHub
and a trophy case, in the `standard` theme. The stub sets the choices made
most often, such as `mode` (`profile` or `repository`), `theme`, `holidays`,
`check` and `commit` (`push`, or `pr` for a pull request); everything else
lives in `.github/markdown.yaml`, and
[`docs/references/Settings.md`](docs/references/Settings.md) has every key.
`MARKDOWN_TOKEN` is optional: `GITHUB_TOKEN` reads everything public.

---

## 📖 Using It

### 🧭 How A Run Draws A Page

<!-- markdown:element:how-it-runs:start -->
<picture>
  <source media="(max-width: 585px) and (prefers-color-scheme: dark)" srcset="assets/elements/how-it-runs-narrow-dark.svg">
  <source media="(max-width: 585px)" srcset="assets/elements/how-it-runs-narrow-day.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/elements/how-it-runs-dark.svg">
  <img alt="How a run draws a page. A repository&#x27;s stub calls the kit&#x27;s workflow, which reads the settings, measures the page over GitHub&#x27;s API and git, draws every file, keeps what it measured in the lock, and commits the page once." src="assets/elements/how-it-runs-day.svg">
</picture>
<!-- markdown:element:how-it-runs:end -->

Each run measures everything again, so a run GitHub delays or drops loses
nothing, and a day on which nothing moved writes nothing. The kit owns only
what sits between its markers in the README, so every word of yours around
them stays yours. On a first run the header goes at the top, the badges under
it, the trophy case over the footer and the footer at the foot; an element
goes where you put its markers.

### 🎨 One Theme For The Whole Page

One setting colours everything, so the header, the badges, the body and the
trophy case read as one family: `standard`, the default; eleven prints, from
`redprint` to `blackprint`, and `rainbowprint`; your own prints; pixel themes
such as `heaven-and-hell` and `brain`; and collections such as `medieval` and
`matrix`, a design for each month. Around each holiday its set takes the page
for a few days, and on the page's birthday the Birthday set does.
[Themes and Sets](docs/technical/Themes.md) defines each kind, and
`markdown-kit themes` lists every theme a page can pick.

<table>
  <tr>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html#standard"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/references/themes/standard/h2-still-dark.svg"><img src="docs/references/themes/standard/h2-still-day.svg" alt="The H2 header in standard, the default theme" width="100%"></picture></a>
      <br /><sub><code>standard</code>, the default</sub>
    </td>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html#blueprint"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/references/themes/blueprint/h2-still-dark.svg"><img src="docs/references/themes/blueprint/h2-still-day.svg" alt="The H2 header in blueprint, this page's print" width="100%"></picture></a>
      <br /><sub><code>blueprint</code>, this page's print</sub>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html#halloween"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/references/themes/halloween/h2-still-dark.svg"><img src="docs/references/themes/halloween/h2-still-day.svg" alt="The H2 header in Halloween's set" width="100%"></picture></a>
      <br /><sub>Halloween's set, October 30 to November 1</sub>
    </td>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html#christmas"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/references/themes/christmas/h2-still-dark.svg"><img src="docs/references/themes/christmas/h2-still-day.svg" alt="The H2 header in Christmas's set" width="100%"></picture></a>
      <br /><sub>Christmas's set, December 24 to 26</sub>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html#heaven-and-hell"><img src="docs/references/themes/heaven-and-hell/h2-still-day.svg" alt="The H2 header in Heaven &amp; Hell by day: the archangel keeping vigil before the glory of heaven" width="100%"></a>
      <br /><sub><code>heaven-and-hell</code> in light mode</sub>
    </td>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html#heaven-and-hell"><img src="docs/references/themes/heaven-and-hell/h2-still-dark.svg" alt="The H2 header in Heaven &amp; Hell by night: the demon before a wall of fire" width="100%"></a>
      <br /><sub><code>heaven-and-hell</code> in dark mode</sub>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html#brain"><img src="docs/references/themes/brain/h2-still-day.svg" alt="The H2 header in brain by day: the brain in its jar in the lit lab, a Tesla coil beside it" width="100%"></a>
      <br /><sub><code>brain</code> in light mode</sub>
    </td>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html#brain"><img src="docs/references/themes/brain/h2-still-dark.svg" alt="The H2 header in brain by night: the jar glowing in the dark lab, lightning off the coil" width="100%"></a>
      <br /><sub><code>brain</code> in dark mode</sub>
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="25%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html#standard"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/references/themes/standard/trophy-trophy-3-dark.svg"><img src="docs/references/themes/standard/trophy-trophy-3-day.svg" alt="A gold trophy card in standard, the default theme" width="100%"></picture></a>
      <br /><sub><code>standard</code></sub>
    </td>
    <td width="25%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html#blueprint"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/references/themes/blueprint/trophy-trophy-3-dark.svg"><img src="docs/references/themes/blueprint/trophy-trophy-3-day.svg" alt="A gold trophy card in blueprint, drawn on its drafting paper" width="100%"></picture></a>
      <br /><sub><code>blueprint</code></sub>
    </td>
    <td width="25%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html#halloween"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/references/themes/halloween/trophy-trophy-3-dark.svg"><img src="docs/references/themes/halloween/trophy-trophy-3-day.svg" alt="A gold trophy card in Halloween's set, in pixels" width="100%"></picture></a>
      <br /><sub>Halloween's set</sub>
    </td>
    <td width="25%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/medieval/index.html"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/references/themes/medieval/medieval-forge/trophy-trophy-3-dark.svg"><img src="docs/references/themes/medieval/medieval-forge/trophy-trophy-3-day.svg" alt="A gold trophy card in Forge, the medieval collection's November design" width="100%"></picture></a>
      <br /><sub><code>medieval</code> in November</sub>
    </td>
  </tr>
</table>

**[See every theme, drawn by the kit](https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html)**,
on GitHub's light and dark grounds, at the size a README shows them.

### ♟️ The Games On @tannergolden's Profile

The kit also draws four games, Chess, Checkers, Pentago and Tic-Tac, for one
page alone: [@tannergolden's profile](https://github.com/tannergolden), where
anyone on GitHub can play the next move through
[tannergolden/play](https://github.com/tannergolden/play). Any other page whose
settings name them is told so. Their designs are proprietary, under
[`LICENSE-GAMES`](LICENSE-GAMES).

<table>
  <tr>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html#chess"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/references/themes/chess/chess-wide-blackprint-still-dark.svg"><img src="docs/references/themes/chess/chess-wide-blackprint-still-day.svg" alt="The chess board in blackprint, from a sample game" width="100%"></picture></a>
      <br /><sub>Chess, in <code>blackprint</code></sub>
    </td>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html#checkers"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/references/themes/checkers/checkers-wide-blackprint-still-dark.svg"><img src="docs/references/themes/checkers/checkers-wide-blackprint-still-day.svg" alt="The Checkers board in blackprint, from a sample game" width="100%"></picture></a>
      <br /><sub>Checkers, in <code>blackprint</code></sub>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html#pentago"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/references/themes/pentago/pentago-wide-blackprint-still-dark.svg"><img src="docs/references/themes/pentago/pentago-wide-blackprint-still-day.svg" alt="The Pentago board in blackprint, from a sample game under the Ghost Rule" width="100%"></picture></a>
      <br /><sub>Pentago, in <code>blackprint</code></sub>
    </td>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html#tictac"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/references/themes/tictac/tictac-wide-blackprint-still-dark.svg"><img src="docs/references/themes/tictac/tictac-wide-blackprint-still-day.svg" alt="The Tic-Tac board in blackprint, from a sample game under the Ghost Rule" width="100%"></picture></a>
      <br /><sub>Tic-Tac, in <code>blackprint</code></sub>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html#chess"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/references/themes/chess/chess-wide-standard-still-dark.svg"><img src="docs/references/themes/chess/chess-wide-standard-still-day.svg" alt="The chess board in standard, from a sample game" width="100%"></picture></a>
      <br /><sub>Chess, in <code>standard</code></sub>
    </td>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html#checkers"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/references/themes/checkers/checkers-wide-standard-still-dark.svg"><img src="docs/references/themes/checkers/checkers-wide-standard-still-day.svg" alt="The Checkers board in standard, from a sample game" width="100%"></picture></a>
      <br /><sub>Checkers, in <code>standard</code></sub>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html#pentago"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/references/themes/pentago/pentago-wide-standard-still-dark.svg"><img src="docs/references/themes/pentago/pentago-wide-standard-still-day.svg" alt="The Pentago board in standard, from a sample game under the Ghost Rule" width="100%"></picture></a>
      <br /><sub>Pentago, in <code>standard</code></sub>
    </td>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html#tictac"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/references/themes/tictac/tictac-wide-standard-still-dark.svg"><img src="docs/references/themes/tictac/tictac-wide-standard-still-day.svg" alt="The Tic-Tac board in standard, from a sample game under the Ghost Rule" width="100%"></picture></a>
      <br /><sub>Tic-Tac, in <code>standard</code></sub>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html#hall-of-fame"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/references/themes/hall-of-fame/hall-of-fame-wide-blackprint-still-dark.svg"><img src="docs/references/themes/hall-of-fame/hall-of-fame-wide-blackprint-still-day.svg" alt="The Hall of Fame of all four games in blackprint, from a sample of fictional winners" width="100%"></picture></a>
      <br /><sub>The Hall of Fame, in <code>blackprint</code></sub>
    </td>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html#hall-of-fame"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/references/themes/hall-of-fame/hall-of-fame-wide-standard-still-dark.svg"><img src="docs/references/themes/hall-of-fame/hall-of-fame-wide-standard-still-day.svg" alt="The Hall of Fame of all four games in standard, from a sample of fictional winners" width="100%"></picture></a>
      <br /><sub>The Hall of Fame, in <code>standard</code></sub>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html#chess"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/references/themes/chess/chess-wide-halloween-still-dark.svg"><img src="docs/references/themes/chess/chess-wide-halloween-still-day.svg" alt="The chess board in the Halloween set's pixels, from a sample game" width="100%"></picture></a>
      <br /><sub>Chess, in the <code>halloween</code> set</sub>
    </td>
    <td width="50%" align="center">
      <a href="https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html#hall-of-fame"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/references/themes/hall-of-fame/hall-of-fame-wide-medieval-hoard-still-dark.svg"><img src="docs/references/themes/hall-of-fame/hall-of-fame-wide-medieval-hoard-still-day.svg" alt="The Hall of Fame of all four games in the Hoard, December's design of the Medieval collection, from a sample of fictional winners" width="100%"></picture></a>
      <br /><sub>The Hall of Fame, in <code>medieval-hoard</code>, December's design</sub>
    </td>
  </tr>
</table>

### 🔍 Checking A Page

The lock, `.github/markdown.lock.json`, keeps what each run measured, so the
committed page can be drawn again with no token and no network and compared
with what is committed. For pull-request CI:

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

### 🖥️ On Your Own Machine

The kit is standard-library Python, 3.10 or later, with nothing to install:

```bash
python3 src/markdown-kit.py preview --root /tmp/page       # a sample page, the way a run draws it
python3 src/markdown-kit.py check --root .                 # is the committed page current?
python3 src/markdown-kit.py themes                         # every theme a page can pick, by kind
```

`python3 src/markdown-kit.py --help` lists the rest, and `make lint test` runs
everything CI runs. [`.github/workflows/README.md`](.github/workflows/README.md)
logs every workflow here.

---

## 📦 What's Inside

| Path                             | Purpose                                                                                                                            |
| :------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------- |
| `.github/workflows/markdown.yml` | **The workflow** every stub calls: checkout, the kit, the commit                                                                   |
| `.github/actions/markdown/`      | **The action** the workflow runs: one run of the kit on the checkout                                                               |
| `src/markdown-kit.py`            | **The kit's** command line, and the one place its layers meet                                                                      |
| `src/domain/`                    | What a page looks like: the palette, the lettering, the themes and every drawing                                                   |
| `src/app/`                       | What a run does: the settings, the measurement, the plan and the commit                                                            |
| `src/infra/`                     | Files, git, GitHub's API, the clock, and the kit's data files                                                                      |
| `docs/`                          | [Settings](docs/references/Settings.md), the trophies' [catalogue](docs/references/Catalogue.md), and the decisions behind the kit |
| `docs/references/themes/`        | The theme-sets page: every theme as the kit draws it, from `make themes`                                                           |
| `tests/`                         | Unit, integration and end-to-end suites, and the fixtures they check against                                                       |

---

## 🤝 Getting Involved

- **Questions**: [`SUPPORT.md`](/.github/SUPPORT.md) says where to ask.
- **A bug or an idea**: open an issue from one of the forms.
- **A change**: [`CONTRIBUTING.md`](/.github/CONTRIBUTING.md) explains how,
  every change follows the
  [standards](https://github.com/tannergolden/standards/blob/Development/docs/README.md)
  by link, and every contribution follows the
  [code of conduct](/.github/CODE_OF_CONDUCT.md).
- **Who decides**: [`GOVERNANCE.md`](/.github/GOVERNANCE.md) names the
  maintainers.

---

## 🛡️ Security

Report a vulnerability privately, never in an issue:
[`SECURITY.md`](/.github/SECURITY.md) says how, and how fast a fix follows.

---

## ⚖️ Licence

The kit is released under the terms in [LICENSE](/LICENSE). The games'
materials are not: they are proprietary, under [`LICENSE-GAMES`](LICENSE-GAMES).

---

<!-- markdown:trophies:start -->
<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/level.svg"><img src="assets/trophies/level-day.svg" alt="tannergolden/markdown: level 21, 7,398 XP, case 29% complete, released 1 days ago"></picture>
  <picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/next-up.svg"><img src="assets/trophies/next-up-day.svg" alt="Next up: Issues Resolved to Bronze 60%, Same-Day Fix 60%, Night Shift 38%"></picture>
</p>

<p align="center">
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-stars"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/stars.svg"><img src="assets/trophies/stars-day.svg" alt="Stars trophy: Unranked, 0, 0% to Bronze"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-forks"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/forks.svg"><img src="assets/trophies/forks-day.svg" alt="Forks trophy: Unranked, 0, 0% to Bronze"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-contributors"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/contributors.svg"><img src="assets/trophies/contributors-day.svg" alt="Contributors trophy: Bronze, 2, 0% to Silver, top 43%, up 1 this week, newly reached"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-commits"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/commits.svg"><img src="assets/trophies/commits-day.svg" alt="Commits trophy: Bronze, 130, 7% to Silver, top 5.5%, up 125 this week"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-releases"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/releases.svg"><img src="assets/trophies/releases-day.svg" alt="Releases trophy: Bronze, 2, 25% to Silver, top 7.3%, up 1 this week"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-merged"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/merged.svg"><img src="assets/trophies/merged-day.svg" alt="Merged PRs trophy: Unranked, 0, 0% to Bronze"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-resolved"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/resolved.svg"><img src="assets/trophies/resolved-day.svg" alt="Issues Resolved trophy: Unranked, 6, 60% to Bronze, up 6 this week"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-active"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/active.svg"><img src="assets/trophies/active-day.svg" alt="Active Days trophy: Unranked, 7 days, 23% to Bronze, up 6 this week"></picture></a>
</p>

<details>
<summary><b>Achievements</b> · 30 of 100 earned · next: Issues Resolved to Bronze, 60%</summary>

<p align="center"><b>Launch</b></p>
<p align="center">
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-first-release"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/first-release.svg"><img src="assets/trophies/achievements/first-release-day.svg" alt="First Release: earned, Rare"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-filed"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/filed.svg"><img src="assets/trophies/achievements/filed-day.svg" alt="Filed: earned, Uncommon"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-first-tag"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/first-tag.svg"><img src="assets/trophies/achievements/first-tag-day.svg" alt="First Tag: earned, Uncommon"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-stranger-report"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/stranger-report.svg"><img src="assets/trophies/achievements/stranger-report-day.svg" alt="Stranger Report: earned, Uncommon"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-named"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/named.svg"><img src="assets/trophies/achievements/named-day.svg" alt="Named: earned, Common"></picture></a>
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
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-by-the-book"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/by-the-book.svg"><img src="assets/trophies/achievements/by-the-book-day.svg" alt="By the Book I: earned, Rare, 26% to By the Book II"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-green-machine"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/green-machine.svg"><img src="assets/trophies/achievements/green-machine-day.svg" alt="Green Machine I: earned, Rare, 25% to Green Machine II"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-signed"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/signed.svg"><img src="assets/trophies/achievements/signed-day.svg" alt="Signed I: earned, Rare, 10% to Signed II"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-test-suite"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/test-suite.svg"><img src="assets/trophies/achievements/test-suite-day.svg" alt="Test Suite: earned, Uncommon"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-wired"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/wired.svg"><img src="assets/trophies/achievements/wired-day.svg" alt="Wired: earned, Uncommon"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-squeaky"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/squeaky.svg"><img src="assets/trophies/achievements/squeaky-day.svg" alt="Squeaky: earned, Common"></picture></a>
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
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-talkative"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/talkative.svg"><img src="assets/trophies/achievements/talkative-day.svg" alt="Talkative: 1% (12 of 1,000)"></picture></a>
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
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-same-day-fix"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/same-day-fix.svg"><img src="assets/trophies/achievements/same-day-fix-day.svg" alt="Same-Day Fix: 60% (6 of 10)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-night-shift"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/night-shift.svg"><img src="assets/trophies/achievements/night-shift-day.svg" alt="Night Shift: 38% (19 of 50)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-long-game"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/long-game.svg"><img src="assets/trophies/achievements/long-game-day.svg" alt="Long Game: 33% (1 of 3)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-streak"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/streak.svg"><img src="assets/trophies/achievements/streak-day.svg" alt="Streak: 20% (6 of 30)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-monthly-release"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/monthly-release.svg"><img src="assets/trophies/achievements/monthly-release-day.svg" alt="Monthly Release: 8% (1 of 12)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-weekend-project"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/weekend-project.svg"><img src="assets/trophies/achievements/weekend-project-day.svg" alt="Weekend Project: 7% (2 of 26)"></picture></a>
  <a href="https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md#repository-big-week"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/big-week.svg"><img src="assets/trophies/achievements/big-week-day.svg" alt="Big Week: 5% (5 of 100)"></picture></a>
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
  <img alt="Drawn at both ends. Fetched at neither. Back to Top. Built with love by @tannergolden. Last updated October 17, 2026." src="assets/banners/footer-day.svg">
</picture>
</a>

<a href="https://github.com/tannergolden/markdown/issues"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/banners/link-issues-dark.svg"><img alt="Issues" src="assets/banners/link-issues-day.svg"></picture></a>
<a href="https://github.com/tannergolden/markdown/pulls"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/banners/link-pull-requests-dark.svg"><img alt="Pull Requests" src="assets/banners/link-pull-requests-day.svg"></picture></a>
<a href="https://github.com/tannergolden/markdown/releases"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/banners/link-releases-dark.svg"><img alt="Releases" src="assets/banners/link-releases-day.svg"></picture></a>
<a href="https://github.com/tannergolden/markdown/actions"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/banners/link-actions-dark.svg"><img alt="Actions" src="assets/banners/link-actions-day.svg"></picture></a>

</div>
<!-- markdown:footer:end -->
