<!--
title: '🏆 CATALOGUE'
description: 'Every trophy and achievement the kit can award, in both modes, with the threshold and the GitHub data behind each one.'
tags: [trophies, achievements, catalogue, reference]
category: docs
-->

<!-- markdownlint-disable MD041 -->

<div align="center">

# 🏆 CATALOGUE

<a name="top"></a>

**Every trophy and achievement, and what earns it.**

_Written from the data by `make catalogue`. Do not edit by hand._

</div>

---

## 🎯 How Tiers Work

A **core trophy** counts something that only grows. It is cut into five tiers,
Bronze to Diamond, and the card shows progress from the tier you hold to the
next one. Past Diamond it earns a **star** each time the Diamond number
doubles, up to five.

An **achievement** is earned or not. A **tiered** one is earned several times,
at each threshold listed, and the pin shows the numeral you hold. Its
**rarity** decides the metal it is drawn in. **Secret** ones show a question
mark until earned. Anything marked **heavy** reads individual commits rather
than a single count, so it runs under a budget and catches up over a week.


<a name="profile"></a>

## 👤 Profile Mode

The subject is a person. Counts run across every repository the account owns, with the profile repository, bot commits, the kit's own refresh commits, forks and self-stars left out.

### The 8 core trophies

| Trophy | Counts | Enamel | Bronze | Silver | Gold | Platinum | Diamond | Source |
| :-- | :-- | :-- | --: | --: | --: | --: | --: | :-- |
| <a name="profile-commits"></a>**Commits** | Commit contributions, all years | `emerald` | 100 | 500 | 2,000 | 5,000 | 10,000 | `contributionsCollection.totalCommitContributions, summed per year` |
| <a name="profile-pulls"></a>**Pull Requests** | Pull requests opened | `violet` | 5 | 25 | 100 | 250 | 1,000 | `user.pullRequests.totalCount` |
| <a name="profile-reviews"></a>**Reviews** | Pull request reviews submitted | `azure` | 5 | 25 | 100 | 250 | 1,000 | `totalPullRequestReviewContributions, summed per year` |
| <a name="profile-issues"></a>**Issues** | Issues opened | `crimson` | 5 | 25 | 100 | 250 | 1,000 | `user.issues.totalCount` |
| <a name="profile-stars"></a>**Stars Earned** | Stars from others on repositories you created | `amber` | 10 | 50 | 250 | 1,000 | 5,000 | `repositories(ownerAffiliations: OWNER, isFork: false).stargazerCount` |
| <a name="profile-followers"></a>**Followers** | Followers | `rose` | 25 | 100 | 350 | 1,000 | 2,500 | `user.followers.totalCount` |
| <a name="profile-streak"></a>**Longest Streak** | Longest run of days with a contribution | `tangerine` | 7 days | 30 days | 100 days | 200 days | 365 days | `contributionCalendar days, all years` |
| <a name="profile-repos"></a>**Repositories** | Public repositories you created, not forks | `turquoise` | 5 | 15 | 30 | 60 | 100 | `repositories(isFork: false, privacy: PUBLIC).totalCount` |

Where each tier sits, as the share of located accounts at or above it:

| Trophy | Bronze | Silver | Gold | Platinum | Diamond | Basis |
| :-- | --: | --: | --: | --: | --: | :-- |
| **Commits** | top 43% | top 22% | top 7.8% | top 2.8% | top 1.1% | derived: all-time commits taken as three times one year's public contributions; yearly shares measured |
| **Pull Requests** | top 45% | top 25% | top 9% | top 4% | top 1% | estimated: readme-stats median 50, Zipf tail |
| **Reviews** | top 30% | top 14% | top 5% | top 2.2% | top 0.6% | estimated: readme-stats median 2, Zipf tail |
| **Issues** | top 45% | top 22% | top 8% | top 3.5% | top 1% | estimated: readme-stats median 25, Zipf tail |
| **Stars Earned** | top 30% | top 15% | top 5% | top 1.6% | top 0.4% | estimated: readme-stats median 50 for card users, discounted for located accounts |
| **Followers** | top 58% | top 29% | top 10% | top 3.4% | top 1% | measured: located accounts |
| **Longest Streak** | top 50% | top 18% | top 5% | top 1.8% | top 0.5% | estimated: yearly activity shares; a 365-day streak needs 365 active days |
| **Repositories** | top 50% | top 22% | top 9% | top 3% | top 1.2% | derived: 2.22 repositories per developer on average, Zipf tail |

### The 100 achievements

### Milestones

| Achievement | Earned by | Rarity | Who earns it | Source |
| :-- | :-- | :-- | :-- | :-- |
| <a name="profile-hello-world"></a>**Hello World** | Make your first commit | Common | 74% <sub>measured</sub> | `contributionsCollection.totalCommitContributions` |
| <a name="profile-first-light"></a>**First Light** | Publish your first public repository | Common | 60% <sub>estimated</sub> | `repositories(privacy: PUBLIC).totalCount` |
| <a name="profile-opening-move"></a>**Opening Move** | Open your first pull request | Common | 45% <sub>estimated</sub> | `user.pullRequests.totalCount` |
| <a name="profile-landed"></a>**Landed** | Get your first pull request merged | Uncommon | 38% <sub>estimated</sub> | `search: is:pr is:merged author:you` |
| <a name="profile-ticket"></a>**Ticket** | Open your first issue | Common | 45% <sub>estimated</sub> | `user.issues.totalCount` |
| <a name="profile-second-opinion"></a>**Second Opinion** | Submit your first review | Uncommon | 25% <sub>estimated</sub> | `totalPullRequestReviewContributions` |
| <a name="profile-shipped"></a>**Shipped** | Publish your first release | Uncommon | 20% <sub>estimated</sub> | `repositories.releases.totalCount` |
| <a name="profile-shipwright"></a>**Shipwright** <sub>tiers 10 / 50 / 200</sub> | Publish 10, 50 and 200 releases | Rare → Epic → Legendary | 8% → 2% → 0.5% <sub>estimated</sub> | `repositories.releases.totalCount` |
| <a name="profile-merge-master"></a>**Merge Master** <sub>tiers 25 / 100 / 500</sub> | Get 25, 100 and 500 pull requests merged | Uncommon → Rare → Epic | 20% → 8% → 1.5% <sub>estimated</sub> | `search: is:pr is:merged author:you` |
| <a name="profile-polyglot"></a>**Polyglot** <sub>tiers 5 / 10 / 20</sub> | Write code in 5, 10 and 20 languages | Uncommon → Uncommon → Rare | 35% → 15% → 4% <sub>estimated</sub> | `repositories.languages` |
| <a name="profile-veteran"></a>**Veteran** <sub>tiers 1 / 5 / 10</sub> | Reach 1, 5 and 10 years on GitHub | Common → Common → Rare | 80% → 45% → 8% <sub>derived</sub> | `user.createdAt` |
| <a name="profile-century"></a>**Century** | Make 100 commits in one repository | Uncommon | 35% <sub>derived</sub> | `repository.defaultBranchRef.history(author).totalCount` |
| <a name="profile-monolith"></a>**Monolith** | Make 1,000 commits in one repository | Rare | 7% <sub>derived</sub> | `repository.defaultBranchRef.history(author).totalCount` |
| <a name="profile-long-haul"></a>**Long Haul** | Commit to a repository five years after creating it | Rare | 10% <sub>estimated</sub> | `repository.createdAt vs latest commit` |
| <a name="profile-stargazer"></a>**Stargazer** <sub>tiers 10 / 100 / 1,000</sub> | Reach 10, 100 and 1,000 stars on one repository | Uncommon → Rare → Epic | 30% → 8% → 1.2% <sub>estimated</sub> | `max stargazerCount, self-stars removed` |
| <a name="profile-forked"></a>**Forked** <sub>tiers 10 / 25 / 100</sub> | Collect 10, 25 and 100 forks by other people | Uncommon → Rare → Epic | 15% → 7% → 1.5% <sub>estimated</sub> | `repositories.forkCount, own forks removed` |
| <a name="profile-watched"></a>**Watched** | Reach 50 watchers on one repository | Epic | 3% <sub>estimated</sub> | `repository.watchers.totalCount` |
| <a name="profile-bug-hunter"></a>**Bug Hunter** | Have 25 issues you opened closed as completed | Rare | 8% <sub>estimated</sub> | `issues(states: CLOSED) with stateReason COMPLETED` |
| <a name="profile-closer"></a>**Closer** | Close 100 issues in your repositories | Rare | 6% <sub>estimated</sub> | `repositories.issues(states: CLOSED).totalCount` |
| <a name="profile-fan-club"></a>**Fan Club** | Reach 100 watchers across your repositories | Rare | 5% <sub>estimated</sub> | `repositories.watchers.totalCount, summed` |
| <a name="profile-branching-out"></a>**Branching Out** | Keep 10 branches on one repository | Rare | 12% <sub>estimated</sub> | `repository.refs(refPrefix: "refs/heads/").totalCount` |

