import json, numpy as np, sys
rows=[json.loads(l) for l in open("aug.jsonl")]; C=json.load(open("emb.json"))
def head(f):
    h=json.load(open(f)); return np.array(h["w"]), h["b"]
def p(text, w, b):
    v=np.array(C[text]); v/=np.linalg.norm(v); return 1/(1+np.exp(-(v@w+b)))
for name,f in [("v0","../health-embed/health-lr.v0.json"),("v1","../health-embed-v1/health-lr.v1.json")]:
    w,b=head(f)
    for r in rows: r[name+"_raw"]=p(r["q"],w,b); r[name+"_aug"]=p(r["aug"],w,b); r[name+"_max"]=max(r[name+"_raw"],r[name+"_aug"])
    groups={"mirror PT danger (28)":lambda r:r["set"]=="mirror","eval PT danger":lambda r:r["set"]=="eval" and r["label"]=="danger" and r["pt"] and r["en"]!="" or (r["set"]=="eval" and r["label"]=="danger" and r["id"] in ("vit-hm-003","vit-hm-004","vit-hm-011","vit-hm-015","vit-h1-017")) ,
            "eval EN danger":lambda r:r["set"]=="eval" and r["label"]=="danger" and not r["pt"],
            "eval PT non-danger":lambda r:r["set"]=="eval" and r["label"]!="danger" and r["pt"],"eval EN non-danger":lambda r:r["set"]=="eval" and r["label"]!="danger" and not r["pt"]}
    print(f"== head {name}")
    for g,f2 in groups.items():
        sub=[r for r in rows if f2(r)]
        print(f"  {g:24} n={len(sub):3} "+"  ".join(f"{m}: {sum(r[name+'_'+m]>.5 for r in sub):3}" for m in ["raw","aug","max"]))
w,b=head("../health-embed-v1/health-lr.v1.json")
print("\nv1 mirror misses (raw→aug):"); [print(f"  {r['v1_raw']:.2f}→{r['v1_aug']:.2f} {r['id']:20} {r['en']}") for r in rows if r["set"]=="mirror" and r["v1_max"]<=.5]
print("v1 aug-induced FPs:"); [print(f"  {r['v1_raw']:.2f}→{r['v1_aug']:.2f} {r['id']} {r['q'][:60]} ({r['en']})") for r in rows if r["label"]!="danger" and r["v1_aug"]>.5 and r["v1_raw"]<=.5]
