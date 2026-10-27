#!/usr/bin/env python3
"""RETBENCH v1 scorer (0 LLM). python3 -I score.py <name> [--base base] -> aggregates/<name>.json + one line on stdout.
MAIN: coverage-map/tools/chunklevel.py score() (fact inside ONE kept chunk body; 92 keyed). ST: own article raw/kept, oracle fact chunk kept/raw (items/st180.json).
TOPICS: an expected title (any group) among kept titles (items/topics27.json). F8 / LS: turn-1 source kept on turn 1 and on turn 2 (uxmatrix/u5 score_u5.py rules).
Context tokens = sum ceil(len(title+body)/4) over kept chunks (items with >= 1 kept). Bytes/q = vector bytes read (RS_BYTES_LOG) / retrieving items. ms = wallMs."""
import json, sys, os, math, re, statistics as stt
A = "<workspace>/rnd/research/coordinator/arms"; RB = A + "/retbench"; CM = A + "/coverage-map"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
src = open(CM + "/tools/chunklevel.py").read(); src = src[:src.index("ARMS = {")]
G = {"__name__": "cl"}; exec(compile(src, "chunklevel.py", "exec"), G)
IT = {n: json.load(open(f"{RB}/items/{n}.json")) for n in ("main92", "st180", "topics27", "f8-48", "longsession")}
MH = {x["id"] for x in IT["main92"] if x["health"]}; ST = {x["id"]: x for x in IT["st180"]}; TP = {x["key"]: x for x in IT["topics27"]}
F8 = {x["id"]: x for x in IT["f8-48"]}; LS = {x["id"]: x for x in IT["longsession"]}
norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", (s or "").lower())).strip()
nid = lambda c: (c or "").replace("pack:local-", "pack:")
tok = lambda k: sum(math.ceil(len(c.get("title", "") + c.get("body", "")) / 4) for c in k)
def pctl(v, q=0.5): return stt.median(v) if v else None
def rows(name, L):
    f = f"{RB}/replays/{name}/{L}.jsonl"; return {r["id"]: r for r in rd(f)} if os.path.exists(f) else None
def bytes_q(name, L, rr):
    f = f"{RB}/replays/{name}/{L}.bytes"; n = sum(1 for r in rr.values() if r.get("raw"))
    tot = sum(json.loads(l)["b"] for l in open(f)) if os.path.exists(f) else 0
    by = {}
    if os.path.exists(f):
        for l in open(f): d = json.loads(l); by[d["k"]] = by.get(d["k"], 0) + d["b"]
    return dict(per_q=round(tot / n) if n else None, by_kind={k: round(v / n) for k, v in by.items()} if n else {}, retrieving=n)
def ctx(rr):
    t = [tok(r.get("keptFull") or []) for r in rr.values() if r.get("keptFull")]
    return dict(p50=pctl(t), total=sum(t), n=len(t))
def ms(rr): return pctl([r["wallMs"] for r in rr.values() if r.get("wallMs") is not None])
def score(name):
    out = {"name": name}
    m = rows(name, "main")
    if m and len(m) == 97:
        s = G["score"](f"{RB}/replays/{name}/main.jsonl")
        ch = {i: bool(v and v["chunk"]) for i, v in s.items()}
        out["main"] = dict(facts=sum(ch.values()), cm=sum(ch[i] and s[i]["set"] == "cm" for i in s), v01=sum(ch[i] and s[i]["set"] == "v0.1" for i in s),
                           art=sum(bool(v and v["art"]) for v in s.values()), facts_ids=sorted(i for i in ch if ch[i]), ctx=ctx(m), ms_p50=ms(m), bytes=bytes_q(name, "main", m),
                           mean_kept=round(sum(len(r.get("keptFull") or []) for r in m.values()) / 97, 2), kept_ids={i: [c["chunkId"] for c in r.get("keptFull") or []] for i, r in m.items()},
                           raw_titles={i: [c["title"] for c in r.get("raw") or []] for i, r in m.items()})
    st = {}
    for g in ("on-k13", "on-k13+qa-bitcoin-se", "on-k13+qa-ethereum-se"):
        r = rows(name, f"st.{g}")
        if r: st.update(r)
    if len(st) == 180:
        per = {}
        for i, r in st.items():
            x = ST[i]; kept = r.get("keptFull") or []; raw = r.get("rawFull") or r.get("raw") or []
            own = lambda c: (c.get("docId") or "") in x["own_docs"]
            per[i] = dict(own_raw=any(own(c) for c in raw), own_kept=any(own(c) for c in kept), fact=any(nid(c.get("chunkId")) in x["fact_chunks"] for c in kept),
                          fact_raw=any(nid(c.get("chunkId")) in x["fact_chunks"] for c in raw), n=len(kept), nown=sum(own(c) for c in kept), pack=x["pack"], health=x["health"],
                          kept=[c.get("chunkId") for c in kept])
        packs = sorted({v["pack"] for v in per.values()})
        crowd = {p: (lambda nk, no: round(1 - no / nk, 3) if nk else None)(sum(v["n"] for v in per.values() if v["pack"] == p), sum(v["nown"] for v in per.values() if v["pack"] == p)) for p in packs}
        out["st"] = dict(own_raw=sum(v["own_raw"] for v in per.values()), own_kept=sum(v["own_kept"] for v in per.values()), fact=sum(v["fact"] for v in per.values()),
                         fact_raw=sum(v["fact_raw"] for v in per.values()), crowd=crowd, crowd_all=round(1 - sum(v["nown"] for v in per.values()) / max(1, sum(v["n"] for v in per.values())), 3),
                         fact_ids=sorted(i for i in per if per[i]["fact"]), own_ids=sorted(i for i in per if per[i]["own_kept"]), health_fact_ids=sorted(i for i in per if per[i]["fact"] and per[i]["health"]),
                         ctx=ctx(st), ms_p50=ms(st), mean_kept=round(sum(v["n"] for v in per.values()) / 180, 2), kept_ids={i: v["kept"] for i, v in per.items()})
    t = rows(name, "topics")
    if t and len(t) == 27:
        hit = {k: any(c["title"] in {tt for g in TP[k]["expected_groups"] for tt in g} for c in (t[k].get("keptFull") or [])) for k in TP}
        hr = {k: any(c["title"] in {tt for g in TP[k]["expected_groups"] for tt in g} for c in (t[k].get("rawFull") or t[k].get("raw") or [])) for k in TP}
        out["topics"] = dict(expected_in_kept=sum(hit.values()), expected_in_raw=sum(hr.values()), ids=sorted(k for k in hit if hit[k]), health_ids=sorted(k for k in hit if hit[k] and TP[k]["health"]))
    f = rows(name, "f8")
    if f and len(f) == 96:
        fh = lambda lst, i: any(norm(F8[i]["gold_quote"]) in norm(c["title"] + " " + c["body"]) for c in lst)
        K1 = [i for i in F8 if fh(f[F8[i]["turn1"]]["keptFull"], i)]; S = [i for i in K1 if fh(f[i]["keptFull"], i)]
        off = [sum((c.get("docId") != F8[i]["gold_doc"]) for c in f[i]["keptFull"]) for i in F8]; nk = [len(f[i]["keptFull"]) for i in F8]
        out["f8"] = dict(K1=len(K1), survived=len(S), K2=sum(fh(f[i]["keptFull"], i) for i in F8), survived_ids=S, offsubject_t2=round(sum(off) / max(1, sum(nk)), 3))
    l = rows(name, "ls")
    if l and len(l) == 50:
        refs = lambda i: [x.lower() for x in LS[i]["referent"]]
        lh = lambda lst, i: bool(refs(i)) and any(x in " ".join((c["title"] + " " + c["body"]).lower() for c in lst) for x in refs(i))
        K1 = [i for i in LS if lh(l[l[i]["prevId"]]["keptFull"], i)]; S = [i for i in K1 if lh(l[i]["keptFull"], i)]
        out["ls"] = dict(K1=len(K1), survived=len(S), survived_ids=S)
    return out
