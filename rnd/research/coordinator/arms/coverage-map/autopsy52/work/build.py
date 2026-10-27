import json, re, collections
C="<workspace>/rnd/research/coordinator/arms/coverage-map/"
L=json.load(open(C+"autopsy52/work/list52.json")); G=json.load(open(C+"autopsy52/work/gold_cm.json"))
P=json.load(open(C+"autopsy52/work/perpack_cm.json")); T=json.load(open(C+"autopsy52/work/termsim.json"))
R={json.loads(l)["id"]:json.loads(l) for l in open(C+"compose/replays/main.N10.gidf.jsonl") if l.strip()}
pk=lambda c: re.match(r"^pack:(?:local-)?([^:]+):", c["chunkId"]).group(1) if c["chunkId"].startswith("pack:") else c["chunkId"].split(":")[0]
TAU=0.77
def win(lst): return [dict(title=c["title"][:60], pack=pk(c), match=c.get("matchType"), chunk=c["chunkId"].split(":")[-1]) for c in lst[:4]]
out={}
HS=lambda r: "grounding:health-strict" in r["reasonCodes"]
for i,g in G.items():
    r=R[i]; doc=f"pack:local-{g['pack']}:a{g['article_id']}"; gch={f"pack:local-{g['pack']}:{f['chunk_id']}" for f in g["facts"]}
    pos=lambda lst,f: next((j for j,c in enumerate(lst) if f(c)),None)
    ra=pos(r["rawFull"],lambda c:c.get("docId")==doc); wa=pos(r["wideFull"],lambda c:c.get("docId")==doc)
    rc=pos(r["rawFull"],lambda c:c["chunkId"] in gch); wc=pos(r["wideFull"],lambda c:c["chunkId"] in gch)
    w=P[i]["wide"]; rw=P[i]["raw"]; own=g["pack"]
    rawpacks=[pk(c) for c in r["rawFull"]]; ownshare=sum(p==own for p in rawpacks)
    hs=HS(r)
    if ra is not None: st="S3"; sub="keep: health-strict filter (onHealthTopic) drops the gold thread in raw"
    elif wa is not None:
        st="S3"; sub=f"rank: gold thread at wide {wa}, outside engine k={r['k']} (" + ("same-pack threads outrank" if ownshare>=r['k']-1 else "other packs take raw slots") + ")"
    elif w["hitsA"]: st="S2"; sub="another pack outranks: gold in the pack's own hits, gidf fusion puts other packs first"
    elif w["poolA"]: st="S2"; sub=f"same-pack threads outrank: gold in bm25 pool at {w['poolA'][0]}/80, not in the pack's top hits"
    else: st="S2"; sub="lexical miss: gold thread not in the pack's bm25 pool (domain terms dropped by maxDf 2%)"
    if L[i]["stage"]=="S3" and ra is None and wa is None: sub="lexical S3 via a sibling thread holding 1 of 2 facts (wide-only); gold thread: "+ ("same-pack threads outrank" if w["poolA"] else "lexical miss")
    lead=w["leadA"]; lsim=w["leadS"]; minidx=min(f["chunk_index"] for f in g["facts"])
    f1 = isinstance(lead,int) and lead==0 and lsim>=TAU and minidx<=2
    f1b = isinstance(lead,int) and lead<=1 and lsim>=TAU and minidx<=2  # L=2 variant
    f2 = T[i]["df25"] is not None and T[i]["df25"]<3 and minidx<=2
    blocked = hs
    fixes=[]
    if hs: fixes.append("F3 HEALTH-NOSOURCE-FALLBACK")
    if f1: fixes.append("F1 SE-LEAD")
    elif f2: fixes.append("F2 SE-TERMS")
    elif f1b: fixes.append("F1 SE-LEAD (L=2)")
    cheapest = ("F3 then " if hs and (f1 or f2 or ra is not None) else "") + ("F1 SE-LEAD (top-1 lead thread, chunks 1-2)" if f1 else "F2 SE-TERMS (keep domain terms)" if f2 else "F1 L=2" if f1b else ("F3 alone" if i=="st-qa-cooking-se-005" else "none of F1-F3 (lead rank %s, lex df25 rank %s)"%(lead,T[i]["df25"])))
    out[i]=dict(set="cm", stage=st, label_stage=L[i]["stage"], sub_stage=sub, key_fact="; ".join(f["fact"] for f in g["facts"]),
        gold=dict(pack=own, article_id=g["article_id"], thread_title=g["title"][:80], chunk_ids=[f["chunk_id"] for f in g["facts"]], chunk_index=[f["chunk_index"] for f in g["facts"]], n_chunks=g["n_chunks"]),
        engine_k=r["k"], gold_article_rank=dict(raw=ra, wide=wa), gold_chunk_rank=dict(raw=rc, wide=wc),
        pack_search=dict(terms=w["terms"], pool_rank_article=(w["poolA"] or [None])[0], pack_hit_rank=dict(raw=(rw["hitsA"] or [None])[0], wide=(w["hitsA"] or [None])[0]), lead_rank=lead, lead_cos=lsim, lex_rank_if_maxdf25=T[i]["df25"], dropped_domain_terms=[s for s in T[i]["stems"] if s not in w["terms"]][:8]),
        health_strict=hs, winners_raw=win(r["rawFull"]), kept_n=len(r["keptFull"]),
        recover=dict(F1=bool(f1 and not hs), F1_with_F3=bool(f1), F1_L2=bool(f1b), F2=bool(f2 and not hs), F3_alone=(i=="st-qa-cooking-se-005")), cheapest_fix=cheapest)
