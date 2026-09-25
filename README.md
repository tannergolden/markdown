<!--
title: '📖 MARKDOWN'
description: 'One stub that keeps a README drawn: banners, badges, trophies and elements, each measured from the repository at its own hour and committed only when something moved.'
tags: [readme, readme-header, readme-badges, readme-trophies, github-actions, reusable-workflow, svg, blueprint]
category: docs
-->

<!-- banners:header:start -->
<!-- markdownlint-disable MD041 -->

<div align="center">

<a name="top"></a>

<picture>
  <source media="(max-width: 585px) and (prefers-color-scheme: dark)" srcset="assets/banners/header-narrow-dark.svg">
  <source media="(max-width: 585px)" srcset="assets/banners/header-narrow-day.svg">
  <source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" srcset="assets/banners/header-still-dark.svg">
  <source media="(prefers-reduced-motion: reduce)" srcset="assets/banners/header-still-day.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/banners/header-dark.svg">
  <img alt="markdown: One stub that keeps a README drawn: banners, badges, trophies and elements, each measured from the repository at its own hour and committed only when…. One stub. The whole page. Project: tannergolden/markdown. Release: v1.0.1. Stars: 0. Forks: 0. Open issues: 1. License: MIT." src="assets/banners/header-day.svg">
</picture>

</div>
<!-- banners:header:end -->

<div align="center">

<a href="./"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/badges/static/status-dark.svg"><img alt="Status: Active" src="assets/badges/static/status.svg"></picture></a>
<a href="./"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/badges/static/role-dark.svg"><img alt="Role: Workflow" src="assets/badges/static/role.svg"></picture></a>
<a href="./"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/badges/static/context-dark.svg"><img alt="Context: README" src="assets/badges/static/context.svg"></picture></a>
<a href="./LICENSE"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/badges/static/license-dark.svg"><img alt="License: MIT" src="assets/badges/static/license.svg"></picture></a>

<a href="#-the-kits"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/badges/static/kits-dark.svg"><img alt="Kits: 4" src="assets/badges/static/kits.svg"></picture></a>
<a href="#-one-stub-three-slots"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/badges/static/slots-dark.svg"><img alt="Slots: 3 a day" src="assets/badges/static/slots.svg"></picture></a>
<a href="#-one-stub-three-slots"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/badges/static/apart-dark.svg"><img alt="Commits: 8 hours apart" src="assets/badges/static/apart.svg"></picture></a>

</div>

---

## 💡 What This Is

Four kits each keep one part of a README current, and each has a stub of
its own. This repository holds the **one workflow that calls all of them**,
so a repository adds a single stub, names an hour for each generator, and
gets a page that measures itself and commits what changed. Nothing here
draws anything: each kit stays in its own repository, on its own release
line, and is called by link.

