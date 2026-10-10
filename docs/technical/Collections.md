<!--
title: '🖌️ DRAWING A COLLECTION'
description: 'How a collection is drawn: its hand first, then twelve designs in that hand, each reviewed beside the others until the year reads as one artist''s work.'
tags: [collections, themes, art-direction, pixel-art, guide]
category: docs
-->

<div align="center">

# 🖌️ DRAWING A COLLECTION

<a name="top"></a>

**Twelve designs, one hand: how a collection is drawn so the year reads as one artist's work.**

_One artist. Twelve months. Every rule that can be measured, tested._

</div>

---

## 🎯 The rule

A collection is twelve pixel designs on one subject, one for each month ([ADR-0006](../adrs/ADR-0006-A-Collection-Changes-With-The-Month.md)). Every collection, the medieval one and every one after it, must read as **the work of one artist**: twelve different worlds drawn by the same hand ([ADR-0007](../adrs/ADR-0007-A-Collection-Is-Drawn-By-One-Hand.md)).

A design keeps its own subject, scene, materials, frame, title and palette. It shares its collection's **hand**: the light, the inks of its words, the band its grounds fall in, its firelight and moonlight, its people, its timing and the month's mark. The hand lives in `src/domain/collections/hand.py`, and the tests hold every design to it.

---

## 🧭 Before the first design: the hand

A collection starts from its hand, not from its January. Before anything is drawn, write its entry in `HANDS`:

| Part | What it fixes | The medieval hand |
| :--- | :------------ | :---------------- |
| `body`, `muted` | The ink of every word, by day and by night, the same in all twelve designs | Iron-gall brown and warm cream |
| `day_ground`, `night_ground` | The band of lightness and colour the sheet behind the words falls in | L\* 72 to 90 and C\* at most 40 by day; L\* 4 to 16 and C\* at most 24 by night |
| `flame`, `moon` | The ramps every fire and every moon is drawn on | One amber flame, one pale moon |
| `skin` | The ramps the people's skin is drawn on | Three tones |
| `glint` | How often a title's glint passes | Every 12 seconds |
| `mark` | The month's mark, at the top centre of every header of a page that follows the calendar | The month's sign of the zodiac in a gold roundel on lapis |
| `signs` | The names of the twelve marks, January's first, so a page can choose one to carry all year with `sign` | Aquarius to Capricorn |

Every colour the hand paints joins each design's closed palette through `CollectionSet`, and every word's ink must clear 4.5:1 against both edges of the hand's bands.

Choose the twelve subjects for their months, and make each one a different world: a different place, material and light. Cohesion comes from the hand, never from making the months alike.

---

## ✏️ Drawing a design

Each design is a package beside the collection's registry, `src/domain/collections/<collection>_<name>/`, with its `palette.py`, `art.py` and `__init__.py`, and its tests in `tests/unit/test_<collection>_<name>.py`. Its class subclasses `CollectionSet` and names its collection; the shared layouts in `src/domain/holidays/designs/` draw it, and it fills in their hooks.

Draw in the hand:

- **The light.** Shade every sprite on the engine's ramps, lit from the upper left. Outline in the darkest tone of the material's own ramp, never pure black.
- **The words.** Take `body` and `muted` from the hand. A design's own colours go to its titles, labels and accents.
- **The ground.** Keep the sheet behind the words in the hand's bands and calm behind every word. Put a month's mood in its hue, not its glare.
- **The lights.** Draw every flame on the hand's flame ramp and every moon on its moon ramp. Night is a different world, lit only by its own sources.
- **The people.** Draw faces and hands to one canon, with skin on the hand's ramps, even where an art form sets its own proportions. By night a face keeps its tone and takes its scene's light.
- **The motion.** Use the hand's glint period and the engine's flicker and twinkle. Keep idles short and ambient sweeps slow.
- **The month's mark.** The layouts draw it when the design is drawn as its month's design, and leave it out when a page keeps the design all year. A page that chose a sign, `sign: leo`, carries that one instead, either way. Keep the top centre of every header clear for it always: `mark_box(p)` is the box, two units more all round. Where a design draws round it, a band parting either side of it, ask `marked` whether it is there.

And to the kit's standard:

- every phone scene is built to the room its words leave;
- footers are never bare;
- every element shows the material;
- nothing touches a word, with two units clear;
- ordinary content fits the budget at full weight with its motion and about 1.5 KB to spare;
- content drawn lighter keeps every piece and its motion.

---

## 🔍 Reviewing a collection

Look at a design the way a reader meets it, and always beside the others:

1. **The year at 1x.** Every design's H1, then H2 and H3, side by side, by day and by night, at the size a README shows them.
2. **The calendar.** The H1s at about 310 pixels, the size the collection's page shows the year.
3. **A phone.** Each header at 360 pixels.

Ask two questions of every design:

- What would make someone stop scrolling?
- Which design is now the weakest of the twelve?

Fix the weakest first, and keep passing until no design stands out as weaker, louder, paler or darker than its year. Then run the hand's check over all twelve; the suite runs it too.

---

## 🚢 Shipping a collection

A collection ships whole. A page can pick it only once all twelve designs are drawn and pass their tests and their hand.

1. **Redraw the themes page.** `make themes` draws the themes page, which shows the collection's year and gives it its own page beside it.
2. **Check the year.** Draw the collection's page with `build-collection.py` and look at all twelve months on both grounds.
3. **Release.** Cut a minor release.

---

## ✅ Checklist

- [ ] The hand is in `HANDS` before the first design: inks, bands, flame, moon, skin, glint, mark and the marks' names.
- [ ] Every design subclasses `CollectionSet` and passes `check`.
- [ ] Every design was reviewed at 1x beside the other eleven, by day and by night, wide and on a phone.
- [ ] No design is the weakest of its year.
- [ ] `make lint` and `make test` pass, and `make themes` has been run.

<div align="center">

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
