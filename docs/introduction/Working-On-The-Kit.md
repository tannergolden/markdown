<!--
title: '🧰 WORKING ON THE KIT'
description: 'What a machine needs to change the kit, how to see any page in any theme on any day without a token, what to run after each kind of change, and which files are only ever generated. Read it before a first change to this repository.'
type: guide
-->

<div align="center">

# 🧰 WORKING ON THE KIT

<a name="top"></a>

**What to have, what to run, and what never to edit by hand.**

_Preview without a token. Push on green._

</div>

---

## 💡 What You Need

Python 3.10 or later, and git. Nothing else is installed: the kit is the
standard library alone, and reads its own YAML
([ADR-0002](../adrs/ADR-0002-Standard-Library-Only.md)). Run Python here with
the tokens unset, as [AGENTS.md](../../AGENTS.md) asks:

```bash
env -u GH_TOKEN -u GITHUB_TOKEN -u MARKDOWN_TOKEN make lint
env -u GH_TOKEN -u GITHUB_TOKEN -u MARKDOWN_TOKEN make test
```

No test reaches the network: [`tests/fakes/`](../../tests/fakes/README.md)
answers for GitHub. `make test` runs every module of the unit, integration,
end-to-end and script suites side by side, one to a core (`TEST_JOBS` sets
another number); the whole of `make lint test` takes about nine minutes on
four cores, inside the fifteen the CI job allows.

---

## 🚀 Seeing A Page Without A Token

`preview` draws the kit's sample page into a folder the way a run would, and
keeps a lock beside it, so `check` passes on it. A folder with a
`.github/markdown.yaml` is drawn from those settings, and one without from the
defaults. `--input` and `--today` choose what you see:

```bash
python3 src/markdown-kit.py preview --root /tmp/page                                    # the sample, in standard
python3 src/markdown-kit.py preview --root /tmp/page --input theme=blueprint            # in a print
python3 src/markdown-kit.py preview --root /tmp/page --today 2026-10-31                 # in Halloween's set
python3 src/markdown-kit.py preview --root /tmp/page --input theme=medieval --today 2026-12-15  # December's design
python3 src/markdown-kit.py preview --root /tmp/page --input mode=profile --input birthday=10-20 --today 2026-10-20
python3 src/markdown-kit.py check --root /tmp/page
```

The fifth draws a profile on its birthday, in the Birthday set. Without
`--today`, a preview is drawn as of the samples' own day, 2026-09-25.

- `make draw` draws both samples, a repository's page and a profile's, from
  [`tests/fixtures/sample/`](../../tests/fixtures/sample/) into `preview/`, which
  git ignores.
- `make themes` draws every theme into `docs/references/themes/`. Open its
  `index.html` in a browser to see every theme as the kit draws it.
- `python3 src/markdown-kit.py settings --root PATH` prints a page's settings in
  full, every default filled in.

Every command and flag is in [Command Line](../references/Command-Line.md).

---

## 🧪 After Each Kind Of Change

| You changed                             | Run, or read                                                                                                                     | Because                                                                                                          |
| :-------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------- |
| Anything                                | `make lint` and `make test`                                                                                                      | Both must pass before a push, and CI runs the same two                                                           |
| What a module imports                   | `make lint`                                                                                                                      | It runs the layering test, which holds each layer to [Source Code](../technical/Source-Code.md#-layering-rules)  |
| How anything on a page is drawn         | `make themes`, and commit `docs/references/themes/` with the change                                                              | The theme-sets page is committed, and shows every theme as the kit draws it                                      |
| A theme or a set, of any kind           | [Themes and Sets](../technical/Themes.md), first                                                                                 | It names every kind, the words people use for each, and how to add or remove one                                 |
| A collection                            | [ADR-0007](../adrs/ADR-0007-A-Collection-Is-Drawn-By-One-Hand.md) and [Drawing a Collection](../technical/Collections.md), first | A collection is drawn by one hand, and its designs are reviewed together                                         |
| A trophy, an achievement or a threshold | `make catalogue`                                                                                                                 | A unit test fails while `docs/references/Catalogue.md` is stale                                                  |
| A workflow or the action                | `make lint`, then CI's workflow lint                                                                                             | 🚦 Checks runs actionlint and zizmor on every workflow                                                           |
| A new or moved file of the games        | Add its path to [LICENSE-GAMES](../../LICENSE-GAMES) in the same commit                                                          | The games are proprietary, and a source file of theirs carries `SPDX-License-Identifier: LicenseRef-Proprietary` |
| Something every page already relies on  | [Choosing The Number](../distribution/Releasing-The-Kit.md#-choosing-the-number)                                                 | It may need a new major rather than a move of `v1`                                                               |

---

## 📦 Never Edited By Hand

| File                                                                                      | Written by                                                     |
| :---------------------------------------------------------------------------------------- | :------------------------------------------------------------- |
| `docs/references/Catalogue.md`                                                            | `make catalogue`, from the trophies' catalogue and calibration |
| `docs/references/themes/`                                                                 | `make themes`                                                  |
| `src/domain/data/calibration/repositories.json`                                           | `make calibrate`, and 📐 Calibrate each quarter                |
| `assets/` part folders, the README's `markdown:` blocks, and `.github/markdown.lock.json` | This repository's own page, 📝 Markdown, every night           |
| Every table between `AUTO-INDEX` markers                                                  | 🗂️ Machined Indexes, after every push                          |

`tests/fixtures/badges/golden.json` changes only on purpose: it holds every
badge as the badges kit drew it, and the tests hold each drawing to it byte for
byte.

---

## 🌿 Committing

Commits follow [CONTRIBUTING](../../.github/CONTRIBUTING.md): Conventional
Commits with an emoji and a scope, signed off. Never give a commit of your own
the scope `chore(markdown)`, or `chore(banners)`, `chore(badges)`,
`chore(trophies)` or `chore(elements)`: the kit reads those subjects as its own
refreshes, so such a commit never counts as the page's last change or toward its
trophies.

---

### 🔗 See also

- [How A Run Works](../technical/How-A-Run-Works.md) - what the code you are changing does on a run
- [Technology Stack & Tooling](../technical/Technology-Stack-&-Tooling.md) - every Makefile target, and what CI runs
- [Introduction](https://github.com/tannergolden/standards/blob/Development/docs/introduction/README.md) - the principles and environment every repository on the standards shares

---

<div align="center">

**Draw it locally, prove it green, then let the run commit the rest.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
