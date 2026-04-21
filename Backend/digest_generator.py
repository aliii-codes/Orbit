import logging
import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

ASSISTANT_NAME = "Orbit"


@lru_cache(maxsize=1)
def _get_llm_client():
    """Lazily create the LLM client based on config."""
    from Backend.config import load_config

    config = load_config()
    provider = config.get("llm_provider", "groq")
    model = config.get("llm_model", "llama-3.3-70b-versatile")

    if provider == "groq":
        from groq import Groq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set. Please add it to your .env file.")
        return {"client": Groq(api_key=api_key), "provider": "groq", "model": model}

    # Use litellm for any other provider (openai, anthropic, ollama, etc.)
    import litellm
    return {"client": litellm, "provider": provider, "model": model}


def _call_llm(prompt: str, temperature: float = 0.5) -> str:
    """Call the configured LLM provider and return the response text."""
    llm = _get_llm_client()
    provider = llm["provider"]
    model = llm["model"]

    if provider == "groq":
        response = llm["client"].chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return response.choices[0].message.content

    # litellm handles all other providers
    import litellm
    response = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return response.choices[0].message.content


def generate_digest(
    digest_data: list[dict] | None = None,
    hf_data: dict[str, list[dict]] | None = None,
    reddit_data: list[dict] | None = None,
    devto_data: list[dict] | None = None,
    gh_trending: list[dict] | None = None,
) -> str:
    """Generate an AI-summarized digest from aggregated source data."""
    if not any([digest_data, hf_data, reddit_data, devto_data, gh_trending]):
        return "No activity found in the last 24 hours."

    raw = ""

    # GitHub repos
    if digest_data:
        raw += "=== GITHUB REPO ACTIVITY ===\n"
        for repo in digest_data:
            raw += f"\nRepo: {repo['repo']} ({repo['url']})\n"
            raw += f"  Commits ({len(repo['commits'])}):\n"
            for c in repo['commits']:
                raw += f"    - [{c['sha']}] {c['message']} by {c['author']} at {c['date']}\n"
            raw += f"  Open Issues ({len(repo['issues'])}):\n"
            for i in repo['issues']:
                raw += f"    - {i['title']} | {i['url']}\n"
            raw += f"  Pull Requests ({len(repo['pulls'])}):\n"
            for p in repo['pulls']:
                raw += f"    - {p['title']} | {p['url']}\n"

    # HuggingFace
    if hf_data:
        raw += "\n=== HUGGINGFACE TRENDING ===\n"
        raw += "Papers:\n"
        for p in hf_data.get("papers", []):
            raw += f"  - {p['title']} | {p['url']}\n"
        raw += "Trending Models:\n"
        for m in hf_data.get("models", []):
            raw += f"  - {m['id']} | ⬇ {m['downloads']} | ♥ {m['likes']} | {m['url']}\n"

    # Reddit
    if reddit_data:
        raw += "\n=== REDDIT HOT POSTS ===\n"
        for p in reddit_data:
            raw += f"  - [r/{p['subreddit']}] {p['title']} | ⬆ {p['upvotes']} | {p['url']}\n"

    # Dev.to
    if devto_data:
        raw += "\n=== DEV.TO ARTICLES ===\n"
        for a in devto_data:
            raw += f"  - [{a['tag']}] {a['title']} by {a['author']} | ♥ {a['reactions']} | {a['url']}\n"

    # GitHub Trending
    if gh_trending:
        raw += "\n=== GITHUB TRENDING ===\n"
        for r in gh_trending:
            lang_label = f" [{r['language']}]" if 'language' in r else ""
            raw += f"  - {r['name']} ⭐ {r['stars']}{lang_label} — {r['description']} | {r['url']}\n"

    prompt = f"""
You are a developer assistant called {ASSISTANT_NAME}. Below is aggregated data from multiple sources.
Write a clean, concise daily digest for a developer. Be professional but friendly.
Sections to include (only if data exists): GitHub Activity, HuggingFace Trending, Reddit Highlights, Dev.to Articles, GitHub Trending.
Keep it skimmable. Use short bullet points. Use Markdown formatting (headers, bold, bullets).

Raw Data:
{raw}

Write the digest now along with the links:
"""

    try:
        return _call_llm(prompt)
    except Exception as e:
        logger.error("LLM generation failed: %s", e)
        return f"Digest generation failed: {e}\n\nRaw data:\n{raw}"


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    result = generate_digest(
        digest_data=[{"repo": "test/repo", "url": "https://github.com/test/repo",
                       "commits": [], "issues": [], "pulls": []}]
    )
    print(result)
