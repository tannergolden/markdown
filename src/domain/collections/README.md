<!--
title: '🗓️ COLLECTIONS'
description: 'The collections: one subject drawn twelve ways, a design for each month, every one in its collection''s hand.'
tags: [source, domain, collections, themes]
category: docs
-->

<div align="center">

# 🗓️ COLLECTIONS

<a name="top"></a>

**Twelve different worlds drawn by the same hand.**

_A design for every month. One artist for the year._

</div>

---

## 💡 What This Folder Is For

A collection is one subject drawn twelve ways: a page that picks it is drawn in
the month's design, which changes on the first of every month
([ADR-0006](../../../docs/adrs/ADR-0006-A-Collection-Changes-With-The-Month.md)).
Each design is a package of its own, its palette in `palette.py` and its drawing
in `art.py`.

[`hand.py`](hand.py) holds what a collection's twelve designs share, so the year
reads as one artist's work: its inks, its ground, its flame, its moon, its skin,
its glint and the month's mark, which [`zodiac.py`](zodiac.py) draws for the
medieval hand
([ADR-0007](../../../docs/adrs/ADR-0007-A-Collection-Is-Drawn-By-One-Hand.md)).
Every design subclasses `CollectionSet`, and the tests hold each one to its
hand. Before starting or changing a collection, read [Drawing a
Collection](../../../docs/technical/Collections.md).

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                                            | Purpose                                                                                                                                                                                    |
| :----------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`medieval_alchemist/`](medieval_alchemist/)     | The Alchemist set: the laboratory at the autumn equinox, in brass and glass.                                                                                                               |
| [`medieval_cathedral/`](medieval_cathedral/)     | The Cathedral set: April's design in the medieval collection, stained glass in stone tracery.                                                                                              |
| [`medieval_chessmen/`](medieval_chessmen/)       | The Chessmen set: a winter's game in a Norse hall, the Lewis chessmen in walrus ivory and bone stained red.                                                                                |
| [`medieval_forge/`](medieval_forge/)             | The Forge set: the smithy and the armoury, beaten out of iron.                                                                                                                             |
| [`medieval_hoard/`](medieval_hoard/)             | The Hoard set: a dragon asleep on its gold in a barrow through midwinter, in hoard gold and garnet.                                                                                        |
| [`medieval_illuminated/`](medieval_illuminated/) | The Illuminated set: a page from the scriptorium, as an illuminator would have painted it, March's design in the medieval collection, drawn in the collection's hand (`collections.hand`). |
| [`medieval_longship/`](medieval_longship/)       | The Longship set: the Viking Age in oak, sea and the northern sky, drawn in the medieval collection's hand.                                                                                |
| [`medieval_mappamundi/`](medieval_mappamundi/)   | The Mappa Mundi set: the medieval world map and the sea chart, in ink on parchment.                                                                                                        |
| [`medieval_mosaic/`](medieval_mosaic/)           | The Mosaic set: the gold of a Byzantine mosaic in August, laid tile by tile.                                                                                                               |
| [`medieval_stronghold/`](medieval_stronghold/)   | The Stronghold set: a castle's wall and its heraldry.                                                                                                                                      |
| [`medieval_tapestry/`](medieval_tapestry/)       | The Tapestry set: the embroidered hanging, after the Bayeux Tapestry.                                                                                                                      |
| [`medieval_tournament/`](medieval_tournament/)   | The Tournament set: the lists in May, in silk, gold cord and plate.                                                                                                                        |
| [`__init__.py`](__init__.py)                     | The collections: one subject drawn twelve ways, a design for each month of the year.                                                                                                       |
| [`hand.py`](hand.py)                             | A collection's hand: what its twelve designs share, so that the year reads as one artist's work.                                                                                           |
| [`README.md`](README.md)                         | This file.                                                                                                                                                                                 |
| [`zodiac.py`](zodiac.py)                         | The medieval hand's month mark: the month's sign of the zodiac, in gold, on a roundel of lapis ringed in gold.                                                                             |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself.

---

<div align="center">

**Twelve worlds, one hand.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
