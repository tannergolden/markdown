<!--
title: '📄 ADR-0007: A COLLECTION IS DRAWN BY ONE HAND'
description: 'The twelve designs of a collection keep their own subjects and share one hand: the same light, inks, ground, flame, people, motion and the month''s mark, so the year reads as one artist''s work.'
tags: [adr, architecture, decisions, themes, collections, art-direction]
category: docs
status: 'Accepted'
date: '2026-10-08'
evidence: 'N/A'
-->

<div align="center">

# 📄 ADR-0007: A COLLECTION IS DRAWN BY ONE HAND

<a name="top"></a>

**The twelve designs of a collection keep their own subjects and share one hand: the same light, inks, ground, flame, people, motion and the month's mark, so the year reads as one artist's work.**

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

[ADR-0006](ADR-0006-A-Collection-Changes-With-The-Month.md) made a collection twelve designs a page moves through, a month at a time. The medieval collection was drawn design by design, each with its own subject and material: a longship under the aurora, the Lewis chessmen, an illuminated page, stained glass, a joust, a sea chart, a castle, a mosaic, a laboratory, the Bayeux tapestry, a smithy and a dragon's hoard.

Every design was good alone, but beside one another they read as an anthology rather than a year:

- one design's day ground was four times as saturated as the rest;
- two were near white and cold, while two were heavy and dark;
- one design's night was twice as light as the others';
- each had its own ink for words, its own firelight and its own timing.

Nothing but the layout said the twelve belonged together. The question was what a collection's designs must share so that a reader turning the year sees one artist's hand, while each month keeps its own world.

---

## 🚦 Decision Drivers

- **One artist**: a reader should feel the twelve were drawn by the same hand, in the same year, for the same calendar.
- **Twelve worlds**: each month keeps its subject, material, palette and mood. Cohesion must come from the hand, not from sameness.
- **Enforced, not hoped for**: the rules a computer can measure are tested, so a new design or a later pass cannot drift from them.
- **Every collection**: the same holds for every collection to come, not only the medieval one.

---

## 🏗️ Considered Options

1. **A style note** that designers read and reviewers check by eye.
2. **One palette and one frame** for all twelve designs.
3. **A shared hand in code**: the rules that make one artist's work, held by a class every design subclasses and by tests every design must pass, with each design free in everything else.

---

## ✅ Decision Outcome

**Chosen Option**: A shared hand in code

### Rationale for Selection

Every collection has a **hand**, in `src/domain/collections/hand.py`, and every design of the collection subclasses `CollectionSet`, which carries it. The hand fixes what one artist would keep the same from page to page:

- **The light.** One lamp, up and to the left and toward the viewer, and seven-tone ramps whose shadows lean purple and whose lights lean gold, from the pixel engine. Outlines are the darkest tone of each material's own ramp, never pure black.
- **The words.** Every design sets its words in the hand's two inks, the same in all twelve, by day and by night. Titles, labels and accents keep the design's own materials.
- **The ground.** The sheet behind the words falls in the hand's band of lightness and colour, by day and by night, so no month glares or sinks beside the others. A month's mood lives in its hue, not in glare. A ground with almost no colour leans warm, never a cold white.
- **The lights.** Every flame burns on the hand's flame ramp, and the moon is the hand's.
- **The people.** Faces and hands are drawn to one canon, their skin on the hand's ramps, whatever the art form.
- **The motion.** Titles glint on the hand's period. Flames flicker and stars twinkle on the engine's cadences, figures idle in short loops, and ambient sweeps are slow.
- **The month's mark.** On a page that follows the collection's calendar, the hand draws the month's mark in the same place at the top centre of every header. The medieval hand's mark is the month's sign of the zodiac in a gold roundel on lapis, the device medieval calendars used. The mark belongs to the calendar: a page that keeps one design all year, as `theme: medieval-forge` does, is drawn without it. A page may choose one of the hand's twelve marks for itself, `sign: leo`, and every header then carries that one all year, on the calendar in place of the month's and on a design kept all year.

What the hand does not fix stays the design's own: its subject, scene, frame, title material, top band, palette within the bands, footers, links, badges and elements.

`check(design)` in the same module lists, in words, how a design breaks its hand. The tests run it over every drawn design of every collection, so a design that sets its words in another ink, or a ground that glares, fails the suite.

---

## 📈 Consequence Matrix

| Category         | Impact / Consequence |
| :--------------- | :------------------- |
| **Positive (+)** | The twelve designs of a collection read as one artist's year, and the tests keep them that way through every later pass. A new collection starts from a hand rather than from twelve blank pages. |
| **Negative (-)** | A design gives up some freedom: its body ink, the brightness of its ground and the colour of its fire are no longer its own. A new collection must define its hand, including its month's mark, before its first design is drawn. |
| **Neutral (~)**  | Holiday sets are not collections and keep their own hands. |

---

## ⚖️ Trade-off Comparative

### Option A: A style note

- ✅ No code, and full freedom for each design.
- ❌ Nothing holds a later pass to it, and the drift this decision answers grew under review by eye.

### Option B: One palette and one frame

- ✅ Unmistakably one set.
- ❌ Twelve months in one palette lose the year: winter and August, ivory and gold, all look alike.

### Option C: A shared hand in code

- ✅ One artist's hand, measured and tested, with twelve different worlds.
- ❌ The rules that cannot be measured, like the people's canon, still need review by eye.

---

## 🔗 Traceability & Links

- [ADR-0006](ADR-0006-A-Collection-Changes-With-The-Month.md): the collections and the month rule.
- [Drawing a collection](../technical/Collections.md): how a collection is drawn, from its hand to its twelfth design.

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
