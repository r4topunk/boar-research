#!/usr/bin/env python3
# BONSAI2 smoke gate (arm.sh SMOKE_GATE): argv1 = traces; rc 0 = pass. Counts/ids only.
# Pass = 0 errors, every answer non-empty, reasoning tokens 0 on every generation (no thinking leak), no "<think>" in any answer,
# runtime.model == config.modelId == GATE_MODEL (default bonsai2-4b-ptq1_0).
import json, os, sys
want = os.environ.get("GATE_MODEL", "bonsai2-4b-ptq1_0"); ok = True
for l in open(sys.argv[1]):
    if not l.strip(): continue
    t = json.loads(l); a = (t.get("answer") or {}).get("text") or ""
    g = [e for e in t.get("events", []) if e.get("kind") == "generation"]
    r = max(sum(e.get("reasoningTokens") or 0 for e in g), t.get("timing", {}).get("reasoningTokens") or 0)
    m = (t.get("runtime") or {}).get("model"); c = (t.get("config") or {}).get("modelId")
    item_ok = not t.get("error") and len(a.split()) > 0 and r == 0 and "<think>" not in a and m == c == want
    print(f"{t['itemId']} gens={len(g)} reasoning={r} words={len(a.split())} think={'<think>' in a} model={m} error={bool(t.get('error'))} {'ok' if item_ok else 'FAIL'}")
    ok = ok and item_ok
print("GATE", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
