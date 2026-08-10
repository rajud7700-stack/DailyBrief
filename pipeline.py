import os
import json
import requests
from fetcher import fetch_latest_feed_entries
from summarizer import summarize_article

SEEN_DB_FILE = "seen_articles.json"

def load_seen_ids() -> set:
    if os.path.exists(SEEN_DB_FILE):
        with open(SEEN_DB_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen_id(guid: str):
    seen = load_seen_ids()
    seen.add(guid)
    with open(SEEN_DB_FILE, "w") as f:
        json.dump(list(seen), f)

def publish_to_dailybrief(brief_data: dict, source_url: str):
    endpoint = os.getenv("DAILYBRIEF_ENDPOINT", "https://api.yourdailybrief.com/v1/articles")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('DAILYBRIEF_API_KEY')}"
    }

    payload = {
        "title": brief_data["title"],
        "category": brief_data["category"],
        "summary": brief_data["summary"],
        "keypoints": brief_data["keypoints"],
        "status": "Published",
        "source_url": source_url
    }

    print(f"Publishing Brief: {brief_data['title']}")
    print(f"Payload Preview:\n{json.dumps(payload, indent=2)}")

def run_pipeline():
    rss_sources = [
        "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
    ]

    seen_ids = load_seen_ids()

    for url in rss_sources:
        entries = fetch_latest_feed_entries(url, limit=2)
        for entry in entries:
            if entry["guid"] in seen_ids:
                print(f"Skipping already processed story: {entry['title']}")
                continue

            print(f"\nProcessing story: {entry['title']}")
            try:
                brief = summarize_article(entry["title"], entry["clean_text"])
                publish_to_dailybrief(brief.model_dump(), entry["link"])
                save_seen_id(entry["guid"])
            except Exception as e:
                print(f"Error processing '{entry['title']}': {e}")

if __name__ == "__main__":
    run_pipeline()