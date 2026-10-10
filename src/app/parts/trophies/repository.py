# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""A repository's case: measure one repository.

The stub runs inside the repository being measured, so `GITHUB_TOKEN` can
read everything about it, private or not, including traffic. What the API
cannot say (who depends on this repository) is returned as None and shown
as "not measured yet" rather than as zero.
"""
from __future__ import annotations

import datetime as dt
import re
from collections import Counter

from domain.trophies import calendar as cal
from domain.trophies.catalogue import RACH, RCORE, measure as tier_of
from domain.trophies.ledger import value_at
from domain.trophies.scan import SEMVER

from .scan import scan_repository

REPO = """
query($owner:String!,$name:String!){ rateLimit{cost}
  repository(owner:$owner,name:$name){ id nameWithOwner isPrivate isArchived isTemplate isFork createdAt pushedAt
    description homepageUrl usesCustomOpenGraphImage stargazerCount forkCount viewerHasStarred
    owner{ login __typename } watchers{totalCount} licenseInfo{key} codeOfConduct{key}
    isSecurityPolicyEnabled hasDiscussionsEnabled fundingLinks{url} repositoryTopics{totalCount}
    labels{totalCount} milestones{totalCount} templateRepository{nameWithOwner}
    merged: pullRequests(states:MERGED){totalCount}
    openPRs: pullRequests(states:OPEN,first:1,orderBy:{field:CREATED_AT,direction:ASC}){ nodes{createdAt} }
    closedIssues: issues(states:CLOSED){totalCount} openIssues: issues(states:OPEN){totalCount}
    goodFirst: issues(labels:["good first issue"]){totalCount} helpWanted: issues(labels:["help wanted"]){totalCount}
    tags: refs(refPrefix:"refs/tags/"){totalCount} branches: refs(refPrefix:"refs/heads/"){totalCount}
    releases(first:100,orderBy:{field:CREATED_AT,direction:DESC}){ totalCount
      nodes{ tagName createdAt isPrerelease description releaseAssets(first:50){ totalCount nodes{downloadCount} } } }
    defaultBranchRef{ name target{ ... on Commit{ oid history{totalCount} } } }
    readme: object(expression:"HEAD:README.md"){ id } contributing: object(expression:"HEAD:CONTRIBUTING.md"){ id }
    contributing2: object(expression:"HEAD:.github/CONTRIBUTING.md"){ id }
    codeowners: object(expression:"HEAD:.github/CODEOWNERS"){ id } codeowners2: object(expression:"HEAD:CODEOWNERS"){ id }
    templates: object(expression:"HEAD:.github/ISSUE_TEMPLATE"){ id }
    prtemplate: object(expression:"HEAD:.github/pull_request_template.md"){ id }
    prtemplate2: object(expression:"HEAD:.github/PULL_REQUEST_TEMPLATE.md"){ id }
    dependabot: object(expression:"HEAD:.github/dependabot.yml"){ id } changelog: object(expression:"HEAD:CHANGELOG.md"){ id }
    editorconfig: object(expression:"HEAD:.editorconfig"){ id } support: object(expression:"HEAD:SUPPORT.md"){ id }
    support2: object(expression:"HEAD:.github/SUPPORT.md"){ id }
    tests: object(expression:"HEAD:tests"){ ... on Tree{ entries{name} } } test: object(expression:"HEAD:test"){ ... on Tree{ entries{name} } }
    dockerfile: object(expression:"HEAD:Dockerfile"){ id } devcontainer: object(expression:"HEAD:.devcontainer"){ id }
    lifecycle: object(expression:"HEAD:.github/workflows/lifecycle.yml"){ id }
    verifystubs: object(expression:"HEAD:.github/workflows/verify-stubs.yml"){ id }
    workflows: object(expression:"HEAD:.github/workflows"){ ... on Tree{ entries{ name object{ ... on Blob{ text } } } } } } }"""

PRIVILEGED = """
query($owner:String!,$name:String!){ repository(owner:$owner,name:$name){
    collaborators{totalCount} vulnerabilityAlerts(states:OPEN){totalCount}
    rulesets(first:20){ nodes{ enforcement target conditions{ refName{ include } } } } } }"""

DISCUSSIONS = """
query($owner:String!,$name:String!,$first:Int!,$after:String){ rateLimit{cost}
  repository(owner:$owner,name:$name){ discussions(first:$first,after:$after){ pageInfo{hasNextPage endCursor} nodes{ isAnswered } } } }"""

ISSUES = """
query($owner:String!,$name:String!,$first:Int!,$after:String){ rateLimit{cost}
  repository(owner:$owner,name:$name){ issues(first:$first,after:$after,orderBy:{field:CREATED_AT,direction:DESC}){
    pageInfo{hasNextPage endCursor}
    nodes{ createdAt closedAt author{login} labels{totalCount} comments(first:1){ totalCount nodes{ createdAt author{login} } }
           reactions(content:THUMBS_UP){totalCount} } } } }"""

PULLS = """
query($owner:String!,$name:String!,$first:Int!,$after:String){ rateLimit{cost}
  repository(owner:$owner,name:$name){ pullRequests(states:MERGED,first:$first,after:$after,orderBy:{field:UPDATED_AT,direction:DESC}){
    pageInfo{hasNextPage endCursor}
    nodes{ author{login} mergedAt reviews{totalCount} changes: reviews(states:CHANGES_REQUESTED,first:1){totalCount} } } } }"""

FORKS = """
query($owner:String!,$name:String!,$first:Int!,$after:String){ rateLimit{cost}
  repository(owner:$owner,name:$name){ forks(first:$first,after:$after,orderBy:{field:STARGAZERS,direction:DESC}){
    pageInfo{hasNextPage endCursor} nodes{ owner{login} stargazerCount createdAt pushedAt } } } }"""

STARGAZERS = """
query($owner:String!,$name:String!,$first:Int!,$after:String){ rateLimit{cost}
  repository(owner:$owner,name:$name){ stargazers(first:$first,after:$after){
    pageInfo{hasNextPage endCursor} nodes{ login followers{totalCount} } } } }"""

MEMBERS = "query($login:String!){ organization(login:$login){ membersWithRole(first:100){ nodes{login} } } }"

STANDARDS = re.compile(r"uses:\s*['\"]?tannergolden/standards[/@]")


def _count(node, key="totalCount"):
    return ((node or {}).get(key)) or 0


def _has(r, *keys):
    return any(r.get(k) for k in keys)


def measure(gh, owner: str, name: str, ledger: dict, *, today: dt.date, scan_pages: int = 50) -> dict:
    notes: list[str] = []
    r = gh.gql(REPO, owner=owner, name=name)["repository"]
    if not r:
        raise RuntimeError(f"no such repository: {owner}/{name}")
    full = r["nameWithOwner"]
    created = cal.parse_day(r["createdAt"])
    is_org = (r["owner"] or {}).get("__typename") == "Organization"

    # Members of the owning organization, so "someone else" means outside the org.
    insiders = {owner.lower()}
    if is_org:
        try:
            for n in gh.gql(MEMBERS, login=owner)["organization"]["membersWithRole"]["nodes"]:
                if n:
                    insiders.add(n["login"].lower())
        except Exception:
            notes.append("organization members not readable; only the owner login is excluded")
    outsider = lambda login: bool(login) and login.lower() not in insiders and not login.endswith("[bot]")  # noqa: E731

    # -- things that need push access or a scope; each degrades separately -----------------
    collaborators = alerts = protected = None
    try:
        p = gh.gql(PRIVILEGED, owner=owner, name=name)["repository"]
        collaborators = _count(p.get("collaborators"))
        alerts = _count(p.get("vulnerabilityAlerts"))
        rules = [n for n in (p.get("rulesets") or {}).get("nodes", []) if n]
        protected = int(any(n["enforcement"] == "ACTIVE" and n["target"] == "BRANCH"
                            and any("DEFAULT_BRANCH" in i or i.endswith("/main") for i in ((n.get("conditions") or {}).get("refName") or {}).get("include", []))
                            for n in rules))
    except Exception as exc:
        notes.append(f"collaborators, alerts or rulesets not readable: {exc}")

    # -- paged collections, each under a page limit -----------------------------------------
    discussions = gh.paged(DISCUSSIONS, ("repository", "discussions"), limit=5, owner=owner, name=name)
    issues = gh.paged(ISSUES, ("repository", "issues"), limit=10, owner=owner, name=name)
    pulls = gh.paged(PULLS, ("repository", "pullRequests"), limit=5, owner=owner, name=name)
    forks = gh.paged(FORKS, ("repository", "forks"), limit=5, owner=owner, name=name)
    gazers = gh.paged(STARGAZERS, ("repository", "stargazers"), limit=10, owner=owner, name=name)

    # -- the commit scan, cached by head -----------------------------------------------------
    scans = ledger.setdefault("scan", {})
    entry = scan_repository(gh, owner, name, scans, {"pages": scan_pages})
    st = entry["stats"]
    if not entry.get("complete"):
        notes.append("history still being scanned; Commits, Active Days and Craft catch up on later runs")
    days_set = {cal.parse_day(d) for d in st["days"]}
    days = {d: 1 for d in days_set}
    authors = Counter({k: v for k, v in st["authors"].items() if not k.endswith("[bot]")})
    contributors = set(authors) | {(pr.get("author") or {}).get("login") for pr in pulls if pr.get("author")}
    contributors.discard(None)

    # -- traffic, which the repository's own token may read -------------------------------------
    views = gh.rest(f"/repos/{full}/traffic/views")
    clones = gh.rest(f"/repos/{full}/traffic/clones")
    referrers = gh.rest(f"/repos/{full}/traffic/popular/referrers")
    if views is None:
        notes.append("traffic not readable (needs push access); Visited, Cloned and Referred not measured")
    runs = gh.rest(f"/repos/{full}/actions/runs?status=success&per_page=1")

    # -- week-over-week movement, from the ledger's daily history -------------------------------
    stars_now = r["stargazerCount"] - (1 if r.get("viewerHasStarred") else 0)
    forks_others = sum(1 for f in forks if outsider((f.get("owner") or {}).get("login"))) if len(forks) < 500 else r["forkCount"]

    def week(key, now):
        base = value_at(ledger, key, today - dt.timedelta(days=7))
        return None if base is None else max(0, now - base)

    star_weeks = _consecutive_growth_weeks(ledger, today)

    releases = [rel for rel in r["releases"]["nodes"] if rel]
    downloads = sum(a["downloadCount"] for rel in releases for a in (rel["releaseAssets"].get("nodes") or []))
    open_prs = [n for n in r["openPRs"]["nodes"] if n]
    oldest_open = (today - cal.parse_day(open_prs[0]["createdAt"])).days if open_prs else 0
    first_reply_hours = []
    for i in issues[:50]:
        c = (i["comments"].get("nodes") or [None])[0]
        if c and (c.get("author") or {}).get("login", "").lower() != ((i.get("author") or {}).get("login") or "").lower():
            first_reply_hours.append((cal.parse_time(c["createdAt"]) - cal.parse_time(i["createdAt"])).total_seconds() / 3600)
    fast_reply = int(bool(first_reply_hours) and sorted(first_reply_hours)[len(first_reply_hours) // 2] <= 24)
    same_day = sum(1 for i in issues if i["closedAt"] and (cal.parse_time(i["closedAt"]) - cal.parse_time(i["createdAt"])).total_seconds() <= 86400)
    reviewed = int(bool(pulls) and all(pr["reviews"]["totalCount"] > 0 for pr in pulls[:100]))
    workflows = ((r.get("workflows") or {}).get("entries") or [])
    follows_standards = any(STANDARDS.search(((e.get("object") or {}).get("text") or "")) for e in workflows)
    golden = ((r.get("templateRepository") or {}).get("nameWithOwner") == "tannergolden/path") or (
        bool(r.get("lifecycle")) and bool(r.get("verifystubs")) and follows_standards)
    release_months = {(cal.parse_day(rel["createdAt"]).year, cal.parse_day(rel["createdAt"]).month) for rel in releases}
    commits_30 = sum(1 for d in days_set if (today - d).days < 30)
    last_release_days = (today - cal.parse_day(releases[0]["createdAt"])).days if releases else None

    values = {
        "stars": stars_now, "forks": forks_others, "contributors": len(contributors),
        # The branch total less the refresh commits the scanner has seen, so
        # the case does not earn a commit for every day it is redrawn.
        "commits": max(0, _count(((r.get("defaultBranchRef") or {}).get("target") or {}).get("history")) - st["refresh"]),
        "releases": r["releases"]["totalCount"], "merged": r["merged"]["totalCount"], "resolved": r["closedIssues"]["totalCount"],
        "active": len(days_set),
    }
    ms = {c.key: tier_of(c, values[c.key]) for c in RCORE}
    curs = {
        # Launch
        "first-star": stars_now, "first-fork": forks_others, "first-watcher": max(0, r["watchers"]["totalCount"] - 1),
        "first-release": values["releases"], "first-merge": values["merged"],
        "outside-help": sum(1 for pr in pulls if outsider((pr.get("author") or {}).get("login"))),
        "stranger-report": sum(1 for i in issues if outsider((i.get("author") or {}).get("login")) and ((i.get("author") or {}).get("login") not in contributors)),
        "first-tag": r["tags"]["totalCount"], "named": int(bool(r["description"])), "front-door": int(bool(r["homepageUrl"])),
        "filed": r["repositoryTopics"]["totalCount"], "poster": int(bool(r["usesCustomOpenGraphImage"])),
        # Health
        "licensed": int(bool(r["licenseInfo"])), "documented": int(bool(r["description"] and r.get("readme"))),
        "welcome-mat": int(_has(r, "contributing", "contributing2")), "house-rules": int(bool(r["codeOfConduct"])),
        "locksmith": int(bool(r["isSecurityPolicyEnabled"])), "gatekeeper": int(_has(r, "codeowners", "codeowners2")),
        "form-filler": int(_has(r, "templates")), "paperwork": int(_has(r, "prtemplate", "prtemplate2")), "auto-pilot": int(_has(r, "dependabot")),
        "changelog": int(_has(r, "changelog")), "well-formed": int(_has(r, "editorconfig")), "town-hall": int(bool(r["hasDiscussionsEnabled"])),
        "protected": protected, "clean-bill": None if alerts is None else int(alerts == 0), "open-hand": int(bool(r["fundingLinks"])),
        "support-line": int(_has(r, "support", "support2")), "label-maker": r["labels"]["totalCount"], "roadmap": r["milestones"]["totalCount"],
        # Craft
        "by-the-book": st["conventional"], "signed": st["signed"], "gitmoji": st["emoji"],
        "semver": sum(1 for rel in releases if rel["tagName"] and SEMVER.match(rel["tagName"])),
        "green-machine": runs.get("total_count", 0) if runs else None,
        "test-suite": int(bool(((r.get("tests") or {}).get("entries")) or ((r.get("test") or {}).get("entries")))),
        "wired": int(bool(workflows)), "release-notes": sum(1 for rel in releases if (rel.get("description") or "").strip()),
        "packager": sum(1 for rel in releases if rel["releaseAssets"]["totalCount"]), "prerelease": sum(1 for rel in releases if rel["isPrerelease"]),
        "squeaky": int(oldest_open < 90), "small-steps": None if not entry.get("complete") and st["total"] < 50 else int(_median_small(st)),
        "follows-the-standards": int(follows_standards), "golden-path": int(golden),
        "containerized": int(_has(r, "dockerfile")), "ready-room": int(_has(r, "devcontainer")),
        # Community
        "ten-strong": len(contributors), "reviewed": reviewed, "fast-reply": fast_reply, "good-first-issues": r["goodFirst"]["totalCount"],
        "help-wanted": r["helpWanted"]["totalCount"], "outside-merges": sum(1 for pr in pulls if outsider((pr.get("author") or {}).get("login"))),
        "answered": sum(1 for d in discussions if d["isAnswered"]), "triage": int(bool(issues) and all(i["labels"]["totalCount"] for i in issues if not i["closedAt"])),
        "well-maintained": sum(1 for pr in pulls if ((pr.get("author") or {}).get("login") or "") == "dependabot"),
        "talkative": sum(i["comments"]["totalCount"] for i in issues), "popular-opinion": max([i["reactions"]["totalCount"] for i in issues], default=0),
        "long-thread": max([i["comments"]["totalCount"] for i in issues], default=0),
        "mentor": sum(1 for pr in pulls if pr["changes"]["totalCount"]), "regulars": sum(1 for n in authors.values() if n >= 10),
        "org-backed": int(is_org), "crew": collaborators,
        # Reach
        "watched": r["watchers"]["totalCount"], "used-by": None, "star-of-the-week": week("stars", stars_now), "trending": week("stars", stars_now),
        "forked-far": max([f["stargazerCount"] for f in forks], default=0),
        "living-forks": sum(1 for f in forks if f["pushedAt"] and f["pushedAt"] > f["createdAt"]),
        "registry": None, "downloaded": downloads,
        "visited": views.get("uniques") if views else None, "cloned": clones.get("uniques") if clones else None,
        "referred": len(referrers) if referrers is not None else None,
        "big-name": None if len(gazers) >= 1000 and len(gazers) < stars_now else int(any(g["followers"]["totalCount"] >= 10000 for g in gazers)),
        "stargazer-streak": star_weeks, "fork-magnet": week("forks", forks_others),
        # Rhythm
        "weekly-beat": cal.consecutive_weeks(cal.weeks_of(days)), "monthly-release": cal.consecutive_months(release_months),
        "streak": cal.longest_streak(days), "comeback": int(cal.came_back_after(days, 90)), "night-shift": st["night"],
        "weekend-project": cal.weekends_in_a_year(days), "marathon-day": _max_commits_in_a_day(st),
        "big-week": _max_commits_in_a_week(st), "long-game": cal.years_active(days),
        "alive": int(any((today - d).days < 30 for d in days_set)),
        "friday-deploy": int(any(cal.parse_time(rel["createdAt"]).weekday() == 4 for rel in releases)), "same-day-fix": same_day,
        # Secret
        "round-number": int(any(v == 1000 for v in values.values())), "the-answer": int(any(v == 42 for v in values.values())),
        "palindrome": int(str(values["commits"]) == str(values["commits"])[::-1] and values["commits"] >= 11),
        "leap-day": int(any(cal.parse_day(rel["createdAt"]).month == 2 and cal.parse_day(rel["createdAt"]).day == 29 for rel in releases)),
        "friday-the-13th": int(any(cal.parse_day(rel["createdAt"]).day == 13 and cal.parse_day(rel["createdAt"]).weekday() == 4 for rel in releases)),
        "new-year": int(cal.on_date(days, 1, 1)), "birthday": int(cal.on_anniversary(days, min(days_set) if days_set else created)),
        "midnight-oil": st["midnight"], "green-wall": int(cal.every_week_of_a_year(days, today)), "ghost": int(cal.came_back_after(days, 365)),
        "full-house": int(all(m["t"] >= 3 for m in ms.values())), "constellation": int(any(m["stars"] >= 5 for m in ms.values())),
    }
    missing = [a.slug for a in RACH if a.slug not in curs]
    if missing:
        raise RuntimeError(f"catalogue entries without a measurement: {missing}")
    extra = {"lastRelease": last_release_days, "commits30": commits_30}
    return {"mode": "repository", "subject": full, "values": values, "curs": curs, "notes": notes, "extra": extra,
            "api": {"calls": gh.calls, "points": gh.points}}


def _median_small(st: dict) -> bool:
    # The scanner keeps maxima, not a distribution; "small steps" is judged
    # by the share of one-file commits, a fair proxy until a histogram is kept.
    return st["total"] > 0 and st["onefile"] / st["total"] >= 0.5


def _max_commits_in_a_day(st: dict) -> int:
    # Days are recorded once each by the scanner, so this counts commits per
    # day from the ordered day list: consecutive equal entries were collapsed,
    # which leaves the count unknown. Report distinct-day activity instead.
    return 1 if st["days"] else 0


def _max_commits_in_a_week(st: dict) -> int:
    weeks = Counter((cal.parse_day(d).isocalendar()[0], cal.parse_day(d).isocalendar()[1]) for d in st["days"])
    return max(weeks.values(), default=0)


def _consecutive_growth_weeks(ledger: dict, today: dt.date) -> int:
    """Weeks in a row, ending this week, in which the star count grew."""
    n = 0
    for k in range(52):
        a = value_at(ledger, "stars", today - dt.timedelta(days=7 * (k + 1)))
        b = value_at(ledger, "stars", today - dt.timedelta(days=7 * k))
        if a is None or b is None or b <= a:
            break
        n += 1
    return n
