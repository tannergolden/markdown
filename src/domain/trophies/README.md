<!--
title: '🏆 TROPHIES'
description: 'The trophy case: what a profile or a repository can earn, where each threshold sits, the ledger in the lock, and the cards each style draws.'
type: index
keywords: [source, domain, svg]
-->

<div align="center">

# 🏆 TROPHIES

<a name="top"></a>

**Trophies and achievements a page earns for itself.**

_Calibrated against real repositories._

</div>

---

## 💡 What This Folder Is For

The trophy case: the catalogue of core trophies and achievements a profile or a
repository can earn ([`catalogue.py`](catalogue.py)), and where each threshold
sits against real GitHub data ([`calibration.py`](calibration.py)).
[`ledger.py`](ledger.py) keeps in the lock what GitHub cannot say afterwards.

[`art.py`](art.py) and [`styles.py`](styles.py) draw the cards in each style,
lettered in outlines so a trophy looks the same on every device: the standard
theme's look. The case is drawn in the page's theme, and
[`looks.py`](looks.py) picks the look: the standard one, a print's, which
[`prints.py`](prints.py) draws on the print's drafting paper, or a pixel set's,
which every holiday's set, pixel theme and collection's design draws from
[`holidays/designs/trophies.py`](../holidays/designs/trophies.py).
[`plan.py`](plan.py) turns one measurement into every file of the case and the
README's block. [`catalogue_md.py`](catalogue_md.py) writes
[`docs/references/Catalogue.md`](../../../docs/references/Catalogue.md) from the catalogue and the
calibration, so the two cannot drift.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                                | Purpose                                                                                                    |
| :----------------------------------- | :--------------------------------------------------------------------------------------------------------- |
| [`__init__.py`](__init__.py)         | The trophy case: trophies and achievements a profile or a repository earns for itself.                     |
| [`art.py`](art.py)                   | The drawing: cards, pins and the two banner cards, as SVG strings.                                         |
| [`block.py`](block.py)               | The README's trophies block: the level and next-up cards, the core trophies, then the achievements.        |
| [`calendar.py`](calendar.py)         | Date arithmetic over a set of active days: streaks, weeks, months, years.                                  |
| [`calibration.py`](calibration.py)   | Where every threshold sits against real GitHub data.                                                       |
| [`catalogue.py`](catalogue.py)       | The catalogue: what a trophy case can hold, in both modes.                                                 |
| [`catalogue_md.py`](catalogue_md.py) | Docs/references/Catalogue.md, written from the catalogue and the calibration so it cannot drift from them. |
| [`ledger.py`](ledger.py)             | The case's record in the lock: what GitHub cannot say afterwards.                                          |
| [`looks.py`](looks.py)               | The look a case is drawn in: the standard theme's, a print's, or a pixel set's.                            |
| [`plan.py`](plan.py)                 | From one measurement to every file of the case, the README's block, and what the commit says.              |
| [`prints.py`](prints.py)             | A trophy case on a print's page: every card a drawing on the print's drafting paper.                       |
| [`README.md`](README.md)             | This file.                                                                                                 |
| [`sample.py`](sample.py)             | Example measurements, for previews and the tests.                                                          |
| [`scan.py`](scan.py)                 | What a commit says about its author, for every "heavy" achievement.                                        |
| [`settings.py`](settings.py)         | The `trophies:` section of a page's settings: how the case is drawn, with a default for everything.        |
| [`styles.py`](styles.py)             | The four other card styles: trophy (the default, a cup), medallion, crystal and plaque.                    |
| [`text.py`](text.py)                 | Outlined lettering, so a trophy looks the same on every device.                                            |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself.

---

<div align="center">

**Earned, not claimed.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
