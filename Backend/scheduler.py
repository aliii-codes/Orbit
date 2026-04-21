import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import schedule

from Backend.config import load_config
from Backend.github_fetcher import fetch_repo_data
from Backend.hf_fetcher import fetch_hf_data
from Backend.reddit_fetcher import fetch_reddit_data
from Backend.devto_fetcher import fetch_devto_data
from Backend.gh_trending_fetcher import fetch_gh_trending
from Backend.digest_generator import generate_digest
from Backend.emailer import send_digest

logger = logging.getLogger(__name__)


def run_digest() -> dict[str, bool] | None:
    """Fetch all sources in parallel, generate digest, and send.

    Returns per-channel send results, or None on failure.
    """
    logger.info("Running Orbit digest agent...")

    config = load_config()
    email = config.get("email", "")
    if not email:
        logger.error("No email found in config")
        return None

    source_states = config.get("source_states", {
        "hf": True, "reddit": True, "devto": True, "trending": True,
    })

    # Fetch all sources in parallel
    fetch_results: dict[str, object] = {}

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(fetch_repo_data): "github",
        }
        if source_states.get("hf", True):
            futures[executor.submit(fetch_hf_data)] = "hf"
        if source_states.get("reddit", True):
            futures[executor.submit(fetch_reddit_data)] = "reddit"
        if source_states.get("devto", True):
            futures[executor.submit(fetch_devto_data)] = "devto"
        if source_states.get("trending", True):
            futures[executor.submit(fetch_gh_trending)] = "trending"

        for future in as_completed(futures):
            key = futures[future]
            try:
                fetch_results[key] = future.result()
            except Exception as e:
                logger.error("Failed to fetch %s: %s", key, e)
                fetch_results[key] = None

    digest = generate_digest(
        digest_data=fetch_results.get("github"),
        hf_data=fetch_results.get("hf"),
        reddit_data=fetch_results.get("reddit"),
        devto_data=fetch_results.get("devto"),
        gh_trending=fetch_results.get("trending"),
    )

    results = send_digest(email, digest)
    logger.info("Digest sent. Results: %s", results)
    return results


def start_scheduler() -> None:
    """Start the scheduler loop (runs in a background thread)."""
    config = load_config()
    schedule_time = config.get("schedule_time", "08:00")

    schedule.every().day.at(schedule_time).do(run_digest)
    logger.info("Scheduler started — digest will run at %s daily", schedule_time)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    run_digest()
