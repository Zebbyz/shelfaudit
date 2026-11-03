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
# likely professional trustees: shown for transparency, excluded from owner counts
TRUSTEE_PEOPLE = {'SA-PER-000017': 'joint shareholder only, in three unrelated store companies across New World and Pak\'nSave'}
import re
TRUST_RE = re.compile(r'\b(TRUSTEES?|NOMINEES?|CUSTODIANS?)\b', re.I)
# people and stores
per_store = C.defaultdict(list); people = []
for r in pp:
    st = [s for s in r['stores'].split('|') if s]; chs = [c for c in r['chains'].split('|') if c]
    p = dict(id=r['person_id'], name=r['name'].title(), role=r['role'].replace('|', ', '), holding=r['shareholding'],
             stores=st, chains=chs, n=len(st), cross=len(set(chs)) > 1, dedupe=r['dedupe_confidence'])
    if p['id'] in TRUSTEE_PEOPLE or TRUST_RE.search(r['name']):
        p.update(trustee=True, role='trustee (likely professional, not an owner-operator)', trustee_note=TRUSTEE_PEOPLE.get(p['id'], 'trustee entity'), cross=False)
    people.append(p)
    for s in st: per_store[s].append(p['id'])
# corporate trustee shareholders of matched store companies (from Companies Office shareholdings)
det = json.load(open(f'{O}/details.json')) if os.path.exists(f'{O}/details.json') else {}
cos = C.defaultdict(list)
for r in so:
    if r['company']: cos[r['company']].append(r['store'])
ENT_RE = re.compile(r"([A-Z][A-Z0-9&().' -]*\b(?:TRUSTEES?|NOMINEES?|CUSTODIANS?)\b[A-Z0-9&().' -]*LIMITED)")
te = C.defaultdict(set)
for v in det.values():
    if v.get('name') in cos:
        t = v.get('text', ''); t = t[t.find('Shareholdings'):] if 'Shareholdings' in t else ''
        for m in set(ENT_RE.findall(t)): te[m.strip()].update(cos[v['name']])
trustee_entities = [dict(name=k.title(), stores=sorted(v), n=len(v)) for k, v in sorted(te.items(), key=lambda x: (-len(x[1]), x[0]))]
stores = []
for r in so:
    stores.append(dict(store=r['store'], chain=r['chain'], company=r['company'], nzbn=r['nzbn'], num=r['company_number'],
        own=r['owner_id'], url=r['registry_url'], conf=r['confidence'], cls=r['classification'], checked=r['checked'],
        people=per_store.get(r['store'], [])))
owners_p = [p for p in people if not p.get('trustee')]
bucket = C.Counter(min(p['n'], 6) for p in owners_p if p['n'])
fr = [s for s in stores if s['chain'] != 'Woolworths']
confirmed = [s for s in fr if s['company'] and s['conf'].split(' ')[0] in ('high', 'medium')]
summ = dict(stores=len(stores), by_chain=C.Counter(s['chain'] for s in stores), franchise=len(fr),
    confirmed=len(confirmed), with_company=sum(1 for s in fr if s['company']), owners=len({s['own'] for s in stores if s['own']}),
    people=len(people), buckets={('6+' if k == 6 else str(k)): bucket[k] for k in range(1, 7)},
    cross=sum(p['cross'] for p in owners_p), trustees_excluded=len(people)-len(owners_p), trustee_entities=len(trustee_entities), brands=len(brands), products=sum(x['products'] for x in share),
    checked=max(s['checked'] for s in stores))
out = dict(summary=summ, suppliers=sup, share=share, stores=stores, people=people, brands=brands, trustee_entities=trustee_entities)
d = f'{ROOT}/public/ownership'; os.makedirs(d, exist_ok=True)
json.dump(out, open(f'{d}/data.json', 'w'), separators=(',', ':'), ensure_ascii=False)
bk = f'{ROOT}/data/ownership'
for sub, files in (('brand_owners', ['supplier_registry.csv', 'brand_map.csv', 'brand_ownership.csv', 'summary.json', 'SUPPLIER_ID.md', 'WEEKLY_CHECK.md', 'brand_research_2026-11-03.csv', 'suppliers.py', 'weekly_attach.py', 'build.py']),
                   ('ownership', ['store_owners.csv', 'owner_people.csv', 'ids.json', 'build.py', 'build2.py', 'build3.py', 'fc_lic.json', 'details.py', 'details.json', 'match_result.json'])):
    os.makedirs(f'{bk}/{sub}', exist_ok=True)
    for f in files:
        if os.path.exists(f'{SRC}/{sub}/{f}'): shutil.copy2(f'{SRC}/{sub}/{f}', f'{bk}/{sub}/{f}')
print(json.dumps(summ, indent=1)); print('bytes', os.path.getsize(f'{d}/data.json'))
