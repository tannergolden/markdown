# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The banners, measured and planned: what a header and a footer say, and the files and blocks they make.

Measuring reads the repository the README lives in and, on a profile, the
person too, through the GitHub client the run is handed, into one plain dict,
the measurement. It is kept in the lock, so a committed banner can be redrawn
and checked later without a token and without the numbers moving underneath.

  repository   the repository: its name, description, release, stars,
               forks, open issues, language, licence, and when it last
               changed
  profile      a person, for the README GitHub shows on their profile:
               name, bio, followers, public repositories and the stars
               they earned, contributions in the last year, their main
               language; plus the profile repository's own licence and
               last change, for the footer

"When it last changed" is the last commit on the default branch that a person
made: `domain.history` sets aside this kit's refreshes, the old kits', and
anything a bot committed, or every refresh would move the date it draws and so
cause the next one. The GraphQL is written out in full, so a reader can see
exactly what is asked.
"""
from __future__ import annotations

from collections import Counter

from domain.banners import plan as banners_plan
from domain.banners import settings as banners_settings
from domain.history import automated

from ..page import mode_and_subject

HISTORY_PAGES = 5
LOCK_KEY = "banners"


def day(stamp: str | None) -> str:
    """An ISO timestamp's date, in UTC, as GitHub stores it; empty for none."""
    return (stamp or "")[:10]


def _automated(node: dict) -> bool:
    who = node.get("committer") or {}
    return automated(node.get("messageHeadline") or "", who.get("name") or "", who.get("email") or "")


REPOSITORY = """
query($owner:String!,$name:String!){ rateLimit{cost}
  repository(owner:$owner,name:$name){ nameWithOwner name description homepageUrl createdAt isArchived isPrivate
    hasIssuesEnabled hasDiscussionsEnabled owner{ login __typename }
    stargazerCount forkCount watchers{totalCount}
    openIssues: issues(states:OPEN){totalCount} openPulls: pullRequests(states:OPEN){totalCount}
    primaryLanguage{ name } licenseInfo{ spdxId name }
    latestRelease{ tagName publishedAt }
    releases{totalCount}
    workflows: object(expression:"HEAD:.github/workflows"){ ... on Tree{ entries{ name } } }
    repositoryTopics(first:20){ nodes{ topic{ name } } }
    defaultBranchRef{ name } } }"""

HISTORY = """
query($owner:String!,$name:String!,$first:Int!,$after:String){ rateLimit{cost}
  repository(owner:$owner,name:$name){ defaultBranchRef{ target{ ... on Commit{
    history(first:$first,after:$after){ pageInfo{hasNextPage endCursor}
      nodes{ committedDate messageHeadline committer{ name email } } } } } } } }"""

USER = """
query($login:String!){ rateLimit{cost}
  user(login:$login){ login name bio company location websiteUrl twitterUsername createdAt
    followers{totalCount} following{totalCount}
    publicRepos: repositories(ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC){totalCount}
    status{ message }
    contributionsCollection{ contributionCalendar{ totalContributions } } } }"""

REPOS = """
query($login:String!,$first:Int!,$after:String){ rateLimit{cost}
  user(login:$login){ repositories(ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC,first:$first,after:$after,
      orderBy:{field:STARGAZERS,direction:DESC}){
    pageInfo{hasNextPage endCursor}
    nodes{ stargazerCount primaryLanguage{ name } } } } }"""


def last_change(gh, owner: str, name: str, notes: list) -> str:
    """The date of the newest default-branch commit a person made, reading back at most a few pages."""
    after = None
    for _ in range(HISTORY_PAGES):
        data = gh.gql(HISTORY, owner=owner, name=name, first=100, after=after)
        target = ((((data or {}).get("repository") or {}).get("defaultBranchRef") or {}).get("target") or {})
        history = target.get("history") or {}
        for node in history.get("nodes") or []:
            if node and not _automated(node):
                return day(node.get("committedDate"))
        info = history.get("pageInfo") or {}
        if not info.get("hasNextPage"):
            break
        after = info.get("endCursor")
    notes.append(f"no commit by a person in the last {HISTORY_PAGES * 100} on {owner}/{name}'s default branch; "
                 "the date is left off")
    return ""


