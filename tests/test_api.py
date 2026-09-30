"""Tests of the API client.

The HTTP layer is replaced by a fake session so the tests are fast and
deterministic. The application itself makes real calls to api.github.com.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

import requests

from github_analyzer.api import (
    GitHubClient,
    GitHubError,
    NetworkError,
    RateLimitError,
    UserNotFoundError,
)


def fake_response(status=200, json_data=None, headers=None):
    response = MagicMock()
    response.status_code = status
    response.ok = 200 <= status < 300
    response.headers = headers or {}
    response.json.return_value = json_data
    return response


def make_client(*responses_or_exc):
    session = MagicMock()
    session.headers = {}
    session.get.side_effect = list(responses_or_exc)
    return GitHubClient(token="", session=session), session


class GitHubClientTests(unittest.TestCase):
    def test_get_user(self):
        client, session = make_client(fake_response(json_data={"login": "octo"}))
        self.assertEqual(client.get_user("octo")["login"], "octo")
        self.assertIn("/users/octo", session.get.call_args.args[0])

    def test_get_repos_single_page(self):
        client, _ = make_client(fake_response(json_data=[{"name": "a"}]))
        self.assertEqual(client.get_repos("octo"), [{"name": "a"}])

    def test_get_repos_follows_pagination(self):
        page1 = [{"name": str(i)} for i in range(100)]
        page2 = [{"name": "last"}]
        client, session = make_client(
            fake_response(json_data=page1), fake_response(json_data=page2)
        )
        self.assertEqual(len(client.get_repos("octo")), 101)
        self.assertEqual(session.get.call_count, 2)

    def test_unknown_user(self):
        client, _ = make_client(fake_response(status=404))
        with self.assertRaises(UserNotFoundError):
            client.get_user("does-not-exist")

    def test_unknown_user_repos(self):
        client, _ = make_client(fake_response(status=404))
        with self.assertRaises(UserNotFoundError):
            client.get_repos("does-not-exist")

    def test_rate_limit(self):
        client, _ = make_client(
            fake_response(status=403, headers={"X-RateLimit-Remaining": "0"})
        )
        with self.assertRaises(RateLimitError):
            client.get_user("octo")

    def test_other_http_error(self):
        client, _ = make_client(fake_response(status=500))
        with self.assertRaises(GitHubError):
            client.get_user("octo")

    def test_network_error(self):
        client, _ = make_client(requests.ConnectionError("boom"))
        with self.assertRaises(NetworkError):
            client.get_user("octo")

    def test_token_from_environment(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "abc"}):
            client = GitHubClient(session=MagicMock(headers={}))
        self.assertEqual(client.session.headers["Authorization"], "Bearer abc")

    def test_no_token_means_no_authorization_header(self):
        with patch.dict(os.environ, {}, clear=True):
            client = GitHubClient(session=MagicMock(headers={}))
        self.assertNotIn("Authorization", client.session.headers)


if __name__ == "__main__":
    unittest.main()