### Craft

| Achievement | Earned by | Rarity | Who earns it | Source |
| :-- | :-- | :-- | :-- | :-- |
| <a name="profile-by-the-book"></a>**By the Book** <sub>tiers 100 / 500 / 2,000, heavy</sub> | Write 100, 500 and 2,000 conventional commits (feat:, fix:, docs: …) | Rare → Epic → Legendary | 8% → 3% → 0.8% <sub>estimated</sub> | `commit messages` |
| <a name="profile-gitmoji"></a>**Gitmoji** <sub>tiers 100 / 500, heavy</sub> | Start 100 and 500 commit messages with an emoji | Rare → Epic | 4% → 1% <sub>estimated</sub> | `commit messages` |
| <a name="profile-signed"></a>**Signed** <sub>tiers 100 / 1,000, heavy</sub> | Sign 100 and 1,000 commits | Rare → Epic | 10% → 2% <sub>estimated</sub> | `commit.signature.isValid` |
| <a name="profile-duet"></a>**Duet** <sub>heavy</sub> | Author 10 commits with a co-author | Rare | 12% <sub>estimated</sub> | `commit.authors.totalCount > 1` |
| <a name="profile-undo"></a>**Undo** <sub>heavy</sub> | Revert a commit | Uncommon | 25% <sub>estimated</sub> | `commit messages starting with Revert` |
| <a name="profile-surgeon"></a>**Surgeon** <sub>heavy</sub> | Make 50 commits that touch exactly one file | Uncommon | 20% <sub>estimated</sub> | `commit.changedFilesIfAvailable` |
| <a name="profile-fixer"></a>**Fixer** <sub>heavy</sub> | Write 50 fix: commits | Uncommon | 15% <sub>estimated</sub> | `commit messages` |
| <a name="profile-tested"></a>**Tested** <sub>heavy</sub> | Write 25 test: commits | Rare | 6% <sub>estimated</sub> | `commit messages` |
| <a name="profile-scribe"></a>**Scribe** <sub>heavy</sub> | Write 25 docs: commits | Rare | 8% <sub>estimated</sub> | `commit messages` |
| <a name="profile-green-machine"></a>**Green Machine** <sub>tiers 100 / 1,000 / 10,000, heavy</sub> | Finish 100, 1,000 and 10,000 successful workflow runs | Rare → Rare → Legendary | 12% → 4% → 0.7% <sub>estimated</sub> | `REST actions/runs?status=success per repository` |
| <a name="profile-well-maintained"></a>**Well Maintained** | Merge 25 Dependabot pull requests | Rare | 6% <sub>estimated</sub> | `search: is:pr is:merged author:app/dependabot user:you` |
| <a name="profile-toolsmith"></a>**Toolsmith** | Publish a GitHub Action | Rare | 4% <sub>estimated</sub> | `object(expression: "HEAD:action.yml")` |
| <a name="profile-heavy-lifter"></a>**Heavy Lifter** <sub>heavy</sub> | Make a commit that changes 1,000 lines | Common | 40% <sub>estimated</sub> | `commit.additions + deletions` |
| <a name="profile-sweeping-change"></a>**Sweeping Change** <sub>heavy</sub> | Make a commit that touches 50 files | Uncommon | 30% <sub>estimated</sub> | `commit.changedFilesIfAvailable` |

### Rhythm

