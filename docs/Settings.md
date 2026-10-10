<!--
title: '⚙️ SETTINGS'
description: 'Every key .github/markdown.yaml can hold, what each does, and the default a page that says nothing gets.'
tags: [settings, configuration, reference]
category: docs
-->

<div align="center">

# ⚙️ SETTINGS

<a name="top"></a>

**Every key a page can set, and what it gets without one.**

_Optional, all of it. Checked, every key of it._

</div>

---

## 📄 The File

A page's settings live in **`.github/markdown.yaml`** (`.github/markdown.yml`
is read too; keep one). A page with no file at all is drawn from what GitHub
says about it, in the `standard` theme, with the holidays on: a header, a
footer and a trophy case, and nothing else until the settings ask.

The file holds the page as a whole at the top, then one section per part:
`banners`, `badges`, `elements` and `trophies`. A part set to `false` is not
drawn, and its files and README block are taken away on the next run.

Each part draws into a folder of its own under `assets/`: `assets/banners/`,
`assets/badges/`, `assets/trophies/` and `assets/elements/`. Every run keeps
the repository clean: a file the kit drew and draws no longer is taken away,
with any folder that leaves empty, and so are the files of the banners,
badges and trophies kits it replaced. A page first drawn into
`assets/markdown/` moves into the parts' folders on its next run. Only files
the kit stamped are ever taken away, so anything made by hand stays.

Every key is checked. An unknown key or value fails the run with the key named,
rather than being quietly ignored. A key may be written with hyphens or with
underscores: `holiday-days` and `holiday_days` are the same key.

```yaml
# .github/markdown.yaml
theme: standard
holiday-days: 5

banners:
  motto: Built to be rebuilt.
  closing: Drawn at both ends. Fetched at neither.

badges:
  - name: build
    label: Build
    icon: check
    measure:
      workflow: checks.yml

trophies:
  style: crest
```

`markdown-kit settings --root .` prints a repository's settings in full, every
default filled in, which is the quickest way to see what a run will do.

---

## 🧭 The Page

