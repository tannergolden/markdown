<!--
title: '📄 ADR-0006: A COLLECTION CHANGES WITH THE MONTH'
description: 'A collection is twelve pixel designs on one subject; a page that picks it is drawn in the month''s design, which changes on the first of every month.'
tags: [adr, architecture, decisions, themes, collections]
category: docs
status: 'Accepted'
date: '2026-10-07'
evidence: 'N/A'
-->

<div align="center">

# 📄 ADR-0006: A COLLECTION CHANGES WITH THE MONTH

<a name="top"></a>

**A collection is twelve pixel designs on one subject; a page that picks it is drawn in the month's design, which changes on the first of every month.**

_Formalized rationale. Transparent intent. Auditable evolution._

</div>

---

## 📋 Meta Information

| Attribute     | Specification                        |
| :------------ | :----------------------------------- |
| **Deciders**  | Tanner Golden                        |
| **Consulted** | Claude Code                          |
| **Informed**  | Everyone whose page the kit draws    |

---

## 🎯 Context & Problem Statement

The kit had two kinds of theme: a single theme, `standard`, and a family of prints a page picks one of, with `rainbowprint` moving through them. The holiday sets showed that a whole page could be drawn as pixel art. A collection is a third kind: one subject drawn twelve ways, so a page that picks it changes through the year. The first is `medieval`. The question was how a page picks a collection, which design it shows when, what a person controls, and how a collection sits beside the holidays.

---

## 🚦 Decision Drivers

- **One setting**: picking a collection should feel like picking any theme.
- **Predictable**: the same day always gives the same design, on every page that picks the collection, and a check can redraw it.
- **Robust**: a late or missed run must never leave a page on the wrong design.
- **Finished**: a collection a page can pick has a design for every month of the year.

---

## 🏗️ Considered Options

1. **A separate `collection:` setting**, beside `theme:`.
2. **A collection that moves to its next design on each update**, as `rainbowprint` does, remembered in the lock.
3. **A collection picked with `theme:`, its design set by the calendar month.**

---

## ✅ Decision Outcome

**Chosen Option**: A collection picked with `theme:`, its design set by the calendar month

### Rationale for Selection

- **One setting.** `theme: medieval` picks the collection, as `theme: blueprint` picks a print. Its names join the list `theme:` accepts, so the stub keeps its shape.
- **The month picks the design.** Every collection has exactly twelve designs, in a fixed order with January's first, and a page is drawn in the design for the month it is in. The change comes at the page's midnight on the first, on the day in the page's `timezone`, as a holiday's does.
- **Nothing to remember.** The design follows from the date, so a run that is late or missed is put right by the next one, and a page that picks a collection mid-month is drawn in that month's design at once. The lock records the design a page was drawn in, so `check` redraws the same one.
- **Designs suit their months.** The order places each design where it fits: the medieval collection's Longship has January for its aurora, Cathedral April for Easter and Tapestry October, the month of Hastings.
- **One design all year.** A page can name a single design, `theme: medieval-forge`, and keep it.
- **Holidays still take over.** With holidays on, a holiday's set is up around its day and hands the page back to the month's design after.
- **Twelve or nothing.** A collection, and each of its designs, can be picked only once all twelve are drawn; a test holds every collection to twelve.
- **Trophies stay standard.** A collection draws the banners, the badges and the elements; the trophy case keeps its standard look.
- **Said in the commit.** The commit on the first of a month says which design took over and when the next one comes.

`src/domain/collections/__init__.py` holds the collections and the month rule, and `markdown-kit collections` prints each one's year.

---

## 📈 Consequence Matrix

| Category         | Impact / Consequence                                                                                       |
| :--------------- | :--------------------------------------------------------------------------------------------------------- |
| **Positive (+)** | A page changes every month with no setup beyond one setting, and every page in a collection shows the same design on the same day. |
| **Negative (-)** | Each design is a full pixel set, so a collection is a large piece of work and grows the kit; none ships until all twelve are drawn. |
| **Neutral (~)**  | A page cannot reorder a collection's months; it can only keep one design all year.                         |

---

## ⚖️ Trade-off Comparative

### Option A: A separate `collection:` setting

- ✅ Makes the new kind of theme visible in the settings.
- ❌ Two settings that cannot both be set, and a stub with a new input.

### Option B: The next design on each update

- ✅ Change tied to what the page shows.
- ❌ Needs the lock, and no two pages show the same design; the month is lost.

### Option C: `theme:` and the calendar month

- ✅ One setting, the same design for everyone on a day, nothing to remember.
- ❌ A collection needs all twelve designs before anyone can pick it.

---

## 🔗 Traceability & Links

- [ADR-0003](ADR-0003-Holiday-Windows.md): the holiday windows, which still take over a collection's page.
- [ADR-0004](ADR-0004-Standard-As-The-Default-Theme.md): `standard`, which the trophy case keeps.

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
