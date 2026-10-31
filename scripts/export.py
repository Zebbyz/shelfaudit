# Exports static JSON for the Shelf Audit site from the national scrape DB.
import sqlite3,re,json,statistics as st,sys,os,importlib.util
from collections import defaultdict,Counter
DB=sys.argv[1] if len(sys.argv)>1 else '/workspace/nz-supermarket-scraper/national/prices.db'
AA='/workspace/aa2'; OUT='public/data'; os.makedirs(OUT+'/s',exist_ok=True)
src=open(AA+'/n.py').read(); helpers=src[src.index('def size'):src.index('# load')]
exec(helpers)
c=sqlite3.connect(f'file:{DB}?mode=ro',uri=True)
snaps={}
for sid,ch,sk,nm,town,ta,n in c.execute('select id,chain,store_key,store_name,town,taken_at,n_products from snapshots order by taken_at'):
  snaps[(ch,sk)]=(sid,nm,town,ta,n)
sids={v[0]:k for k,v in snaps.items()}
CH={'woolworths':'Woolworths','paknsave':"Pak'nSave",'newworld':'New World','freshchoice':'FreshChoice'}
norm=lambda s:re.sub(r'[^a-z0-9]','',s.lower().replace('paknsave','paknsave'))
geo={}
for r in json.load(open(AA+'/stores.json')): geo[norm(r[0])]=(r[2],r[3],r[4],r[5])
for r in json.load(open(AA+'/pp.json')): geo.setdefault(norm(r['name']),(r['town'],r['region'],r['lat'],r['lng']))
for r in json.load(open(AA+'/idx2.json')): geo.setdefault('k'+r[1],(r[3],r[4],None,None))
PROPER={r[1]:r[2] for r in json.load(open(AA+'/idx2.json'))}
items=[]
for sid,ch,sk,pid,name,price,stype,was in c.execute('select snapshot_id,chain,store_key,product_id,name,price,special_type,was_price from prices where price>0'):
  if sids.get(sid)!=(ch,sk): continue
  items.append((ch,sk,pid,name,price,stype,was))
def cid(ch,pid): return ('fs' if ch in('paknsave','newworld') else ch)+':'+pid
parent={}
def find(x):
  while parent.get(x,x)!=x: x=parent[x]
  return x
def union(a,b):
  a,b=find(a),find(b)
  if a!=b: parent[b]=a
cname={}
for ch,sk,pid,name,*_ in items: cname.setdefault(cid(ch,pid),(ch,name))
nk={}
for k,(ch,name) in cname.items():
  z=size(name);t=toks(name)
  if z and t:
    key=(z,t)
    if key in nk and find(nk[key])!=find(k): union(nk[key],k)
    else: nk.setdefault(key,k)
prod=defaultdict(dict)
for ch,sk,pid,name,price,stype,was in items:
  prod[find(cid(ch,pid))].setdefault((ch,sk),(price,1 if stype or was else 0))
out=[]
for r,d in prod.items():
  if len(d)<5: continue
  ps=[v[0] for v in d.values()];mn,mx=min(ps),max(ps)
  if mx/mn>4: continue
  ch,nm=cname[r]; w,_=dedup(nm); nm=' '.join(w); nm=nm[:1].upper()+nm[1:]
  b=brand(ch,cname[r][1])
  out.append(dict(n=nm,b=b,g=B2G.get(b.lower(),'Other brands'),c=cat(nm),chs=len({s[0] for s in d}),d=d,md=st.median(ps),mn=mn,mx=mx))
# store index
A=defaultdict(lambda:[[],0,{}])
for o in out:
  for s,(p,_) in o['d'].items():
    a=A[s];a[0].append(p/o['md']);a[1]+=p>o['md']+0.005
    a[2].setdefault(o['c'],[]).append(p/o['md'])
