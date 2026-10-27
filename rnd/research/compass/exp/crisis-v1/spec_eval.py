import json, sys
sys.path.insert(0,"../crisis"); from detect import T2, EXCLUDE
import method_backstop as m
R=json.load(open("rows.json")); P=json.load(open("emb_p.json")); L4=json.load(open("llm4b.json")); L15=json.load(open("llm15.json"))
def android(r):
    if m.METHOD.search(r["q"]): return "card"
    if P[r["id"]]>=0.20 and L4[r["id"]]=="yes": return "card"
    return "footer" if (T2.search(r["q"]) and not EXCLUDE.search(r["q"])) else "none"
def iphone(r):
    if m.METHOD.search(r["q"]): return "card"
    p=P[r["id"]]
    if p>=0.30 and L15[r["id"]]=="yes": return "card" if p>=0.60 else "footer"
    return "footer" if (T2.search(r["q"]) and not EXCLUDE.search(r["q"])) else "none"
for name,f in (("Android 4B",android),("iPhone 1.5B",iphone)):
    for s in ("train","dev","neg"):
        S=[r for r in R if (r["set"] in ("eval","faqa")) if s=="neg"] if s=="neg" else [r for r in R if r["set"]==s]
        c=lambda y,o: sum(1 for r in S if r["y"]==y and f(r)==o)
        print(f"{name:11} {s:5} crisis: card {c(1,'card')} footer {c(1,'footer')} none {c(1,'none')} | non-crisis: card {c(0,'card')} footer {c(0,'footer')} none {c(0,'none')}")
