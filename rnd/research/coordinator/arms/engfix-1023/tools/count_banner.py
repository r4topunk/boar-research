import json, sys, re, collections
BANNER = "Not found in this phone's offline library"
STOP = set("the a an of and or in on to for is are was were how why what which who when does do did with from by as at it its their they this that be vs versus between compare explain".split())
def words(s): return {w for w in re.findall(r"[a-z]+", s.lower()) if len(w) > 3 and w not in STOP}
for path in sys.argv[1:]:
    c = collections.Counter(); rows = []
    for l in open(path):
        r = json.loads(l); t = (r.get("answer") or {}).get("text") or ""
        kept = r["retrieval"]["kept"]; codes = r["route"]["reasonCodes"]
        rel = [k.split("released-")[1] for k in codes if "compact-decline-released-" in k]
        c["n"] += 1
        if not t.startswith(BANNER): continue
        c["banner"] += 1
        if not kept: c["banner_kept0"] += 1; rows.append((r["itemId"], 0, None, False, rel)); continue
        c["banner_kept>=1"] += 1
        mx = max(k["similarity"] or 0 for k in kept)
        if mx >= 0.7: c["banner_kept>=1_sim>=0.70"] += 1
        tw = words(r["question"]); title_hit = any(words(k["title"] or "") & tw for k in kept)
        if title_hit: c["banner_kept>=1_titlematch"] += 1
        for x in rel: c["rule:" + x] += 1
        rows.append((r["itemId"], len(kept), round(mx, 3), title_hit, rel))
    print(path.split("/")[-1], dict(c))
    for row in rows: print("  ", row)
