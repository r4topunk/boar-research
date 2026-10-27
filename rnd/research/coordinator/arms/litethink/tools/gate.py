#!/usr/bin/env python3
# LITETHINK gate (0 calls): argv = budget traces... ; prints per item numbers/ids only. LLM item = has a generation event.
# Per-item pass: 0 errors, non-empty answer, no '<think>' in answer, LLM items: 0 < reasoning <= budget + 10 (THINK4B deviation 1: the
# adapter flag thinkingBudgetExceeded counts the budget message tokens, so it is printed, not gated), finishReason not 'length' when present.
# Exit 0 PASS; 1 FAIL. With KILL=1 applies the frozen kill_if instead: > 1 empty/cut OR reasoning 0 on >= 3 LLM items -> KILL (rc 9).
import json, os, sys
B = int(sys.argv[1]); rows = [json.loads(l) for f in sys.argv[2:] for l in open(f)]
bad = 0; empty_cut = 0; r0 = 0; nllm = 0; tot = []
for t in rows:
    g = [e for e in t.get("events", []) if e.get("kind") == "generation"]
    r = t.get("timing", {}).get("reasoningTokens") or 0; a = t.get("answer"); a = a.get("text", "") if isinstance(a, dict) else str(a or "")
    cut = any((e.get("finishReason") or e.get("stopReason")) == "length" for e in g) or any(e.get("truncated") for e in g)
    exc = any(e.get("thinkingBudgetExceeded") for e in g); llm = len(g) > 0; nllm += llm
    ok = not t.get("error") and len(a.split()) > 0 and "<think>" not in a and not cut and (not llm or 0 < r <= B + 10)
    empty_cut += (len(a.split()) == 0 or cut); r0 += (llm and r == 0); bad += (not ok); tot.append((t.get("timing", {}).get("totalMs") or 0) / 1000)
    print(f"{t['itemId']} llm={llm} gens={len(g)} reasoning={r} answerWords={len(a.split())} cut={cut} error={bool(t.get('error'))} totalS={round(tot[-1],1)} ttftS={round((t.get('timing',{}).get('ttftMs') or 0)/1000,1)} budgetExceededFlag={exc} ok={ok}")
tot.sort(); print(f"n={len(rows)} llm={nllm} fail={bad} empty_or_cut={empty_cut} reasoning0_llm={r0} total_p50={tot[len(tot)//2]:.1f}s")
if os.environ.get("KILL") == "1":
    k = empty_cut > 1 or r0 >= 3; print("KILL" if k else "NO-KILL"); sys.exit(9 if k else 0)
print("GATE", "PASS" if bad == 0 else "FAIL"); sys.exit(0 if bad == 0 else 1)