stores=[];SID={}
for i,(k,(sid,nm,town,ta,n)) in enumerate(sorted(snaps.items(),key=lambda x:x[1][1])):
  nm=PROPER.get(k[1],nm)
  g=geo.get(norm(nm)) or geo.get('k'+k[1]) or (town,'',None,None)
  t,reg,lat,lng=g
  if not t or t=='?': t=town
  t=re.sub(r' Click and Collect$','',str(t)).title() if t and t.islower() else re.sub(r' Click and Collect$','',str(t))
  a=A.get(k); m=len(a[0]) if a else 0
  nm2=nm if not nm.split()[-1].islower() else ' '.join(x if not x.islower() else x.title() for x in nm.split())
  nm2=nm2.replace('PAKnSAVE',"Pak'nSave").replace("PAK'nSAVE","Pak'nSave")
  stores.append(dict(id=i,ch=CH[k[0]],nm=nm2,t=t,r=reg or '',la=lat,lo=lng,ix=round(100*st.mean(a[0]),1) if m else None,
    above=round(100*a[1]/m) if m else None,m=m,thin=m<1000,at=ta,cats={ct:round(100*st.mean(v),1) for ct,v in a[2].items() if len(v)>=15} if a else {}))
  SID[k]=i
# fill missing coords with same-town average
tc=defaultdict(list)
for s in stores:
  if s['la']: tc[s['t'].lower()].append((s['la'],s['lo']))
for s in stores:
  if not s['la'] and tc.get(s['t'].lower()): v=tc[s['t'].lower()];s['la']=round(sum(x for x,_ in v)/len(v),4);s['lo']=round(sum(y for _,y in v)/len(v),4)
# product catalogue: most widely stocked
out.sort(key=lambda o:(-o['chs'],-len(o['d'])))
P=out[:6000]
CHS=['Woolworths',"Pak'nSave",'New World','FreshChoice']
cat_=[]; per=defaultdict(dict)
for i,o in enumerate(P):
  chm={}
  for chn in CHS:
    v=[p for (c2,_),(p,_) in o['d'].items() if CH[c2]==chn]
    if v: chm[chn]=round(st.median(v),2)
  cheapest=sorted(o['d'].items(),key=lambda x:x[1][0])[:5]
  cat_.append([o['n'][:70],o['b'],o['c'],round(o['md'],2),o['mn'],o['mx'],len(o['d']),chm,[[SID[s],p] for s,(p,_) in cheapest]])
  for s,(p,sp) in o['d'].items(): per[SID[s]][i]=[p,sp] if sp else p
for sid,m in per.items(): json.dump(m,open(f'{OUT}/s/{sid}.json','w'),separators=(',',':'))
json.dump(stores,open(OUT+'/stores.json','w'),separators=(',',':'),ensure_ascii=False)
json.dump(cat_,open(OUT+'/products.json','w'),separators=(',',':'),ensure_ascii=False)
chi={}
for chn in CHS:
  v=[s['ix'] for s in stores if s['ch']==chn and s['ix'] and not s['thin']]
  chi[chn]=dict(ix=round(st.median(v),1) if v else None,n=len([s for s in stores if s['ch']==chn]),full=len(v))
hist=Counter(min(int(100*(o['mx']-o['mn'])/o['mn']//10)*10,100) for o in out)
dairy=json.load(open(AA+'/dairy_track.json'))
meta=dict(generated=__import__('datetime').datetime.now().astimezone().isoformat(timespec='minutes'),first=min(s['at'] for s in stores),last=max(s['at'] for s in stores),
  stores=len(stores),full=sum(1 for s in stores if s['ix'] and not s['thin']),prices=len(items),matched=len(out),cross=sum(o['chs']>1 for o in out),chains=chi,spread=sorted(hist.items()))
json.dump(meta,open(OUT+'/meta.json','w'),ensure_ascii=False)
json.dump(dict(updated=dairy['updated'],fonterra=dairy['fonterra_forecasts'],gdt=dairy['gdt_events'],shelf=dairy['shelf'],notes=dairy.get('shelf_notes',[]),sources=dairy.get('sources',{})),open(OUT+'/dairy.json','w'),ensure_ascii=False)
print(meta['stores'],meta['full'],len(P),meta['matched'],sum(1 for s in stores if not s['la']))
