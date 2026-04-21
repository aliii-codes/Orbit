from Backend.sources.base import SourcePlugin
from Backend.github_fetcher import fetch_repo_data


class GitHubSource(SourcePlugin):
    @property
    def name(self) -> str:
        return "GitHub"

    @property
    def key(self) -> str:
        return "github"

    def fetch(self) -> list[dict]:
        return fetch_repo_data()

    def format_raw(self, data: object) -> str:
        if not data:
            return ""
        raw = "=== GITHUB REPO ACTIVITY ===\n"
        for repo in data:
            raw += f"\nRepo: {repo['repo']} ({repo['url']})\n"
            raw += f"  Commits ({len(repo['commits'])}):\n"
            for c in repo['commits']:
                raw += f"    - [{c['sha']}] {c['message']} by {c['author']} at {c['date']}\n"
            raw += f"  Open Issues ({len(repo['issues'])}):\n"
            for i in repo['issues']:
                raw += f"    - {i['title']} | {i['url']}\n"
            raw += f"  Pull Requests ({len(repo['pulls'])}):\n"
            for p in repo['pulls']:
                raw += f"    - {p['title']} | {p['url']}\n"
        return raw
