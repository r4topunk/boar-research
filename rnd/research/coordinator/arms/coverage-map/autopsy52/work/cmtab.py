import json, re
C="<workspace>/rnd/research/coordinator/arms/coverage-map/"
L=json.load(open(C+"autopsy52/work/list52.json")); G=json.load(open(C+"autopsy52/work/gold_cm.json"))
R={json.loads(l)["id"]:json.loads(l) for l in open(C+"compose/replays/main.N10.gidf.jsonl") if l.strip()}
pk=lambda c: re.match(r"^pack:(?:local-)?([^:]+):", c["chunkId"]).group(1) if c["chunkId"].startswith("pack:") else c["chunkId"].split(":")[0]
ab={"qa-cooking-se":"CK","qa-money-se":"MN","wiki-vital5":"V5","boar-simplewiki-en":"SW","qa-travel-se":"TR","qa-health-se":"HS","qa-outdoors-se":"OD","boar-wikivoyage-en":"WV","boar-crypto":"CR","boar-firstaid-en":"FA","boar-medlineplus-en":"ML","boar-factbook":"FB","boar-visa-en":"VI"}
for i,g in G.items():
    r=R[i]; doc=f"pack:local-{g['pack']}:a{g['article_id']}"; gch={f"pack:local-{g['pack']}:{f['chunk_id']}" for f in g["facts"]}
    def pos(lst):
        a=[j for j,c in enumerate(lst) if c.get("docId")==doc]; c=[j for j,c in enumerate(lst) if c["chunkId"] in gch]
        return (a[0] if a else "-", c[0] if c else "-")
    own=g["pack"]
    comp=lambda lst: "".join(("o" if pk(c)==own and c.get("docId")!=doc else ("G" if c.get("docId")==doc else ab.get(pk(c),"?").lower() if c.get("matchType")=="semantic" else ab.get(pk(c),"?")))+" " for c in lst)
    rc=[x for x in r["reasonCodes"] if x.startswith(("grounding","context","headpass:budget","headpass:health"))]
    print(f"{i[3:]:18} {L[i]['stage']} k={r['k']} rawA/C={pos(r['rawFull'])} wideA/C={pos(r['wideFull'])} keptA/C={pos(r['keptFull'])} gch={[f['chunk_index'] for f in g['facts']]}/{g['n_chunks']}")
    print("    raw:",comp(r["rawFull"]),"| wide:",comp(r["wideFull"]),"| kept:",comp(r["keptFull"])," ",rc)
