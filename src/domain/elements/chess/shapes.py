# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: LicenseRef-Proprietary
"""The pieces' shapes, shared by every theme: one set of silhouettes, so a knight is the same knight in each skin.

Every piece is drawn in a 45-unit box, its foot on one base plate. Parts are drawn back to front, each with the
edge, so the seams between collar, body and base read as a turned piece's do. A skin decides only what they are
made of: lit enamel in the standard theme, ink and line shading on a print.
"""
from __future__ import annotations

BASE = '<rect x="9.5" y="33.5" width="26" height="5" rx="2"/>'
PARTS = {
    "pawn": ['<path d="M17.6 21.5C17.6 26.6 15.2 30.4 12.8 33.5H32.2C29.8 30.4 27.4 26.6 27.4 21.5Z"/>', BASE,
             '<rect x="15.6" y="19" width="13.8" height="3.4" rx="1.7"/>', '<circle cx="22.5" cy="13.2" r="6"/>'],
    "rook": ['<path d="M14 33.5 16.2 29.2H28.8L31 33.5Z"/>', BASE,
             '<rect x="16.2" y="17.4" width="12.6" height="11.8"/>',
             '<path d="M12.3 8.4H16.9V11.6H20.4V8.4H24.6V11.6H28.1V8.4H32.7V15L30.4 17.6H14.6L12.3 15Z"/>'],
    "bishop": ['<path d="M18.1 25.4C18.1 29.4 15.6 31.4 13.4 33.5H31.6C29.4 31.4 26.9 29.4 26.9 25.4Z"/>', BASE,
               '<rect x="15.6" y="22.2" width="13.8" height="3.4" rx="1.7"/>',
               '<path d="M22.5 9.3C28.9 13.1 30.5 18.4 28.4 22.2H16.6C14.5 18.4 16.1 13.1 22.5 9.3Z"/>',
               '<circle cx="22.5" cy="6.9" r="2.5"/>'],
    "knight": ['<path d="M14.3 33.5C14.3 28.4 16.9 25.8 20.6 22.9L14.6 24.4C11.4 25.2 9.4 22.6 10.9 20.4L17.9 11.5'
               'L18.5 6.8L22.4 9.9C29.9 10.4 34.4 16.3 33.7 24.1C33.4 28.3 32.1 31.2 31.6 33.5Z"/>', BASE],
    "queen": ['<path d="M16.4 28.6C16.4 30.9 14.9 32.3 13.3 33.5H31.7C30.1 32.3 28.6 30.9 28.6 28.6Z"/>', BASE,
              '<rect x="14.2" y="25.6" width="16.6" height="3.4" rx="1.7"/>',
              '<path d="M10.6 13.6 15 25.8H30L34.4 13.6 28.9 20.2 28.1 10.9 24.7 19.4 22.5 9.6 20.3 19.4 16.9 10.9'
              ' 16.1 20.2Z"/>',
              '<circle cx="10.6" cy="13.1" r="2.2"/><circle cx="16.9" cy="10.4" r="2.2"/>'
              '<circle cx="22.5" cy="8.7" r="2.3"/><circle cx="28.1" cy="10.4" r="2.2"/>'
              '<circle cx="34.4" cy="13.1" r="2.2"/>'],
    "king": ['<path d="M16.4 28.6C16.4 30.9 14.9 32.3 13.3 33.5H31.7C30.1 32.3 28.6 30.9 28.6 28.6Z"/>', BASE,
             '<rect x="14.2" y="25.6" width="16.6" height="3.4" rx="1.7"/>',
             '<path d="M22.5 12.4C29.9 12.4 33.8 16.4 32.3 21.1C31.5 23.7 30.1 24.9 29.9 25.8H15.1C14.9 24.9 13.5 23.7 '
             '12.7 21.1C11.2 16.4 15.1 12.4 22.5 12.4Z"/>',
             '<path d="M21.2 3.2H23.8V5.9H26.5V8.5H23.8V12.4H21.2V8.5H18.5V5.9H21.2Z"/>'],
}
# Lines carved into a piece, in the other side's colour: the bishop's slit, the knight's eye, nostril and mane,
# the king's crown band, the queen's and the rook's bands.
DETAIL = {
    "pawn": "",
    "rook": '<path d="M16.2 17.6H28.8M16.2 29.2H28.8"/>',
    "bishop": '<path d="M25.1 13.4 20.5 18.6"/>',
    "knight": '<path d="M24.6 12.1C29.4 14.2 31.9 18.9 31.4 25.4"/><path d="M20.6 22.9C22.5 21.2 24.2 20.8 25.6 21.3"/>',
    "queen": '<path d="M16.6 22.9H28.4"/>',
    "king": '<path d="M15.2 20.1C19.8 18.7 25.2 18.7 29.8 20.1"/>',
}
DOTS = {"knight": '<circle cx="18.7" cy="15.4" r="1.45"/><circle cx="12.6" cy="21.4" r=".85"/>'}
# Where the lamp catches a black piece: a short bright line on its upper left, and along its base.
SPEC = {
    "pawn": "M18.7 11.3A4.4 4.4 0 0 1 21.3 8.9M17.7 30.6C18.8 28.4 19.3 26 19.4 23.6",
    "rook": "M14.3 10.2V14M18.1 19.6V27.3",
    "bishop": "M18.4 15.2C19.3 13.3 20.4 12.1 21.6 11.3M18.1 30.4C19.1 29.2 19.7 28 19.9 26.8",
    "knight": "M12.7 20.3L17.9 13.5M16.6 31.1C16.8 28.9 17.9 27 19.6 25.5",
    "queen": "M12.9 16.3L15.8 23.8M15.8 32.1C16.8 31.3 17.4 30.6 17.6 29.8",
    "king": "M15.2 16.4C16.6 14.9 18.5 14.1 20.4 13.9M15.8 32.1C16.8 31.3 17.4 30.6 17.6 29.8",
}
BASE_SPEC = "M12 35.1H21"
FOOT = (24.8, 38.8, 15.8, 3.4)      # the shadow at a piece's foot: centre and radii, in the box
LETTER = {"king": "K", "queen": "Q", "rook": "R", "bishop": "B", "knight": "N", "pawn": "P"}
KINDS = ("king", "queen", "rook", "bishop", "knight", "pawn")
