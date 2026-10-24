<!--
title: '🎨 THEMES AND SETS'
description: 'Every kind of theme and set the kit draws, defined once: what each is, how a page gets it, what people call it, and how to add or remove one.'
type: standard
-->

<div align="center">

# 🎨 THEMES AND SETS

<a name="top"></a>

**Every kind of look the kit draws a page in, defined once, so a request in plain words reaches the right one.**

_One word for each kind. One place to add it. One place to take it away._

</div>

---

## 🎯 The two questions

Everything the kit draws a page in answers one of two questions.

1. **What does the page wear?** Its **theme**, the one value of `theme:` in
   `.github/markdown.yaml` or the stub's `theme` input. The page wears it every
   day nothing on the calendar takes the page.
2. **What takes the page for a few days?** A **set on the calendar**: a
   holiday's set around its holiday, and the Birthday set on the page's
   birthday. No setting picks one. The calendar puts it up, takes it down, and
   hands the page back to its theme.

Every theme and every set draws each file twice, once for a reader in GitHub's
light mode and once for one in its dark mode. **Light and dark are the two
halves of one theme, never two themes.** A theme may draw its halves as twins,
as Heaven & Hell draws heaven by day and hell by night, but `theme:` still names
one thing.

`markdown-kit themes` prints every theme a page can pick, by kind, and the sets
the calendar puts up. The
[theme-sets page](https://raw.githack.com/tannergolden/markdown/Development/docs/references/themes/index.html)
shows every one of them drawn.

---

## 📚 The kinds of theme

There are five, and `theme:` takes one value of exactly one of them.

| Kind                      | `theme:` takes                                                                                      | What it is                                                                                                                                         | Where it lives                                                              | Decided in                                                                                                                             |
| :------------------------ | :-------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------- |
| **Standard**              | `standard`, the default                                                                             | The original badges' look at the size of a header, laid out as a masthead.                                                                         | `src/domain/standard/`                                                      | [ADR-0004](../adrs/ADR-0004-Standard-As-The-Default-Theme.md)                                                                          |
| **Print**                 | `blueprint`, `redprint` to `pinkprint`, `brownprint`, `blackprint`, `rainbowprint`, or a page's own | One colour drawn as a drafting sheet: lines on white by day, the sheet by night. `rainbowprint` walks the spectrum. Prints are data, not drawings. | `src/domain/data/prints.json`; a page's own under `prints:` in its settings | [ADR-0004](../adrs/ADR-0004-Standard-As-The-Default-Theme.md)                                                                          |
| **Pixel theme**           | `heaven-and-hell`                                                                                   | One world drawn as pixel art, kept all year: no calendar, no month's mark, no sign.                                                                | `src/domain/pixelthemes/<key>/`                                             | [ADR-0012](../adrs/ADR-0012-A-Pixel-Theme-Is-Kept-All-Year.md)                                                                         |
| **Collection**            | `medieval`, `matrix`                                                                                | One subject drawn twelve ways, a pixel design for each month, changing on the first, the twelve drawn by one hand.                                 | `src/domain/collections/`                                                   | [ADR-0006](../adrs/ADR-0006-A-Collection-Changes-With-The-Month.md), [ADR-0007](../adrs/ADR-0007-A-Collection-Is-Drawn-By-One-Hand.md) |
| **A collection's design** | `medieval-longship` to `medieval-hoard`, `matrix-rain` to `matrix-architect`                        | One of a collection's twelve, named alone and kept all year, without the month's mark.                                                             | `src/domain/collections/<key>/`                                             | [ADR-0006](../adrs/ADR-0006-A-Collection-Changes-With-The-Month.md)                                                                    |

A pixel theme and a collection's design named alone draw a page the same way:
one set, every day. They differ in where they come from. A design is one of
twelve and keeps its collection's hand; a pixel theme belongs to nothing and
answers to no year.

---

## 📅 The sets on the calendar

| Kind              | When it is up                                                                    | How a page turns it off | Where it lives               | Decided in                                            |
| :---------------- | :------------------------------------------------------------------------------- | :---------------------- | :--------------------------- | :---------------------------------------------------- |
| **Holiday's set** | 3 to 7 days around each of seven holidays, `holiday-days` long; New Year's Day 3 | `holidays: false`       | `src/domain/holidays/<key>/` | [ADR-0003](../adrs/ADR-0003-Holiday-Windows.md)       |
| **Birthday set**  | The page's birthday, midnight to midnight, over a holiday's set too              | `birthday: false`       | `src/domain/birthday/`       | [ADR-0011](../adrs/ADR-0011-A-Page-Has-A-Birthday.md) |

Either takes the page over from whatever theme it wears, a print, a pixel theme
or a collection's design alike, and hands it back after.

---

## 🧩 Words that mean one thing here

- **Theme**: what `theme:` names, of the five kinds above. Never a holiday's set
  or the Birthday set, which no setting picks.
- **Set**: a drawing of every part of a page in pixel art, by the shared layouts
  and pixel engine in `src/domain/holidays/designs/` and
  `src/domain/holidays/pixel/`: in code, a subclass of
  `holidays.designs.Holiday`. Every holiday's set, the Birthday set, every
  collection's design and every pixel theme is a set. `standard` and the prints
  are themes but not sets.
- **Pixel theme**: a theme that is one set kept all year.
- **Print**: a theme that is one colour on a drafting sheet. A **print of your
  own** is a page's, written under `prints:` in its settings, with no code.
- **Plate**: a badge drawn in a print, with a day file and a dark one. A badge
  style, not a theme.
- **Collection**: a theme of twelve designs, one for each month.
- **Design**: one of a collection's twelve, which a page can also name alone.
- **Hand**: what a collection's twelve designs share, so the year reads as one
  artist's work, in `src/domain/collections/hand.py`. Only a collection has one.
- **Month's mark** and **sign**: the mark a collection's headers carry while the
  page follows its calendar, the medieval hand's roundel with the month's sign
  of the zodiac in it or the Matrix hand's screen with the month's numeral lit
  on it, and the name of the month it marks, which `sign:` can fix. Only a
  collection's designs carry them.
- **Twins**: the two halves of a theme drawn as a pair, each thing of one with
  its counterpart standing where it stood.
- **Look**: `look:` under `trophies:`, which keeps the trophy case in the
  standard look in any theme.
- **Style**: a badge's style (`for-the-badge`, `flat`, a plate and so on), or a
  trophy's (a cup, a crest). Never a theme.
- **Mode**: `mode:` says whose page it is, a profile, a repository or an
  organization. GitHub's light mode and dark mode are the reader's, and every
  theme draws both. Neither is a theme.
- **Tone**: in code, the print a page is drawn in, with `rainbowprint` resolved
  to its colour of the day.

---

## 🗣️ What people say, and what they mean

A request in plain words names a kind loosely. Read it against this table, and
when it could mean two kinds, ask which before writing anything.

| They say                                                                                                   | They mean                                                                                                |
| :--------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------- |
| "a theme", "a skin", "a look", "a style for my README"                                                     | A theme, of any kind: ask which kind if it is a new one.                                                 |
| "a single theme", "one theme all year", "a standalone theme", "an evergreen theme", "a pixel theme"        | A **pixel theme** when it is pixel art, a **print** when it is one colour.                               |
| "a theme collection", "monthly themes", "a theme for every month", "a series of themes", "a set of twelve" | A **collection**.                                                                                        |
| "just November's design", "keep the forge one", "one month all year"                                       | **A collection's design** named alone: `theme: medieval-forge`.                                          |
| "a holiday theme", "a seasonal theme", "a Christmas theme", "a Halloween look"                             | A **holiday's set**: on the calendar, not a theme. A whole season's look worn all year is a pixel theme. |
| "a birthday theme"                                                                                         | The **Birthday set**.                                                                                    |
| "a colour theme", "my brand's colours", "a custom theme with no code"                                      | A **print of your own**, under `prints:`.                                                                |
| "the dark mode theme", "a light version", "a night theme"                                                  | The dark or light half every theme already draws: not a separate theme.                                  |
| "a badge theme", "the badge style", "plates"                                                               | A **badge style**: not a theme.                                                                          |

---

## ➕ Adding one

### A print of your own

For one page, with no code: name it and give its colours under `prints:`, and
set `theme:` to its name ([Settings](../references/Settings.md#your-own-prints)).
Its name may not be one the kit already draws a theme by.

### A print the kit draws

Add it to `src/domain/data/prints.json`, give it a row in the Themes table of
[Settings](../references/Settings.md#-themes) and the README, and run
`make themes`.

### A pixel theme

1. Give it a key, lowercase words joined by hyphens, and add it to `THEMES` in
   `src/domain/pixelthemes/__init__.py`: its key, its name and a sentence of
   what it draws.
2. Draw its set as a package named for its key with underscores,
   `src/domain/pixelthemes/<key_with_underscores>/`, its `SET` a subclass of
   `holidays.designs.Holiday` with the same `key` and `name`, its closed palette
   as `tokens`, and the hooks it draws in: its ink, paper and sky, its frame
   and garland, its titles, its scenes, its elements' touches and its badges.
   It never names a private repository, and its files carry the MIT licence.
3. Build its boards and its Hall's podium of its own world's stuffs
   (`game_squares`, `game_frame` and `game_podium`). What a theme draws of the
   games is Game Materials, under [LICENSE-GAMES](../../LICENSE-GAMES): a file
   that holds nothing but the games joins its list of paths in the same commit
   and carries `SPDX-License-Identifier: LicenseRef-Proprietary`.
4. Test it. The registry hands it to the holiday sets' suite, the games' suite
   and every suite that walks every set, which hold it to every set's rules:
   well formed, within its lint and budgets, in its own palette, the same every
   time, every letter at 4.5:1 and moving only where the kit allows. Give what
   is its own a test file of its own.
5. Give it a row in the Themes table of
   [Settings](../references/Settings.md#-themes) and the README, and run
   `make themes`, which draws it on the theme-sets page.
6. Review every header at 1x, by day and by night, wide and on a phone, and fix
   the weakest first. The bar is the owner's: "make sure they are absolutely
   badass and anyone viewing it would be AMAZED!"

### A collection

Read [Drawing a Collection](Collections.md) first. Its hand comes before its
first design, in `src/domain/collections/hand.py`; it joins `COLLECTIONS` in
`src/domain/collections/__init__.py` with its twelve designs in month order;
and a page can pick it, or any of its designs, once all twelve are drawn.

### A holiday's set

Its holiday joins `HOLIDAYS` in `src/domain/holidays/__init__.py` with the day
it falls on, its set joins `SETS`, and its package sits beside them, held to the
holiday sets' suite. A holiday's window may never overlap another's
([ADR-0003](../adrs/ADR-0003-Holiday-Windows.md)).

---

## ➖ Removing one

A page that still names a theme the kit no longer draws fails its run, with the
themes it can name listed, so a removal is announced in the release that makes
it.

- **A print of your own**: take it out of `prints:`, and out of `theme:`.
- **A print the kit draws**: take it out of `prints.json`, its rows out of the
  Settings and the README, and run `make themes`.
- **A pixel theme**: take its key out of `THEMES` and delete its package and its
  own tests, then take its rows out of the Settings and the README and run
  `make themes`, which takes its folder off the theme-sets page.
- **A collection**: take it and its twelve designs out together, as a page may
  name any of them. A design is never removed alone, for a collection has
  exactly twelve.
- **A holiday's set**: take it out of `SETS` and delete its package; the holiday
  stays on the calendar with no set, and the page keeps its own theme that day.

A change to what a kind is, rather than to one of its members, is a new decision
record that supersedes the old one.

---

## ✅ Checklist

- [ ] The request names a kind from the tables, or the person was asked which.
- [ ] The key is lowercase words joined by hyphens, and no print takes it.
- [ ] The registry, the package, the tests and the docs change in one commit.
- [ ] `make lint` and `make test` pass, and `make themes` has drawn the page.
- [ ] Every header was reviewed at 1x, by day and by night, wide and on a phone.

---

<div align="center">

**Name the kind first. Everything else follows from it.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
