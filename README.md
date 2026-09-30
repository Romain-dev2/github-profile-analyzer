# GitHub Profile Analyzer

A Python command-line application that analyzes GitHub profiles using the
[GitHub REST API](https://docs.github.com/en/rest).

Give it a username and it fetches the profile and public repositories, then
prints statistics: followers, stars, forks, language breakdown and top repositories.

## Features

- Retrieve public GitHub user information
- List and analyze public repositories (pagination handled)
- Language breakdown (by number of repositories)
- Total stars and forks, top repositories
- Forks excluded from statistics by default (`--include-forks` to include them)
- Clear handling of unknown users, rate limits and network errors
- Works without a token; optional `GITHUB_TOKEN` for a higher rate limit

## GitHub Integration

This project integrates with GitHub through the official GitHub REST API
(`https://api.github.com`). It uses these endpoints:

- `GET /users/{username}`
- `GET /users/{username}/repos`

All requests are real calls to the GitHub API; nothing is simulated.

## Technologies

- Python 3.9+
- GitHub REST API
- [Requests](https://requests.readthedocs.io/)
- unittest / pytest

## Installation

```bash
git clone https://github.com/Romain-dev2/github-profile-analyzer.git
cd github-profile-analyzer
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

## Usage

```bash
python -m github_analyzer.main Romain-dev2
# or, after `pip install -e .`
github-analyzer Romain-dev2 --top 3
```

Options:

| Option            | Description                                    |
|-------------------|------------------------------------------------|
| `--top N`         | Number of top repositories to show (default 5) |
| `--include-forks` | Include forked repositories in the statistics  |

### Example output

```text
GitHub Profile Analyzer - Romain-dev2
========================================
Name:          Romain
Member since:  2025-03-24
Public repos:  7 (7 analyzed)
Total stars:   0

Languages (by repository count):
  Python          ##########           50.0% (3)
  CSS             ###                  16.7% (1)
  Java            ###                  16.7% (1)
  HTML            ###                  16.7% (1)
```

## Optional token configuration

Without authentication, GitHub allows 60 requests per hour per IP address.
To raise the limit, create a
[personal access token](https://github.com/settings/tokens) (no scopes needed
for public data) and expose it as an environment variable:

```bash
export GITHUB_TOKEN="your_token_here"        # Windows PowerShell: $env:GITHUB_TOKEN="..."
```

The token is never stored in the code or the repository.

## Tests

```bash
pip install pytest
pytest
# or, with unittest (after `pip install -e .`)
python -m unittest discover -s tests -v
```

The tests replace the HTTP layer with a fake session so they run offline.

## Project structure

```
src/github_analyzer/
  api.py        GitHub REST API client (errors, pagination, optional token)
  analyzer.py   Analysis logic (stars, forks, languages)
  main.py       Command-line interface
tests/
```

## Support

For questions or issues, please open an issue on this repository or contact:
romain.messager49@gmail.com

## License

MIT
