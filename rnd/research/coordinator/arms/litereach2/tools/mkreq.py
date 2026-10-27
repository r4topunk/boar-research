"""LITEREACH2 requests: the LITE5-180 ON request rows of the given ids, only runId changed (asserted), one file per pack (the adapter
requires one config, and the kit differs per pack). Usage: mkreq.py <ids file> <runId prefix> <out dir>  -> <out dir>/<prefix>-<pack>-s42.requests.jsonl"""
import json, sys, glob, collections
A = "<workspace>/rnd/research/coordinator/arms"; ids = [l.strip() for l in open(sys.argv[1]) if l.strip()]; pre, od = sys.argv[2], sys.argv[3]
src = {}
for f in sorted(glob.glob(f"{A}/lite5/runs/180/lite5-180-on-*-s42.requests.jsonl")):
    p = f.split("lite5-180-on-")[1].rsplit("-s42", 1)[0]
    for l in open(f):
        if l.strip(): r = json.loads(l); src[r["item"]["id"]] = (p, r)
by = collections.defaultdict(list)
for i in ids:
    p, r0 = src[i]; r = json.loads(json.dumps(r0)); r["runId"] = f"{pre}-{p}-s42"
    a, b = dict(r0), dict(r); a.pop("runId"); b.pop("runId"); assert a == b
    by[p].append(r)
for p, rs in by.items():
    open(f"{od}/{pre}-{p}-s42.requests.jsonl", "w").write("".join(json.dumps(r) + "\n" for r in rs)); print(p, len(rs))
