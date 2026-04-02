import requests

SUBREDDITS = ["MachineLearning", "artificial", "learnpython"]
HEADERS = {"User-Agent": "Orbit/1.0 (digest agent by aliii-codes)"}

def fetch_reddit_data():
    posts = []
    for sub in SUBREDDITS:
        try:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit=3"
            res = requests.get(url, headers=HEADERS, timeout=10)
            if res.status_code == 200:
                items = res.json()["data"]["children"]
                for item in items:
                    p = item["data"]
                    posts.append({
                        "subreddit": sub,
                        "title": p["title"],
                        "url": f"https://reddit.com{p['permalink']}",
                        "upvotes": p["ups"],
                        "comments": p["num_comments"]
                    })
        except Exception as e:
            print(f"Reddit error r/{sub}: {e}")
    return posts

if __name__ == "__main__":
    posts = fetch_reddit_data()
    for p in posts:
        print(f"[r/{p['subreddit']}] {p['title']}")