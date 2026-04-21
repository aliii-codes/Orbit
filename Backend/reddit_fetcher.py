import logging

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from Backend.config import load_config

logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": "Orbit/1.0 (digest agent by aliii-codes)"}


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def _fetch_subreddit(sub: str, limit: int = 3) -> list[dict]:
    """Fetch hot posts from a single subreddit."""
    url = f"https://www.reddit.com/r/{sub}/hot.json?limit={limit}"
    res = requests.get(url, headers=HEADERS, timeout=10)
    res.raise_for_status()
    items = res.json()["data"]["children"]
    return [
        {
            "subreddit": sub,
            "title": p["data"]["title"],
            "url": f"https://reddit.com{p['data']['permalink']}",
            "upvotes": p["data"]["ups"],
            "comments": p["data"]["num_comments"],
        }
        for p in items
    ]


def fetch_reddit_data(subreddits: list[str] | None = None) -> list[dict]:
    """Fetch hot posts from configured subreddits."""
    if subreddits is None:
        config = load_config()
        subreddits = config.get("subreddits") or ["MachineLearning", "artificial", "learnpython"]

    posts: list[dict] = []
    for sub in subreddits:
        try:
            posts.extend(_fetch_subreddit(sub))
        except Exception as e:
            logger.error("Reddit error r/%s: %s", sub, e)
    return posts


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    posts = fetch_reddit_data()
    for p in posts:
        print(f"[r/{p['subreddit']}] {p['title']}")
