import unittest

from github_analyzer.analyzer import analyze_profile, summarize_repo
from github_analyzer.main import format_report

USER = {
    "login": "octo",
    "name": "Octo Cat",
    "bio": None,
    "created_at": "2020-01-02T03:04:05Z",
    "public_repos": 4,
    "followers": 3,
    "following": 1,
}


def repo(name, stars=0, forks=0, language=None, fork=False):
    return {
        "name": name,
        "stargazers_count": stars,
        "forks_count": forks,
        "language": language,
        "created_at": "2021-01-01T00:00:00Z",
        "fork": fork,
    }


REPOS = [
    repo("a", stars=5, forks=1, language="Python"),
    repo("b", stars=2, forks=0, language="Python"),
    repo("c", stars=1, forks=4, language="HTML"),
    repo("upstream", stars=1000, forks=500, language="Go", fork=True),
]


class AnalyzerTests(unittest.TestCase):
    def test_summarize_repo_handles_missing_fields(self):
        summary = summarize_repo({"name": "x"})
        self.assertEqual((summary.stars, summary.forks, summary.language), (0, 0, None))

    def test_totals_ignore_forks_by_default(self):
        report = analyze_profile(USER, REPOS)
        self.assertEqual(report.analyzed_repos, 3)
        self.assertEqual(report.total_stars, 8)
        self.assertEqual(report.total_forks, 5)

    def test_include_forks(self):
        report = analyze_profile(USER, REPOS, include_forks=True)
        self.assertEqual(report.analyzed_repos, 4)
        self.assertEqual(report.total_stars, 1008)

    def test_languages_sorted_by_usage(self):
        report = analyze_profile(USER, REPOS)
        self.assertEqual(report.languages, {"Python": 2, "HTML": 1})
        self.assertEqual(report.main_language, "Python")

    def test_top_repos_sorted_and_limited(self):
        report = analyze_profile(USER, REPOS, top_n=2)
        self.assertEqual([r.name for r in report.top_repos], ["a", "b"])

    def test_empty_repositories(self):
        report = analyze_profile(USER, [])
        self.assertEqual(report.analyzed_repos, 0)
        self.assertIsNone(report.main_language)

    def test_format_report_contains_key_information(self):
        text = format_report(analyze_profile(USER, REPOS))
        self.assertIn("octo", text)
        self.assertIn("Python", text)
        self.assertIn("Total stars:   8", text)


if __name__ == "__main__":
    unittest.main()
