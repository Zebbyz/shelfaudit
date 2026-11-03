"""Assign stable Shelf Audit supplier IDs. Registry is append-only: existing IDs never change."""
import pandas as pd, json, os
REG='supplier_registry.csv'
SEED=[  # name, legal_name, nzbn, type, brands
 ('Foodstuffs NZ','Foodstuffs North Island Ltd / Foodstuffs South Island Ltd','9429040750835|9429039459077', 'supermarket_cooperative',
  ['pams','pams value','value','pams finest','pams pure','gilmours',"pak'nsave",'new world']),
 ('Woolworths NZ','Woolworths New Zealand Ltd','9429040683379', 'supermarket_chain',
  ['woolworths','select','macro','essentials','woolworths essentials','the odd bunch','odd bunch','homebrand',
   'free from','signature range','woolworths gold','woolworths macro','freshchoice','fresh choice','ww','macro organic']),
 ("Farrah's",'Farrah\'s Breads Ltd (to verify)','', 'manufacturer',["farrah's",'farrahs']),
 ("Kraft Heinz (Heinz Wattie's)","HEINZ WATTIE'S LIMITED | parent: The Kraft Heinz Company (US)",'9429039009975','manufacturer_multinational',["wattie's", 'watties', 'heinz', 'heinz seriously good']),
 ('Nestle NZ','NESTLE NEW ZEALAND LIMITED | parent: Nestle SA (Switzerland)','9429000001786','manufacturer_multinational',['maggi', 'nestle', 'nescafe', 'purina', 'kitkat']),
 ('Mondelez NZ','MONDELEZ NEW ZEALAND | parent: Mondelez International (US)','9429000001748','manufacturer_multinational',['cadbury', 'cadbury dairy milk', 'oreo']),
 ("Arnott's","ARNOTT'S NEW ZEALAND LIMITED | parent: The Arnott's Group (KKR owned)",'9429000002578','manufacturer_multinational',["arnott's"]),
 ('Sealord','SEALORD GROUP LIMITED | parent: Nissui (Japan) 50% / Moana NZ 50%','9429040180434','manufacturer_multinational',['sealord']),
 ('Mars NZ','MARS NEW ZEALAND LIMITED | parent: Mars Inc (US)','9429032032789','manufacturer_multinational',['masterfoods', 'whiskas']),
 ('General Mills','GENERAL MILLS NEW ZEALAND LIMITED | parent: General Mills Inc (US)','9429000005661','manufacturer_multinational',['old el paso']),
 ('Goodman Fielder','GOODMAN FIELDER NEW ZEALAND LIMITED | parent: Wilmar International (Singapore)','9429000007801','manufacturer_multinational',['meadow fresh', 'edmonds', "vogel's", 'molenberg']),
 ("Griffin's","GRIFFIN'S FOODS LIMITED | parent: Universal Robina Corporation (Philippines)",'9429040963365','manufacturer_multinational',['griffins', "griffin's", 'eta']),
 ('Tegel','TEGEL FOODS LIMITED | parent: Bounty Fresh Group (Philippines)','9429040443737','manufacturer_multinational',['tegel', 'tegel free range']),
 ('Sanitarium','Sanitarium Health Food Company (NZ entity not found on register) | parent: Seventh-day Adventist Church (charitable)','','manufacturer_nz_au_church_owned',['sanitarium up & go', 'sanitarium', 'weet-bix']),
 ('Kimberly-Clark','Kimberly-Clark NZ (NZ entity not found on register) | parent: Kimberly-Clark Corporation (US)','','manufacturer_multinational',['huggies', 'huggies ultra dry', 'u by kotex']),
 ('Unilever','UNILEVER NEW ZEALAND LIMITED | parent: Unilever plc (UK)','9429040971278','manufacturer_multinational',['dove']),
 ('Beiersdorf','Beiersdorf NZ (NZ entity not found on register) | parent: Beiersdorf AG (Germany)','','manufacturer_multinational',['nivea']),
 ("L'Oreal","L'OREAL NEW ZEALAND LIMITED | parent: L'Oreal SA (France)",'9429040690933','manufacturer_multinational',['maybelline new york', "l'oreal paris", 'garnier']),
 ('Procter & Gamble','Procter & Gamble NZ (NZ entity not found on register) | parent: Procter & Gamble Co (US)','','manufacturer_multinational',['head & shoulders']),
 ('Henkel','HENKEL NEW ZEALAND LIMITED | parent: Henkel AG (Germany)','9429040689609','manufacturer_multinational',['schwarzkopf', 'schwarzkopf extra care']),
 ('Reckitt','RECKITT BENCKISER (NEW ZEALAND) LIMITED | parent: Reckitt plc (UK)','9429037449377','manufacturer_multinational',['dettol']),
 ('Clorox (Glad)','CLOROX NEW ZEALAND LIMITED | parent: The Clorox Company (US)','9429000007610','manufacturer_multinational',['glad']),
 ('Energizer','ENERGIZER NZ LIMITED | parent: Energizer Holdings (US)','9429000003391','manufacturer_multinational',['energizer']),
 ('McCain','MCCAIN FOODS (NZ) LIMITED | parent: McCain Foods Ltd (Canada)','9429039562739','manufacturer_multinational',['mccain']),
 ('PepsiCo (Bluebird)','BLUEBIRD FOODS LIMITED | parent: PepsiCo Inc (US)','9429040224541','manufacturer_multinational',['bluebird', 'doritos']),
 ('Kellanova (Pringles)','Kellanova NZ (NZ entity not found on register) | parent: Kellanova; Mars acquisition announced Aug 2024 (completion status unverified)','','manufacturer_multinational',['pringles']),
 ('Simplot','SIMPLOT NEW ZEALAND LIMITED (verify) | parent: J.R. Simplot Company (US)','9429000071857','manufacturer_multinational',['john west', "leggo's"]),
 ('Lee Kum Kee','Lee Kum Kee (NZ entity not found on register) | parent: Lee Kum Kee Co (Hong Kong)','','manufacturer_multinational',['lee kum kee']),
 ('Barilla','Barilla (NZ entity not found on register) | parent: Barilla G. e R. Fratelli (Italy)','','manufacturer_multinational',['barilla']),
 ('Dilmah','DILMAH NEW ZEALAND LIMITED | parent: MJF Group (Sri Lanka)','9429038845864','manufacturer_multinational',['dilmah']),
 ("JDE Peet's","JDE Peet's NZ (NZ entity not found on register) | parent: JDE Peet's NV (Netherlands)",'','manufacturer_multinational',['moccona']),
 ('Chobani','CHOBANI NEW ZEALAND LIMITED | parent: Chobani Global Holdings (US)','9429052534225','manufacturer_multinational',['chobani']),
 ('Froneri (Tip Top ice cream)','FRONERI NZ LIMITED | parent: Froneri (Nestle / PAI Partners JV)','9429047470439','manufacturer_multinational',['tip top']),
 ("Whittaker's",'J H WHITTAKER & SONS LIMITED | parent: Whittaker family (NZ private)','9429040968407','manufacturer_nz_private',["whittaker's"]),
 ('Bundaberg','BUNDABERG BREWED DRINKS NZ LIMITED | parent: Fleming family (AU private)','9429040223421','manufacturer_au_private',['bundaberg']),
 ('San Remo','San Remo Macaroni Co (NZ entity not found on register) | parent: San Remo (AU private)','','manufacturer_au_private',['san remo']),
 ("Barker's",'BARKER FRUIT PROCESSORS LIMITED | parent: Barker family (NZ private)','9429031856522','manufacturer_nz_private',["barker's"]),
 ('Cookie Time','COOKIE TIME LIMITED | parent: Cookie Time (NZ private)','9429039340870','manufacturer_nz_private',['cookie time']),
]
if os.path.exists(REG): reg=pd.read_csv(REG,dtype=str).fillna('')
else: reg=pd.DataFrame(columns=['supplier_id','name','legal_name','nzbn','supplier_type','brands','status'])
nxt=max([int(x[-6:]) for x in reg.supplier_id] or [0])+1
for name,legal,nzbn,typ,brands in SEED:
    if name in set(reg.name):
        i=reg.index[reg.name==name][0]
        b=sorted(set(reg.at[i,'brands'].split('|'))|set(brands)-{''}); reg.at[i,'brands']='|'.join(b)
    else:
        reg.loc[len(reg)]=[f'SA-SUP-{nxt:06d}',name,legal,nzbn,typ,'|'.join(sorted(brands)),'active']; nxt+=1
reg.to_csv(REG,index=False)
b2s={b:r.supplier_id for r in reg.itertuples() for b in r.brands.split('|')}
d=pd.read_csv('brand_ownership.csv')
d=d.drop(columns=[c for c in ('supplier_id',) if c in d])
d.insert(0,'supplier_id',d.brand.map(b2s).fillna(''))
d.to_csv('brand_ownership.csv',index=False)
p=pd.read_csv('products_brand.csv',low_memory=False)
if 'supplier_id' in p: p=p.drop(columns='supplier_id')
p.insert(0,'supplier_id',p.brand.map(b2s).fillna('')); p.to_csv('products_brand.csv',index=False)
print(reg.to_string()); print('brands mapped',(d.supplier_id!='').sum(),'products mapped',(p.supplier_id!='').sum())
