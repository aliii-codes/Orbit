import logging

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from Backend.config import load_config

logger = logging.getLogger(__name__)

HF_PAPERS_API = "https://huggingface.co/api/daily_papers"
HF_MODELS_API = "https://huggingface.co/api/models"


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def _fetch_papers() -> list[dict]:
    """Fetch trending HuggingFace papers."""
    res = requests.get(HF_PAPERS_API, timeout=10)
    res.raise_for_status()
    papers = res.json()[:5]
    return [
        {
            "title": p.get("paper", {}).get("title", "Unknown"),
            "url": f"https://huggingface.co/papers/{p.get('paper', {}).get('id', '')}",
            "upvotes": p.get("numComments", 0),
        }
        for p in papers
    ]


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def _fetch_models() -> list[dict]:
    """Fetch trending HuggingFace models."""
    res = requests.get(HF_MODELS_API, params={"sort": "trending", "limit": 5}, timeout=10)
    res.raise_for_status()
    return [
        {
            "id": m.get("id", ""),
            "url": f"https://huggingface.co/{m.get('id', '')}",
            "downloads": m.get("downloads", 0),
            "likes": m.get("likes", 0),
        }
        for m in res.json()
    ]


def fetch_hf_data() -> dict[str, list[dict]]:
    """Fetch HuggingFace trending papers and models."""
    data: dict[str, list[dict]] = {"papers": [], "models": []}

    try:
        data["papers"] = _fetch_papers()
    except Exception as e:
        logger.error("HF Papers error: %s", e)

    try:
        data["models"] = _fetch_models()
    except Exception as e:
        logger.error("HF Models error: %s", e)

    return data


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    d = fetch_hf_data()
    print("Papers:", len(d["papers"]))
    print("Models:", len(d["models"]))
