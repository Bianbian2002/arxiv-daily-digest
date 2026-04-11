# Arxiv Daily Digest

A personalized daily digest of arXiv `math.OC` (and cross-listed `cs.LG` /
`stat.ML`) papers, ranked by taste match to a reference corpus of papers the
researcher already likes. Taste leans toward **optimization dynamics**,
**spectral / sign / preconditioned optimizers**, **scaling laws for
optimization**, and **tractable proxies** (linear regression, linear bigram,
noisy quadratic model).

**Live site:** https://bianbian2002.github.io/arxiv-daily-digest/

## How it works

1. A scheduled Claude agent fires each morning after the new arXiv listing.
2. `fetch_arxiv.py` pulls the day's `cat:math.OC` papers (a single query that
   also catches `cs.LG` / `stat.ML` papers cross-listed into `math.OC`).
3. The agent reads `taste.bib` and ranks candidates by taste match, writing
   `ranked.json` with a 1–2 sentence "why you'd care" per paper.
4. `scripts/render.py` turns `ranked.json` into `archive/<date>.html` and
   refreshes `index.html`.
5. A GitHub Pages Action deploys on push.

## Files

- `fetch_arxiv.py` — arXiv fetcher (deterministic, no LLM)
- `scripts/render.py` — Jinja HTML renderer
- `templates/page.html.j2`, `templates/index.html.j2` — site templates
- `taste.bib` — reference papers defining the researcher's taste
- `AGENT_PROMPT.md` — the prompt driving the scheduled agent
- `archive/YYYY-MM-DD.html` — daily digest pages
- `.github/workflows/deploy-pages.yml` — Pages deployment

## Local test

```
pip install -r requirements.txt
python fetch_arxiv.py --hours 36 --out candidates.json
# hand-rank into ranked.json, or let a Claude agent do it
python scripts/render.py
open archive/$(date -u +%Y-%m-%d).html
```

## Tuning taste

Edit `taste.bib` — add papers you like, remove papers that drift from your
current interests. The agent reads this file on every run.
