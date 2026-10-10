<!--
title: '🧩 ELEMENTS'
description: 'The elements: the body of a page, six drawings made from the repository itself, on the same paper as its header and footer.'
tags: [source, domain, elements, svg]
category: docs
-->

<div align="center">

# 🧩 ELEMENTS

<a name="top"></a>

**The body of a page, drawn from its own repository.**

_No coordinate in a data file._

</div>

---

## 💡 What This Folder Is For

The six blueprint elements a page's body is made of: the schematic, the
instruments, the milestones, the roster, the certificate and the placards
([`draw.py`](draw.py)), drawn on the same paper as the page's header and footer.
What each draws from is the `elements:` section of the page's settings
([`data.py`](data.py)).

[`layout.py`](layout.py) computes every position, so a data file never carries a
coordinate.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                        | Purpose                                                                                             |
| :--------------------------- | :-------------------------------------------------------------------------------------------------- |
| [`__init__.py`](__init__.py) | The elements: the body of a README, drawn on the same paper as its header and footer.               |
| [`data.py`](data.py)         | The `elements:` section of a page's settings: which elements it draws, and what each is drawn from. |
| [`draw.py`](draw.py)         | The blueprint elements: six drawings a README makes from its own repository.                        |
| [`layout.py`](layout.py)     | Layout the kit computes, so a data file never carries a coordinate.                                 |
| [`README.md`](README.md)     | This file.                                                                                          |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself.

---

<div align="center">

**The repository, drawn as its own blueprint.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