| Key            | Default           | What it does                                                                                                                                                                         |
| :------------- | :---------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `mode`         | `auto`            | `profile`, `repository` or `organization`. `auto` reads a profile repository (`name/name`) as a profile, an organization's `.github` as its page, and anything else as a repository. |
| `subject`      | (the repo)        | Whose page it is: a login, an organization, or `owner/name`. Empty: this repository, or its owner on a profile.                                                                      |
| `theme`        | `standard`        | `standard`, a print, `rainbowprint`, a print of your own, or a collection. See [Themes](#-themes) and [Collections](#-collections).                                                  |
| `sign`         | (the month's)     | The sign of the zodiac a collection's headers carry all year, as `leo`, in place of the month's. See [Collections](#-collections).                                                   |
| `holidays`     | `true`            | `false` keeps the holiday sets away. See [Holidays](#-holidays).                                                                                                                     |
| `holiday-days` | `3`               | How long each holiday's set is up: 3 to 7 days. New Year's Day is always 3.                                                                                                          |
| `timezone`     | `UTC`             | The zone the page's day changes in, so a holiday starts at its own midnight. An IANA name: `America/New_York`.                                                                       |
| `readme`       | `README.md`       | The README the blocks are written into; `profile/README.md` for an organization.                                                                                                     |
| `out`          | `assets`          | Where the drawings go, each part in a folder of its own: `banners`, `badges`, `trophies` and `elements`. `profile/assets` for an organization.                                       |
| `lock`         | `true`            | Keep `.github/markdown.lock.json`: what was measured, so `check` can draw the page again with no token.                                                                              |
| `prints`       | none              | Your own prints, each a name and its colours. See [Your own prints](#your-own-prints).                                                                                               |

The stub can set `mode`, `theme`, `sign`, `holidays` and `holiday-days` too, as
inputs of the reusable workflow. A value the stub sets wins over the file's.

---

## 🎨 Themes

| Theme                      | What it draws                                                                                             |
| :------------------------- | :-------------------------------------------------------------------------------------------------------- |
| `standard`                 | The default: the original badges' look at the size of a header, laid out as a masthead.                   |
| `blueprint`                | A print: blue lines on white by day, a blueprint by night, with a drafting sheet's grid and title block.  |
| `redprint` to `pinkprint`  | The spectrum, one print per colour: red, orange, yellow, green, teal, blue, indigo, purple, pink.         |
| `brownprint`, `blackprint` | The two prints the trade named first after the blueprint.                                                 |
| `rainbowprint`             | The next colour of the spectrum each time something the page shows moves. The lock remembers where it is. |
| `medieval`                 | A collection: a pixel design for each month, changing on the first. See [Collections](#-collections).    |

The theme reaches every part at once. The banners and the elements are drawn in
it. The badges are drawn as written in `standard`, and in a print each becomes
its plate in that print. The trophy case keeps its own five styles in every
theme, and its standard look in a collection.

### Your own prints

A print is data: a name, and a colour for its lines, its lettering and its
night sheet, each a palette token or `#RRGGBB`. `label` and `night` are
optional.

```yaml
prints:
  goldprint:
    label: Goldprint
    line: '#B8860B'
    ink: '#5C4400'
    sheet: '#7A5B00'
theme: goldprint
```

`markdown-kit palette` lists the 64 tokens.

---

## 📅 Collections

A collection is one subject drawn twelve ways, as pixel art: a design for each
month of the year. `theme: medieval` draws the page in the medieval
collection's design for the month it is in, and the next design takes over at
the page's midnight on the first of every month, in its `timezone`. Nothing is
remembered to make it happen, so a late or missed run is put right by the next
one, and a page that picks a collection mid-month gets that month's design at
once.

| Month     | Design      | Theme to keep it all year | Its sign      |
| :-------- | :---------- | :------------------------ | :------------ |
| January   | Longship    | `medieval-longship`       | `aquarius`    |
| February  | Chessmen    | `medieval-chessmen`       | `pisces`      |
| March     | Illuminated | `medieval-illuminated`    | `aries`       |
| April     | Cathedral   | `medieval-cathedral`      | `taurus`      |
| May       | Tournament  | `medieval-tournament`     | `gemini`      |
| June      | Mappa Mundi | `medieval-mappamundi`     | `cancer`      |
| July      | Stronghold  | `medieval-stronghold`     | `leo`         |
| August    | Mosaic      | `medieval-mosaic`         | `virgo`       |
| September | Alchemist   | `medieval-alchemist`      | `libra`       |
| October   | Tapestry    | `medieval-tapestry`       | `scorpio`     |
| November  | Forge       | `medieval-forge`          | `sagittarius` |
| December  | Hoard       | `medieval-hoard`          | `capricorn`   |

A design redraws the header, the footer and its buttons, the badges and the
elements, at the same sizes and in the same files, as a holiday's set does.
The trophy case keeps its standard look. With holidays on, a holiday's set
still takes over around its day and hands the page back to the month's design.
Naming one design, `theme: medieval-forge`, keeps it all year. The commit on
the first of a month says which design took over.

Every collection is drawn by one hand: its twelve designs keep their own
subjects and share the light, the ink of their words, the band their grounds
fall in, their firelight, their people and their timing, so the year reads as
one artist's work. A page that follows the collection's calendar carries the
month's mark at the top centre of every header: the medieval collection's is
the month's sign of the zodiac in a gold roundel, as medieval calendars marked
their months. The mark belongs to the calendar, so a page that keeps one
design all year, `theme: medieval-forge`, is drawn without it. See
[Drawing a Collection](technical/Collections.md).

A page can choose its own sign instead, one of the twelve in the table, and
every header then carries that sign in the roundel all year: on a design kept
all year, and on the collection's calendar in place of the month's.

```yaml
theme: medieval-forge
sign: leo
```

Every collection has exactly twelve designs, and a page can pick a collection,
or one of its designs, only once all twelve are drawn.
`markdown-kit collections` prints each collection's year and the design up
today.

---

## 🎃 Holidays

Around each holiday its set takes over the whole page and then hands it back
to the page's theme, or to a collection's design for the month: New Year's Day, Valentine's Day, Juneteenth, Independence
Day, Halloween, Thanksgiving and Christmas. A set is up for `holiday-days`,
centred on the day with the odd day before it; New Year's Day always runs from
December 31 to January 2. There is no switch per holiday: `holidays: false`
keeps them all away.

`markdown-kit holidays --year 2026 --days 5` prints every window of a year.

A set redraws the header, the footer and its buttons, the badges and the
elements as pixel art in its own palette, at the same sizes and in the same
files, so the README's blocks never change. A badge keeps its style, its icon
and its files: a plate still has a day file and a night file, and a live badge
still shows its state, in the set's colours. The trophy case keeps its own
styles all year. A file a set cannot draw, like a title in letters its pixels
lack, is drawn in the page's own theme. A `rainbowprint` holds its colour while
a set is up and picks up where it was. The commit says when a set goes up and
when it comes down.

---

## 🪧 `banners:`

A text field left empty is read from GitHub: the title is the repository's
name or the person's, the tagline its description or their bio. Setting one
keeps it; listing a field under `hide` leaves it out of the drawing, and out of
the alt text with it.

| Key           | Default       | What it does                                                                                                                                |
| :------------ | :------------ | :------------------------------------------------------------------------------------------------------------------------------------------ |
| `header`      | `section`     | `sheet` (H1), `section` (H2), `strip` (H3), or `none`.                                                                                      |
| `footer`      | (the pair)    | `title-block` (F1) or `scale-bar` (F2), or `none`. Empty: the one made for the header.                                                      |
| `title`       | (from GitHub) | The title, drawn in capitals.                                                                                                               |
| `tagline`     | (from GitHub) | The line under the title.                                                                                                                   |
| `motto`       | none          | The first note. On a profile, empty reads the person's status message.                                                                      |
| `notes`       | none          | Up to two more notes after the motto.                                                                                                       |
| `description` | none          | A longer line under the tagline.                                                                                                            |
| `figures`     | (the mode's)  | Which figures, in order. See below.                                                                                                         |
| `closing`     | none          | The footer's closing words.                                                                                                                 |
| `top`         | `Back to Top` | The footer's way back up. The whole footer links to the top either way.                                                                     |
| `links`       | (GitHub's)    | Up to four buttons under the footer: a map of `Label: URL`, or a list of `Label \| URL`.                                                    |
| `hide`        | none          | Fields not drawn: `title`, `tagline`, `motto`, `notes`, `description`, `figures`, `closing`, `top`, `built`, `license`, `updated`, `links`. |

**Figures.** A repository's are `project`, `release`, `stars`, `forks`,
`watchers`, `issues`, `pulls`, `language`, `license`, `updated`, `created` and
`site`; by default `project`, `release`, `stars`, `forks`, `issues`,
`language` and `license`. A profile's are `account`, `followers`, `following`,
`repositories`, `stars`, `contributions`, `language`, `since`, `location`,
`company` and `site`; by default `account`, `followers`, `repositories`,
`stars`, `contributions`, `language` and `since`. A figure GitHub has no value
for is left out rather than drawn empty.

In `standard`, the release (or a person's account) stands in the header's
accent block, and the project's path (or a person's site) over the title; the
rest are the badges along its foot.

---

## 🏷️ `badges:`

The list of badges, in the order they stand under the header. Badges with a
black label make one row and those with the gold label a row beneath it.

The kit files each badge by what it is, and no setting names a folder. A live
badge, one with a `measure`, is drawn into `assets/badges/dynamic/`. A static
badge, which says what its author wrote, is drawn into `assets/badges/static/`,
and so is every shields.io badge `localize` draws, in `static/localized/`.
Only a live badge may wear the gold label.

```yaml
badges:
  localize: true          # optional: also turn shields.io links in the repository's Markdown into files
  list:
    - name: status        # the file's name: kebab-case, and unique
      label: Status
      message: Active
      icon: pulse         # one of the 64: markdown-kit icons
      message_color: green
      link: ./
    - name: build
      label: Build
      icon: check
      measure:
        workflow: checks.yml
    - name: coverage      # a workflow measures it: markdown-kit set coverage=87%:green
      label: Coverage
      icon: pulse
      measure: set
```

A plain list works too when `localize` is not wanted.

| Field           | What it holds                                                                                                                               |
| :-------------- | :------------------------------------------------------------------------------------------------------------------------------------------ |
| `name`          | The file's name, kebab-case and unique.                                                                                                     |
| `label`         | The left panel's word.                                                                                                                      |
| `message`       | The right panel's word. A badge the kit measures leaves it out; one a workflow sets holds what it last wrote.                               |
| `label_color`   | A token or `#RRGGBB`. Gold, the live label, by default for a live badge and black for a static one. Only a live badge may be gold.          |
| `message_color` | A token, `#RRGGBB`, or `rotate` for a colour that changes each week. A live badge's is a state.                                             |
| `icon`          | One of the 64 icons.                                                                                                                        |
| `style`         | `for-the-badge` (the default), `flat`, `flat-square`, `plastic`, `pill`, `compact`, or any as a plate: `blueprint-for-the-badge` and so on. |
| `print`         | A plate's print, when the style is a plate.                                                                                                 |
| `reserve`       | Values a plate keeps room for, so it never changes width.                                                                                   |
| `link`          | Where the badge goes when it is clicked.                                                                                                    |
| `measure`       | What makes it live: what the kit measures for it, or `set` for a value a workflow writes. See below.                                        |

**Live badges.** A badge with a `measure:` is live, and wears the gold label
unless it names another: its colour is then a state, green, yellow or red, or
slate for no data. The kit measures the first three kinds itself, every run,
and takes both the message and the state from what it measured. The fourth,
`set`, is a value a workflow measures and writes with `markdown-kit set`:

| `measure:`                                   | Message and state                                                                      |
| :------------------------------------------- | :------------------------------------------------------------------------------------- |
| `workflow: checks.yml`                       | Passing (green), Failing (red), No Data (slate). `repository:` and `branch:` optional. |
| `last-commit` (or `last-commit: owner/name`) | This Week (green), This Month (yellow), Over a Month (red).                            |
| `release` (or `release: owner/name`)         | The tag: green within 90 days, yellow within a year, red after; No Release (slate).    |
| `set`                                        | What a workflow last wrote with `markdown-kit set`; No Data (slate) until then.        |

A person's commit is what counts: the kit's own refreshes, the old kits' and
anything a bot committed never do.

**Letters.** A badge's letters are white where white holds 4.5:1 against the
panel and dark where the dark ink does, so every badge reads at the contrast
WCAG asks of text.

**From the command line.** `markdown-kit set status=Paused coverage=87%:green`
writes a badge's value into the settings, keeping every comment, and the next
run draws it: a static badge's, or a live one's that names `measure: set`. A
badge the kit measures refuses it, since the next run would measure it again.

---

## 🧩 `elements:`

The body of the page. Each element has an id, which names its files and its
README block, and a `kind`. An element is drawn only where the README carries
its markers, because only the README's author knows which section it belongs in:

```html
<!-- markdown:element:how-it-runs:start -->
<!-- markdown:element:how-it-runs:end -->
```

| Kind          | What it draws                                                                | `measure:` fills it from                                                                        |
| :------------ | :--------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------- |
| `schematic`   | Boxes and the wires between them, laid out by the kit.                       | Nothing: it is written by hand.                                                                 |
| `instruments` | Commits per week, days since the last release, bytes by file type, counters. | git: `weeks` (10), and `count:` a map of `LABEL: glob` counted in the tree.                     |
| `milestones`  | Every version tag on a time line.                                            | git: `notable` (a map of `tag: [notes]`) and `planned` releases.                                |
| `roster`      | The people who made it, by commit count.                                     | git: `most` (4), `bots` (true), and `rename` to correct a name.                                 |
| `certificate` | The checks a repository passes, with the evidence for each.                  | git and GitHub: licence, security policy, pinned actions, Conventional Commits, and `ci: main`. |
| `placard`     | A card that links to another repository.                                     | GitHub: `measure: owner/name`.                                                                  |

What the settings write wins over what was measured, so any element can carry
a `title`, a `caption` or a `desc` of its own, and a roster or a certificate
takes `size: half` to stand beside the other at half the page's width. The
fields each kind draws from are in
[`tests/fixtures/driftmark`](../tests/fixtures/driftmark/.github/markdown.yaml),
a made-up project that writes every one of them by hand.

---

## 🏆 `trophies:`

The trophy case: the core trophies with their tiers, and the achievements. A
profile's case counts a person's work; a repository's counts the repository's.
Every trophy and achievement is listed with its threshold and rarity in the
[catalogue](Catalogue.md).

| Key            | Default             | What it does                                                                  |
| :------------- | :------------------ | :---------------------------------------------------------------------------- |
| `style`        | `trophy`            | `trophy`, `crest`, `medallion`, `crystal` or `plaque`.                        |
| `case`         | `both`              | `both`, or only `night` or only `day`.                                        |
| `embed`        | `picture`           | `picture` follows the reader's theme; `fragment` writes GitHub's older links. |
| `banner`       | `true`              | The level and next-up cards above the trophies.                               |
| `streak`       | `current`           | Which streak a profile's level card leads with: `current` or `longest`.       |
| `core`         | (all eight)         | A subset of the core trophies, in order.                                      |
| `enamel`       | none                | A core trophy's colour, as a token: `stars: amber`.                           |
| `achievements` | `all`               | `all`, `none`, or a list of their slugs.                                      |
| `card`         | `rank, weekly, new` | What a trophy card shows besides its tier.                                    |
| `private`      | `false`             | Count private contributions too. Needs `MARKDOWN_TOKEN`.                      |
| `scan-pages`   | `30`                | How many pages of commits, a hundred each, a run reads at most.               |
| `block`        | `true`              | `false` draws the files and leaves the README to its author.                  |

The lock keeps the case's history: the day each tier was first reached, which
dates a NEW ribbon, and the values each card's weekly change is read from. A
page that ran the trophies kit before keeps its history: the first run takes
over `.github/trophies.lock.json`.

---

## 🔗 Traceability & Links

- [README](../README.md): the stub, and what a run does.
- [Catalogue](Catalogue.md): every trophy and achievement.
- [ADR-0003](adrs/ADR-0003-Holiday-Windows.md): the holiday windows.
- [ADR-0004](adrs/ADR-0004-Standard-As-The-Default-Theme.md): `standard` as the default theme.
- [ADR-0005](adrs/ADR-0005-The-Kit-Measures-Live-Badges.md): the live badges.
- [ADR-0006](adrs/ADR-0006-A-Collection-Changes-With-The-Month.md): the collections.
- [ADR-0007](adrs/ADR-0007-A-Collection-Is-Drawn-By-One-Hand.md): one hand for a collection's twelve designs.

### 🔗 See also

> [!TIP]
> Every canonical guide is indexed in the [&#x1F4DA; Standards Index](https://github.com/tannergolden/standards/blob/Development/docs/README.md). If you rename or move a file, update every reference to it across the repository to prevent link drift.

---

<div align="center">

**One file. Every key checked. Nothing required.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by [@tannergolden](https://github.com/tannergolden). Distributed under the MIT License.

</div>