| Kit          | Draws                                                                                                          | Lives in                                                                                     | Slot                |
| :----------- | :------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------- | :------------------ |
| **banners**  | The header at the top of the page and the footer at its foot, from what GitHub knows about the repository      | [`tannergolden/banners`](https://github.com/tannergolden/banners)                            | 00:07               |
| **elements** | The body of the page: a schematic, instruments, a floor plan, milestones, a roster, a certificate, placards, a seal | [`tannergolden/banners`](https://github.com/tannergolden/banners), beside the banners    | 00:07, after them   |
| **badges**   | The badges under the header, from one data file, in six styles and their blueprint twins                        | [`tannergolden/badges`](https://github.com/tannergolden/badges)                              | 08:07               |
| **trophies** | The case: the trophies and achievements the repository has earned                                               | [`tannergolden/trophies`](https://github.com/tannergolden/trophies)                          | 16:07               |

Every one of them draws **committed SVGs** on the same drafting paper, in the
same eleven prints, lettered with the same outlines, so a page drawn by all
four reads as one set of engineering drawings. No request at view time,
nothing to rate-limit, and nothing to keep in step by hand.

**Called, never copied.** Your repository holds a stub that names three
crons. This workflow runs the right kit when each fires, and each kit does
its measuring, drawing and committing in its own repository, so a fix to any
of them lands once and reaches every README pinned to `v1`. That is the
rule every one of these repositories follows, published in
[`tannergolden/standards`](https://github.com/tannergolden/standards).

---

## 🕗 One Stub, Three Slots

There are three generator repositories, so there are three slots in a day,
**eight hours apart**: the banners and the elements at seven minutes past
midnight, the badges at seven past eight, the trophies at seven past four.
A repository is committed to at most once in each slot, and a slot in which
nothing that kit shows has moved commits nothing at all. A manual run, from
the Actions tab, draws everything, one kit after another, so no two ever
push at once.

The stub says each cron twice: once under `on.schedule`, so GitHub fires
it, and once under `with:`, so the workflow knows which kit it means. On a
schedule the workflow reads which cron fired and runs that kit alone; on any
other event it runs every kit the stub names. A cron that fires and names no
kit fails loudly rather than drawing the wrong thing.

<!-- elements:how-it-runs:start -->
<picture>
  <source media="(max-width: 585px) and (prefers-color-scheme: dark)" srcset="assets/elements/how-it-runs-narrow-dark.svg">
  <source media="(max-width: 585px)" srcset="assets/elements/how-it-runs-narrow-day.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/elements/how-it-runs-dark.svg">
  <img alt="A day in the life of one stub. A stub in your repository calls this workflow at three crons, eight hours apart. At seven past midnight it draws the banners, then the elements; at seven past eight, the badges; at seven past four, the trophies. Each kit commits between its own markers, and a quiet slot commits nothing." src="assets/elements/how-it-runs-day.svg">
</picture>
<!-- elements:how-it-runs:end -->

---

## 🖼️ This Page, Drawn By Itself

The header at the top of this page and the footer at its foot are the
banners; the badges under the header are the badges; the rest of this
chapter is the elements and the trophies. All of it is drawn for this
repository by [`📖 Own README`](.github/workflows/own-readme.yml), which
calls the same workflow you would, at the same three crons. Nothing on this
page is fetched from anywhere.

### The body

The elements read this repository's git history in the banners slot: commits
per week and the days since the last release, the tree as a floor plan, the
releases on a time line, who drew it, and the checks it passes. Only the two
notes on the plan and the words on the certificate's ring are written by
hand, in [`.github/elements.yml`](.github/elements.yml).

<!-- elements:vitals:start -->
<picture>
  <source media="(max-width: 585px) and (prefers-color-scheme: dark)" srcset="assets/elements/vitals-narrow-dark.svg">
  <source media="(max-width: 585px)" srcset="assets/elements/vitals-narrow-day.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/elements/vitals-dark.svg">
  <img alt="Instruments for tannergolden/markdown. Commits per week, days since the last release, tracked bytes by file type and counts for tannergolden/markdown." src="assets/elements/vitals-day.svg">
</picture>
<!-- elements:vitals:end -->

<!-- elements:layout:start -->
<picture>
  <source media="(max-width: 585px) and (prefers-color-scheme: dark)" srcset="assets/elements/layout-narrow-dark.svg">
  <source media="(max-width: 585px)" srcset="assets/elements/layout-narrow-day.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/elements/layout-dark.svg">
  <img alt="Plan of tannergolden/markdown. tannergolden/markdown as a floor plan: 61 tracked files in 1 rooms and a lobby." src="assets/elements/layout-day.svg">
</picture>
<!-- elements:layout:end -->

<!-- elements:history:start -->
<picture>
  <source media="(max-width: 585px) and (prefers-color-scheme: dark)" srcset="assets/elements/history-narrow-dark.svg">
  <source media="(max-width: 585px)" srcset="assets/elements/history-narrow-day.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/elements/history-dark.svg">
  <img alt="Milestones of tannergolden/markdown. 0 releases of tannergolden/markdown on a time line." src="assets/elements/history-day.svg">
</picture>
<!-- elements:history:end -->

<div align="center">

<!-- elements:contributors:start -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/elements/contributors-dark.svg">
  <img alt="Contributors to tannergolden/markdown. TANNER GOLDEN: 1 commits." src="assets/elements/contributors-day.svg">
</picture>
<!-- elements:contributors:end -->
<!-- elements:conformance:start -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/elements/conformance-dark.svg">
  <img alt="Conformance of tannergolden/markdown. 4 checks on tannergolden/markdown, with the evidence for each; not met: Security policy." src="assets/elements/conformance-day.svg">
</picture>
<!-- elements:conformance:end -->

</div>

### The case

The trophies read this repository in the trophies slot: stars from other
people, forks, contributors, commits, releases, merged pull requests, issues
resolved and active days, with a hundred achievements behind them. A new
repository starts with an empty case, which is the honest one.

<!-- trophies:start -->
<!-- trophies:end -->

---

## 🚀 Use It In Your README

Add this as `.github/workflows/readme.yml` in any repository. That stub is
the whole interface.

```yaml
name: README
on:
  schedule:
    - cron: '7 0 * * *'
    - cron: '7 8 * * *'
    - cron: '7 16 * * *'
  workflow_dispatch:

permissions: {}

jobs:
  readme:
    permissions:
      contents: write
      pull-requests: write
    uses: tannergolden/markdown/.github/workflows/readme.yml@v1
    with:
      banners: '7 0 * * *'
      badges: '7 8 * * *'
      trophies: '7 16 * * *'
```

Run it once from the Actions tab. The banners put a header block at the top
of your README and a footer block at its foot, the elements write a data
file with the five elements that need nothing by hand and put a pair of
markers for each at the foot, and the trophies put their block there too;
every kit draws into its own folder under `assets/` and commits. Move any
pair of markers wherever you like: later runs rewrite only what is between
them, and each kit writes only between its own. The badges wait for a
[`.github/badges.yml`](https://github.com/tannergolden/badges/blob/Development/docs/badges.example.yml),
since only you know which badges a page should carry, and say so in the
run's log until it exists.

Drop a kit by deleting its cron in both places. Keep the minutes off the
hour, as they are here: GitHub delays scheduled runs that pile up at `:00`,
and a delayed run costs nothing, since the next one measures everything
again, but an odd minute makes the delays rarer.
[`examples/stub.yml`](examples/stub.yml) is the stub above with its options.

### Or gate on it

Everything the kits draw is committed files, so it can be checked like any
other. With `check: true` the same workflow measures nothing and commits
nothing: every kit the stub names redraws from its lock and the run fails
if any file or README block differs from what the kit draws. No token is
used, and the caller grants `contents: read` and nothing more, so it runs
on a pull request from a fork:
[`examples/stub-check.yml`](examples/stub-check.yml).

### Options

The workflow takes, besides the three crons:

| Input      | Default                          | Meaning                                                                                                    |
| :--------- | :------------------------------- | :--------------------------------------------------------------------------------------------------------- |
| `elements` | `true`                           | Draw the elements in the banners slot, after the banners. `false` leaves the banners alone in their slot.  |
| `mode`     | `repository`                     | `repository`, or `profile` in the repository named after your account. The banners and the trophies both take it. |
| `theme`    | the banners' config              | The print the banners are drawn in, `blueprint` by default, or `rainbowprint`.                              |
| `style`    | the trophies' config             | `trophy`, `crest`, `medallion`, `crystal` or `plaque`.                                                      |
| `author`   | the kits' author                 | Who each refresh commit is by, as `Name <email>`.                                                           |
| `check`    | `false`                          | Verify what is committed instead of refreshing it.                                                          |

Each kit still reads its own config file, so `.github/banners.yml`,
`.github/badges.yml`, `.github/trophies.yml` and `.github/elements.yml` set
everything the kit can set, exactly as they would under the kit's own stub.
Optional tokens are passed through under the kits' own names,
`BANNERS_TOKEN`, `TROPHIES_TOKEN` and `ELEMENTS_TOKEN`; nothing on a
repository's own page needs one.

---

## 🧰 The Kits

<div align="center">

<!-- elements:banners:start -->
<a href="https://github.com/tannergolden/banners">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/elements/banners-dark.svg">
  <img alt="tannergolden/banners. The two ends of the page and its body. Headers, footers and eight elements, measured from GitHub and git, drawn on one paper." src="assets/elements/banners-day.svg">
</picture>
</a>
<!-- elements:banners:end -->
<!-- elements:badges:start -->
<a href="https://github.com/tannergolden/badges">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/elements/badges-dark.svg">
  <img alt="tannergolden/badges. Badges a repository draws for itself from one data file, in six styles and their blueprint twins, so no README depends on a third-party service." src="assets/elements/badges-day.svg">
</picture>
</a>
<!-- elements:badges:end -->

<!-- elements:trophies:start -->
<a href="https://github.com/tannergolden/trophies">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/elements/trophies-dark.svg">
  <img alt="tannergolden/trophies. Trophies and achievements a profile or a repository earns for itself, measured on a schedule, in five styles." src="assets/elements/trophies-day.svg">
</picture>
</a>
<!-- elements:trophies:end -->
<!-- elements:standards:start -->
<a href="https://github.com/tannergolden/standards">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/elements/standards-dark.svg">
  <img alt="tannergolden/standards. The engineering standards every kit follows and the automation that delivers them, called by link rather than copied." src="assets/elements/standards-day.svg">
</picture>
</a>
<!-- elements:standards:end -->

</div>

---

## 🧭 Layout

```bash
markdown/
├── .github/workflows/readme.yml            the reusable workflow your stub calls
├── .github/workflows/own-readme.yml        this page's own stub, at the same three crons
├── .github/workflows/own-readme-check.yml  the check, on a pull request
├── .github/workflows/cut-release.yml       cuts a version and moves v1, via the standards
├── .github/banners.yml                     this page's banners config, and the lock beside it
├── .github/badges.yml                      this page's badges
├── .github/trophies.yml                    this page's trophies config, and the ledger beside it
├── .github/elements.yml                    this page's elements, and the lock beside it
├── .github/scripts/                        the repository's own checks, and the slot picker's test
├── assets/banners/, badges/, trophies/, elements/   what every kit drew for this page
├── examples/                               the stub and the check stub to copy
└── .github/docs/                           the seeded documents every repository carries
```

---

## 🛠️ Working On It

Consuming this needs nothing but the stub above. For the repository itself:

```bash
python3 .github/scripts/validate-repository.py                    # every YAML and JSON file, every pin, every line ending
python3 -m unittest discover -s .github/scripts -p 'test_*.py'    # the slot picker under every event, and the scaffold's own checks
```

The slot picker lives inside the workflow, because a reusable workflow runs
against the caller's checkout where nothing of this repository is on disk;
its test lifts the script out of the YAML and runs it under every event.
A version is cut by dispatching **🏷️ Cut Release** with `vX.Y.Z`: the
standards' release workflow proves the workflow and the stubs exist at the
commit and that the checks pass, then tags the version and moves `v1`.

---

## 📄 License

MIT. See [`LICENSE`](LICENSE). Every image on this page was drawn by one of
the four kits, under their licences.

---

## 🔗 See also

> [!TIP]
> [`tannergolden/banners`](https://github.com/tannergolden/banners) draws the
> header, the footer and the body of the page,
> [`tannergolden/badges`](https://github.com/tannergolden/badges) its badges,
> and [`tannergolden/trophies`](https://github.com/tannergolden/trophies) its
> case. Each can be called on its own, with its own stub; this calls all of
> them with one. The engineering standards they follow are published in
> [`tannergolden/standards`](https://github.com/tannergolden/standards).

<div align="center">

<!-- elements:stamp:start -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/elements/stamp-dark.svg">
  <img alt="Seal: drawn, never fetched. The seal at the foot of a page every kit drew." src="assets/elements/stamp-day.svg">
</picture>
<!-- elements:stamp:end -->

</div>

<!-- banners:footer:start -->
<div align="center">

<a href="#top">
<picture>
  <source media="(max-width: 585px) and (prefers-color-scheme: dark)" srcset="assets/banners/footer-narrow-dark.svg">
  <source media="(max-width: 585px)" srcset="assets/banners/footer-narrow-day.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/banners/footer-dark.svg">
  <img alt="Drawn at both ends, and everything between. Back to Top. Built with love by @tannergolden. Distributed under the MIT License. Last updated September 25, 2026." src="assets/banners/footer-day.svg">
</picture>
</a>

<a href="https://github.com/tannergolden/markdown/issues"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/banners/link-issues-dark.svg"><img alt="Issues" src="assets/banners/link-issues-day.svg"></picture></a>
<a href="https://github.com/tannergolden/markdown/pulls"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/banners/link-pull-requests-dark.svg"><img alt="Pull Requests" src="assets/banners/link-pull-requests-day.svg"></picture></a>
<a href="https://github.com/tannergolden/markdown/releases"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/banners/link-releases-dark.svg"><img alt="Releases" src="assets/banners/link-releases-day.svg"></picture></a>
<a href="https://github.com/tannergolden/markdown/actions"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/banners/link-actions-dark.svg"><img alt="Actions" src="assets/banners/link-actions-day.svg"></picture></a>

</div>
<!-- banners:footer:end -->
