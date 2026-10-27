#!/usr/bin/env python3
"""VEXACT-ACCEPT requests: the 11 public V-exact items (bench-vslice/questions.jsonl) for the claim engine (cut 7 + HEADPASS-X2b tree).
Config = the X2b requests' config (arms/headpass-st/tools/mkreq_x2b.py): commit 0cfd4a77, arm cut7-headpass-x2, Qwen3-4B-Instruct-2507 Q4_K_M,
settings quickFirst/alwaysComplete as the claim runs + packHeadPass a2 + packDense2 append-budget, android 12 GB, claim kit boar-crypto +
boar-wikivoyage-en (+ any --pack id=sha256 the candidate adds). GPS items keep their context lat/lon (the device fix).
Usage: python3 -I mkreq.py --run-id <id> --seed <n> [--pack id=sha256 ...] [--ids a,b] > requests.jsonl"""
import argparse, json, sys
VS = "<workspace>/rnd/research/compass/exp/bounty-eval/bench-vslice/questions.jsonl"
KIT = [{"id": "boar-crypto", "sha256": "ae9fbd2c7a46a46a815d46d0283e7b192adb4c342b38a2adc4881e8f9d8831fb"},
       {"id": "boar-wikivoyage-en", "sha256": "ff8595e32f56b8b84e20464afd8bf88532d47d2d82d799e3df8489440004b66e"}]
ap = argparse.ArgumentParser(); ap.add_argument("--run-id", required=True); ap.add_argument("--seed", type=int, required=True)
ap.add_argument("--pack", action="append", default=[]); ap.add_argument("--ids", default="")
a = ap.parse_args()
kit = [dict(k) for k in KIT]
for p in a.pack:
    i, s = p.split("=", 1); assert len(s) == 64 and all(c in "0123456789abcdef" for c in s), f"bad sha256 for {i}"
    assert i not in {k["id"] for k in kit}, f"pack {i} already in the kit"; kit.append({"id": i, "sha256": s})
cfg = {"commit": "0cfd4a77", "arm": "cut7-headpass-x2", "modelId": "qwen3-4b-instruct-2507-q4km",
       "settings": {"quickFirst": True, "alwaysComplete": False, "packHeadPass": "a2", "packDense2": "append-budget"},
       "kit": kit, "device": {"platform": "android", "ramGb": 12.0}}
want = [x for x in a.ids.split(",") if x]
items = [json.loads(l) for l in open(VS) if l.strip()]
assert len(items) == 11, len(items)
for it in items:
    if want and it["id"] not in want: continue
    item = {"id": it["id"], "question": it["question"], "lang": it.get("lang", "en"), **({"context": it["context"]} if it.get("context") else {})}
    sys.stdout.write(json.dumps({"protocol": "1.0.0", "runId": a.run_id, "item": item, "config": cfg, "seed": a.seed}, ensure_ascii=False) + "\n")
