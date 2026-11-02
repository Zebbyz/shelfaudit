"""Bake public/data/report.json: worst-priced store report card + grade scale.
Source: /workspace/aa/spread/worst.json and store_index.csv (regular shelf prices, index 100 = own chain median)."""
import csv, json, re, sys
SRC = sys.argv[1] if len(sys.argv) > 1 else '/workspace/aa/spread'
SCALE = [['A', 99.0, 'Sharp: below its chain'], ['B', 101.0, 'Fair: on chain pricing'], ['C', 103.0, 'Watch: a little dear'],
         ['D', 105.0, 'Dear: well above chain'], ['F', 999, 'Worst pricing: flagged']]
grade = lambda ix: 'F' if ix >= 105 else next(g for g, hi, _ in SCALE if ix <= hi)
key = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
stores = json.load(open('public/data/stores.json'))
ids = {key(s['nm']): s['id'] for s in stores}
rows = list(csv.DictReader(open(f'{SRC}/store_index.csv')))
W = {w['store']: w for w in json.load(open(f'{SRC}/worst.json'))['stores']}
CH = {'freshchoice': 'FreshChoice', 'newworld': 'New World', 'paknsave': "Pak'nSave", 'woolworths': 'Woolworths'}
def pretty(n): return re.sub(r'\b([a-z])', lambda m: m.group(1).upper(), n) if n != n.title() else n
out = []
for r in rows[:5]:
    ix = float(r['within_chain_index']); w = W.get(r['store'], {})
    t = (w.get('top') or [None])[0]
    out.append({'rank': int(r['rank']), 'nm': stores[ids[key(r['store'])]]['nm'] if key(r['store']) in ids else pretty(r['store']), 'ch': CH.get(r['chain'], r['chain']),
                'id': ids.get(key(r['store'])), 'ix': ix, 'nat': float(r['national_index']), 'g': grade(ix),
                'n': int(r['products']), 'med': float(r['median_pct_vs_chain']), 'o20': int(r['n_over20']), 'o20p': float(r['pct_over20']),
                'ex': t and {'p': t['name'], 'v': t['price'], 'm': t['chain_median'], 'pct': t['pct']}})
dist = {g: 0 for g, *_ in SCALE}
for r in rows: dist[grade(float(r['within_chain_index']))] += 1
cheap = min(rows, key=lambda r: float(r['within_chain_index']))
json.dump({'stores': len(rows), 'scale': [[g, d] for g, _, d in SCALE], 'dist': dist, 'top': out,
           'best': {'nm': cheap['store'].replace("PAK'nSAVE", "Pak'nSave"), 'ix': float(cheap['within_chain_index']), 'id': ids.get(key(cheap['store']))}},
          open('public/data/report.json', 'w'), separators=(',', ':'))
print(json.dumps(out[0]), dist)
