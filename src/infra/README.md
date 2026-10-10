<!--
title: '🔌 INFRASTRUCTURE LAYER'
description: 'The infrastructure layer: adapters that implement the domain interfaces against databases, networks, and outside services.'
tags: [source, infrastructure-layer, adapters, architecture]
category: docs
-->

<div align="center">

# 🔌 INFRASTRUCTURE LAYER

<a name="top"></a>

**The adapters that connect the project to databases, networks, and outside services.**

_Implement the interface. Hide the vendor._

</div>

---

## 💡 What This Folder Is For

Persistence, transport, and every adapter to something outside the process live
here: the repository that talks to the database, the client that calls an
external API, the publisher that writes to a queue. Each implements an interface
that [`../domain/`](../domain/README.md) or [`../app/`](../app/README.md)
declares, so the rest of the code depends on the interface and never on the
vendor.

Nothing imports this layer directly except the composition root that wires it
in, which is what lets one adapter be replaced without touching a use case.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                              | Purpose                                                                          |
| :--------------------------------- | :------------------------------------------------------------------------------- |
| [`__init__.py`](__init__.py)       | The infrastructure: every way the kit touches the world outside its own memory.  |
| [`clock.py`](clock.py)             | What day it is where the page is read.                                           |
| [`files.py`](files.py)             | Reading and writing the files a run leaves in the repository.                    |
| [`git.py`](git.py)                 | The repository the kit runs in, through the `git` on the machine.                |
| [`github.py`](github.py)           | A small GitHub client on urllib: GraphQL, REST, retries and a cost meter.        |
| [`README.md`](README.md)           | This file.                                                                       |
| [`resources.py`](resources.py)     | The kit's own data files, read from `src/domain/data/` and handed to the domain. |
| [`yaml_reader.py`](yaml_reader.py) | The YAML the settings file is written in, read with the standard library alone.  |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push, from what each file says
about itself. A subfolder appears as one row, so give it a README of its own and
its row links to that.

---

<div align="center">

**Every outside dependency behind an interface the project owns.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
