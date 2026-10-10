<!--
title: '🎭 FAKES'
description: 'Stand-ins for the outside world: a GitHub that answers from a table, so no test touches the network.'
tags: [testing, fakes, test-doubles, github]
category: docs
-->

<div align="center">

# 🎭 FAKES

<a name="top"></a>

**The outside world, answered from a table.**

_Same methods. No network._

</div>

---

## 💡 What This Folder Is For

[`github.py`](github.py) is a GitHub client with the same methods as
`infra.github.GitHub`, answering every call from a table, so the tests measure a
page the way a run does, with no token and no network.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                        | Purpose                                                                                           |
| :--------------------------- | :------------------------------------------------------------------------------------------------ |
| [`__init__.py`](__init__.py) | Stand-ins for the outside world: a GitHub that answers from a table, and the answers it gives.    |
| [`github.py`](github.py)     | A GitHub client that answers from a table: the same methods as `infra.github.GitHub`, no network. |
| [`README.md`](README.md)     | This file.                                                                                        |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself.

---

<div align="center">

**Real code, a world made to order.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
