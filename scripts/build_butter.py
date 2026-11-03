#!/usr/bin/env python3
"""Build public/data/butter.json from the dairy tracker. Run after each tracker update."""
import json,re,sys
src=sys.argv[1] if len(sys.argv)>1 else '/workspace/aa2/dairy_track.json'
d=json.load(open(src))
note=[n for n in d['shelf_notes'] if 'Anchor butter up at every Woolworths' in n][-1]
ww=re.search(r'Anchor butter up at every Woolworths \((\d+), \$([\d.]+) advertised to \$([\d.]+) or \$([\d.]+)\)',note)
ps=re.search(r"every Pak'nSave \((\d+), mostly \$([\d.]+) advertised to \$([\d.]+)\)",note)
ml=re.search(r'Mainland butter down at every Woolworths \((\d+), \$([\d.]+) or \$([\d.]+) to \$([\d.]+)',note)
g=[e for e in d['gdt_events'] if e.get('butter_usd_t')][-1]
pg=re.search(r'butter (-?[\d.]+)%',g.get('index_change_note',''))
out={'checked':d['updated'],'ww':{'stores':int(ww[1]),'from':float(ww[2]),'to':sorted([float(ww[3]),float(ww[4])])},
 'pns':{'stores':int(ps[1]),'from':float(ps[2]),'to':float(ps[3])},
 'gdt':{'date':g['date'],'butter_usd_t':g['butter_usd_t'],'change_pct':float(pg[1])},
 'mainland':{'ww_stores':int(ml[1]),'to':float(ml[4])}}
json.dump(out,open('public/data/butter.json','w'),indent=1);print(out)
