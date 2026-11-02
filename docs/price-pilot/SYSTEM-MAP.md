# Price Pilot system map (v0 shell)

Price Pilot is the store-side SaaS on the Shelf Audit platform. Advise first, write-back later.

## End-to-end flow
1. **Login** - one login per physical store (chain deals: every store gets its own).
2. **Geo lock** - login is bound to the store's street address and lat/long at provisioning. User cannot edit it.
3. **Fence** - radius set by the seat: 50 km (Local, $1,150/mo) or 100 km (Local 100, $1,600/mo). Only stores inside the fence are visible. Sharing a password only shows that store's fence.
4. **Nightly sync** - generic integrator kit loads the store's prices + product list into D1.
5. **Rules engine** - store / head office rules (brand, item, category, keyword, seasonal).
6. **Enforcement** - rules checked against national Shelf Audit scrape + fence competitors.
7. **Advise cockpit** - flagged lines with recommended clean prices and impact preview.
8. **Export** - clean price list (CSV). Write-back to POS / accounting is a later upgrade.

## Screens
| Route | Screen | Seat |
| --- | --- | --- |
| `#/home` | Suburb Summary: rank in 50 km + week-by-week year graph | 50 km |
| `#/fence` | Fence compare: competitors inside radius | 50 km |
| `#/rules` | Rules engine | 50 km |
| `#/advise` | Advise / flags | 50 km |
| `#/export` | Clean export | 50 km |
| `#/scorecard` | Full store scorecard (hundreds of metrics) | 100 km only |
| `#/supplier` | Supplier Pack (suppliers inside 100 km) | 100 km only |
| `#/forecast` | Forecast Pack (WoW, MoM, vs 12 months earlier) | 100 km only |
| `#/lossleader` | Loss-leader lab | 100 km only |
| `#/pricesales` | Price to Sales (elasticity, cross-effects, etc.) | 100 km only |

50 km seats see an upgrade card on premium routes, not the module.

## Pricing (ex GST)
- Local 50 km $1,150/mo, Local 100 km $1,600/mo
- Annual: 35% off. Chain NZ buy-in: 25% off, all stores, per-store logins.

## Hosting
Cloudflare Pages (`public/pilot/`), Pages Functions (rules, API), D1 (tenants, seats, rules, catalogues, recommendations).

## Stubs in v0
All data is mock (`public/pilot/app.js`). No real auth, no D1 tables for tenants/seats/rules yet, no integrator kit, export is a client-side CSV of mock rows. Seat toggle in the header is a demo switch only; in production radius comes from the seat record server-side.
