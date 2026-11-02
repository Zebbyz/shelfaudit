# Price Pilot (Shelf Audit platform): Design Spec

Product name: **Price Pilot**. Price Pilot is the pricing SaaS built on the Shelf Audit platform. Shelf Audit remains the data platform and the paid API brand; Price Pilot is the product stores and head offices buy and log in to.

Date: 2 November 2026
Status: Approved by Guy Hollister
Language: NZ English. No em dashes.

## 1. Vision: the insurance logic

Shelf Audit works like an insurer.

- Some supermarkets over-price and rip off customers. Internally Guy calls these Uptickers. In all public and customer-facing copy they are described neutrally as "flagged" stores or lines.
- Some supermarkets price fairly and play the game to sell more and keep customers. These are the honest customers.
- The SaaS is built for the honest ones. It helps them stay sharp, win volume and keep shoppers.
- National observed prices from the Shelf Audit scrape are the shared risk pool. Every store is measured against the same national data.

## 2. Two layers

### 2.1 Paid API (freestyle)

- Customers buy access and play with the data however they like.
- Local: $595 per calendar month plus GST, stores within a 50 km radius of the customer's location.
- Local 100 km (premium): stores within a 100 km radius. Priced a lot more than the 50 km Local tier. Exact price to be set.
- National: $1,850 per month plus GST paid monthly, or $1,450 per month plus GST paid annually.
- A National key gets the entire nation instantly, all stores and products in one go.
- Hosted on Cloudflare Pages Functions with D1. No RapidAPI or other marketplace.
- No rate limiting required.
- Already partially live on the intel preview under `/api/v1/p/`.

### 2.2 Price Pilot: pricing SaaS (rigid engine)

- Product name: Price Pilot (Shelf Audit platform), locked by Guy on 2 November 2026.
- A rigid system that tunes the customer's whole business pricing model.
- Advise first: the engine flags lines and recommends prices, the customer applies them.
- Write-back to the customer's POS comes later as a paid upgrade.

## 3. Buyers

Both packages from day one, priced differently:

- Store package: independent and franchise stores, including owners of several stores.
- Head office package: chains such as Foodstuffs and Woolworths NZ.

## 4. What "clean pricing" means

The customer's own rules, enforced against national Shelf Audit data. Examples:

- No line more than 5% above the chain median.
- Match the cheapest competitor within 10 km.

### 4.1 Rules engine scope

Stores and head offices will want to move pricing at every level, not just line by line. Every rule targets a scope, and scopes can be combined.

Rule scopes:

- **Brand:** every line from one brand (for example all Pams, all Anchor).
- **Item:** one specific SKU or barcode in one store.
- **Product:** the same product across sizes and variants (for example Anchor Blue Top in every size).
- **Category:** a whole aisle or category tree level (for example Dairy, or Dairy > Milk).
- **Seasonal section:** an entire seasonal range (for example Christmas, Easter, BBQ season, back to school), with start and end dates so the rule switches on and off by itself.
- **Keyword:** any line whose name or description matches a keyword or phrase (for example "gluten free", "organic", "lamb").
- **Custom tag:** any group the customer defines and tags themselves (for example "key value items", "loss leaders", "local suppliers").

Combining scopes:

- Scopes can be joined with AND, OR and NOT (for example Brand = Pams AND Category = Dairy, NOT keyword "organic").
- Rules can apply to one store, a hand-picked group of stores, or the whole account.
- When rules overlap, the most specific scope wins (item, then product, then keyword or custom tag, then brand, then category, then seasonal section, then account-wide), unless the customer sets an explicit priority.
- Every rule shows a preview of how many lines it touches and the price change before it is applied.
- Actions per rule: set a ceiling or floor against national Shelf Audit data, match or beat a nearby competitor, apply a fixed or percentage move, or hold a price.

## 5. Connectors

- Day one the connector pulls prices and the product list only. Cost, margin, promos and stock come later.
- Plug-and-play for stores is a centrepiece of v1.
- Generic integrator kit now: CSV or SFTP price file, one-time column mapping, scheduled nightly sync.
- Named NZ POS connectors come later.

## 6. Approach

Advise cockpit on Cloudflare. Full POS middleware is not part of v1.

## 7. Product shape

All of this ships under the Price Pilot name, on the Shelf Audit platform.

### Store package

- Connect a store, set rules, see flagged lines and recommended prices, export a clean price list to apply by hand.
- Multi-store ownership: an owner with several stores (for example four) connects all of them under one account and compares them side by side, line by line, with each store's flags and recommendations shown together. Every store in the compare must hold its own paid seat (see 10.1).

### Head office package

- The same engine across many stores.
- Chain-wide rules, league tables, and which stores are drifting.

### Underneath both

- National scrape plus the paid API data as the enforcement layer.
- File connectors day one. Write-back later.

## 8. Architecture

- Cloudflare Pages for the store and head office UIs.
- Pages Functions for the rules engine and the API.
- D1 for tenants, stores, rules, uploaded catalogues and recommendations.
- National data from the Shelf Audit scrape.
- Integrator module: column mapper and scheduled sync, named POS adapters later.
- No Supabase.
- Custom domain later (shelfaudit.co.nz is available). DNS only, no code change.

## 9. Store day flow

1. Plug in the generic kit and map the price file columns once.
2. Nightly sync pulls prices and products.
3. Rules engine compares each line to national Shelf Audit data under the customer's rules.
4. Cockpit shows flagged lines and recommended prices.
5. Customer exports a clean list (write-back later).
6. Multi-store owners see their stores side by side. Head office sees the same across the whole chain.

## 10. Billing

- Flat pricing: API Local and National fees plus SaaS subscriptions.
- Competitor radius ("look over the fence"): Price Pilot customers can see every supermarket within 50 km of their store, aligned with the Local API price context ($595 per month plus GST). A wider 100 km radius is a premium tier that costs a lot more than 50 km. National remains the full NZ view of every store.
- No cut of supermarket sales. That was a metaphor for the logic, not the billing model.

### 10.1 Licensing rule: one paid seat per physical store

- One paid seat covers one physical store, identified by its trading address and store identity.
- Multi-store side-by-side compare only works when every store in the compare is licensed on the account.
- Copy-pasting the same catalogue into one seat as extra "stores" is not allowed. A seat cannot hold more than one store.
- Enforcement in v1:
  - Each seat is bound to one store location (address, plus the matching Shelf Audit store ID where one exists). Adding a store means adding a seat.
  - The integrator flags uploads where a second store's catalogue is a near copy of another on the account, or where the location does not match the seat, and holds it for review.
  - Seat changes (moving a seat to a different store) are logged and limited, so one licence cannot be rotated around several shops.
- Terms of service state the rule plainly, and breaches mean back-billing for the unlicensed stores.

## 11. Build order

1. Finish the paid API and load full per-store prices into D1.
2. Generic integrator kit.
3. Rules engine and store cockpit (advise and export), including multi-store side-by-side compare.
4. Head office multi-store view.
5. Named POS connectors and write-back later.

## 12. Out of scope for v1

- Commerce Commission filing (separate track, nothing sent without Guy's go).
- Stripe billing automation details.
- Turnstile.
- R2, unless it becomes necessary.
