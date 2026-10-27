#!/usr/bin/env python3 -I
"""Length-slope dataset builder (0 LLM). Walks existing judge.v1 rows (ok, not floorScored, seed 7) under coordinator/arms, ruler, boar-eval/runs, rnd/kiln
(never blind/ or veil), resolves tracesSha256 to the traces file, and emits one row per (judge family, model, persona, item, answer text):
s = mean over the two orders of mean(correctness, completeness, usefulness) of the boar answer (1-5); words = whitespace-split word count of answer.text.
declined/warned = null-cal labels.label. Output: argv[1] json."""
import json, os, sys, hashlib, collections
ROOT = "<workspace>"
ROOTS = [f"{ROOT}/rnd/research/coordinator/arms", f"{ROOT}/rnd/research/coordinator/ruler", f"{ROOT}/boar-eval/runs", f"{ROOT}/rnd/kiln"]
sys.path.insert(0, f"{ROOT}/rnd/research/coordinator/arms/null-cal/tools"); from labels import label
K = ("correctness", "completeness", "usefulness")
jf, tf = [], []
for r in ROOTS:
    for dp, dn, fn in os.walk(r):
        if "veil" in dp or "/blind" in dp or ".shards" in dp or "/web-actions" in dp: continue
        for f in fn:
            p = os.path.join(dp, f)
            if f.endswith(".jsonl") and "judgments" in f: jf.append(p)
            elif f.endswith("traces.jsonl"): tf.append(p)
rows = collections.defaultdict(list)
for p in sorted(jf):
    try:
        for l in open(p):
            if '"mapped"' not in l: continue
            r = json.loads(l)
            jm = str(r.get("judgeModel")); jv = str(r.get("judgeVersion"))
            if not r.get("ok") or r.get("floorScored") or not jv.startswith("judge.v1") or r.get("seed") != 7 or not r.get("tracesSha256"): continue
            fam = "opus" if "opus" in jm else "haiku" if "haiku" in jm else None
            if fam: rows[r["tracesSha256"]].append((fam, r))
    except (ValueError, UnicodeDecodeError): pass
th = {}
for p in sorted(tf):
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    if h in rows and h not in th: th[h] = p
out = {}; stats = collections.Counter()
for h, rs in rows.items():
    if h not in th: stats["traces_missing"] += 1; continue
    T = {}
    for l in open(th[h]):
        j = json.loads(l); T[j.get("itemId") or j.get("queryId")] = j
    for fam, r in rs:
        t = T.get(r["queryId"])
        if not t or t.get("error") or not t.get("answer"): continue
        a = t["answer"]; txt = a["text"]; rt = t.get("runtime") or {}; v = rt.get("versions", {})
        key = (fam, r["queryId"], hashlib.sha256(txt.encode()).hexdigest())
        u = out.setdefault(key, dict(judge=fam, id=r["queryId"], model=rt.get("model") or t.get("model"), persona=v.get("persona"),
                                     run=t.get("runId"), arm=(t.get("engine") or {}).get("arm"), words=len(txt.split()), chars=len(txt),
                                     declined=None, warned=None, orders={}))
        u["orders"].setdefault(r["order"], sum(r["mapped"]["boar"][k] for k in K) / 3)
        u["corr"] = u.get("corr", {}); u["corr"].setdefault(r["order"], r["mapped"]["boar"]["correctness"])
        if u["declined"] is None:
            lb = label(dict(text=txt, declined=a.get("declined"), corr=3, s=0, sref=0)); u["declined"] = lb["decline"]; u["warned"] = lb["warned"]
res = []
for k, u in out.items():
    if set(u["orders"]) != {"boarA", "boarB"}: stats["one_order"] += 1; continue
    u["s"] = sum(u["orders"].values()) / 2; u["c"] = sum(u["corr"].values()) / 2; del u["orders"], u["corr"]; res.append(u)
json.dump(res, open(sys.argv[1], "w")); print(len(res), dict(stats))
