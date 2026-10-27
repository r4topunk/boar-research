#!/usr/bin/env python3
"""PACKSHAPE diagnosis (0 LLM): per factbook self-test, the ON label (PACKPROOF), own article raw/kept, own fact chunk kept
(an in_pack_facts quote, normalised, inside one kept factbook chunk body of the own article), and the kept factbook chunks.
python3 -I diagnose.py [replay.jsonl] -> stdout + ../diagnose.json"""
import json, re, sys, unicodedata, importlib.util
CO = "<workspace>/rnd/research/coordinator/"; PP = CO + "arms/packproof/"; D = CO + "arms/packshape/"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
s = importlib.util.spec_from_file_location("agg0", PP + "tools/agg.py"); src = open(PP + "tools/agg.py").read()
g = {}; exec(src[:src.index("L = resolve(")], g)
L = g["resolve"](PP + "judge/labels.jsonl"); A = json.load(open(PP + "judge/answers.json"))
LA = {r["key"]: r["label"] for r in rd(PP + "judge/labels.jsonl") if r["call"] == "A" and r["ok"]}
ST = {r["id"]: r for r in rd("<workspace>/rnd/research/packs/selftest/boar-factbook.jsonl")}
def n2(x):
    x = unicodedata.normalize("NFKC", x or "").lower().replace("’", "'")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", x)).strip()
rep = sys.argv[1] if len(sys.argv) > 1 else CO + "arms/coverage-map/nowiki/replay/st.K13.on-k13.jsonl"
R = {r["id"]: r for r in rd(rep) if "factbook" in r["id"]}
PFX = "pack:local-boar-factbook:"
out = {}
for i in sorted(ST):
    st = ST[i]; aid = st["source"]["article_id"]; r = R[i]; doc = f"{PFX}a{aid}"
    raw = any(c.get("docId") == doc for c in (r.get("rawFull") or []))
    kept = [c for c in (r.get("keptFull") or []) if c["docId"] == doc]
    qs = [n2(f["quote"]) for f in st["in_pack_facts"]]
    fact = [c for c in kept if any(q and q in n2(c["body"]) for q in qs)]
    a = A.get(f"on|{i}"); lab = L.get(a["key"], (None,))[0] if a else None
    out[i] = dict(q=st["question"], cat=st["category"], title=st["source"]["title"], raw=raw, kept=bool(kept), fact=bool(fact), label=lab, labelA=LA.get(a["key"]) if a else None,
                  answer=a["text"] if a else None, facts=[(f["fact"], f["quote"], f["chunk_index"]) for f in st["in_pack_facts"]],
                  kept_fb=[dict(t=c["title"], b=c["body"][:400], own=c["docId"] == doc) for c in (r.get("keptFull") or []) if c["docId"].startswith(PFX)],
                  kept_all=[(c["docId"].split(":")[1], c["title"]) for c in (r.get("keptFull") or [])])
json.dump(out, open(D + "diagnose.json", "w"), indent=1)
for i, x in out.items():
    print(f"{i} raw={x['raw']:d} kept={x['kept']:d} fact={x['fact']:d} lab={x['label']} | {x['title']} | {x['cat']}")
print("raw", sum(x["raw"] for x in out.values()), "kept", sum(x["kept"] for x in out.values()), "fact", sum(x["fact"] for x in out.values()))
