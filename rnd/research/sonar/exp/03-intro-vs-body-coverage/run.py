"""Sonar exp-03: is the answer key of each bench-60 item in the vital5 intro of its reference Wikipedia article, or only
in the article body? Proxy for 'intro-only packs cap quality'. Answer key = the item's precheck must_any groups
(each group: any term matches, case-insensitive; must_k = groups required, default all). Full text = live Wikipedia
plaintext extract (fetched 2026-10-01, cached in fulltext/), intro = all wiki-vital5 chunks of that title (pack d3b87d56).
Read-only on rnd/bench and shared-data."""
import json, os, re, sqlite3, time, urllib.error, urllib.parse, urllib.request
Q = "<workspace>/rnd/bench/questions/v0/questions.public.jsonl"
V5 = sqlite3.connect("file:<workspace>/shared-data/packs/wiki-vital5.sqlite?mode=ro", uri=True)
os.makedirs("fulltext", exist_ok=True)
def full(title):
    p = f"fulltext/{re.sub(r'[^A-Za-z0-9]+','_',title)}.txt"
    if os.path.exists(p): return open(p).read()
    u = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({"action":"query","prop":"extracts","explaintext":1,"redirects":1,"titles":title,"format":"json"})
    req = urllib.request.Request(u, headers={"User-Agent": "BOAR-research-sonar/0.1 (offline RAG coverage study)"})
    for attempt in range(6):
        try:
            d = json.load(urllib.request.urlopen(req, timeout=30)); break
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 5: raise
            time.sleep(int(e.headers.get("Retry-After") or 0) or 5 * 2 ** attempt)
    time.sleep(2)
    t = "\n".join(pg.get("extract","") for pg in d["query"]["pages"].values())
    open(p, "w").write(t); return t
def intro(title):
    rows = V5.execute("SELECT body FROM chunks WHERE title = ? COLLATE NOCASE", (title,)).fetchall()
    return None if not rows else "\n".join(r[0] for r in rows)
def norm(s): return re.sub(r"\s+", " ", s.lower().replace("’","'"))
def hits(text, groups):
    t = norm(text); return [any(norm(term) in t for term in g) for g in groups]
out = []
for line in open(Q):
    x = json.loads(line); gr = x["grading"]; groups = gr.get("must_any")
    titles = [urllib.parse.unquote(u.split("/wiki/")[1]).replace("_"," ") for u in x["reference_sources"] if "en.wikipedia.org/wiki/" in u]
    if not groups or not titles: continue
    k = gr.get("must_k", len(groups))
    it = [intro(t) for t in titles]; ft = [full(t) for t in titles]
    in_v5 = [t for t, b in zip(titles, it) if b is not None]
    ih = hits("\n".join(b for b in it if b), groups); fh = hits("\n".join(ft), groups)
    out.append({"id": x["id"], "cat": x["category"], "titles": titles, "in_vital5": in_v5, "k": k, "groups": len(groups),
                "intro_ok": sum(ih) >= k, "full_ok": sum(fh) >= k, "intro_groups": sum(ih), "full_groups": sum(fh)})
json.dump(out, open("coverage.json", "w"), indent=1)
n = len(out); io = sum(r["intro_ok"] for r in out); fo = sum(r["full_ok"] for r in out); nv = sum(bool(r["in_vital5"]) for r in out)
body_only = [r["id"] for r in out if r["full_ok"] and not r["intro_ok"]]
print(f"items scored {n}; any ref title in vital5: {nv}; key in vital5 intro: {io}; key in full article: {fo}; body-only: {len(body_only)}")
print("body-only:", ", ".join(body_only))
print("neither:", ", ".join(r["id"] for r in out if not r["full_ok"]))
import collections
c = collections.defaultdict(lambda: [0,0,0])
for r in out: c[r["cat"]][0]+=1; c[r["cat"]][1]+=r["intro_ok"]; c[r["cat"]][2]+=r["full_ok"]
for k,v in sorted(c.items()): print(f"  {k}: n={v[0]} intro={v[1]} full={v[2]}")
