<!--
title: '🧪 TESTS'
description: 'The test suites, from isolated units to whole user journeys, and how CI comes to run them.'
tags: [testing, test-suites, ci, scaffold]
category: docs
-->

<div align="center">

# 🧪 TESTS

<a name="top"></a>

**The test suites, one folder for each layer of the pyramid.**

_Many fast tests. Few slow ones._

</div>

---

## 💡 What This Folder Is For

The kit's suites, one folder for each layer of the pyramid: the rules in
[`unit/`](unit/README.md), git and files on real temporary repositories in
[`integration/`](integration/README.md), and the command line as a person runs
it in [`e2e/`](e2e/README.md). [`fixtures/`](fixtures/README.md) holds the golden
files and sample pages they compare against, and [`fakes/`](fakes/README.md)
stands in for GitHub, so no test touches the network.

`make test` runs all three, then the tests of the scripts under
`.github/scripts/`, and
[`.github/workflows/checks.yml`](../.github/workflows/checks.yml) runs the same
command on every pull request.

The binding standard is the canonical
[Testing Strategy](https://github.com/tannergolden/standards/blob/Development/docs/distribution/Testing-Strategy.md);
the fill-in standards under `docs/templates/technical/testing/` are seeded for
your own conventions inside it.

This directory is **yours from the first commit**. Nothing here syncs, and
nothing upstream will ever write to it or delete from it: 🔄 Template Sync
leaves this whole folder to you, this README included.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                                   | Purpose                                                                                                                            |
| :-------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------- |
| [`e2e/`](e2e/README.md)                 | End-to-end tests: whole user journeys driven against a running system, gating promotion to Preview and Release.                    |
| [`fakes/`](fakes/README.md)             | Stand-ins for the outside world: a GitHub that answers from a table, so no test touches the network.                               |
| [`fixtures/`](fixtures/README.md)       | What the tests compare against: the golden files of the badges and trophies, a sample page's settings, and the driftmark specimen. |
| [`integration/`](integration/README.md) | Integration tests: checks that cross a real boundary such as a database, the filesystem, or an HTTP service.                       |
| [`unit/`](unit/README.md)               | Unit tests: fast, isolated checks of one piece of logic each, run on every push.                                                   |
| [`__init__.py`](__init__.py)            | The kit's tests: `unit/` for the rules, `integration/` across a real boundary, `e2e/` through the command line.                    |
| [`gql_check.py`](gql_check.py)          | Every GraphQL document the kit sends, checked before GitHub finds a typo one run at a time.                                        |
| [`parallel.py`](parallel.py)            | Run a folder's test modules at once, one interpreter to a module, as `unittest discover` would run them in one.                    |
| [`README.md`](README.md)                | This file.                                                                                                                         |
| [`support.py`](support.py)              | What every test shares: `src/` on the import path, and the kit's data handed to the domain once.                                   |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push. Each suite logs its own
files.

---

<div align="center">

**Catch it at the lowest level that can catch it.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