| Achievement | Earned by | Rarity | Who earns it | Source |
| :-- | :-- | :-- | :-- | :-- |
| <a name="profile-perfect-month"></a>**Perfect Month** | Contribute on every day of one calendar month | Rare | 6% <sub>derived</sub> | `contributionCalendar` |
| <a name="profile-weekender"></a>**Weekender** | Contribute on 26 weekends in one year | Rare | 12% <sub>derived</sub> | `contributionCalendar` |
| <a name="profile-night-owl"></a>**Night Owl** <sub>tiers 50 / 500, heavy</sub> | Author 50 and 500 commits between midnight and 5 a.m. | Uncommon → Epic | 15% → 2% <sub>estimated</sub> | `commit timestamps` |
| <a name="profile-early-bird"></a>**Early Bird** <sub>tiers 50 / 500, heavy</sub> | Author 50 and 500 commits between 5 and 8 a.m. | Rare → Epic | 10% → 1.5% <sub>estimated</sub> | `commit timestamps` |
| <a name="profile-marathon-day"></a>**Marathon Day** <sub>tiers 25 / 50 / 100</sub> | Make 25, 50 and 100 contributions in a single day | Uncommon → Rare → Epic | 20% → 7% → 2% <sub>derived</sub> | `contributionCalendar` |
| <a name="profile-big-week"></a>**Big Week** | Make 100 contributions in one week | Uncommon | 20% <sub>derived</sub> | `contributionCalendar` |
| <a name="profile-sprint"></a>**Sprint** | Make 500 contributions in one month | Rare | 6% <sub>derived</sub> | `contributionCalendar` |
| <a name="profile-weekday-warrior"></a>**Weekday Warrior** | Contribute on 200 weekdays in one year | Rare | 4% <sub>derived</sub> | `contributionCalendar` |
| <a name="profile-year-of-code"></a>**Year of Code** | Contribute on 300 days in one calendar year | Legendary | 0.6% <sub>derived</sub> | `contributionCalendar` |
| <a name="profile-four-seasons"></a>**Four Seasons** | Contribute in all twelve months of one year | Uncommon | 15% <sub>derived</sub> | `contributionCalendar` |
| <a name="profile-long-game"></a>**Long Game** <sub>tiers 3 / 5 / 10</sub> | Contribute in 3, 5 and 10 different years | Common → Uncommon → Rare | 40% → 20% → 5% <sub>derived</sub> | `contributionsCollection per year` |
| <a name="profile-comeback"></a>**Comeback** | Contribute again after a gap of 90 days | Common | 45% <sub>estimated</sub> | `contributionCalendar` |
| <a name="profile-friday-deploy"></a>**Friday Deploy** | Publish a release on a Friday | Rare | 12% <sub>estimated</sub> | `releases.createdAt` |
| <a name="profile-lunch-break"></a>**Lunch Break** <sub>heavy</sub> | Author 50 commits between noon and 1 p.m. | Uncommon | 20% <sub>estimated</sub> | `commit timestamps` |

### Community

| Achievement | Earned by | Rarity | Who earns it | Source |
| :-- | :-- | :-- | :-- | :-- |
| <a name="profile-upstream"></a>**Upstream** <sub>tiers 1 / 10 / 50</sub> | Get 1, 10 and 50 pull requests merged into repositories you don’t own | Uncommon → Rare → Epic | 35% → 10% → 2.5% <sub>estimated</sub> | `search: is:pr is:merged author:you -user:you` |
| <a name="profile-open-door"></a>**Open Door** <sub>tiers 1 / 10 / 50</sub> | Merge 1, 10 and 50 pull requests from other people into your repositories | Uncommon → Rare → Epic | 25% → 8% → 2% <sub>estimated</sub> | `search: is:pr is:merged user:you -author:you` |
| <a name="profile-second-pair-of-eyes"></a>**Second Pair of Eyes** | Review 50 pull requests in repositories you don’t own | Rare | 6% <sub>estimated</sub> | `search: is:pr reviewed-by:you -user:you` |
| <a name="profile-reporter"></a>**Reporter** | Open 25 issues in repositories you don’t own | Rare | 12% <sub>estimated</sub> | `search: is:issue author:you -user:you` |
| <a name="profile-voice"></a>**Voice** | Comment on 100 issues in repositories you don’t own | Rare | 8% <sub>estimated</sub> | `user.issueComments, own repositories removed` |
| <a name="profile-answer-key"></a>**Answer Key** | Have 10 answers accepted in Discussions | Epic | 1.5% <sub>estimated</sub> | `repositoryDiscussionComments(onlyAnswers: true)` |
| <a name="profile-conversation-starter"></a>**Conversation Starter** | Start 10 discussions | Epic | 3% <sub>estimated</sub> | `user.repositoryDiscussions.totalCount` |
| <a name="profile-team-player"></a>**Team Player** | Be a public member of 3 organizations | Rare | 10% <sub>estimated</sub> | `user.organizations.totalCount` |
| <a name="profile-founder"></a>**Founder** | Own an organization | Rare | 12% <sub>estimated</sub> | `organizations where viewerCanAdminister` |
| <a name="profile-crew"></a>**Crew** | Be a collaborator on 5 repositories you don’t own | Uncommon | 15% <sub>estimated</sub> | `repositories(affiliations: COLLABORATOR)` |
| <a name="profile-generous"></a>**Generous** | Star 100 repositories | Uncommon | 25% <sub>estimated</sub> | `user.starredRepositories.totalCount` |
| <a name="profile-curious"></a>**Curious** | Follow 50 people | Uncommon | 20% <sub>estimated</sub> | `user.following.totalCount` |
| <a name="profile-patron"></a>**Patron** | Sponsor someone on GitHub Sponsors | Epic | 1.5% <sub>estimated</sub> | `user.sponsoring.totalCount` |
| <a name="profile-backed"></a>**Backed** | Receive a sponsorship | Legendary | 0.6% <sub>estimated</sub> | `user.sponsors.totalCount` |
| <a name="profile-gist-keeper"></a>**Gist Keeper** | Publish 10 public gists | Rare | 8% <sub>estimated</sub> | `user.gists.totalCount` |
| <a name="profile-planner"></a>**Planner** | Create 5 projects | Rare | 6% <sub>estimated</sub> | `user.projectsV2.totalCount` |
| <a name="profile-registry"></a>**Registry** | Publish 5 packages | Rare | 4% <sub>estimated</sub> | `user.packages.totalCount` |
| <a name="profile-introduced"></a>**Introduced** | Fill in your bio, location, website and profile README | Uncommon | 30% <sub>estimated</sub> | `user.bio, location, websiteUrl, profile repository` |
| <a name="profile-green-light"></a>**Green Light** | Approve 50 pull requests | Rare | 8% <sub>estimated</sub> | `search: is:pr reviewed-by:you review:approved` |
| <a name="profile-red-pen"></a>**Red Pen** | Request changes on 25 pull requests | Rare | 4% <sub>estimated</sub> | `search: is:pr reviewed-by:you review:changes_requested` |
| <a name="profile-roundtable"></a>**Roundtable** | Write 50 comments in Discussions | Epic | 2% <sub>estimated</sub> | `user.repositoryDiscussionComments.totalCount` |

### Housekeeping

