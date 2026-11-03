(function(){var I=window.BLOG_IDX||[],i=document.getElementById("bs"),L=document.getElementById("bs-list"),n=document.getElementById("bs-n"),r=document.getElementById("bs-r"),all=document.getElementById("bl-all"),sel=-1,cur=[];
var SUF=["ations","ation","ings","ing","ers","er","ies","ied","ed","es","s"];function stem(w){for(var k=0;k<SUF.length;k++){var s=SUF[k];if(w.length-s.length>=4&&w.slice(-s.length)===s)return w.slice(0,-s.length)}return w}
function toks(s){return (s.toLowerCase().replace(/[’']/g,"").match(/[a-z0-9]+/g)||[]).map(stem)}
I.forEach(function(p){p.T=toks(p.t);p.G=toks(p.g);p.D=toks(p.d);p.B=toks(p.b)});
function cnt(a,q){var c=0;for(var k=0;k<a.length;k++)if(a[k].indexOf(q)===0)c++;return c}
function score(p,qs){var s=0;for(var k=0;k<qs.length;k++){var q=qs[k],h=cnt(p.T,q)*8+cnt(p.G,q)*6+cnt(p.D,q)*3+cnt(p.B,q);if(!h)return 0;s+=h}return s}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
function card(p){return '<a class="bl-card" style="border-left:12px solid '+p.c+'" href="/blog/'+p.s+'/"><div class="bl-card-body"><div class="bl-kicker" style="margin:0">'+esc(p.k)+' &middot; '+p.dt+'</div><div class="bl-card-title">'+esc(p.t)+'</div><p>'+esc(p.d)+'</p></div></a>'}
function snip(p,q){var b=p.b,lo=b.toLowerCase(),j=lo.indexOf(q);if(j<0)return esc(p.d.slice(0,90));var s=Math.max(0,j-30);return (s?"...":"")+esc(b.slice(s,j+60))+"..."}
function close(){L.hidden=true;i.setAttribute("aria-expanded","false");sel=-1}
function run(){var raw=i.value.trim().toLowerCase(),qs=toks(raw);if(!qs.length){r.hidden=true;all.hidden=false;n.textContent="";close();return}
cur=I.map(function(p){return[score(p,qs),p]}).filter(function(x){return x[0]>0}).sort(function(a,b){return b[0]-a[0]}).map(function(x){return x[1]});
n.textContent=cur.length?cur.length+(cur.length===1?" post matches":" posts match")+' "'+i.value.trim()+'"':'No posts match "'+i.value.trim()+'". Try specials, loyalty or duopoly.';
r.innerHTML=cur.map(card).join("");r.hidden=false;all.hidden=true;
var tagHits=[];I.forEach(function(p){p.g.split(" ").length;});
L.innerHTML=cur.slice(0,6).map(function(p,k){return '<li role="option" id="bs-o'+k+'" data-s="'+p.s+'"><small>'+esc(p.k)+'</small>'+esc(p.t)+'<small style="text-transform:none;letter-spacing:0;font-weight:400;margin:3px 0 0">'+snip(p,raw.split(" ")[0])+'</small></li>'}).join("");
L.hidden=!cur.length;i.setAttribute("aria-expanded",cur.length?"true":"false");sel=-1}
function hi(k){var o=L.querySelectorAll("li");o.forEach(function(x,j){x.setAttribute("aria-selected",j===k?"true":"false")});sel=k;if(o[k])i.setAttribute("aria-activedescendant",o[k].id)}
i.addEventListener("input",run);
i.addEventListener("keydown",function(ev){var o=L.querySelectorAll("li");if(ev.key==="ArrowDown"&&o.length){ev.preventDefault();hi((sel+1)%o.length)}else if(ev.key==="ArrowUp"&&o.length){ev.preventDefault();hi((sel-1+o.length)%o.length)}else if(ev.key==="Enter"){if(sel>=0&&o[sel]){ev.preventDefault();location.href="/blog/"+o[sel].dataset.s+"/"}else{close();i.blur()}}else if(ev.key==="Escape")close()});
L.addEventListener("mousedown",function(ev){var li=ev.target.closest("li");if(li){ev.preventDefault();location.href="/blog/"+li.dataset.s+"/"}});
document.addEventListener("click",function(ev){if(!ev.target.closest(".bl-ac"))close()});
var q=new URLSearchParams(location.search).get("q");if(q){i.value=q;run();close()}})();
