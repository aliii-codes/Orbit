import logging
import time
from datetime import datetime, timedelta, timezone
from functools import lru_cache

from dotenv import load_dotenv
from github import Github, Auth
from tenacity import retry, stop_after_attempt, wait_exponential

from Backend.config import load_config

load_dotenv()

logger = logging.getLogger(__name__)

GITHUB_TOKEN: str | None = None


def _get_github_token() -> str | None:
    """Lazily resolve GitHub token."""
    global GITHUB_TOKEN
    if GITHUB_TOKEN is None:
        import os
        GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    return GITHUB_TOKEN


@lru_cache(maxsize=1)
def _get_github_client() -> Github:
    """Create a PyGithub client (cached)."""
    token = _get_github_token()
    if not token:
        raise ValueError("GITHUB_TOKEN is not set. Please add it to your .env file.")
    auth = Auth.Token(token)
    return Github(auth=auth)


def _check_rate_limit(g: Github) -> None:
    """Log a warning if GitHub API rate limit is low."""
    try:
        remaining = g.get_rate_limit().core.remaining
        if remaining < 10:
            logger.warning("GitHub API rate limit low: %d remaining", remaining)
        if remaining <= 0:
            reset_time = g.get_rate_limit().core.reset
            wait_seconds = (reset_time - datetime.now(timezone.utc)).total_seconds()
            if wait_seconds > 0:
                logger.warning("Rate limit exceeded. Waiting %.0f seconds.", wait_seconds)
                time.sleep(wait_seconds + 1)
    except Exception as e:
        logger.debug("Could not check rate limit: %s", e)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def fetch_repo_data() -> list[dict]:
    """Fetch commits, issues, and PRs for all monitored repos (last 24h)."""
    g = _get_github_client()
    _check_rate_limit(g)

    config = load_config()
    repos = config.get("repos", [])

    since = datetime.now(timezone.utc) - timedelta(days=1)
    digest_data: list[dict] = []

    for repo_info in repos:
        owner = repo_info["owner"]
        name = repo_info["name"]
        full_name = f"{owner}/{name}"

        try:
            repo = g.get_repo(full_name)

            commits = [
                {
                    "sha": c.sha[:7],
                    "message": c.commit.message.split("\n")[0],
                    "author": c.commit.author.name,
                    "date": c.commit.author.date.strftime("%Y-%m-%d %H:%M"),
                }
                for c in repo.get_commits(since=since)
            ]

            issues = [
                {
                    "title": i.title,
                    "state": i.state,
                    "url": i.html_url,
                    "created_at": i.created_at.strftime("%Y-%m-%d %H:%M"),
                }
                for i in repo.get_issues(state="open", since=since)
            ]

            pulls = [
                {
                    "title": p.title,
                    "state": p.state,
                    "url": p.html_url,
                    "created_at": p.created_at.strftime("%Y-%m-%d %H:%M"),
                }
                for p in repo.get_pulls(state="open", sort="created", direction="desc")
                if p.created_at >= since
            ]

            digest_data.append({
                "repo": full_name,
                "url": repo_info["url"],
                "commits": commits,
                "issues": issues,
                "pulls": pulls,
            })

            # Small delay between repos to be kind to rate limits
            time.sleep(0.5)

        except Exception as e:
            logger.error("Failed to fetch %s: %s", full_name, e)

    return digest_data


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    data = fetch_repo_data()
    for repo in data:
        print(f"\n {repo['repo']}")
        print(f"Commits: {len(repo['commits'])}")
        print(f"Issues: {len(repo['issues'])}")
        print(f"PRs: {len(repo['pulls'])}")