| Achievement | Earned by | Rarity | Who earns it | Source |
| :-- | :-- | :-- | :-- | :-- |
| <a name="profile-licensed"></a>**Licensed** <sub>tiers 1 / 5 / 25</sub> | Put a license on 1, 5 and 25 repositories | Common → Uncommon → Rare | 45% → 20% → 4% <sub>estimated</sub> | `repository.licenseInfo` |
| <a name="profile-documented"></a>**Documented** <sub>tiers 1 / 5 / 25</sub> | Give 1, 5 and 25 repositories a description and a README | Common → Uncommon → Rare | 55% → 25% → 5% <sub>estimated</sub> | `repository.description + object("HEAD:README.md")` |
| <a name="profile-curator"></a>**Curator** <sub>tiers 5 / 15 / 50</sub> | Add topics to 5, 15 and 50 repositories | Uncommon → Rare → Epic | 20% → 8% → 1.5% <sub>estimated</sub> | `repository.repositoryTopics` |
| <a name="profile-front-door"></a>**Front Door** | Add a homepage link to 5 repositories | Rare | 12% <sub>estimated</sub> | `repository.homepageUrl` |
| <a name="profile-welcome-mat"></a>**Welcome Mat** | Publish a contributing guide | Rare | 8% <sub>estimated</sub> | `CONTRIBUTING.md, or the account .github repository` |
| <a name="profile-house-rules"></a>**House Rules** | Publish a code of conduct | Rare | 5% <sub>estimated</sub> | `repository.codeOfConduct` |
| <a name="profile-locksmith"></a>**Locksmith** | Publish a security policy | Epic | 3% <sub>estimated</sub> | `repository.isSecurityPolicyEnabled` |
| <a name="profile-gatekeeper"></a>**Gatekeeper** | Add CODEOWNERS to 5 repositories | Epic | 2% <sub>estimated</sub> | `object("HEAD:.github/CODEOWNERS")` |
| <a name="profile-auto-pilot"></a>**Auto-pilot** | Configure Dependabot on a repository | Rare | 10% <sub>estimated</sub> | `object("HEAD:.github/dependabot.yml")` |
| <a name="profile-blueprint"></a>**Blueprint** | Publish a template repository | Rare | 8% <sub>estimated</sub> | `repository.isTemplate` |
| <a name="profile-open-hand"></a>**Open Hand** | Add a FUNDING.yml | Rare | 4% <sub>estimated</sub> | `repository.fundingLinks` |
| <a name="profile-town-hall"></a>**Town Hall** | Turn on Discussions for a repository | Rare | 6% <sub>estimated</sub> | `repository.hasDiscussionsEnabled` |
| <a name="profile-tidy"></a>**Tidy** | Archive 5 repositories | Rare | 12% <sub>estimated</sub> | `repository.isArchived` |
| <a name="profile-packager"></a>**Packager** | Attach a file to a release | Rare | 12% <sub>estimated</sub> | `release.releaseAssets.totalCount` |
| <a name="profile-semver"></a>**Semver** | Tag 10 releases as vMAJOR.MINOR.PATCH | Rare | 12% <sub>estimated</sub> | `release.tagName` |
| <a name="profile-form-filler"></a>**Form Filler** | Add issue templates to a repository | Rare | 8% <sub>estimated</sub> | `object("HEAD:.github/ISSUE_TEMPLATE")` |
| <a name="profile-roadmap"></a>**Roadmap** | Use 5 milestones on one repository | Rare | 4% <sub>estimated</sub> | `repository.milestones.totalCount` |
| <a name="profile-label-maker"></a>**Label Maker** | Define 25 labels on one repository | Rare | 6% <sub>estimated</sub> | `repository.labels.totalCount` |

### Secret

| Achievement | Earned by | Rarity | Who earns it | Source |
| :-- | :-- | :-- | :-- | :-- |
| <a name="profile-new-year"></a>**New Year** <sub>secret</sub> | Contribute on 1 January | Uncommon | 15% <sub>derived</sub> | `contributionCalendar` |
| <a name="profile-leap-day"></a>**Leap Day** <sub>secret</sub> | Contribute on 29 February | Rare | 5% <sub>derived</sub> | `contributionCalendar` |
| <a name="profile-green-wall"></a>**Green Wall** <sub>secret</sub> | Contribute in every week of a calendar year | Epic | 2% <sub>derived</sub> | `contributionCalendar` |
| <a name="profile-homecoming"></a>**Homecoming** <sub>secret</sub> | Contribute on the anniversary of the day you joined | Rare | 10% <sub>derived</sub> | `contributionCalendar + user.createdAt` |
| <a name="profile-friday-the-13th"></a>**Friday the 13th** <sub>secret</sub> | Contribute on a Friday the 13th | Rare | 12% <sub>derived</sub> | `contributionCalendar` |
| <a name="profile-midnight-oil"></a>**Midnight Oil** <sub>secret, heavy</sub> | Author a commit at exactly midnight | Epic | 3% <sub>estimated</sub> | `commit timestamps` |
| <a name="profile-the-answer"></a>**The Answer** <sub>secret</sub> | Have a trophy total read exactly 42 on a daily check | Rare | 4% <sub>estimated</sub> | `any core count == 42` |
| <a name="profile-full-house"></a>**Full House** <sub>secret</sub> | Hold every core trophy at Gold or better | Legendary | 0.5% <sub>estimated</sub> | `core tiers` |
| <a name="profile-constellation"></a>**Constellation** <sub>secret</sub> | Earn five stars on one trophy | Legendary | 0.1% <sub>estimated</sub> | `core stars` |
| <a name="profile-inbox-zero"></a>**Inbox Zero** <sub>secret</sub> | Have no open issues across your repositories, with at least 25 closed | Rare | 5% <sub>estimated</sub> | `repositories.issues(states: OPEN)` |
| <a name="profile-ghost"></a>**Ghost** <sub>secret</sub> | Come back after a year away | Uncommon | 20% <sub>estimated</sub> | `contributionCalendar` |
| <a name="profile-round-number"></a>**Round Number** <sub>secret</sub> | Have a trophy total land exactly on 1,000 | Epic | 3% <sub>estimated</sub> | `any core count == 1000` |

### Maker

| Achievement | Earned by | Rarity | Who earns it | Source |
| :-- | :-- | :-- | :-- | :-- |
| <a name="profile-trophy-maker"></a>**Trophy Maker** <sub>owner of `tannergolden/markdown` only</sub> | Own tannergolden/markdown, the kit that draws these | Legendary | 0.001% <sub>measured</sub> | `viewer.login == repository(owner: "tannergolden", name: "markdown").owner.login` |
| <a name="profile-badge-maker"></a>**Badge Maker** <sub>owner of `tannergolden/markdown` only</sub> | Own tannergolden/markdown, the kit that draws the badges beside these | Legendary | 0.001% <sub>measured</sub> | `viewer.login == repository(owner: "tannergolden", name: "markdown").owner.login` |
| <a name="profile-standard-bearer"></a>**Standard Bearer** <sub>owner of `tannergolden/standards` only</sub> | Own tannergolden/standards, the rules every repository on the account follows and the workflows that enforce them | Legendary | 0.001% <sub>measured</sub> | `viewer.login == repository(owner: "tannergolden", name: "standards").owner.login` |
| <a name="profile-pathfinder"></a>**Pathfinder** <sub>owner of `tannergolden/path` only</sub> | Own tannergolden/path, the golden path every new repository starts from | Legendary | 0.001% <sub>measured</sub> | `viewer.login == repository(owner: "tannergolden", name: "path").owner.login` |

---

<a name="repository"></a>

