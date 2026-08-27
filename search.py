import time
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from ddgs import DDGS

BLOCKED_DOMAINS = [
    "bing.com/aclick",
    "googleadservices.com",
    "doubleclick.net",
    "amazon.com/s?",
    "pinterest.com",
    "facebook.com",
    "instagram.com",
    "quora.com",
]

def is_junk_url(url: str) -> bool:
    url_lower = url.lower()
    return any(blocked in url_lower for blocked in BLOCKED_DOMAINS)

def get_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return url

def fetch_page_text(url: str, max_chars: int = 8000) -> str:
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=8,
        )
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = " ".join(soup.get_text(separator=" ").split())
        return text[:max_chars]
    except Exception:
        return ""

def search_web(query: str, max_results: int = 5, max_per_domain: int = 2) -> list[dict]:
    """
    Searches the web, filters junk, and enforces domain diversity so
    results aren't dominated by a single website.
    """
    parsed = []
    raw_results = []
    domain_counts = {}

    for attempt in range(3):
        try:
            with DDGS() as ddgs:
                raw_results = list(ddgs.text(query, max_results=max_results + 8, backend="html"))
            if raw_results:
                break
        except Exception:
            time.sleep(2)

    for r in raw_results:
        url = r.get("href", "")

        if not url or is_junk_url(url):
            continue

        domain = get_domain(url)
        if domain_counts.get(domain, 0) >= max_per_domain:
            continue

        snippet = r.get("body", "")
        full_text = fetch_page_text(url)

        parsed.append({
            "title": r.get("title", ""),
            "url": url,
            "content": full_text if full_text else snippet,
        })

        domain_counts[domain] = domain_counts.get(domain, 0) + 1

        if len(parsed) >= max_results:
            break

    return parsed