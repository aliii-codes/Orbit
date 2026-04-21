from Backend.sources.base import SourcePlugin
from Backend.hf_fetcher import fetch_hf_data


class HuggingFaceSource(SourcePlugin):
    @property
    def name(self) -> str:
        return "HuggingFace"

    @property
    def key(self) -> str:
        return "hf"

    def fetch(self) -> dict[str, list[dict]]:
        return fetch_hf_data()

    def format_raw(self, data: object) -> str:
        if not data:
            return ""
        raw = "\n=== HUGGINGFACE TRENDING ===\n"
        raw += "Papers:\n"
        for p in data.get("papers", []):
            raw += f"  - {p['title']} | {p['url']}\n"
        raw += "Trending Models:\n"
        for m in data.get("models", []):
            raw += f"  - {m['id']} | ⬇ {m['downloads']} | ♥ {m['likes']} | {m['url']}\n"
        return raw
