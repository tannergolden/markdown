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
  <img alt="markdown: One stub that keeps a README drawn: banners, badges, trophies and elements, each measured from the repository at its own hour and committed only when…. One stub. The whole page. Project: tannergolden/markdown. Release: v1.0.1. Stars: 0. Forks: 0. Open issues: 0. License: MIT." src="assets/banners/header-day.svg">
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
| **elements** | The body of the page: a schematic, instruments, milestones, a roster, a certificate, placards, a seal              | [`tannergolden/banners`](https://github.com/tannergolden/banners), beside the banners    | 00:07, after them   |
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
per week and the days since the last release, the releases on a time line,
who drew it, and the checks it passes. Only the notes on the releases and the
words on the certificate's ring are written by hand, in
[`.github/elements.yml`](.github/elements.yml).

<!-- elements:vitals:start -->
<picture>
  <source media="(max-width: 585px) and (prefers-color-scheme: dark)" srcset="assets/elements/vitals-narrow-dark.svg">
  <source media="(max-width: 585px)" srcset="assets/elements/vitals-narrow-day.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/elements/vitals-dark.svg">
  <img alt="Instruments for tannergolden/markdown. Commits per week, days since the last release, tracked bytes by file type and counts for tannergolden/markdown." src="assets/elements/vitals-day.svg">
</picture>
<!-- elements:vitals:end -->

<!-- elements:history:start -->
<picture>
  <source media="(max-width: 585px) and (prefers-color-scheme: dark)" srcset="assets/elements/history-narrow-dark.svg">
  <source media="(max-width: 585px)" srcset="assets/elements/history-narrow-day.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/elements/history-dark.svg">
  <img alt="Milestones of tannergolden/markdown. 2 releases of tannergolden/markdown on a time line." src="assets/elements/history-day.svg">
</picture>
<!-- elements:history:end -->

<div align="center">

<!-- elements:contributors:start -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/elements/contributors-dark.svg">
  <img alt="Contributors to tannergolden/markdown. TANNER GOLDEN: 8 commits; CLAUDE: 3 commits." src="assets/elements/contributors-day.svg">
</picture>
<!-- elements:contributors:end -->
<!-- elements:conformance:start -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/elements/conformance-dark.svg">
  <img alt="Conformance of tannergolden/markdown. 5 checks on tannergolden/markdown, with the evidence for each, each met." src="assets/elements/conformance-day.svg">
</picture>
<!-- elements:conformance:end -->

</div>

### The case

The trophies read this repository in the trophies slot: stars from other
people, forks, contributors, commits, releases, merged pull requests, issues
resolved and active days, with a hundred achievements behind them. A new
repository starts with an empty case, which is the honest one.

<!-- trophies:start -->

<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/level.svg"><img src="assets/trophies/level-day.svg" alt="tannergolden/markdown: level 17, 4,719 XP, case 19% complete, released 0 days ago"></picture>
  <picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/next-up.svg"><img src="assets/trophies/next-up-day.svg" alt="Next up: Contributors to Bronze 50%, Label Maker 48%, Green Machine I 27%"></picture>
</p>

<p align="center">
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-stars"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/stars.svg"><img src="assets/trophies/stars-day.svg" alt="Stars trophy: Unranked, 0, 0% to Bronze"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-forks"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/forks.svg"><img src="assets/trophies/forks-day.svg" alt="Forks trophy: Unranked, 0, 0% to Bronze"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-contributors"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/contributors.svg"><img src="assets/trophies/contributors-day.svg" alt="Contributors trophy: Unranked, 1, 50% to Bronze"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-commits"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/commits.svg"><img src="assets/trophies/commits-day.svg" alt="Commits trophy: Unranked, 6, 6% to Bronze"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-releases"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/releases.svg"><img src="assets/trophies/releases-day.svg" alt="Releases trophy: Bronze, 1, 0% to Silver, top 10%, newly reached"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-merged"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/merged.svg"><img src="assets/trophies/merged-day.svg" alt="Merged PRs trophy: Unranked, 0, 0% to Bronze"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-resolved"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/resolved.svg"><img src="assets/trophies/resolved-day.svg" alt="Issues Resolved trophy: Unranked, 1, 10% to Bronze"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-active"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/active.svg"><img src="assets/trophies/active-day.svg" alt="Active Days trophy: Unranked, 1 days, 3% to Bronze"></picture></a>
</p>

<details>
<summary><b>Achievements</b> · 20 of 100 earned · next: Contributors to Bronze, 50%</summary>

<p align="center"><b>Launch</b></p>
<p align="center">
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-first-release"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/first-release.svg"><img src="assets/trophies/achievements/first-release-day.svg" alt="First Release: earned, Rare"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-first-tag"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/first-tag.svg"><img src="assets/trophies/achievements/first-tag-day.svg" alt="First Tag: earned, Uncommon"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-stranger-report"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/stranger-report.svg"><img src="assets/trophies/achievements/stranger-report-day.svg" alt="Stranger Report: earned, Uncommon"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-named"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/named.svg"><img src="assets/trophies/achievements/named-day.svg" alt="Named: earned, Common"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-filed"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/filed.svg"><img src="assets/trophies/achievements/filed-day.svg" alt="Filed: 0% (0 of 3)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-first-fork"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/first-fork.svg"><img src="assets/trophies/achievements/first-fork-day.svg" alt="First Fork: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-first-merge"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/first-merge.svg"><img src="assets/trophies/achievements/first-merge-day.svg" alt="First Merge: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-first-star"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/first-star.svg"><img src="assets/trophies/achievements/first-star-day.svg" alt="First Star: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-first-watcher"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/first-watcher.svg"><img src="assets/trophies/achievements/first-watcher-day.svg" alt="First Watcher: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-front-door"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/front-door.svg"><img src="assets/trophies/achievements/front-door-day.svg" alt="Front Door: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-outside-help"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/outside-help.svg"><img src="assets/trophies/achievements/outside-help-day.svg" alt="Outside Help: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-poster"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/poster.svg"><img src="assets/trophies/achievements/poster-day.svg" alt="Poster: 0% (0 of 1)"></picture></a>
</p>

<p align="center"><b>Health</b></p>
<p align="center">
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-gatekeeper"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/gatekeeper.svg"><img src="assets/trophies/achievements/gatekeeper-day.svg" alt="Gatekeeper: earned, Epic"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-locksmith"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/locksmith.svg"><img src="assets/trophies/achievements/locksmith-day.svg" alt="Locksmith: earned, Epic"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-auto-pilot"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/auto-pilot.svg"><img src="assets/trophies/achievements/auto-pilot-day.svg" alt="Auto-pilot: earned, Rare"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-house-rules"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/house-rules.svg"><img src="assets/trophies/achievements/house-rules-day.svg" alt="House Rules: earned, Rare"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-well-formed"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/well-formed.svg"><img src="assets/trophies/achievements/well-formed-day.svg" alt="Well-Formed: earned, Uncommon"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-clean-bill"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/clean-bill.svg"><img src="assets/trophies/achievements/clean-bill-day.svg" alt="Clean Bill: earned, Common"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-documented"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/documented.svg"><img src="assets/trophies/achievements/documented-day.svg" alt="Documented: earned, Common"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-licensed"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/licensed.svg"><img src="assets/trophies/achievements/licensed-day.svg" alt="Licensed: earned, Common"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-label-maker"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/label-maker.svg"><img src="assets/trophies/achievements/label-maker-day.svg" alt="Label Maker: 48% (12 of 25)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-changelog"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/changelog.svg"><img src="assets/trophies/achievements/changelog-day.svg" alt="Changelog: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-form-filler"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/form-filler.svg"><img src="assets/trophies/achievements/form-filler-day.svg" alt="Form Filler: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-open-hand"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/open-hand.svg"><img src="assets/trophies/achievements/open-hand-day.svg" alt="Open Hand: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-paperwork"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/paperwork.svg"><img src="assets/trophies/achievements/paperwork-day.svg" alt="Paperwork: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-protected"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/protected.svg"><img src="assets/trophies/achievements/protected-day.svg" alt="Protected: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-roadmap"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/roadmap.svg"><img src="assets/trophies/achievements/roadmap-day.svg" alt="Roadmap: 0% (0 of 5)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-support-line"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/support-line.svg"><img src="assets/trophies/achievements/support-line-day.svg" alt="Support Line: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-town-hall"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/town-hall.svg"><img src="assets/trophies/achievements/town-hall-day.svg" alt="Town Hall: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-welcome-mat"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/welcome-mat.svg"><img src="assets/trophies/achievements/welcome-mat-day.svg" alt="Welcome Mat: 0% (0 of 1)"></picture></a>
</p>

<p align="center"><b>Craft</b></p>
<p align="center">
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-follows-the-standards"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/follows-the-standards.svg"><img src="assets/trophies/achievements/follows-the-standards-day.svg" alt="Follows the Standards: earned, Legendary"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-golden-path"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/golden-path.svg"><img src="assets/trophies/achievements/golden-path-day.svg" alt="Golden Path: earned, Legendary"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-ready-room"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/ready-room.svg"><img src="assets/trophies/achievements/ready-room-day.svg" alt="Ready Room: earned, Epic"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-wired"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/wired.svg"><img src="assets/trophies/achievements/wired-day.svg" alt="Wired: earned, Uncommon"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-squeaky"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/squeaky.svg"><img src="assets/trophies/achievements/squeaky-day.svg" alt="Squeaky: earned, Common"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-green-machine"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/green-machine.svg"><img src="assets/trophies/achievements/green-machine-day.svg" alt="Green Machine: 27% (27 of 100)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-release-notes"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/release-notes.svg"><img src="assets/trophies/achievements/release-notes-day.svg" alt="Release Notes: 10% (1 of 10)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-semver"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/semver.svg"><img src="assets/trophies/achievements/semver-day.svg" alt="Semver: 10% (1 of 10)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-by-the-book"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/by-the-book.svg"><img src="assets/trophies/achievements/by-the-book-day.svg" alt="By the Book: 6% (6 of 100)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-containerized"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/containerized.svg"><img src="assets/trophies/achievements/containerized-day.svg" alt="Containerized: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-gitmoji"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/gitmoji.svg"><img src="assets/trophies/achievements/gitmoji-day.svg" alt="Gitmoji: 0% (0 of 100)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-packager"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/packager.svg"><img src="assets/trophies/achievements/packager-day.svg" alt="Packager: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-prerelease"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/prerelease.svg"><img src="assets/trophies/achievements/prerelease-day.svg" alt="Prerelease: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-signed"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/signed.svg"><img src="assets/trophies/achievements/signed-day.svg" alt="Signed: 0% (0 of 100)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-small-steps"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/small-steps.svg"><img src="assets/trophies/achievements/small-steps-day.svg" alt="Small Steps: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-test-suite"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/test-suite.svg"><img src="assets/trophies/achievements/test-suite-day.svg" alt="Test Suite: 0% (0 of 1)"></picture></a>
</p>

<p align="center"><b>Community</b></p>
<p align="center">
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-triage"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/triage.svg"><img src="assets/trophies/achievements/triage-day.svg" alt="Triage: earned, Rare"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-crew"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/crew.svg"><img src="assets/trophies/achievements/crew-day.svg" alt="Crew: 20% (1 of 5)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-ten-strong"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/ten-strong.svg"><img src="assets/trophies/achievements/ten-strong-day.svg" alt="Ten Strong: 10% (1 of 10)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-long-thread"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/long-thread.svg"><img src="assets/trophies/achievements/long-thread-day.svg" alt="Long Thread: 1% (1 of 100)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-talkative"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/talkative.svg"><img src="assets/trophies/achievements/talkative-day.svg" alt="Talkative: 0% (1 of 1,000)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-answered"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/answered.svg"><img src="assets/trophies/achievements/answered-day.svg" alt="Answered: 0% (0 of 10)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-fast-reply"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/fast-reply.svg"><img src="assets/trophies/achievements/fast-reply-day.svg" alt="Fast Reply: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-good-first-issues"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/good-first-issues.svg"><img src="assets/trophies/achievements/good-first-issues-day.svg" alt="Good First Issues: 0% (0 of 5)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-help-wanted"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/help-wanted.svg"><img src="assets/trophies/achievements/help-wanted-day.svg" alt="Help Wanted: 0% (0 of 5)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-mentor"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/mentor.svg"><img src="assets/trophies/achievements/mentor-day.svg" alt="Mentor: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-org-backed"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/org-backed.svg"><img src="assets/trophies/achievements/org-backed-day.svg" alt="Org Backed: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-outside-merges"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/outside-merges.svg"><img src="assets/trophies/achievements/outside-merges-day.svg" alt="Outside Merges: 0% (0 of 10)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-popular-opinion"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/popular-opinion.svg"><img src="assets/trophies/achievements/popular-opinion-day.svg" alt="Popular Opinion: 0% (0 of 50)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-regulars"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/regulars.svg"><img src="assets/trophies/achievements/regulars-day.svg" alt="Regulars: 0% (0 of 5)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-reviewed"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/reviewed.svg"><img src="assets/trophies/achievements/reviewed-day.svg" alt="Reviewed: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-well-maintained"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/well-maintained.svg"><img src="assets/trophies/achievements/well-maintained-day.svg" alt="Well Maintained: 0% (0 of 25)"></picture></a>
</p>

<p align="center"><b>Reach</b></p>
<p align="center">
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-big-name"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/big-name.svg"><img src="assets/trophies/achievements/big-name-day.svg" alt="Big Name: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-cloned"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/cloned.svg"><img src="assets/trophies/achievements/cloned-day.svg" alt="Cloned: not measured yet"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-downloaded"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/downloaded.svg"><img src="assets/trophies/achievements/downloaded-day.svg" alt="Downloaded: 0% (0 of 1,000)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-fork-magnet"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/fork-magnet.svg"><img src="assets/trophies/achievements/fork-magnet-day.svg" alt="Fork Magnet: not measured yet"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-forked-far"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/forked-far.svg"><img src="assets/trophies/achievements/forked-far-day.svg" alt="Forked Far: 0% (0 of 100)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-living-forks"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/living-forks.svg"><img src="assets/trophies/achievements/living-forks-day.svg" alt="Living Forks: 0% (0 of 10)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-referred"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/referred.svg"><img src="assets/trophies/achievements/referred-day.svg" alt="Referred: not measured yet"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-registry"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/registry.svg"><img src="assets/trophies/achievements/registry-day.svg" alt="Registry: not measured yet"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-star-of-the-week"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/star-of-the-week.svg"><img src="assets/trophies/achievements/star-of-the-week-day.svg" alt="Star of the Week: not measured yet"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-stargazer-streak"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/stargazer-streak.svg"><img src="assets/trophies/achievements/stargazer-streak-day.svg" alt="Stargazer Streak: 0% (0 of 12)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-trending"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/trending.svg"><img src="assets/trophies/achievements/trending-day.svg" alt="Trending: not measured yet"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-used-by"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/used-by.svg"><img src="assets/trophies/achievements/used-by-day.svg" alt="Used By: not measured yet"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-visited"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/visited.svg"><img src="assets/trophies/achievements/visited-day.svg" alt="Visited: not measured yet"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-watched"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/watched.svg"><img src="assets/trophies/achievements/watched-day.svg" alt="Watched: 0% (0 of 25)"></picture></a>
</p>

<p align="center"><b>Rhythm</b></p>
<p align="center">
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-friday-deploy"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/friday-deploy.svg"><img src="assets/trophies/achievements/friday-deploy-day.svg" alt="Friday Deploy: earned, Rare"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-alive"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/alive.svg"><img src="assets/trophies/achievements/alive-day.svg" alt="Alive: earned, Uncommon"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-long-game"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/long-game.svg"><img src="assets/trophies/achievements/long-game-day.svg" alt="Long Game: 33% (1 of 3)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-same-day-fix"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/same-day-fix.svg"><img src="assets/trophies/achievements/same-day-fix-day.svg" alt="Same-Day Fix: 10% (1 of 10)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-monthly-release"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/monthly-release.svg"><img src="assets/trophies/achievements/monthly-release-day.svg" alt="Monthly Release: 8% (1 of 12)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-streak"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/streak.svg"><img src="assets/trophies/achievements/streak-day.svg" alt="Streak: 3% (1 of 30)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-marathon-day"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/marathon-day.svg"><img src="assets/trophies/achievements/marathon-day-day.svg" alt="Marathon Day: 2% (1 of 50)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-weekly-beat"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/weekly-beat.svg"><img src="assets/trophies/achievements/weekly-beat-day.svg" alt="Weekly Beat: 1% (1 of 52)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-big-week"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/big-week.svg"><img src="assets/trophies/achievements/big-week-day.svg" alt="Big Week: 1% (1 of 100)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-comeback"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/comeback.svg"><img src="assets/trophies/achievements/comeback-day.svg" alt="Comeback: 0% (0 of 1)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-night-shift"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/night-shift.svg"><img src="assets/trophies/achievements/night-shift-day.svg" alt="Night Shift: 0% (0 of 50)"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-weekend-project"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/weekend-project.svg"><img src="assets/trophies/achievements/weekend-project-day.svg" alt="Weekend Project: 0% (0 of 26)"></picture></a>
</p>

<p align="center"><b>Secret</b></p>
<p align="center">
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-birthday"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/birthday.svg"><img src="assets/trophies/achievements/birthday-day.svg" alt="Secret achievement"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-constellation"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/constellation.svg"><img src="assets/trophies/achievements/constellation-day.svg" alt="Secret achievement"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-friday-the-13th"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/friday-the-13th.svg"><img src="assets/trophies/achievements/friday-the-13th-day.svg" alt="Secret achievement"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-full-house"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/full-house.svg"><img src="assets/trophies/achievements/full-house-day.svg" alt="Secret achievement"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-ghost"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/ghost.svg"><img src="assets/trophies/achievements/ghost-day.svg" alt="Secret achievement"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-green-wall"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/green-wall.svg"><img src="assets/trophies/achievements/green-wall-day.svg" alt="Secret achievement"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-leap-day"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/leap-day.svg"><img src="assets/trophies/achievements/leap-day-day.svg" alt="Secret achievement"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-midnight-oil"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/midnight-oil.svg"><img src="assets/trophies/achievements/midnight-oil-day.svg" alt="Secret achievement"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-new-year"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/new-year.svg"><img src="assets/trophies/achievements/new-year-day.svg" alt="Secret achievement"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-palindrome"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/palindrome.svg"><img src="assets/trophies/achievements/palindrome-day.svg" alt="Secret achievement"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-round-number"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/round-number.svg"><img src="assets/trophies/achievements/round-number-day.svg" alt="Secret achievement"></picture></a>
  <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository-the-answer"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/trophies/achievements/the-answer.svg"><img src="assets/trophies/achievements/the-answer-day.svg" alt="Secret achievement"></picture></a>
</p>

</details>

<p align="center"><sub>Refreshed daily by <a href="https://github.com/tannergolden/trophies">tannergolden/trophies</a> · Every trophy and achievement, what it is for and how to earn it: <a href="https://github.com/tannergolden/trophies/blob/HEAD/docs/Catalogue.md#repository">the catalogue</a>. Click any card for its entry.</sub></p>
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
file with the four elements that need nothing by hand and put a pair of
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
  <img alt="tannergolden/banners. The two ends of the page and its body. Headers, footers and seven elements, measured from GitHub and git, drawn on one paper." src="assets/elements/banners-day.svg">
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
  <img alt="Drawn at both ends, and everything between. Back to Top. Built with love by @tannergolden. Distributed under the MIT License. Last updated September 26, 2026." src="assets/banners/footer-day.svg">
</picture>
</a>

<a href="https://github.com/tannergolden/markdown/issues"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/banners/link-issues-dark.svg"><img alt="Issues" src="assets/banners/link-issues-day.svg"></picture></a>
<a href="https://github.com/tannergolden/markdown/pulls"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/banners/link-pull-requests-dark.svg"><img alt="Pull Requests" src="assets/banners/link-pull-requests-day.svg"></picture></a>
<a href="https://github.com/tannergolden/markdown/releases"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/banners/link-releases-dark.svg"><img alt="Releases" src="assets/banners/link-releases-day.svg"></picture></a>
<a href="https://github.com/tannergolden/markdown/actions"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/banners/link-actions-dark.svg"><img alt="Actions" src="assets/banners/link-actions-day.svg"></picture></a>

</div>
<!-- banners:footer:end -->
