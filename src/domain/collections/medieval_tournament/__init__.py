# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Tournament set: the lists in May, in silk, gold cord and plate.

Every sheet is cut from a pavilion's canvas, unbleached and sunlit by day in broad panels, every other one dyed
the livery's pale green and stitched at its seams, and by night the same canvas from inside, warm under the
lanterns hung along its ridge and falling to deep blue toward its hem. A striped tent pole stands down each side
with a gilt finial on its head and a guy rope beside it, and along a header's top hangs the valance, a band of
green silk under a gold cord, dagged in tongues of green and white with a gold fringe that ripples in the wind, its
dags pausing at the top centre where the month's mark hangs; by night a lantern of pierced brass hangs from it near
each pole, lit. Titles are letters of painted silk appliqued on the canvas and edged in gold cord, a gleam running
across them in a wide moving header. The design is drawn in the medieval collection's hand (`collections.hand`):
its words in the hand's inks, its canvas within the hand's grounds, its fires on the hand's flame and its people's
faces on the hand's skins.

An H1 is the joust at the moment of impact under the standard of the lists, which flies from its staff just under
the valance: two knights in plate under their crests on caparisoned horses, the near knight a third larger riding
before the tilt and the far one beyond it, higher and smaller, both lances couched and meeting over it, the near
knight's breaking on the far knight's shield in a burst of splinters that fly out in an arc while its coronel
spins away; the near knight rides under a gold lion's head with its mane and the far knight under a white swan, his
horse and caparison shown beyond the near horse's head, the flash breaking round him. Where the words leave the slot
wide the joust spreads along the tilt, torches along it and the knights' pavilions standing back at its far end;
at the other side the stand rises in two tiers under a canopy striped green and white, a banner on each outer post
and the knights' shields along its front, ladies in their hennins and veils and lords in their bright dress, one
lady waving her favour, and the herald before it with his trumpet raised and its banner hanging. By night the
torches burn, their light glints along the plate, the strike throws sparks, the pavilions glow from within and the
lanterns along the stand's canopy light the faces under them. An H2 is the knights' camp: a great pavilion with a
lance and the knight's shield at each side of its door, the knight at rest before it with his squire holding his
lance, and beyond them the tree of shields, the shield last struck swinging on its strap, and the camp's pavilions
differing in size and state, one laced shut and one with its door looped wide on a knight being armed, his squire
setting the great helm on his head; by night the doors are lit from within. An H3 is the tiltyard, a knight running
at the quintain beside the rack of lances, or the crested helm on its post. On a phone the camp and the tiltyard
always stand under the words, across the phone at their full height in rows of their own on their own ground: the
camp beside the lists, the tilt running back to the standard of the lists and a knight's pavilion beyond it laced
shut, the knight at rest on his great horse with his squire holding his lance, and his great pavilion with a lance
at each side of its door; the tiltyard with a pavilion standing back, a knight on his great horse running at the
quintain, the rack of lances, the crested helm on its post and a torch. The marks beside a title are crested helms
with their mantling, and the counter-lists, an oak fence capped in gilt, run along every rule where no word lies
near. A footer stands on the tilt's barrier, which runs its whole width, its planking painted green and white
rising wherever the cells leave room and a post capped in gilt at every bay; at the corner of its notes the
herald's trumpet hangs on a pole with its banner, a lantern on the pole's head lit by night; and the design's mark,
a crested great helm with its mantling on a post, stands at the right end of a title block after the way back up
and in the scale bar's cell beside the bar. A link is a banneret on a lance.