V={
 "lan-ref-001":("S2","router: answer:facts-winner short-circuit (no retrieval; facts layer answers)","2017 Literature Nobel: Kazuo Ishiguro","wiki-vital5 Kazuo Ishiguro / simplewiki 234015","none: not a loss (facts layer)","C_router_shortcircuit"),
 "lan-rsn-007":("S2","router: answer:facts-dates short-circuit","Berlin Wall built 1961, fell 1989","simplewiki 43483 Berlin Wall","none: not a loss","C_router_shortcircuit"),
 "lan-exp-006":("S2","router: answer:facts-height short-circuit","Kilimanjaro 5,895 m dormant stratovolcano","wiki-vital5 40508","none: not a loss","C_router_shortcircuit"),
 "lan-ref-005":("S2","router: answer:facts-host short-circuit","2016 Summer Olympics host: Rio de Janeiro","wiki-vital5 78879 (side mention)","none: not a loss","C_router_shortcircuit"),
 "lan-cmp-001":("S2","router: answer:facts-population short-circuit","Brazil ~213M vs Russia ~144M people","factbook Brazil","none: not a loss","C_router_shortcircuit"),
 "lan-ref-004":("S2","router: answer:facts-area short-circuit","Iceland about 103,000 km2","pool FP (Bog, storm area chunks)","none: not a loss","C_router_shortcircuit"),
 "vit-trv-004":("S2","router: answer:calculator-travel-distance short-circuit","Paris-Rome walk ~1,400 km each way","pool FP (Rome/Old Rome bar list)","none: not a loss","C_router_shortcircuit"),
 "vit-cry-007":("S2","ruler FP: pool matched 'ACC' (sports, Bolivia party); d/acc not in any kit pack","d/acc = defensive/decentralized accelerationism (the post author)","none in kit","content (ship a the post author blog pack)","D_content_absent_ruler_fp"),
 "lan-cmp-003":("S2","ruler FP: area ranking table stripped at build; pool hits are single-word matches","Russia, Canada, US, China, Brazil, Australia bigger than India","none in kit (table)","content (keep list/table rows)","D_content_absent_ruler_fp"),
 "vit-cry-009":("S3","rank: Pectra 41393 (2048 ETH) at wide 5, outside k=4; named EIP-7251 takes 3 of 4 raw slots","Max effective balance 2048 ETH after EIP-7251","boar-crypto 41393 ethereum.org Pectra","per-article cap 2 on named hits (or A74 ground-dense)","F_engine_other"),
 "vit-hlt-001":("S3","keep: health-strict topic set empty for jellyfish (H2); fa-card fires","Vinegar, not fresh water, on jellyfish stings","wikivoyage 130055 Gulf Islands / 84351 Darwin","card answer wins (H2 rejected on safety); not a pack fix","F_engine_other"),
 "vit-hlt-002":("S3","keep: health-strict symptom-only topic + compression drop altitude chunks","Headache+nausea at altitude = AMS: stop ascending, descend","wikivoyage 7446/7462 Altitude sickness","card answer wins; not a pack fix","F_engine_other"),
 "vit-cry-010":("S3","keep: compressContext cut the fact sentence of kept 40957 (705->390 chars), budget binding","DAO fork; dissenters formed Ethereum Classic","boar-crypto 40957 Timeline of Ethereum forks","H3 tested 0/25; leave","F_engine_other"),
 "lan-cmp-002":("S2","dense dedup: Kodiak 80274 (weights) not retrieved; sibling 80275 at wide 3; dense append takes Polar bear 35004+35009","Polar bear males 350-700 kg vs grizzly 180-360 kg","wiki-vital5 80274 Kodiak bear","H1 per-article dense dedup","F_engine_other"),
 "lan-cmp-005":("S3","keep: onTopic proper-noun gate drops raw #2 Saltwater crocodile 70969 (no 'Nile' in text)","Saltwater croc males 6 m / 1,000+ kg, bigger than Nile","wiki-vital5 70969 Saltwater crocodile","compare questions: proper-noun gate per entity (any named entity in title)","E_keep_propernoun_gate"),
 "lan-rsn-005":("S3","keep: Amazon River 761 (raw #1) dropped by onSubject (proper noun 'Earth' absent); X1 Gilgit neighbours take budget","Nile vs Amazon length disputed by source/measurement","wiki-vital5 761 Amazon River","proper-noun gate exemption + H1 slate","E_keep_propernoun_gate"),
}
CLS_CM=lambda e: ("B_health_strict_misfire" if e["health_strict"] else
   "A1_se_lexical_miss" if e["sub_stage"].startswith("lexical miss") else
   "A2_se_same_pack_outranks" if ("same-pack" in e["sub_stage"]) else
   "A3_se_other_pack_outranks" if ("other pack" in e["sub_stage"] or "another pack" in e["sub_stage"]) else "A_other")
