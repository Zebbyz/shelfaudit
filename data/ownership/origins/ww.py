import csv,json,requests,time,os
from concurrent.futures import ThreadPoolExecutor
own=('woolworths','ww','macro','essentials','select','countdown','homebrand')
rows=[r for r in csv.DictReader(open('../off/ww_barcodes.csv')) if r['ww_brand'].lower().startswith(own)]
done=set()
if os.path.exists('ww_origins.jsonl'): done={json.loads(l)['sku'] for l in open('ww_origins.jsonl')}
out=open('ww_origins.jsonl','a')
H={'x-requested-with':'OnlineShopping.WebApp','User-Agent':'Mozilla/5.0'}
def go(r):
  for t in range(3):
    try:
      d=requests.get('https://www.woolworths.co.nz/api/v1/products/'+r['product_id'],headers=H,timeout=30).json()
      return {'sku':r['product_id'],'barcode':r['barcode'],'brand':d.get('brand') or r['ww_brand'],'name':d.get('name') or r['ww_name'],'origins':d.get('origins'),'own':any((t.get('additionalTag') or {}).get('name','').endswith("Own") for t in d.get('productTags') or [])}
    except Exception: time.sleep(3)
  return {'sku':r['product_id'],'barcode':r['barcode'],'brand':r['ww_brand'],'name':r['ww_name'],'origins':None,'err':1}
todo=[r for r in rows if r['product_id'] not in done]
with ThreadPoolExecutor(3) as ex:
  for i,x in enumerate(ex.map(go,todo)):
    out.write(json.dumps(x)+'\n');out.flush()
    if i%100==0: print(i,len(todo),flush=True)
