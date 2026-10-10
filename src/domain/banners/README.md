<!--
title: '🪧 BANNERS'
description: 'The banners: a page''s header and footer, the links row under the footer, and the plan and commit a run makes of them.'
tags: [source, domain, banners, svg]
category: docs
-->

<div align="center">

# 🪧 BANNERS

<a name="top"></a>

**The first and last sheets of a page's drawings.**

_One measurement. Every design._

</div>

---

## 💡 What This Folder Is For

A page's header and footer, drawn from one measurement and the page's settings:
what each says ([`content.py`](content.py)), how it is composed
([`compose.py`](compose.py)), and every design that draws it
([`designs.py`](designs.py), [`headers.py`](headers.py) and
[`footers.py`](footers.py)), with the row of link chips under the footer.

[`plan.py`](plan.py) settles what a run draws and writes, and the commit that
records it, naming the files it took away apart from the ones it rewrote.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                        | Purpose                                                                                   |
| :--------------------------- | :---------------------------------------------------------------------------------------- |
| [`__init__.py`](__init__.py) | The banners: a README's header and footer, and the links row under the footer.            |
| [`compose.py`](compose.py)   | A measurement and a config, as the header and the footer the designs draw.                |
| [`content.py`](content.py)   | What a header and a footer carry, and the alt text that says it.                          |
| [`designs.py`](designs.py)   | Every design, and every file it draws.                                                    |
| [`footers.py`](footers.py)   | The footers: the foot of the same set of drawings, and the chips their links are made of. |
| [`headers.py`](headers.py)   | The headers: the first sheet of a set of drawings.                                        |
| [`layout.py`](layout.py)     | Layout helpers the designs share: a vertical cursor and the title run.                    |
| [`plan.py`](plan.py)         | What a run draws and writes, and the commit that records it.                              |
| [`README.md`](README.md)     | This file.                                                                                |
| [`sample.py`](sample.py)     | Example measurements, for the gallery, the preview page, `preview` mode and the tests.    |
| [`settings.py`](settings.py) | The `banners:` section of a page's settings, with a default for everything in it.         |
| [`snippets.py`](snippets.py) | The markup a README pastes: one `&lt;picture&gt;` per image.                              |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself.

---

<div align="center">

**Every page opens and closes on the same set of drawings.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
