import logging

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from Backend.config import load_config

logger = logging.getLogger(__name__)

DEVTO_API = "https://dev.to/api/articles"


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def _fetch_tag(tag: str, per_page: int = 2) -> list[dict]:
    """Fetch top Dev.to articles for a single tag."""
    res = requests.get(DEVTO_API, params={"tag": tag, "top": 1, "per_page": per_page}, timeout=10)
    res.raise_for_status()
    return [
        {
            "title": a["title"],
            "url": a["url"],
            "author": a["user"]["name"],
            "reactions": a["positive_reactions_count"],
            "tag": tag,
        }
        for a in res.json()
    ]


def fetch_devto_data(tags: list[str] | None = None) -> list[dict]:
    """Fetch top Dev.to articles for configured tags."""
    if tags is None:
        config = load_config()
        tags = config.get("devto_tags", ["python", "ai", "machinelearning"])

    articles: list[dict] = []
    for tag in tags:
        try:
            articles.extend(_fetch_tag(tag))
        except Exception as e:
            logger.error("Dev.to error [%s]: %s", tag, e)
    return articles


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    articles = fetch_devto_data()
    for a in articles:
        print(f"[{a['tag']}] {a['title']} by {a['author']}")
