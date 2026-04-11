"""Fetch the latest math.OC papers from arXiv.

A paper cross-listed from cs.LG or stat.ML into math.OC also appears in a
`cat:math.OC` query, so a single query covers the scope.
"""
import argparse
import json
import sys
from datetime import datetime, timedelta, timezone

import feedparser
import requests

ARXIV_API = "https://export.arxiv.org/api/query"


def fetch(category: str = "math.OC", hours_back: int = 36, max_results: int = 400):
    params = {
        "search_query": f"cat:{category}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    resp = requests.get(ARXIV_API, params=params, timeout=30)
    resp.raise_for_status()
    feed = feedparser.parse(resp.content)
    if feed.bozo and not feed.entries:
        raise RuntimeError(f"arxiv fetch failed: {feed.bozo_exception}")

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    papers = []
    for e in feed.entries:
        published = datetime(*e.published_parsed[:6], tzinfo=timezone.utc)
        if published < cutoff:
            continue
        arxiv_id = e.id.rsplit("/", 1)[-1].split("v")[0]
        papers.append(
            {
                "arxiv_id": arxiv_id,
                "title": " ".join(e.title.split()),
                "authors": [a.name for a in e.authors],
                "abstract": " ".join(e.summary.split()),
                "published": e.published,
                "categories": [t.term for t in e.tags],
                "primary_category": e.tags[0].term if e.tags else None,
                "url": f"https://arxiv.org/abs/{arxiv_id}",
            }
        )
    return papers


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="candidates.json")
    ap.add_argument("--hours", type=int, default=36)
    ap.add_argument("--max-results", type=int, default=400)
    args = ap.parse_args()

    papers = fetch(hours_back=args.hours, max_results=args.max_results)
    with open(args.out, "w") as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)
    print(f"wrote {len(papers)} papers to {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
