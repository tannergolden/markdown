# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The catalogue: what a trophy case can hold, in both modes.

Everything a run measures or draws is described here as plain data, so the
catalogue page, the tests and the drawing cannot disagree. A core trophy has
five thresholds (Bronze to Diamond); past Diamond it earns a star each time
the Diamond number doubles, up to five. An achievement has one goal, or
several for a tiered one, and a rarity per tier that decides its metal.

Enamel colours are palette tokens and the icons are the kit's own, so a case
matches the badges and banners beside it. Five icons are the case's alone:
`pull`, `issue`, `q` and `tick`, and its `check`, which is a tick in a ring.

This file is data. `markdown-kit catalogue` writes docs/Catalogue.md from it.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..palette import ICONS as SHARED_ICONS
from ..palette import PALETTE

TIER_NAMES = ("Unranked", "Bronze", "Silver", "Gold", "Platinum", "Diamond")
RARITY_NAMES = ("", "Common", "Uncommon", "Rare", "Epic", "Legendary")
ROMAN = ("", "I", "II", "III", "IV", "V")
MAX_STARS = 5

# Metal ramps per tier: dark, mid, light, highlight.
TIERS = [
    {
        "name": "Unranked",
        "d": "#252A32",
        "m": "#3A414B",
        "l": "#5A626D",
        "h": "#838B96"
    },
    {
        "name": "Bronze",
        "d": "#4A2711",
        "m": "#8F5125",
        "l": "#CC8850",
        "h": "#F5C69A"
    },
    {
        "name": "Silver",
        "d": "#4E5661",
        "m": "#98A2AD",
        "l": "#D4DAE0",
        "h": "#FFFFFF"
    },
    {
        "name": "Gold",
        "d": "#6B4306",
        "m": "#BE8818",
        "l": "#EDC34A",
        "h": "#FFF1B5"
    },
    {
        "name": "Platinum",
        "d": "#3F4F66",
        "m": "#8FA6C0",
        "l": "#D3E4F4",
        "h": "#FFFFFF"
    },
    {
        "name": "Diamond",
        "d": "#2C3A96",
        "m": "#5CB6EC",
        "l": "#C2B3FF",
        "h": "#FFFFFF"
    }
]

# The enamel colours: palette tokens, in the order the catalogue page lists them.
PAL = {k: PALETTE[k] for k in (
    "emerald", "violet", "azure", "crimson", "amber", "rose", "tangerine", "turquoise",
    "coral", "amethyst", "teal", "jade", "plum", "brown", "indigo", "honey",
    "forest", "apricot", "cobalt", "denim", "sky", "fuchsia", "mustard", "aqua",
    "lime", "salmon", "cherry", "navy", "steel", "moss", "sage", "ocean",
    "iris", "mauve", "orchid", "clay", "taupe", "lavender", "mint", "cyan",
    "peach", "magenta", "ruby", "maroon", "ash", "brick", "tan", "orange",
    "purple", "olive", "gold",
)}

# The case's own icons, beside the kit's 64: a pull request, an issue, a question mark for a secret, and
# its check, a tick in a ring. The kit's own check is the case's tick.
_OWN = {
    "pull": "<circle cx=\"6\" cy=\"5.5\" r=\"2.4\"/><circle cx=\"6\" cy=\"18.5\" r=\"2.4\"/><circle cx=\"18\" cy=\"18.5\" r=\"2.4\"/><path d=\"M6 7.9v8.2M18 16.1V9a3 3 0 0 0-3-3h-4M13.5 3.5L11 6l2.5 2.5\"/>",
    "issue": "<circle cx=\"12\" cy=\"12\" r=\"9\"/><circle cx=\"12\" cy=\"12\" r=\"1.6\"/>",
    "check": "<circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M8 12l3 3 5-6\"/>",
    "q": "<path d=\"M9.5 9a2.5 2.5 0 1 1 3.8 2.1c-.8.5-1.3 1-1.3 1.9v.5\"/><path d=\"M12 17h.01\"/>",
    "tick": SHARED_ICONS["check"],
}
ICONS = {k: _OWN[k] if k in _OWN else SHARED_ICONS[k] for k in (
    "commit", "pull", "eye", "issue", "star", "users", "flame", "book",
    "trophy", "rocket", "code", "branch", "tag", "clock", "calendar", "flag",
    "bolt", "chart", "moon", "sun", "upload", "check", "chat", "layers",
    "heart", "sparkle", "target", "grid", "home", "q", "pulse", "shield",
    "scale", "tick", "cross", "gear", "arrow", "lock", "search", "package",
    "download", "cloud", "terminal", "bug", "flask", "database", "key", "globe",
    "medal", "chip", "link", "folder", "sync", "alert", "info", "play",
    "server", "bell", "mail", "pin", "compass", "wrench", "trash", "plus",
    "infinity",
)}


@dataclass(frozen=True)
class Core:
    """A core trophy: a count that only grows, cut into five tiers."""

    key: str
    title: str
    icon: str
    tok: str
    steps: tuple
    counts: str
    src: str
    word: str
    unit: str = ""

    @property
    def hue(self) -> str:
        return PAL[self.tok]


@dataclass(frozen=True)
class Achievement:
    """An achievement: earned or not, or earned in tiers."""

    name: str
    g: int
    icon: str
    tok: str
    rarity: object  # int, or a tuple with one entry per tier
    how: str
    src: str
    goal: int = 1
    goals: tuple = ()
    word: str = ""
    heavy: bool = False  # reads individual commits, so it runs under a budget
    passive: bool = False  # time does the work, so it stays out of "next up"
    secret: bool = False  # a question mark until earned
    only: str = ""  # owner/repo whose owner alone can hold this

    @property
    def hue(self) -> str:
        return PAL[self.tok]

    @property
    def tiers(self) -> tuple:
        return tuple(self.goals) if self.goals else (self.goal,)

    @property
    def rarities(self) -> tuple:
        return tuple(self.rarity) if isinstance(self.rarity, (list, tuple)) else (self.rarity,)

    @property
    def slug(self) -> str:
        s = "".join(c if c.isalnum() else "-" for c in self.name.lower())
        while "--" in s:
            s = s.replace("--", "-")
        return s.strip("-")


def C(**kw) -> Core:
    kw["steps"] = tuple(kw["steps"])
    return Core(**kw)