The elements are the tournament's things: cards of painted silk edged in gold cord, each with a dagged band of its
tincture at its head and its icon on a heater shield, on wires of gold cord; upright lances for the histogram's
weeks; the quintain for the dial, its face the target painted in quarters, its hand a lance with its vamplate and
coronel, its hub the pivot on its post; the herald's score cheque for the counters; the tilt for the time line with
pennons for its releases and a crested helm at today; crested helms with their mantling for the roster (the quintain
for a bot); the prize for the seal, a jewelled circlet on a tasselled cushion of crimson velvet with the lady's
favour for its ribbon; and a proclamation board for a placard. A badge is silk with a gold cord along its top.
"""
from __future__ import annotations

from ...holidays.designs import WIDE
from ...holidays.designs.badges import inside
from ..hand import CollectionSet
from . import art as A
from .palette import C, RAMP, TOKENS, X, step

V, G, CV, DU = RAMP["vert"], RAMP["or"], RAMP["canvas"], RAMP["dusk"]


# The camp beyond the knight at rest on an H2, from him leftward as far as the words leave room: the tree of
# shields, then pavilions of the knights differing in size and state, each (state, tincture, width, height).
CAMP = (("tree", None, A.TREE_W, 50), ("arming", "azure", 31, 50), ("closed", "gules", 19, 30),
        ("open", "vert", 25, 42))
# The columns of an F2's scale cell the design's mark may stand in, beside the scale bar and short of the rule
# closing the cell; on a phone, the column it must end before, short of the way back up; and the row of the rule
# under a phone's scale bar, which its mark stands on.
SCALE_CELL = (69, 94)
PHONE_SCALE_CELL = 108
PHONE_SCALE_RULE = 34
# The sizes the design's mark is tried at in a footer, the largest first (see `art.HELMS`).
MARKS = ("L", "Ls", "M")


class Tournament(CollectionSet):
    collection = "medieval"
    key = "medieval-tournament"
    name = "Tournament"
    # What the design is, in words, for the page that shows the collection.
    tagline = (
        "The lists in May: a joust at the moment of impact before a stand of ladies and lords, in silk, gold cord and "
        "plate.")
    about = (
        "A tournament pitched on a pavilion's canvas: striped poles with gilt finials, a valance of green and white "
        "silk dags rippling along the top, and titles of painted silk edged in gold cord. The H1 is the joust at the "
        "moment of impact, the near knight under a gold lion's head charging the far knight under his swan, a lance "
        "breaking over the tilt in a burst of slivers as its coronel spins away. Across the lists the stand rises in "
        "two tiers under its striped canopy, ladies in hennins and veils and lords in bright dress watching, one "
        "waving her favour, the challengers' shields along its front and the herald before it with his trumpet "
        "raised. By night the torches burn, their light glints along the plate, the pavilions glow from within and "
        "the stand's lanterns light the faces under them. The H2 is the knights' camp, a knight at rest with his "
        "squire before his great pavilion, and beyond them a tree of shields and pavilions laced shut or open on a "
        "knight whose squire sets the great helm on his head. The H3 is the tiltyard, a knight running at the "
        "quintain beside the rack of lances. On a phone the camp and the tiltyard stand whole under the words, the "
        "knight on his great horse at rest before his pavilion beside the lists or charging the quintain. Footers "
        "stand on the tilt's barrier, the herald's trumpet and lantern at the corner of their notes and a crested "
        "great helm on its post at the right end and beside the scale bar; links are bannerets on lances, badges are "
        "painted silk edged in gold cord, and every element is made of the tournament's things, from silk cards on "
        "heraldic shields to the quintain for a dial and the prize circlet on its cushion for a seal.")
    tokens = frozenset(TOKENS)
    phone_scene_rows = 60   # a phone's lists: the joust between the stand and a pavilion, its notes set above

    # ---- colour and paper
    def ink(self, night):
        return dict(
            title=V[5] if night else V[2], shadow=DU[0] if night else CV[3],
            body=C["ink_n"] if night else C["ink"], muted=X["muted_night"] if night else X["muted_day"],
            rule=X["rule_night"] if night else X["rule_day"], accent=G[4] if night else X["accent_day"],
            tag=V[1], tag_ink=G[5],
            fill=C["fill_n"] if night else C["fill"], dim=X["dim_night"] if night else X["dim_day"],
        )

    def paper(self, p, night, uid="p"):
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        return A.bg_at(p, night, y)

    def stars(self, p, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        """The gold spangles on the canvas, fewer than the kit's stars."""
        A.stars(p, x0, y0, x1, y1, max(3, round(n * 0.45)), seed=seed, twinkling=twinkling, faint=faint, avoid=avoid)

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """A header's canvas, its spangles kept off the month's mark's box at its top centre."""
        super().sky(p, night, y1, seed=seed, motion=motion, avoid=(*avoid, A.mark_box(p)))

    def frame(self, p, night, webs=False):
        """The poles, their finials and ropes, and the hem; a header's valance is its garland's. A footer, the
        sheet the layout frames without webs on the banners' paper, stands on the tilt's rail."""
        A.frame(p, night, header=webs, footer=not webs and getattr(p, "sheet", "") == "p")

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """The valance along the header's top, between the finials."""
        A.valance(p, x0, x1, night, seed=seed)
        p.valanced = True

    def tag(self, p, x, y, w, h, night):
        """A block of dark green silk a tag's gold letters sit on, its upper edge catching the light. The ribbon
        under a certificate's seal, the one tag set low on its sheet, is the lady's favour of blue silk with its
        ends cut in forks, as long as its column has room for them."""
        if y >= 30 and h >= 9:
            p.rect(x, y, w, h, RAMP["azure"][1])
            p.hline(x, x + w, y, G[4])
            p.hline(x, x + w, y + h - 1, G[2])
            tail = min(4, x - 6, (100 if p.w == WIDE else 88) - 2 - (x + w))
            if tail >= 3:
                A.silk_ribbon(p, x, y, w, h, night, tail=tail)
            return
        p.rect(x, y, w, h, V[1])
        p.hline(x, x + w, y, V[3])
        p.hline(x, x + w, y + h - 1, V[0])

    def title_text(self, p, x, y, s, night, scale):
        return A.silk_title(p, x, y, s, night, scale, motion=p.w == WIDE)

    # ---- the headers' scenes
    @staticmethod
    def _room(p, x0, x1, g, most, least):
        """The rows free of words above the ground at row g between x0 and x1, `most` at the most, keeping three
        rows of margin above and two beside; None when fewer than `least` are free."""
        for room in range(most, least - 1, -1):
            if p.clear_of_words(x0 - 2, g - room - 3, x1 + 2, g + 3):
                return room
        return None

    @staticmethod
    def _stand_fit(p, x0, w, g):
        """The tiers and banners of the tallest stand `w` wide from x0 on the ground at row g that the words leave
        room for, two tiers before one and its banners before none; None when even the least does not fit."""
        for tiers, banners in ((2, True), (2, False), (1, True), (1, False)):
            top = g - A.stand_height(tiers, banners)
            if top >= A.VALANCE_FOOT + 2 and p.clear_of_words(x0 - 6, top - 2, x0 + w + 6, g + 3):
                return tiers, banners
        return None

    @staticmethod
    def _reach(p, x0, g, step=1, limit=None, rows=20):
        """How far right from x0 (or left, with a negative `step`) a band `rows` tall over the ground at row g runs
        clear of words, two units of margin kept; at most to `limit`."""
        x = x0
        while (limit is None or (x < limit if step > 0 else x > limit)) and \
                p.clear_of_words(x - 2, g - rows - 2, x + 3, g + 3):
            x += step
        return x

    def scene(self, design, p, rule, night, motion):
        g = rule - 1
        moving = motion
        spans = []
        if design == "H1":
            spans += self._lists(p, g, night, moving)
            spans += self._gallery(p, g, night, moving)
        elif design == "H2":
            spans += self._camp(p, g, night, moving)
        else:
            spans += self._yard(p, g, night, moving)
        return spans

    def _camp(self, p, g, night, moving):
        """The right of an H2, the knights' camp: a great pavilion with its pennon, its door drawn wide and lit from
        within by night, a lance planted at each side of it with a pennon at its head and the knight's shield hung
        on it; before it the knight at rest on his horse, a third larger where the rows allow, his squire at his
        horse's head holding his lance (a middling knight holds his own); and where the words leave the ground
        further left, the camp beyond, standing back, as far as it runs: the tree of shields, then pavilions
        differing in size and state (`CAMP`), one with its door looped wide on a knight being armed where its wall
        is tall enough for him, one laced shut."""
        room = self._room(p, 306, 411, g, min(80, g - 16), 40)
        if not room:
            return []
        great = room >= 58 and self._room(p, 306, 411, g, 58, 58)
        x0 = 305
        left = self._reach(p, x0 - 1, g, step=-1, limit=150, rows=min(room, 46))
        for i, (state, tinc, w, h) in enumerate(CAMP):
            cx = x0 - 5 - w // 2
            back = cx - w // 2 - 1 >= left and self._room(p, cx - w // 2 - 1, cx + w // 2 + 2, g,
                                                          min(h + 13, g - 16), 34)
            if not back:
                break
            if state == "tree":
                if back < h + 1:
                    break
                A.shield_tree(p, cx, g - 3, night, motion=moving, h=h, seed=50)
            else:
                ph = min(h, back - 13)
                A.pavilion(p, cx, g - 3, night, tinc, w=w, h=ph, motion=moving, phase=i + 2, seed=30 + i, far=True,
                           state=state if state != "arming" or ph >= 48 else "open")
            x0 = cx - w // 2 - 1
        A.ground(p, x0, 411, g - 3, g, night, uid="gd3")
        if room >= 48:
            h = min(64, room - 14)
            A.pavilion(p, 389, g - 3, night, "purpure", w=39, h=h, motion=moving, phase=1, seed=6, great=True)
            A.door_lances(p, 389, g - 2, g - 3 - round(h * 0.48) - 9, "stag", night, motion=moving)
        if great:
            A.squire(p, 307, g - 1, "stag", night, motion=moving)
            A.knight_at_rest(p, 320, g - 1, "stag", night, motion=moving, size="L")
        else:
            A.knight_at_rest(p, 318, g - 2, "stag", night, motion=moving)
        return [(x0 - 1, 412)]

    def _yard(self, p, g, night, moving):
        """The right of an H3, the tiltyard: where the words leave room enough, a knight running at the quintain
        with pavilions standing back beyond him as far as the room runs, no two alike in size or state, and where
        less the quintain alone, with the rack of lances beyond it and by night a torch at the rack. When the title
        is too long for the crested helm beside it, the helm stands on its post in the quintain's place."""
        room = self._room(p, 351, 411, g, min(60, g - 16), 38)
        if not room:
            return []
        helm = not getattr(p, "marked", False)
        left = self._reach(p, 350, g, step=-1, limit=150, rows=38)
        x0 = 309 if not helm and left <= 309 else 349
        for i, cx in enumerate(range(x0 - 20, left + 16, -40) if x0 < 349 else ()):
            back = self._room(p, cx - 15, cx + 15, g, min(48, g - 16), 34)
            if not back:
                break
            A.pavilion(p, cx, g - 3, night, ("gules", "vert", "azure", "purpure")[i % 4], w=(27, 19, 25, 21)[i % 4],
                       h=min(34, back - 13) - (0, 8, 3, 5)[i % 4], motion=moving, phase=i + 1, seed=40 + i, far=True,
                       state=("open", "closed", "open", "closed")[i % 4])
            x0 = cx - 16
        A.ground(p, x0, 411, g - 3, g, night, uid="gd4")
        if helm:
            A.helm_stand(p, 358, g - 2, "lion", night)
        elif x0 < 349:
            A.tilting(p, 312, g - 2, night, motion=moving)
        else:
            A.quintain_post(p, 353, g - 2, night, motion=moving)
        A.lance_rack(p, 388, g - 2, night, h=room - 2)
        if night:
            A.torch(p, 403, g - 2, night, h=22, phase=2)
        return [(x0 - 1, 412)]

    @staticmethod
    def _stage(p, x0, g, layouts, reach):
        """The first staging of the joust among `layouts` whose every cell keeps two units clear of every word from x0
        on the ground at row g: (layout, width, how far ahead the far knight rides), or Nones. A spread one runs as
        far as `reach`; a diagonal one sends its far knight as far ahead as the words let him."""
        def clear(layout, width, ahead=None):
            return all(p.clear_of_words(x - 2, y - 2, x + 3, y + 3) for x, y in A.joust_cells(p, layout, x0, g, width,
                                                                                               ahead))
        for layout in layouts:
            least = A.LAYOUTS[layout][7]
            if layout == "spread":
                if reach >= least and clear(layout, min(190, reach)):
                    return layout, min(190, reach), None
            elif layout in ("rising", "diagonal"):
                cover = 27 if layout == "diagonal" else 26
                for ahead in range(A.LAYOUTS[layout][3], 20 if layout == "diagonal" else 24, -2):
                    if clear(layout, max(least, ahead + cover), ahead):
                        return layout, max(least, ahead + cover), ahead
            elif clear(layout, least):
                return layout, least, None
        return None, 0, None

    def _lists(self, p, g, night, moving):
        """The left of an H1, the lists: the joust at the moment of impact, as large as the words leave it room to
        be, under the standard of the lists flying from just under the valance on its staff at the slot's edge, the
        staff's cresset burning by night to light the knights' plate. Spread out along the tilt where its slot is
        wide, the near knight a third larger and the two a lance's length apart, torches along the tilt and its
        knights' pavilions standing back at its far end, no two alike in size or state; rising where it is
        narrower, the near knight large below and the far one middling, higher beyond the tilt; on the diagonal
        where it is narrower still, the far knight small and high over his horse's head; or middling, the tilt
        running on along the foot as far as the words leave it."""
        reach = self._reach(p, 5, g, limit=240, rows=A.LAYOUTS["spread"][6]) - 6
        layout, width, ahead = self._stage(p, 4, g, ("spread", "rising", "diagonal", "middling"), reach)
        if not layout:
            return []
        top = g - A.LAYOUTS[layout][5]
        if layout != "middling":
            fly = self._reach(p, 8, A.HANG_TOP + 22, limit=60, rows=14) - 10
            A.lists_standard(p, 6, g - 10, A.VALANCE_FOOT + 4, night, motion=moving, w=max(24, min(44, fly)))
        if layout == "spread":
            busy = A.joust_cells(p, layout, 4, g, width)
            for i, cx in enumerate(range(4 + width - 16, 100, -30)):
                back = self._room(p, cx - 14, cx + 14, top, min(42, top - 16), 30)
                if not back or any(abs(x - cx) < 17 and y < top - 2 for x, y in busy):
                    break
                A.pavilion(p, cx, top, night, ("azure", "vert", "gules")[i % 3], w=(25, 19, 23)[i % 3],
                           h=min(30, back - 13) - (0, 8, 3)[i % 3], motion=moving, phase=i + 1, seed=20 + i, far=True,
                           state=("open", "closed", "open")[i % 3])
        span = A.joust(p, 4, g, night, motion=moving, layout=layout, width=width, reach=ahead)
        if layout == "spread":
            for i, tx in enumerate(range(4 + width - 34, 100, -34)):
                A.torch(p, tx, top + 1, night, h=17, phase=i + 1, reach=24)
        spans = [span]
        if layout == "middling":
            end = self._reach(p, 59, g, limit=200, rows=27)
            if end > 76:
                A.tilt(p, 58, end - 2, g - 15, g - 3, night, uid="tl2")
                A.ground(p, 58, end - 2, g - 3, g, night, uid="gd2")
                for i, tx in enumerate(range(68, end - 8, 42)):
                    A.torch(p, tx, g - 9, night, h=16, phase=i)
                spans.append((57, end - 1))
        return spans

    def _gallery(self, p, g, night, moving):
        """The right of an H1: the stand with its ladies and lords, in two tiers under its canopy with a banner on
        each of its outer posts where the rows allow and one tier where they are fewer, as wide as the words leave it;
        and the herald before it with his trumpet raised toward the lists, its banner hanging, standing further in
        front of the stand's corner where the words come close to it."""
        spans = []
        for tiers, banners in ((2, True), (2, False), (1, True), (1, False)):
            top = g - A.stand_height(tiers, banners)
            if top < A.VALANCE_FOOT + 2:
                continue
            x0 = next((x for x in range(356, 372) if p.clear_of_words(x - 6, top - 2, 412, g + 3)), None)
            if x0 is not None:
                break
        else:
            return spans
        w = min(A.STAND_W, 406 - x0)
        spans.append(A.stand(p, x0, g, night, motion=moving, w=w, tiers=tiers, banners=banners))
        hx = next((x for x in range(x0 - 27, x0 - 6) if self._clear(p, A.HERALD, x, g - len(A.HERALD))), None)
        if hx is not None:
            A.herald(p, hx, g, night)
            spans.append((hx - 1, hx + 26))
        return spans

    @staticmethod
    def _clear(p, art, x, top, margin=2):
        """Whether every pixel of `art` set with its top-left at (x, top) keeps `margin` units from every word."""
        return all(p.clear_of_words(x + i - margin, top + j - margin, x + i + margin + 1, top + j + margin + 1)
                   for j, row in enumerate(art) for i, ch in enumerate(row) if ch != ".")

    def scene_narrow(self, design, p, y, night):
        """A phone's H1 scene, built to the rows its words leave free: the lists across the band under the words,
        the stand at the left in as many tiers as the rows allow, the joust in the middle and a pavilion at the
        right, the tilt running under them, or where the rows are fewer the small joust on the tilt, between two
        pavilions where they stand. A phone's H2 and H3 stand their heroes under their words instead, the camp and
        the tiltyard at their full height (see `scene_under`)."""
        if design == "H1":
            g = y - 1
            room = self._room(p, 5, 175, g, 64, A.LAYOUTS["compact"][6])
            if not room:
                return
            p.held = [(4, 176)]
            if room >= 44:
                layout = "diagonal" if room >= A.LAYOUTS["diagonal"][6] + 3 else "middling"
                ttop = A.LAYOUTS[layout][5]
                A.tilt(p, 5, 175, g - ttop, g - 3, night, uid="tl5")
                A.ground(p, 5, 175, g - 3, g, night, uid="gd5")
                fit = self._stand_fit(p, 9, 40, g)
                if fit:
                    A.stand(p, 9, g, night, motion=False, w=40, seed=1, tiers=fit[0], banners=fit[1])
                elif self._room(p, 12, 41, g, 50, 34):
                    A.pavilion(p, 26, g - 3, night, "azure", w=27, h=min(50, room - 14), motion=False, seed=8)
                A.joust(p, 56 if layout == "diagonal" else 61, g, night, motion=False, layout=layout, uid="tl6")
                A.pavilion(p, 150, g - 3, night, "purpure", w=33, h=min(50, room - 14), motion=False, seed=7)
            else:
                A.tilt(p, 5, 175, g - A.LAYOUTS["compact"][5], g - 3, night, uid="tl5")
                A.ground(p, 5, 175, g - 3, g, night, uid="gd5")
                if room >= 36:
                    A.pavilion(p, 22, g - 3, night, "purpure", w=25, h=room - 14, motion=False, seed=7)
                    A.pavilion(p, 158, g - 3, night, "azure", w=25, h=room - 14, motion=False, seed=8)
                A.joust(p, 66, g, night, motion=False, layout="compact", uid="tl6")

    # ---- a phone's heroes under its words
    PHONE_ROWS = {"H2": 58, "H3": 48}   # the rows the camp and the tiltyard take under a phone's words
    _under = None                       # the header being laid out with those rows

    def h2_narrow(self, h, night):
        """A phone's H2, laid out with rows under its words for the knights' camp at its full height (see
        `phone_rows`): beside the words the camp could stand only a pavilion tall, so it always stands under them."""
        return self._phone("H2", super().h2_narrow, h, night)

    def h3_narrow(self, h, night):
        """A phone's H3, laid out with rows under its words for the tiltyard at its full height (see
        `phone_rows`)."""
        return self._phone("H3", super().h3_narrow, h, night)

    def _phone(self, design, draw, h, night):
        """A phone's `design` header drawn by `draw` with the rows under its words that `phone_rows` gives it."""
        self._under = design
        try:
            return draw(h, night)
        finally:
            self._under = None

    def phone_rows(self, design, title_w):
        """The rows a phone's H2 or H3 leaves under its words for its hero, whatever its title: as many as the camp
        or the tiltyard needs (see `PHONE_ROWS`)."""
        return self.PHONE_ROWS[design] if self._under == design else 0

    def scene_under(self, design, p, y0, y1, night):
        """The hero under a phone's words, from the last of them at row y0 to the rule at y1, on its own ground
        across the phone: on an H2 the knights' camp (`_camp_under`), on an H3 the tiltyard (`_yard_under`). Its
        ground runs the width of the phone, so no counter-lists run along the rule under it."""
        g = y1 - 1
        p.held = [(4, 176)]
        A.ground(p, 5, 175, g - 3, g, night, uid="gd9")
        if design == "H2":
            self._camp_under(p, y0, g, night)
        else:
            self._yard_under(p, y0, g, night)

    @staticmethod
    def _camp_under(p, y0, g, night):
        """The knights' camp across a phone on the ground over row g, at its full height under the words that end
        at row y0: at the left the lists, the tilt running back to the standard of the lists on its tall staff and
        a knight's pavilion standing beyond it, laced shut; before them the knight at rest on his great horse, his
        squire at his horse's head holding his lance with its pennon; and at the right his great pavilion, its door
        drawn wide between a lance at each side with his shield hung on it. By night its door is lit from within,
        the pavilion beyond the lists glows and the standard's cresset burns."""
        top = y0 - 1
        A.pavilion(p, 44, g - 3, night, "vert", w=25, h=34, motion=False, phase=2, seed=31, far=True,
                   state="closed")
        A.lists_standard(p, 8, g - 3, top + 3, night, motion=False, w=36)
        A.tilt(p, 5, 66, g - 17, g - 3, night, uid="tl9")
        A.squire(p, 62, g - 1, "stag", night, motion=False)
        A.knight_at_rest(p, 75, g - 1, "stag", night, motion=False, size="L")
        h = min(50, g - 14 - top)
        A.pavilion(p, 152, g - 3, night, "purpure", w=39, h=h, motion=False, phase=1, seed=32, great=True)
        A.door_lances(p, 152, g - 2, g - 3 - round(h * 0.48) - 9, "stag", night, motion=False)

    @staticmethod
    def _yard_under(p, y0, g, night):
        """The tiltyard across a phone on the ground over row g, at its full height under the words that end at
        row y0: a pavilion standing back, a knight on his great horse running at the quintain, his couched lance
        striking its shield, the rack of lances and the crested helm on its post, and a torch at the end, cold by
        day and burning by night."""
        A.pavilion(p, 18, g - 3, night, "gules", w=23, h=34, motion=False, phase=1, seed=41, far=True)
        A.tilting(p, 24, g - 2, night, motion=False, size="L")
        A.lance_rack(p, 118, g - 2, night, h=44)
        A.helm_stand(p, 139, g - 2, "lion", night)
        A.torch(p, 167, g - 2, night, h=24, phase=2)

    def section_mark(self, p, x, y, night):
        """A small crested helm with the stag for its crest beside SECTION A-A, from a row above the words to four
        under them: two clear of the title's foot above and of the tagline below."""
        A.crested_helm(p, x, y - 1, "stag", night, "purpure", "or", "X")

    def strip_mark(self, p, x, y, night):
        """A crested great helm with its mantling beside a strip's title."""
        A.crested_helm(p, x, y - 12, "lion", night, "gules", "or", "L")
        p.marked = True

    def rule_decor(self, p, x0, x1, y, seed, night):
        """The counter-lists along a rule: the low oak fence round the lists, its posts capped in gilt, kept two
        units from every word and off the ground a phone's scene stands on."""
        cuts = sorted(getattr(p, "held", ()))
        for a, b in cuts:
            if a > x0:
                A.counter_lists(p, x0, min(a, x1), y, night, seed=seed)
            x0 = max(x0, b)
        if x0 < x1:
            A.counter_lists(p, x0, x1, y, night, seed=seed)

    def finish(self, p, night):
        """The last pass: by night the lanterns hung from a header's valance, and the light of the torches, the
        lanterns and the pavilions on what stands near them; on an instruments sheet the dial's hand made a lance;
        and every label's backing lifted off the canvas."""
        if night and getattr(p, "valanced", False):
            A.hanging_lanterns(p)
        if night:
            A.firelight(p)
        if getattr(p, "dial", None):
            A.quintain_hand(p, night, self.ink(night)["accent"])
        A.lift_keys(p)

    def _finish(self, p, night):
        """The last pass, on a drawing made lighter to fit its budget as on any other: the lighter drawing keeps every
        light and every figure, thinning only the texture `finish` lays (see `finish`)."""
        self.finish(p, night)

    # ---- the elements
    def card_bevel(self, night):
        return (C["fill_n"], DU[1]) if night else (C["white"], CV[4])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A card as a banner of painted silk edged all round in gold cord, a dagged band of a tincture at its head
        and its icon worked in gold on a heater shield of the tincture."""
        A.silk_card(p, x, y, w, h, night, seed, self.ink(night)["body"], self.ink(night)["fill"])

    def wire_ink(self, night):
        return G[3] if not night else G[2]

    def wire_lights(self, p, cells, night, seed):
        """The wire as a gold cord, twisted, knotted where it bends."""
        A.cord_wire(p, cells, night)

    def dashes(self, night):
        return [V[3 if night else 2], G[4 if night else 3]]

    def ornament(self, kind, p, x, y, night):
        """A crested great helm with its mantling in a free corner of the schematic."""
        if kind == "schematic":
            if p is not None:
                A.crested_helm(p, x, y, "swan", night, "azure", "argent", "L")
            return (24, 24)
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as a tilting lance standing upright, a vamplate on it, in the tinctures by turns."""
        n = getattr(p, "bars", 0)
        p.bars = n + 1
        A.lance_bar(p, bx, base, bw, v, night, i=n)

    def peak_mark(self, p, x, y, night):
        """A pennon of gules flown beside the busiest week's count."""
        k = -1 if night else 0
        Gu = RAMP["gules"]
        p.vline(x, y - 1, y + 6, RAMP["wood"][4 + k])
        p.px(x, y - 2, G[6 + k])
        for dx in range(1, 5):
            for dy in range(0, 3 if dx < 4 else 2):
                p.px(x + dx, y + dy, Gu[3 + k] if dy < 2 else Gu[1 + k])

    def dial_ring(self, p, arc, night):
        """The dial as the quintain's target: a round shield painted in quarters of gules and argent, bound in an
        iron rim."""
        cx = (arc[0][0] + arc[-1][0]) / 2
        cy = arc[0][1]
        r = (arc[-1][0] - arc[0][0]) / 2 + 1.5
        p.dial = (cx, cy, r)
        A.quintain_ring(p, arc, night)

    def dial_tick(self, p, x, y, night):
        """A gold rivet in the target's iron rim."""
        p.px(x, y, G[5])
        p.px(x + 1, y + 1, G[2])

    def dial_hub(self, p, cx, cy, night):
        """The quintain's pivot on the head of its post: an iron cap on a gold collar, the post's oak head under
        it bound with an iron band."""
        from ...holidays.pixel import sphere
        k = -1 if night else 0
        for y in range(cy + 2, cy + 6):
            for i, xx in enumerate(range(cx - 2, cx + 3)):
                p.px(xx, y, A.S[2 + k] if y == cy + 4 else A.WD[(5, 4, 3, 3, 1)[i] + k])
        for i, xx in enumerate(range(cx - 4, cx + 5)):
            p.px(xx, cy + 2, G[5 + k] if i < 3 else G[4 + k] if i < 7 else G[2 + k])
        sphere(p, cx + 0.5, cy - 0.5, 3.2, RAMP["steel"], lo=1, hi=6)

    def material(self, i, xx, yy, y0, y1, lift, night):
        return A.material(i, xx, yy, y0, y1, lift, night)

    def counter_cell(self, q, ox, oy, night):
        A.cheque(q, ox, oy, night)

    def counter_ink(self, night, dim):
        """A numeral painted on the herald's cheque: in red ink by day, in gold by night; a leading nought fainter."""
        if night:
            return G[2] if dim else G[5]
        return CV[3] if dim else RAMP["gules"][1]

    def timeline_line(self, p, x0, x1, y, night):
        """The tilt the releases stand along, up to today."""
        if x1 - x0 >= 2:
            A.tilt_line(p, x0, x1, y, night)

    def release(self, p, x, gy, kind, night, i=0):
        A.release_pennon(p, x, gy, kind, night, i)

    def today_mark(self, p, x, y, night):
        """A crested great helm at today's end of the tilt, where the words leave it room, else a gilt finial."""
        if p.clear_of_words(x - 9, y - 21, x + 10, y + 2):
            A.today_helm(p, x, y, night)
        else:
            p.px(x, y - 1, G[6])
            p.px(x, y - 2, G[4])

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor as a crested great helm with its mantling in their own colours; a bot as the quintain."""
        A.knight_avatar(p, cx, cy, i, night, bot=not person.get("initials"))

    def commit_bar(self, p, x, y, w, fill, night):
        """A contributor's share as a tilting lance laid in its groove, painted in a spiral of gules and gold as far
        as their commits reach, the steel of its coronel at its head."""
        k = -1 if night else 0
        T = RAMP["gules"]
        p.box(x, y, w + 2, 4, RAMP["wood"][2 + k])
        p.hline(x + 1, x + w + 1, y + 1, RAMP["wood"][5 + k] if not night else DU[4])
        p.hline(x + 1, x + w + 1, y + 2, RAMP["wood"][4 + k] if not night else DU[3])
        for xx in range(x + 1, x + 1 + fill):
            u = xx - x
            p.px(xx, y + 1, G[5 + k] if ((u + 1) // 3) % 2 else T[4 + k])
            p.px(xx, y + 2, G[3 + k] if (u // 3) % 2 else T[2 + k])
        if fill >= 3:
            p.px(x + fill, y + 1, RAMP["steel"][5 + k])
            p.px(x + fill, y + 2, RAMP["steel"][3 + k])

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """The tourney's prize: a gold circlet on a cushion of crimson velvet with gold tassels."""
        A.cushion(p, cx, cy, r0, r1, night)

    def seal_mark(self, p, x, y, night):
        A.rose(p, x + 5, y, night)

    def placard_board(self, p, night):
        """A herald's proclamation board between its poles."""
        A.proclamation(p, night)

    def placard_mark(self, p, x, y, night):
        A.crested_helm(p, x - 2, y - 8, "stag", night, "purpure", "or", "S")

    def heart(self, p, x, y):
        R = RAMP["gules"]
        art = [".54.43.", "5443321", "4433221", ".33221.", "..221..", "...1..."]
        p.sprite(x, y, art, {str(i): R[i] for i in range(7)})

    def bar(self, p, x0, y0, w, h, period=5):
        """A tilting lance laid along the scale, gules and gold by turns."""
        A.scale_lance(p, x0, y0, w, h, period)

    # ---- the footers and links
    def footer_mark(self, p, x, y, night):
        """The herald's trumpet hung up on a pole with its banner at the corner of the closing notes, and a lantern on
        the pole's bracket, lit by night."""
        A.footer_mark(p, x, y, night)

    def _footed(self, p, night, helm=()):
        """A footer once its cells are laid: the tilt's barrier along its foot with its planking wherever they leave
        room, the herald's mark at the corner of the notes, the design's mark, the crested great helm on its post,
        where `helm` finds it room (see `art.footing`), and by night the lantern's light on what stands near it."""
        A.footing(p, night, self.ink(night)["rule"], helm)
        if night:
            A.firelight(p)
        return p

    @staticmethod
    def _after_words(p, foot):
        """Where a title block's right end begins, after the last of its words: two units on from the right edge of
        the rightmost word over the rows a helm on row `foot` stands in."""
        return max((b[2] for b in p.words if b[3] > foot - 36), default=4) + 2

    def f1(self, ft, night):
        """The title block, the design's mark at its right end after the way back up where the cells leave room."""
        p = super().f1(ft, night)
        return self._footed(p, night, [(self._after_words(p, p.h), p.w - 6, p.h, True, MARKS)])

    def f2(self, ft, night):
        """The scale bar, the design's mark in its cell beside the bar."""
        p = super().f2(ft, night)
        return self._footed(p, night, [(SCALE_CELL[0], SCALE_CELL[1], p.h, False, MARKS)])

    def f1_narrow(self, ft, night):
        """A phone's title block, the design's mark at its right end where the cells leave room; else, on a block
        with no notes and so no herald's mark, the small helm set down on the barrier where the last row of cells
        leaves room, the right first."""
        p = super().f1_narrow(ft, night)
        spots = [(self._after_words(p, p.h), p.w - 6, p.h, True, MARKS)]
        if not ft.get("closing"):
            spots.append((6, p.w - 6, None, True, ("S",)))
        return self._footed(p, night, spots)

    def f2_narrow(self, ft, night):
        """A phone's scale bar, the design's mark beside it, standing on the rule under them."""
        p = super().f2_narrow(ft, night)
        return self._footed(p, night, [(SCALE_CELL[0], PHONE_SCALE_CELL, PHONE_SCALE_RULE, False, MARKS)])

    def link_colours(self, night):
        """A banneret's cloth (repainted in its tincture by `link_top`), its edge, white letters and its foot."""
        return RAMP["gules"][2], RAMP["sable"][1], C["white"], RAMP["gules"][1]

    def link_top(self, p, x0, x1, y, seed, night):
        """The button finished as a banneret hung from a lance: see `art.banneret`."""
        A.banneret(p, p.w, seed, night)

    def link_icon(self, index, night, ink):
        return A.ICONS[A.LINK_SPRITES[index % len(A.LINK_SPRITES)]], A.icon_pal(night)

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """The set's touch over a badge, kept inside its shape and off its letters: a gold cord laid along its top two
        rows, its strands twisted, the silk's sheen under it, a dark seam where the label's silk meets the value's,
        and the foot of the silk in shade."""
        h = s["h"]
        ty = self._text_y(s)
        text_rows = range(ty - 1, ty + (7 if s["font"] == "57" else 5) + 1)

        def ins(x, y):
            return 0 <= x < w and 0 <= y < h and inside(x, y, w, h, s["corner"])
        row = h - 2 if (h - 2) % 4 != 2 else h - 3
        first = next((x for x in range(w) if ins(x, row) and ins(x, row - 1)), 0)
        edge = next((x for x in range(first + 2, w) if ins(x, row) and p.get(x, row) != p.get(x - 1, row)
                     and p.get(x, row - 1) != p.get(x - 1, row - 1)), w)
        for y in range(h):
            for x in range(w):
                if not ins(x, y):
                    continue
                c = p.get(x, y)
                if y == 0:
                    p.px(x, y, (G[5], G[4], G[2])[(x + y) % 3])
                    continue
                if y == 1:
                    p.px(x, y, (G[3], G[2], G[1])[(x + y) % 3])
                    continue
                try:
                    if y == h - 1:
                        p.px(x, y, step(c, -1))
                    elif x == edge and edge < w:
                        p.px(x, y, step(c, -1))
                    elif y == 2 and y not in text_rows:
                        p.px(x, y, step(c, 1))
                except KeyError:
                    pass

    def badge_label(self):
        return (V[1], G[5])

    def badge_gold(self):
        return (G[3], RAMP["sable"][0])

    def badge_states(self):
        return {"green": (V[2], C["white"]), "yellow": (G[4], RAMP["sable"][0]),
                "red": (RAMP["gules"][3], C["white"]), "slate": (RAMP["sable"][4], C["white"])}

    def badge_swatches(self):
        R = RAMP
        return {"gules": (R["gules"][3], C["white"], None), "tenne": (R["tenne"][4], R["sable"][0], None),
                "or": (G[4], R["sable"][0], None), "vert": (V[2], C["white"], None),
                "azure": (R["azure"][2], C["white"], None), "purpure": (R["purpure"][2], C["white"], None),
                "argent": (R["argent"][6], R["sable"][1], "damask"), "sable": (R["sable"][1], C["white"], None),
                "steel": (R["steel"][3], C["white"], None), "wood": (R["wood"][2], C["white"], None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        """White silk woven with a damask of small lozenges, kept off the letters' rows."""
        if pattern == "damask" and y not in text_rows and (x + y) % 4 == 0 and (x - y) % 8 == 0:
            return RAMP["argent"][4]
        return c

    def badge_outline(self, pattern):
        return RAMP["argent"][3] if pattern == "damask" else None

    def badge_shine(self, c, y, h):
        try:
            return step(c, 1) if y == 2 else step(c, -1) if y == h - 1 else c
        except KeyError:
            return c

    def plate_colours(self, mode):
        """A plate is a strip of the pavilion's canvas, stitched: unbleached by day and lantern-lit by night, the
        value on a block of green silk with white letters; a live plate is cloth of gold."""
        if mode == "day":
            return dict(paper=X["panel_a"], dot=X["stitch_a"], frame=V[1], block=V[2], ink=C["ink"],
                        letters=C["white"])
        if mode == "night":
            return dict(paper=DU[2], dot=DU[3], frame=G[2], block=V[2], ink=C["ink_n"], letters=C["white"])
        return dict(paper=G[3], dot=G[2], frame=RAMP["sable"][0], edge=G[1], ink=RAMP["sable"][0])

    def plate_edge(self, block):
        return step(block, -1)


SET = Tournament()
