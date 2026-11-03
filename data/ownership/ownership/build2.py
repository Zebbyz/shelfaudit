import json,re,csv,collections,os
exec(open('build.py').read().split("json.dump({k:")[0])
D=json.load(open('details.json'))
def parse(v):
    t=v['text']
    dirs=re.findall(r'Full legal name: (.*?) Residential Address: (.*?) Appointment',t.split('Former Directors')[0].split('Shareholdings (')[0])
    i=t.find('Total Number of Shares'); sh=t[i:]
    allocs=[]
    for m in re.finditer(r'(\d+) : (\d+)\s+\(([\d.]+)%\)(.*?)(?=\s\d+ : \d+\s+\(|$)',sh):
        parts=[p.strip() for p in re.split(r'\s{3,}',m.group(4)) if p.strip()]
        holders=[(parts[j],parts[j+1] if j+1<len(parts) else '') for j in range(0,len(parts),2)]
        allocs.append((float(m.group(3)),holders))
    return dirs,allocs
# registry IDs: persistent
idf='ids.json'; IDS=json.load(open(idf)) if os.path.exists(idf) else {'own':{},'per':{}}
def oid(k,T):
    d=IDS[T]
    if k not in d: d[k]=f"SA-{'OWN' if T=='own' else 'PER'}-{len(d)+1:06d}"
    return d[k]
WW='61262'
rows=[];people=collections.defaultdict(lambda:{'names':set(),'addr':set(),'roles':set(),'sh':[],'cos':set(),'stores':set(),'chains':set()})
corp=collections.defaultdict(lambda:{'name':'','stores':set(),'chains':set()})
for s in stores:
    sid=str(s['id'])
    if s['ch']=='Woolworths':
        rows.append([sid,s['nm'],s['ch'],'WOOLWORTHS NEW ZEALAND LIMITED','9429040683379',WW,oid(WW,'own'),f'https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/{WW}/detail','2026-11-03','high (corporate store)','big_two_owned']); continue
    s_,hi,conf=match[sid]
    if len(hi)!=1:
        rows.append([sid,s['nm'],s['ch'],'' if not hi else ' OR '.join(D[c]['name'] for c in hi),'', ';'.join(hi),'','','2026-11-04',conf+(' (multiple candidates)' if len(hi)>1 else ''),'franchised_or_cooperative_member_owner_unconfirmed']); continue
    c=hi[0];v=D[c];cls='franchised_supplied_by_woolworths' if s['ch']=='FreshChoice' else 'foodstuffs_cooperative_member'
    dirs,allocs=parse(v)
    fs_own=[p for p,h in allocs for n,a in h if 'FOODSTUFFS' in n.upper()]
    if fs_own: cls+=f' (Foodstuffs holds {sum(fs_own):.0f}%)'
    rows.append([sid,s['nm'],s['ch'],v['name'],v['nzbn'],c,oid(c,'own'),f'https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/{c}/detail','2026-11-04',conf,cls])
    seen=set()
    for n,a in dirs: seen.add((n.upper(),'director',a,''))
    for p,h in allocs:
        for n,a in h: seen.add((n.upper(),'shareholder',a,f'{p}%' if len(h)==1 else f'{p}% jointly'))
    for n,role,a,pct in seen:
        iscorp=bool(re.search(r'LIMITED|LTD|TRUSTEE|COMPANY|HOLDINGS',n))
        if iscorp:
            k=corp[n];k['name']=n;k['stores'].add(s['nm']);k['chains'].add(s['ch'])
        else:
            P=people[n];P['names'].add(n);P['addr'].add(a.split(',')[-3].strip() if a.count(',')>=2 else a);P['roles'].add(role)
            if pct:P['sh'].append(f"{v['name']} {pct}")
            P['cos'].add(v['name']);P['stores'].add(s['nm']);P['chains'].add(s['ch'])
with open('store_owners.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow(['store_id','store','chain','company','nzbn','company_number','owner_id','registry_url','checked','confidence','classification']);w.writerows(rows)
with open('owner_people.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow(['person_id','name','role','shareholding','companies','stores','chains','dedupe_confidence'])
    for n,P in sorted(people.items()):
        w.writerow([oid('P:'+n,'per'),n,'|'.join(sorted(P['roles'])),'; '.join(P['sh']),'|'.join(sorted(P['cos'])),'|'.join(sorted(P['stores'])),'|'.join(sorted(P['chains'])),('check: shareholder only, possibly professional trustee' if P['roles']=={'shareholder'} and len(P['stores'])>1 else 'high') if len(P['addr'])<=1 else 'low (same name, different addresses: '+'/'.join(sorted(P['addr']))+')'])
json.dump(IDS,open(idf,'w'),indent=0)
def bucket(n): return str(n) if n<6 else '6+'
print('people',collections.Counter(bucket(len(P['stores'])) for P in people.values()))
print('companies(holders)',collections.Counter(bucket(len(k['stores'])) for k in corp.values()))
print('confirmed',sum(1 for r in rows if r[6]))
for n,P in sorted(people.items(),key=lambda x:-len(x[1]['stores']))[:15]:
    if len(P['stores'])>1: print('P',n,len(P['stores']),sorted(P['stores']),'CROSS' if len(P['chains'])>1 else '','|'.join(P['roles']),P['addr'])
for n,k in sorted(corp.items(),key=lambda x:-len(x[1]['stores']))[:15]:
    if len(k['stores'])>1: print('C',n,len(k['stores']),sorted(k['stores']))
