import requests,json,time
F="code,product_name,brands,brands_tags,origins,origins_tags,manufacturing_places,emb_codes,countries_tags,labels_tags"
out=open('off_brand_search.jsonl','w')
for b in ['woolworths','countdown','macro','essentials','woolworths-essentials','select','homebrand','pams','pams-finest','pams-value','value','pams-pure','pak-n-save','new-world','freshchoice']:
  p=1
  while True:
    for t in range(4):
      try:
        r=requests.get('https://world.openfoodfacts.org/api/v2/search',params={'brands_tags':b,'countries_tags_en':'new-zealand','fields':F,'page_size':100,'page':p},headers={'User-Agent':'ShelfAudit/0.1 (hello@thequietpath.co.nz)'},timeout=60);d=r.json();break
      except Exception as e: time.sleep(5);d=None
    if not d: break
    for x in d.get('products',[]): x['_q']=b; out.write(json.dumps(x)+'\n')
    print(b,p,d.get('count'),flush=True)
    if p*100>=d.get('count',0): break
    p+=1; time.sleep(2)
