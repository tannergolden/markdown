<!--
title: '⌨️ COMMAND LINE'
description: 'Every markdown-kit command with its flags, what it reads and writes, whether it needs a token, the environment it reads, and what its exit status means. Look a command up here before scripting it or running it against a page.'
type: reference
keywords: [cli, markdown-kit, commands, flags, exit status, environment variables]
-->

<div align="center">

# ⌨️ COMMAND LINE

<a name="top"></a>

**Every command the kit answers to, with what it reads, writes and needs.**

_Sixteen commands. Three need a token._

</div>

---

## 🚀 Running It

The kit is [`src/markdown-kit.py`](../../src/markdown-kit.py), standard-library
Python 3.10 or later, with nothing to install. Run it from a clone of this
repository, and point `--root` at the page's checkout:

```bash
python3 src/markdown-kit.py check --root ../the-page
python3 src/markdown-kit.py preview --root /tmp/page --input theme=medieval --today 2026-12-15
```

`python3 src/markdown-kit.py --help` lists the commands, and `COMMAND --help`
the flags of one. The [Makefile](../../Makefile) wraps the ones this repository
runs most: `make draw`, `make lint`, `make catalogue` and `make calibrate`.

---

## 📋 The Commands

| Command       | Does                                                                                                 | Reads GitHub                          | Writes                                                  |
| :------------ | :--------------------------------------------------------------------------------------------------- | :------------------------------------ | :------------------------------------------------------ |
| `run`         | Measures the page, draws every part, and writes what changed                                         | Yes, with a token, and git            | The drawn files, the README's blocks and the lock       |
| `render`      | Draws again from what the lock kept, or from `--from`                                                | No                                    | The drawn files and the README's blocks, never the lock |
| `check`       | Draws again from the lock, or from `--from`, and compares byte for byte                              | No                                    | Nothing                                                 |
| `preview`     | Draws a sample page the way a run would                                                              | No                                    | The files, a README and a lock, into `--root`           |
| `measure`     | Measures the page and prints the measurement as JSON                                                 | Yes, with a token, and git            | Nothing                                                 |
| `set`         | Writes badges' values into the settings file, keeping its comments                                   | No                                    | The settings file                                       |
| `settings`    | Prints the settings in full, every default filled in, as JSON                                        | No                                    | Nothing                                                 |
| `lint`        | Draws every design for every sample in every print, every badge, trophy and set, and lints each file | No                                    | Nothing                                                 |
| `catalogue`   | Prints `docs/references/Catalogue.md` from the trophies' catalogue and calibration                   | No                                    | Nothing; `make catalogue` writes the file               |
| `calibrate`   | Measures the repository population the repository-mode trophies are set against                      | Yes, with a token, thousands of calls | `--out`                                                 |
| `holidays`    | Which holiday's set is up on a day, and the windows ahead or in a year                               | No                                    | Nothing                                                 |
| `collections` | Each collection's design for every month, and the one up on a day                                    | No                                    | Nothing                                                 |
| `palette`     | The 64 colour tokens, each with the letters it takes                                                 | No                                    | Nothing                                                 |
| `icons`       | The 64 icons                                                                                         | No                                    | Nothing                                                 |
| `version`     | The kit and the version of the files it draws                                                        | No                                    | Nothing                                                 |
| `replay`      | Draws a finished game's replay, for @tannergolden's profile alone                                    | No                                    | Two files, by day and by dark                           |

What `run`, `render`, `check` and `preview` each skip is in
[How A Run Works](../technical/How-A-Run-Works.md#-the-four-commands-that-draw).

---

## ⚙️ The Flags

Every command that reads a page takes `--root`, the page's checkout (the current
folder by default), and `--input KEY=VALUE`, once for each value a stub sets:
`mode`, `theme`, `sign`, `holidays`, `holiday-days` or `birthday`. A value given
this way wins over the settings file's, as a stub's input does.

| Command           | Its own flags                                                                                                                                                                                                                 |
| :---------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `run`             | `--today YYYY-MM-DD`, the day to draw (today in the page's `timezone` by default); `--commit-file PATH`, where a commit message goes when something changed; `--save PATH`, the measurement as JSON                           |
| `render`, `check` | `--from PATH`, a saved measurement to draw from instead of the lock                                                                                                                                                           |
| `preview`         | `--today YYYY-MM-DD`. Without it the sample is drawn as of its own day, 2026-09-25                                                                                                                                            |
| `measure`         | `--today YYYY-MM-DD`                                                                                                                                                                                                          |
| `set`             | One or more `NAME=MESSAGE[:COLOR]`: a badge's name, its message, and a colour after a colon if it changes                                                                                                                     |
| `lint`            | `--specimen PATH`, a repository whose elements are drawn in every print too; `make lint` passes `tests/fixtures/driftmark`                                                                                                    |
| `calibrate`       | `--per-band N`, repositories measured in each star band (40); `--seed N`, the sample's seed (today's ordinal, so a re-run the same day repeats it); `--today`; `--out PATH` (`src/domain/data/calibration/repositories.json`) |
| `holidays`        | `--year YEAR`, every window in a year; `--days N`, `holiday-days` from 3 to 7 (3); `--today`; `--timezone ZONE` (UTC)                                                                                                         |
| `collections`     | `--today`; `--timezone ZONE` (UTC)                                                                                                                                                                                            |

`set` refuses a badge the kit measures itself, since the next run would measure
it again, and a badge not written as an entry of its own, `- name: NAME`, in the
settings file.

---

## 🚦 Exit Status

| Status | Means                                                                                                                                                                                   |
| :----- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0      | Done. For `check`, the committed page is current                                                                                                                                        |
| 1      | A fault outside the settings, such as a refused token, no network or a git failure; a `check` that found the page stale; a `lint` that found a problem                                  |
| 2      | A setting or a file the kit reads is wrong, said in one line on standard error as `markdown-kit: ...`; a `check` with no measurement to draw from; or a command line the parser refuses |

[Troubleshooting A Run](../operations/Troubleshooting-A-Run.md) has the messages
and their fixes.

---

## 🛡️ The Environment

| Variable              | Read by                             | For                                                                                                  |
| :-------------------- | :---------------------------------- | :--------------------------------------------------------------------------------------------------- |
| `MARKDOWN_TOKEN`      | `run`, `measure`                    | The token to measure with, before `GITHUB_TOKEN`                                                     |
| `GITHUB_TOKEN`        | `run`, `measure`, `calibrate`       | The token when `MARKDOWN_TOKEN` is not set; `calibrate` reads this one, or `GH_TOKEN`                |
| `GITHUB_REPOSITORY`   | `run`, `measure`, `render`, `check` | Which repository the page is in. Without it, the GitHub repository `origin` points at                |
| `GITHUB_RUN_ID`       | `run`                               | Named in the commit message's body                                                                   |
| `GITHUB_STEP_SUMMARY` | `run`, `render`, `preview`          | A file the run's summary is appended to                                                              |
| `GITHUB_ACTIONS`      | `run`, `measure`                    | Set, the GitHub client writes its retries and partial answers as `::debug::` and `::warning::` lines |

Work on this repository runs Python with the tokens unset, as
[CLAUDE.md](../../CLAUDE.md) asks, so only `run`, `measure` and `calibrate` ever
need one exported.

---

### 🔗 See also

- [Settings](Settings.md) - every key `--input` and the settings file can hold
- [Technology Stack & Tooling](../technical/Technology-Stack-&-Tooling.md) - the Makefile targets CI runs

---

<div align="center">

**Name the command, point it at the page, read what it prints.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the MIT License.

</div>
