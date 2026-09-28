# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""A GitHub client that answers from a table: the same methods as `infra.github.GitHub`, no network.

The answers are shaped exactly like GitHub's, for a made-up developer,
octo-dev, and their repository, toolkit.
"""
from __future__ import annotations

from tests import support  # noqa: F401  (puts src/ on the path)

from app.parts import banners as measure


class FakeGitHub:
    """Answers each query from `answers`, keyed by the query text; a callable answer gets the variables."""

    def __init__(self, answers: dict, users: dict | None = None):
        self.answers = answers
        self.users = users or {}
        self.calls = 0
        self.points = 0
        self.last_errors: list[str] = []
        self.asked: list = []

    def gql(self, query: str, **variables) -> dict:
        self.calls += 1
        self.asked.append((query, variables))
        answer = self.answers[query]
        return answer(**variables) if callable(answer) else answer

    def rest(self, path: str, **params):
        self.calls += 1
        self.asked.append((path, params))
        login = path.rsplit("/", 1)[-1]
        return self.users.get(login)

    def paged(self, query: str, path: tuple, page_size: int = 100, limit: int = 10, **variables) -> list:
        nodes, after = [], None
        for _ in range(limit):
            data = self.gql(query, first=page_size, after=after, **variables)
            conn = data
            for key in path:
                conn = (conn or {}).get(key)
            if not conn:
                break
            nodes.extend(n for n in conn.get("nodes", []) if n)
            info = conn.get("pageInfo") or {}
            if not info.get("hasNextPage"):
                break
            after = info.get("endCursor")
        return nodes


def commit(day: str, headline: str, committer: str = "Octo Dev", email: str = "octo@users.noreply.github.com") -> dict:
    return {"committedDate": f"{day}T12:00:00Z", "messageHeadline": headline,
            "committer": {"name": committer, "email": email}}


BOT = ("github-actions[bot]", "41898282+github-actions[bot]@users.noreply.github.com")


def repository_answer(**overrides) -> dict:
    r = {
        "nameWithOwner": "octo-dev/toolkit", "name": "toolkit",
        "description": "\U0001F9F0 A small, sharp set of command-line tools for working with structured logs.",
        "homepageUrl": "https://toolkit.octo.dev", "createdAt": "2019-03-14T09:00:00Z", "isArchived": False,
        "isPrivate": False, "hasIssuesEnabled": True, "hasDiscussionsEnabled": False,
        "owner": {"login": "octo-dev", "__typename": "User"},
        "stargazerCount": 1284, "forkCount": 96, "watchers": {"totalCount": 41},
        "openIssues": {"totalCount": 23}, "openPulls": {"totalCount": 4},
        "primaryLanguage": {"name": "Python"}, "licenseInfo": {"spdxId": "MIT", "name": "MIT License"},
        "latestRelease": {"tagName": "v2.4.0", "publishedAt": "2026-09-02T10:00:00Z"},
        "releases": {"totalCount": 31},
        "workflows": {"entries": [{"name": "markdown.yml"}, {"name": "checks.yaml"}, {"name": "README.md"}]},
        "repositoryTopics": {"nodes": [{"topic": {"name": "cli"}}, {"topic": {"name": "logs"}}, {"topic": {"name": "python"}}]},
        "defaultBranchRef": {"name": "main"},
    }
    r.update(overrides)
    return {"rateLimit": {"cost": 1}, "repository": r}


def history_answer(pages: list[list[dict]]):
    """A HISTORY answer that pages through `pages`, 100 at a time as the real one would."""
    def answer(owner, name, first, after=None):
        i = int(after or 0)
        return {"repository": {"defaultBranchRef": {"target": {"history": {
            "pageInfo": {"hasNextPage": i + 1 < len(pages), "endCursor": str(i + 1)},
            "nodes": pages[i]}}}}}
    return answer


def user_answer(**overrides) -> dict:
    u = {
        "login": "octo-dev", "name": "Octo Dev", "bio": "Builds small tools for big logs. Maintainer of toolkit.",
        "company": "", "location": "Lisbon, Portugal", "websiteUrl": "https://octo.dev", "twitterUsername": None,
        "createdAt": "2018-05-02T08:00:00Z", "followers": {"totalCount": 88}, "following": {"totalCount": 61},
        "publicRepos": {"totalCount": 34},
        "status": {"message": "Shipping toolkit 2.5"},
        "contributionsCollection": {"contributionCalendar": {"totalContributions": 1864}},
    }
    u.update(overrides)
    return {"rateLimit": {"cost": 1}, "user": u}


def repos_answer(nodes: list[dict]):
    def answer(login, first, after=None):
        i = int(after or 0)
        chunk = nodes[i * first:(i + 1) * first]
        return {"user": {"repositories": {"pageInfo": {"hasNextPage": (i + 1) * first < len(nodes), "endCursor": str(i + 1)},
                                          "nodes": chunk}}}
    return answer


def repository_client(pages=None, **overrides) -> FakeGitHub:
    pages = pages or [[commit("2026-09-25", "chore(markdown): \U0001FAA7 redraw with 1,284 stars", *BOT),
                       commit("2026-09-24", "chore(trophies): \U0001F3C6 refresh the case", *BOT),
                       commit("2026-09-23", "feat: add the tail command")]]
    return FakeGitHub({measure.REPOSITORY: repository_answer(**overrides), measure.HISTORY: history_answer(pages)})


def profile_client() -> FakeGitHub:
    repos = [{"stargazerCount": 200, "primaryLanguage": {"name": "Python"}},
             {"stargazerCount": 90, "primaryLanguage": {"name": "Go"}},
             {"stargazerCount": 12, "primaryLanguage": {"name": "Go"}},
             {"stargazerCount": 10, "primaryLanguage": {"name": "Python"}},
             {"stargazerCount": 0, "primaryLanguage": None}]
    readme = repository_answer(nameWithOwner="octo-dev/octo-dev", name="octo-dev", description="", homepageUrl="",
                               stargazerCount=3, forkCount=0, primaryLanguage=None, latestRelease=None,
                               releases={"totalCount": 0}, repositoryTopics={"nodes": []})
    return FakeGitHub({measure.USER: user_answer(), measure.REPOS: repos_answer(repos), measure.REPOSITORY: readme,
                       measure.HISTORY: history_answer([[commit("2026-09-20", "docs: say hello")]])},
                      users={"octo-dev": {"login": "octo-dev", "type": "User"}})
