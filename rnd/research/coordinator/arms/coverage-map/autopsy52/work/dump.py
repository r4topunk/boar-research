import json, re, sys
C="<workspace>/rnd/research/coordinator/arms/coverage-map/"
L=json.load(open(C+"autopsy52/work/list52.json")); O=json.load(open(C+"aggregates/cm-oracle.json"))
R={}
for v in ("gidf","stock"):
    R[v]={json.loads(l)["id"]:json.loads(l) for l in open(C+f"compose/replays/main.N10.{v}.jsonl") if l.strip()}
pk=lambda c: re.match(r"^pack:(?:local-)?([^:]+):", c["chunkId"]).group(1) if c["chunkId"].startswith("pack:") else c["chunkId"].split(":")[0]
def fmt(lst, doc):
    s=[]
    for j,c in enumerate(lst):
        g="*" if doc and c.get("docId")==doc else " "
        s.append(f"{g}{j}:{pk(c)[:10]}|{c['title'][:38]}|{c.get('matchType','')[:3]}|{c['chunkId'].split(':')[-1]}|{round(c.get('score') or 0,2)}")
    return "\n      ".join(s)
only=sys.argv[1].split(",") if len(sys.argv)>1 else None
for i,e in L.items():
    if only and i not in only: continue
    if e["set"]!="cm" and not only: continue
    o=O.get(i); doc=f"pack:local-{o['pack']}:a{o['article_id']}" if o else None
    r=R["gidf"][i]
    print(f"== {i} {e['stage']} lex={e['lexstage']} or={e['oracle']} gold={o and o['article_id']} '{o and o['title']}'")
    print("  q:", (r["query"] or "")[:120])
    print("  RAW ", fmt(r["rawFull"],doc)); print("  WIDE", fmt(r["wideFull"],doc)); print("  KEPT", fmt(r["keptFull"],doc))
    print("  RC", [x for x in r["reasonCodes"] if not x.startswith(("task:","generate:","detector","instant","offer"))][:14])
