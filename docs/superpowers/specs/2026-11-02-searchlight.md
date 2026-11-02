# Searchlight (Shelf Audit for groups)

Date: 2 November 2026. Owner: Guy Hollister, Unlimited Potential.

## Member tiers
1. Stores: Price Pilot for supermarket owners (pricing cockpit, 50 / 100 km fences).
2. Consumers: Shelf Audit app (GPS store audit PDF, receipts, tips, syndicates).
3. Groups: Searchlight for schools, sports clubs, community groups and syndicates.

## Problem
Schools and clubs buy the same groceries every week (breakfast clubs, canteens, fundraisers, sausage sizzles) and rarely check which local store does the whole list cheapest.

## Flow
1. Create a group (name, type, suburb). Shared login per group, later multiple members.
2. Add a buy list: paste lines, upload CSV / TXT, saved online supermarket order export, or receipt photo (multi-photo stitch shared with consumer app).
3. Map each line to Shelf Audit products (barcode, name match, size normalise).
4. Compare every store inside the group's radius using nightly Shelf Audit prices.
5. Show cheapest store, total per store, distance, savings $ per shop and per year (40 school weeks).
6. Export CSV now; PDF brief by email to the board or committee later.

## Later
- Import saved carts from online supermarket systems directly.
- Split-shop suggestion when two stores beat one by more than travel cost.
- Bulk pooling across several groups; supplier direct quotes.
- Term savings report; ComCom evidence pack from aggregate group data.

## Pricing (locked 2 November 2026)
Shelf Audit clips the ticket: fee is 10% of the dollars saved versus the dearest local store for the same list. No saving, no fee. Papakura demo: $66.70 saved, $6.67 fee, group keeps $60.03. Fee shown on compare results and the features page.

## Build status
v1 demo at /searchlight/ with mock prices, parse, compare, savings and CSV export.

## Submit back to Searchlight (added 2 November 2026)

- Optional checkbox after a compare: "Submit this compare back to Searchlight". Off by default.
- When ticked, Shelf Audit emails the dearer supermarket: date and time, that a local school, business or club shopped elsewhere after comparing their store, their total vs the cheaper store total, dollars saved. CC the Commerce Commission.
- Group name is withheld unless the group opts in.
- Phase 1 (now): checkbox, live preview of the report text, copy on /searchlight and /searchlight/features. Nothing is sent.
- Email template: docs/templates/searchlight-submit-back-email.md.
- Phase 2: store contact list, ComCom address confirmed, sending switched on only after Guy approves.
