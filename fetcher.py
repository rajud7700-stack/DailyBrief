import feedparser
from bs4 import BeautifulSoup

def clean_html(raw_html: str) -> str:
    """Strips HTML tags to provide clean text to the LLM."""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def fetch_latest_feed_entries(rss_url: str, limit: int = 5) -> list[dict]:
    """Fetches and cleans top entries from an RSS feed."""
    feed = feedparser.parse(rss_url)
    parsed_entries = []

    for entry in feed.entries[:limit]:
        raw_content = entry.get("content", [{}])[0].get("value") or entry.get("summary", "")
        parsed_entries.append({
            "guid": entry.get("id", entry.get("link")),
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
            "clean_text": clean_html(raw_content)
        })

    return parsed_entries