import json,re,csv,collections
D=json.load(open('details.json'))
stores=[s for s in json.load(open('/workspace/shelfaudit/public/data/stores.json'))]
fix={'Greenisland':'Green Island','Halfmoonbay':'Half Moon Bay','Kellyroad':'Kelly Road','Lakehawea':'Lake Hawea','Mangerebridge':'Mangere Bridge','Nelsoncity':'Nelson City','Teanau':'Te Anau','Teawamutu':'Te Awamutu','Tengae':'Te Ngae','Pyespa':'Pyes Pa'}
def norm(x):
    x=x.lower().replace("pak 'n' save",'paknsave').replace("pak'nsave",'paknsave').replace("pak n save",'paknsave').replace("pak'n'save",'paknsave').replace('pak nsave','paknsave')
    x=x.replace('fresh choice','freshchoice').replace('super value','supervalue').replace('mt ','mount ').replace('st ','saint ')
    return re.sub(r'[^a-z0-9]','',x)
CH={'New World':['newworld'],"Pak'nSave":['paknsave'],'FreshChoice':['freshchoice','supervalue']}
def tn(v): return [norm(t) for t in re.split(r',|;|\|',v['trading'].replace('View more','')) if t.strip() and 'no trading' not in t.lower()]
match={}
for s in stores:
    if s['ch']=='Woolworths': continue
    t=s['nm'][len(s['ch'])+1:] if s['nm'].startswith(s['ch']+' ') else s['nm'].split(' ',1)[1]; t=fix.get(t,t)
    if t.startswith('SuperValue'): keys=['supervaluebellblock','bellblocksupervalue']; town='bellblock'
    else:
        town=norm(t); keys=[p+town for p in CH[s['ch']]]+[town+p for p in CH[s['ch']]]
    hi=[c for c,v in D.items() if any(k==x or x in (k+'metro',) for x in tn(v) for k in keys)]
    conf='high' if hi else ''
    if not hi:
        hi=[c for c,v in D.items() if any(x.endswith(k) or k in x and not x[x.find(k)+len(k):x.find(k)+len(k)+1].isalpha() for x in tn(v) for k in keys)]
        conf='medium' if hi else ''
    if not hi:
        hi=[c for c,v in D.items() if town in norm(v['name']) and re.search(r'SUPERMARKET|FOODMARKET|NEW WORLD|FRESH|SUPERVALUE|PAK|PNS|\bNW\b|\bFC\b',v['name'].upper()) and 'G411' in v['industry'] and not any(o in x for x in tn(v) for o in ['newworld','paknsave','freshchoice','supervalue','foursquare'] if o not in CH.get(s['ch'],[]))]
        conf='medium' if len(hi)==1 else 'low' if hi else 'none'
    match[str(s['id'])]=(s,hi,conf)
json.dump({k:(v[1],v[2]) for k,v in match.items()},open('match_result.json','w'))
c=collections.Counter(v[2] for v in match.values()); print(c)
for k,(s,h,cf) in list(match.items()):
    if len(h)>1 and cf=='high': print('MULTI',s['nm'],[D[x]['name'] for x in h])
