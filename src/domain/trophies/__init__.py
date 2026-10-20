# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The trophy case: trophies and achievements a profile or a repository earns for itself.

  catalogue     what a case can hold, in both modes: eight core trophies and a
                hundred achievements each, with the tier and rarity rules
  calibration   where every threshold sits against real GitHub data
  calendar      streaks, weeks, months and years over the days someone was active
  scan          what a commit says about its author: conventional, signed, at 3 a.m.
  ledger        what GitHub cannot say again later: when a tier was first
                reached, a sparse history of the core values, the scanner's cache
  text          outlined lettering on the kit's shared glyphs
  art, styles   the cards (crest, trophy, medallion, crystal, plaque), the
                achievement pins, and the level and next-up cards
  prints        the same, drawn on a print's drafting paper
  looks         which look a case is drawn in: the standard one, a print's, or a
                pixel set's (`holidays.designs.trophies`)
  block         the README block: the cards, then the achievements by group
  plan          one measurement to every file, the block, and what the commit says
  settings      the `trophies:` section of the settings
  sample        made-up measurements for previews and the tests
  catalogue_md  docs/references/Catalogue.md, written from the catalogue

A case is drawn in the page's theme, as every part is: its five styles are
the standard theme's, a print draws them on its drafting paper, and a
holiday's set or a collection's design strikes them in its pixels. Each look
keeps the style, the sizes and the words, and `look: standard` in the
settings keeps the standard look in every theme.
"""
