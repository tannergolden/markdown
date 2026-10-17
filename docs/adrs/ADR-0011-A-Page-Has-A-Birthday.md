<!--
title: '📄 ADR-0011: A PAGE HAS A BIRTHDAY'
description: 'On the page''s birthday the Birthday set takes the page for that one day, over a holiday''s set too: a person''s birthday as the settings give it, a month and a day or the whole date, a repository''s the day GitHub created it.'
tags: [adr, architecture, decisions, birthday, holidays]
category: docs
status: 'Accepted'
date: '2026-10-17'
evidence: 'N/A'
-->

<div align="center">

# 📄 ADR-0011: A PAGE HAS A BIRTHDAY

<a name="top"></a>

**On the page's birthday the Birthday set takes the page for that one day, over a holiday's set too: a person's birthday as the settings give it, a month and a day or the whole date, a repository's the day GitHub created it.**

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

The kit draws a page in a holiday's set around each of seven holidays
([ADR-0003](ADR-0003-Holiday-Windows.md)). A page also has a birthday of its
own: a person's, and a repository's first commit to GitHub. The Birthday set is
a pixel set like the holidays', drawn with their layouts and engine, but it is
no holiday and no theme a page picks. The questions were whose birthday a page
has, where the kit learns it, how long the set stays up, what wins when it
falls on a holiday, and what a person gives away by naming it.

---

## 🚦 Decision Drivers

- **Delight without setup**: a repository's page gets its birthday with no
  settings at all, as it gets the holidays.
- **One day is a birthday**: the set is up for the day, not a season around it.
- **The birthday wins its day**: whatever else would draw the page that day
  gives way, a holiday's set too.
- **A person's choice**: a person says whether their page shows their age; the
  kit never needs their year.
- **Measured, never typed, for a repository**: its birthday is GitHub's date,
  and no setting can name another.
- **Predictable**: the same day always draws the same page, and `check` can
  redraw it with no token.

---

## 🏗️ Considered Options

1. **A window like the holidays'**, `holiday-days` long and centred on the day.
2. **The day alone**, from the page's midnight to the next, winning over
   whatever else is up.
3. **A birthday week**, from the day on.

---

## ✅ Decision Outcome

**Chosen Option**: The day alone, winning over whatever else is up

### Rationale for Selection

- **Whose birthday.** A profile's is the person's, as the settings give it:
  `birthday: 03-14`, or the whole date, `birthday: 1990-03-14`. GitHub keeps no
  birthday for a person, so a profile without one has none. A repository's is
  the day GitHub created it, and a setting that names another day fails the
  run.
- **The year is the person's to give.** Without it the cake carries five slim
  candles and the page says nothing of anyone's age. With it the cake carries
  the age in number candles, as a repository's always does, and the commit says
  which birthday it is. The settings file is as public as the page, so the
  documentation says that a year written there can be read by anyone. No
  message the kit prints repeats what was written.
- **From the first anniversary.** A birthday whose year is known is celebrated
  from its first anniversary on: the day a repository is made is no birthday.
  A February 29 birthday is kept on February 28 in a common year.
- **One day, in the page's time zone.** The set is up from the page's midnight
  to the next, as a holiday's set changes over at the page's midnight. A
  repository's day is the moment GitHub created it, read in that zone, so a
  repository made late in the evening in New York has its birthday that
  evening's day, not the next one in UTC.
- **It wins its day.** The Birthday set draws the page over its theme, a
  collection's design and a holiday's set, and on the next day whatever would
  have drawn the page draws it again, a holiday's set whose window is still
  open included.
- **On by default, with a switch of its own.** `birthday: false` in the
  settings or the stub keeps the set away. `holidays: false` leaves it on.
- **Remembered.** The lock keeps the day GitHub created a repository, and that
  the Birthday set drew the page, so `check` redraws the same files with no
  token.

`src/domain/birthday/` holds the birthday and its set, drawn with
`src/domain/holidays/designs/` and `src/domain/holidays/pixel/`.

---

## 📈 Consequence Matrix

| Category         | Impact / Consequence                                                                                                 |
| :--------------- | :------------------------------------------------------------------------------------------------------------------- |
| **Positive (+)** | Every repository's page celebrates its birthday with no setup, and a person's with one line, the age theirs to give. |
| **Negative (-)** | A run that misses the one day misses the birthday: a set up for one day cannot be put right the day after.           |
| **Neutral (~)**  | A repository moved to GitHub from elsewhere celebrates the day it reached GitHub, not the day it began.               |

---

## ⚖️ Trade-off Comparative

### Option A: A window like the holidays'

- ✅ A late or missed run still finds the set up.
- ❌ Centred on the day, it puts HAPPY BIRTHDAY up the day before, and an age
  on the wrong day.

### Option B: The day alone

- ✅ A birthday is a day, and it wins that day.
- ❌ One missed run, and the page never wears it that year.

### Option C: A birthday week

- ✅ Up for longer.
- ❌ A second setting, and a week of a birthday overlaps a holiday's window far
  more often.

---

## 🔗 Traceability & Links

- [ADR-0001](ADR-0001-One-Kit-One-Stub.md): the stub's `birthday` input.
- [ADR-0003](ADR-0003-Holiday-Windows.md): the holiday windows the birthday
  wins its day from.
- [ADR-0008](ADR-0008-The-Trophy-Case-Wears-The-Pages-Theme.md) and
  [ADR-0009](ADR-0009-The-Games-Wear-The-Pages-Theme.md): the trophy case and
  the games wear the Birthday set while it is up, as they wear a holiday's.

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
