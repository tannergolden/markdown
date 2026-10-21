<!--
title: '🏷️ RELEASING THE KIT'
description: 'How a version of the kit is cut with Cut Release, what it checks, what moving v1 does to every page, how to undo a release, and how a page pins a version of its own. Read it before dispatching a release or changing what a page already relies on.'
type: guide
-->

<div align="center">

# 🏷️ RELEASING THE KIT

<a name="top"></a>

**Every page runs `v1`, so a release changes every page at once.**

_Cut forward. Watch this page first. Undo with a patch._

</div>

---

## 💡 What A Release Is

A release leaves two tags: `vX.Y.Z`, the version just cut, and `v1`, moved onto
it. Every stub calls [`markdown.yml`](../../.github/workflows/markdown.yml) at
`@v1`, and that workflow fetches the kit at its `kit-ref` input, which is `v1`
unless the stub passes another. So the workflow, the action and the kit a page
runs come from the same release, and every page runs a new release on its next
run with nobody on its side doing anything.

Each release also prunes every release before it, page and tag, so a page
cannot pin an older version for long: see [Pinning A Page](#-pinning-a-page).

`KIT_VERSION`, in [`src/domain/__init__.py`](../../src/domain/__init__.py), is
not the release. It is the version stamped into every file the kit draws,
`<!--markdown-kit v1 ...-->`, and a run recognises its own files by that stamp
when it takes away what it no longer draws.

---

## 🔢 Choosing The Number

The standards'
[Releases & Versioning](https://github.com/tannergolden/standards/blob/Development/docs/distribution/Releases-&-Versioning.md)
sets the SemVer rules every repository follows. For the kit, the question is
what a page on `v1` already has: its stub, its settings, its lock and its files.
A change belongs in a new major, never a move of `v1`, when it would break any
of them on that page's next run:

- **A settings key or value taken away or renamed.** An unknown key fails the
  run, so every page that still writes it stops drawing.
- **A workflow input taken away.** A stub that still passes it fails, and
  🔬 Verify Stub Ceilings checks this repository's own stubs for exactly that:
  an input the called workflow does not accept.
- **A scope added to the reusable workflow's `permissions:`.** Every stub grants
  `contents: write` and `pull-requests: write`, and a called job that asks for
  more than its caller grants fails before it starts.
- **The lock's `VERSION`**, in [`src/domain/lock.py`](../../src/domain/lock.py).
  A kit refuses a lock of any other version, so every page's next run would fail
  until its lock is carried over.
- **The stamp's opening, `<!--markdown-kit v`.** A run takes away only the files
  it recognises by it, so every page would keep its old files for good.

A new theme, a new collection, a new key with a default or a new element kind is
a minor release; a fix is a patch. A release that changes how a file is drawn
makes every page commit the redrawn file on its next run, and until then a
page's `check` reports that file as differing.

---

## 🚀 Cutting A Release

- [ ] The change is merged on `Development`, the default branch, and 🚦 Checks
      passed there.
- [ ] Every generated file is current: `make themes` after anything a page
      draws changed, and `make catalogue` after a trophy or a threshold did.
- [ ] Dispatch **🏷️ Cut Release** from the Actions tab, on `Development`, with
      `version` as `vX.Y.Z` and `move-major` left on.
- [ ] Watch both of its jobs pass.
- [ ] Draw this repository's page at once, as [After The Release](#-after-the-release)
      says.

| Job                                 | What it does                                                                                                                                                                                                                                                                                                                            |
| :---------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🧪 Verify The Release Candidate     | `make lint test` on the commit about to be tagged, with half an hour. The suite takes about six minutes on a quick runner and more than ten on a slow one, longer than the publisher's job allows                                                                                                                                       |
| 🏷️ Publish Version & Move Major Tag | The standards' `release.yml`, called rather than copied. It refuses a commit that is not on the default branch and a version that does not move forward, proves the files below exist and `make lint` passes, tags `vX.Y.Z`, force-moves `v1`, publishes the release with generated notes, and prunes every older release, page and tag |

The files a page resolves at the tag, which a release is refused without, are
named in [`cut-release.yml`](../../.github/workflows/cut-release.yml):
`.github/workflows/markdown.yml`, `.github/actions/markdown/action.yml`,
`src/markdown-kit.py`, `src/app/run.py`, `src/domain/data/fonts/glyphs.json` and
`src/domain/data/prints.json`. A change that moves one of them changes that list
in the same commit.

With `move-major` off, the version is tagged and published but `v1` stays where
it was, so no page on `v1` runs it.

---

## 👀 After The Release

This repository's own page, [`own-page.yml`](../../.github/workflows/own-page.yml),
calls the kit at `v1` exactly as every other page does, so it shows what the
release draws, and a broken release shows here first. It runs at midnight UTC;
dispatch **📝 Markdown** from the Actions tab to draw it at once. That run
measures the new tag for the header and the release badge, and its commit says
so, such as `chore(markdown): 🪧 redraw with release v1.17.0`. If it fails,
🚨 CI Failure Alerts opens an issue.

---

## ⏪ Undoing A Release

There is no older tag to point `v1` back at: each release prunes the ones before
it, and Cut Release refuses a version that does not move forward. So a release is
undone forward:

1. Revert the change on `Development`, and let 🚦 Checks pass.
2. Cut the next patch, which moves `v1` onto the revert.
3. Draw this repository's page, and read it.

---

## 📌 Pinning A Page

| A stub's pin                                  | Runs                          | Lasts                                                    |
| :-------------------------------------------- | :---------------------------- | :------------------------------------------------------- |
| `uses: ...markdown.yml@v1`, with no `kit-ref` | Each release in the `v1` line | For good                                                 |
| `@vX.Y.Z`, with `kit-ref: vX.Y.Z`             | That version                  | Until the next release prunes its tag, then fails        |
| `@COMMIT`, with `kit-ref: COMMIT`             | Exactly that commit           | For good: the prune takes releases and tags, not commits |

Pass `kit-ref` whenever `uses:` names anything but `v1`. The workflow fetches
the kit at `kit-ref`, and that is `v1` whatever ref the stub's `uses:` names, so
a stub pinned to a commit without it would run that commit's workflow with the
kit at `v1`.

`kit-ref` and `author`, who the refresh commit is authored by, are the two
inputs the reusable workflow takes beyond the README's table of stub inputs.

---

## 📦 The Other Release Workflow

[`release.yml`](../../.github/workflows/release.yml), **📦 Release**, came with
the template: it drafts release notes through the week and, for a published
release, publishes its assets and prunes. Cut Release is deliberately not it:
that one calls the shared publisher, which computes an information-rich tag and
never writes a moving major, so it cannot produce the `v1` a stub resolves.
Cut every release of the kit with 🏷️ Cut Release.

---

### 🔗 See also

- [How A Run Works](../technical/How-A-Run-Works.md) - what a page's next run does with the release
- [Drawing a Collection](../technical/Collections.md#-shipping-a-collection) - a collection ships whole, in a minor release
- [Troubleshooting A Run](../operations/Troubleshooting-A-Run.md) - when a page's run fails after one

---

<div align="center">

**One tag moves, and every page follows it on its next run.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