## 📦 Repository Mode

The subject is one repository: the one the stub runs in. Health is binary here, Reach draws on the ledger and the traffic API, and stars exclude the owner and, for an organization, its members.

### The 8 core trophies

| Trophy | Counts | Enamel | Bronze | Silver | Gold | Platinum | Diamond | Source |
| :-- | :-- | :-- | --: | --: | --: | --: | --: | :-- |
| <a name="repository-stars"></a>**Stars** | Stargazers, owner and members excluded | `amber` | 10 | 100 | 500 | 2,000 | 10,000 | `repository.stargazers` |
| <a name="repository-forks"></a>**Forks** | Forks by other accounts | `jade` | 5 | 25 | 100 | 500 | 2,000 | `repository.forks` |
| <a name="repository-contributors"></a>**Contributors** | People with a merged commit or pull request | `rose` | 2 | 5 | 15 | 50 | 200 | `history authors + pullRequests(states: MERGED).author` |
| <a name="repository-commits"></a>**Commits** | Commits on the default branch | `emerald` | 100 | 500 | 2,000 | 5,000 | 20,000 | `defaultBranchRef.target.history.totalCount` |
| <a name="repository-releases"></a>**Releases** | Published releases | `teal` | 1 | 5 | 20 | 50 | 200 | `repository.releases.totalCount` |
| <a name="repository-merged"></a>**Merged PRs** | Pull requests merged | `violet` | 10 | 50 | 250 | 1,000 | 5,000 | `pullRequests(states: MERGED).totalCount` |
| <a name="repository-resolved"></a>**Issues Resolved** | Issues closed as completed | `crimson` | 10 | 50 | 250 | 1,000 | 5,000 | `issues(states: CLOSED), stateReason COMPLETED` |
| <a name="repository-active"></a>**Active Days** | Days with at least one commit | `tangerine` | 30 days | 100 days | 365 days | 1,000 days | 2,500 days | `history.committedDate, distinct days` |

Where each tier sits, as the share of starred public repositories at or above it:

| Trophy | Bronze | Silver | Gold | Platinum | Diamond | Basis |
| :-- | --: | --: | --: | --: | --: | :-- |
| **Stars** | top 8.9% | top 1.5% | top 0.38% | top 0.1% | top 0.017% | measured: every starred public repository counted by the search API, 2026-09-24 |
| **Forks** | top 7.1% | top 1.8% | top 0.47% | top 0.087% | top 0.017% | measured: every starred public repository counted by the search API, 2026-09-24 |
| **Contributors** | top 43% | top 9.8% | top 0.98% | top 0.42% | top 0.032% | measured: 200 repositories in 5 star bands, weighted by band, 2026-09-24 |
| **Commits** | top 8% | top 0.83% | top 0.2% | top 0.073% | top 0.01% | measured: 200 repositories in 5 star bands, weighted by band, 2026-09-24 |
| **Releases** | top 10% | top 4.2% | top 0.9% | top 0.53% | top 0.19% | measured: 200 repositories in 5 star bands, weighted by band, 2026-09-24 |
| **Merged PRs** | top 6.7% | top 0.67% | top 0.21% | top 0.068% | top 0.015% | measured: 200 repositories in 5 star bands, weighted by band, 2026-09-24 |
| **Issues Resolved** | top 9.6% | top 0.94% | top 0.22% | top 0.041% | top 0.0055% | measured: 200 repositories in 5 star bands, weighted by band, 2026-09-24 |
| **Active Days** | top 15% | top 5% | top 1% | top 0.2% | top 0.04% | estimated: 1.66 pushes a quarter per developer on average |

### The 100 achievements

### Launch

| Achievement | Earned by | Rarity | Who earns it | Source |
| :-- | :-- | :-- | :-- | :-- |
| <a name="repository-first-star"></a>**First Star** | Receive a star from someone else | Common | 100% <sub>measured</sub> | `stargazers, owner excluded` |
| <a name="repository-first-fork"></a>**First Fork** | Be forked by another account | Common | 40% <sub>estimated</sub> | `forks` |
| <a name="repository-first-watcher"></a>**First Watcher** | Gain a watcher who is not the owner | Common | 60% <sub>estimated</sub> | `watchers` |
| <a name="repository-first-release"></a>**First Release** | Publish a release | Rare | 12% <sub>estimated</sub> | `releases.totalCount` |
| <a name="repository-first-merge"></a>**First Merge** | Merge a pull request | Uncommon | 30% <sub>estimated</sub> | `pullRequests(states: MERGED)` |
| <a name="repository-outside-help"></a>**Outside Help** | Merge a pull request from someone other than the owner | Rare | 8% <sub>estimated</sub> | `pullRequests(states: MERGED).author != owner` |
| <a name="repository-stranger-report"></a>**Stranger Report** | Receive an issue from someone who has never contributed | Uncommon | 15% <sub>estimated</sub> | `issues.author not in contributors` |
| <a name="repository-first-tag"></a>**First Tag** | Push a tag | Uncommon | 20% <sub>estimated</sub> | `refs(refPrefix: "refs/tags/")` |
| <a name="repository-named"></a>**Named** | Set a description | Common | 70% <sub>estimated</sub> | `repository.description` |
| <a name="repository-front-door"></a>**Front Door** | Set a homepage link | Uncommon | 20% <sub>estimated</sub> | `repository.homepageUrl` |
| <a name="repository-filed"></a>**Filed** | Add 3 topics | Uncommon | 15% <sub>estimated</sub> | `repositoryTopics.totalCount` |
| <a name="repository-poster"></a>**Poster** | Upload a social preview image | Epic | 3% <sub>estimated</sub> | `repository.usesCustomOpenGraphImage` |

### Health

