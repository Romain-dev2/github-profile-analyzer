"""Command-line interface: python -m github_analyzer.main <username>."""

from __future__ import annotations

import argparse
import sys

from .analyzer import ProfileReport, analyze_profile
from .api import GitHubClient, GitHubError

BAR_WIDTH = 20


def format_report(report: ProfileReport) -> str:
    """Render a ProfileReport as human-readable text."""
    lines = [
        f"GitHub Profile Analyzer - {report.username}",
        "=" * 40,
        f"Name:          {report.name or '-'}",
        f"Bio:           {report.bio or '-'}",
        f"Member since:  {report.created_at[:10] or '-'}",
        f"Followers:     {report.followers}",
        f"Following:     {report.following}",
        f"Public repos:  {report.public_repos} ({report.analyzed_repos} analyzed)",
        f"Total stars:   {report.total_stars}",
        f"Total forks:   {report.total_forks}",
    ]

    if report.languages:
        lines += ["", "Languages (by repository count):"]
        total = sum(report.languages.values())
        for language, count in report.languages.items():
            share = count / total
            bar = "#" * max(1, round(share * BAR_WIDTH))
            lines.append(f"  {language:<15} {bar:<{BAR_WIDTH}} {share:5.1%} ({count})")

    if report.top_repos:
        lines += ["", "Top repositories:"]
        for repo in report.top_repos:
            lines.append(
                f"  {repo.name:<30} * {repo.stars:<4} forks {repo.forks:<4} "
                f"{repo.language or '-'}"
            )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="github_analyzer",
        description="Analyze a GitHub profile using the GitHub REST API.",
    )
    parser.add_argument("username", help="GitHub username to analyze")
    parser.add_argument(
        "--top", type=int, default=5, help="number of top repositories to show (default: 5)"
    )
    parser.add_argument(
        "--include-forks", action="store_true", help="include forked repositories in the stats"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    client = GitHubClient()  # reads GITHUB_TOKEN from the environment if set
    try:
        user = client.get_user(args.username)
        repos = client.get_repos(args.username)
    except GitHubError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    report = analyze_profile(user, repos, top_n=args.top, include_forks=args.include_forks)
    print(format_report(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
