#!/usr/bin/env python3
"""CV5 shared helper (0 calls): index every existing Opus judge.v1 row (ok, both orders) under rnd/research/coordinator/{arms,ruler}, boar-eval/runs
and rnd/kiln by unit key = item id | sha256(answer text), resolving each row's tracesSha256 to its traces file. Frame filter: refsSha256 and
questionsSha256 equal to the caller's frame; seed 7. blind/ and rnd/veil are never walked. Used by cv5_ladder_prep.py and cv5_per100_prep.py.
pool(frame_refs, frame_q) -> {key: {"boarA": mapped, "boarB": mapped, "src": file}}"""
import json, os, hashlib, collections
ROOT = "<workspace>"
ROOTS = [f"{ROOT}/rnd/research/coordinator/arms", f"{ROOT}/rnd/research/coordinator/ruler", f"{ROOT}/boar-eval/runs", f"{ROOT}/rnd/kiln"]
def key(q, t): return f"{q}|{hashlib.sha256(t.encode()).hexdigest()}"
def walk():
    jf, tf = [], []
    for r in ROOTS:
        for dp, dn, fn in os.walk(r):
            if "veil" in dp or "/blind" in dp or ".shards" in dp: continue
            for f in fn:
                p = os.path.join(dp, f)
                if f.endswith(".jsonl") and "judgments" in f: jf.append(p)
                elif f.endswith("traces.jsonl"): tf.append(p)
    return sorted(jf), sorted(tf)
def pool(fr, fq, exclude_prefix=None):
    jf, tf = walk(); rows = collections.defaultdict(list)
    for p in jf:
        if exclude_prefix and p.startswith(os.path.normpath(exclude_prefix)): continue
        try:
            for l in open(p):
                if "opus" not in l: continue
                r = json.loads(l)
                if r.get("ok") and not r.get("floorScored") and "opus" in str(r.get("judgeModel")) and r.get("judgeVersion") == "judge.v1" \
                   and r.get("refsSha256") == fr and r.get("questionsSha256") == fq and r.get("seed") == 7 and r.get("tracesSha256"):
                    rows[r["tracesSha256"]].append((p, r))
        except (ValueError, UnicodeDecodeError): pass
    th = {}
    for p in tf:
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        if h in rows and h not in th: th[h] = p
    out = {}
    for h, rs in rows.items():
        if h not in th: continue
        T = {}
        for l in open(th[h]):
            j = json.loads(l); T[j.get("itemId") or j.get("queryId")] = j
        for p, r in rs:
            t = T.get(r["queryId"])
            if not t or t.get("error"): continue
            k = key(r["queryId"], t["answer"]["text"]); u = out.setdefault(k, {"src": p})
            if u["src"] == p: u.setdefault(r["order"], r["mapped"])
    return {k: v for k, v in out.items() if "boarA" in v and "boarB" in v}
