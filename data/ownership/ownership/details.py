from fast import *
import json,re
from concurrent.futures import ThreadPoolExecutor
p=json.load(open('pool.json'))
KW=r'SUPERMARKET|FRESH|\bFC\b|SUPERVALUE|SUPER VALUE|FOOD|GROCER|MARKET|NEW WORLD|\bNW\b|PAK|\bPNS\b|\bPS\b|RETAIL'
ids={k:v for k,v in p.items() if not k.startswith('NAME:') and re.search(KW,v.upper())}
fs=set()
def res(n):
    for e in search(n):
        if e['name'].upper()==n.upper() and e.get('statusGroup')=='REGISTERED': return str(e['identifier']),n
with ThreadPoolExecutor(8) as ex:
    for r in ex.map(res,[k[5:] for k in p if k.startswith('NAME:')]):
        if r: ids[r[0]]=r[1]; fs.add(r[0])
print('ids',len(ids),flush=True)
def det(cid):
    t=txt(get(f'{B}/ui/pages/companies/{cid}/detail'))
    g=lambda a,b: (t[t.find(a)+len(a):t.find(b,t.find(a))].strip() if a in t else '')
    return cid,{'name':ids[cid],'fs_member':cid in fs,'trading':g('Trading Name(s):','Phone Number'),'industry':g('Industry Classification(s):','View all NZBN'),
      'nzbn':(re.search(r'NZBN:?\s*(\d{13})',t) or [None,''])[1],'text':t[t.find('Directors ('):t.find('Share allocations less') if 'Share allocations less' in t else None][:8000]}
out={}
with ThreadPoolExecutor(8) as ex:
    for i,(c,v) in enumerate(ex.map(det,sorted(ids,key=lambda c:(0 if c in fs else 1 if __import__('re').search(r'SUPERMARKET|FOODMARKET|NEW WORLD|FRESH CHOICE|SUPERVALUE|SUPER VALUE|\bPNS\b|\bNW\b|\bFC\b|PAK|FOOD ?CENTRE',ids[c].upper()) else 2)))):
        out[c]=v
        if i%100==0: print(i,flush=True); json.dump(out,open('details.json','w'))
json.dump(out,open('details.json','w'))
print('done',len(out))
