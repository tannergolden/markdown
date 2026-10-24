<!--
title: '📄 ADR-0012: A PIXEL THEME IS KEPT ALL YEAR'
description: 'A pixel theme is one world drawn as pixel art, a theme a page names and keeps all year: no calendar, no month''s mark and no sign, every part of the page in its pixels, and the holidays and the birthday still taking their days.'
type: record
status: 'Accepted'
date: '2026-10-20'
evidence: 'N/A'
-->

<div align="center">

# 📄 ADR-0012: A PIXEL THEME IS KEPT ALL YEAR

<a name="top"></a>

**A pixel theme is one world drawn as pixel art, a theme a page names and keeps all year: no calendar, no month's mark and no sign, every part of the page in its pixels, and the holidays and the birthday still taking their days.**

_Formalized rationale. Transparent intent. Auditable evolution._

</div>

---

## 📋 Meta Information

| Attribute     | Specification                     |
| :------------ | :-------------------------------- |
| **Deciders**  | Tanner Golden                     |
| **Consulted** | Claude Code                       |
| **Informed**  | Everyone whose page the kit draws |

---

## 🎯 Context & Problem Statement

A page names its theme in its settings: `standard`
([ADR-0004](ADR-0004-Standard-As-The-Default-Theme.md)), a print, a collection,
which draws the page in a pixel design for each month
([ADR-0006](ADR-0006-A-Collection-Changes-With-The-Month.md)), or one design
of a collection, kept all year. The holiday sets and the Birthday set are drawn
in the same pixels, but no page picks them: the calendar puts them up
([ADR-0003](ADR-0003-Holiday-Windows.md),
[ADR-0011](ADR-0011-A-Page-Has-A-Birthday.md)).

The owner asked for a theme whose light mode is heaven and whose dark mode is
hell: angels by day, demons by night, one world in two halves, worn all year.
None of the kinds there were fits it. A collection is twelve designs on one
subject that change on the first of every month, drawn by one hand
([ADR-0007](ADR-0007-A-Collection-Is-Drawn-By-One-Hand.md)), and a page can
pick it, or one of its designs, only once all twelve are drawn. A holiday's set
is up for days, not a year. The questions were what kind of theme one pixel
world kept all year is, how a page picks it, what it draws, and what rules it
is held to, and what to call each kind so that a person, or an AI agent asked
to add or remove a theme, can tell them apart.

---

## 🚦 Decision Drivers

- **One line**: a page picks it as it picks any theme, `theme: heaven-and-hell`.
- **The whole page**: it draws every part a set draws, the banners, the badges,
  the elements, the trophy case and the games
  ([ADR-0008](ADR-0008-The-Trophy-Case-Wears-The-Pages-Theme.md),
  [ADR-0009](ADR-0009-The-Games-Wear-The-Pages-Theme.md)).
- **The calendar keeps its days**: a holiday's set and the Birthday set still
  take the page over and hand it back.
- **The same bar as every set**: its files are held to every rule a holiday's
  set and a collection's design are held to, with no twelve designs to draw
  before a page can wear it.
- **Words that cannot be confused**: every kind of theme has one name, written
  down once, that says what it is.

---

## 🏗️ Considered Options

1. **A pixel theme**: a kind of its own, one set kept all year.
2. **A collection of twelve**: Heaven & Hell drawn twelve ways, one for each
   month.
3. **A design with no collection**: one design named alone, as
   `medieval-forge` is, belonging to no collection.
4. **A window on the calendar**: up for days around a day of its own, as a
   holiday's set is.

---

## ✅ Decision Outcome

**Chosen Option**: A pixel theme, a kind of its own

### Rationale for Selection

- **Its own kind, its own registry.** `src/domain/pixelthemes/` lists every
  pixel theme by its key and name, and each is a package beside it named for
  its key: `heaven-and-hell` is `src/domain/pixelthemes/heaven_and_hell/`. A
  page can pick a pixel theme once its package is there.
- **Kept all year, with no calendar.** The page is drawn in the theme's set
  every day, as a page that names one design of a collection is. It does not
  change with the month, and its headers carry no month's mark and no sign: the
  mark belongs to a collection's calendar, and `sign:` to a collection's hand.
