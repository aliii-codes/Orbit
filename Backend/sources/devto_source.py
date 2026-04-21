from Backend.sources.base import SourcePlugin
from Backend.devto_fetcher import fetch_devto_data


class DevToSource(SourcePlugin):
    @property
    def name(self) -> str:
        return "Dev.to"

    @property
    def key(self) -> str:
        return "devto"

    def fetch(self) -> list[dict]:
        return fetch_devto_data()

    def format_raw(self, data: object) -> str:
        if not data:
            return ""
        raw = "\n=== DEV.TO ARTICLES ===\n"
        for a in data:
            raw += f"  - [{a['tag']}] {a['title']} by {a['author']} | ♥ {a['reactions']} | {a['url']}\n"
        return raw
