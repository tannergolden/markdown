# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
import datetime as dt
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests import support  # noqa: F401

from domain.history import automated
from infra.git import ACTIONS_BOT, Git, GitError, Person

PERSON = Person("Tanner Golden", "24684994+tannergolden@users.noreply.github.com")


def sh(cwd, *args, env=None):
    import os
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, env={**os.environ, **(env or {})})


class GitTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.remote, self.root = base / "remote.git", base / "work"
        sh(base, "init", "--quiet", "--bare", "--initial-branch=main", str(self.remote))
        sh(base, "clone", "--quiet", str(self.remote), str(self.root))
        # A clone of an empty repository takes this machine's default branch name; the test wants main.
        sh(self.root, "symbolic-ref", "HEAD", "refs/heads/main")
        sh(self.root, "config", "user.name", "Test")
        sh(self.root, "config", "user.email", "test@example.com")
        sh(self.root, "config", "commit.gpgsign", "false")
        self.git = Git(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def commit(self, path, text, subject, who=PERSON, when="2026-09-01T12:00:00+00:00"):
        (self.root / path).parent.mkdir(parents=True, exist_ok=True)
        (self.root / path).write_text(text, encoding="utf-8")
        sh(self.root, "add", path)
        env = {**who.env("AUTHOR"), **who.env("COMMITTER"), "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when}
        sh(self.root, "commit", "--quiet", "-m", subject, env=env)

    def test_it_knows_its_repository(self):
        self.assertTrue(self.git.is_repo())
        self.assertFalse(Git(Path(self.tmp.name)).is_repo())
        self.assertIsNone(self.git.head())
        self.commit("README.md", "# hi\n", "docs: start")
        self.assertRegex(self.git.head(), r"^[0-9a-f]{40}$")
        self.assertEqual(self.git.branch(), "main")
        self.assertFalse(self.git.is_shallow())

    def test_it_reads_the_github_slug_from_origin(self):
        for url, slug in (("https://github.com/tannergolden/markdown.git", ("tannergolden", "markdown")),
                          ("git@github.com:acme/.github.git", ("acme", ".github")),
                          ("https://x-access-token:t@github.com/acme/site", ("acme", "site"))):
            sh(self.root, "remote", "set-url", "origin", url)
            self.assertEqual(self.git.slug(), slug)

    def test_the_readmes_last_change_by_a_person(self):
        self.commit("README.md", "# one\n", "docs(readme): 📝 first", when="2026-09-01T23:30:00-04:00")
        self.commit("README.md", "# two\n", "chore(markdown): 🎨 redraw", when="2026-09-05T10:00:00+00:00")
        self.commit("README.md", "# three\n", "docs: by a bot", who=ACTIONS_BOT, when="2026-09-06T10:00:00+00:00")
        self.commit("other.md", "x\n", "docs: elsewhere", when="2026-09-07T10:00:00+00:00")
        log = self.git.commits("README.md")
        self.assertEqual([c.subject for c in log], ["docs: by a bot", "chore(markdown): 🎨 redraw", "docs(readme): 📝 first"])
        person = next(c for c in log if not automated(c.subject, c.committer_name, c.committer_email))
        # 23:30 in New York on September 1 is September 2 in UTC.
        self.assertEqual(person.when, dt.datetime(2026, 9, 2, 3, 30, tzinfo=dt.timezone.utc))

    def test_changed_lists_what_differs_from_head(self):
        self.commit("a.txt", "a\n", "docs: a")
        (self.root / "a.txt").write_text("b\n")
        (self.root / "new dir").mkdir()
        (self.root / "new dir" / "n.svg").write_text("<svg/>")
        self.assertEqual(sorted(self.git.changed()), ["a.txt", "new dir/n.svg"])
        self.assertEqual(self.git.changed(["new dir"]), ["new dir/n.svg"])

    def test_commit_and_push_as_the_person_through_the_bot(self):
        self.commit("README.md", "# hi\n", "docs: start")
        sh(self.root, "push", "--quiet", "origin", "main")
        self.assertIsNone(self.git.commit("chore(markdown): nothing", author=PERSON))
        (self.root / "assets").mkdir()
        (self.root / "assets" / "h.svg").write_text("<svg/>")
        self.git.add(["assets"])
        sha = self.git.commit("chore(markdown): 🎨 draw\n\nBody.\n", author=PERSON)
        self.assertEqual(sha, self.git.head())
        who = self.git.run("log", "-1", "--format=%an <%ae>|%cn")
        self.assertEqual(who.strip(), f"{PERSON.name} <{PERSON.email}>|{ACTIONS_BOT.name}")
        self.git.push("main")
        self.assertEqual(Git(self.remote).run("rev-parse", "main").strip(), sha)

    def test_push_rebases_onto_what_the_remote_gained(self):
        self.commit("README.md", "# hi\n", "docs: start")
        sh(self.root, "push", "--quiet", "origin", "main")
        other = Path(self.tmp.name) / "other"
        sh(Path(self.tmp.name), "clone", "--quiet", str(self.remote), str(other))
        (other / "b.txt").write_text("b\n")
        sh(other, "add", "b.txt")
        sh(other, "-c", "user.name=O", "-c", "user.email=o@example.com", "commit", "--quiet", "-m", "docs: b")
        sh(other, "push", "--quiet", "origin", "main")
        (self.root / "c.txt").write_text("c\n")
        self.git.add(["c.txt"])
        self.git.commit("chore(markdown): c", author=PERSON)
        self.git.push("main")
        files = Git(self.remote).run("ls-tree", "--name-only", "main").split()
        self.assertEqual(sorted(files), ["README.md", "b.txt", "c.txt"])

    def test_a_failing_command_says_which(self):
        with self.assertRaisesRegex(GitError, "`git rev-parse --verify nope` failed"):
            self.git.run("rev-parse", "--verify", "nope")


if __name__ == "__main__":
    unittest.main()
