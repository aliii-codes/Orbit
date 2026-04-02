import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)
ASSISTANT_NAME = "Orbit"

def generate_digest(digest_data: list) -> str:
    if not digest_data:
        return "No activity found in the last 24 hours."

    
    raw = ""
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

    prompt = f"""
You are a developer assistant {ASSISTANT_NAME}. Below is raw GitHub activity data from the last 24 hours.
Write a clean, concise daily digest summary for a developer.
Be professional but friendly. Highlight key commits, issues, and PRs.
Group by repo.

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


if __name__ == "__main__":
    # Test with dummy data
    dummy = [
        {
            "repo": "aliii-codes/groq-coding-agent",
            "url": "https://github.com/aliii-codes/groq-coding-agent",
            "commits": [
                {"sha": "a1b2c3d", "message": "Add agentic loop", "author": "Ali", "date": "2025-03-30 07:00"}
            ],
            "issues": [],
            "pulls": []
        }
    ]
    print(generate_digest(dummy))