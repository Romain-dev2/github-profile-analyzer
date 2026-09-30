"""Pure analysis logic: turns raw GitHub API data into a report."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RepoSummary:
    name: str
    stars: int
    forks: int
    language: str | None
    created_at: str
    is_fork: bool


@dataclass
class ProfileReport:
    username: str
    name: str | None
    bio: str | None
    created_at: str
    public_repos: int
    followers: int
    following: int
    analyzed_repos: int = 0
    total_stars: int = 0
    total_forks: int = 0
    languages: dict[str, int] = field(default_factory=dict)
    top_repos: list[RepoSummary] = field(default_factory=list)

    @property
    def main_language(self) -> str | None:
        """Most used language (by number of repositories), or None."""
        return next(iter(self.languages), None)


def summarize_repo(raw: dict[str, Any]) -> RepoSummary:
    """Convert one raw repository object from the API into a RepoSummary."""
    return RepoSummary(
        name=raw.get("name", "?"),
        stars=raw.get("stargazers_count", 0) or 0,
        forks=raw.get("forks_count", 0) or 0,
        language=raw.get("language"),
        created_at=raw.get("created_at", ""),
        is_fork=bool(raw.get("fork", False)),
    )


def analyze_profile(
    user: dict[str, Any],
    repos: list[dict[str, Any]],
    top_n: int = 5,
    include_forks: bool = False,
) -> ProfileReport:
    """Build a ProfileReport from the raw user and repository data.

    Forked repositories are ignored by default so the statistics reflect
    the user's own work.
    """
    summaries = [summarize_repo(r) for r in repos]
    if not include_forks:
        summaries = [s for s in summaries if not s.is_fork]

    languages = Counter(s.language for s in summaries if s.language)
    top = sorted(summaries, key=lambda s: (-s.stars, -s.forks, s.name.lower()))[:top_n]

    return ProfileReport(
        username=user.get("login", ""),
        name=user.get("name"),
        bio=user.get("bio"),
        created_at=user.get("created_at", ""),
        public_repos=user.get("public_repos", 0) or 0,
        followers=user.get("followers", 0) or 0,
        following=user.get("following", 0) or 0,
        analyzed_repos=len(summaries),
        total_stars=sum(s.stars for s in summaries),
        total_forks=sum(s.forks for s in summaries),
        languages=dict(languages.most_common()),
        top_repos=top,
    )
