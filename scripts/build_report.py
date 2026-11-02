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
           'nx': {str(ids[key(r['store'])]): [float(r['national_index']), int(r['products'])] for r in rows if key(r['store']) in ids},
           'best': {'nm': cheap['store'].replace("PAK'nSAVE", "Pak'nSave"), 'ix': float(cheap['within_chain_index']), 'id': ids.get(key(cheap['store']))}},
          open('public/data/report.json', 'w'), separators=(',', ':'))
print(json.dumps(out[0]), dist)

# Nearby cheaper stores for the report card: real road drive time and distance from the public OSRM router
# (OpenStreetMap roads), saving = typical weekly shop x national index gap (same basis as the cost box).
import math, urllib.request
BASKET = 214.10
NAT = {key(r['store']): float(r['national_index']) for r in rows}
def hav(a, b):
    p = math.pi / 180; d = math.sin((b['la'] - a['la']) * p / 2) ** 2 + math.cos(a['la'] * p) * math.cos(b['la'] * p) * math.sin((b['lo'] - a['lo']) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(d))
rep = json.load(open('public/data/report.json'))
for t in rep['top']:
    if t['id'] is None: continue
    me = next(s for s in stores if s['id'] == t['id']); cand = []
    if me['la'] is None or me['lo'] is None: t['near'] = []; continue
    for s in stores:
        n = NAT.get(key(s['nm']))
        if s['id'] == me['id'] or s['la'] is None or s['lo'] is None or n is None or n >= t['nat'] - 0.5: continue
        d = hav(me, s)
        if d <= 25: cand.append((d, s, n))
    cand = sorted(cand, key=lambda c: c[0])[:8]
    if not cand: t['near'] = []; continue
    pts = ';'.join(f"{p['lo']},{p['la']}" for p in [me] + [c[1] for c in cand])
    try:
        j = json.load(urllib.request.urlopen(f'https://router.project-osrm.org/table/v1/driving/{pts}?sources=0&annotations=duration,distance', timeout=30))
        dur, dist, src = j['durations'][0][1:], j['distances'][0][1:], 'osrm'
    except Exception as e:
        print('OSRM failed, straight-line fallback', e); dur = [c[0] * 1.3 / 50 * 3600 for c in cand]; dist = [c[0] * 1300 for c in cand]; src = 'est'
    t['near'] = sorted([{'id': s['id'], 'nm': s['nm'], 'ch': s['ch'], 'nat': n, 'km': round(dist[i] / 1000, 1), 'min': max(1, round(dur[i] / 60)),
                  'wk': round(BASKET * (t['nat'] - n) / 100, 2), 'src': src} for i, (_, s, n) in enumerate(cand)], key=lambda x: x['min'])[:6]
json.dump(rep, open('public/data/report.json', 'w'), separators=(',', ':'))
print(json.dumps(rep['top'][0]['near'], indent=0))
