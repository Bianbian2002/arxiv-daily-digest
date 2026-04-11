"""Render ranked.json into archive/<date>.html and refresh index.html."""
import json
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


def main():
    repo = Path(__file__).resolve().parents[1]
    ranked = json.loads((repo / "ranked.json").read_text())
    date = ranked.get("date") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ranked["date"] = date

    env = Environment(
        loader=FileSystemLoader(repo / "templates"),
        autoescape=select_autoescape(["html", "j2"]),
    )

    archive_dir = repo / "archive"
    archive_dir.mkdir(exist_ok=True)
    page_html = env.get_template("page.html.j2").render(
        date=date,
        papers=ranked["papers"],
        summary=ranked.get("summary", ""),
    )
    (archive_dir / f"{date}.html").write_text(page_html)

    archives = sorted(
        (p.stem for p in archive_dir.glob("*.html")),
        reverse=True,
    )
    index_html = env.get_template("index.html.j2").render(
        archives=archives,
        latest=ranked,
    )
    (repo / "index.html").write_text(index_html)
    print(f"rendered {date} with {len(ranked['papers'])} papers")


if __name__ == "__main__":
    main()
