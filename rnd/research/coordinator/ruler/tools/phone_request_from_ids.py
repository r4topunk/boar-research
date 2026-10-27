#!/usr/bin/env python3
"""Build a BOAR Bench phone request from an existing one, keeping only the ids in an ids file (and/or dropping a skip list). 0 LLM.
Usage: python3 -I phone_request_from_ids.py <base.request.json> <new requestId> [--keep ids] [--skip ids] [--model id] > new.request.json
The warm-up item (warmup-000) is always kept first. Question text/category come from the base request; order follows the base."""
import json, sys
a = sys.argv[1:]; base, rid = a[0], a[1]; opt = dict(zip(a[2::2], a[3::2]))
rd = lambda f: set(open(f).read().split())
req = json.load(open(base)); keep = rd(opt["--keep"]) if "--keep" in opt else None; skip = rd(opt["--skip"]) if "--skip" in opt else set()
qs = [q for q in req["questions"] if q["id"] == "warmup-000" or ((keep is None or q["id"] in keep) and q["id"] not in skip)]
missing = (keep or set()) - {q["id"] for q in req["questions"]}
if missing: sys.exit(f"ids not in base request: {sorted(missing)}")
req["requestId"] = rid; req["questions"] = qs
if "--model" in opt: req["models"] = [opt["--model"]]
req["evalSetVersion"] = req.get("evalSetVersion", "") + f"-subset{len(qs)}"
print(json.dumps(req, indent=1, ensure_ascii=False)); print(f"{len(qs)} questions (incl. warm-up)", file=sys.stderr)
