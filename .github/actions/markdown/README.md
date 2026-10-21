<!--
title: '🎬 MARKDOWN ACTION'
description: 'The composite action every page runs: the kit itself, at the tag a page pins, with nothing installed.'
type: index
-->

<div align="center">

# 🎬 MARKDOWN ACTION

<a name="top"></a>

**The kit as one step: what a page's workflow runs to draw it.**

_Called at a tag. Never copied._

</div>

---

## 💡 What This Folder Is For

[`action.yml`](action.yml) is the composite action that draws a page: one run
of the kit on the checkout. The reusable workflow every page's stub calls,
[`markdown.yml`](../../workflows/markdown.yml), fetches this repository at the
tag the page pins and runs the action from it by local path, so the workflow,
the action and the kit it runs always come from the same release.

The action runs [`src/markdown-kit.py`](../../../src/markdown-kit.py) on a bare
`python3`, with nothing installed, and keeps the fetched kit out of git's view,
so nothing of it reaches the page's tree.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                      | Purpose                                                                                 |
| :------------------------- | :-------------------------------------------------------------------------------------- |
| [`action.yml`](action.yml) | The action the reusable workflow runs: one run of the kit on the checkout it is handed. |
| [`README.md`](README.md)   | This file.                                                                              |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself.

---

<div align="center">

**One release: the workflow, the action and the kit it runs.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
