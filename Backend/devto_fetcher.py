import requests

DEVTO_API = "https://dev.to/api/articles"
TAGS = ["python", "ai", "machinelearning"]

def fetch_devto_data():
    articles = []
    for tag in TAGS:
        try:
            res = requests.get(DEVTO_API, params={
                "tag": tag,
                "top": 1,
                "per_page": 2
            }, timeout=10)
            if res.status_code == 200:
                for a in res.json():
                    articles.append({
                        "title": a["title"],
                        "url": a["url"],
                        "author": a["user"]["name"],
                        "reactions": a["positive_reactions_count"],
                        "tag": tag
                    })
        except Exception as e:
            print(f"Dev.to error [{tag}]: {e}")
    return articles

if __name__ == "__main__":
    articles = fetch_devto_data()
    for a in articles:
        print(f"[{a['tag']}] {a['title']} by {a['author']}")