def repository(gh, owner: str, name: str, notes: list) -> dict:
    r = gh.gql(REPOSITORY, owner=owner, name=name).get("repository")
    if not r:
        why = "; ".join(getattr(gh, "last_errors", []) or []) or "not found, or not readable with this token"
        raise RuntimeError(f"cannot read repository {owner}/{name}: {why}")
    licence = (r.get("licenseInfo") or {}).get("spdxId") or ""
    release = r.get("latestRelease") or {}
    return {
        "full": r["nameWithOwner"], "name": r["name"], "owner": (r.get("owner") or {}).get("login") or owner,
        "org": (r.get("owner") or {}).get("__typename") == "Organization",
        "description": r.get("description") or "", "homepage": r.get("homepageUrl") or "",
        "created": day(r.get("createdAt")), "archived": bool(r.get("isArchived")), "private": bool(r.get("isPrivate")),
        "stars": r.get("stargazerCount") or 0, "forks": r.get("forkCount") or 0,
        "watchers": ((r.get("watchers") or {}).get("totalCount")) or 0,
        "issues": ((r.get("openIssues") or {}).get("totalCount")) or 0,
        "pulls": ((r.get("openPulls") or {}).get("totalCount")) or 0,
        "issuesOn": bool(r.get("hasIssuesEnabled")),
        "discussionsOn": bool(r.get("hasDiscussionsEnabled")),
        # The workflow files on the default branch: an Actions page with none has nothing to show.
        "workflows": sum(1 for e in ((r.get("workflows") or {}).get("entries") or [])
                         if (e.get("name") or "").endswith((".yml", ".yaml"))),
        "language": (r.get("primaryLanguage") or {}).get("name") or "",
        # NOASSERTION is GitHub saying it found a licence file it cannot name.
        "license": "" if licence in ("", "NOASSERTION") else licence,
        "release": release.get("tagName") or "", "released": day(release.get("publishedAt")),
        "releases": ((r.get("releases") or {}).get("totalCount")) or 0,
        "topics": [((n or {}).get("topic") or {}).get("name") for n in ((r.get("repositoryTopics") or {}).get("nodes") or [])
                   if ((n or {}).get("topic") or {}).get("name")],
        "branch": (r.get("defaultBranchRef") or {}).get("name") or "",
        "updated": last_change(gh, owner, name, notes) if r.get("defaultBranchRef") else "",
    }


def profile(gh, login: str, notes: list) -> dict:
    u = gh.gql(USER, login=login).get("user")
    if not u:
        why = "; ".join(getattr(gh, "last_errors", []) or []) or "no such user"
        raise RuntimeError(f"cannot read user {login}: {why} (profile mode measures a person, not an organization)")
    repos = gh.paged(REPOS, ("user", "repositories"), login=login)
    languages = Counter((r.get("primaryLanguage") or {}).get("name") for r in repos if r.get("primaryLanguage"))
    # The language most of their repositories are written in; a tie goes to the one whose repositories have more stars.
    stars_in = Counter()
    for r in repos:
        if r.get("primaryLanguage"):
            stars_in[r["primaryLanguage"]["name"]] += r.get("stargazerCount") or 0
    top = sorted(languages, key=lambda k: (-languages[k], -stars_in[k], k))
    status = u.get("status") or {}
    site = u.get("websiteUrl") or ""
    return {
        "login": u["login"], "name": u.get("name") or "", "bio": u.get("bio") or "",
        "company": u.get("company") or "", "location": u.get("location") or "", "website": site,
        "twitter": u.get("twitterUsername") or "", "created": day(u.get("createdAt")),
        "followers": ((u.get("followers") or {}).get("totalCount")) or 0,
        "following": ((u.get("following") or {}).get("totalCount")) or 0,
        "repositories": ((u.get("publicRepos") or {}).get("totalCount")) or 0,
        "stars": sum(r.get("stargazerCount") or 0 for r in repos),
        "contributions": ((((u.get("contributionsCollection") or {}).get("contributionCalendar")) or {})
                          .get("totalContributions")) or 0,
        "language": top[0] if top else "",
        "status": {"message": (status.get("message") or "").strip()},
    }


def measure(gh, mode: str, subject: str, here: str, *, today: str) -> dict:
    """The measurement: the mode, its subject, the README's repository, and on a profile the person.

    A mode of `auto`, or no subject, is settled from `here` the way a page is.
    """
    if mode == "auto" or not subject:
        mode, subject = mode_and_subject({"mode": mode, "subject": subject}, here)
    notes: list[str] = []
    result: dict = {"mode": mode, "subject": subject, "today": today}
    if mode == "profile":
        result["profile"] = profile(gh, subject, notes)
    target = subject if mode == "repository" else here
    owner, _, name = target.partition("/")
    try:
        result["repository"] = repository(gh, owner, name, notes)
    except RuntimeError as exc:
        if mode == "repository":
            raise
        # A profile measured from somewhere other than its own repository still has a header.
        notes.append(f"{exc}; the footer's licence and date are left off")
        result["repository"] = None
    result["notes"] = notes
    result["api"] = {"calls": gh.calls, "points": gh.points}
    return result


def settings(cfg: dict) -> dict:
    """The banners' own settings under the page's: the section, with the theme, the files' folder and the README."""
    section = cfg["banners"] if isinstance(cfg["banners"], dict) else banners_settings.check({})
    return section


def plan(measurement: dict, section: dict, *, theme: str, out: str, readme: str, draw: bool = True) -> dict:
    """Everything the banners write for this measurement: files by path, README blocks, notes and facts."""
    return banners_plan.plan(measurement, {**section, "theme": theme, "out": out, "readme_path": readme}, draw=draw)
