import csv,re,json,statistics as st
from collections import defaultdict,Counter
rows=list(csv.DictReader(open('/workspace/aa/spread/within_chain_spreads.csv')))
def norm(s):return re.sub(r"\s+"," ",(s or '').lower().replace('’',"'")).strip()
# 1) brands from Woolworths doubled prefix "brand brand desc"
B=Counter()
for r in rows:
    if r['chain']!='woolworths':continue
    w=norm(r['name']).split()
    for k in range(4,0,-1):
        if len(w)>=2*k and w[:k]==w[k:2*k]:B[' '.join(w[:k])]+=1;break
HOUSE={ # brand -> (owner, group, confidence, note)
 'woolworths':('Woolworths NZ','Woolworths NZ','known'),'countdown':('Woolworths NZ','Woolworths NZ','known'),
 'essentials':('Woolworths NZ','Woolworths NZ','known'),'woolworths essentials':('Woolworths NZ','Woolworths NZ','known'),
 'macro':('Woolworths NZ','Woolworths NZ','known'),'woolworths macro':('Woolworths NZ','Woolworths NZ','known'),
 'free from':('Woolworths NZ','Woolworths NZ','known'),'woolworths free from':('Woolworths NZ','Woolworths NZ','known'),'freefrom':('Woolworths NZ','Woolworths NZ','known'),
 'homebrand':('Woolworths NZ','Woolworths NZ','known'),'select':('Woolworths NZ','Woolworths NZ','likely'),
 'woolworths gold':('Woolworths NZ','Woolworths NZ','known'),'signature range':('Woolworths NZ','Woolworths NZ','likely'),
 'little journey':('Woolworths NZ','Woolworths NZ','known'),'odd bunch':('Woolworths NZ','Woolworths NZ','known'),
 'the odd bunch':('Woolworths NZ','Woolworths NZ','known'),'plantitude':('Woolworths NZ','Woolworths NZ','likely'),
 'woolworths food co':('Woolworths NZ','Woolworths NZ','known'),'countdown essentials':('Woolworths NZ','Woolworths NZ','known'),
 'pams':('Foodstuffs NZ','Foodstuffs','known'),'pams finest':('Foodstuffs NZ','Foodstuffs','known'),
 'pams value':('Foodstuffs NZ','Foodstuffs','known'),'pams pure':('Foodstuffs NZ','Foodstuffs','known'),
 'value':('Foodstuffs NZ (Pams Value)','Foodstuffs','likely'),'budget':('Foodstuffs NZ','Foodstuffs','likely'),
 'pak n save':('Foodstuffs NZ','Foodstuffs','known'),"pak'n save":('Foodstuffs NZ','Foodstuffs','known'),"pak'nsave":('Foodstuffs NZ','Foodstuffs','known'),
 'new world':('Foodstuffs NZ','Foodstuffs','known'),'four square':('Foodstuffs NZ','Foodstuffs','known'),
 'gilmours':('Foodstuffs NZ','Foodstuffs','known'),'freshchoice':('Woolworths NZ (supplied banner)','Woolworths NZ','likely'),
 'fresh choice':('Woolworths NZ (supplied banner)','Woolworths NZ','likely'),
}
dict_brands=set(B)|set(HOUSE)
maxk=6
def brand_of(name):
    w=norm(name).split()
    for k in range(min(maxk,len(w)),0,-1):
        p=' '.join(w[:k])
        if p in dict_brands:return p,'dictionary'
    return (w[0] if w else ''),'first_word_guess'
agg=defaultdict(lambda:dict(n=0,chains=set(),src=Counter(),sp=[],ex=[]))
prod_out=[]
for r in rows:
    b,src=brand_of(r['name']);own=HOUSE.get(b)
    grp=own[1] if own else 'manufacturer_or_unknown'
    a=agg[b];a['n']+=1;a['chains'].add(r['chain']);a['src'][src]+=1
    if len(a['ex'])<3:a['ex'].append(r['name'])
    ok=r['reg_spread_pct'] not in('',None) and int(r['reg_n_stores'] or 0)>=5 and r['weighed']=='0' and float(r['reg_spread_pct'])<=300
    if ok:a['sp'].append((float(r['reg_spread_pct']),float(r['reg_spread_dollars'])))
    prod_out.append(dict(chain=r['chain'],product_id=r['product_id'],name=r['name'],brand=b,brand_source=src,owner_group=grp,
       reg_n_stores=r['reg_n_stores'],reg_min=r['reg_min'],reg_max=r['reg_max'],reg_spread_pct=r['reg_spread_pct'],clean=int(ok)))
with open('products_brand.csv','w',newline='') as f:
    W=csv.DictWriter(f,fieldnames=list(prod_out[0]));W.writeheader();W.writerows(prod_out)
own_rows=[]
for b,a in sorted(agg.items(),key=lambda x:-x[1]['n']):
    o=HOUSE.get(b);s=[x[0] for x in a['sp']]
    own_rows.append(dict(brand=b,n_products=a['n'],chains='+'.join(sorted(a['chains'])),
      owner=o[0] if o else '',owner_group=o[1] if o else 'unknown',
      confidence=o[2] if o else ('needs_research' if a['src']['dictionary'] else 'needs_research_brand_guess'),
      clean_n=len(s),median_reg_spread_pct=round(st.median(s),1) if s else '',total_reg_gap_dollars=round(sum(x[1] for x in a['sp']),2),
      examples=' | '.join(a['ex'])))
with open('brand_ownership.csv','w',newline='') as f:
    W=csv.DictWriter(f,fieldnames=list(own_rows[0]));W.writeheader();W.writerows(own_rows)
# group compare by chain
G=defaultdict(list)
for p in prod_out:
    if p['clean']:G[(p['chain'],p['owner_group'])].append(float(p['reg_spread_pct']))
cmp={f'{c}|{g}':dict(n=len(v),median_spread_pct=round(st.median(v),1),mean=round(st.mean(v),1),share_over20=round(100*sum(x>20 for x in v)/len(v),1)) for (c,g),v in sorted(G.items())}
# cross-chain: house brands vs others
cc=list(csv.DictReader(open('/workspace/aa/spread/cross_chain_spreads.csv')))
X=defaultdict(list)
for r in cc:
    b,_=brand_of(r['name']);o=HOUSE.get(b);X[o[1] if o else 'manufacturer_or_unknown'].append(float(r['spread_pct']))
xc={g:dict(n=len(v),median_spread_pct=round(st.median(v),1)) for g,v in X.items()}
S=dict(products=len(prod_out),distinct_brands=len(agg),dictionary_brands_from_woolworths=len(B),
 brands_by_group=Counter(r['owner_group'] for r in own_rows),
 products_by_group=Counter(p['owner_group'] for p in prod_out),
 products_brand_source=Counter(p['brand_source'] for p in prod_out),
 within_chain_compare=cmp,cross_chain_compare=xc,
 house_brands_found=[(r['brand'],r['n_products'],r['owner_group'],r['median_reg_spread_pct']) for r in own_rows if r['owner_group']!='unknown'])
json.dump(S,open('summary.json','w'),indent=1,default=list);print(json.dumps(S,indent=1,default=list))
