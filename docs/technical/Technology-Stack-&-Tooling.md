<!--
title: '📝 TECHNOLOGY STACK & TOOLING'
description: 'Declares the technology stack and maps it to the universal make interface.'
tags: [stack, tooling, configuration, technical]
category: docs
-->

<div align="center">

# 📝 TECHNOLOGY STACK & TOOLING

<a name="top"></a>

**Recording the official ledger of our universal technology standards.**

_Standardized architecture. Modern tooling. Documented decisions._

</div>

---

## 🎯 Our Technology Philosophy

We adhere to a **Universal Technology Stack** philosophy. This allows for flexibility in tool selection while maintaining strict adherence to repository standards. Every choice recorded here is made with long-term maintenance, security, and developer velocity in mind.

- **Standardized Interop**: Regardless of the tool, it must integrate with our Makefile and CI standards.
- **Traceability**: Every pivot or architectural change must be recorded in this document.
- **AI-Augmented**: We leverage modern AI builders and IDEs to accelerate delivery without sacrificing quality.

---

> [!IMPORTANT]
> **Documentation is Mandatory**. Any tool or stack choice must be recorded here. If you pivot to a new tool or AI app builder, update this file immediately via a **Pull Request (PR)**.

---

## 🤖 AI Orchestration & IDEs

The tools used for engineering acceleration and prototyping.

| Tool Name     | Purpose       | Strategic Note                                                         | Description                    |
| :------------ | :------------ | :--------------------------------------------------------------------- | :----------------------------- |
| `Claude Code` | `Development` | Pairs on the kit; every commit it helps write says so in its trailers. | Primary AI orchestration tool. |

---

## 🏗️ Core Application Stack

The server and substrate choices for the system.

- **Backend Framework**: None. The kit is Python 3.10 or later and its standard library, with nothing to install ([ADR-0002](../adrs/ADR-0002-Standard-Library-Only.md)).
- **Cloud Provider**: GitHub. The kit runs inside the workflow of the repository it draws, on GitHub Actions' hosted runners.
- **Infrastructure Strategy**: Serverless: one scheduled job a day in the consumer's own workflow, calling this repository's `markdown.yml` ([ADR-0001](../adrs/ADR-0001-One-Kit-One-Stub.md)).

---

## 💾 Persistence Store

Where the application state lives.

- **Primary Database**: None. What a run must remember lives in the consumer's repository, in `.github/markdown.lock.json`.
- **Asset Storage**: The consumer's repository: every file the kit draws is committed there, under `assets/markdown/` (or beside an organization's `profile/README.md`), and nothing is fetched when the page is viewed.

---

## 🌐 User Interface Layer

The frameworks used to deliver the visual experience.

- **Web Framework**: None. The output is SVG files and the blocks of a README that show them, which GitHub renders.
- **Mobile Framework**: None. Every header, footer and wide element is also drawn 360 px wide for a phone.

---

## 🧪 Quality & Delivery

The tools ensuring stability and automated promotion.

- **Unit Testing**: `unittest`, from the standard library.
- **E2E Testing**: `unittest`, driving `src/markdown-kit.py` in a fresh process as a person runs it.
- **CI/CD Platform**: GitHub Actions (Standard), through the standards' reusable `ci.yml`.

---

## 🛠️ Repository Target Mapping

Mapping the project-specific tools to the universal repository interface (Makefile).

| Makefile Target   | Execution Logic           | Strategic Purpose                         |
| :---------------- | :------------------------ | :---------------------------------------- |
| **Setup** | Nothing: the kit installs nothing, so there is no `make setup`. | Bootstrap the local workspace. |
| **Lint** (`lint-command`) | `make lint`: the repository validator, `compileall` over `src` and `tests`, and the layering test. | Static analysis and style enforcement. |
| **Test** (`test-command`) | `make test`: `unittest` over `tests/unit`, `tests/integration`, `tests/e2e` and `.github/scripts`. | Execution of the validation suite. |
| **Build** (`build-command`) | Nothing is built: the action runs the source as it is tagged. | Transformation into deployable artifacts. |
| **`make deploy`** | None: a release is a tag, cut by the release workflow. | Environmental promotion.                  |

### 🔗 See also

> [!TIP]
> Every canonical guide is indexed in the [&#x1F4DA; Standards Index](https://github.com/tannergolden/standards/blob/Development/docs/README.md). If you rename or move a file, update every reference to it across the repository to prevent link drift.

---

<div align="center">

**Standardized tech. Accelerated delivery.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
