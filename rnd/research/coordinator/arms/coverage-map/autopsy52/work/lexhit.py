import json, re, os, sys, glob, unicodedata, importlib.util
CO="<workspace>/rnd/research/coordinator/"; R=CO+"arms/retrieve-sweep"; BE="<workspace>/boar-eval/bench/"
rd=lambda f:[json.loads(l) for l in open(f) if l.strip()]
src=open(R+"/tools/sweep.py").read().split("\n")
a=next(i for i,l in enumerate(src) if l.startswith("spec = importlib.util.spec_from_file_location")); b=next(i for i,l in enumerate(src) if l.startswith("FUN = json.load"))
exec("\n".join(src[a:b]))
Rw={json.loads(l)["id"]:json.loads(l) for l in open(CO+"arms/coverage-map/compose/replays/main.N10.gidf.jsonl") if l.strip()}
for i in sys.argv[1].split(","):
    r=Rw[i]; c=list({c["chunkId"]:c for c in r["rawFull"]+r["wideFull"]}.values())
    print(i, "all:", present(i,c))
    for x in c:
        q=QS[i]; s=share_st(q,[f"{x['title']}\n{x['body']}"]) if "selftest" in q else share_v01(q,[f"{x['title']}\n{x['body']}"])
        if s: print("  ",round(s,2),x["chunkId"],x["title"][:60])
    print("  facts:",[f["fact"] for f in QS[i]["selftest"]["in_pack_facts"]] if "selftest" in QS[i] else QS[i].get("grading"))
