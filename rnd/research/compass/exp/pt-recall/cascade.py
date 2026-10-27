import json, re, numpy as np
rows=[json.loads(l) for l in open("aug.jsonl")]; C=json.load(open("emb.json")); L=json.load(open(__import__("sys").argv[1] if len(__import__("sys").argv)>1 else "llm.json"))
h=json.load(open("../health-embed-v1/health-lr.v1.json")); w,b=np.array(h["w"]),h["b"]
pv=lambda t:(lambda v:1/(1+np.exp(-(v/np.linalg.norm(v))@w-b)))(np.array(C[t]))
en=lambda q:re.search(r"\b(the|my|what|should|is|how|i|a)\b",q.lower()) and not re.search(r"[ãõç]",q)
for r in rows: r["p"]=pv(r["q"]); r["llm"]=L[r["id"]]=="yes"
G={"mirror PT danger":lambda r:r["set"]=="mirror","eval PT danger":lambda r:r["set"]=="eval" and r["label"]=="danger" and not en(r["q"]),
   "eval EN danger":lambda r:r["set"]=="eval" and r["label"]=="danger" and en(r["q"]),"eval PT non-danger":lambda r:r["set"]=="eval" and r["label"]!="danger" and not en(r["q"]),
   "eval EN non-danger":lambda r:r["set"]=="eval" and r["label"]!="danger" and en(r["q"])}
rules={"v1 alone":lambda r:r["p"]>.5,"LLM alone":lambda r:r["llm"],"v1 OR LLM":lambda r:r["p"]>.5 or r["llm"],
 "cascade lo=.25":lambda r:r["p"]>.5 or (r["p"]>.25 and r["llm"]),"cascade lo=.15":lambda r:r["p"]>.5 or (r["p"]>.15 and r["llm"]),
 "EN:v1 / PT:v1 OR LLM":lambda r:r["p"]>.5 or (not en(r["q"]) and r["llm"])}
print(f"{'rule':24}"+"".join(f"{g[:18]:>20}" for g in G)+"   LLM calls")
for k,f in rules.items():
    calls=sum(1 for r in rows if r["set"]=="eval" and (("cascade" in k and r["p"]<=.5 and r["p"]>float(k.split('=')[1])) or ("LLM" in k and "OR" not in k) or (k=="v1 OR LLM") or (k.startswith("EN") and not en(r["q"]) and r["p"]<=.5)))
    print(f"{k:24}"+"".join(f"{sum(f(r) for r in rows if g(r)):>14}/{sum(1 for r in rows if g(r)):<5}" for g in G.values())+f"   {calls}/275")
print("p of LLM FPs:",[(r["id"],round(r["p"],2)) for r in rows if r["label"]!="danger" and r["llm"]])
print("p of v1 PT misses:",[(r["id"],round(r["p"],2),r["llm"]) for r in rows if r["label"]=="danger" and r["p"]<=.5])
