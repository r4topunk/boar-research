#!/usr/bin/env python3
"""COMBINED replay reads (0 LLM). python3 -I chunk_cmp.py -> ../replays-read.json
(1) chunk-level + article-level delivery of COMBINED (RD1 on) and COMBINED-off vs SEFIX-ALL (sefix/replays/main.F1F2F3F4.jsonl) and the K3 control replay B0, via tools/chunklevel.py's own scorer (exec of its definitions, same rules);
(2) switch-off identity (raw, wide12, kept chunk ids and reason codes) of COMBINED-off vs SEFIX-ALL over all 97; (3) which items RD1 changes in the context (keptFull order/content vs SEFIX-ALL), junk and kept tokens."""
import json, sys, os, collections
A = "<workspace>/rnd/research/coordinator/arms"; CM = A + "/coverage-map"; CB = CM + "/combined"
src = open(CM + "/tools/chunklevel.py").read(); cut = src.index("ARMS = {")
exec(src[:cut].replace('"""CHUNKLEVEL', '"""CHUNKLEVEL', 1))
arms = {"K3 control replay B0": A + "/retrieve-sweep/replay/B0.main.jsonl", "SEFIX-ALL replay": CM + "/sefix/replays/main.F1F2F3F4.jsonl",
        "COMBINED-off replay": CB + "/replays/main.off.jsonl", "COMBINED replay (RD1 on)": CB + "/replays/main.on.jsonl"}
RES = {k: score(v) for k, v in arms.items() if os.path.exists(v)}
def summ(s):
    f = lambda ids, k: sum(1 for i in ids if s[i] and s[i][k])
    return dict(art=f(ids92, "art"), chunk=f(ids92, "chunk"), art_cm=f(CMI, "art"), chunk_cm=f(CMI, "chunk"), chunk_cm_all=f(CMI, "chunk_all"), art_v01=f(V01, "art"), chunk_v01=f(V01, "chunk"), chunk_v01_strict=f(V01, "chunk_strict"), overstated=f(ids92, "art") - f(ids92, "chunk"))
out = dict(summary={k: summ(v) for k, v in RES.items()})
rows = {k: {r["id"]: r for r in rd(v)} for k, v in arms.items() if os.path.exists(v)}
ids = list(rows["SEFIX-ALL replay"])
S = rows["SEFIX-ALL replay"]
def ident(a, b):
    ra, rb = rows[a], rows[b]; res = {}
    for i in ids:
        if i not in ra or i not in rb: res.setdefault("missing", []).append(i); continue
        x, y = ra[i], rb[i]
        chk = dict(raw=x.get("raw") == y.get("raw"), wide12=x.get("wide12") == y.get("wide12"), keptIds=[c.get("chunkId") or c.get("title") for c in x["keptFull"]] == [c.get("chunkId") or c.get("title") for c in y["keptFull"]],
                   reason=x.get("reasonCodes") == y.get("reasonCodes"))
        for k, v in chk.items():
            if not v: res.setdefault(k + "_differs", []).append(i)
    res["all_four_identical"] = sum(1 for i in ids if i in ra and i in rb and all(rows[a][i].get(k) == rows[b][i].get(k) for k in ("raw", "wide12", "reasonCodes")) and [c.get("chunkId") or c.get("title") for c in ra[i]["keptFull"]] == [c.get("chunkId") or c.get("title") for c in rb[i]["keptFull"]])
    res["n"] = len(ids); return res
out["identity_off_vs_SEFIXALL"] = ident("COMBINED-off replay", "SEFIX-ALL replay") if "COMBINED-off replay" in rows else None
out["keys_example"] = sorted(S[ids[0]].keys())
# RD1 effect on the context vs SEFIX-ALL
if "COMBINED replay (RD1 on)" in rows:
    on = rows["COMBINED replay (RD1 on)"]
    kid = lambda r: [c.get("chunkId") or c["title"] for c in r["keptFull"]]
    ch = [i for i in ids if kid(on[i]) != kid(S[i])]
    out["contexts_changed_by_RD1"] = dict(n=len(ch), ids=ch, same_multiset=[i for i in ch if collections.Counter(kid(on[i])) == collections.Counter(kid(S[i]))], fewer_chunks=[i for i in ch if len(kid(on[i])) < len(kid(S[i]))])
    out["readseq_codes_fired"] = [i for i in ids if any(str(x).startswith("readseq") for x in on[i].get("reasonCodes", []))]
    tok = lambda r: sum(len((c.get("body") or "")) for c in r["keptFull"]) / 4
    out["kept_tokens_mean"] = dict(SEFIXALL=round(sum(tok(S[i]) for i in ids) / len(ids), 1), COMBINED=round(sum(tok(on[i]) for i in ids) / len(ids), 1))
    out["kept_chunks_mean"] = dict(SEFIXALL=round(sum(len(S[i]["keptFull"]) for i in ids) / len(ids), 3), COMBINED=round(sum(len(on[i]["keptFull"]) for i in ids) / len(ids), 3))
    a, b = RES["SEFIX-ALL replay"], RES["COMBINED replay (RD1 on)"]
    out["delivery_flips_vs_SEFIXALL"] = {k: [i for i in ids92 if a[i] and b[i] and a[i][k] != b[i][k]] for k in ("art", "chunk")}
    out["flags_combined"] = {i: dict(art=b[i]["art"], chunk=b[i]["chunk"], set=b[i]["set"]) for i in ids92 if b[i]}
    out["flags_sefixall"] = {i: dict(art=a[i]["art"], chunk=a[i]["chunk"], set=a[i]["set"]) for i in ids92 if a[i]}
    k3 = RES["K3 control replay B0"]; out["flags_k3"] = {i: dict(art=k3[i]["art"], chunk=k3[i]["chunk"], set=k3[i]["set"]) for i in ids92 if k3[i]}
# junk = mean kept chunks on keyed items with no fact chunk delivered (chunk level), own set per arm and the common no-fact set
nf = lambda a: [i for i in ids92 if RES[a][i] and not RES[a][i]["chunk"]]
if "COMBINED replay (RD1 on)" in rows:
    kc = lambda a, xs: round(sum(len(rows[a][i]["keptFull"]) for i in xs) / len(xs), 3) if xs else None
    both = [i for i in nf("SEFIX-ALL replay") if i in set(nf("COMBINED replay (RD1 on)"))]
    out["junk"] = dict(SEFIXALL_own=dict(n=len(nf("SEFIX-ALL replay")), mean_kept=kc("SEFIX-ALL replay", nf("SEFIX-ALL replay"))), COMBINED_own=dict(n=len(nf("COMBINED replay (RD1 on)")), mean_kept=kc("COMBINED replay (RD1 on)", nf("COMBINED replay (RD1 on)"))),
                       common=dict(n=len(both), SEFIXALL=kc("SEFIX-ALL replay", both), COMBINED=kc("COMBINED replay (RD1 on)", both)))
json.dump(out, open(CB + "/replays-read.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if not k.startswith("flags_") and k != "keys_example"}, indent=0)[:6000])