for i,e in out.items(): e["class"]=CLS_CM(e)
for i,(st,sub,fact,gold,fix,cls) in V.items():
    r=R[i]
    out[i]=dict(set="v0.1", stage=st, label_stage=L[i]["stage"], sub_stage=sub, key_fact=fact, gold=dict(where=gold), winners_raw=win(r["rawFull"]), kept_n=len(r["keptFull"]),
        reason=[x for x in r["reasonCodes"] if x.startswith(("answer:","grounding","context:","headpass:budget"))][:5], cheapest_fix=fix, **{"class": cls},
        recover=dict(F1=False,F1_with_F3=False,F1_L2=False,F2=False,F3_alone=False))
assert len(out)==52
c=collections.Counter(e["class"] for e in out.values()); print(sorted(c.items()))
for k in ("F1","F1_with_F3","F1_L2","F2","F3_alone"): print(k, sum(e["recover"][k] for e in out.values()))
print("F1|F2 (no health):", sum((e["recover"]["F1"] or e["recover"]["F2"]) for e in out.values()))
print("F1+F2+F3:", sum(((e["recover"]["F1_with_F3"] or (e["pack_search"]["lex_rank_if_maxdf25"] is not None and e["pack_search"]["lex_rank_if_maxdf25"]<3 and min(e["gold"]["chunk_index"])<=2) ) if e["set"]=="cm" else False) or e["recover"]["F3_alone"] for e in out.values()))
print(collections.Counter(e["sub_stage"].split(":")[0] for e in out.values() if e["set"]=="cm"))
json.dump(dict(meta=dict(arm="AUTOPSY52", date="2026-10-22", label="N10.gidf", tau_lead=TAU, note="0 LLM; ids + facts only, no question text; cm facts = selftest in_pack_facts; per-pack ranks from an instrumented replay (identity 52/52 vs compose/replays/main.N10.gidf.jsonl)"), items=out), open(C+"autopsy52/autopsy52.json","w"), indent=1)
for i,e in out.items():
    if e["set"]=="cm": print(f"{i[3:]:18} {e['stage']} {e['class'][:3]} lead={e['pack_search']['lead_rank']} pool={e['pack_search']['pool_rank_article']} df25={e['pack_search']['lex_rank_if_maxdf25']} | {e['sub_stage'][:70]} | {e['cheapest_fix'][:40]}")