def A(**kw) -> Achievement:
    if "goals" in kw:
        kw["goals"] = tuple(kw["goals"])
    if isinstance(kw.get("rarity"), list):
        kw["rarity"] = tuple(kw["rarity"])
    return Achievement(**kw)


# --- Profile mode: the subject is a person -----------------------------------
CORE = [
    C(key="commits", title="Commits", icon="commit", tok="emerald", steps=[100, 500, 2000, 5000, 10000], counts="Commit contributions, all years", src="contributionsCollection.totalCommitContributions, summed per year", word="commits"),
    C(key="pulls", title="Pull Requests", icon="pull", tok="violet", steps=[5, 25, 100, 250, 1000], counts="Pull requests opened", src="user.pullRequests.totalCount", word="pull requests"),
    C(key="reviews", title="Reviews", icon="eye", tok="azure", steps=[5, 25, 100, 250, 1000], counts="Pull request reviews submitted", src="totalPullRequestReviewContributions, summed per year", word="reviews"),
    C(key="issues", title="Issues", icon="issue", tok="crimson", steps=[5, 25, 100, 250, 1000], counts="Issues opened", src="user.issues.totalCount", word="issues"),
    C(key="stars", title="Stars Earned", icon="star", tok="amber", steps=[10, 50, 250, 1000, 5000], counts="Stars from others on repositories you created", src="repositories(ownerAffiliations: OWNER, isFork: false).stargazerCount", word="stars"),
    C(key="followers", title="Followers", icon="users", tok="rose", steps=[25, 100, 350, 1000, 2500], counts="Followers", src="user.followers.totalCount", word="followers"),
    C(key="streak", title="Longest Streak", icon="flame", tok="tangerine", steps=[7, 30, 100, 200, 365], counts="Longest run of days with a contribution", src="contributionCalendar days, all years", word="days", unit="days"),
    C(key="repos", title="Repositories", icon="book", tok="turquoise", steps=[5, 15, 30, 60, 100], counts="Public repositories you created, not forks", src="repositories(isFork: false, privacy: PUBLIC).totalCount", word="repositories"),
]

GROUPS = ["Milestones", "Craft", "Rhythm", "Community", "Housekeeping", "Secret", "Maker"]

