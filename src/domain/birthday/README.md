<!--
title: '🎂 BIRTHDAY'
description: 'The page''s birthday and its set: whether the Birthday set draws a page on a given day, how old the page turns, and the set itself, drawn with the holiday sets'' pixels.'
tags: [source, domain, birthday, themes]
category: docs
-->

<div align="center">

# 🎂 BIRTHDAY

<a name="top"></a>

**On the page's birthday, the page is drawn in the Birthday set.**

_On by default. One day, and it wins it._

</div>

---

## 💡 What This Folder Is For

[`__init__.py`](__init__.py) is the page's birthday: whether the Birthday set
draws a page on a given day, and how old the page turns
([ADR-0011](../../../docs/adrs/ADR-0011-A-Page-Has-A-Birthday.md)). A person's
birthday is the one their settings give, a month and a day or the whole date; a
repository's is the day GitHub created it. On the day, the set takes the page
from whatever else would draw it, a holiday's set too, and hands it back the
day after.

The set is drawn with the holiday sets' layouts and pixel engine
([`../holidays/designs/`](../holidays/designs/) and
[`../holidays/pixel/`](../holidays/pixel/)), and held to the same checks: its
palette in `palette.py`, its art in `art.py`, and the set in `party.py`.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                        | Purpose                                                                                                                              |
| :--------------------------- | :----------------------------------------------------------------------------------------------------------------------------------- |
| [`__init__.py`](__init__.py) | The page's birthday: whether the Birthday set draws the page on a given day, and how old the page turns.                             |
| [`art.py`](art.py)           | The Birthday set's scenery and sprites, drawn on the shared pixel canvas.                                                            |
| [`palette.py`](palette.py)   | The Birthday set's palette: its ramps, its named colours and its night, and the closed set of every colour one of its files may use. |
| [`party.py`](party.py)       | The Birthday set: a party for the page's birthday, drawn in pixels for the day.                                                      |
| [`README.md`](README.md)     | This file.                                                                                                                           |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself.

---

<div align="center">

**One day a year, drawn in pixels.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
