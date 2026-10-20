<!--
title: '🩺 TROUBLESHOOTING A RUN'
description: 'What to do when a page''s run fails, a check says the page is stale, or a run passes and the page still looks wrong: each message the kit prints, what it means, and the fix. Read it with the failed run''s log open.'
type: guide
keywords: [errors, failures, stale, check mode, tokens, permissions, notes, runbook]
-->

<div align="center">

# 🩺 TROUBLESHOOTING A RUN

<a name="top"></a>

**Every message a run prints, what it means, and the fix that clears it.**

_The run names its fault. Fix that, then run it again._

</div>

---

## 💡 Where A Run Says What Happened

A page's run is one job, **📝 Measure and draw**, in the page's own Actions tab.
Its step **📝 The page** is the kit, which prints:

- One line saying what it drew, such as
  `banners for octo/drift (repository): H2 Section and F1 Title block in blueprint; ...`.
- A `note:` line for each thing it drew short, those found while measuring
  before that line and those found while drawing after it.
- `N files changed`, or `nothing changed`.
- The commit's subject, last, when something changed.

The line saying what it drew, and the notes found while drawing, also go to the
run's summary page, under **Markdown**. A field of GitHub's that the token may
not read shows as a `GraphQL partial:` warning on the run, which goes on without
it. The kit's exit status says how it ended:

| Status | Means                                                                                                       |
| :----- | :---------------------------------------------------------------------------------------------------------- |
| 0      | The page is drawn. Any `note:` line says what was drawn short, and the run still passes                     |
| 1      | A fault outside the settings: GitHub refused or did not answer, git failed, or a check found the page stale |
| 2      | A setting, or a file the kit reads, is wrong. One line, `markdown-kit: ...`, names it                       |

This repository's own page is drawn every night by the same stub every page
copies, and 🚨 CI Failure Alerts opens an issue when 📝 Markdown or 📐 Calibrate
fails here on a long-lived branch, then closes it when that workflow recovers.

---

## 🚦 First Steps

- [ ] Open the failed step and read the last line the kit printed.
- [ ] Find that line below and fix what it names.
- [ ] Where you can, reproduce it from a clone of this kit, with no token, against
      a checkout of the page.
- [ ] Run the page's workflow again from its Actions tab, or wait for the
      schedule. Every run measures everything again, so a failed one loses
      nothing.

```bash
python3 src/markdown-kit.py settings --root ../the-page   # what a run will read, every default filled in
python3 src/markdown-kit.py check --root ../the-page      # is the committed page what the lock says?
```

---

## ⚙️ A Setting Is Wrong (Status 2)

| The kit says                                                                              | What to do                                                                                                                                    |
| :---------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------- |
| `unknown key in .github/markdown.yaml: KEY`                                               | Correct or remove the key. Every key is checked, and [Settings](../references/Settings.md) has them all; hyphens and underscores are the same |
| `.github/markdown.yaml: line N: ...`                                                      | The file is not YAML the kit reads. The line number says where it breaks                                                                      |
| `both .github/markdown.yaml and .github/markdown.yml are here; keep one`                  | Merge them into one file and delete the other                                                                                                 |
| `theme: 'NAME' is not one of ...`                                                         | Name a theme from the list, or define the print under `prints:` first                                                                         |
| `theme: rainbowprint remembers its last colour in the lock; set lock: true`               | Take `lock: false` out                                                                                                                        |
| `timezone: 'NAME' is not ...`                                                             | Use an IANA zone name, such as `America/New_York`, or `UTC`                                                                                   |
| `repository mode needs subject: owner/name, or a run inside the repository`               | Set `subject: owner/name`, or run the kit inside the repository it draws                                                                      |
| `organization pages are not drawn yet; set mode: repository for now`                      | Set `mode: repository` on an organization's `.github`                                                                                         |
| `birthday: a repository's birthday is the day GitHub created it; ...`                     | On a repository's page, `birthday` is `true` or `false` only                                                                                  |
| `<!-- markdown:NAME:start --> has no <!-- markdown:NAME:end --> after it`                 | Put the end marker back after its start, or remove both                                                                                       |
| `the lock is version N; this kit reads version 1`, or `the lock is not JSON (...)`        | The lock was edited by hand or broken in a merge. Restore it from git, or delete it: that loses its history, never correctness                |
| `check needs a measurement of the ...: run the kit once with the lock on, or pass --from` | A check before the page's first run, or on a page with `lock: false`. Let one run write the lock, or pass `--from` a saved measurement        |

A message that names a part, such as `elements: ...` or `trophies: ...`, is that
part's own section of the settings refused, and names the field.

---

## 🛡️ GitHub Refused Or Did Not Answer (Status 1)

| The kit says                                                                        | What to do                                                                                                                                                        |
| :---------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `no token: set GITHUB_TOKEN (every workflow has one) or MARKDOWN_TOKEN`             | Only seen outside Actions. Export a token for `run` or `measure`, or use `preview`, `render` and `check`, which need none                                         |
| `GitHub refused the token (401) for URL`                                            | The page's `MARKDOWN_TOKEN` secret has expired or been revoked. Replace it, or delete it and the run measures with `GITHUB_TOKEN`                                 |
| `cannot read repository OWNER/NAME: ...`                                            | The subject is misspelled, or the token cannot read it. `GITHUB_TOKEN` reads the repository the run is in and everything public                                   |
| `cannot read user LOGIN: ... (profile mode measures a person, not an organization)` | `subject` names an organization, or a login that does not exist                                                                                                   |
| `GitHub answered CODE for URL: ...` or `network failure for URL: ...`               | GitHub refused the request, or still failed after four retries of a 5xx, a rate limit or the network. A fault of GitHub's own passes, and the next run catches up |
| `` `git ...` failed: ... ``                                                         | A git command the run reads the repository with failed. Locally, run the kit inside a clone with its whole history                                                |

