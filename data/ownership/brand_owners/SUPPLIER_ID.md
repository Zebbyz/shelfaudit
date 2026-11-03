# Shelf Audit supplier ID

Format: `SA-SUP-NNNNNN` (prefix SA-SUP, hyphen, 6 digit zero padded sequence). Regex: `^SA-SUP-\d{6}$`.

Rules
- One ID per legal supplier company (not per brand). Brands map many to one.
- IDs are permanent. Never reused, never renumbered. The registry (`supplier_registry.csv`) is append only; `suppliers.py` only adds new rows or new brands.
- Retired or merged suppliers keep their ID with `status` set to `merged:<SA-SUP-id>` or `inactive`.

Files
- `supplier_registry.csv`: supplier_id, name, legal_name, nzbn, supplier_type, brands (pipe separated), status
- `brand_ownership.csv` and `products_brand.csv`: start with supplier_id, supplier_name, supplier_status (see WEEKLY_CHECK.md)

Office DB join
- Store `supplier_id` as CHAR(13) in the office supplier table, unique index.
- Preferred join: `office.supplier_id = registry.supplier_id`.
- Fallback match when the office has no SA ID yet: NZBN (13 digit, from the NZ Companies Office / NZBN register), then GS1 company prefix, then normalised legal name. Once matched, write the SA ID back into the office record so later joins are exact.
- NZBN column is blank for now, to be filled from the NZBN register.
