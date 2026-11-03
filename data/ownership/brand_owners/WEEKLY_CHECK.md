# Weekly brand to supplier check

Start position: 2026-11-02. 9,411 brands, 24 attached to a supplier (6,366 of 145,209 products, 4.4%). Everything else is UNASSIGNED and queued.

## Columns every week
Both `brand_ownership.csv` and `products_brand.csv` always start with:
- `supplier_id`: SA-SUP-NNNNNN, blank only when no supplier is known yet
- `supplier_name`: from `supplier_registry.csv`, or `UNASSIGNED`
- `supplier_status`: `mapped`, `unmapped` (seen before, still no owner), `new_unmapped` (first seen this week)
The script fails if any row is missing a name or carries an ID not in the registry.

## Source of truth
- `supplier_registry.csv`: one row per supplier company. Append only. IDs never change or get reused.
- `brand_map.csv`: one row per brand string: brand, supplier_id, match_method, first_seen, last_seen, status. Append only. Once a brand has a supplier it keeps it unless someone edits it on purpose (for example a brand sold to a new owner, which gets noted).

## Weekly run (in order)
1. Re-scrape all stores (refreshes `/workspace/aa/spread/within_chain_spreads.csv`).
2. `python3 build.py` (re-extracts brands and rebuilds both CSVs from scratch).
3. `python3 suppliers.py` (adds any new suppliers or brands to the registry, existing IDs untouched).
4. `python3 weekly_attach.py` (joins every brand to `brand_map.csv`, writes supplier columns, flags new brands).
5. Review `weekly/new_brands_YYYY-MM-DD.csv` and `weekly/unassigned_brands.csv` (biggest first). Research owners, add the supplier to the registry (new ID) or the brand to an existing supplier's `brands`, rerun step 3 and 4.
6. `weekly/run_log.csv` gets one line per run so coverage can be tracked week to week.

## How the join works
product row -> `brand` -> `brand_map.brand` -> `supplier_id` -> `supplier_registry.supplier_id` -> name, NZBN, type.
Office DB joins on `supplier_id` (CHAR(13), unique). Before an office record has an SA ID, match on NZBN, then GS1 company prefix, then normalised legal name, and write the SA ID back. See `SUPPLIER_ID.md`.
Week to week comparisons join on `supplier_id` + `product_id` + `chain`, so a supplier's price history stays intact even if the brand text changes.

## Known gaps
- Brand text is a first word guess for most lines, so many "brands" are product words (for example "chillies"). These sit as UNASSIGNED until the brand extractor improves.
- "ww" (1,807 FreshChoice lines) looks like Woolworths own brand but is not attached until confirmed.
