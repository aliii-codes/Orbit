import json
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from github import Github, Auth


load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "Frontend", "data", "config.json")

if os.path.exists(CONFIG_PATH):
    print("Path exists")
else:
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump({"email": "", "repos": []}, f, indent=4)
    print("Config created")

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)
    
def fetch_repo_data():
    auth = Auth.Token(GITHUB_TOKEN)

    g = Github(auth=auth)
    config = load_config()
    repos = config.get("repos", [])

    since = datetime.now(timezone.utc) - timedelta(days=1)
    digest_data = []  # empty list to save the data temporarly

    for repo_info in repos:
        owner = repo_info["owner"]
        name = repo_info["name"]

        try:
            repo = g.get_repo(f"{owner}/{name}")

            commits = [
                {
                    "sha": c.sha[:7],
                    "message": c.commit.message.split("\n")[0],
                    "author": c.commit.author.name,
                    "date": c.commit.author.date.strftime("%Y-%m-%d %H:%M")
                }
                for c in repo.get_commits(since=since)
            ]

            issues = [
                {
                    "title" :i.title,
                    "state" : i.state,
                    "url" : i.html_url,
                    "created_at" : i.created_at.strftime("%Y-%m-%d %H:%M")
                }
                for i in repo.get_issues(state="open", since=since)
            ]

            pulls = [
                {
                    "title": p.title,
                    "state": p.state,
                    "url": p.html_url,
                    "created_at": p.created_at.strftime("%Y-%m-%d %H:%M")
                }
                for p in repo.get_pulls(state="open", sort="created", direction="desc")
                if p.created_at >= since
            ]

            digest_data.append({
                "repo": f"{owner}/{name}",
                "url": repo_info["url"],
                "commits": commits,
                "issues": issues,
                "pulls": pulls
            })

        except Exception as e:
            print(f"Error: Failed to fetch {owner}/{name}: {e}")
    return digest_data

if __name__ == "__main__":
    data = fetch_repo_data()

    for repo in data:
        print(f"\n {repo['repo']}")
        print(f"Commits: {len(repo['commits'])}")
        print(f"Issues: {len(repo['issues'])}")
        print(f"PRs: {len(repo['pulls'])}")