ACH = [
    A(name="Hello World", g=0, icon="commit", tok="emerald", rarity=1, how="Make your first commit", src="contributionsCollection.totalCommitContributions"),
    A(name="First Light", g=0, icon="rocket", tok="coral", rarity=1, how="Publish your first public repository", src="repositories(privacy: PUBLIC).totalCount"),
    A(name="Opening Move", g=0, icon="pull", tok="violet", rarity=1, how="Open your first pull request", src="user.pullRequests.totalCount"),
    A(name="Landed", g=0, icon="tick", tok="jade", rarity=2, how="Get your first pull request merged", src="search: is:pr is:merged author:you"),
    A(name="Ticket", g=0, icon="issue", tok="crimson", rarity=1, how="Open your first issue", src="user.issues.totalCount"),
    A(name="Second Opinion", g=0, icon="eye", tok="azure", rarity=2, how="Submit your first review", src="totalPullRequestReviewContributions"),
    A(name="Shipped", g=0, icon="tag", tok="teal", rarity=2, how="Publish your first release", src="repositories.releases.totalCount"),
    A(name="Shipwright", g=0, icon="package", tok="turquoise", rarity=[3, 4, 5], how="Publish 10, 50 and 200 releases", src="repositories.releases.totalCount", goals=[10, 50, 200], word="releases"),
    A(name="Merge Master", g=0, icon="check", tok="plum", rarity=[2, 3, 4], how="Get 25, 100 and 500 pull requests merged", src="search: is:pr is:merged author:you", goals=[25, 100, 500], word="merged"),
    A(name="Polyglot", g=0, icon="code", tok="amethyst", rarity=[2, 2, 3], how="Write code in 5, 10 and 20 languages", src="repositories.languages", goals=[5, 10, 20], word="languages"),
    A(name="Veteran", g=0, icon="clock", tok="brown", rarity=[1, 1, 3], how="Reach 1, 5 and 10 years on GitHub", src="user.createdAt", goals=[1, 5, 10], word="years", passive=True),
    A(name="Century", g=0, icon="chart", tok="forest", rarity=2, how="Make 100 commits in one repository", src="repository.defaultBranchRef.history(author).totalCount", goal=100, word="commits"),
    A(name="Monolith", g=0, icon="database", tok="steel", rarity=3, how="Make 1,000 commits in one repository", src="repository.defaultBranchRef.history(author).totalCount", goal=1000, word="commits"),
    A(name="Long Haul", g=0, icon="infinity", tok="ocean", rarity=3, how="Commit to a repository five years after creating it", src="repository.createdAt vs latest commit", word="repository"),
    A(name="Stargazer", g=0, icon="star", tok="amber", rarity=[2, 3, 4], how="Reach 10, 100 and 1,000 stars on one repository", src="max stargazerCount, self-stars removed", goals=[10, 100, 1000], word="stars"),
    A(name="Forked", g=0, icon="branch", tok="jade", rarity=[2, 3, 4], how="Collect 10, 25 and 100 forks by other people", src="repositories.forkCount, own forks removed", goals=[10, 25, 100], word="forks"),
    A(name="Watched", g=0, icon="bell", tok="sky", rarity=4, how="Reach 50 watchers on one repository", src="repository.watchers.totalCount", goal=50, word="watchers"),
    A(name="Bug Hunter", g=0, icon="bug", tok="cherry", rarity=3, how="Have 25 issues you opened closed as completed", src="issues(states: CLOSED) with stateReason COMPLETED", goal=25, word="issues"),
    A(name="Closer", g=0, icon="cross", tok="moss", rarity=3, how="Close 100 issues in your repositories", src="repositories.issues(states: CLOSED).totalCount", goal=100, word="issues"),
    A(name="By the Book", g=1, icon="book", tok="denim", rarity=[3, 4, 5], how="Write 100, 500 and 2,000 conventional commits (feat:, fix:, docs: …)", src="commit messages", goals=[100, 500, 2000], word="commits", heavy=True),
    A(name="Gitmoji", g=1, icon="sparkle", tok="honey", rarity=[3, 4], how="Start 100 and 500 commit messages with an emoji", src="commit messages", goals=[100, 500], word="commits", heavy=True),
    A(name="Signed", g=1, icon="key", tok="mustard", rarity=[3, 4], how="Sign 100 and 1,000 commits", src="commit.signature.isValid", goals=[100, 1000], word="commits", heavy=True),
    A(name="Duet", g=1, icon="users", tok="rose", rarity=3, how="Author 10 commits with a co-author", src="commit.authors.totalCount > 1", goal=10, word="commits", heavy=True),
    A(name="Undo", g=1, icon="sync", tok="clay", rarity=2, how="Revert a commit", src="commit messages starting with Revert", heavy=True),
    A(name="Surgeon", g=1, icon="target", tok="taupe", rarity=2, how="Make 50 commits that touch exactly one file", src="commit.changedFilesIfAvailable", goal=50, word="commits", heavy=True),
    A(name="Fixer", g=1, icon="wrench", tok="tangerine", rarity=2, how="Write 50 fix: commits", src="commit messages", goal=50, word="commits", heavy=True),
    A(name="Tested", g=1, icon="flask", tok="mint", rarity=3, how="Write 25 test: commits", src="commit messages", goal=25, word="commits", heavy=True),
    A(name="Scribe", g=1, icon="info", tok="lavender", rarity=3, how="Write 25 docs: commits", src="commit messages", goal=25, word="commits", heavy=True),
    A(name="Green Machine", g=1, icon="play", tok="emerald", rarity=[3, 3, 5], how="Finish 100, 1,000 and 10,000 successful workflow runs", src="REST actions/runs?status=success per repository", goals=[100, 1000, 10000], word="runs", heavy=True),
    A(name="Well Maintained", g=1, icon="download", tok="cobalt", rarity=3, how="Merge 25 Dependabot pull requests", src="search: is:pr is:merged author:app/dependabot user:you", goal=25, word="merged"),
    A(name="Toolsmith", g=1, icon="gear", tok="orange", rarity=3, how="Publish a GitHub Action", src="object(expression: \"HEAD:action.yml\")"),
    A(name="Perfect Month", g=2, icon="calendar", tok="emerald", rarity=3, how="Contribute on every day of one calendar month", src="contributionCalendar"),
    A(name="Weekender", g=2, icon="flag", tok="rose", rarity=3, how="Contribute on 26 weekends in one year", src="contributionCalendar", goal=26, word="weekends"),
    A(name="Night Owl", g=2, icon="moon", tok="indigo", rarity=[2, 4], how="Author 50 and 500 commits between midnight and 5 a.m.", src="commit timestamps", goals=[50, 500], word="late commits", heavy=True),
    A(name="Early Bird", g=2, icon="sun", tok="apricot", rarity=[3, 4], how="Author 50 and 500 commits between 5 and 8 a.m.", src="commit timestamps", goals=[50, 500], word="early commits", heavy=True),
    A(name="Marathon Day", g=2, icon="bolt", tok="honey", rarity=[2, 3, 4], how="Make 25, 50 and 100 contributions in a single day", src="contributionCalendar", goals=[25, 50, 100], word="in one day"),
    A(name="Big Week", g=2, icon="pulse", tok="cyan", rarity=2, how="Make 100 contributions in one week", src="contributionCalendar", goal=100, word="in one week"),
    A(name="Sprint", g=2, icon="flame", tok="tangerine", rarity=3, how="Make 500 contributions in one month", src="contributionCalendar", goal=500, word="in one month"),
    A(name="Weekday Warrior", g=2, icon="arrow", tok="lime", rarity=3, how="Contribute on 200 weekdays in one year", src="contributionCalendar", goal=200, word="weekdays"),
    A(name="Year of Code", g=2, icon="chart", tok="forest", rarity=5, how="Contribute on 300 days in one calendar year", src="contributionCalendar", goal=300, word="days"),
    A(name="Four Seasons", g=2, icon="compass", tok="sage", rarity=2, how="Contribute in all twelve months of one year", src="contributionCalendar"),
    A(name="Long Game", g=2, icon="layers", tok="ocean", rarity=[1, 2, 3], how="Contribute in 3, 5 and 10 different years", src="contributionsCollection per year", goals=[3, 5, 10], word="years", passive=True),
    A(name="Comeback", g=2, icon="sync", tok="jade", rarity=1, how="Contribute again after a gap of 90 days", src="contributionCalendar"),
    A(name="Friday Deploy", g=2, icon="rocket", tok="cherry", rarity=3, how="Publish a release on a Friday", src="releases.createdAt"),
    A(name="Upstream", g=3, icon="upload", tok="cobalt", rarity=[2, 3, 4], how="Get 1, 10 and 50 pull requests merged into repositories you don’t own", src="search: is:pr is:merged author:you -user:you", goals=[1, 10, 50], word="merged"),
    A(name="Open Door", g=3, icon="home", tok="jade", rarity=[2, 3, 4], how="Merge 1, 10 and 50 pull requests from other people into your repositories", src="search: is:pr is:merged user:you -author:you", goals=[1, 10, 50], word="merged"),
    A(name="Second Pair of Eyes", g=3, icon="search", tok="teal", rarity=3, how="Review 50 pull requests in repositories you don’t own", src="search: is:pr reviewed-by:you -user:you", goal=50, word="reviews"),
    A(name="Reporter", g=3, icon="alert", tok="crimson", rarity=3, how="Open 25 issues in repositories you don’t own", src="search: is:issue author:you -user:you", goal=25, word="issues"),
    A(name="Voice", g=3, icon="chat", tok="azure", rarity=3, how="Comment on 100 issues in repositories you don’t own", src="user.issueComments, own repositories removed", goal=100, word="comments"),
    A(name="Answer Key", g=3, icon="check", tok="sky", rarity=4, how="Have 10 answers accepted in Discussions", src="repositoryDiscussionComments(onlyAnswers: true)", goal=10, word="answers"),
    A(name="Conversation Starter", g=3, icon="mail", tok="orchid", rarity=4, how="Start 10 discussions", src="user.repositoryDiscussions.totalCount", goal=10, word="discussions"),
    A(name="Team Player", g=3, icon="layers", tok="denim", rarity=3, how="Be a public member of 3 organizations", src="user.organizations.totalCount", goal=3, word="organizations"),
    A(name="Founder", g=3, icon="shield", tok="navy", rarity=3, how="Own an organization", src="organizations where viewerCanAdminister"),
    A(name="Crew", g=3, icon="link", tok="steel", rarity=2, how="Be a collaborator on 5 repositories you don’t own", src="repositories(affiliations: COLLABORATOR)", goal=5, word="repositories"),
    A(name="Generous", g=3, icon="plus", tok="amber", rarity=2, how="Star 100 repositories", src="user.starredRepositories.totalCount", goal=100, word="stars"),
    A(name="Curious", g=3, icon="users", tok="peach", rarity=2, how="Follow 50 people", src="user.following.totalCount", goal=50, word="follows"),
    A(name="Patron", g=3, icon="heart", tok="fuchsia", rarity=4, how="Sponsor someone on GitHub Sponsors", src="user.sponsoring.totalCount", word="sponsorship"),
    A(name="Backed", g=3, icon="medal", tok="honey", rarity=5, how="Receive a sponsorship", src="user.sponsors.totalCount", word="sponsor"),
    A(name="Gist Keeper", g=3, icon="terminal", tok="sage", rarity=3, how="Publish 10 public gists", src="user.gists.totalCount", goal=10, word="gists"),
    A(name="Planner", g=3, icon="grid", tok="lavender", rarity=3, how="Create 5 projects", src="user.projectsV2.totalCount", goal=5, word="projects"),
    A(name="Registry", g=3, icon="package", tok="ocean", rarity=3, how="Publish 5 packages", src="user.packages.totalCount", goal=5, word="packages"),
    A(name="Introduced", g=3, icon="pin", tok="mint", rarity=2, how="Fill in your bio, location, website and profile README", src="user.bio, location, websiteUrl, profile repository"),
    A(name="Licensed", g=4, icon="scale", tok="mustard", rarity=[1, 2, 3], how="Put a license on 1, 5 and 25 repositories", src="repository.licenseInfo", goals=[1, 5, 25], word="repositories"),
    A(name="Documented", g=4, icon="book", tok="cobalt", rarity=[1, 2, 3], how="Give 1, 5 and 25 repositories a description and a README", src="repository.description + object(\"HEAD:README.md\")", goals=[1, 5, 25], word="repositories"),
    A(name="Curator", g=4, icon="tag", tok="amber", rarity=[2, 3, 4], how="Add topics to 5, 15 and 50 repositories", src="repository.repositoryTopics", goals=[5, 15, 50], word="repositories"),
    A(name="Front Door", g=4, icon="globe", tok="sky", rarity=3, how="Add a homepage link to 5 repositories", src="repository.homepageUrl", goal=5, word="repositories"),
    A(name="Welcome Mat", g=4, icon="home", tok="coral", rarity=3, how="Publish a contributing guide", src="CONTRIBUTING.md, or the account .github repository"),
    A(name="House Rules", g=4, icon="tick", tok="sage", rarity=3, how="Publish a code of conduct", src="repository.codeOfConduct"),
    A(name="Locksmith", g=4, icon="lock", tok="cherry", rarity=4, how="Publish a security policy", src="repository.isSecurityPolicyEnabled"),
    A(name="Gatekeeper", g=4, icon="server", tok="steel", rarity=4, how="Add CODEOWNERS to 5 repositories", src="object(\"HEAD:.github/CODEOWNERS\")", goal=5, word="repositories"),
    A(name="Auto-pilot", g=4, icon="gear", tok="cyan", rarity=3, how="Configure Dependabot on a repository", src="object(\"HEAD:.github/dependabot.yml\")"),
    A(name="Blueprint", g=4, icon="folder", tok="lavender", rarity=3, how="Publish a template repository", src="repository.isTemplate"),
    A(name="Open Hand", g=4, icon="heart", tok="rose", rarity=3, how="Add a FUNDING.yml", src="repository.fundingLinks"),
    A(name="Town Hall", g=4, icon="chat", tok="orchid", rarity=3, how="Turn on Discussions for a repository", src="repository.hasDiscussionsEnabled"),
    A(name="Tidy", g=4, icon="trash", tok="ash", rarity=3, how="Archive 5 repositories", src="repository.isArchived", goal=5, word="repositories"),
    A(name="Packager", g=4, icon="download", tok="plum", rarity=3, how="Attach a file to a release", src="release.releaseAssets.totalCount"),
    A(name="Semver", g=4, icon="target", tok="jade", rarity=3, how="Tag 10 releases as vMAJOR.MINOR.PATCH", src="release.tagName", goal=10, word="releases"),
    A(name="New Year", g=5, icon="sparkle", tok="mustard", rarity=2, how="Contribute on 1 January", src="contributionCalendar", secret=True),
    A(name="Leap Day", g=5, icon="calendar", tok="aqua", rarity=3, how="Contribute on 29 February", src="contributionCalendar", secret=True),
    A(name="Green Wall", g=5, icon="grid", tok="lime", rarity=4, how="Contribute in every week of a calendar year", src="contributionCalendar", secret=True),
    A(name="Homecoming", g=5, icon="home", tok="salmon", rarity=3, how="Contribute on the anniversary of the day you joined", src="contributionCalendar + user.createdAt", secret=True),
    A(name="Friday the 13th", g=5, icon="alert", tok="maroon", rarity=3, how="Contribute on a Friday the 13th", src="contributionCalendar", secret=True),
    A(name="Midnight Oil", g=5, icon="clock", tok="indigo", rarity=4, how="Author a commit at exactly midnight", src="commit timestamps", heavy=True, secret=True),
    A(name="The Answer", g=5, icon="q", tok="teal", rarity=3, how="Have a trophy total read exactly 42 on a daily check", src="any core count == 42", secret=True),
    A(name="Full House", g=5, icon="trophy", tok="honey", rarity=5, how="Hold every core trophy at Gold or better", src="core tiers", secret=True),
    A(name="Constellation", g=5, icon="star", tok="iris", rarity=5, how="Earn five stars on one trophy", src="core stars", secret=True),
    A(name="Inbox Zero", g=5, icon="mail", tok="mint", rarity=3, how="Have no open issues across your repositories, with at least 25 closed", src="repositories.issues(states: OPEN)", secret=True),
    A(name="Ghost", g=5, icon="moon", tok="steel", rarity=2, how="Come back after a year away", src="contributionCalendar", secret=True),
    A(name="Fan Club", g=0, icon="heart", tok="peach", rarity=3, how="Reach 100 watchers across your repositories", src="repositories.watchers.totalCount, summed", goal=100, word="watchers"),
    A(name="Branching Out", g=0, icon="branch", tok="moss", rarity=3, how="Keep 10 branches on one repository", src="repository.refs(refPrefix: \"refs/heads/\").totalCount", goal=10, word="branches"),
    A(name="Heavy Lifter", g=1, icon="upload", tok="brick", rarity=1, how="Make a commit that changes 1,000 lines", src="commit.additions + deletions", heavy=True),
    A(name="Sweeping Change", g=1, icon="layers", tok="ruby", rarity=2, how="Make a commit that touches 50 files", src="commit.changedFilesIfAvailable", heavy=True),
    A(name="Lunch Break", g=2, icon="sun", tok="tan", rarity=2, how="Author 50 commits between noon and 1 p.m.", src="commit timestamps", goal=50, word="lunchtime commits", heavy=True),
    A(name="Green Light", g=3, icon="tick", tok="emerald", rarity=3, how="Approve 50 pull requests", src="search: is:pr reviewed-by:you review:approved", goal=50, word="approvals"),
    A(name="Red Pen", g=3, icon="cross", tok="cherry", rarity=3, how="Request changes on 25 pull requests", src="search: is:pr reviewed-by:you review:changes_requested", goal=25, word="reviews"),
    A(name="Roundtable", g=3, icon="chat", tok="mauve", rarity=4, how="Write 50 comments in Discussions", src="user.repositoryDiscussionComments.totalCount", goal=50, word="comments"),
    A(name="Form Filler", g=4, icon="info", tok="denim", rarity=3, how="Add issue templates to a repository", src="object(\"HEAD:.github/ISSUE_TEMPLATE\")"),
    A(name="Roadmap", g=4, icon="compass", tok="olive", rarity=3, how="Use 5 milestones on one repository", src="repository.milestones.totalCount", goal=5, word="milestones"),
    A(name="Label Maker", g=4, icon="tag", tok="magenta", rarity=3, how="Define 25 labels on one repository", src="repository.labels.totalCount", goal=25, word="labels"),
    A(name="Round Number", g=5, icon="target", tok="purple", rarity=4, how="Have a trophy total land exactly on 1,000", src="any core count == 1000", secret=True),
    A(name="Trophy Maker", g=6, icon="trophy", tok="gold", rarity=5, how="Own tannergolden/markdown, the kit that draws these", src="viewer.login == repository(owner: \"tannergolden\", name: \"markdown\").owner.login", only="tannergolden/markdown"),
    A(name="Badge Maker", g=6, icon="tag", tok="gold", rarity=5, how="Own tannergolden/markdown, the kit that draws the badges beside these", src="viewer.login == repository(owner: \"tannergolden\", name: \"markdown\").owner.login", only="tannergolden/markdown"),
    A(name="Standard Bearer", g=6, icon="scale", tok="gold", rarity=5, how="Own tannergolden/standards, the rules every repository on the account follows and the workflows that enforce them", src="viewer.login == repository(owner: \"tannergolden\", name: \"standards\").owner.login", only="tannergolden/standards"),
    A(name="Pathfinder", g=6, icon="compass", tok="gold", rarity=5, how="Own tannergolden/path, the golden path every new repository starts from", src="viewer.login == repository(owner: \"tannergolden\", name: \"path\").owner.login", only="tannergolden/path"),
]