- **Two halves, as every set has.** Every set draws each file twice, once for a
  reader in GitHub's light mode and once for one in its dark mode. A pixel
  theme may draw the two as twins, as Heaven & Hell is heaven by day and hell
  by night, each thing of heaven's with its fallen twin standing where it
  stood.
- **The whole page.** A pixel theme draws the banners, the badges, the elements,
  the trophy case and the games through the same layouts and pixel engine as
  every set (`src/domain/holidays/designs/` and `src/domain/holidays/pixel/`),
  and builds the games' boards and the Hall's podium of its own world's stuffs.
  A file it cannot draw, like a title in letters its pixels lack, is drawn in
  the standard theme, as a collection's is.
- **The calendar still wins its days.** With holidays on, a holiday's set takes
  the page over around its day and hands it back to the pixel theme, and on the
  page's birthday the Birthday set takes it for the day.
- **Held to every set's rules.** The holiday sets' suite holds every pixel
  theme to the rules it holds a holiday's set to, its files well formed, in
  their lint and budgets, in the set's closed palette, the same every time,
  its letters at 4.5:1 and moving only where the kit allows, and the games'
  suite holds its boards and its Hall to theirs. A collection's one hand is a
  rule for its year, and a pixel theme has no year to share.
- **The kinds, written down.** [Themes](../technical/Themes.md) defines every
  kind of theme and set the kit draws, the words people use for each, and how
  to add or remove one, so that a request in plain words reaches the right
  kind.

---

## 📈 Consequence Matrix

| Category         | Impact / Consequence                                                                                              |
| :--------------- | :---------------------------------------------------------------------------------------------------------------- |
| **Positive (+)** | A page wears one world all year with one line, and a new world needs one set, not twelve designs.                 |
| **Negative (-)** | One more kind of theme to tell apart from a collection's design kept all year, which draws the page the same way. |
| **Neutral (~)**  | The theme-sets page draws each pixel theme beside the holiday sets and the collections' months.                   |

---

## ⚖️ Trade-off Comparative

### Option A: A pixel theme

- ✅ One line, all year, and one set to draw.
- ❌ A kind of its own, with its own registry and its own name to learn.

### Option B: A collection of twelve

- ✅ Fits the kind the kit already has.
- ❌ Twelve designs for one idea, and heaven and hell keep no calendar.

### Option C: A design with no collection

- ✅ Draws the page the way a design kept all year already does.
- ❌ Every collection has exactly twelve designs; a design of none breaks that
  rule, and its name, `medieval-` before it, would say it belongs to one.

### Option D: A window on the calendar

- ✅ Fits the holiday sets' way of taking over.
- ❌ Up for days, when the page wants it all year.

---

## 🔗 Traceability & Links

- [ADR-0003](ADR-0003-Holiday-Windows.md) and
  [ADR-0011](ADR-0011-A-Page-Has-A-Birthday.md): the holiday's set and the
  Birthday set that still take a pixel theme's page for their days.
- [ADR-0004](ADR-0004-Standard-As-The-Default-Theme.md): `standard`, which draws
  any file a pixel theme cannot.
- [ADR-0006](ADR-0006-A-Collection-Changes-With-The-Month.md) and
  [ADR-0007](ADR-0007-A-Collection-Is-Drawn-By-One-Hand.md): the collections, the
  kind a pixel theme is not.
- [ADR-0008](ADR-0008-The-Trophy-Case-Wears-The-Pages-Theme.md) and
  [ADR-0009](ADR-0009-The-Games-Wear-The-Pages-Theme.md): the trophy case and
  the games wear a pixel theme as they wear every theme.
- [ADR-0010](ADR-0010-The-Games-Are-Proprietary.md): what a pixel theme draws of
  the games is Game Materials, under LICENSE-GAMES.

### 🔗 See also

> [!TIP]
> Every canonical guide is indexed in the [&#x1F4DA; Standards Index](https://github.com/tannergolden/standards/blob/Development/docs/README.md). If you rename or move a file, update every reference to it across the repository to prevent link drift.

---

<div align="center">

**One decision. One record. Zero ambiguity.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
