# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
import email.message
import io
import json
import os
import unittest
import urllib.error
from unittest import mock

from tests import support  # noqa: F401

from infra.github import ApiError, GitHub, token_from_env


class Reply:
    def __init__(self, body, status=200):
        self.status, self._body, self.headers = status, json.dumps(body).encode(), {}

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def http_error(code, reason="", retry_after=None, body=b"{}"):
    headers = email.message.Message()
    if retry_after is not None:
        headers["Retry-After"] = str(retry_after)
    return urllib.error.HTTPError("https://api.github.com/x", code, reason, headers, io.BytesIO(body))


class Script:
    """An opener that answers each request with the next of `replies` and remembers the requests."""

    def __init__(self, *replies):
        self.replies, self.requests = list(replies), []

    def __call__(self, req, timeout=None):
        self.requests.append(req)
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply


def client(*replies, **kw):
    script = Script(*replies)
    return GitHub("t0ken", quiet=True, sleep=lambda s: None, opener=script, **kw), script


class GitHubTest(unittest.TestCase):
    def test_the_markdown_token_comes_before_the_workflow_token(self):
        self.assertEqual(token_from_env({"GITHUB_TOKEN": "a", "MARKDOWN_TOKEN": "b"}), "b")
        self.assertEqual(token_from_env({"GITHUB_TOKEN": "a"}), "a")
        self.assertEqual(token_from_env({}), "")

    def test_no_token_is_said_plainly(self):
        with mock.patch.dict(os.environ, {}, clear=True), self.assertRaisesRegex(ApiError, "no token"):
            GitHub(quiet=True)

    def test_graphql_sends_the_token_and_sums_the_cost(self):
        gh, script = client(Reply({"data": {"viewer": {"login": "x"}, "rateLimit": {"cost": 2}}}))
        self.assertEqual(gh.gql("query { viewer { login } }")["viewer"]["login"], "x")
        self.assertEqual(gh.points, 2)
        self.assertEqual(script.requests[0].get_header("Authorization"), "Bearer t0ken")

    def test_graphql_keeps_partial_data_and_names_the_field(self):
        gh, _ = client(Reply({"data": {"a": 1}, "errors": [{"message": "no scope", "path": ["user", "email"]}]}))
        self.assertEqual(gh.gql("q"), {"a": 1})
        self.assertEqual(gh.last_errors, ["no scope (at user.email)"])

    def test_graphql_errors_without_data_fail(self):
        gh, _ = client(Reply({"errors": [{"message": "bad query"}]}))
        with self.assertRaisesRegex(ApiError, "bad query"):
            gh.gql("q")

    def test_a_server_error_is_retried(self):
        gh, script = client(http_error(502), Reply({"data": {"ok": True}}))
        self.assertEqual(gh.gql("q"), {"ok": True})
        self.assertEqual(len(script.requests), 2)

    def test_a_secondary_rate_limit_waits_as_told(self):
        waited = []
        script = Script(http_error(403, "rate limit", retry_after=7), Reply([1, 2]))
        gh = GitHub("t", quiet=True, sleep=waited.append, opener=script)
        self.assertEqual(gh.rest("/x"), [1, 2])
        self.assertEqual(waited, [7.0])

    def test_rest_gives_none_for_404_and_for_403(self):
        gh, _ = client(http_error(404), http_error(403, "Forbidden"))
        self.assertIsNone(gh.rest("/repos/a/b"))
        self.assertIsNone(gh.rest("/repos/a/b/private"))

    def test_a_refused_token_is_not_retried(self):
        gh, script = client(http_error(401))
        with self.assertRaisesRegex(ApiError, "refused the token"):
            gh.rest("/user")
        self.assertEqual(len(script.requests), 1)

    def test_rest_pages_stops_at_a_short_page(self):
        gh, script = client(Reply([1] * 2), Reply([2]))
        self.assertEqual(gh.rest_pages("/items", per_page=2), [1, 1, 2])
        self.assertIn("page=2", script.requests[1].full_url)

    def test_paged_walks_a_connection(self):
        page = lambda nodes, more, cur: Reply({"data": {"r": {"c": {"nodes": nodes, "pageInfo": {"hasNextPage": more, "endCursor": cur}}}}})
        gh, script = client(page([1, 2], True, "x"), page([3], False, None))
        self.assertEqual(gh.paged("q", ("r", "c"), page_size=2), [1, 2, 3])
        self.assertEqual(json.loads(script.requests[1].data)["variables"]["after"], "x")


if __name__ == "__main__":
    unittest.main()
