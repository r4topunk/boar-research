#!/usr/bin/env python3
"""Schema-only census of jev caches under blind/*/runs-*/*-cache. Prints counts + key names/types; never values."""
import glob, json, os, collections, sys
ROOT = "<workspace>/blind"
def schema(x, d=0):
    if isinstance(x, dict):
        if d > 3: return "dict"
        return {k: schema(v, d+1) for k, v in sorted(x.items())}
    if isinstance(x, list): return [schema(x[0], d+1)] if x else []
    return type(x).__name__
for cd in sorted(glob.glob(f"{ROOT}/*/runs-*/*-cache")):
    fs = glob.glob(f"{cd}/**/*.json", recursive=True)
    sch = collections.Counter(); qn = collections.Counter()
    for f in fs:
        try: r = json.load(open(f))
        except Exception: sch["<unreadable>"] += 1; continue
        a = r.get("answers") if isinstance(r, dict) else None
        if isinstance(a, dict):
            for k in a: qn[k.split("_")[0] if "_" in k and k[-1].isdigit() else k] += 1
            sch[json.dumps(schema({k: v for k, v in r.items() if k != "answers"}) | {"answers.<q>": schema(next(iter(a.values()))) if a else {}}, sort_keys=True)] += 1
        else: sch["<no answers>"] += 1
    print(os.path.relpath(cd, ROOT), "files", len(fs), "qnames", dict(qn.most_common(8)))
    for s, n in sch.most_common(3): print("   ", n, s[:600])
