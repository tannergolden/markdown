<!--
title: '🌗 PIXEL THEMES'
description: 'The pixel themes: one world drawn as pixel art, a theme a page names and keeps all year, every part of the page in its pixels.'
type: index
-->

<div align="center">

# 🌗 PIXEL THEMES

<a name="top"></a>

**One world drawn as pixel art, worn every day of the year.**

_One set. Two halves. No calendar._

</div>

---

## 💡 What This Folder Is For

A pixel theme is a theme a page names, `theme: heaven-and-hell`, and keeps all
year ([ADR-0012](../../../docs/adrs/ADR-0012-A-Pixel-Theme-Is-Kept-All-Year.md)).
The page is drawn in its set every day: the banners, the badges, the elements,
the trophy case and the games. It has no calendar, so it never changes with the
month, and its headers carry no month's mark and no sign. A holiday's set still
takes the page around its day, and the Birthday set on its birthday, and both
hand it back.

[`__init__.py`](__init__.py) lists every pixel theme in `THEMES`, its key, its
name and a sentence of what it draws, and finds the set that draws one. Each
theme is a package of its own here, named for its key with underscores, whose
`SET` subclasses `holidays.designs.Holiday` and draws with the holiday sets'
layouts and pixel engine. Every set draws each file twice, for GitHub's light
mode and its dark mode, and a pixel theme may make the two twins, as Heaven &
Hell is heaven by day and hell by night. The holiday sets' suite and the games'
suite hold every pixel theme to every rule they hold a set to.
[Themes](../../../docs/technical/Themes.md) defines every kind of theme the kit
draws, and says how to add or remove a pixel theme.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                                  | Purpose                                                                                    |
| :------------------------------------- | :----------------------------------------------------------------------------------------- |
| [`heaven_and_hell/`](heaven_and_hell/) | Heaven & Hell, a pixel theme: angels by day and demons by night, `theme: heaven-and-hell`. |
| [`__init__.py`](__init__.py)           | The pixel themes: one world drawn as pixel art, a theme a page keeps all year.             |
| [`README.md`](README.md)               | This file.                                                                                 |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself.

---

<div align="center">

**A world for the whole year, drawn by the kit's own hand.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the terms in [LICENSE](/LICENSE).

</div>
