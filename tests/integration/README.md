<!--
title: '🔗 INTEGRATION TESTS'
description: 'Integration tests: checks that cross a real boundary such as a database, the filesystem, or an HTTP service.'
tags: [testing, integration-tests, test-suites, quality]
category: docs
-->

<div align="center">

# 🔗 INTEGRATION TESTS

<a name="top"></a>

**Tests that cross a real boundary, proving the adapters against the real thing.**

_One real boundary per test._

</div>

---

## 💡 What This Folder Is For

An integration test exercises the code where it meets something outside the
process: a database, the filesystem, an HTTP service. These are the tests that
prove the adapters in `src/infra/` work, which no amount of mocking in a unit
test can.

They run on every push, like the unit tests, against local emulators or
containers rather than a shared environment, so a run on a laptop and a run in
CI meet the same dependencies. Keep each test to one boundary, so a failure
names the thing that broke.

The canonical
[Testing Strategy](https://github.com/tannergolden/standards/blob/Development/docs/distribution/Testing-Strategy.md)
sets where this layer sits and when it runs.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                                              | Purpose                                                                                                                                                                                                                                                                                             |
| :------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`__init__.py`](__init__.py)                       | Makes the suite a package, so `make test` discovers it from the repository's root.                                                                                                                                                                                                                  |
| [`README.md`](README.md)                           | This file.                                                                                                                                                                                                                                                                                          |
| [`test_badges_run.py`](test_badges_run.py)         | The badges through the command line, on a real git repository: measured, drawn, checked, rethemed, localized, set from outside, and taken away again.                                                                                                                                               |
| [`test_banners_run.py`](test_banners_run.py)       | A run of the banners through the command line, on a real folder, with the measurement standing in for GitHub.                                                                                                                                                                                       |
| [`test_clean_run.py`](test_clean_run.py)           | A run keeps a repository clean. Each part draws into a folder of its own under the page's `out`, `assets` by default: `banners`, `badges`, `trophies` and `elements`, and never a folder named for the kit.                                                                                         |
| [`test_collection_run.py`](test_collection_run.py) | A page in a collection, run by run: drawn in the month's design, the next design taking over on the first of the month and named in its commit, a holiday's set still taking over and handing back to the month's design, a named design kept all year, and a collection still being drawn refused. |
| [`test_elements_run.py`](test_elements_run.py)     | The elements through the command line, on a copy of the driftmark specimen, and measured from a real git history: render, check drift, prune, fill blocks, and take the old kit's markers over.                                                                                                     |
| [`test_files.py`](test_files.py)                   | Writing only what changed, line endings and JSON as the kit writes them, and pruning only what the kit drew.                                                                                                                                                                                        |
| [`test_git.py`](test_git.py)                       | The repository through the real `git`: its slug, a person's last change, what differs from HEAD, and committing and pushing through the bot.                                                                                                                                                        |
| [`test_holiday_run.py`](test_holiday_run.py)       | A page through a holiday's window, run by run: its set goes up at the window's first midnight, holds on a quiet day, checks, and comes down after, each change named in its commit; with holidays off it never goes up, and a rainbowprint holds its colour while the set is up.                    |
| [`test_resources.py`](test_resources.py)           | The kit's data files read from disk and handed to the domain, and what day it is where a page is read.                                                                                                                                                                                              |
| [`test_trophies_run.py`](test_trophies_run.py)     | The trophy case through the command line, on real files: drawn, folded into the lock, checked, taken over from the trophies kit's lock, and taken away again.                                                                                                                                       |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself. A subfolder appears as one row, so give it a README of its own and
its row links to that.

---

<div align="center">

**Mock the world in a unit test. Meet it here.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