# --- Repository mode: the subject is one repository -------------------------
RCORE = [
    C(key="stars", title="Stars", icon="star", tok="amber", steps=[10, 100, 500, 2000, 10000], counts="Stargazers, owner and members excluded", src="repository.stargazers", word="stars"),
    C(key="forks", title="Forks", icon="branch", tok="jade", steps=[5, 25, 100, 500, 2000], counts="Forks by other accounts", src="repository.forks", word="forks"),
    C(key="contributors", title="Contributors", icon="users", tok="rose", steps=[2, 5, 15, 50, 200], counts="People with a merged commit or pull request", src="history authors + pullRequests(states: MERGED).author", word="contributors"),
    C(key="commits", title="Commits", icon="commit", tok="emerald", steps=[100, 500, 2000, 5000, 20000], counts="Commits on the default branch", src="defaultBranchRef.target.history.totalCount", word="commits"),
    C(key="releases", title="Releases", icon="tag", tok="teal", steps=[1, 5, 20, 50, 200], counts="Published releases", src="repository.releases.totalCount", word="releases"),
    C(key="merged", title="Merged PRs", icon="pull", tok="violet", steps=[10, 50, 250, 1000, 5000], counts="Pull requests merged", src="pullRequests(states: MERGED).totalCount", word="merged"),
    C(key="resolved", title="Issues Resolved", icon="check", tok="crimson", steps=[10, 50, 250, 1000, 5000], counts="Issues closed as completed", src="issues(states: CLOSED), stateReason COMPLETED", word="issues"),
    C(key="active", title="Active Days", icon="calendar", tok="tangerine", steps=[30, 100, 365, 1000, 2500], counts="Days with at least one commit", src="history.committedDate, distinct days", word="days", unit="days"),
]

