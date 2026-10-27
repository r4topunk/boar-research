#!/usr/bin/env python3
# mkreq_swap.py <src.requests> <out.requests> <runId> <modelId>: copy requests changing only runId and config.modelId (compact JSON). Prints counts/shas only.
import json, sys, hashlib
src, out, run, mid = sys.argv[1:5]; rows = []
for l in open(src):
    if not l.strip(): continue
    x = json.loads(l); x["runId"] = run; x["config"]["modelId"] = mid; rows.append(json.dumps(x, separators=(",", ":"), ensure_ascii=False) + "\n")
open(out, "w").writelines(rows)
norm = lambda p: hashlib.sha256("".join(sorted(json.dumps({k: v for k, v in json.loads(l).items() if k != "runId"} | {"config": {k: v for k, v in json.loads(l)["config"].items() if k != "modelId"}}, sort_keys=True) for l in open(p) if l.strip())).encode()).hexdigest()[:16]
print(f"{run}: {len(rows)} requests, arm {sorted({json.loads(r)['config']['arm'] for r in rows})}, sha {hashlib.sha256(''.join(rows).encode()).hexdigest()[:16]}, normalised(src)={norm(src)} normalised(out)={norm(out)}")
