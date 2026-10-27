#!/usr/bin/env python3
"""VITALADD smoke gate (argv1 = traces.jsonl; rc 0 = pass): 3/3 deep-thinking, 0 errors, non-empty answers, 1 <= reasoning <= 522,
an addpack:* code on every item and addpack:kept-1 on >= 2 items. Prints counts only."""
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
codes = [set(r.get("route", {}).get("reasonCodes") or []) for r in rows]
deep = sum("generate:deep-thinking" in c for c in codes); err = sum(1 for r in rows if r.get("error")); ans = sum(1 for r in rows if (r.get("answer") or {}).get("text"))
# v2 (addendum 1): health items take the extractive path (no deep generation); they pass on "grounding:health-extractive" instead of reasoning tokens.
rt = [int((r.get("timing") or {}).get("reasoningTokens") or 0) for r in rows]
rok = sum((1 <= t <= 522) or ("grounding:health-extractive" in c) for t, c in zip(rt, codes))
addany = sum(any(x.startswith("addpack:") for x in c) for c in codes); kept1 = sum("addpack:kept-1" in c for c in codes)
print(f"n={len(rows)} deep={deep} errors={err} answers={ans} reasoning_ok={rok} reasoning={rt} addpack_any={addany} addpack_kept1={kept1}")
ok = len(rows) >= 3 and deep == len(rows) and err == 0 and ans == len(rows) and rok == len(rows) and addany == len(rows) and kept1 >= 2
print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
