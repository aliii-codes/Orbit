import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)
ASSISTANT_NAME = "Orbit"

def generate_digest(digest_data: list, hf_data=None, reddit_data=None, devto_data=None, gh_trending=None) -> str | None:
    if not digest_data and not hf_data and not reddit_data and not devto_data and not gh_trending:
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
        raw += "\n=== GITHUB TRENDING (Python) ===\n"
        for r in gh_trending:
            raw += f"  - {r['name']} ⭐ {r['stars']} — {r['description']} | {r['url']}\n"

    prompt = f"""
You are a developer assistant called {ASSISTANT_NAME}. Below is aggregated data from multiple sources.
Write a clean, concise daily digest for a developer. Be professional but friendly.
Sections to include (only if data exists): GitHub Activity, HuggingFace Trending, Reddit Highlights, Dev.to Articles, GitHub Trending.
Keep it skimmable. Use short bullet points.

Raw Data:
{raw}

Write the digest now:
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message.content