RGROUPS = ["Launch", "Health", "Craft", "Community", "Reach", "Rhythm", "Secret"]

RACH = [
    A(name="First Star", g=0, icon="star", tok="amber", rarity=1, how="Receive a star from someone else", src="stargazers, owner excluded"),
    A(name="First Fork", g=0, icon="branch", tok="jade", rarity=1, how="Be forked by another account", src="forks"),
    A(name="First Watcher", g=0, icon="eye", tok="sky", rarity=1, how="Gain a watcher who is not the owner", src="watchers"),
    A(name="First Release", g=0, icon="tag", tok="teal", rarity=3, how="Publish a release", src="releases.totalCount"),
    A(name="First Merge", g=0, icon="pull", tok="violet", rarity=2, how="Merge a pull request", src="pullRequests(states: MERGED)"),
    A(name="Outside Help", g=0, icon="upload", tok="cobalt", rarity=3, how="Merge a pull request from someone other than the owner", src="pullRequests(states: MERGED).author != owner"),
    A(name="Stranger Report", g=0, icon="alert", tok="crimson", rarity=2, how="Receive an issue from someone who has never contributed", src="issues.author not in contributors"),
    A(name="First Tag", g=0, icon="pin", tok="mint", rarity=2, how="Push a tag", src="refs(refPrefix: \"refs/tags/\")"),
    A(name="Named", g=0, icon="info", tok="denim", rarity=1, how="Set a description", src="repository.description"),
    A(name="Front Door", g=0, icon="globe", tok="sky", rarity=2, how="Set a homepage link", src="repository.homepageUrl"),
    A(name="Filed", g=0, icon="tag", tok="magenta", rarity=2, how="Add 3 topics", src="repositoryTopics.totalCount", goal=3, word="topics"),
    A(name="Poster", g=0, icon="grid", tok="lavender", rarity=4, how="Upload a social preview image", src="repository.usesCustomOpenGraphImage"),
    A(name="Licensed", g=1, icon="scale", tok="mustard", rarity=1, how="Choose a license", src="repository.licenseInfo"),
    A(name="Documented", g=1, icon="book", tok="cobalt", rarity=1, how="Have a README and a description", src="object(\"HEAD:README.md\") + description"),
    A(name="Welcome Mat", g=1, icon="home", tok="coral", rarity=3, how="Publish a contributing guide", src="CONTRIBUTING.md, or the account .github repository"),
    A(name="House Rules", g=1, icon="tick", tok="sage", rarity=3, how="Publish a code of conduct", src="repository.codeOfConduct"),
    A(name="Locksmith", g=1, icon="lock", tok="cherry", rarity=4, how="Publish a security policy", src="repository.isSecurityPolicyEnabled"),
    A(name="Gatekeeper", g=1, icon="server", tok="steel", rarity=4, how="Add a CODEOWNERS file", src="object(\"HEAD:.github/CODEOWNERS\")"),
    A(name="Form Filler", g=1, icon="info", tok="denim", rarity=3, how="Add issue templates", src="object(\"HEAD:.github/ISSUE_TEMPLATE\")"),
    A(name="Paperwork", g=1, icon="mail", tok="mauve", rarity=4, how="Add a pull request template", src="object(\"HEAD:.github/pull_request_template.md\")"),
    A(name="Auto-pilot", g=1, icon="gear", tok="cyan", rarity=3, how="Configure Dependabot", src="object(\"HEAD:.github/dependabot.yml\")"),
    A(name="Changelog", g=1, icon="terminal", tok="olive", rarity=3, how="Keep a CHANGELOG.md", src="object(\"HEAD:CHANGELOG.md\")"),
    A(name="Well-Formed", g=1, icon="layers", tok="taupe", rarity=2, how="Add an .editorconfig", src="object(\"HEAD:.editorconfig\")"),
    A(name="Town Hall", g=1, icon="chat", tok="orchid", rarity=4, how="Turn on Discussions", src="repository.hasDiscussionsEnabled"),
    A(name="Protected", g=1, icon="shield", tok="navy", rarity=3, how="Protect the default branch with a ruleset", src="repository.rulesets targeting ~DEFAULT_BRANCH"),
    A(name="Clean Bill", g=1, icon="pulse", tok="emerald", rarity=1, how="Have zero open Dependabot alerts", src="vulnerabilityAlerts(states: OPEN), needs security-events: read"),
    A(name="Open Hand", g=1, icon="heart", tok="rose", rarity=4, how="Add a FUNDING.yml", src="repository.fundingLinks"),
    A(name="Support Line", g=1, icon="bell", tok="peach", rarity=4, how="Publish a SUPPORT.md", src="object(\"HEAD:SUPPORT.md\")"),
    A(name="Label Maker", g=1, icon="tag", tok="magenta", rarity=3, how="Define 25 labels", src="repository.labels.totalCount", goal=25, word="labels"),
    A(name="Roadmap", g=1, icon="compass", tok="olive", rarity=4, how="Use 5 milestones", src="repository.milestones.totalCount", goal=5, word="milestones"),
    A(name="By the Book", g=2, icon="book", tok="denim", rarity=[3, 4, 5], how="Land 100, 500 and 2,000 conventional commits", src="commit messages", goals=[100, 500, 2000], word="commits", heavy=True),
    A(name="Signed", g=2, icon="key", tok="mustard", rarity=[3, 4], how="Land 100 and 1,000 signed commits", src="commit.signature.isValid", goals=[100, 1000], word="commits", heavy=True),
    A(name="Gitmoji", g=2, icon="sparkle", tok="honey", rarity=[4, 5], how="Land 100 and 500 commits that start with an emoji", src="commit messages", goals=[100, 500], word="commits", heavy=True),
    A(name="Semver", g=2, icon="target", tok="jade", rarity=3, how="Tag 10 releases as vMAJOR.MINOR.PATCH", src="release.tagName", goal=10, word="releases"),
    A(name="Green Machine", g=2, icon="play", tok="emerald", rarity=[3, 4, 5], how="Finish 100, 1,000 and 10,000 successful workflow runs", src="REST actions/runs?status=success", goals=[100, 1000, 10000], word="runs"),
    A(name="Test Suite", g=2, icon="flask", tok="mint", rarity=2, how="Keep a tests directory with files in it", src="object(\"HEAD:tests\") or test/"),
    A(name="Wired", g=2, icon="bolt", tok="honey", rarity=2, how="Run at least one workflow", src="object(\"HEAD:.github/workflows\")"),
    A(name="Release Notes", g=2, icon="info", tok="lavender", rarity=3, how="Write notes on 10 releases", src="release.description", goal=10, word="releases"),
    A(name="Packager", g=2, icon="download", tok="plum", rarity=3, how="Attach a file to a release", src="release.releaseAssets.totalCount"),
    A(name="Prerelease", g=2, icon="flag", tok="apricot", rarity=3, how="Publish a pre-release", src="release.isPrerelease"),
    A(name="Squeaky", g=2, icon="tick", tok="sage", rarity=1, how="Have no open pull request older than 90 days", src="pullRequests(states: OPEN).createdAt"),
    A(name="Small Steps", g=2, icon="commit", tok="moss", rarity=2, how="Keep the median commit under 50 changed lines", src="commit.additions + deletions, last 500 commits", heavy=True),
    A(name="Follows the Standards", g=2, icon="scale", tok="gold", rarity=5, how="Call tannergolden/standards from a workflow", src="workflow files containing uses: tannergolden/standards"),
    A(name="Golden Path", g=2, icon="compass", tok="gold", rarity=5, how="Be generated from tannergolden/path", src="repository.templateRepository, or the template fingerprint"),
    A(name="Containerized", g=2, icon="package", tok="ocean", rarity=2, how="Ship a Dockerfile", src="object(\"HEAD:Dockerfile\")"),
    A(name="Ready Room", g=2, icon="terminal", tok="cyan", rarity=4, how="Ship a dev container", src="object(\"HEAD:.devcontainer\")"),
    A(name="Ten Strong", g=3, icon="users", tok="rose", rarity=[3, 5, 5], how="Reach 10, 50 and 100 contributors", src="distinct contributors", goals=[10, 50, 100], word="contributors"),
    A(name="Reviewed", g=3, icon="eye", tok="azure", rarity=4, how="Have each of the last 100 merged pull requests reviewed", src="pullRequests.reviews.totalCount"),
    A(name="Fast Reply", g=3, icon="bolt", tok="tangerine", rarity=3, how="Answer new issues within a day, at the median of the last 50", src="issues.comments[0].createdAt - createdAt"),
    A(name="Good First Issues", g=3, icon="sparkle", tok="mint", rarity=4, how="Label 5 issues good first issue", src="issues(labels: [\"good first issue\"])", goal=5, word="issues"),
    A(name="Help Wanted", g=3, icon="flag", tok="coral", rarity=4, how="Label 5 issues help wanted", src="issues(labels: [\"help wanted\"])", goal=5, word="issues"),
    A(name="Outside Merges", g=3, icon="upload", tok="cobalt", rarity=[3, 4, 5], how="Merge 10, 50 and 200 pull requests from people other than the owner", src="pullRequests(states: MERGED).author != owner", goals=[10, 50, 200], word="merged"),
    A(name="Answered", g=3, icon="check", tok="sky", rarity=4, how="Mark 10 discussions as answered", src="discussions(answered: true)", goal=10, word="discussions"),
    A(name="Triage", g=3, icon="tag", tok="amber", rarity=3, how="Keep every open issue labeled", src="issues(states: OPEN) without labels == 0"),
    A(name="Well Maintained", g=3, icon="sync", tok="cobalt", rarity=3, how="Merge 25 Dependabot pull requests", src="pullRequests by app/dependabot, merged", goal=25, word="merged"),
    A(name="Talkative", g=3, icon="chat", tok="orchid", rarity=4, how="Collect 1,000 issue comments", src="issues.comments.totalCount, summed", goal=1000, word="comments"),
    A(name="Popular Opinion", g=3, icon="heart", tok="fuchsia", rarity=4, how="Have an issue with 50 thumbs up", src="issue.reactions(content: THUMBS_UP).totalCount", goal=50, word="reactions"),
    A(name="Long Thread", g=3, icon="mail", tok="mauve", rarity=4, how="Have an issue with 100 comments", src="issue.comments.totalCount", goal=100, word="comments"),
    A(name="Mentor", g=3, icon="search", tok="teal", rarity=3, how="Merge a pull request after requesting changes on it", src="reviews(states: CHANGES_REQUESTED) then merged", heavy=True),
    A(name="Regulars", g=3, icon="medal", tok="honey", rarity=4, how="Have 5 contributors with 10 or more commits each", src="history authors, counted", goal=5, word="regulars"),
    A(name="Org Backed", g=3, icon="shield", tok="navy", rarity=2, how="Be owned by an organization", src="repository.owner.__typename == Organization"),
    A(name="Crew", g=3, icon="link", tok="steel", rarity=3, how="Have 5 collaborators", src="repository.collaborators.totalCount", goal=5, word="collaborators"),
    A(name="Watched", g=4, icon="bell", tok="sky", rarity=[4, 5, 5], how="Reach 25, 100 and 1,000 watchers", src="repository.watchers.totalCount", goals=[25, 100, 1000], word="watchers"),
    A(name="Used By", g=4, icon="layers", tok="iris", rarity=[3, 5, 5], how="Be a dependency of 10, 100 and 1,000 repositories", src="dependents, from the dependency graph", goals=[10, 100, 1000], word="dependents", heavy=True),
    A(name="Star of the Week", g=4, icon="star", tok="amber", rarity=4, how="Gain 50 stars in one week", src="ledger snapshots", goal=50, word="stars this week"),
    A(name="Trending", g=4, icon="chart", tok="tangerine", rarity=5, how="Gain 100 stars in one week", src="ledger snapshots", goal=100, word="stars this week"),
    A(name="Forked Far", g=4, icon="branch", tok="jade", rarity=5, how="Have a fork that earns 100 stars of its own", src="forks.stargazerCount", goal=100, word="stars on a fork"),
    A(name="Living Forks", g=4, icon="sync", tok="moss", rarity=4, how="Have 10 forks with commits of their own", src="forks where pushedAt > createdAt", goal=10, word="living forks"),
    A(name="Registry", g=4, icon="package", tok="ocean", rarity=3, how="Publish a package from this repository", src="repository.packages.totalCount"),
    A(name="Downloaded", g=4, icon="download", tok="plum", rarity=[3, 4, 5], how="Reach 1,000, 10,000 and 100,000 release downloads", src="releaseAssets.downloadCount, summed", goals=[1000, 10000, 100000], word="downloads"),
    A(name="Visited", g=4, icon="eye", tok="azure", rarity=4, how="Reach 1,000 unique visitors in two weeks", src="REST traffic/views, needs push access", goal=1000, word="visitors"),
    A(name="Cloned", g=4, icon="terminal", tok="cyan", rarity=3, how="Reach 100 unique cloners in two weeks", src="REST traffic/clones", goal=100, word="cloners"),
    A(name="Referred", g=4, icon="link", tok="denim", rarity=3, how="Be linked from 5 referring sites", src="REST traffic/popular/referrers", goal=5, word="referrers"),
    A(name="Big Name", g=4, icon="medal", tok="gold", rarity=4, how="Be starred by someone with 10,000 followers", src="stargazers.followers.totalCount", heavy=True),
    A(name="Stargazer Streak", g=4, icon="sparkle", tok="honey", rarity=4, how="Gain a star in each of 12 consecutive weeks", src="ledger snapshots", goal=12, word="weeks"),
    A(name="Fork Magnet", g=4, icon="bolt", tok="lime", rarity=4, how="Gain 10 forks in one week", src="ledger snapshots", goal=10, word="forks this week"),
    A(name="Weekly Beat", g=5, icon="pulse", tok="emerald", rarity=4, how="Land a commit in 52 consecutive weeks", src="history.committedDate", goal=52, word="weeks"),
    A(name="Monthly Release", g=5, icon="tag", tok="teal", rarity=5, how="Publish a release in each of 12 consecutive months", src="releases.createdAt", goal=12, word="months"),
    A(name="Streak", g=5, icon="flame", tok="tangerine", rarity=[4, 5, 5], how="Commit on 30, 100 and 365 consecutive days", src="history.committedDate", goals=[30, 100, 365], word="days"),
    A(name="Comeback", g=5, icon="sync", tok="jade", rarity=1, how="Land a commit after a gap of 90 days", src="history.committedDate"),
    A(name="Night Shift", g=5, icon="moon", tok="indigo", rarity=3, how="Land 50 commits between midnight and 5 a.m.", src="commit timestamps", goal=50, word="late commits", heavy=True),
    A(name="Weekend Project", g=5, icon="flag", tok="rose", rarity=3, how="Land commits on 26 weekends in one year", src="history.committedDate", goal=26, word="weekends"),
    A(name="Marathon Day", g=5, icon="bolt", tok="honey", rarity=3, how="Land 50 commits in a single day", src="history.committedDate", goal=50, word="in one day"),
    A(name="Big Week", g=5, icon="chart", tok="cyan", rarity=3, how="Land 100 commits in one week", src="history.committedDate", goal=100, word="in one week"),
    A(name="Long Game", g=5, icon="layers", tok="ocean", rarity=[2, 3, 4], how="Land commits in 3, 5 and 10 different years", src="history.committedDate", goals=[3, 5, 10], word="years", passive=True),
    A(name="Alive", g=5, icon="sun", tok="lime", rarity=2, how="Land a commit in the last 30 days", src="history.committedDate"),
    A(name="Friday Deploy", g=5, icon="rocket", tok="cherry", rarity=3, how="Publish a release on a Friday", src="releases.createdAt"),
    A(name="Same-Day Fix", g=5, icon="wrench", tok="apricot", rarity=3, how="Close 10 issues within a day of them being opened", src="issues.closedAt - createdAt", goal=10, word="fixes"),
    A(name="Round Number", g=6, icon="target", tok="purple", rarity=4, how="Have a trophy total land exactly on 1,000", src="any core count == 1000", secret=True),
    A(name="The Answer", g=6, icon="q", tok="teal", rarity=4, how="Have a trophy total read exactly 42 on a daily check", src="any core count == 42", secret=True),
    A(name="Palindrome", g=6, icon="infinity", tok="iris", rarity=3, how="Have a commit count that reads the same backwards", src="history.totalCount", secret=True),
    A(name="Leap Day", g=6, icon="calendar", tok="aqua", rarity=5, how="Publish a release on 29 February", src="releases.createdAt", secret=True),
    A(name="Friday the 13th", g=6, icon="alert", tok="maroon", rarity=4, how="Publish a release on a Friday the 13th", src="releases.createdAt", secret=True),
    A(name="New Year", g=6, icon="sparkle", tok="mustard", rarity=3, how="Land a commit on 1 January", src="history.committedDate", secret=True),
    A(name="Birthday", g=6, icon="home", tok="salmon", rarity=3, how="Land a commit on the anniversary of the first commit", src="history.committedDate", secret=True),
    A(name="Midnight Oil", g=6, icon="clock", tok="indigo", rarity=4, how="Land a commit at exactly midnight", src="commit timestamps", heavy=True, secret=True),
    A(name="Green Wall", g=6, icon="grid", tok="lime", rarity=4, how="Land a commit in every week of a calendar year", src="history.committedDate", secret=True),
    A(name="Ghost", g=6, icon="moon", tok="steel", rarity=2, how="Land a commit after a year of silence", src="history.committedDate", secret=True),
    A(name="Full House", g=6, icon="trophy", tok="honey", rarity=5, how="Hold every core trophy at Gold or better", src="core tiers", secret=True),
    A(name="Constellation", g=6, icon="star", tok="iris", rarity=5, how="Earn five stars on one trophy", src="core stars", secret=True),
]

