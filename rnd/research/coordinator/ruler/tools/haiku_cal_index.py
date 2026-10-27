#!/usr/bin/env python3
"""HAIKU-CAL step 1 (0 calls): index every Haiku/Opus judge.v1 both-order label by unit (queryId, sha16(text), refsSha256).
python3 -I haiku_cal_index.py -> ../haiku-cal/units.json. Never reads blind/ or rnd/veil/."""
import json, os, glob, hashlib, collections, sys
ROOT = "<workspace>"; RUL = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = f"{RUL}/../arms"
sys.path.insert(0, f"{RUL}/../arms/null-cal/tools"); from labels import W, is_decline  # noqa
BAD = ("/blind/", "/veil/", ".shards/", ".preflight/", "/node_modules/")
def walk(pat):
    out = []
    for base in (f"{ROOT}/boar-eval", f"{ROOT}/rnd"):
        for dp, dn, fn in os.walk(base):
            dn[:] = [d for d in dn if d not in ("blind", "veil", "node_modules", ".git") and not d.endswith(".shards")]
            for f in fn:
                if pat(f): p = f"{dp}/{f}"; out.append(p) if not any(b in p for b in BAD) else None
    return out
TRF = walk(lambda f: f.endswith(".traces.jsonl") or f == "traces.jsonl")
sha2tr = {}
for p in TRF:
    h = hashlib.sha256(open(p, "rb").read()).hexdigest(); sha2tr.setdefault(h, p)
JF = walk(lambda f: "judgments" in f and f.endswith(".jsonl"))
FAM = {("claude-haiku-5-5", "judge.v1-low"): "haiku", ("claude-opus-5-5", "judge.v1"): "opus"}
groups = collections.defaultdict(dict); nores = collections.Counter()
for p in JF:
    for l in open(p):
        try: x = json.loads(l)
        except Exception: continue
        if x.get("ok") is not True or x.get("floorScored") or "mapped" not in x: continue
        f = FAM.get((x.get("judgeModel"), x.get("judgeVersion")))
        if not f: continue
        ts = x.get("tracesSha256")
        if not ts or ts not in sha2tr: nores[f] += 1; continue
        groups[(p, ts, x["queryId"], x.get("refsSha256"), f)][x["order"]] = x["mapped"]
TX = {}
def trace(ts, q):
    if ts not in TX:
        TX[ts] = {}
        for l in open(sha2tr[ts]):
            if l.strip():
                t = json.loads(l); TX[ts][t.get("itemId") or t.get("queryId")] = t
    return TX[ts].get(q)
units = {}
for (p, ts, q, rs, f), v in groups.items():
    if set(v) != {"boarA", "boarB"}: continue
    t = trace(ts, q)
    if t is None: continue
    tx = t["answer"]["text"]; key = f"{q}|{hashlib.sha256(tx.encode()).hexdigest()[:16]}|{(rs or '')[:16]}"
    ms = [v["boarA"], v["boarB"]]
    lab = {d: sum(m["boar"][d] for m in ms) / 2 for d in ("correctness", "completeness", "usefulness")}
    lab["sref"] = sum(sum(m["ref"].values()) / 3 for m in ms) / 2
    u = units.setdefault(key, dict(id=q, refs=rs, haiku=[], opus=[], files={"haiku": [], "opus": []},
        tier=t.get("runtime", {}).get("model"), warned=tx.startswith(W), declined=is_decline(tx, t["answer"].get("declined")),
        kept=len((t.get("retrieval") or {}).get("kept") or []), ot=((t.get("timing") or {}).get("outputTokens") or 0), runIds=[]))
    u[f].append(lab); u["files"][f].append(os.path.relpath(p, ROOT))
    if t.get("runId") not in u["runIds"]: u["runIds"].append(t.get("runId"))
both = {k: u for k, u in units.items() if u["haiku"] and u["opus"]}
json.dump(dict(n_traces_files=len(TRF), n_judgment_files=len(JF), unresolved_rows=dict(nores), n_units=len(units), n_both=len(both), units=both),
          open(f"{RUL}/haiku-cal/units.json", "w"))
print(len(TRF), len(JF), dict(nores), len(units), "both", len(both))