| Achievement | Earned by | Rarity | Who earns it | Source |
| :-- | :-- | :-- | :-- | :-- |
| <a name="repository-licensed"></a>**Licensed** | Choose a license | Common | 55% <sub>estimated</sub> | `repository.licenseInfo` |
| <a name="repository-documented"></a>**Documented** | Have a README and a description | Common | 75% <sub>estimated</sub> | `object("HEAD:README.md") + description` |
| <a name="repository-welcome-mat"></a>**Welcome Mat** | Publish a contributing guide | Rare | 6% <sub>estimated</sub> | `CONTRIBUTING.md, or the account .github repository` |
| <a name="repository-house-rules"></a>**House Rules** | Publish a code of conduct | Rare | 4% <sub>estimated</sub> | `repository.codeOfConduct` |
| <a name="repository-locksmith"></a>**Locksmith** | Publish a security policy | Epic | 1.5% <sub>estimated</sub> | `repository.isSecurityPolicyEnabled` |
| <a name="repository-gatekeeper"></a>**Gatekeeper** | Add a CODEOWNERS file | Epic | 2% <sub>estimated</sub> | `object("HEAD:.github/CODEOWNERS")` |
| <a name="repository-form-filler"></a>**Form Filler** | Add issue templates | Rare | 4% <sub>estimated</sub> | `object("HEAD:.github/ISSUE_TEMPLATE")` |
| <a name="repository-paperwork"></a>**Paperwork** | Add a pull request template | Epic | 3% <sub>estimated</sub> | `object("HEAD:.github/pull_request_template.md")` |
| <a name="repository-auto-pilot"></a>**Auto-pilot** | Configure Dependabot | Rare | 6% <sub>estimated</sub> | `object("HEAD:.github/dependabot.yml")` |
| <a name="repository-changelog"></a>**Changelog** | Keep a CHANGELOG.md | Rare | 10% <sub>estimated</sub> | `object("HEAD:CHANGELOG.md")` |
| <a name="repository-well-formed"></a>**Well-Formed** | Add an .editorconfig | Uncommon | 15% <sub>estimated</sub> | `object("HEAD:.editorconfig")` |
| <a name="repository-town-hall"></a>**Town Hall** | Turn on Discussions | Epic | 3% <sub>estimated</sub> | `repository.hasDiscussionsEnabled` |
| <a name="repository-protected"></a>**Protected** | Protect the default branch with a ruleset | Rare | 8% <sub>estimated</sub> | `repository.rulesets targeting ~DEFAULT_BRANCH` |
| <a name="repository-clean-bill"></a>**Clean Bill** | Have zero open Dependabot alerts | Common | 40% <sub>estimated</sub> | `vulnerabilityAlerts(states: OPEN), needs security-events: read` |
| <a name="repository-open-hand"></a>**Open Hand** | Add a FUNDING.yml | Epic | 3% <sub>estimated</sub> | `repository.fundingLinks` |
| <a name="repository-support-line"></a>**Support Line** | Publish a SUPPORT.md | Epic | 1.5% <sub>estimated</sub> | `object("HEAD:SUPPORT.md")` |
| <a name="repository-label-maker"></a>**Label Maker** | Define 25 labels | Rare | 5% <sub>estimated</sub> | `repository.labels.totalCount` |
| <a name="repository-roadmap"></a>**Roadmap** | Use 5 milestones | Epic | 3% <sub>estimated</sub> | `repository.milestones.totalCount` |

### Craft

| Achievement | Earned by | Rarity | Who earns it | Source |
| :-- | :-- | :-- | :-- | :-- |
| <a name="repository-by-the-book"></a>**By the Book** <sub>tiers 100 / 500 / 2,000, heavy</sub> | Land 100, 500 and 2,000 conventional commits | Rare → Epic → Legendary | 5% → 1.5% → 0.3% <sub>estimated</sub> | `commit messages` |
| <a name="repository-signed"></a>**Signed** <sub>tiers 100 / 1,000, heavy</sub> | Land 100 and 1,000 signed commits | Rare → Epic | 6% → 1% <sub>estimated</sub> | `commit.signature.isValid` |
| <a name="repository-gitmoji"></a>**Gitmoji** <sub>tiers 100 / 500, heavy</sub> | Land 100 and 500 commits that start with an emoji | Epic → Legendary | 3% → 0.8% <sub>estimated</sub> | `commit messages` |
| <a name="repository-semver"></a>**Semver** | Tag 10 releases as vMAJOR.MINOR.PATCH | Rare | 6% <sub>estimated</sub> | `release.tagName` |
| <a name="repository-green-machine"></a>**Green Machine** <sub>tiers 100 / 1,000 / 10,000</sub> | Finish 100, 1,000 and 10,000 successful workflow runs | Rare → Epic → Legendary | 8% → 2.5% → 0.4% <sub>estimated</sub> | `REST actions/runs?status=success` |
| <a name="repository-test-suite"></a>**Test Suite** | Keep a tests directory with files in it | Uncommon | 35% <sub>estimated</sub> | `object("HEAD:tests") or test/` |
| <a name="repository-wired"></a>**Wired** | Run at least one workflow | Uncommon | 30% <sub>estimated</sub> | `object("HEAD:.github/workflows")` |
| <a name="repository-release-notes"></a>**Release Notes** | Write notes on 10 releases | Rare | 5% <sub>estimated</sub> | `release.description` |
| <a name="repository-packager"></a>**Packager** | Attach a file to a release | Rare | 8% <sub>estimated</sub> | `release.releaseAssets.totalCount` |
| <a name="repository-prerelease"></a>**Prerelease** | Publish a pre-release | Rare | 5% <sub>estimated</sub> | `release.isPrerelease` |
| <a name="repository-squeaky"></a>**Squeaky** | Have no open pull request older than 90 days | Common | 45% <sub>estimated</sub> | `pullRequests(states: OPEN).createdAt` |
| <a name="repository-small-steps"></a>**Small Steps** <sub>heavy</sub> | Keep the median commit under 50 changed lines | Uncommon | 30% <sub>estimated</sub> | `commit.additions + deletions, last 500 commits` |
| <a name="repository-follows-the-standards"></a>**Follows the Standards** | Call tannergolden/standards from a workflow | Legendary | 0.01% <sub>measured</sub> | `workflow files containing uses: tannergolden/standards` |
| <a name="repository-golden-path"></a>**Golden Path** | Be generated from tannergolden/path | Legendary | 0.01% <sub>measured</sub> | `repository.templateRepository, or the template fingerprint` |
| <a name="repository-containerized"></a>**Containerized** | Ship a Dockerfile | Uncommon | 15% <sub>estimated</sub> | `object("HEAD:Dockerfile")` |
| <a name="repository-ready-room"></a>**Ready Room** | Ship a dev container | Epic | 3% <sub>estimated</sub> | `object("HEAD:.devcontainer")` |

### Community

