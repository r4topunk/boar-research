#!/usr/bin/env python3
# MP4B smoke/slice gate: rc 0 iff 0 errors, every answer non-empty, >= 1 item ran multipass (health items legitimately stay single: answer.ts grounding:health-no-multipass). Prints counts only.
import json, sys, collections
T = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
err = [t["itemId"] for t in T if t.get("error")]
empty = [t["itemId"] for t in T if not t.get("error") and not (t.get("answer", {}).get("text") or "").strip()]
mode = collections.Counter((t.get("route") or {}).get("mode") for t in T)
gens = [sum(1 for e in t.get("events", []) if e.get("type") == "generation" or e.get("kind") == "generation") for t in T]
print(json.dumps({"n": len(T), "errors": len(err), "empty": len(empty), "mode": dict(mode), "generationEventsPerItem_median": sorted(gens)[len(gens)//2] if gens else None}))
ok = not err and not empty and mode.get("multipass", 0) >= 1
sys.exit(0 if ok else 1)
