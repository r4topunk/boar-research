# THINK4B smoke gate (arm.sh SMOKE_GATE): argv1 = traces; rc 0 = pass. Prints numbers/ids only.
# Pass = every item routed generate:user-model-qwen3-4b-thinking-2507-q4km (fast tier, single), 0 errors, non-empty answer,
# GATE_MIN <= reasoning tokens <= GATE_MAX (budget enforced: 256 + message ≈ 266, or 512 + message ≈ 522).
# DEVIATION 1 (10:5x): the adapter flag budgetExceeded = reasoningTokens > budget counts the budget message tokens (264 = 256 + 8 on the
# smoke), so it is always true when the budget binds; it is printed, not gated (the criterion clause "budgetExceeded false" was written wrongly).
import json, os, sys
lo, hi = int(os.environ.get("GATE_MIN", "1")), int(os.environ.get("GATE_MAX", "266"))
ok = True
for l in open(sys.argv[1]):
    t = json.loads(l); rc = t.get("route", {}).get("reasonCodes", []); g = [e for e in t.get("events", []) if e.get("kind") == "generation"]
    r = t.get("timing", {}).get("reasoningTokens", sum(e.get("reasoningTokens") or 0 for e in g)); a = t.get("answer"); a = a.get("text", "") if isinstance(a, dict) else str(a or "")
    routed = "generate:user-model-qwen3-4b-thinking-2507-q4km" in rc; exc = any(e.get("thinkingBudgetExceeded") for e in g)
    print(f"{t['itemId']} routed={routed} gens={len(g)} reasoning={r} answerWords={len(a.split())} error={bool(t.get('error'))} totalS={round((t.get('timing', {}).get('totalMs') or 0)/1000,1)} budgetExceeded={exc}")
    ok = ok and routed and lo <= r <= hi and len(a.split()) > 0 and not t.get("error")
print("GATE", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
