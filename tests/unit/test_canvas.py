# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
import unittest

from tests import support

from domain import KIT, KIT_VERSION, draw
from domain.canvas import BUDGET, Canvas, c, lint


def clean() -> str:
    cv = Canvas(200, 40, title="A title", desc="A description.", stamp="test")
    cid = draw.clip_rect(cv, 0, 0, 200, 40, 4)
    cv.add(f'<g clip-path="url(#{cid})"><rect width="200" height="40" fill="{c("navy")}"/>'
           + cv.L.text("HELLO", face="meta", size=14, x=10, y=26, fill=c("white")) + "</g>",
           draw.icon("star", 170, 8, 24, "amber"))
    return cv.svg()


class CanvasTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        support.install()

    def test_a_clean_file_passes(self):
        self.assertEqual(lint(clean(), budget=BUDGET["header"]), [])

    def test_the_file_is_stamped_with_the_kit(self):
        self.assertIn(f"<!--{KIT} v{KIT_VERSION} test-->", clean())

    def test_ids_never_read_as_colours(self):
        cv = Canvas(10, 10, title="t", desc="d", stamp="s")
        self.assertTrue(all(cv.uid().startswith("k") for _ in range(20)))

    def assertFinds(self, svg: str, words: str, budget: int = BUDGET["header"]):
        problems = lint(svg, budget=budget)
        self.assertTrue(any(words in p for p in problems), problems)

    def test_refuses_a_script(self):
        self.assertFinds(clean().replace("</svg>", "<script>x()</script></svg>"), "contains <script")

    def test_refuses_an_outside_reference(self):
        self.assertFinds(clean().replace("</svg>", '<use href="https://x.test/a.svg#b"/></svg>'), "outside the file")

    def test_refuses_a_colour_that_is_not_a_token(self):
        self.assertFinds(clean().replace("</svg>", '<rect fill="#123456"/></svg>'), "#123456 is not a palette token")

    def test_refuses_a_named_colour(self):
        self.assertFinds(clean().replace("</svg>", '<rect fill="red"/></svg>'), "fill 'red' is not a token")

    def test_allows_smil_fill_freeze(self):
        svg = clean().replace("</svg>", '<animate attributeName="opacity" to="1" dur="1s" fill="freeze"/></svg>')
        self.assertEqual(lint(svg, budget=BUDGET["header"]), [])

    def test_refuses_text_elements(self):
        self.assertFinds(clean().replace("</svg>", "<text>hi</text></svg>"), "text not drawn as paths")
        svg = clean().replace("</svg>", "<text>hi</text></svg>")
        self.assertFalse(any("text" in p for p in lint(svg, budget=BUDGET["header"], text_ok=True)))

    def test_refuses_an_em_dash(self):
        self.assertFinds(clean().replace("A title", "A \u2014 title"), "dash")

    def test_refuses_a_missing_title(self):
        self.assertFinds(clean().replace("A title", " "), "no title")

    def test_refuses_duplicate_and_dangling_ids(self):
        svg = clean().replace("</svg>", '<g id="kx"/><g id="kx"/><use href="#knowhere"/></svg>')
        problems = lint(svg, budget=BUDGET["header"])
        self.assertIn("duplicate ids", problems)
        self.assertIn("#knowhere is referenced but never defined", problems)

    def test_refuses_a_file_over_its_budget(self):
        self.assertFinds(clean(), "over the 100 budget", budget=100)


if __name__ == "__main__":
    unittest.main()
