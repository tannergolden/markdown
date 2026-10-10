<!--
title: '🧠 DOMAIN LAYER'
description: 'The domain layer: entities, business rules, and pure logic that import nothing outside themselves.'
tags: [source, domain-layer, business-rules, architecture]
category: docs
-->

<div align="center">

# 🧠 DOMAIN LAYER

<a name="top"></a>

**The entities and business rules that make this project what it is, with no I/O.**

_Import nothing. Depend on nothing._

</div>

---

## 💡 What This Folder Is For

The domain layer holds what would still be true if the project changed its
framework, its database, and its transport tomorrow: its entities, its business
rules, and the pure logic that applies them. No I/O happens here - no network,
no disk, no database - which also makes it the easiest code in the project to
test.

It imports nothing outside itself except the standard library. When it needs
the outside world, it declares an interface, and
[`../infra/`](../infra/README.md) implements it.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                                   | Purpose                                                                                                                                        |
| :-------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------- |
| [`badges/`](badges/README.md)           | The badges: the classic styles and their blueprint plates, what a live badge measures, and the shields.io links a page localizes.              |
| [`banners/`](banners/README.md)         | The banners: a page's header and footer, the links row under the footer, and the plan and commit a run makes of them.                          |
| [`collections/`](collections/README.md) | The collections: one subject drawn twelve ways, a design for each month, every one in its collection's hand.                                   |
| [`data/`](data/README.md)               | The kit's data: the glyph outlines and their licences, the print catalogue, and the repository population the trophies are calibrated against. |
| [`elements/`](elements/README.md)       | The elements: the body of a page, six drawings made from the repository itself, on the same paper as its header and footer.                    |
| [`holidays/`](holidays/README.md)       | The holiday calendar and its sets: which holiday draws a page on a given day, the pixel engine the sets share, and one package per holiday.    |
| [`standard/`](standard/README.md)       | The standard theme: the original badges' own look, grown to a masthead header, its footer and the six elements.                                |
| [`trophies/`](trophies/README.md)       | The trophy case: what a profile or a repository can earn, where each threshold sits, the ledger in the lock, and the cards each style draws.   |
| [`__init__.py`](__init__.py)            | The domain: what a README page is drawn from and how, with no I/O at all.                                                                      |
| [`canvas.py`](canvas.py)                | One SVG in progress, and the lint every finished one has to pass.                                                                              |
| [`drafting.py`](drafting.py)            | Drafting: the paper every sheet in a print is drawn on, the banners' and the elements' alike.                                                  |
| [`draw.py`](draw.py)                    | Drawing helpers every part shares: icons, the grain, a clip.                                                                                   |
| [`history.py`](history.py)              | Which commits a person made, as opposed to the kit or a bot.                                                                                   |
| [`lettering.py`](lettering.py)          | Outlined lettering, so a file looks the same on every screen.                                                                                  |
| [`lock.py`](lock.py)                    | The lock, `.github/markdown.lock.json`: what the committed files were drawn from.                                                              |
| [`palette.py`](palette.py)              | The 64 colour tokens and the 64 icons every file is drawn with.                                                                                |
| [`pixelsets.py`](pixelsets.py)          | The pixel set a page is drawn in: a holiday's set around its day, or a collection's design for its month.                                      |
| [`prints.py`](prints.py)                | The themes a page can be drawn in: `standard`, the prints, and `rainbowprint`.                                                                 |
| [`README.md`](README.md)                | This file.                                                                                                                                     |
| [`readme.py`](readme.py)                | The README's blocks: what the kit owns between `&lt;!-- markdown:NAME:start --&gt;` and its end marker.                                        |
| [`settings.py`](settings.py)            | `.github/markdown.yaml`: a page's settings, with a default for every one of them.                                                              |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself. A subfolder appears as one row, so give it a README of its own and
its row links to that.

---

<div align="center">

**The rules of the business, free of everything else.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
