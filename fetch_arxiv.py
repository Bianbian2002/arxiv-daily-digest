"""Fetch the latest math.OC papers from arXiv.

Uses the RSS feed (which updates same-day) to discover paper IDs, then
batch-queries the arXiv API for full metadata (abstracts, categories).
The API alone has a multi-day indexing delay, so relying on it for discovery
misses the current day's listing.
"""
import argparse
import json
import re
import sys
import time

import feedparser
import requests

RSS_URL = "https://rss.arxiv.org/rss/math.OC"
ARXIV_API = "https://export.arxiv.org/api/query"


def _ids_from_rss(rss_url: str = RSS_URL) -> list[str]:
    """Return arxiv IDs from today's RSS listing."""
    resp = requests.get(rss_url, timeout=30)
    resp.raise_for_status()
    feed = feedparser.parse(resp.content)
    ids = []
    for e in feed.entries:
        link = e.get("link", "")
        m = re.search(r"(\d{4}\.\d{4,5})", link)
        if m:
            ids.append(m.group(1))
    return ids


def _fetch_metadata(arxiv_ids: list[str]) -> list[dict]:
    """Batch-query the arXiv API for full metadata given a list of IDs."""
    papers = []
    batch_size = 50
    for i in range(0, len(arxiv_ids), batch_size):
        batch = arxiv_ids[i : i + batch_size]
        id_list = ",".join(batch)
        resp = requests.get(
            ARXIV_API,
            params={"id_list": id_list, "max_results": len(batch)},
            timeout=30,
        )
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        for e in feed.entries:
            aid = e.id.rsplit("/", 1)[-1].split("v")[0]
            papers.append(
                {
                    "arxiv_id": aid,
                    "title": " ".join(e.title.split()),
                    "authors": [a.name for a in e.authors],
                    "abstract": " ".join(e.summary.split()),
                    "published": e.published,
                    "categories": [t.term for t in e.tags],
                    "primary_category": e.tags[0].term if e.tags else None,
                    "url": f"https://arxiv.org/abs/{aid}",
                }
            )
        if i + batch_size < len(arxiv_ids):
            time.sleep(3)  # respect arXiv rate limits
    return papers


def fetch(category: str = "math.OC") -> list[dict]:
    ids = _ids_from_rss(f"https://rss.arxiv.org/rss/{category}")
    if not ids:
        return []
    return _fetch_metadata(ids)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="candidates.json")
    args = ap.parse_args()

    papers = fetch()
    with open(args.out, "w") as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)
    print(f"wrote {len(papers)} papers to {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
