# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Reading commits for the heavy achievements: a hundred at a time, under a budget, cached by branch head.

What a commit says is `domain.trophies.scan`'s; this is the reading. It runs
under a page budget per run, remembers what it has read in the lock's
trophies record keyed by the branch head, and only reads a repository again
when its head moved. A big account is fully read within about a week of
daily runs and cheaply thereafter.
"""
from __future__ import annotations

from domain.trophies.scan import classify, empty_stats

HISTORY = """
query($owner:String!,$name:String!,$first:Int!,$after:String,$author:CommitAuthor){ rateLimit{cost}
  repository(owner:$owner,name:$name){ defaultBranchRef{ target{ ... on Commit{ oid
    history(first:$first,after:$after,author:$author){ totalCount pageInfo{hasNextPage endCursor}
      nodes{ oid message committedDate author{ date user{login} name } signature{isValid}
             authors(first:2){totalCount} changedFilesIfAvailable additions deletions } } } } } } }"""


def scan_repository(gh, owner: str, name: str, cache: dict, budget: dict, author_id: str | None = None,
                    page_size: int = 100) -> dict:
    """Read a repository's default-branch history into `cache[owner/name]`.

    `cache` is the ledger's scan section; `budget["pages"]` is decremented for
    every page read across the whole run. A repository whose recorded head
    still matches is returned as is. One whose head moved starts again; if the
    budget runs out mid-way the partial result is kept with `complete: False`
    and finished on a later run.
    """
    key = f"{owner}/{name}"
    entry = cache.get(key) or {}
    author = {"id": author_id} if author_id else None
    after = entry.get("cursor") if not entry.get("complete") else None
    head = None
    stats = entry.get("stats") if entry.get("cursor") else None
    while budget["pages"] > 0:
        data = gh.gql(HISTORY, owner=owner, name=name, first=page_size, after=after, author=author)
        ref = ((data.get("repository") or {}).get("defaultBranchRef") or {})
        target = ref.get("target") or {}
        head = target.get("oid")
        hist = target.get("history") or {}
        if head is None:
            cache[key] = {"head": None, "complete": True, "stats": empty_stats(), "total": 0}
            return cache[key]
        if entry.get("complete") and entry.get("head") == head:
            return entry  # nothing moved since last time
        if stats is None:
            stats = empty_stats()
        budget["pages"] -= 1
        for node in hist.get("nodes") or []:
            if node:
                classify(node, stats)
        info = hist.get("pageInfo") or {}
        cache[key] = {"head": head, "complete": not info.get("hasNextPage"), "cursor": info.get("endCursor"),
                      "stats": stats, "total": hist.get("totalCount", stats["total"])}
        if not info.get("hasNextPage"):
            cache[key]["cursor"] = None
            return cache[key]
        after = info.get("endCursor")
    return cache.get(key) or {"head": head, "complete": False, "stats": stats or empty_stats(), "total": 0}
