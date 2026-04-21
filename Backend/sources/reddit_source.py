from Backend.sources.base import SourcePlugin
from Backend.reddit_fetcher import fetch_reddit_data


class RedditSource(SourcePlugin):
    @property
    def name(self) -> str:
        return "Reddit"

    @property
    def key(self) -> str:
        return "reddit"

    def fetch(self) -> list[dict]:
        return fetch_reddit_data()

    def format_raw(self, data: object) -> str:
        if not data:
            return ""
        raw = "\n=== REDDIT HOT POSTS ===\n"
        for p in data:
            raw += f"  - [r/{p['subreddit']}] {p['title']} | ⬆ {p['upvotes']} | {p['url']}\n"
        return raw
