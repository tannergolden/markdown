# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""A small GitHub client on urllib: GraphQL, REST, retries and a cost meter.

The banners, elements and trophies kits each carried a copy of this; here there
is one. Nothing in it knows what a page draws: it exists so a part can say what
it wants in one line, and so a test can hand in a fake with the same methods.

The token is the one the run is given: `MARKDOWN_TOKEN` when the workflow
passes one for private data, and otherwise the `GITHUB_TOKEN` every workflow
has, which reads everything public.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

GRAPHQL = "https://api.github.com/graphql"
REST = "https://api.github.com"
UA = "tannergolden-markdown"
TOKENS = ("MARKDOWN_TOKEN", "GITHUB_TOKEN")


class ApiError(RuntimeError):
    pass


def token_from_env(env: dict | None = None) -> str:
    env = os.environ if env is None else env
    return next((env[k] for k in TOKENS if env.get(k)), "")


class GitHub:
    """`gql(query, **variables)`, `rest(path)` and `paged(...)`, with retries on 5xx and on secondary limits."""

    def __init__(self, token: str | None = None, retries: int = 4, quiet: bool = False, sleep=time.sleep,
                 opener=urllib.request.urlopen):
        self.token = token or token_from_env()
        if not self.token:
            raise ApiError("no token: set GITHUB_TOKEN (every workflow has one) or MARKDOWN_TOKEN")
        self.retries = retries
        self.quiet = quiet
        self.calls = 0
        self.points = 0  # GraphQL rate-limit cost, summed from each response
        self.last_errors: list[str] = []  # per-field errors of the last GraphQL reply
        self._sleep = sleep
        self._open = opener

    # -- transport -------------------------------------------------------------
    def _request(self, url: str, body: bytes | None, accept: str) -> tuple[int, dict, object]:
        req = urllib.request.Request(url, data=body, method="POST" if body is not None else "GET")
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Accept", accept)
        req.add_header("User-Agent", UA)
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        if body is not None:
            req.add_header("Content-Type", "application/json")
        delay = 2.0
        for attempt in range(self.retries + 1):
            try:
                with self._open(req, timeout=60) as resp:  # noqa: S310 - a fixed https endpoint
                    self.calls += 1
                    raw = resp.read()
                    return resp.status, dict(resp.headers), (json.loads(raw) if raw else None)
            except urllib.error.HTTPError as exc:
                self.calls += 1
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                limited = exc.code in (403, 429) and bool(retry_after or "rate limit" in (exc.reason or "").lower())
                if exc.code == 404:
                    return 404, dict(exc.headers or {}), None
                if exc.code == 401:
                    raise ApiError(f"GitHub refused the token (401) for {url}") from exc
                if not (exc.code >= 500 or limited) or attempt == self.retries:
                    detail = exc.read().decode("utf-8", "replace")[:300] if exc.fp else ""
                    raise ApiError(f"GitHub answered {exc.code} for {url}: {detail}") from exc
                wait = float(retry_after) if retry_after else delay
                self._log(f"retrying after {exc.code} in {wait:.0f}s")
                self._sleep(wait)
                delay *= 2
            except (urllib.error.URLError, TimeoutError) as exc:
                if attempt == self.retries:
                    raise ApiError(f"network failure for {url}: {exc}") from exc
                self._sleep(delay)
                delay *= 2
        raise ApiError("unreachable")  # pragma: no cover

    def _log(self, msg: str) -> None:
        if not self.quiet:
            print(f"::debug::{msg}" if os.environ.get("GITHUB_ACTIONS") else f"  {msg}", file=sys.stderr)

    def _warn(self, msg: str) -> None:
        """A line the run log shows without debug logging switched on."""
        if not self.quiet:
            print(f"::warning::{msg}" if os.environ.get("GITHUB_ACTIONS") else f"  {msg}", file=sys.stderr)

    # -- the calls -----------------------------------------------------------------
    def gql(self, query: str, **variables) -> dict:
        body = json.dumps({"query": query, "variables": variables}).encode()
        _, _, data = self._request(GRAPHQL, body, "application/vnd.github+json")
        if not isinstance(data, dict):
            raise ApiError("GraphQL returned no body")
        cost = ((data.get("data") or {}).get("rateLimit") or {}).get("cost")
        if cost:
            self.points += cost
        errors = data.get("errors")
        if errors and not data.get("data"):
            raise ApiError("GraphQL: " + "; ".join(e.get("message", "?") for e in errors))
        # The path names the field, which is what a scope error hides.
        self.last_errors = [e.get("message", "?") + (f" (at {'.'.join(str(x) for x in e['path'])})" if e.get("path") else "")
                            for e in errors or []]
        for msg in self.last_errors:
            # Partial data with per-field errors (a private field, a missing
            # scope): keep what came back and say, visibly, what did not.
            self._warn("GraphQL partial: " + msg)
        return data["data"]

    def rest(self, path: str, accept: str = "application/vnd.github+json", **params):
        """GET a REST path. Returns the parsed body, or None on 404 or on 403 (no permission)."""
        url = path if path.startswith("http") else REST + path
        if params:
            url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
        try:
            status, _, data = self._request(url, None, accept)
        except ApiError as exc:
            if "answered 403" in str(exc):
                return None
            raise
        return None if status == 404 else data

    def rest_pages(self, path: str, per_page: int = 100, limit: int = 10, **params) -> list:
        """Every item of a REST list, a page at a time, up to `limit` pages."""
        out: list = []
        for page in range(1, limit + 1):
            data = self.rest(path, per_page=per_page, page=page, **params)
            items = data.get("items", []) if isinstance(data, dict) else (data or [])
            out.extend(items)
            if len(items) < per_page:
                break
        return out

    def paged(self, query: str, path: tuple, page_size: int = 100, limit: int = 10, **variables) -> list:
        """Walk a GraphQL connection at `path` (keys into the response) until it ends or `limit` pages."""
        nodes: list = []
        after = None
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


