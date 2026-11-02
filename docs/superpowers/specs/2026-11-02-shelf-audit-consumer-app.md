# Shelf Audit consumer app v1 (mobile web)

Live at /app/ on the Shelf Audit intel site (Cloudflare Pages). NZ English. Mobile first, installable later as a PWA, native iPhone later.

## Flow
1. Create account or sign in with a phone number (one-time code). v1: stub, any 6 digit code works, stored on the device only.
2. Locate: browser GPS (asked once, with a reason). Fallback: type a town or use the Papakura demo.
3. Pick store: nearest stores from the national scrape, sorted by distance, with chain and price index.
4. Report preview: national rank, local rank inside 50 km, % above own chain median, % above nearest competitor, distance to it.
5. Email PDF: download now; email send is a stub until the mail Worker is live.
6. Receipts: snap a receipt in several overlapping photos, stitch, OCR, check each line vs Shelf Audit prices, earn points.
7. Coffee table: one phone captures several mates' receipts in one session, each tagged to a person.
8. Tip / dob a rip-off: product, store, price seen, optional photo.
9. Syndicates: groups of 3 to 4 mates sharing deals, receipts and rip-off warnings.

## Features
- GPS nearby stores (Haversine against stores.json).
- Rewards hint (stub): later, with explicit Gmail OAuth consent, read only Everyday Rewards / Clubcard / New World sender headers to suggest preferred chains. v1 is a manual tick list. No mailbox is read.
- PDF audit report.
- Receipt capture: multi photo, own or mates'.
- Tip line.
- My receipts and points: history, savings found, points (10 per receipt, 25 per confirmed rip-off tip).
- Syndicates: create (gets a 6 character code) or join by code, max 4 members, shared feed of deals, rip-off warnings and receipt finds.

## Privacy
- GPS: used in the browser to sort stores. Only the chosen store id is kept, never raw coordinates.
- Email: used only to send the report. Rewards scanning needs separate opt-in OAuth, read-only, sender headers only, revocable.
- Phone: login only, hashed at rest, never sold.
- Receipts: images processed then deleted after 30 days; line items kept without names, card numbers or loyalty numbers (redacted at OCR). Mates' receipts need their verbal consent; the app shows a consent tick per person.
- Syndicate posts visible only to members.
- NZ Privacy Act 2020 aligned; delete account removes all.

## PDF contents
Header and date, store name and chain, overall grade, national rank of N, local rank inside 50 km, % above own chain median, nearest competitor, gap $ on a typical basket per year, distance, top 5 overpriced categories, method note, Unlimited Potential credit.

## Receipt stitch pipeline
1. Capture 1 to 8 overlapping photos, top to bottom.
2. Client: downscale, deskew, greyscale.
3. Server Worker: feature match (ORB) on overlap bands, vertical homography, blend into one tall strip.
4. OCR (Workers AI vision or Google Vision) to text lines.
5. Parse: store header, date, item lines, price, qty, total. Dedupe lines repeated in overlap.
6. Match items to Shelf Audit products (barcode or fuzzy name), flag lines above chain median.
7. Redact PII, store in D1, award points, optional post to syndicate.
v1: UI and capture only; stitch and OCR are stubbed.

## Stubs in v1
Auth, email send, OCR/stitch, syndicate sync (device local storage), rewards hint.