| Achievement | Earned by | Rarity | Who earns it | Source |
| :-- | :-- | :-- | :-- | :-- |
| <a name="repository-ten-strong"></a>**Ten Strong** <sub>tiers 10 / 50 / 100</sub> | Reach 10, 50 and 100 contributors | Rare → Legendary → Legendary | 4% → 0.6% → 0.25% <sub>estimated</sub> | `distinct contributors` |
| <a name="repository-reviewed"></a>**Reviewed** | Have each of the last 100 merged pull requests reviewed | Epic | 3% <sub>estimated</sub> | `pullRequests.reviews.totalCount` |
| <a name="repository-fast-reply"></a>**Fast Reply** | Answer new issues within a day, at the median of the last 50 | Rare | 6% <sub>estimated</sub> | `issues.comments[0].createdAt - createdAt` |
| <a name="repository-good-first-issues"></a>**Good First Issues** | Label 5 issues good first issue | Epic | 3% <sub>estimated</sub> | `issues(labels: ["good first issue"])` |
| <a name="repository-help-wanted"></a>**Help Wanted** | Label 5 issues help wanted | Epic | 3% <sub>estimated</sub> | `issues(labels: ["help wanted"])` |
| <a name="repository-outside-merges"></a>**Outside Merges** <sub>tiers 10 / 50 / 200</sub> | Merge 10, 50 and 200 pull requests from people other than the owner | Rare → Epic → Legendary | 4% → 1% → 0.2% <sub>estimated</sub> | `pullRequests(states: MERGED).author != owner` |
| <a name="repository-answered"></a>**Answered** | Mark 10 discussions as answered | Epic | 1% <sub>estimated</sub> | `discussions(answered: true)` |
| <a name="repository-triage"></a>**Triage** | Keep every open issue labeled | Rare | 5% <sub>estimated</sub> | `issues(states: OPEN) without labels == 0` |
| <a name="repository-well-maintained"></a>**Well Maintained** | Merge 25 Dependabot pull requests | Rare | 5% <sub>estimated</sub> | `pullRequests by app/dependabot, merged` |
| <a name="repository-talkative"></a>**Talkative** | Collect 1,000 issue comments | Epic | 1% <sub>estimated</sub> | `issues.comments.totalCount, summed` |
| <a name="repository-popular-opinion"></a>**Popular Opinion** | Have an issue with 50 thumbs up | Epic | 1.5% <sub>estimated</sub> | `issue.reactions(content: THUMBS_UP).totalCount` |
| <a name="repository-long-thread"></a>**Long Thread** | Have an issue with 100 comments | Epic | 1.5% <sub>estimated</sub> | `issue.comments.totalCount` |
| <a name="repository-mentor"></a>**Mentor** <sub>heavy</sub> | Merge a pull request after requesting changes on it | Rare | 6% <sub>estimated</sub> | `reviews(states: CHANGES_REQUESTED) then merged` |
| <a name="repository-regulars"></a>**Regulars** | Have 5 contributors with 10 or more commits each | Epic | 1.5% <sub>estimated</sub> | `history authors, counted` |
| <a name="repository-org-backed"></a>**Org Backed** | Be owned by an organization | Uncommon | 15% <sub>estimated</sub> | `repository.owner.__typename == Organization` |
| <a name="repository-crew"></a>**Crew** | Have 5 collaborators | Rare | 8% <sub>estimated</sub> | `repository.collaborators.totalCount` |

### Reach

| Achievement | Earned by | Rarity | Who earns it | Source |
| :-- | :-- | :-- | :-- | :-- |
| <a name="repository-watched"></a>**Watched** <sub>tiers 25 / 100 / 1,000</sub> | Reach 25, 100 and 1,000 watchers | Epic → Legendary → Legendary | 1.5% → 0.4% → 0.03% <sub>estimated</sub> | `repository.watchers.totalCount` |
| <a name="repository-used-by"></a>**Used By** <sub>tiers 10 / 100 / 1,000, heavy</sub> | Be a dependency of 10, 100 and 1,000 repositories | Rare → Legendary → Legendary | 4% → 0.8% → 0.1% <sub>estimated</sub> | `dependents, from the dependency graph` |
| <a name="repository-star-of-the-week"></a>**Star of the Week** | Gain 50 stars in one week | Epic | 1.5% <sub>estimated</sub> | `ledger snapshots` |
| <a name="repository-trending"></a>**Trending** | Gain 100 stars in one week | Legendary | 0.6% <sub>estimated</sub> | `ledger snapshots` |
| <a name="repository-forked-far"></a>**Forked Far** | Have a fork that earns 100 stars of its own | Legendary | 0.5% <sub>estimated</sub> | `forks.stargazerCount` |
| <a name="repository-living-forks"></a>**Living Forks** | Have 10 forks with commits of their own | Epic | 3% <sub>estimated</sub> | `forks where pushedAt > createdAt` |
| <a name="repository-registry"></a>**Registry** | Publish a package from this repository | Rare | 5% <sub>estimated</sub> | `repository.packages.totalCount` |
| <a name="repository-downloaded"></a>**Downloaded** <sub>tiers 1,000 / 10,000 / 100,000</sub> | Reach 1,000, 10,000 and 100,000 release downloads | Rare → Epic → Legendary | 4% → 1.2% → 0.25% <sub>estimated</sub> | `releaseAssets.downloadCount, summed` |
| <a name="repository-visited"></a>**Visited** | Reach 1,000 unique visitors in two weeks | Epic | 3% <sub>estimated</sub> | `REST traffic/views, needs push access` |
| <a name="repository-cloned"></a>**Cloned** | Reach 100 unique cloners in two weeks | Rare | 5% <sub>estimated</sub> | `REST traffic/clones` |
| <a name="repository-referred"></a>**Referred** | Be linked from 5 referring sites | Rare | 4% <sub>estimated</sub> | `REST traffic/popular/referrers` |
| <a name="repository-big-name"></a>**Big Name** <sub>heavy</sub> | Be starred by someone with 10,000 followers | Epic | 3% <sub>estimated</sub> | `stargazers.followers.totalCount` |
| <a name="repository-stargazer-streak"></a>**Stargazer Streak** | Gain a star in each of 12 consecutive weeks | Epic | 1.5% <sub>estimated</sub> | `ledger snapshots` |
| <a name="repository-fork-magnet"></a>**Fork Magnet** | Gain 10 forks in one week | Epic | 1.5% <sub>estimated</sub> | `ledger snapshots` |

### Rhythm

| Achievement | Earned by | Rarity | Who earns it | Source |
| :-- | :-- | :-- | :-- | :-- |
| <a name="repository-weekly-beat"></a>**Weekly Beat** | Land a commit in 52 consecutive weeks | Epic | 2% <sub>estimated</sub> | `history.committedDate` |
| <a name="repository-monthly-release"></a>**Monthly Release** | Publish a release in each of 12 consecutive months | Legendary | 0.8% <sub>estimated</sub> | `releases.createdAt` |
| <a name="repository-streak"></a>**Streak** <sub>tiers 30 / 100 / 365</sub> | Commit on 30, 100 and 365 consecutive days | Epic → Legendary → Legendary | 3% → 0.5% → 0.05% <sub>estimated</sub> | `history.committedDate` |
| <a name="repository-comeback"></a>**Comeback** | Land a commit after a gap of 90 days | Common | 40% <sub>estimated</sub> | `history.committedDate` |
| <a name="repository-night-shift"></a>**Night Shift** <sub>heavy</sub> | Land 50 commits between midnight and 5 a.m. | Rare | 8% <sub>estimated</sub> | `commit timestamps` |
| <a name="repository-weekend-project"></a>**Weekend Project** | Land commits on 26 weekends in one year | Rare | 8% <sub>estimated</sub> | `history.committedDate` |
| <a name="repository-marathon-day"></a>**Marathon Day** | Land 50 commits in a single day | Rare | 10% <sub>estimated</sub> | `history.committedDate` |
| <a name="repository-big-week"></a>**Big Week** | Land 100 commits in one week | Rare | 6% <sub>estimated</sub> | `history.committedDate` |
| <a name="repository-long-game"></a>**Long Game** <sub>tiers 3 / 5 / 10</sub> | Land commits in 3, 5 and 10 different years | Uncommon → Rare → Epic | 25% → 10% → 1.5% <sub>estimated</sub> | `history.committedDate` |
| <a name="repository-alive"></a>**Alive** | Land a commit in the last 30 days | Uncommon | 20% <sub>estimated</sub> | `history.committedDate` |
| <a name="repository-friday-deploy"></a>**Friday Deploy** | Publish a release on a Friday | Rare | 8% <sub>estimated</sub> | `releases.createdAt` |
| <a name="repository-same-day-fix"></a>**Same-Day Fix** | Close 10 issues within a day of them being opened | Rare | 6% <sub>estimated</sub> | `issues.closedAt - createdAt` |

