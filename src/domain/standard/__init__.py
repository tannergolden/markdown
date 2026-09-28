# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The standard theme: the original badges' own look, grown to the size of a header.

`pieces` holds the parts every drawing is made of, a badge's two panels at any
size among them; `banners` draws the headers, the footers and the links under
them; `elements` draws the six elements. The banners and the elements hand a
drawing here whenever the page is drawn in `standard`, and to their prints
otherwise, so a design's name, its files and its README block are the same in
every theme.
"""
