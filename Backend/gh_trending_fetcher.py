import logging

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from Backend.config import load_config

logger = logging.getLogger(__name__)

GH_TRENDING_BASE_URL = "https://github.com/trending"


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def _fetch_language_trending(language: str, since: str = "daily") -> list[dict]:
    """Fetch trending repos for a single language."""
    url = f"{GH_TRENDING_BASE_URL}/{language}?since={since}"
    res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    articles = soup.select("article.Box-row")[:5]
    repos: list[dict] = []

    for article in articles:
        name_tag = article.select_one("h2 a")
        desc_tag = article.select_one("p")
        stars_tag = article.select_one("a[href$='/stargazers']")
        if name_tag:
            full_name = name_tag.get("href", "").strip("/")
            repos.append({
                "name": full_name,
                "url": f"https://github.com/{full_name}",
                "description": desc_tag.text.strip() if desc_tag else "No description",
                "stars": stars_tag.text.strip() if stars_tag else "?",
                "language": language,
            })

    return repos


def fetch_gh_trending(languages: list[str] | None = None) -> list[dict]:
    """Fetch trending repos for configured languages."""
    if languages is None:
        config = load_config()
        languages = config.get("trending_languages", ["python"])

    repos: list[dict] = []
    for lang in languages:
        try:
            repos.extend(_fetch_language_trending(lang))
        except Exception as e:
            logger.error("GitHub Trending error [%s]: %s", lang, e)
    return repos


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    repos = fetch_gh_trending()
    for r in repos:
        print(f"{r['name']} ⭐ {r['stars']} — {r['url']}")