MODES = {
    "profile": {"core": CORE, "ach": ACH, "groups": GROUPS},
    "repository": {"core": RCORE, "ach": RACH, "groups": RGROUPS},
}


def visible(ach, subject_login: str, owner_of) -> list:
    """The achievements a subject can hold.

    `owner_of("owner/name")` answers who owns that repository, or None. An
    owner-only achievement is dropped entirely, not shown as a secret, unless
    the subject is that owner, so everyone else's total is exactly one hundred.
    """
    out = []
    for a in ach:
        if a.only:
            login = owner_of(a.only)
            if not login or login.lower() != subject_login.lower():
                continue
        out.append(a)
    return out


def measure(core: Core, value: int) -> dict:
    """Tier, stars and progress toward the next step for a core value."""
    t = 0
    while t < 5 and value >= core.steps[t]:
        t += 1
    if t == 5:
        d = core.steps[4]
        k = 0
        while k < MAX_STARS and value >= d * 2 ** (k + 1):
            k += 1
        if k >= MAX_STARS:
            return {"t": 5, "v": value, "stars": MAX_STARS, "pct": 1.0, "next": None, "to_go": 0}
        lo, hi = d * 2**k, d * 2 ** (k + 1)
        return {"t": 5, "v": value, "stars": k, "pct": (value - lo) / (hi - lo), "next": f"star {k + 1}", "to_go": hi - value}
    lo = 0 if t == 0 else core.steps[t - 1]
    hi = core.steps[t]
    return {"t": t, "v": value, "stars": 0, "pct": (value - lo) / (hi - lo), "next": TIER_NAMES[t + 1], "to_go": hi - value}


