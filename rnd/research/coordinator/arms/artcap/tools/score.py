#!/usr/bin/env python3
"""ARTCAP scorer (criterion 4069ae83). python3 -I score.py -> ../artcap.json + table on stdout.
MAIN: chunklevel.py score() (92 keyed). ST: oracle fact chunk in kept/raw, own article kept (qrewrite score.py docId rule). Context = sum ceil(len(title+body)/4) over kept."""
import json, math, statistics as stt, os
A = "<workspace>/rnd/research/coordinator/arms"; AC = A + "/artcap"; CM = A + "/coverage-map"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
src = open(CM + "/tools/chunklevel.py").read(); src = src[:src.index("ARMS = {")]
G = {"__name__": "cl"}; exec(compile(src, "chunklevel.py", "exec"), G)
OWN = json.load(open(A + "/packproof/in/own.json")); ITEMS = {x["id"]: x["pack"] for x in json.load(open(A + "/packproof/in/items.json"))["items"]}
OF = json.load(open(A + "/oracle-st/tools/oracle-facts.json"))
D = {x["id"]: x for x in json.load(open(A + "/h8st/tools/diag/diag137.json"))}
CAP37 = sorted(i for i, x in D.items() if x.get("best") and x["best"]["cls"] == "article_cap" and not x["S_kept_ST2"])
OTH19 = sorted(i for i, x in D.items() if x.get("best") and x["best"]["cls"] == "article_found_other_chunk" and not x["S_kept_ST2"])
assert len(CAP37) == 37 and len(OTH19) == 19
HP = {"qa-health-se", "boar-firstaid-en", "boar-medlineplus-en"}; hmain = lambda i: i.startswith(("lan-hlt-", "vit-hlt-", "dng-"))
norm = lambda c: (c or "").replace("pack:local-", "pack:")
tok = lambda k: sum(math.ceil(len(c.get("title", "") + c.get("body", "")) / 4) for c in k)
def ctx(rows):
    t = [tok(r.get("keptFull") or []) for r in rows.values() if r.get("keptFull")]
    return dict(p50=stt.median(t) if t else 0, total=sum(t), n=len(t))
def main(lab):
    f = f"{AC}/replays/main.{lab}.jsonl"; s = G["score"](f); rows = {r["id"]: r for r in rd(f)}
    return s, rows
def st(lab):
    rows = {r["id"]: r for r in rd(f"{AC}/replays/st.{lab}.jsonl")}; out = {}
    for i, r in rows.items():
        p = ITEMS[i]; fc = set(OF[i]["fact_chunks"]); kept = r.get("keptFull") or []; raw = r.get("rawFull") or []
        own = lambda c: any((c.get("docId") or "") == f"pack:local-{p}:a{a['article']}" for a in OWN[i])
        out[i] = dict(fact=any(norm(c["chunkId"]) in fc for c in kept), fact_raw=any(norm(c["chunkId"]) in fc for c in raw),
                      own=any(own(c) for c in kept), pack=p, keptids=[c["chunkId"] for c in kept])
    return out, rows
R = {"criterion": "4069ae83dfe0bc2876e0fcc78b6e8bf8c45e137f38aab6d59c58c7510d51db14", "cap37": CAP37, "oth19": OTH19, "arms": {}}
mb, mbr = main("base"); sb, sbr = st("base")
cb_m, cb_s = ctx(mbr), ctx(sbr)
for lab in ["base", "cap4", "capfact", "cap4lead"]:
    if not os.path.exists(f"{AC}/replays/main.{lab}.jsonl") or not os.path.exists(f"{AC}/replays/st.{lab}.jsonl"): continue
    m, mr = main(lab); s, sr = st(lab)
    if len(mr) != 97 or len(sr) != 180: print(lab, "incomplete", len(mr), len(sr)); continue
    ch = lambda x, i: bool(x[i] and x[i]["chunk"])
    mg = [i for i in m if ch(m, i) and not ch(mb, i)]; ml = [i for i in m if ch(mb, i) and not ch(m, i)]
    mchg = [i for i in mr if [c["chunkId"] for c in mr[i].get("keptFull") or []] != [c["chunkId"] for c in mbr[i].get("keptFull") or []]]
    sg = [i for i in s if s[i]["fact"] and not sb[i]["fact"]]; sl = [i for i in s if sb[i]["fact"] and not s[i]["fact"]]
    cm, cs = ctx(mr), ctx(sr)
    e = dict(main=dict(chunk=sum(ch(m, i) for i in m), cm=sum(ch(m, i) and m[i]["set"] == "cm" for i in m), v01=sum(ch(m, i) and m[i]["set"] == "v0.1" for i in m),
                       art=sum(bool(m[i] and m[i]["art"]) for i in m), gained=mg, lost=ml, health_lost=[i for i in ml if hmain(i)], changed=len(mchg), changed_ids=mchg,
                       ctx_p50=cm["p50"], ctx_p50_ratio=round(cm["p50"] / cb_m["p50"], 3), ctx_total_ratio=round(cm["total"] / cb_m["total"], 3),
                       mean_kept=round(sum(len(r.get("keptFull") or []) for r in mr.values()) / 97, 2), wall_p50=stt.median([r.get("wallMs") or 0 for r in mr.values()])),
             st=dict(fact=sum(v["fact"] for v in s.values()), fact_raw=sum(v["fact_raw"] for v in s.values()), own=sum(v["own"] for v in s.values()),
                     gained=sg, lost=sl, health_lost=[i for i in sl if s[i]["pack"] in HP], changed=sum(s[i]["keptids"] != sb[i]["keptids"] for i in s),
                     ctx_p50=cs["p50"], ctx_p50_ratio=round(cs["p50"] / cb_s["p50"], 3), ctx_total_ratio=round(cs["total"] / cb_s["total"], 3),
                     mean_kept=round(sum(len(r.get("keptFull") or []) for r in sr.values()) / 180, 2), wall_p50=stt.median([r.get("wallMs") or 0 for r in sr.values()]),
                     cap37=[i for i in CAP37 if s[i]["fact"]], oth19=[i for i in OTH19 if s[i]["fact"]],
                     by_pack={p: sum(s[i]["fact"] for i in s if s[i]["pack"] == p) for p in sorted(set(ITEMS.values()))}))
    b = R["arms"].get("base")
    if b:
        e["gate"] = dict(main_facts=e["main"]["chunk"] >= b["main"]["chunk"] + 6, st_fact=e["st"]["fact"] >= b["st"]["fact"] + 25,
                         health0=not e["main"]["health_lost"], ctx=e["main"]["ctx_p50_ratio"] <= 1.15)
        g = e["gate"]; g["PASS"] = (g["main_facts"] or g["st_fact"]) and g["health0"] and g["ctx"]
    R["arms"][lab] = e
    M, S = e["main"], e["st"]
    print(f"{lab:9s} MAIN {M['chunk']} (cm {M['cm']} v01 {M['v01']}) +{len(M['gained'])}/-{len(M['lost'])} hl {M['health_lost']} chg {M['changed']} ctx p50 {M['ctx_p50']} x{M['ctx_p50_ratio']} tot x{M['ctx_total_ratio']} | "
          f"ST fact {S['fact']} raw {S['fact_raw']} own {S['own']} +{len(S['gained'])}/-{len(S['lost'])} hl {S['health_lost']} ctx x{S['ctx_p50_ratio']} tot x{S['ctx_total_ratio']} cap37 {len(S['cap37'])} oth19 {len(S['oth19'])} gate {e.get('gate',{}).get('PASS')}")
json.dump(R, open(AC + "/artcap.json", "w"), indent=1)
