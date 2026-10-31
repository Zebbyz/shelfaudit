// Shelf Audit API: tips, members, receipts, leaderboard, admin. D1 only.
const J=(o,s=200)=>new Response(JSON.stringify(o),{status:s,headers:{'content-type':'application/json','cache-control':'no-store'}});
const sha=async t=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(t)))].map(b=>b.toString(16).padStart(2,'0')).join('');
const cfg=async(env,k)=>(await env.DB.prepare('SELECT v FROM config WHERE k=?').bind(k).first())?.v;
const clip=(v,n)=>(v==null?'':String(v)).trim().slice(0,n);
const MAXB=600*1024, IMG=['image/jpeg','image/png','image/webp','application/pdf'];
async function limit(env,ip,kind,max,win){const now=Date.now();
  await env.DB.prepare('DELETE FROM hits WHERE ts<?').bind(now-86400000).run();
  const c=(await env.DB.prepare('SELECT COUNT(*) n FROM hits WHERE ip_hash=? AND kind=? AND ts>?').bind(ip,kind,now-win).first()).n;
  if(c>=max)return false;await env.DB.prepare('INSERT INTO hits VALUES(?,?,?)').bind(ip,kind,now).run();return true}
async function human(env,f,ip){const sec=await cfg(env,'ts_secret');if(!sec)return true;
  const t=f.get('cf-turnstile-response');if(!t)return false;
  const r=await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify',{method:'POST',body:new URLSearchParams({secret:sec,response:t})});return (await r.json()).success}
async function member(env,req){const a=req.headers.get('authorization')||'';const t=a.replace(/^Bearer\s+/i,'');if(t.length<20)return null;
  return env.DB.prepare('SELECT id,nick FROM members WHERE token_hash=?').bind(await sha(t)).first()}
async function file(f,k){const x=f.get(k);if(!x||typeof x==='string'||!x.size)return [null,null];
  if(x.size>MAXB)throw new Error('File too large, keep it under 600 KB');if(!IMG.includes(x.type))throw new Error('Photo or PDF only');
  return [new Uint8Array(await x.arrayBuffer()),x.type]}
async function admin(env,req){const t=req.headers.get('x-admin-token')||'';const h=await cfg(env,'admin_hash');return h&&t.length>20&&(await sha(t))===h}

export async function onRequest({request:req,env,params}){
  const p=(params.path||[]).join('/'),m=req.method;
  const ip=await sha((req.headers.get('cf-connecting-ip')||'x')+'|sa');
  if(p.startsWith('v1/'))return env.ASSETS.fetch(req);
  try{
  if(p==='config')return J({sitekey:(await cfg(env,'ts_sitekey'))||null});
  if(p==='tip'&&m==='POST'){const f=await req.formData();if(clip(f.get('website'),5))return J({ok:true});
    if(!await limit(env,ip,'tip',5,3600000))return J({error:'Too many tips from here, try again in an hour'},429);
    if(!await human(env,f,ip))return J({error:'Please complete the check'},400);
    const issue=clip(f.get('issue'),2000);if(issue.length<5)return J({error:'Tell us what is wrong'},400);
    const [ph,pt]=await file(f,'photo');const me=await member(env,req);const price=parseFloat(f.get('price'));
    await env.DB.prepare('INSERT INTO tips(store_id,store_name,product,price,issue,contact,staff,member_id,photo,photo_type,ip_hash) VALUES(?,?,?,?,?,?,?,?,?,?,?)')
      .bind(clip(f.get('store_id'),20),clip(f.get('store_name'),120),clip(f.get('product'),200),isFinite(price)?price:null,issue,clip(f.get('contact'),200),f.get('staff')?1:0,me?.id??null,ph,pt,ip).run();
    return J({ok:true})}
  if(p==='enquiry'&&m==='POST'){const f=await req.formData();if(clip(f.get('website'),5))return J({ok:true});
    if(!await limit(env,ip,'enq',3,86400000))return J({error:'Too many enquiries from here today'},429);
    if(!await human(env,f,ip))return J({error:'Please complete the check'},400);
    const email=clip(f.get('email'),200);if(!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email))return J({error:'Check your email address'},400);
    await env.DB.prepare('INSERT INTO enquiries(name,org,email,kind,msg) VALUES(?,?,?,?,?)').bind(clip(f.get('name'),120),clip(f.get('org'),160),email,clip(f.get('kind'),40),clip(f.get('msg'),3000)).run();return J({ok:true})}
  if(p==='join'&&m==='POST'){const f=await req.formData();if(clip(f.get('website'),5))return J({ok:true});
    if(!await limit(env,ip,'join',3,86400000))return J({error:'Too many sign-ups from here today'},429);
    if(!await human(env,f,ip))return J({error:'Please complete the check'},400);
    const nick=clip(f.get('nick'),30),email=clip(f.get('email'),200).toLowerCase();
    if(!/^[\p{L}\p{N} _.-]{2,30}$/u.test(nick))return J({error:'Nickname: 2 to 30 letters or numbers'},400);
    if(!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email))return J({error:'Check your email address'},400);
    if(await env.DB.prepare('SELECT 1 FROM members WHERE email=?').bind(email).first())return J({error:'That email is already signed up. Use the device you joined on.'},409);
    const tok=[...crypto.getRandomValues(new Uint8Array(24))].map(b=>b.toString(16).padStart(2,'0')).join('');
    await env.DB.prepare('INSERT INTO members(nick,email,token_hash) VALUES(?,?,?)').bind(nick,email,await sha(tok)).run();
    return J({ok:true,token:tok,nick})}
  if(p==='receipt'&&m==='POST'){const me=await member(env,req);if(!me)return J({error:'Sign up first'},401);
    if(!await limit(env,ip,'rcpt',10,86400000))return J({error:'Daily receipt limit reached'},429);
    const f=await req.formData();const [im,it]=await file(f,'file');if(!im)return J({error:'Add a photo or PDF of the receipt'},400);
    const tot=parseFloat(f.get('total'));
    await env.DB.prepare('INSERT INTO receipts(member_id,store_id,store_name,rdate,total,img,img_type) VALUES(?,?,?,?,?,?,?)')
      .bind(me.id,clip(f.get('store_id'),20),clip(f.get('store_name'),120),clip(f.get('date'),10),isFinite(tot)?tot:null,im,it).run();
    return J({ok:true})}
  if(p==='me'){const me=await member(env,req);if(!me)return J({error:'Not signed in'},401);
    const r=await env.DB.prepare('SELECT id,created,store_name,rdate,total,status FROM receipts WHERE member_id=? ORDER BY id DESC LIMIT 50').bind(me.id).all();
    return J({nick:me.nick,receipts:r.results})}
  if(p==='leaderboard'){const r=await env.DB.prepare(`SELECT m.nick,(SELECT COUNT(*) FROM receipts r WHERE r.member_id=m.id AND r.status='verified') rc,(SELECT COUNT(*) FROM tips t WHERE t.member_id=m.id AND t.status='verified') tc FROM members m) WHERE rc+tc>0 ORDER BY rc+tc DESC LIMIT 50`.replace('SELECT m.nick','SELECT * FROM (SELECT m.nick')).all();
    return J({rows:r.results})}
  if(p.startsWith('admin/')){if(!await admin(env,req))return J({error:'no'},403);
    if(p==='admin/list'){const t=await env.DB.prepare('SELECT id,created,store_name,product,price,issue,contact,staff,member_id,status,photo_type,length(photo) psz FROM tips ORDER BY id DESC LIMIT 200').all();
      const r=await env.DB.prepare('SELECT r.id,r.created,m.nick,m.email,r.store_name,r.rdate,r.total,r.status,r.img_type,length(r.img) isz FROM receipts r JOIN members m ON m.id=r.member_id ORDER BY r.id DESC LIMIT 200').all();
      const n=await env.DB.prepare('SELECT COUNT(*) n FROM members').first();const q=await env.DB.prepare('SELECT * FROM enquiries ORDER BY id DESC LIMIT 200').all();return J({tips:t.results,receipts:r.results,members:n.n,enquiries:q.results})}
    if(p==='admin/set'&&m==='POST'){const b=await req.json();const tb=b.kind==='tip'?'tips':'receipts';
      if(!['pending','verified','rejected'].includes(b.status))return J({error:'bad status'},400);
      await env.DB.prepare(`UPDATE ${tb} SET status=? WHERE id=?`).bind(b.status,b.id|0).run();return J({ok:true})}
    if(p==='admin/file'){const u=new URL(req.url),k=u.searchParams.get('kind')==='tip';const row=await env.DB.prepare(k?'SELECT photo b,photo_type t FROM tips WHERE id=?':'SELECT img b,img_type t FROM receipts WHERE id=?').bind(u.searchParams.get('id')|0).first();
      if(!row?.b)return J({error:'none'},404);return new Response(new Uint8Array(row.b),{headers:{'content-type':row.t,'cache-control':'no-store'}})}}
  return J({error:'not found'},404)}catch(e){return J({error:e.message||'error'},400)}}