def ach_state(a: Achievement, cur) -> dict:
    """Earned tier, rarity and progress for an achievement at value `cur`.

    `cur is None` means the run could not measure it; it renders as unearned
    with no progress and is listed in the run summary.
    """
    goals, rar = a.tiers, a.rarities
    tiered = len(goals) > 1
    if cur is None:
        return {"measured": False, "earned": False, "done": False, "k": 0, "next": goals[0], "tiered": tiered,
                "tier": "", "next_tier": ROMAN[1] if tiered else "", "rarity": rar[0], "next_rarity": rar[0],
                "pct": 0.0, "secret": bool(a.secret), "cur": 0}
    k = 0
    while k < len(goals) and cur >= goals[k]:
        k += 1
    earned, done = k > 0, k >= len(goals)
    nxt = None if done else goals[k]
    return {"measured": True, "earned": earned, "done": done, "k": k, "next": nxt, "tiered": tiered,
            "tier": ROMAN[k] if tiered else "", "next_tier": ROMAN[k + 1] if tiered and not done else "",
            "rarity": rar[k - 1] if earned else rar[0], "next_rarity": rar[k - 1] if done else rar[k],
            "pct": 1.0 if done else min(1.0, cur / nxt), "secret": bool(a.secret) and not earned, "cur": cur}
