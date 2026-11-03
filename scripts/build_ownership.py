#!/usr/bin/env python3
"""Build public/ownership/data.json from the brand owner and store ownership systems.
Rerun: python3 scripts/build_ownership.py [--src /workspace/aa]  (also refreshes data/ownership backup)"""
import csv, json, sys, os, shutil, collections as C
SRC = sys.argv[sys.argv.index('--src')+1] if '--src' in sys.argv else '/workspace/aa'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B, O = f'{SRC}/brand_owners', f'{SRC}/ownership'
rd = lambda p: list(csv.DictReader(open(p, encoding='utf-8')))
reg = rd(f'{B}/supplier_registry.csv'); bo = rd(f'{B}/brand_ownership.csv')
so = rd(f'{O}/store_owners.csv'); pp = rd(f'{O}/owner_people.csv')
ids = json.load(open(f'{O}/ids.json'))
# suppliers
bc = C.Counter(); pc = C.Counter()
for r in bo:
    if r['supplier_id']: bc[r['supplier_id']] += 1; pc[r['supplier_id']] += int(r['n_products'] or 0)
sup = [dict(id=r['supplier_id'], name=r['name'], legal=r['legal_name'], nzbn=r['nzbn'], type=r['supplier_type'],
            brands=bc[r['supplier_id']], products=pc[r['supplier_id']], status=r['status']) for r in reg]
# own-brand share by chain (aggregated from products_brand)
ch = C.defaultdict(C.Counter)
for r in csv.DictReader(open(f'{B}/products_brand.csv', encoding='utf-8')):
    ch[r['chain']]['total'] += 1; ch[r['chain']][r['owner_group']] += 1
share = [dict(chain=k, products=v['total'], foodstuffs=v['Foodstuffs'], woolworths=v['Woolworths NZ'],
              other=v['manufacturer_or_unknown']) for k, v in sorted(ch.items())]
# compact brand index: [brand, supplier_id, products, chains, owner_group, confidence]
brands = sorted(([r['brand'], r['supplier_id'], int(r['n_products'] or 0), r['chains'], r['owner_group'], r['confidence']]
                 for r in bo), key=lambda x: -x[2])
# people and stores
per_store = C.defaultdict(list); people = []
for r in pp:
    st = [s for s in r['stores'].split('|') if s]; chs = [c for c in r['chains'].split('|') if c]
    p = dict(id=r['person_id'], name=r['name'].title(), role=r['role'].replace('|', ', '), holding=r['shareholding'],
             stores=st, chains=chs, n=len(st), cross=len(set(chs)) > 1, dedupe=r['dedupe_confidence'])
    people.append(p)
    for s in st: per_store[s].append(p['id'])
stores = []
for r in so:
    stores.append(dict(store=r['store'], chain=r['chain'], company=r['company'], nzbn=r['nzbn'], num=r['company_number'],
        own=r['owner_id'], url=r['registry_url'], conf=r['confidence'], cls=r['classification'], checked=r['checked'],
        people=per_store.get(r['store'], [])))
bucket = C.Counter(min(p['n'], 6) for p in people if p['n'])
fr = [s for s in stores if s['chain'] != 'Woolworths']
confirmed = [s for s in fr if s['company'] and s['conf'] in ('high', 'medium')]
summ = dict(stores=len(stores), by_chain=C.Counter(s['chain'] for s in stores), franchise=len(fr),
    confirmed=len(confirmed), with_company=sum(1 for s in fr if s['company']), owners=len({s['own'] for s in stores if s['own']}),
    people=len(people), buckets={('6+' if k == 6 else str(k)): bucket[k] for k in range(1, 7)},
    cross=sum(p['cross'] for p in people), brands=len(brands), products=sum(x['products'] for x in share),
    checked=max(s['checked'] for s in stores))
out = dict(summary=summ, suppliers=sup, share=share, stores=stores, people=people, brands=brands)
d = f'{ROOT}/public/ownership'; os.makedirs(d, exist_ok=True)
json.dump(out, open(f'{d}/data.json', 'w'), separators=(',', ':'), ensure_ascii=False)
bk = f'{ROOT}/data/ownership'
for sub, files in (('brand_owners', ['supplier_registry.csv', 'brand_map.csv', 'brand_ownership.csv', 'summary.json', 'SUPPLIER_ID.md', 'WEEKLY_CHECK.md', 'brand_research_2026-11-03.csv', 'suppliers.py', 'weekly_attach.py', 'build.py']),
                   ('ownership', ['store_owners.csv', 'owner_people.csv', 'ids.json', 'build.py', 'build2.py', 'details.py', 'details.json', 'match_result.json'])):
    os.makedirs(f'{bk}/{sub}', exist_ok=True)
    for f in files:
        if os.path.exists(f'{SRC}/{sub}/{f}'): shutil.copy2(f'{SRC}/{sub}/{f}', f'{bk}/{sub}/{f}')
print(json.dumps(summ, indent=1)); print('bytes', os.path.getsize(f'{d}/data.json'))
