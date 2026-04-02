import requests

HF_PAPERS_API = "https://huggingface.co/api/daily_papers"
HF_MODELS_API = "https://huggingface.co/api/models"

def fetch_hf_data():
    data = {"papers": [], "models": []}

    try:
        res = requests.get(HF_PAPERS_API, timeout=10)
        if res.status_code == 200:
            papers = res.json()[:5]
            for p in papers:
                data["papers"].append({
                    "title": p.get("paper", {}).get("title", "Unknown"),
                    "url": f"https://huggingface.co/papers/{p.get('paper', {}).get('id', '')}",
                    "upvotes": p.get("numComments", 0)
                })
    except Exception as e:
        print(f"HF Papers error: {e}")

    try:
        res = requests.get(HF_MODELS_API, params={
            "sort": "trending",
            "limit": 5
        }, timeout=10)
        if res.status_code == 200:
            for m in res.json():
                data["models"].append({
                    "id": m.get("id", ""),
                    "url": f"https://huggingface.co/{m.get('id', '')}",
                    "downloads": m.get("downloads", 0),
                    "likes": m.get("likes", 0)
                })
    except Exception as e:
        print(f"HF Models error: {e}")

    return data

if __name__ == "__main__":
    d = fetch_hf_data()
    print("Papers:", len(d["papers"]))
    print("Models:", len(d["models"]))