# Shelf Audit Pricing API (v1)

Hosting: Cloudflare Pages (static site + data files) with Pages Functions for `/api/*`, and the free D1 database `shelfaudit` for keys, plans and usage. No Supabase, no paid host. Preview: https://intel.shelfaudit.pages.dev (custom domain later).

## Plans (GST exclusive)
- Local: $595 per calendar month. Stores within 50 km of the registered centre (lat/lon). 30 requests/min, 2,000/day.
- National: $1,850 per month, or $1,450 per month paid annually. All stores. 60 requests/min, 10,000/day.

## Auth
Send the key as `x-api-key: sa_nat_...` (or `Authorization: Bearer sa_...`). Keys are random, shown once, and only a SHA-256 hash is kept in D1 (`api_keys`). Usage is counted per day and per minute in `api_usage`; responses carry `x-ratelimit-*` headers, and 429 when over.

## Endpoints (GET, JSON)
- `/api/v1/p/me` plan, scope and limits
- `/api/v1/p/stores` stores in scope (local adds `distance_km`)
- `/api/v1/p/index` price index (local: stores in scope)
- `/api/v1/p/gaps` largest observed regular-price gaps (local: gaps touching a store in scope)
- `/api/v1/p/products/{id}` product price summary (local: cheapest list limited to stores in scope)

Every response includes `scope` and a `notice`: prices as observed on public store listings at capture time; differences are flagged for review and are not findings of wrongdoing.

```
curl -H "x-api-key: $SHELFAUDIT_KEY" https://intel.shelfaudit.pages.dev/api/v1/p/stores
```

## Issuing keys (admin only)
```
curl -X POST https://intel.shelfaudit.pages.dev/api/admin/apikey \
  -H "x-admin-token: $(cat /home/box/secrets/shelfaudit_admin_token)" -H content-type:application/json \
  -d '{"plan":"local","lat":-39.93,"lon":175.05,"org":"Example Ltd","email":"x@example.nz","billing":"monthly"}'
```
List: `GET /api/admin/apikeys`. Revoke/pause: `POST /api/admin/apikey/status {"id":1,"status":"revoked"}`.
The admin token is checked against `admin_hash` in the D1 `config` table, so no Pages env secret is required.

## Deploy
```
npx wrangler pages deploy public --project-name shelfaudit --branch intel
```
Schema: `migrations/0005_api_keys.sql` (also auto-created on first call). The public `/api/v1/*.json` files remain open for the site itself.
