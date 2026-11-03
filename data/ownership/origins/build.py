import json,csv,re
from collections import Counter,defaultdict
C={'new zealand':'New Zealand','nz':'New Zealand','australia':'Australia','china':'China','thailand':'Thailand','italy':'Italy','spain':'Spain','south africa':'South Africa','malaysia':'Malaysia','vietnam':'Vietnam','viet nam':'Vietnam','india':'India','indonesia':'Indonesia','germany':'Germany','france':'France','canada':'Canada','usa':'United States','united states':'United States','u.s.a':'United States','california':'United States','alaska':'United States','belgium':'Belgium','netherlands':'Netherlands','holland':'Netherlands','chile':'Chile','peru':'Peru','turkey':'Turkey','greece':'Greece','fiji':'Fiji','philippines':'Philippines','sri lanka':'Sri Lanka','korea':'South Korea','japan':'Japan','taiwan':'Taiwan','poland':'Poland','uk':'United Kingdom','united kingdom':'United Kingdom','england':'United Kingdom','ireland':'Ireland','denmark':'Denmark','mexico':'Mexico','argentina':'Argentina','brazil':'Brazil','egypt':'Egypt','pakistan':'Pakistan','singapore':'Singapore','austria':'Austria','switzerland':'Switzerland','portugal':'Portugal','israel':'Israel','ecuador':'Ecuador','cambodia':'Cambodia','bangladesh':'Bangladesh','myanmar':'Myanmar','hungary':'Hungary','czech':'Czech Republic','sweden':'Sweden','uae':'UAE','lithuania':'Lithuania','latvia':'Latvia','estonia':'Estonia','serbia':'Serbia','bulgaria':'Bulgaria','romania':'Romania','ukraine':'Ukraine','slovenia':'Slovenia','croatia':'Croatia','south korea':'South Korea','hong kong':'Hong Kong','tonga':'Tonga','samoa':'Samoa','norway':'Norway','finland':'Finland','scotland':'United Kingdom','colombia':'Colombia','tunisia':'Tunisia','morocco':'Morocco','uruguay':'Uruguay'}
keys=sorted(C,key=len,reverse=True)
def find(s):
  s=' '+s.lower()+' '
  best=None
  for k in keys:
    m=re.search(r'[^a-z]'+re.escape(k)+r'[^a-z]',s)
    if m and (best is None or m.start()<best[0]): best=(m.start(),C[k])
  return best[1] if best else ''
def country(o):
  o=o.strip(); l=o.lower()
  m=re.search(r'(made|product|produced|packed|grown|manufactured|processed|roasted|brewed|baked|bottled|blended|prepared)\s+(in|of)\s+(.*)',l)
  if m:
    c=find(m.group(3)); 
    if c: return c,m.group(1)
  c=find(l); return (c,'stated') if c else ('','')
rows=[]
for l in open('ww_origins.jsonl'):
  x=json.loads(l); o=' / '.join(x.get('origins') or [])
  c,verb=country(o) if o else ('','')
  rows.append(dict(brand=x['brand'],product=x['name'],chain='Woolworths',country=c,manufacturer='',origin_statement=o,
    source='https://www.woolworths.co.nz/shop/productdetails?stockcode='+x['sku'],
    confidence=('high' if verb in('made','product','produced','grown','manufactured') else 'medium' if c else 'none'),basis=('retailer label: '+verb) if c else ('retailer label unparsed' if o else 'no origin on retailer page')))
seen=set()
for l in open('off_brand_search.jsonl'):
  x=json.loads(l)
  if x['code'] in seen: continue
  seen.add(x['code'])
  q=x['_q']; fs=q in('pams','pams-finest','pams-value','value','pams-pure','pak-n-save','new-world','freshchoice')
  if not fs: continue  # Woolworths covered by retailer API
  o=' / '.join(v for v in [x.get('origins') or '',x.get('manufacturing_places') or ''] if v and v!='None')
  c=country(o)[0] if o else ''
  if o and not c and 'new zealand' in o.lower(): c='New Zealand'
  if not c:
    if 'made in new zealand' in o.lower(): c='New Zealand'
  rows.append(dict(brand=x.get('brands') or q,product=x.get('product_name') or '',chain='Foodstuffs',country=c,manufacturer='',origin_statement=o,
    source='https://world.openfoodfacts.org/product/'+x['code'],confidence='medium' if c else 'none',basis='Open Food Facts crowd entry' if c else 'listed on OFF, no origin'))
# packer/manufacturer from emb codes etc: none product-level found
F=['brand','product','chain','country','manufacturer','source','confidence','origin_statement','basis']
w=csv.DictWriter(open('../own_brand_origins.csv','w'),F);w.writeheader();w.writerows(rows)
def fam(b):
  b=b.lower()
  for k in['macro','essentials','pams finest','pams value','pams pure','value','pams','woolworths','countdown']:
    if k in b: return k
  return b
S=defaultdict(Counter)
for r in rows: S[(r['chain'],fam(r['brand']))][r['country'] or 'UNKNOWN']+=1
out=[]
for (ch,b),c in sorted(S.items()):
  tot=sum(c.values()); known=tot-c['UNKNOWN']; nz=c['New Zealand']
  out.append(f"{ch} | {b} | products {tot} | origin known {known} | NZ {nz} ({round(100*nz/known) if known else 0}% of known) | imported {known-nz} | "+', '.join(f'{k} {v}' for k,v in c.most_common() if k!='UNKNOWN'))
for ch in['Woolworths','Foodstuffs']:
  c=Counter(r['country'] or 'UNKNOWN' for r in rows if r['chain']==ch); tot=sum(c.values());k=tot-c['UNKNOWN']
  out.append(f"TOTAL {ch} | products {tot} | known {k} | NZ {c['New Zealand']} ({round(100*c['New Zealand']/k)}%) | "+', '.join(f'{a} {b}' for a,b in c.most_common(15) if a!='UNKNOWN'))
open('../own_brand_origins_summary.txt','w').write('\n'.join(out)+'\n');print('\n'.join(out))
print(Counter(r['origin_statement'] for r in rows if r['origin_statement'] and not r['country']).most_common(15))