---

## 🌿 The Workflow Failed Around The Kit

- **The run failed before any job started, with no log.** A stub's
  `permissions:` is a ceiling on the job it calls, and the kit's job asks for
  `contents: write` and `pull-requests: write`. A stub that grants less fails at
  startup. Grant both, even with `check: true`, as the
  [README's stubs](../../README.md#-one-stub) do.
- **📥 Fetch the kit failed.** The stub's `kit-ref` names a ref that is gone.
  Every release prunes the version tags before it, so a `kit-ref` of an older
  `vX.Y.Z` stops resolving once a newer one is cut, and a stub whose `uses:`
  names such a tag stops finding the workflow at all. Leave both on `v1`, or pin
  a commit: [Pinning A Page](../distribution/Releasing-The-Kit.md#-pinning-a-page).
- **📤 Commit and push failed.** The branch moved during the run, and replaying
  the drawing onto it met a change to the same lines, such as a hand edit in a
  drawn file, inside the README's blocks, or in the lock. The next run draws
  from the branch as it stands then. A branch that cannot take the push takes
  `commit: pr` instead, which sends the drawing as one pull request on
  `commit-branch`.
- **📝 The page failed.** The kit's own exit: read its last line, above.

---

## 🔍 A Check Says Stale

`check` prints `stale:` and every difference, then exits 1. The fix for each is
the page's next run, or a run started by hand; what differs says why it drifted:

| It says                                    | Why                                                                                                    | What to do                                                     |
| :----------------------------------------- | :----------------------------------------------------------------------------------------------------- | :------------------------------------------------------------- |
| `PATH (missing)`                           | A file the page shows is not committed                                                                 | Restore it from git, or let a run draw it                      |
| `PATH (differs)`                           | The file was edited by hand, or the kit at `v1` now draws it differently from the release that drew it | Never edit a drawn file. A run draws it again                  |
| `PATH (no longer drawn)`                   | A file under `out` carries the kit's stamp and nothing draws it, often a copy of a drawn file          | Delete it, or keep the copy outside `out`                      |
| `README.md (NAME markers missing)`         | The header, badges, trophies or footer block lost its markers                                          | Put the two markers back, or let a run place the block again   |
| `README.md (NAME block differs)`           | Something inside the block was edited, or the settings changed without a run                           | Keep your own words outside the markers, then let a run redraw |
| `README.md (NAME block no longer drawn)`   | The settings no longer ask for that block                                                              | A run takes it out                                             |
| `PATH (shields.io links to localize)`      | `localize` is on and the document still links to shields.io                                            | A run draws those badges and rewrites the links                |
| `PATH (links to localized badges to move)` | The document links to a folder localized badges have since left                                        | A run moves the links                                          |

---

## 📝 The Run Passed, The Page Looks Wrong

| You see                                        | Why                                                                                                                                                                                                                            | What to do                                                                                             |
| :--------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------- |
| An element is missing from the page            | Its markers are not in the README, and the run said `note: element:ID: the README has no markers for it yet, ...`                                                                                                              | Add its two markers where it belongs; the next run fills them                                          |
| A live badge says No Data                      | The run could not read what it measures, and a `note:` names it, such as `cannot read the runs of checks.yml in octo/drift; its badge shows no data`                                                                           | Check the badge's `workflow:` file, its `repository:`, and what the token can read                     |
| The footer's date does not move, or is missing | It is the day of the newest commit a person made on the default branch. The kit's commits, bots' and any subject scoped `chore(markdown)` are set aside, and with no person's commit among the newest 500 the date is left off | Give your own commits another scope                                                                    |
| An achievement reads not measured yet          | The run could not read what it counts: a `note:` says so, such as traffic needing push access or a scope the token lacks. Some counts, such as who depends on a repository, the API never gives                                | Nothing: it is never drawn as a zero. A `MARKDOWN_TOKEN` with the named scope reads what a scope gates |
| A note says history is still being scanned     | The heavy achievements read commits, at most `scan-pages` pages a run, and catch up over the next runs                                                                                                                         | Wait, or raise `scan-pages` under `trophies:`                                                          |
| A holiday's set went up a day early or late    | The page's day turns at midnight in its `timezone`, UTC unless the settings name another                                                                                                                                       | Set `timezone`. `markdown-kit holidays --year 2026` lists every window                                 |
| A set took the page over                       | A holiday's window is open, or it is the page's birthday                                                                                                                                                                       | `holidays: false` or `birthday: false` keeps either away                                               |
| The page changed colour                        | It is a `rainbowprint`, which moves to the next colour with each update                                                                                                                                                        | Name one print to keep it                                                                              |
| A file under `assets/` disappeared             | It carried the kit's stamp and nothing draws it now. A copy of a drawn file carries the stamp too                                                                                                                              | Keep copies outside `out`. A file without the stamp is never removed                                   |
| Nothing was committed for days                 | Nothing the page shows moved, so the runs wrote nothing                                                                                                                                                                        | Nothing: the lock is still written once a week                                                         |
| A run waits for another                        | The stub's `concurrency` group draws one at a time; the waiting run draws the page as it stands by then                                                                                                                        | Nothing                                                                                                |

[How A Run Works](../technical/How-A-Run-Works.md) says why each of these happens,
and [Command Line](../references/Command-Line.md) has every command these steps
use.

---

### 🔗 See also

- [Troubleshooting](https://github.com/tannergolden/standards/blob/Development/docs/operations/Troubleshooting.md) - the shared triage for every repository's failures
- [Settings](../references/Settings.md) - every key the settings can hold

---

<div align="center">

**Read the line it printed, fix that, and let the next run catch up.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