# --- a paced client, for the calibration --------------------------------------------------

def link_last(link: str) -> int | None:
    """The last page a Link header names, or None when there is only the one page."""
    m = re.search(r'[?&]page=(\d+)>;\s*rel="last"', link or "")
    return int(m.group(1)) if m else None


class Paced:
    """The smallest REST client that keeps inside GitHub's two rate limits, for `calibrate`.

    The calibration reads thousands of pages through search (thirty calls a
    minute) and REST (a thousand an hour with an Actions token), so this
    sleeps through a limit rather than failing on it, and hands back the
    headers too, because a count behind a paged endpoint is read off its
    Link header.
    """

    def __init__(self, token: str | None = None, quiet: bool = False, sleep=time.sleep, clock=time.time,
                 opener=urllib.request.urlopen):
        self.token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
        if not self.token:
            raise ApiError("no token: calibrate reads GitHub's API with GITHUB_TOKEN")
        self.quiet = quiet
        self.calls = 0
        self._sleep_fn, self._clock, self._open = sleep, clock, opener

    def get(self, path: str, params: dict | None = None):
        """(the JSON body or None, the headers). Sleeps through rate limits; None on 404, 409, 422 and 451."""
        url = path if path.startswith("http") else REST + path
        if params:
            url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
        for attempt in range(10):
            req = urllib.request.Request(url, headers={
                "Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github+json",
                "User-Agent": f"{UA}-calibrate", "X-GitHub-Api-Version": "2022-11-28"})
            try:
                with self._open(req, timeout=60) as r:
                    self.calls += 1
                    body = r.read()
                    headers = {k.lower(): v for k, v in r.headers.items()}
                    self._pace(headers)
                    return (json.loads(body) if body else None), headers
            except urllib.error.HTTPError as e:
                headers = {k.lower(): v for k, v in e.headers.items()}
                if e.code in (403, 429):
                    if "too large" in (e.read() or b"").decode("utf-8", "replace").lower():
                        return {"too_large": True}, headers
                    self._wait(headers, attempt)
                    continue
                if e.code in (404, 409, 422, 451):
                    return None, headers
                if e.code == 202:  # statistics being computed
                    self._sleep_fn(3)
                    continue
                self._sleep_fn(2 + attempt)
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                self._sleep_fn(2 + attempt)
        return None, {}

    def _pace(self, headers: dict) -> None:
        if headers.get("x-ratelimit-remaining") in ("0", "1") and headers.get("x-ratelimit-reset"):
            self._sleep(int(headers["x-ratelimit-reset"]) - self._clock() + 2)

    def _wait(self, headers: dict, attempt: int) -> None:
        if headers.get("retry-after"):
            self._sleep(int(headers["retry-after"]) + 1)
        elif headers.get("x-ratelimit-reset"):
            self._sleep(int(headers["x-ratelimit-reset"]) - self._clock() + 2)
        else:
            self._sleep(min(120, 15 * (attempt + 1)))

    def _sleep(self, seconds: float) -> None:
        seconds = max(1.0, min(seconds, 3600))
        if not self.quiet:
            print(f"  rate limit: sleeping {seconds:.0f}s", file=sys.stderr, flush=True)
        self._sleep_fn(seconds)

    def count(self, kind: str, q: str) -> int | None:
        """How many a search finds, or None when it could not ask."""
        data, _ = self.get(f"/search/{kind}", {"q": q, "per_page": 1})
        return None if data is None else data.get("total_count")

    def last_page(self, path: str, params: dict) -> int | None:
        """The count behind a paged endpoint, from its Link header's last page."""
        data, headers = self.get(path, dict(params, per_page=1))
        if isinstance(data, dict) and data.get("too_large"):
            return 500  # GitHub refuses to list more than 500 contributors
        if data is None:
            return 0
        n = link_last(headers.get("link", ""))
        return n if n is not None else (len(data) if isinstance(data, list) else 0)
