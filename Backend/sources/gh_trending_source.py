from Backend.sources.base import SourcePlugin
from Backend.gh_trending_fetcher import fetch_gh_trending


class GHTrendingSource(SourcePlugin):
    @property
    def name(self) -> str:
        return "GitHub Trending"

    @property
    def key(self) -> str:
        return "trending"

    def fetch(self) -> list[dict]:
        return fetch_gh_trending()

    def format_raw(self, data: object) -> str:
        if not data:
            return ""
        raw = "\n=== GITHUB TRENDING ===\n"
        for r in data:
            lang_label = f" [{r['language']}]" if 'language' in r else ""
            raw += f"  - {r['name']} ⭐ {r['stars']}{lang_label} — {r['description']} | {r['url']}\n"
        return raw
