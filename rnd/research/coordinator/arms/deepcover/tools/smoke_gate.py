#!/usr/bin/env python3
"""DEEPCOVER smoke gate (argv1 = traces.jsonl; rc 0 = pass): 3/3 deep-thinking + deepcover:on, 0 errors, 1 <= reasoning <= 522,
outputTokens <= 300 on 3/3, answers 90-230 words on >= 2/3. Prints counts only."""
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
codes = [set(r.get("route", {}).get("reasonCodes") or []) for r in rows]
deep = sum("generate:deep-thinking" in c for c in codes); on = sum("deepcover:on" in c for c in codes)
err = sum(1 for r in rows if r.get("error")); rt = [int((r.get("timing") or {}).get("reasoningTokens") or 0) for r in rows]
rok = sum(1 <= t <= 522 for t in rt); out = [int((r.get("timing") or {}).get("outputTokens") or 0) - t for r, t in zip(rows, rt)]
words = [len(((r.get("answer") or {}).get("text") or "").split()) for r in rows]; wok = sum(90 <= w <= 230 for w in words)
print(f"n={len(rows)} deep={deep} deepcover_on={on} errors={err} reasoning={rt} answer_tokens={out} words={words} words_ok={wok}")
ok = len(rows) >= 3 and deep == len(rows) and on == len(rows) and err == 0 and rok == len(rows) and all(o <= 300 for o in out) and wok >= 2
print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
