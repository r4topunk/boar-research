#!/usr/bin/env python3
"""Selection over n samples per item (best-of-n), then precheck v2.2 on each selection. Selectors (no model calls):
  s1       the first sample (= single-sample baseline at temp 0.7, seed 1)
  medoid   MBR-style: the sample with the highest mean content-word Jaccard to the other samples (consensus)
  support  the sample whose sentences are best supported by the prompt's sources (engine-style key-term overlap)
  oracle   the best sample by precheck (upper bound; not a real selector)
Usage: select.py runs/q4b-n4.jsonl"""
import json, re, subprocess, sys, unicodedata, collections, os
STOP = set(("a an the and or but if then else of to in on at by for with from as is are was were be been being do does did doing have has had having it its this that these those there here what which who whom whose when where why how can could should would will shall may might must i you he she we they me him her us them my your his our their not no yes so than too very just about into over under between vs versus also tell explain describe give me please much many more most some any all each other such only own same").split())
def stem(t):
    if len(t) > 5 and t.endswith("ies"): return t[:-3] + "y"
    if len(t) > 4 and (t.endswith("es") or t.endswith("ed")): return t[:-2]
    if len(t) > 3 and t.endswith("s") and not t.endswith("ss"): return t[:-1]
    if len(t) > 5 and t.endswith("ing"): return t[:-3]
    return t
def terms(x):
    x = unicodedata.normalize("NFKD", x.lower()); x = "".join(c for c in x if not unicodedata.combining(c))
    return [stem(t) for t in re.findall(r"[a-z0-9]+", x) if len(t) > 1 and t not in STOP]
def jacc(a, b):
    A, B = set(terms(a)), set(terms(b)); return len(A & B) / max(1, len(A | B))
def support(ans, sources):
    sents = [s for s in re.split(r"(?<=[.!?])\s+|\n+", re.sub(r"\[\d+\]", " ", ans)) if len(terms(s)) >= 2]
    if not sents: return 0.0
    src = [set(terms(s["title"] + " " + s["body"])) for s in sources]
    tot = 0.0
    for s in sents:
        k = set(terms(s)); tot += max(len(k & S) / len(k) for S in src) if src else 0
    return tot / len(sents)
rows = [json.loads(l) for l in open(sys.argv[1])]
n = len(rows[0]["samples"])
pick = {"s1": [], "medoid": [], "support": []}
for r in rows:
    S = r["samples"]
    pick["s1"].append(0)
    pick["medoid"].append(max(range(n), key=lambda i: sum(jacc(S[i], S[j]) for j in range(n) if j != i)))
    pick["support"].append(max(range(n), key=lambda i: support(S[i], r["sources"])))
PRE = "<workspace>/rnd/lantern/tools/precheck.py"
base = os.path.splitext(sys.argv[1])[0]
def precheck(name, texts):
    pin = f"{base}.{name}.pin.jsonl"
    with open(pin, "w") as f:
        for r, t in zip(rows, texts): f.write(json.dumps({"queryId": r["queryId"], "answer": t, "declined": False}) + "\n")
    js = f"{base}.{name}.precheck.json"
    out = subprocess.run(["python3", PRE, pin, "--json", js], capture_output=True, text=True).stdout
    return {x["id"]: x for x in json.load(open(js))}, [l for l in out.splitlines() if l.startswith("n=")][0]
# per-sample status (for oracle)
stat = [precheck(f"sample{i+1}", [r["samples"][i] for r in rows])[0] for i in range(n)]
rank = {"pass": 3, "fail-missing": 2, "refused": 1, "confident-wrong": 0}
oracle = [max(range(n), key=lambda i: rank.get(stat[i][r["queryId"]]["status"], 1)) for r in rows]
for name, idx in list(pick.items()) + [("oracle", oracle)]:
    _, line = precheck(name, [r["samples"][i] for r, i in zip(rows, idx)])
    print(f"{name:8s} {line}")
per = [sum(1 for r in rows if stat[i][r["queryId"]]["counts_as_pass"]) for i in range(n)]
cw = [sum(1 for r in rows if stat[i][r["queryId"]]["status"] == "confident-wrong") for i in range(n)]
print("per-sample pass:", per, "CW:", cw)
