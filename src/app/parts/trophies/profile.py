# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""A profile's case: measure a person.

Everything a profile case shows comes out of `measure(gh, login, ...)` as one
dict: the eight core values, a value per achievement slug (or None where the
run could not measure it), and a few extras for the level card. The GraphQL
here is written out in full so a reader can see exactly what is counted.
"""
from __future__ import annotations

import datetime as dt

from domain.trophies import calendar as cal
from domain.trophies.catalogue import ACH, CORE, measure as tier_of
from domain.trophies.scan import SEMVER, merge_stats, without_refreshes

from .scan import scan_repository

USER = """
query($login:String!){ rateLimit{cost}
  user(login:$login){ id login createdAt bio location websiteUrl
    followers{totalCount} following{totalCount}
    starredRepositories{totalCount} pullRequests{totalCount} issues{totalCount}
    repositoryDiscussions{totalCount}
    answers: repositoryDiscussionComments(onlyAnswers:true){totalCount}
    discussionComments: repositoryDiscussionComments{totalCount}
    issueComments{totalCount}
    publicRepos: repositories(ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC){totalCount}
    contributionsCollection{ contributionYears }
    profileReadme: repository(name:$login){ id } } }"""

PACKAGES = "query($login:String!){ user(login:$login){ packages{totalCount} } }"

# Each of these needs a scope the Actions token may lack (read:project for
# projects, read:org for memberships, and sponsorships vary by account). A
# field that errors nulls the whole `user` it sits in, so each is asked for
# on its own and answers None rather than taking the run down.
ORGANIZATIONS = "query($login:String!){ user(login:$login){ organizations{totalCount} } }"
SPONSORING = "query($login:String!){ user(login:$login){ sponsoring{totalCount} } }"
SPONSORS = "query($login:String!){ user(login:$login){ sponsors{totalCount} } }"
PROJECTS = "query($login:String!){ user(login:$login){ projectsV2{totalCount} } }"
GISTS = "query($login:String!){ user(login:$login){ gists(privacy:PUBLIC){totalCount} } }"  # refused to an Actions token
VIEWER = """
query{ viewer{ login organizations(first:50){ nodes{ viewerCanAdminister } }
  collaborating: repositories(affiliations:[COLLABORATOR]){totalCount} } }"""

YEAR = """
query($login:String!,$from:DateTime!,$to:DateTime!){ rateLimit{cost}
  user(login:$login){ contributionsCollection(from:$from,to:$to){
    totalCommitContributions totalPullRequestReviewContributions restrictedContributionsCount
    contributionCalendar{ weeks{ contributionDays{ date contributionCount } } } } } }"""

REPOS = """
query($login:String!,$id:ID!,$first:Int!,$after:String){ rateLimit{cost}
  user(login:$login){ repositories(ownerAffiliations:OWNER,first:$first,after:$after,orderBy:{field:PUSHED_AT,direction:DESC}){
    pageInfo{hasNextPage endCursor}
    nodes{ name nameWithOwner isFork isPrivate isArchived isTemplate createdAt pushedAt description homepageUrl
      stargazerCount forkCount viewerHasStarred watchers{totalCount} isSecurityPolicyEnabled hasDiscussionsEnabled
      licenseInfo{key} codeOfConduct{key} fundingLinks{url} repositoryTopics{totalCount} labels{totalCount} milestones{totalCount}
      closedIssues: issues(states:CLOSED){totalCount} openIssues: issues(states:OPEN){totalCount}
      languages(first:30){ nodes{name} }
      branches: refs(refPrefix:"refs/heads/"){totalCount}
      releases(first:50,orderBy:{field:CREATED_AT,direction:DESC}){ totalCount nodes{ tagName createdAt isPrerelease releaseAssets{totalCount} } }
      defaultBranchRef{ name target{ ... on Commit{ oid mine: history(author:{id:$id}){totalCount} } } }
      readme: object(expression:"HEAD:README.md"){ id } contributing: object(expression:"HEAD:CONTRIBUTING.md"){ id }
      contributing2: object(expression:"HEAD:.github/CONTRIBUTING.md"){ id }
      codeowners: object(expression:"HEAD:.github/CODEOWNERS"){ id } codeowners2: object(expression:"HEAD:CODEOWNERS"){ id }
      dependabot: object(expression:"HEAD:.github/dependabot.yml"){ id } action: object(expression:"HEAD:action.yml"){ id }
      templates: object(expression:"HEAD:.github/ISSUE_TEMPLATE"){ id } } } } }"""

SEARCH = """
query($merged:String!,$upstream:String!,$opendoor:String!,$reporter:String!,$reviews:String!,$approved:String!,$changes:String!,$bot:String!,$bugs:String!,$voice:String!){ rateLimit{cost}
  merged: search(type:ISSUE,query:$merged){issueCount} upstream: search(type:ISSUE,query:$upstream){issueCount}
  opendoor: search(type:ISSUE,query:$opendoor){issueCount} reporter: search(type:ISSUE,query:$reporter){issueCount}
  reviews: search(type:ISSUE,query:$reviews){issueCount} approved: search(type:ISSUE,query:$approved){issueCount}
  changes: search(type:ISSUE,query:$changes){issueCount} bot: search(type:ISSUE,query:$bot){issueCount}
  bugs: search(type:ISSUE,query:$bugs){issueCount} voice: search(type:ISSUE,query:$voice){issueCount} }"""

OWNER = "query($owner:String!,$name:String!){ repository(owner:$owner,name:$name){ owner{login} } }"


def owner_of(gh, repo: str):
    owner, _, name = repo.partition("/")
    try:
        data = gh.gql(OWNER, owner=owner, name=name)
    except Exception:
        return None
    return (((data or {}).get("repository") or {}).get("owner") or {}).get("login")


def _count(node, key="totalCount"):
    return ((node or {}).get(key)) or 0


def _optional(gh, query: str, login: str, field: str, notes: list) -> int | None:
    """One user field the token may not be allowed to read: its count, or None."""
    try:
        u = gh.gql(query, login=login)["user"]
    except Exception as exc:
        notes.append(f"{field} not readable with this token ({exc})")
        return None
    if not u:
        notes.append(f"{field} not readable with this token")
        return None
    return _count(u.get(field))


def measure(gh, login: str, ledger: dict, *, today: dt.date, private: bool = False, scan_pages: int = 30,
            run_repos: int = 30) -> dict:
    notes: list[str] = []
    u = gh.gql(USER, login=login)["user"]
    if not u:
        why = "; ".join(getattr(gh, "last_errors", []) or []) or "no such user"
        raise RuntimeError(f"cannot read user {login}: {why}")
    uid = u["id"]
    created = cal.parse_day(u["createdAt"])

    # -- the contribution calendar, one query per year --------------------------------
    days: dict = {}
    commits = reviews = 0
    for year in u["contributionsCollection"]["contributionYears"]:
        frm = f"{year}-01-01T00:00:00Z"
        to = f"{year}-12-31T23:59:59Z"
        cc = gh.gql(YEAR, login=login, **{"from": frm, "to": to})["user"]["contributionsCollection"]
        commits += cc["totalCommitContributions"] + (cc["restrictedContributionsCount"] if private else 0)
        reviews += cc["totalPullRequestReviewContributions"]
        for w in cc["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                if d["contributionCount"]:
                    days[cal.parse_day(d["date"])] = d["contributionCount"]

    # -- every repository the account owns -------------------------------------------
    repos = gh.paged(REPOS, ("user", "repositories"), limit=10, login=login, id=uid)
    own = [r for r in repos if not r["isFork"]]
    own_public = [r for r in own if not r["isPrivate"]]
    if not private:
        own = own_public
    stars = sum(r["stargazerCount"] - (1 if r.get("viewerHasStarred") else 0) for r in own)
    languages = {n["name"] for r in own for n in (r.get("languages") or {}).get("nodes", [])}
    releases = [rel for r in own for rel in (r["releases"].get("nodes") or [])]

    # -- searches: ten counts in one query --------------------------------------------
    q = lambda s: s.replace("@", login)  # noqa: E731
    s = gh.gql(SEARCH, merged=q("is:pr is:merged author:@"), upstream=q("is:pr is:merged author:@ -user:@"),
               opendoor=q("is:pr is:merged user:@ -author:@"), reporter=q("is:issue author:@ -user:@"),
               reviews=q("is:pr reviewed-by:@ -user:@"), approved=q("is:pr reviewed-by:@ review:approved"),
               changes=q("is:pr reviewed-by:@ review:changes_requested"), bot=q("is:pr is:merged author:app/dependabot user:@"),
               bugs=q("is:issue author:@ is:closed reason:completed"), voice=q("is:issue commenter:@ -user:@"))
    count = lambda k: _count(s.get(k), "issueCount")  # noqa: E731

    # -- things only the token's own account can answer ----------------------------------
    founder = crew = packages = None
    organizations = _optional(gh, ORGANIZATIONS, login, "organizations", notes)
    sponsoring = _optional(gh, SPONSORING, login, "sponsoring", notes)
    sponsors = _optional(gh, SPONSORS, login, "sponsors", notes)
    projects = _optional(gh, PROJECTS, login, "projectsV2", notes)
    gists = _optional(gh, GISTS, login, "gists", notes)
    try:
        v = gh.gql(VIEWER)["viewer"]
        if v["login"].lower() == login.lower():
            founder = sum(1 for o in v["organizations"]["nodes"] if o and o["viewerCanAdminister"])
            crew = v["collaborating"]["totalCount"]
    except Exception as exc:  # a fine-grained token without the scope
        notes.append(f"viewer query skipped: {exc}")
    try:
        packages = gh.gql(PACKAGES, login=login)["user"]["packages"]["totalCount"]
    except Exception:
        notes.append("packages not readable with this token (read:packages)")

    # -- the heavy part: read commits, under a budget, cached in the ledger ---------------
    scans = ledger.setdefault("scan", {})
    budget = {"pages": scan_pages}
    for r in sorted(own, key=lambda r: r["pushedAt"] or "", reverse=True):
        if budget["pages"] <= 0:
            break
        if _count(((r.get("defaultBranchRef") or {}).get("target") or {}).get("mine")):
            o, n = r["nameWithOwner"].split("/", 1)
            scan_repository(gh, o, n, scans, budget, author_id=uid)
    entries = [scans[r["nameWithOwner"]] for r in own if r["nameWithOwner"] in scans]
    incomplete = sum(1 for e in entries if not e.get("complete"))
    st = merge_stats(entries)
    # A refresh commit authored by the subject counts in GitHub's calendar
    # and totals like any other; the scanner knows which they were.
    commits = max(0, commits - st["refresh"])
    days = without_refreshes(days, st)
    refreshed_in = {r["nameWithOwner"]: (scans[r["nameWithOwner"]].get("stats") or {}).get("refresh", 0)
                    for r in own if r["nameWithOwner"] in scans}
    if incomplete:
        notes.append(f"{incomplete} repositories still being scanned; heavy achievements catch up on later runs")

    # -- successful workflow runs, one REST call per recently pushed repository ----------
    runs = 0
    for r in sorted(own, key=lambda r: r["pushedAt"] or "", reverse=True)[:run_repos]:
        data = gh.rest(f"/repos/{r['nameWithOwner']}/actions/runs?status=success&per_page=1")
        if data:
            runs += data.get("total_count", 0)

    # -- core values --------------------------------------------------------------------
    values = {
        "commits": commits, "pulls": u["pullRequests"]["totalCount"], "reviews": reviews, "issues": u["issues"]["totalCount"],
        "stars": stars, "followers": u["followers"]["totalCount"], "streak": cal.longest_streak(days),
        "repos": len(own_public),
    }
    ms = {c.key: tier_of(c, values[c.key]) for c in CORE}

    # -- achievements, by slug ---------------------------------------------------------------
    has = lambda r, *keys: any(r.get(k) for k in keys)  # noqa: E731
    per_repo = lambda pred: sum(1 for r in own if pred(r))  # noqa: E731
    mine = lambda r: max(0, _count(((r.get("defaultBranchRef") or {}).get("target") or {}).get("mine")) - refreshed_in.get(r["nameWithOwner"], 0))  # noqa: E731
    years_on = (today - created).days // 365
    friday_release = any(cal.parse_time(rel["createdAt"]).weekday() == 4 for rel in releases)
    curs = {
        # Milestones
        "hello-world": commits, "first-light": len(own_public), "opening-move": values["pulls"], "landed": count("merged"),
        "ticket": values["issues"], "second-opinion": reviews, "shipped": sum(r["releases"]["totalCount"] for r in own),
        "shipwright": sum(r["releases"]["totalCount"] for r in own), "merge-master": count("merged"), "polyglot": len(languages),
        "veteran": years_on, "century": max([mine(r) for r in own], default=0), "monolith": max([mine(r) for r in own], default=0),
        "long-haul": per_repo(lambda r: (cal.parse_day(r["pushedAt"]) - cal.parse_day(r["createdAt"])).days >= 5 * 365 if r["pushedAt"] else False),
        "stargazer": max([r["stargazerCount"] - (1 if r.get("viewerHasStarred") else 0) for r in own], default=0),
        "forked": sum(r["forkCount"] for r in own), "watched": max([r["watchers"]["totalCount"] for r in own], default=0),
        "bug-hunter": count("bugs"), "closer": sum(r["closedIssues"]["totalCount"] for r in own),
        "inbox-zero": int(sum(r["closedIssues"]["totalCount"] for r in own) >= 25
                          and not any(r["openIssues"]["totalCount"] for r in own)),
        "fan-club": sum(r["watchers"]["totalCount"] for r in own), "branching-out": max([r["branches"]["totalCount"] for r in own], default=0),
        # Craft
        "by-the-book": st["conventional"], "gitmoji": st["emoji"], "signed": st["signed"], "duet": st["coauthored"], "undo": st["revert"],
        "surgeon": st["onefile"], "fixer": st["fix"], "tested": st["test"], "scribe": st["docs"], "green-machine": runs,
        "well-maintained": count("bot"), "toolsmith": per_repo(lambda r: has(r, "action")),
        "heavy-lifter": st["heavy"], "sweeping-change": st["sweeping"],
        # Rhythm
        "perfect-month": cal.perfect_months(days), "weekender": cal.weekends_in_a_year(days), "night-owl": st["night"], "early-bird": st["early"],
        "marathon-day": cal.max_in_a_day(days), "big-week": cal.max_in_a_week(days), "sprint": cal.max_in_a_month(days),
        "weekday-warrior": cal.weekdays_in_a_year(days), "year-of-code": cal.max_days_in_a_year(days),
        "four-seasons": int(cal.all_twelve_months(days)), "long-game": cal.years_active(days), "comeback": int(cal.came_back_after(days, 90)),
        "friday-deploy": int(friday_release), "lunch-break": st["lunch"],
        # Community
        "upstream": count("upstream"), "open-door": count("opendoor"), "second-pair-of-eyes": count("reviews"), "reporter": count("reporter"),
        "voice": count("voice"), "answer-key": u["answers"]["totalCount"], "conversation-starter": u["repositoryDiscussions"]["totalCount"],
        "team-player": organizations, "founder": founder, "crew": crew, "generous": u["starredRepositories"]["totalCount"],
        "curious": u["following"]["totalCount"], "patron": sponsoring, "backed": sponsors,
        "gist-keeper": gists, "planner": projects, "registry": packages,
        "introduced": int(bool(u["bio"] and u["location"] and u["websiteUrl"] and u["profileReadme"])),
        "green-light": count("approved"), "red-pen": count("changes"), "roundtable": u["discussionComments"]["totalCount"],
        # Housekeeping
        "licensed": per_repo(lambda r: r["licenseInfo"]), "documented": per_repo(lambda r: r["description"] and r.get("readme")),
        "curator": per_repo(lambda r: r["repositoryTopics"]["totalCount"]), "front-door": per_repo(lambda r: r["homepageUrl"]),
        "welcome-mat": per_repo(lambda r: has(r, "contributing", "contributing2")), "house-rules": per_repo(lambda r: r["codeOfConduct"]),
        "locksmith": per_repo(lambda r: r["isSecurityPolicyEnabled"]), "gatekeeper": per_repo(lambda r: has(r, "codeowners", "codeowners2")),
        "auto-pilot": per_repo(lambda r: has(r, "dependabot")), "blueprint": per_repo(lambda r: r["isTemplate"]),
        "open-hand": per_repo(lambda r: r["fundingLinks"]), "town-hall": per_repo(lambda r: r["hasDiscussionsEnabled"]),
        "tidy": sum(1 for r in repos if r["isArchived"]), "packager": sum(1 for rel in releases if rel["releaseAssets"]["totalCount"]),
        "semver": sum(1 for rel in releases if rel["tagName"] and SEMVER.match(rel["tagName"])),
        "form-filler": per_repo(lambda r: has(r, "templates")), "roadmap": max([r["milestones"]["totalCount"] for r in own], default=0),
        "label-maker": max([r["labels"]["totalCount"] for r in own], default=0),
        # Secret
        "new-year": int(cal.on_date(days, 1, 1)), "leap-day": int(cal.on_date(days, 2, 29)), "green-wall": int(cal.every_week_of_a_year(days, today)),
        "homecoming": int(cal.on_anniversary(days, created)), "friday-the-13th": int(cal.on_friday_13th(days)), "midnight-oil": st["midnight"],
        "the-answer": int(any(v == 42 for v in values.values())), "round-number": int(any(v == 1000 for v in values.values())),
        "full-house": int(all(m["t"] >= 3 for m in ms.values())), "constellation": int(any(m["stars"] >= 5 for m in ms.values())),
        "ghost": int(cal.came_back_after(days, 365)),
        # Maker: 1 when the subject owns the named repository; visibility is decided elsewhere
        "trophy-maker": 1, "badge-maker": 1, "standard-bearer": 1, "pathfinder": 1,
    }
    missing = [a.slug for a in ACH if a.slug not in curs]
    if missing:
        raise RuntimeError(f"catalogue entries without a measurement: {missing}")
    return {
        "mode": "profile", "subject": login, "values": values, "curs": curs, "notes": notes,
        "extra": {"currentStreak": cal.current_streak(days, today), "streak": values["streak"], "years": years_on},
        "api": {"calls": gh.calls, "points": gh.points},
    }
