# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""A holiday set: the layouts every set shares, and the hooks each one draws its own art in.

`Holiday` lays out every file the kit draws in a set: the headers, footers
and link buttons (`banners`), the six elements (`elements`) and the badges
(`badges`). A set is a subclass that overrides the drawing hooks below: its
colours (`ink`), its paper and sky, its frame and garland, how its titles are
lettered, the scenes its headers stand on and the ornaments of its footers,
elements and badges. The kit calls the entry points at the bottom, with the
same content and theme it hands a print, and gets finished SVGs back.
"""
from __future__ import annotations

from ... import KIT, KIT_VERSION
from ...canvas import BUDGET
from ..pixel import Pix
from .badges import Badges
from .banners import NARROW, WIDE, Banners
from .elements import Elements

__all__ = ["Holiday", "NARROW", "WIDE"]


class Holiday(Banners, Elements, Badges):
    """One holiday's set. Subclasses override the hooks; the layouts are shared."""
    key = ""          # the calendar's key: "halloween"
    name = ""         # "Halloween"
    tokens: frozenset = frozenset()   # every colour its files may use, upper-case #RRGGBB

    # ------------------------------------------------------------------------------------------ hooks
    def ink(self, night: bool) -> dict:
        """The colours text and rules take: title, shadow, body, muted, rule, accent, tag, tag_ink, fill,
        dim. Every text colour clears 4.5:1 on the paper by day and the sky by night."""
        raise NotImplementedError

    def lit(self, night: bool) -> dict:
        """How a title is lit: keyword arguments for `Pix.text` (bevel, glow, paint, night)."""
        return {}

    def paper(self, p: Pix, night: bool, uid: str = "p"):
        """The ground a drawing sits on: the day paper, or the night sky."""
        raise NotImplementedError

    def bg_at(self, p: Pix, night: bool, y: int) -> str:
        """The colour behind row `y`: what a label's backing is filled with."""
        raise NotImplementedError

    def stars(self, p: Pix, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        """The night sky's stars, kept out of the boxes in `avoid`."""

    def sky(self, p: Pix, night: bool, y1: int, seed: int = 1, motion: bool = True, avoid=()):
        """The sheet behind a header: the paper, or by night the sky and its stars (half as many on a
        drawing made lighter to fit its budget)."""
        self.paper(p, night)
        if night:
            self.stars(p, 6, 16, p.w - 6, int(y1 * 0.7), n=p.w // (20 if p.lite else 10), seed=seed,
                       twinkling=motion, avoid=avoid)

    def frame(self, p: Pix, night: bool, webs: bool = False):
        """The sheet's border."""
        raise NotImplementedError

    def garland(self, p: Pix, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """What hangs across a header's top edge."""

    def tag(self, p: Pix, x, y, w, h, night):
        """The block a tag's letters and a note's number sit on."""
        raise NotImplementedError

    def title_text(self, p: Pix, x, y, s, night, scale) -> int:
        """A title, the way the set letters it. Returns its width."""
        k = self.ink(night)
        return p.text(x, y, s, k["title"], "57", scale, shadow=k["shadow"], **self.lit(night))

    def section_mark(self, p: Pix, x, y, night):
        """The small sprite after SECTION A-A under an H2's title."""

    def strip_mark(self, p: Pix, x, y, night):
        """The small sprite beside an H3's title."""

    def scene(self, design: str, p: Pix, rule: int, night: bool, motion: bool) -> list:
        """The scene a wide header stands on, its ground at `rule`. Returns the spans (x0, x1) of the rule
        it covers, which the rule's decoration leaves alone."""
        return []

    def scene_narrow(self, design: str, p: Pix, y: int, night: bool):
        """The scene of a phone's header: H1's stands on the rule at `y`; H2's goes beside SECTION A-A at
        `y`; H3's beside the title's foot at `y`."""

    def rule_decor(self, p: Pix, x0, x1, y, seed, night):
        """What lies on a header's rule where no scene stands."""

    def finish(self, p: Pix, night: bool):
        """The last pass over a finished drawing, like the light its lamps cast."""

    def footer_mark(self, p: Pix, x, y, night):
        """The ornament in the corner of a title block's notes."""

    def heart(self, p: Pix, x, y):
        """The heart in BUILT WITH (heart) BY."""
        raise NotImplementedError

    def bar(self, p: Pix, x0, y0, w, h, period=5):
        """The graphic scale's bar."""
        raise NotImplementedError

    def link_colours(self, night: bool) -> tuple:
        """A link button's face, edge, letters and the shade along its foot."""
        raise NotImplementedError

    def link_top(self, p: Pix, x0, x1, y, seed, night):
        """What lies along a link button's top edge."""

    def link_icon(self, index: int, night: bool, ink: str) -> tuple:
        """The sprite (rows, palette) at the start of the `index`-th link button."""
        raise NotImplementedError

    # ------------------------------------------------------------------------------------ drawing lighter
    _lite = False

    def canvas(self, w: int, h: int) -> Pix:
        """A new drawing, made lighter while a file is redrawn to fit its budget."""
        return Pix(w, h, lite=self._lite)

    def _finish(self, p: Pix, night: bool):
        if not p.lite:
            self.finish(p, night)

    def _fitted(self, draw, budget: int, *then) -> str:
        """`draw()`'s file, drawn again lighter if it comes out over `budget` bytes (a title without its
        glow or finish, no last pass of light, half the stars), and failing that each of `then` in turn,
        lighter too. The kit still checks what it gets, and draws the file itself if it is over."""
        svg = draw()
        if len(svg.encode("utf-8")) <= budget:
            return svg
        self._lite = True
        try:
            for again in (draw, *then):
                svg = again()
                if len(svg.encode("utf-8")) <= budget:
                    break
            return svg
        finally:
            self._lite = False

    # ------------------------------------------------------------------------------------ the entry points
    def stamp(self, what: str) -> str:
        return f"{KIT} v{KIT_VERSION} {self.key} {what}"

    def header(self, code: str, content, theme: dict, wide: bool, motion: bool) -> str:
        """One header file, H1, H2 or H3, as the kit names its variants."""
        night = bool(theme["dark"])
        what = f"{code} {theme['name']}" + ("" if wide else " narrow") + ("" if motion else " still")

        def draw(moving: bool) -> str:
            if wide:
                p = {"H1": self.h1, "H2": self.h2, "H3": self.h3}[code](content, night, moving)
            else:
                p = {"H1": self.h1_narrow, "H2": self.h2_narrow, "H3": self.h3_narrow}[code](content, night)
            return p.svg(content.spoken_title(), content.spoken(), still=not (wide and moving),
                         stamp=self.stamp(what))
        # A moving header that is still too heavy drawn lighter holds still: its motion is the last to go.
        return self._fitted(lambda: draw(motion), BUDGET["header"], *([lambda: draw(False)] if motion else []))

    def footer(self, code: str, content, theme: dict, wide: bool, motion: bool) -> str:
        """One footer file, F1 or F2. A footer holds still."""
        night = bool(theme["dark"])
        what = f"{code} {theme['name']}" + ("" if wide else " narrow") + ("" if motion else " still")

        def draw() -> str:
            if wide:
                p = {"F1": self.f1, "F2": self.f2}[code](content, night)
            else:
                p = {"F1": self.f1_narrow, "F2": self.f2_narrow}[code](content, night)
            return p.svg(content.get("closing") or "Footer", content.spoken(), still=True, stamp=self.stamp(what))
        return self._fitted(draw, BUDGET["footer"])

    def link(self, label: str, theme: dict, index: int = 0) -> str:
        """One link button under the footer."""
        p = self.link_button(label, index, bool(theme["dark"]))
        return p.svg(label, f"Link: {label}", still=True, stamp=self.stamp(f"link {theme['name']}"))

    def element(self, kind: str, d: dict, theme: dict, variant: str, height: int | None = None) -> str:
        """One element file in a kit variant (wide, narrow or half), from data whose title and description
        the kit has filled in. An element holds still."""
        title = str(d.get("title") or kind.capitalize())
        desc = str(d.get("desc") or title)

        def draw() -> str:
            p = self.draw_element(kind, d, bool(theme["dark"]), variant, height)
            return p.svg(title, desc, still=True, stamp=self.stamp(f"elements {kind} {variant} {theme['name']}"))
        return self._fitted(draw, BUDGET["card" if kind == "placard" else "sheet"])
