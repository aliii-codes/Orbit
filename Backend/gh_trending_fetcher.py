import requests
from bs4 import BeautifulSoup

GH_TRENDING_URL = "https://github.com/trending/python?since=daily"

def fetch_gh_trending():
    repos = []
    try:
        res = requests.get(GH_TRENDING_URL, timeout=10, headers={
            "User-Agent": "Mozilla/5.0"
        })
        soup = BeautifulSoup(res.text, "html.parser")
        articles = soup.select("article.Box-row")[:5]
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
                    "stars": stars_tag.text.strip() if stars_tag else "?"
                })
    except Exception as e:  
        print(f"GitHub Trending error: {e}")
    return repos

if __name__ == "__main__":
    repos = fetch_gh_trending()
    for r in repos:
        print(f"{r['name']} ⭐ {r['stars']} — {r['url']}")