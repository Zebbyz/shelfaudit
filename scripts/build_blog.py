import json, re, os, html, datetime, sys
sys.path.insert(0, os.path.dirname(__file__))
from blog_posts import POSTS as ALL_POSTS
from zoneinfo import ZoneInfo
TODAY = os.environ.get("BLOG_TODAY") or datetime.datetime.now(ZoneInfo("Pacific/Auckland")).date().isoformat()
POSTS = [p for p in ALL_POSTS if p["date"] <= TODAY]
OUT = os.path.join(os.path.dirname(__file__), "..", "public", "blog")
import shutil
for _d in os.listdir(OUT) if os.path.isdir(OUT) else []:
    if os.path.isdir(os.path.join(OUT, _d)): shutil.rmtree(os.path.join(OUT, _d))
PAL = ["#ff4a36","#3ddc97","#ffe14a","#5aa9ff","#c58bff","#ff8a3d","#2ec4b6","#ff5fa2","#a3e635","#f59e0b","#60a5fa","#f472b6","#34d399","#fbbf24","#e879f9","#94a3b8","#fb7185","#22d3ee"]
tags = []
for p in POSTS:
    for t in p["tags"]:
        if t not in tags: tags.append(t)
COL = {t: PAL[i % len(PAL)] for i, t in enumerate(tags)}
def slug(t): return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
def fd(d): return datetime.date.fromisoformat(d).strftime("%-d %b %Y")
e = html.escape
HEAD = """<!doctype html><html lang="en-NZ"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="{desc}"><link rel="canonical" href="https://intel.shelfaudit.pages.dev{path}"><link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700;900&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet"><link rel="stylesheet" href="/styles.css"><link rel="stylesheet" href="/blog/blog.css"></head><body>
<header class="top"><a href="/" class="brand" aria-label="Shelf Audit home"><span class="bw"><span>Shelf Audit</span><small class="tagline">Daily oversight of the largest market in NZ</small></span></a>
<nav class="bnav"><a href="/">Watchdog</a><a href="/#/join">Members</a><a href="/monopolies/">Who controls NZ</a><a href="/ownership/">Ownership</a><a href="/blog/" class="on">Blog</a><a href="/plans/" class="nav-ice">For supermarkets</a></nav></header>"""
FOOT = """<footer class="foot"><div class="foot-in"><div><strong>Shelf Audit</strong><p>An independent price watchdog for New Zealand shoppers. Not affiliated with any supermarket.</p></div>
<div class="foot-links"><a href="/">Shopper watchdog</a><a href="/app/">Shopper app</a><a href="/searchlight/">Searchlight</a><a href="/monopolies/">Who controls NZ</a><a href="/ownership/">Ownership</a><a href="/blog/">Blog</a><a href="/plans/">Price Pilot plans</a></div>
<p class="fine">Concept, design and execution by <a href="https://unlimitedpotential.co.nz" rel="noopener">Unlimited Potential</a></p></div></footer>
</body></html>"""
def card(p):
    t = p["tags"][0]
    return (f'<a class="bl-card" style="border-left:12px solid {COL[t]}" href="/blog/{p["slug"]}/"><div class="bl-card-body">'
            f'<div class="bl-kicker" style="margin:0">{e(t)} &middot; {fd(p["date"])}</div><div class="bl-card-title">{e(p["title"])}</div><p>{e(p["summary"])}</p></div></a>')
def chips(sel=None):
    return '<nav class="bl-chips" aria-label="Blog tags">' + "".join(
        f'<a class="tc{" on" if t==sel else ""}" style="background:{COL[t]};border-color:{COL[t]}" href="/blog/tag/{slug(t)}/">{e(t)}</a>' for t in tags) + "</nav>"