### Secret

| Achievement | Earned by | Rarity | Who earns it | Source |
| :-- | :-- | :-- | :-- | :-- |
| <a name="repository-round-number"></a>**Round Number** <sub>secret</sub> | Have a trophy total land exactly on 1,000 | Epic | 2% <sub>estimated</sub> | `any core count == 1000` |
| <a name="repository-the-answer"></a>**The Answer** <sub>secret</sub> | Have a trophy total read exactly 42 on a daily check | Epic | 3% <sub>estimated</sub> | `any core count == 42` |
| <a name="repository-palindrome"></a>**Palindrome** <sub>secret</sub> | Have a commit count that reads the same backwards | Rare | 8% <sub>estimated</sub> | `history.totalCount` |
| <a name="repository-leap-day"></a>**Leap Day** <sub>secret</sub> | Publish a release on 29 February | Legendary | 0.3% <sub>estimated</sub> | `releases.createdAt` |
| <a name="repository-friday-the-13th"></a>**Friday the 13th** <sub>secret</sub> | Publish a release on a Friday the 13th | Epic | 1.5% <sub>estimated</sub> | `releases.createdAt` |
| <a name="repository-new-year"></a>**New Year** <sub>secret</sub> | Land a commit on 1 January | Rare | 5% <sub>estimated</sub> | `history.committedDate` |
| <a name="repository-birthday"></a>**Birthday** <sub>secret</sub> | Land a commit on the anniversary of the first commit | Rare | 6% <sub>estimated</sub> | `history.committedDate` |
| <a name="repository-midnight-oil"></a>**Midnight Oil** <sub>secret, heavy</sub> | Land a commit at exactly midnight | Epic | 2% <sub>estimated</sub> | `commit timestamps` |
| <a name="repository-green-wall"></a>**Green Wall** <sub>secret</sub> | Land a commit in every week of a calendar year | Epic | 1.5% <sub>estimated</sub> | `history.committedDate` |
| <a name="repository-ghost"></a>**Ghost** <sub>secret</sub> | Land a commit after a year of silence | Uncommon | 15% <sub>estimated</sub> | `history.committedDate` |
| <a name="repository-full-house"></a>**Full House** <sub>secret</sub> | Hold every core trophy at Gold or better | Legendary | 0.3% <sub>estimated</sub> | `core tiers` |
| <a name="repository-constellation"></a>**Constellation** <sub>secret</sub> | Earn five stars on one trophy | Legendary | 0.05% <sub>estimated</sub> | `core stars` |

---

## 📐 How The Numbers Were Set

A tier name and a rarity are claims about how many reach a number. Every
threshold and every rarity in this catalogue is pinned to a share of a
reference population, and each share says how it was got.

**Two reference populations.**

- **Profile mode: located GitHub accounts.** Every account with a location set,
  as collected by [`gayanvoice/top-github-users`](https://github.com/gayanvoice/top-github-users)
  across 138 countries: 122,914 accounts refreshed on 2026-09-24, each with its
  followers and its public and private contributions over the last year. A
  located account is a person who filled in a profile, which is the population
  that puts a trophy case on one. The median has 36 followers and 18 public
  contributions a year; 26% made none.
- **Repository mode: public, non-fork repositories with at least one star,**
  measured through GitHub's API on 2026-09-24 by `markdown-kit calibrate` (the
  **📐 Calibrate** workflow, quarterly). Stars and forks are counted exactly:
  the search API answers how many of the 32,180,494 such repositories sit at or
  above each threshold. The other cores come from 200 repositories sampled
  across five star bands (40 in each of 1 to 9, 10 to 99, 100 to 999, 1,000 to 9,999, 10,000+ stars), each measured the way a case measures
  it (contributors, commits, releases, merged pull requests, resolved
  issues) and weighted by its band's share of the population. Active days
  cannot be read from the API and stay estimated.

**Three kinds of number.** *Measured* is read off a dataset directly (followers,
yearly activity, and every repository-mode core the sample carries). *Derived* is a dataset scaled by a stated factor (all-time
commits as three times one year's contributions; 2.22 repositories per developer
from the Innovation Graph). *Estimated* applies the population's shape to a count
no dataset holds, using the anchors above and the medians
[`github-readme-stats`](https://github.com/anuraghazra/github-readme-stats) uses
for its ranks (250 commits a year, 50 pull requests, 25 issues, 2 reviews, 50
stars, 10 followers).

**Rarity follows the share.** Common is 40% or more of the population, Uncommon
15% to 40%, Rare 4% to 15%, Epic 1% to 4%, Legendary under 1%. The tier ladder
aims at the same cuts for every trophy: Bronze about the top half, Silver the
top quarter to third, Gold the top tenth, Platinum the top 3%, Diamond the top
1%. The **Top N%** chip on a card interpolates between a trophy's anchors, so a
value between two tiers reads a share between their two shares.

The measured column is the honest one; the estimated column is a model, stated
so it can be argued with. When a better dataset turns up, the numbers move and
the words follow, in `src/domain/trophies/calibration.py`.

## 🏅 Tiers and Rarities

| Tier | Unranked | Bronze | Silver | Gold | Platinum | Diamond |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| Metal | ghost | bronze | silver | gold | platinum | diamond |

| Rarity | Common | Uncommon | Rare | Epic | Legendary |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Metal | bronze | silver | gold | platinum | diamond |

---

## 🔗 See also

> [!TIP]
> The [README](../README.md) shows a case in use. Every trophy and achievement
> here is read from `src/domain/trophies/catalogue.py` and every number from
> `src/domain/trophies/calibration.py`; edit those and run `make catalogue`,
> never this file.

---

<div align="center">

**Every threshold named. Every share stated.**

[↑ Back to Top](#top)

</div>
