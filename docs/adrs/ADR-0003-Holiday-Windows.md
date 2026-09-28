<!--
title: '📄 ADR-0003: HOLIDAY WINDOWS'
description: 'The holiday sets are on by default and take over for 3 to 7 days centred on each holiday; New Year''s Day always runs 3.'
tags: [adr, architecture, decisions, holidays]
category: docs
status: 'Accepted'
date: '2026-09-28'
evidence: 'N/A'
-->

<div align="center">

# 📄 ADR-0003: HOLIDAY WINDOWS

<a name="top"></a>

**The holiday sets are on by default and take over for 3 to 7 days centred on each holiday; New Year's Day always runs 3.**

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

The kit has a set of drawings for each of seven holidays: New Year's Day, Valentine's Day, Juneteenth, Independence Day, Halloween, Thanksgiving and Christmas. They are not themes a page chooses the way it chooses `standard` or a print. The question was how they reach a page: when they start, how long they stay, what a person controls, and what happens at the edges of the year.

---

## 🚦 Decision Drivers

- **Delight without setup**: a page should get the holidays without doing anything.
- **Control without fuss**: one switch to turn them off, and one number for how long they stay.
- **Predictable**: the same day always gives the same drawing, and a check can redraw it.
- **No collisions**: two holidays' sets never compete for the same day.

---

## 🏗️ Considered Options

1. **Holiday themes a page selects**, like any other theme.
2. **Automatic, a fixed 72 hours around each holiday.**
3. **Automatic, 3 to 7 days, the person's choice, centred on the holiday.**

---

## ✅ Decision Outcome

**Chosen Option**: Automatic, 3 to 7 days, centred on the holiday

### Rationale for Selection

- **On by default.** `holidays: false` in the stub or the settings turns every set off. All seven run; none is skipped on its own.
- **How long.** `holiday-days`, from 3 to 7, default 3. The window is centred on the holiday; an even count cannot centre, so the odd day goes before it: 4 days is two before, the day, and one after.
- **New Year's Day always runs 3 days**, December 31 to January 2, whatever `holiday-days` says, so it never reaches back into Christmas.
- **No overlaps.** At 7 days none of the seven can overlap (Christmas and New Year's Day stay three days apart). The calendar still trims any pair that would, at the day between them, and a test checks every year from 1950 to 2150 at every length.
- **The page's own midnight.** The switch happens when the stub runs, on the day in the page's `timezone` (UTC unless the settings name another), so the stub's schedule should sit at the page's midnight.
- **Remembered.** The lock records the holiday a page was drawn in, so `check` redraws the same thing on any day.

`src/domain/holidays/__init__.py` holds the calendar and `make holidays` prints this year's windows.

---

## 📈 Consequence Matrix

| Category         | Impact / Consequence                                                                        |
| :--------------- | :------------------------------------------------------------------------------------------ |
| **Positive (+)** | Every page gets the holidays with no setup, and one switch and one number control them.     |
| **Negative (-)** | A page that wants some holidays and not others cannot have that; it is all seven or none.   |
| **Neutral (~)**  | The page's own theme is untouched; a set hands it back when its window ends.                |

---

## ⚖️ Trade-off Comparative

### Option A: Holiday themes a page selects

- ✅ Full control.
- ❌ Someone has to remember to switch it on, and off again.

### Option B: A fixed 72 hours

- ✅ Simplest.
- ❌ No say in how long a set stays up.

### Option C: 3 to 7 days, centred

- ✅ Automatic, and adjustable with one number.
- ❌ All or none: no single holiday can be skipped.

---

## 🔗 Traceability & Links

- [ADR-0001](ADR-0001-One-Kit-One-Stub.md): the stub's `holidays` and `holiday-days` inputs.
- [ADR-0004](ADR-0004-Standard-As-The-Default-Theme.md): the theme a set hands back to.

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
