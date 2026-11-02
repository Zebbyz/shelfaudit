// Shelf Audit partner pricing API (keyed). Plans: local (stores within radius of a registered centre) | national.
const H={'content-type':'application/json','cache-control':'no-store','access-control-allow-origin':'*','access-control-allow-headers':'authorization,x-api-key'};
const J=(o,s=200,x={})=>new Response(JSON.stringify(o),{status:s,headers:{...H,...x}});
const sha=async t=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(t)))].map(b=>b.toString(16).padStart(2,'0')).join('');
export const PLANS={local:{label:'Local',radius_km:50,per_min:30,per_day:2000},national:{label:'National',radius_km:null,per_min:60,per_day:10000}};
export const SCHEMA=[
`CREATE TABLE IF NOT EXISTS api_keys(id INTEGER PRIMARY KEY,prefix TEXT NOT NULL,key_hash TEXT UNIQUE NOT NULL,org TEXT,email TEXT,plan TEXT NOT NULL CHECK(plan IN('local','national')),billing TEXT,lat REAL,lon REAL,radius_km REAL,status TEXT NOT NULL DEFAULT 'active',created TEXT DEFAULT CURRENT_TIMESTAMP,expires TEXT,note TEXT)`,
`CREATE TABLE IF NOT EXISTS api_usage(key_id INTEGER NOT NULL,bucket TEXT NOT NULL,n INTEGER NOT NULL DEFAULT 0,PRIMARY KEY(key_id,bucket))`];
let ready=false;
export async function ensure(env){if(ready)return;for(const s of SCHEMA)await env.DB.prepare(s).run();ready=true}
const km=(a,b,c,d)=>{const r=Math.PI/180,x=Math.sin((c-a)*r/2)**2+Math.cos(a*r)*Math.cos(c*r)*Math.sin((d-b)*r/2)**2;return 12742*Math.asin(Math.sqrt(x))};
async function asset(env,req,path){const u=new URL(req.url);u.pathname=path;u.search='';const r=await env.ASSETS.fetch(new Request(u));return r.ok?r.json():null}
export async function issue(env,b){await ensure(env);
  const plan=b.plan;if(!PLANS[plan])throw new Error('plan must be local or national');
  let lat=null,lon=null,rad=null;if(plan==='local'){lat=+b.lat;lon=+b.lon;rad=+(b.radius_km||50);
    if(!(lat<-30&&lat>-50&&lon>165&&lon<180))throw new Error('local plan needs an NZ lat and lon for the centre');}
  const raw=[...crypto.getRandomValues(new Uint8Array(24))].map(x=>x.toString(16).padStart(2,'0')).join('');
  const key='sa_'+(plan==='local'?'loc':'nat')+'_'+raw;
  const r=await env.DB.prepare('INSERT INTO api_keys(prefix,key_hash,org,email,plan,billing,lat,lon,radius_km,expires,note) VALUES(?,?,?,?,?,?,?,?,?,?,?) RETURNING id')
    .bind(key.slice(0,12),await sha(key),String(b.org||'').slice(0,160),String(b.email||'').slice(0,160),plan,String(b.billing||'monthly'),lat,lon,rad,b.expires||null,String(b.note||'').slice(0,500)).first();
  return {id:r.id,key,plan,lat,lon,radius_km:rad,warning:'Shown once only. Store it safely.'}}
async function auth(env,req){const a=req.headers.get('x-api-key')||(req.headers.get('authorization')||'').replace(/^Bearer\s+/i,'');
  if(!/^sa_(loc|nat)_[0-9a-f]{48}$/.test(a))return null;
  const k=await env.DB.prepare('SELECT * FROM api_keys WHERE key_hash=?').bind(await sha(a)).first();
  if(!k||k.status!=='active'||(k.expires&&k.expires<new Date().toISOString().slice(0,10)))return null;return k}
async function meter(env,k){const p=PLANS[k.plan],d=new Date().toISOString(),day='d'+d.slice(0,10),min='m'+d.slice(0,16);
  const q='INSERT INTO api_usage(key_id,bucket,n) VALUES(?,?,1) ON CONFLICT(key_id,bucket) DO UPDATE SET n=n+1 RETURNING n';
  const [a,b]=await env.DB.batch([env.DB.prepare(q).bind(k.id,day),env.DB.prepare(q).bind(k.id,min)]);
  if(Math.random()<0.02)await env.DB.prepare("DELETE FROM api_usage WHERE bucket LIKE 'm%' AND bucket<?").bind('m'+new Date(Date.now()-3600e3).toISOString().slice(0,16)).run();
  const nd=a.results[0].n,nm=b.results[0].n;return {ok:nd<=p.per_day&&nm<=p.per_min,hdr:{'x-ratelimit-day-limit':''+p.per_day,'x-ratelimit-day-used':''+nd,'x-ratelimit-minute-limit':''+p.per_min}}}
export async function partner(env,req,p){
  if(req.method==='OPTIONS')return new Response(null,{headers:H});
  if(req.method!=='GET')return J({error:'GET only'},405);
  await ensure(env);const k=await auth(env,req);
  if(!k)return J({error:'Missing or invalid API key. Send it as the x-api-key header.',docs:'/#/api'},401);
  const m=await meter(env,k);if(!m.ok)return J({error:'Rate limit reached for your plan'},429,{...m.hdr,'retry-after':'60'});
  const stAll=await asset(env,req,'/api/v1/stores.json');
  const local=k.plan==='local';
  const inR=s=>!local||(s.lat!=null&&km(k.lat,k.lon,s.lat,s.lon)<=k.radius_km);
  const ids=new Set(stAll.stores.filter(inR).map(s=>s.id));
  const scope={plan:k.plan,stores_in_scope:ids.size,...(local?{centre:{lat:k.lat,lon:k.lon},radius_km:k.radius_km}:{})};
  const out=(o)=>J({...o,scope,notice:'Prices as observed on public store listings at capture time. Differences are flagged for review and are not findings of wrongdoing.'},200,m.hdr);
  const seg=p.replace(/^partner\/?|^v1\/(p\/)?/,'').replace(/\.json$/,'');
  if(seg===''||seg==='me')return out({org:k.org,key_prefix:k.prefix,limits:PLANS[k.plan],endpoints:['stores','gaps','index','products/{id}']});
  if(seg==='stores'){const s=stAll.stores.filter(inR).map(s=>local?{...s,distance_km:+km(k.lat,k.lon,s.lat,s.lon).toFixed(1)}:s);return out({captured:stAll.captured,count:s.length,stores:s})}
  if(seg==='index'){const d=await asset(env,req,'/api/v1/index.json');return out(local?{captured:d.captured,note:d.note,chains:d.chains,stores:stAll.stores.filter(inR).map(s=>({id:s.id,name:s.name,chain:s.chain,index:s.index,thin_data:!!s.thin_data}))}:d)}
  if(seg==='gaps'){const d=await asset(env,req,'/api/v1/gaps.json');const g=local?d.gaps.filter(x=>ids.has(x.cheapest.store.id)||ids.has(x.dearest.store.id)):d.gaps;return out({captured:d.captured,rule:d.rule,count:g.length,gaps:g})}
  const pm=seg.match(/^products\/(\d+)$/);if(pm){const d=await asset(env,req,`/api/v1/products/${pm[1]}.json`);if(!d)return J({error:'Unknown product id'},404,m.hdr);
    if(local)d.cheapest=(d.cheapest||[]).filter(c=>ids.has(c.store.id));return out(d)}
  return J({error:'Unknown endpoint',endpoints:['stores','gaps','index','products/{id}','me']},404,m.hdr)}
