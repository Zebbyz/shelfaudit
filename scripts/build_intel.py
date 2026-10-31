import json,glob,os,statistics as st,sys
from collections import defaultdict
D=sys.argv[1]
P=json.load(open(f'{D}/products.json'));S=json.load(open(f'{D}/stores.json'));M=json.load(open(f'{D}/meta.json'))
sid={s['id']:s for s in S}
prices={}
for f in glob.glob(f'{D}/s/*.json'):
    prices[int(os.path.basename(f)[:-5])]=json.load(open(f))
full=[s for s in S if s.get('ix') and not s.get('thin') and s['id'] in prices]
# per product, per chain regular (non-special) prices
pc=defaultdict(lambda:defaultdict(list)); sp=defaultdict(lambda:[0,0])
for s in S:
    m=prices.get(s['id'],{})
    for k,v in m.items():
        isp=isinstance(v,list); sp[s['ch']][1]+=1; sp[s['ch']][0]+=isp
        if not isp: pc[int(k)][s['ch']].append((v,s['id']))
pchain={}; same=[]; differ=defaultdict(lambda:[0,0])
for i,chs in pc.items():
    row={}
    for c,l in chs.items():
        l.sort(); lo,hi=l[0],l[-1]; row[c]=[lo[0],hi[0],len(l)]
        if len(l)>=20 and lo[0]>0:
            differ[c][1]+=1; differ[c][0]+= hi[0]-lo[0]>0.005
            if lo[0]>=2 and hi[0]/lo[0]<4: same.append([i,c,lo[0],lo[1],hi[0],hi[1],len(l)])
    pchain[i]=row
same.sort(key=lambda x:-(x[4]-x[2])); same=same[:40]
# chain x category index (store-level mean of price/median, non-thin stores, regular+special as captured)
cc=defaultdict(lambda:defaultdict(list))
for s in full:
    for k,v in prices[s['id']].items():
        p=P[int(k)]; v=v[0] if isinstance(v,list) else v
        if p[3]: cc[s['ch']][p[2]].append(v/p[3])
chaincat={c:{k:round(100*st.mean(v),1) for k,v in d.items() if len(v)>=200} for c,d in cc.items()}
# outliers vs own chain
chix={c:v['ix'] for c,v in M['chains'].items() if v['ix']}
out=sorted([[s['id'],round(s['ix']-chix[s['ch']],1)] for s in full if s['ch'] in chix],key=lambda x:x[1])
# regions
rg=defaultdict(list)
for s in full:
    if s.get('r'): rg[s['r']].append(s)
regions=[]
for r,l in rg.items():
    l=sorted(l,key=lambda s:s['ix']); byc=defaultdict(list)
    for s in l: byc[s['ch']].append(s['ix'])
    regions.append({'r':r,'n':len(l),'med':round(st.median([s['ix'] for s in l]),1),'lo':l[0]['id'],'hi':l[-1]['id'],'ch':{c:round(st.median(v),1) for c,v in byc.items()}})
regions.sort(key=lambda x:x['med'])
# national regular-price cash gaps
gaps=[]
for i,chs in pc.items():
    l=sorted(x for c in chs.values() for x in c)
    if len(l)>=40 and l[0][0]>=1 and l[-1][0]/l[0][0]<4: gaps.append([i,l[0][0],l[0][1],l[-1][0],l[-1][1],len(l)])
gaps.sort(key=lambda x:-(x[3]-x[1])); gaps=gaps[:30]
# head to head on chain medians
chs=[c for c in chix]; h2h={}
for a in chs:
    for b in chs:
        if a>=b: continue
        w=[0,0,0]
        for p in P:
            m=p[7]
            if a in m and b in m:
                d=m[a]-m[b]; w[0 if d<-0.005 else 2 if d>0.005 else 1]+=1
        h2h[f'{a}|{b}']=w
json.dump({'same':same,'differ':{c:v for c,v in differ.items()},'chaincat':chaincat,'out':out,'regions':regions,'gaps':gaps,'h2h':h2h,
  'specials':{c:[v[0],v[1]] for c,v in sp.items()},'chix':chix},open(f'{D}/intel.json','w'),separators=(',',':'))
json.dump(pchain,open(f'{D}/pchain.json','w'),separators=(',',':'))
