"""Thin client around the GitHub REST API (https://docs.github.com/en/rest)."""

from __future__ import annotations

import os
from typing import Any

import requests

API_BASE_URL = "https://api.github.com"
DEFAULT_TIMEOUT = 10  # seconds
PER_PAGE = 100  # maximum allowed by the GitHub API
MAX_PAGES = 10  # safety cap: at most 1000 repositories


class GitHubError(Exception):
    """Base class for all errors raised by this package."""


class UserNotFoundError(GitHubError):
    """The requested GitHub user does not exist."""


class RateLimitError(GitHubError):
    """The GitHub API rate limit has been reached."""


class NetworkError(GitHubError):
    """The GitHub API could not be reached (DNS, timeout, connection...)."""


class GitHubClient:
    """Minimal GitHub REST API client.

    Works without authentication for public endpoints (60 requests/hour).
    A token can be given explicitly or through the ``GITHUB_TOKEN``
    environment variable to raise the rate limit (5000 requests/hour).
    """

    def __init__(
        self,
        token: str | None = None,
        session: requests.Session | None = None,
        base_url: str = API_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        if token is None:
            token = os.environ.get("GITHUB_TOKEN")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "github-profile-analyzer",
            }
        )
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def _get(self, path: str, params: dict[str, Any] | None = None) -> requests.Response:
        url = f"{self.base_url}{path}"
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
        except requests.RequestException as exc:
            raise NetworkError(f"Could not reach the GitHub API: {exc}") from exc

        if response.status_code in (403, 429) and (
            response.headers.get("X-RateLimit-Remaining") == "0"
            or response.status_code == 429
        ):
            raise RateLimitError(
                "GitHub API rate limit reached. Set GITHUB_TOKEN to increase it."
            )
        return response

    def get_user(self, username: str) -> dict[str, Any]:
        """Return the public profile of ``username`` (GET /users/{username})."""
        response = self._get(f"/users/{username}")
        if response.status_code == 404:
            raise UserNotFoundError(f"GitHub user '{username}' not found.")
        if not response.ok:
            raise GitHubError(f"Unexpected response from GitHub: HTTP {response.status_code}")
        return response.json()

    def get_repos(self, username: str) -> list[dict[str, Any]]:
        """Return all public repositories of ``username``, following pagination."""
        repos: list[dict[str, Any]] = []
        for page in range(1, MAX_PAGES + 1):
            response = self._get(
                f"/users/{username}/repos",
                params={"per_page": PER_PAGE, "page": page, "type": "owner"},
            )
            if response.status_code == 404:
                raise UserNotFoundError(f"GitHub user '{username}' not found.")
            if not response.ok:
                raise GitHubError(
                    f"Unexpected response from GitHub: HTTP {response.status_code}"
                )
            batch = response.json()
            repos.extend(batch)
            if len(batch) < PER_PAGE:
                break
        return repos
