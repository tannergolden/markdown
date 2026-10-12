<!--
title: '📄 ADR-0008: THE TROPHY CASE WEARS THE PAGE''S THEME'
description: 'The trophy case is drawn in the page''s theme, as every other part is: its five styles are the standard theme''s, a print draws them on its drafting paper, and a holiday''s set or a collection''s design strikes them in its pixels.'
tags: [adr, architecture, decisions, themes, trophies]
category: docs
status: 'Accepted'
date: '2026-10-12'
evidence: 'N/A'
-->

<div align="center">

# 📄 ADR-0008: THE TROPHY CASE WEARS THE PAGE'S THEME

<a name="top"></a>

**The trophy case is drawn in the page's theme, as every other part is: its five styles are the standard theme's, a print draws them on its drafting paper, and a holiday's set or a collection's design strikes them in its pixels.**

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

[ADR-0001](ADR-0001-One-Kit-One-Stub.md) made one theme set the whole page, and the banners, the badges and the elements each follow it. The trophy case did not. It came from the trophies kit with its own five styles, a cup, a crest, a medallion, a crystal and a plaque, struck in metal and enamel, and kept them in every theme; [ADR-0006](ADR-0006-A-Collection-Changes-With-The-Month.md) kept them in a collection too. On a page in a print the case stood in enamel under a drafting sheet, and on a page in a holiday's set or a collection's design it stood in vector metal under pixel art. It was the one part that did not belong to the page it sat on.

The owner asked for a trophy case for every theme, so that a page whose owner picks a theme flows as one from its header to its footer. The question was how the case takes a theme: what each theme draws, what stays the same, what a person controls, and what happens to the case people already have.

---

## 🚦 Decision Drivers

- **One theme, one page**: the setting that colours the banners, the badges and the elements colours the case.
- **Nothing lost**: the five styles people chose stay their choice, and the standard look stays the trophies kit's own, byte for byte.
- **Nothing moves**: a case keeps its sizes, its words, its files and its README block in every theme, so a holiday coming or going moves no row.
- **Every theme, now and to come**: every print, a repository's own, `rainbowprint`, every holiday's set and every collection's design, without drawing each one by hand.
- **Each theme's rules**: a print keeps to the palette, a set to its closed palette, and a collection's design to its hand.

---

## 🏗️ Considered Options

1. **The standard look in every theme**, as it was.
2. **A trophy style per theme**, `style: blueprint` or `style: pixel`, picked in the trophies section.
3. **The case follows the page's theme**: the standard theme's five styles, a print's drawing of each, a pixel set's art of each, picked by the same `theme:` setting, with `look: standard` to keep the old case.

---

## ✅ Decision Outcome

**Chosen Option**: The case follows the page's theme

### Rationale for Selection

- **One setting.** The page's theme decides the case as it decides every other part: nothing new in the stub, nothing to keep in step.
- **The style is still a choice.** `style:` picks the trophy's shape in every look. A cup is a cup in the blueprint and in the Halloween set, a crest a crest.
- **The standard look is the trophies kit's.** The five styles as they were drawn are the standard theme's look, unchanged to the byte, and a page in `standard` sees no change at all.
- **A print draws.** Each card is a sheet from the set, on the same drafting paper the print's banners are drawn on: the trophy in elevation over a title block, drawn further as its tier rises, from a phantom where it will stand to a finished sheet with its section lining, its ornament and its rays, and its shaded side inked darker tier by tier, lined at gold, crossed at platinum and solid at diamond, so a tier reads at a glance as a metal does. Every colour is the print's, so a card keeps to the palette like the print's banners, a repository's own print included, and `rainbowprint` draws the case in the print it is on.
- **A pixel set strikes.** The layouts live with the sets' others, in `holidays/designs/trophies.py`, and draw from each set's own hooks: its paper, frame and sky, its tags as the plates a tier is engraved on, its inks, its badge colours as enamels, and its own touch along every plate's top. The trophies are struck in five shared metals, each a seven-tone ramp under the engine's one lamp, so gold is gold in every set, and those metals join each set's closed palette for its trophy files alone. Every holiday's set and every collection's design draws the case with no work of its own, every file keeping clear of its frame (a design with a deeper frame says how deep), and a set can still strike its trophies in metals, grounds or plates of its own.
- **A collection's hand holds.** A design letters every word of the case in its hand's two inks on its own ground, and its gold glints on its hand's period.
- **Nothing moves.** A card, a pin, the level card and the next-up card keep the standard look's sizes, so the README's rows stand still, and every look says the same words: the alt text and the README block are the same in every theme.
- **Motion that holds still.** A trophy has no still file, so every look moves in CSS, which a reader's reduced motion stops: a print's linework draws itself in as the page opens, gold glints and platinum sparkles.
- **A case a set cannot letter.** A set's two faces cannot draw every character there is. A case with a word its set cannot letter is drawn whole in the page's own look, never half and half, and the run says why.
- **A way back.** `look: standard` in the trophies section keeps the standard look in every theme.

`src/domain/trophies/looks.py` picks the look from the page's theme and the set it is drawn in, `src/domain/trophies/prints.py` draws a print's case, and the tests hold every look to its lint, its palette, its budget and the standard look's sizes.

---

## 📈 Consequence Matrix

| Category         | Impact / Consequence                                                                                                                          |
| :--------------- | :-------------------------------------------------------------------------------------------------------------------------------------------- |
| **Positive (+)** | The whole page reads as one theme, and every print, holiday's set and collection's design to come draws its trophy case with nothing added.   |
| **Negative (-)** | More drawings to keep: the case is drawn and linted in every look, and the tests and the lint grow with it.                                   |
| **Neutral (~)**  | A case that already had a page in a print or a set changes its look on its next run; `look: standard` keeps it as it was.                     |

---

## ⚖️ Trade-off Comparative

### Option A: The standard look in every theme

- ✅ Nothing to draw.
- ❌ The one part of the page that ignores its theme.

### Option B: A trophy style per theme

- ✅ Full control over the case's look.
- ❌ A second setting to keep in step with the theme, and a holiday's set or a collection's design changes every month while the setting stays.

### Option C: The case follows the page's theme

- ✅ One setting, every theme, the styles kept and the standard look untouched.
- ❌ Every look must draw every style, tier and state, within every theme's rules.

---

## 🔗 Traceability & Links

- [ADR-0001](ADR-0001-One-Kit-One-Stub.md): one theme sets the whole page.
- [ADR-0003](ADR-0003-Holiday-Windows.md): the holiday windows, whose sets now draw the case too.
- [ADR-0004](ADR-0004-Standard-As-The-Default-Theme.md): `standard`, whose look the trophies kit's five styles are.
- [ADR-0006](ADR-0006-A-Collection-Changes-With-The-Month.md): its rule that the trophies stay standard in a collection is replaced by this one.
- [ADR-0007](ADR-0007-A-Collection-Is-Drawn-By-One-Hand.md): the hand a design's trophy case is lettered in.

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
