<!--
title: '🎉 HOLIDAYS'
description: 'The holiday calendar and its sets: which holiday draws a page on a given day, the pixel engine the sets share, and one package per holiday.'
tags: [source, domain, holidays, themes]
category: docs
-->

<div align="center">

# 🎉 HOLIDAYS

<a name="top"></a>

**Around each holiday, a page is drawn in that holiday's set.**

_On by default. Three to seven days._

</div>

---

## 💡 What This Folder Is For

[`__init__.py`](__init__.py) is the calendar: which holiday's set, if any, draws
a page on a given day, for a window of three to seven days centred on the
holiday ([ADR-0003](../../../docs/adrs/ADR-0003-Holiday-Windows.md)). Each
holiday is a package of its own, its palette in `palette.py` and its art in
`art.py`.

The sets share two packages: `pixel/`, the engine they are drawn with, and
`designs/`, the layouts every set shares and the hooks each one draws its own
art in.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                                    | Purpose                                                                                                                                       |
| :--------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------- |
| [`christmas/`](christmas/)               | The Christmas set: a snowy winter sheet under a string of lights.                                                                             |
| [`designs/`](designs/)                   | A holiday set: the layouts every set shares, and the hooks each one draws its own art in.                                                     |
| [`halloween/`](halloween/)               | The Halloween set: a haunted sheet by moonlight.                                                                                              |
| [`independence_day/`](independence_day/) | The Independence Day set: the Fourth of July in red, white and blue.                                                                          |
| [`juneteenth/`](juneteenth/)             | The Juneteenth set: a cookout and Galveston on the Gulf, June 19.                                                                             |
| [`new_years_day/`](new_years_day/)       | The New Year's Day set: the last minutes of the old year, and the first morning of the new one.                                               |
| [`pixel/`](pixel/)                       | The pixel engine the holiday sets draw with: the canvas, its two faces, the badges' icons in pixels, and the light every sprite is shaded by. |
| [`thanksgiving/`](thanksgiving/)         | The Thanksgiving set: a harvest sheet at the turn of the leaves.                                                                              |
| [`valentines_day/`](valentines_day/)     | The Valentine's Day set: a love letter of a sheet.                                                                                            |
| [`__init__.py`](__init__.py)             | The holiday calendar: which holiday's set, if any, draws a page on a given day.                                                               |
| [`README.md`](README.md)                 | This file.                                                                                                                                    |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself.

---

<div align="center">

**Seven holidays, drawn in pixels.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
