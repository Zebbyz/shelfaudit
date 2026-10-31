# Shelf Audit

Independent, store-by-store price index for New Zealand supermarkets on identical products.

- `public/` static site (no build step). Data lives in `public/data/*.json`.
- `scripts/export.py` regenerates the JSON from the national scrape database.
- Hosted on Cloudflare Pages: `npx wrangler pages deploy public --project-name shelfaudit`.
