"""Weekly step: attach every brand to a supplier company. Run after build.py.
Keeps SA-SUP IDs stable (registry and brand_map are append only), writes supplier_id + supplier_name
into brand_ownership.csv and products_brand.csv, and flags brands with no supplier."""
import pandas as pd, os, datetime as dt
T=dt.date.today().isoformat()
reg=pd.read_csv('supplier_registry.csv',dtype=str).fillna('')
# brand_map: one row per brand, permanent once a supplier is assigned
BM='brand_map.csv'
bm=pd.read_csv(BM,dtype=str).fillna('') if os.path.exists(BM) else pd.DataFrame(columns=['brand','supplier_id','match_method','first_seen','last_seen','status'])
for r in reg.itertuples():                      # registry brands seed the map
    for b in filter(None,r.brands.split('|')):
        if b not in set(bm.brand): bm.loc[len(bm)]=[b,r.supplier_id,'registry',T,'','mapped']
        elif bm.loc[bm.brand==b,'supplier_id'].iloc[0]=='':
            bm.loc[bm.brand==b,['supplier_id','match_method','status']]=[r.supplier_id,'registry','mapped']
d=pd.read_csv('brand_ownership.csv',dtype=str).fillna('')
d=d.drop(columns=[c for c in ['supplier_id','supplier_name','supplier_status'] if c in d])
known=set(bm.brand); new=[b for b in d.brand if b not in known]
for b in new: bm.loc[len(bm)]=[b,'','',T,'','new_unmapped']
bm.loc[bm.brand.isin(set(d.brand)),'last_seen']=T
bm.loc[(bm.supplier_id=='')&(~bm.brand.isin(new))&(bm.brand.isin(set(d.brand))),'status']='unmapped'
bm.loc[~bm.brand.isin(set(d.brand)),'status']=bm.status.where(bm.supplier_id=='', 'mapped_not_seen')
bm.to_csv(BM,index=False)
sid=dict(zip(bm.brand,bm.supplier_id)); sname=dict(zip(reg.supplier_id,reg.name)); st=dict(zip(bm.brand,bm.status))
def attach(df):
    df.insert(0,'supplier_status',df.brand.map(st).fillna('new_unmapped'))
    df.insert(0,'supplier_name',df.brand.map(sid).map(sname).fillna(''))
    df.insert(0,'supplier_id',df.brand.map(sid).fillna(''))
    df.loc[df.supplier_id=='','supplier_name']='UNASSIGNED'
    return df
attach(d).to_csv('brand_ownership.csv',index=False)
p=pd.read_csv('products_brand.csv',dtype=str,low_memory=False).fillna('')
p=p.drop(columns=[c for c in ['supplier_id','supplier_name','supplier_status'] if c in p])
attach(p).to_csv('products_brand.csv',index=False)
# checks: every row has both columns, every ID exists in registry
for n,x in [('brands',d),('products',p)]:
    assert x.supplier_name.ne('').all()
    assert set(x.supplier_id[x.supplier_id!=''])<=set(reg.supplier_id), n
nb=d[d.brand.isin(new)].sort_values('n_products',key=lambda s:s.astype(int),ascending=False)
os.makedirs('weekly',exist_ok=True)
nb[['brand','n_products','chains','examples']].to_csv(f'weekly/new_brands_{T}.csv',index=False)
un=d[d.supplier_id==''].sort_values('n_products',key=lambda s:s.astype(int),ascending=False)
un[['brand','n_products','chains','examples']].to_csv('weekly/unassigned_brands.csv',index=False)
mp=(p.supplier_id!='')
line=f"{T},brands={len(d)},brands_mapped={(d.supplier_id!='').sum()},new_brands={len(new)},products={len(p)},products_mapped={mp.sum()},products_mapped_pct={100*mp.mean():.1f}\n"
open('weekly/run_log.csv','a').write(line); print(line)