def compare(o, b):
    d = {}
    if "main" in o and "main" in b:
        g = sorted(set(o["main"]["facts_ids"]) - set(b["main"]["facts_ids"])); lo = sorted(set(b["main"]["facts_ids"]) - set(o["main"]["facts_ids"]))
        d["main"] = dict(gained=g, lost=lo, health_lost=[i for i in lo if i in MH], changed=sum(o["main"]["kept_ids"][i] != b["main"]["kept_ids"][i] for i in b["main"]["kept_ids"]),
                         ctx_p50_x=round(o["main"]["ctx"]["p50"] / b["main"]["ctx"]["p50"], 3), ctx_total_x=round(o["main"]["ctx"]["total"] / b["main"]["ctx"]["total"], 3),
                         bytes_x=round(o["main"]["bytes"]["per_q"] / b["main"]["bytes"]["per_q"], 3) if b["main"]["bytes"]["per_q"] else None)
    if "st" in o and "st" in b:
        lo = sorted(set(b["st"]["fact_ids"]) - set(o["st"]["fact_ids"]))
        d["st"] = dict(fact_gained=sorted(set(o["st"]["fact_ids"]) - set(b["st"]["fact_ids"])), fact_lost=lo, health_lost=[i for i in lo if ST[i]["health"]],
                       own_lost=sorted(set(b["st"]["own_ids"]) - set(o["st"]["own_ids"])), changed=sum(o["st"]["kept_ids"][i] != b["st"]["kept_ids"][i] for i in b["st"]["kept_ids"]),
                       ctx_p50_x=round(o["st"]["ctx"]["p50"] / b["st"]["ctx"]["p50"], 3))
    if "topics" in o and "topics" in b:
        lo = sorted(set(b["topics"]["ids"]) - set(o["topics"]["ids"])); d["topics"] = dict(lost=lo, gained=sorted(set(o["topics"]["ids"]) - set(b["topics"]["ids"])), health_lost=[k for k in lo if TP[k]["health"]])
    hl = d.get("main", {}).get("health_lost", []) + d.get("st", {}).get("health_lost", []) + d.get("topics", {}).get("health_lost", [])
    d["health_losses"] = len(hl); d["health_lost_ids"] = hl
    return d
if __name__ == "__main__":
    name = sys.argv[1]; base = sys.argv[sys.argv.index("--base") + 1] if "--base" in sys.argv else "base"
    o = score(name)
    bf = f"{RB}/aggregates/{base}.json"
    if name != base and os.path.exists(bf): o["vs_base"] = compare(o, json.load(open(bf)))
    json.dump(o, open(f"{RB}/aggregates/{name}.json", "w"), indent=1)
    M, S, T, F = o.get("main", {}), o.get("st", {}), o.get("topics", {}), o.get("f8", {})
    print(name, "MAIN", M.get("facts"), "ST own", S.get("own_kept"), "fact", S.get("fact"), "TOPICS", T.get("expected_in_kept"), "F8", F.get("survived"), "/", F.get("K1"), "LS", o.get("ls", {}).get("survived"),
          "ctx", M.get("ctx", {}).get("p50"), "bytes/q", M.get("bytes", {}).get("per_q"), "ms", M.get("ms_p50"), "vs", json.dumps({k: (v if not isinstance(v, dict) else {kk: (len(vv) if isinstance(vv, list) else vv) for kk, vv in v.items()}) for k, v in o.get("vs_base", {}).items()}))