def text(h): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()
idx = [dict(s=p["slug"], t=p["title"], g=" ".join(p["tags"]), d=p["summary"], b=text(p["body"]), k=p["tags"][0], c=COL[p["tags"][0]], dt=fd(p["date"])) for p in POSTS]
SEARCH = """<div class="bl-search" role="search"><label for="bs" class="sr">Search the blog</label><div class="bl-ac"><input id="bs" type="search" placeholder="Search the blog, eg specials, loyalty, self-checkout" autocomplete="off" enterkeyhint="search" role="combobox" aria-expanded="false" aria-controls="bs-list" aria-autocomplete="list"><ul id="bs-list" role="listbox" hidden></ul></div><p id="bs-n" aria-live="polite"></p></div><div class="bl-grid" id="bs-r" hidden></div>"""
JS = "<script>window.BLOG_IDX=" + json.dumps(idx) + ";</script><script src=\"/blog/search.js\"></script>"
def write(path, s):
    os.makedirs(os.path.dirname(path), exist_ok=True); open(path, "w").write(s)
posts = sorted(POSTS, key=lambda p: p["date"], reverse=True)
intro = '<div class="bl-hero"><div class="bl-kicker">Blog &middot; Shelf Audit</div><h1>How the squeeze reaches your pocket</h1><p class="bl-lede">Sourced, dated facts on how New Zealand supermarkets push costs further into your life. Every claim links to its source. Opinion is labelled.</p></div>'
write(f"{OUT}/index.html", HEAD.format(title="Blog: how the supermarket squeeze reaches your pocket | Shelf Audit", desc="Sourced facts on NZ supermarket pricing, the duopoly, specials, shrinkflation, loyalty data, self-checkout and more.", path="/blog/")
      + '<main class="bl">' + SEARCH + intro + chips() + '<div class="bl-grid" id="bl-all">' + "".join(card(p) for p in posts) + "</div></main>" + FOOT.replace("</body>", JS + "</body>"))
for t in tags:
    ps = [p for p in posts if t in p["tags"]]
    write(f"{OUT}/tag/{slug(t)}/index.html", HEAD.format(title=f"{e(t)} | Shelf Audit blog", desc=f"Shelf Audit posts tagged {e(t)}.", path=f"/blog/tag/{slug(t)}/")
          + f'<main class="bl"><div class="bl-hero"><div class="bl-kicker"><a href="/blog/">Blog</a> &middot; Tag</div><h1>{e(t)}</h1></div>' + chips(t)
          + '<div class="bl-grid">' + "".join(card(p) for p in ps) + "</div></main>" + FOOT)
for i, p in enumerate(posts):
    src = "".join(f'<li><a href="{e(u)}" rel="noopener" target="_blank">{e(n)}</a>, {e(d)}</li>' for n, u, d in p["sources"])
    tg = " ".join(f'<a href="/blog/tag/{slug(t)}/" style="background:{COL[t]}">{e(t)}</a>' for t in p["tags"])
    more = [q for q in posts if q is not p][:3] if False else [posts[(i + k) % len(posts)] for k in (1, 2, 3)]
    write(f"{OUT}/{p['slug']}/index.html", HEAD.format(title=f"{e(p['title'])} | Shelf Audit", desc=e(p["summary"]), path=f"/blog/{p['slug']}/")
          + f'<main class="bl"><article class="bl-post"><div class="bl-kicker"><a href="/blog/">Blog</a> &middot; {e(p["tags"][0])}</div><h1>{e(p["title"])}</h1>'
          + f'<p class="bl-meta">{fd(p["date"])} &middot; Shelf Audit</p><div class="bl-tags">{tg}</div><p class="bl-sum">{e(p["summary"])}</p>{p["body"]}'
          + f'<h2>Sources</h2><ol class="bl-src">{src}</ol></article><div class="bl-more"><div class="bl-kicker">More from the blog</div></div><div class="bl-grid">' + "".join(card(q) for q in more) + "</div></main>" + FOOT)
write(f"{OUT}/search.json", json.dumps(idx))
bad = [f for f in os.popen(f"grep -rl $'\u2014' {OUT}").read().split()]
print("posts", len(posts), "tags", len(tags), "emdash files", bad)
