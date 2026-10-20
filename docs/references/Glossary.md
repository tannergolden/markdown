<!--
title: '📖 GLOSSARY'
description: 'The words the kit, its settings and its code use in a sense of their own, from block and lock to plate, set, hand and ledger, each defined once with where to read more. Look a word up here when Settings or a module uses it without saying what it is.'
type: reference
-->

<div align="center">

# 📖 GLOSSARY

<a name="top"></a>

**The kit's own words, each said once, with where to read the rest.**

_A plate is not a badge. A holiday's set is not a theme._

</div>

---

## 🧭 The Page And The Run

| Word                                  | Means                                                                                                                                                                                                                                                            | More                                                                     |
| :------------------------------------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------- |
| **Page**                              | A README the kit draws, with every file it shows. A profile's (a repository named after its owner) or a repository's; organization pages are not drawn yet                                                                                                       | [Settings](Settings.md#-the-page)                                        |
| **Mode**                              | `profile` or `repository`: which kind of page, and so what the banners and the trophy case count. `auto` tells them apart by the repository's name                                                                                                               | [Settings](Settings.md#-the-page)                                        |
| **Subject**                           | Whose page it is: a login, or `owner/name`                                                                                                                                                                                                                       | [Settings](Settings.md#-the-page)                                        |
| **Part**                              | One of the four things a page is drawn in: the banners, the badges, the elements and the trophy case. Each is measured and planned on its own, and `false` turns one off                                                                                         | [`src/app/parts/`](../../src/app/parts/README.md)                        |
| **Stub**                              | The one workflow a page keeps, `.github/workflows/markdown.yml`, which names the schedule and calls the kit's reusable workflow at `@v1`                                                                                                                         | [README](../../README.md#-one-stub)                                      |
| **Run**                               | One execution of the kit on a page: settle, measure, plan, write, lock, and one commit                                                                                                                                                                           | [How A Run Works](../technical/How-A-Run-Works.md)                       |
| **Measurement**                       | What a part read from GitHub and git on a run, as plain data. The lock keeps it, so the page can be drawn again offline                                                                                                                                          | [How A Run Works](../technical/How-A-Run-Works.md#-measuring)            |
| **Plan**                              | Everything a run will write: each file by path, each README block by name, and the notes                                                                                                                                                                         | [How A Run Works](../technical/How-A-Run-Works.md#-planning-and-writing) |
| **Block**                             | The README's text between `<!-- markdown:NAME:start -->` and `<!-- markdown:NAME:end -->`, which the kit owns and rewrites on every run                                                                                                                          | [`src/domain/readme.py`](../../src/domain/readme.py)                     |
| **Markers**                           | Those two comments. An element is drawn into the README only where its markers stand                                                                                                                                                                             | [Settings](Settings.md#-elements)                                        |
| **Lock**                              | `.github/markdown.lock.json`: what the committed files were drawn from, and what GitHub cannot say again afterwards                                                                                                                                              | [How A Run Works](../technical/How-A-Run-Works.md#-the-lock)             |
| **Snapshot**                          | The lock's write for its own sake, once a week, which keeps a quiet repository's schedule from being switched off                                                                                                                                                | [`src/domain/lock.py`](../../src/domain/lock.py)                         |
| **Stamp**                             | The comment every drawn file opens with, `<!--markdown-kit v1 ...-->`. A run takes away only stamped files it no longer draws                                                                                                                                    | [`src/infra/files.py`](../../src/infra/files.py)                         |
| **Note**                              | A `note:` line a run prints when it drew something short, such as a badge with no data. The run still passes                                                                                                                                                     | [Troubleshooting A Run](../operations/Troubleshooting-A-Run.md)          |
| **Check**                             | The `check` command: the committed page drawn again from the lock and compared byte for byte, with no token                                                                                                                                                      | [README](../../README.md#-checking-a-page)                               |
| **Day, dark, narrow and still files** | Most pictures come as a day file and a dark file, which the README's `<picture>` picks between by the reader's light or dark mode. Headers, footers and wide elements add a pair drawn 360 pixels wide for a phone, and a header a still pair for reduced motion | [Settings](Settings.md#-themes)                                          |
| **Specimen**                          | `tests/fixtures/driftmark`, a made-up project whose settings write every element's fields by hand, which `make lint` and the tests draw in every design                                                                                                          | [Fixtures](../../tests/fixtures/README.md)                               |

---

## 🎨 Themes, Prints And Sets

| Word                       | Means                                                                                                                                                                                                                                                                                    | More                                                                      |
| :------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------ |
| **Theme**                  | What the whole page is drawn in, set once by `theme:`, of one of five kinds: `standard`, a print (`rainbowprint` and a print of the page's own among them), a pixel theme, a collection, or one of a collection's designs named alone. Never a holiday's set or the Birthday set         | [Themes and Sets](../technical/Themes.md)                                 |
| **Standard**               | The default theme: the original badges' own look, grown to the size of a header                                                                                                                                                                                                          | [ADR-0004](../adrs/ADR-0004-Standard-As-The-Default-Theme.md)             |
| **Print**                  | A colour a drawing is reproduced in: lines and lettering on white by day, and by night the sheet they are printed on. Eleven ship, and a page adds its own under `prints:`                                                                                                               | [Settings](Settings.md#your-own-prints)                                   |
| **Rainbowprint**           | A theme that draws each update in the next print of the spectrum, red to pink. The lock remembers which one it is on                                                                                                                                                                     | [Settings](Settings.md#-themes)                                           |
| **Drafting paper**         | The grid and title block every sheet in a print is drawn on, the banners' and the elements' alike                                                                                                                                                                                        | [`src/domain/drafting.py`](../../src/domain/drafting.py)                  |
| **Plate**                  | A badge's blueprint twin: in a print, every badge is drawn as its plate, lettered in that print                                                                                                                                                                                          | [Settings](Settings.md#-badges)                                           |
| **Sheet, section, strip**  | The three header designs, H1, H2 and H3. `section` is the default                                                                                                                                                                                                                        | [Settings](Settings.md#-banners)                                          |
| **Title block, scale bar** | The two footer designs, F1 and F2. Left empty, the footer is the one made for the header                                                                                                                                                                                                 | [Settings](Settings.md#-banners)                                          |
| **Set**                    | Every part of a page drawn in pixel art, in the same files: a holiday's set or the Birthday set, which take the page over on their days and hand it back, and every pixel theme and collection's design, which a page wears as its theme. `standard` and the prints are themes, not sets | [Themes and Sets](../technical/Themes.md#-words-that-mean-one-thing-here) |
| **Window**                 | The days a holiday's set is up: `holiday-days`, 3 to 7, centred on the day. New Year's Day always runs December 31 to January 2                                                                                                                                                          | [ADR-0003](../adrs/ADR-0003-Holiday-Windows.md)                           |
| **Pixel theme**            | One world drawn as pixel art and kept all year, such as `heaven-and-hell`: one set every day, with no calendar, no month's mark and no sign. A holiday's set still takes its days                                                                                                        | [ADR-0012](../adrs/ADR-0012-A-Pixel-Theme-Is-Kept-All-Year.md)            |
| **Collection**             | One subject drawn as twelve pixel designs, one for each month. `medieval` is the first                                                                                                                                                                                                   | [ADR-0006](../adrs/ADR-0006-A-Collection-Changes-With-The-Month.md)       |
| **Design**                 | One of a collection's twelve. Naming one, such as `medieval-forge`, keeps it all year                                                                                                                                                                                                    | [Settings](Settings.md#-collections)                                      |
| **Hand**                   | What a collection's twelve designs share, so the year reads as one artist's work: the light, the inks of its words, the bands its grounds fall in, its flame and moon, its people, its glint and the month's mark                                                                        | [Drawing a Collection](../technical/Collections.md)                       |
| **Mark, sign**             | The month's mark at the top centre of every header on a collection's calendar; the medieval collection's is the month's sign of the zodiac in a gold roundel. `sign` keeps one sign all year                                                                                             | [Settings](Settings.md#-collections)                                      |
| **Look**                   | How the trophy case is drawn: `theme` follows the page's theme, and `standard` keeps the standard look in every theme                                                                                                                                                                    | [Settings](Settings.md#-trophies)                                         |
| **Theme-sets page**        | `docs/references/themes/index.html`, drawn by `make themes`: every theme as the kit draws it, on GitHub's light and dark grounds                                                                                                                                                         | [README](../../README.md#-one-theme-for-the-whole-page)                   |

---

## 🏷️ Badges And Elements

| Word             | Means                                                                                                                                                                                     | More                                                         |
| :--------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------- |
| **Static badge** | A badge that says what its settings write, drawn into `assets/badges/static/`                                                                                                             | [Settings](Settings.md#-badges)                              |
| **Live badge**   | A badge with a `measure:`. The kit measures a workflow, the last commit or the release on every run, or a workflow writes it with `markdown-kit set`; drawn into `assets/badges/dynamic/` | [ADR-0005](../adrs/ADR-0005-The-Kit-Measures-Live-Badges.md) |
| **Gold label**   | The label colour only a live badge may wear, so gold always means a measured value                                                                                                        | [Settings](Settings.md#-badges)                              |
| **State**        | A live badge's colour: green, yellow or red, or slate for no data                                                                                                                         | [Settings](Settings.md#-badges)                              |
| **Localize**     | Drawing a static shields.io badge the repository's Markdown links to as a committed file, and pointing the link at it                                                                     | [Settings](Settings.md#-badges)                              |
| **Element**      | One drawing in the page's body, with an id that names its files and its README block, and a `kind`, such as a schematic, a roster or a certificate                                        | [Settings](Settings.md#-elements)                            |
| **`measure:`**   | On an element, what fills it from GitHub or git on every run. Left out, the element is drawn from its settings alone; `{}` asks for the defaults. On a badge, it makes the badge live     | [Settings](Settings.md#-elements)                            |

---

## 🏆 The Trophy Case

| Word                             | Means                                                                                                                                                                           | More                                                                   |
| :------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :--------------------------------------------------------------------- |
| **Case**                         | The trophy case: the core trophies, the level and next-up cards over them, and the achievements                                                                                 | [Settings](Settings.md#-trophies)                                      |
| **Core trophy**                  | A count that only grows, cut into five tiers, with a star past Diamond each time the Diamond number doubles, up to five                                                         | [Catalogue](Catalogue.md#-how-tiers-work)                              |
| **Tier**                         | Bronze, Silver, Gold, Platinum or Diamond, with Unranked below Bronze                                                                                                           | [Catalogue](Catalogue.md#-tiers-and-rarities)                          |
| **Achievement**                  | Earned or not. A tiered one is earned at each of its thresholds; a secret one shows a question mark until it is earned                                                          | [Catalogue](Catalogue.md#-how-tiers-work)                              |
| **Rarity**                       | Common, Uncommon, Rare, Epic or Legendary: the share of the population expected to earn an achievement, which decides the metal it is drawn in                                  | [Catalogue](Catalogue.md#-how-the-numbers-were-set)                    |
| **Heavy**                        | An achievement that reads individual commits rather than one count, under the `scan-pages` budget, so it catches up over the next runs                                          | [Catalogue](Catalogue.md#-how-tiers-work)                              |
| **Level and next-up cards**      | The two cards over the trophies: the case's level and how complete it is, and the steps it is nearest to                                                                        | [Settings](Settings.md#-trophies)                                      |
| **NEW ribbon**                   | The mark on a tier first reached in the last seven days, dated from the ledger                                                                                                  | [`src/domain/trophies/ledger.py`](../../src/domain/trophies/ledger.py) |
| **Ledger**                       | The case's record in the lock: the day each tier was first reached, a daily history of the core values, the commit scanner's cache, and the measurement the case was drawn from | [How A Run Works](../technical/How-A-Run-Works.md#-the-lock)           |
| **Calibration**                  | Pinning every threshold and rarity to a measured share of a reference population. 📐 Calibrate measures the repository population each quarter                                  | [Catalogue](Catalogue.md#-how-the-numbers-were-set)                    |
| **Measured, derived, estimated** | Where a share comes from: read off a dataset, a dataset scaled by a stated factor, or the population's shape applied to a count no dataset holds                                | [Catalogue](Catalogue.md#-how-the-numbers-were-set)                    |
| **Top N%**                       | The chip on a card: the share of the reference population at or above its value, interpolated between the trophy's anchors                                                      | [Catalogue](Catalogue.md#-how-the-numbers-were-set)                    |

---

### 🔗 See also

- [Glossary](https://github.com/tannergolden/standards/blob/Development/docs/references/Glossary.md) - the words every repository on the standards shares
- [Settings](Settings.md) - every key these words name
- [Themes and Sets](../technical/Themes.md) - every kind of theme and set, and the words people use for each

---

<div align="center">

**One word, one meaning, one place to look it up.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
