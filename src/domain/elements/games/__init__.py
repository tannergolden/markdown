# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: LicenseRef-Proprietary
"""What every game on @tannergolden's profile shares, so the four sheets read as one family drawn by one hand.

Chess came first, and the games beside it (Tic-Tac, Pentago and Checkers) are drawn the way it is: the
same card or drafting sheet and its band, the same two materials (the standard theme's enamel and a print's
drawing), the same lettering, and the same panel beside the board, a section at a time: the two sides with the
turn ringed, the turn's plate and when the move is due, the last move in notation and in words, what the game
itself keeps count of, and the score sheet. A finished game's board stays up for two days with its plate saying
who won and how, as chess's does.

  sides   the house and GitHub: who they are and what each is called
  skin    chess's two skins, and what a game beside chess adds to both: words fitted to their room, the light and
          dark materials, a side's medallion, and the mark on what the side to move must answer
  panel   the panel's sections, each fitted to its room on a wide sheet and on a phone
  sheet   a board sheet, wide and a phone's, around a game's own board and its own count
  data    what every game's data is checked for, as strictly as chess's, and the state every sheet reads from it
  readme  the README block's words under a sheet: every legal move, folded, then the note

A game's own package draws its board and its pieces and says how its moves are written; everything else is here or
is chess's, imported rather than copied.
"""
from __future__ import annotations

from .sides import GITHUB, HOUSE, SIDES, name, other

__all__ = ["GITHUB", "HOUSE", "SIDES", "name", "other"]
