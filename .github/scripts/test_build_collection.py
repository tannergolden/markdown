#!/usr/bin/env python3
"""Tests for the collection page builder.

WHY THIS EXISTS. A collection's page is drawn rarely, by hand or by `make
themes` once all twelve of its designs are drawn, so a broken path or a stale
template would only show up as a blank picture nobody re-checks. These tests
draw a stand-in collection with two of its designs drawn, borrowing two that
are, and hold the page to what it reads and what a committed file must be.

Run it:

    python3 .github/scripts/test_build_collection.py
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import pathlib
import re
import tempfile
import unittest
from unittest import mock

SCRIPT = pathlib.Path(__file__).resolve().parent / 'build-collection.py'
_spec = importlib.util.spec_from_file_location('build_collection', SCRIPT)
builder = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(builder)
C = builder.collections

DRAWN = [k for c in C.COLLECTIONS.values() for k in c.keys if C.is_drawn(k)]
PACKAGE = C.package


def stand_in(drawn: int):
    """Patches that make `standin` a collection of twelve with its first `drawn` designs drawn, each borrowing a
    design that is."""
    keys = [f'standin-{m.lower()}' for m in C.MONTHS]
    names = [f'Design {i + 1}' for i in range(12)]
    borrowed = {k: DRAWN[i % len(DRAWN)] for i, k in enumerate(keys[:drawn])}
    designs = tuple(zip(keys, names))
    return [mock.patch.object(C, 'COLLECTIONS', {'standin': C.Collection('standin', 'Stand-in', designs)}),
            mock.patch.object(C, 'package', lambda k: PACKAGE(borrowed[k]) if k in borrowed else PACKAGE(k))]


def manifest_of(page: str) -> dict:
    return json.loads(re.search(r'<script type="application/json" id="manifest">(.*?)</script>', page, re.S)[1])


class Draft(unittest.TestCase):
    def setUp(self):
        for p in stand_in(2):
            p.start()
            self.addCleanup(p.stop)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = pathlib.Path(self.tmp.name) / 'standin'

    def build(self, **kw) -> dict:
        with contextlib.redirect_stdout(io.StringIO()):
            return builder.build('standin', self.out, **kw)

    def test_a_draft_draws_its_drawn_months_and_marks_the_rest(self):
        manifest = self.build(draft=True)
        page = (self.out / 'index.html').read_text(encoding='utf-8')
        self.assertTrue(page.startswith('<!doctype html>'))
        self.assertIn(builder.MARK, page)
        self.assertNotRegex(page, r'__[A-Z]+__')
        self.assertEqual(manifest_of(page)['months'], manifest['months'])
        months = manifest['months']
        self.assertEqual([m['month'] for m in months], list(C.MONTHS))
        self.assertEqual([m['drawn'] for m in months], [True, True] + [False] * 10)
        self.assertEqual((manifest['drawn'], manifest['draft']), (2, True))
        self.assertEqual([m['sign'] for m in months[:2]], ['aquarius', 'pisces'], "each month's own sign to suggest")
        for m in months[:2]:
            self.assertEqual(m['use'], f"theme: {m['key']}")
            self.assertTrue(m['sections'])
            for path in builder.TS.paths(m) + list(m['hero'].values()):
                self.assertTrue((self.out / path).is_file(), path)

    def test_a_page_of_files_reads_each_drawing_from_beside_it(self):
        manifest = self.build(draft=True)
        page = (self.out / 'index.html').read_text(encoding='utf-8')
        self.assertEqual(manifest['payload'], 'files')
        self.assertEqual(json.loads(re.search(r'<script type="application/json" id="first">(.*?)</script>',
                                              page, re.S)[1]), {})
        # No design rides in the page itself, so its script takes a first design only when there is one, points
        # each picture at the file beside the page, and never fetches a design's bundle.
        self.assertIn('if (first.key) {', page)
        self.assertIn('if (M.payload === "files") return path;', page)
        self.assertIn('if (M.payload === "files" || loaded.has(key)) return;', page)

    def test_each_design_is_drawn_as_its_months_design_so_its_headers_carry_the_mark(self):
        asked, drawn_by = [], C.drawn_by
        with mock.patch.object(C, 'drawn_by', lambda key: asked.append(key) or drawn_by(key)):
            self.build(draft=True)
        self.assertIn('standin-january:2026-01-01', asked)
        self.assertIn('standin-february:2026-02-01', asked)
        self.assertFalse([k for k in asked if ':' in k and not k.startswith(('standin-january:2026-01-01',
                                                                               'standin-february:2026-02-01'))])

    def test_a_collection_still_being_drawn_is_drawn_only_as_a_draft(self):
        with self.assertRaises(SystemExit) as caught:
            self.build()
        self.assertIn('standin is a collection still being drawn, with 2 of its 12 designs done', str(caught.exception))

    def test_a_bundle_carries_each_drawn_design_in_its_own_file(self):
        manifest = self.build(draft=True, bundle=True)
        page = (self.out / 'index.html').read_text(encoding='utf-8')
        self.assertFalse(page.startswith('<!doctype html>'))
        for m in manifest['months'][:2]:
            files = json.loads((self.out / 'themes' / f"{m['key']}.json").read_text(encoding='utf-8'))
            self.assertEqual(set(files), set(builder.TS.paths(m)))
        self.assertEqual(sorted(p.name for p in (self.out / 'themes').iterdir()),
                         sorted(f"{m['key']}.json" for m in manifest['months'][:2]))

    def test_a_folder_holding_something_else_is_never_emptied(self):
        self.out.mkdir(parents=True)
        (self.out / 'keep.txt').write_text('mine', encoding='utf-8')
        with self.assertRaises(SystemExit):
            self.build(draft=True)
        self.assertTrue((self.out / 'keep.txt').is_file())


if __name__ == '__main__':
    unittest.main()
