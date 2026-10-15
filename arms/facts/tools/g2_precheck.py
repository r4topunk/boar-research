#!/usr/bin/env python3
"""G2: apply bench v0.1 grading (rnd/rnd/research/agent-notes/tools/precheck.py grade(): must_any / must_k / forbid / echo filter) to the
FACTS instant answer of each step-1 target item. Usage: python3 -I g2_precheck.py <facts_check.jsonl>"""
import json, sys
sys.path.insert(0, "$BOAR_WS/rnd/rnd/research/agent-notes/tools")
from precheck import grade
TARGETS = ["lan-cmp-001", "lan-rsn-002", "lan-ref-001", "lan-ref-004", "lan-exp-006", "lan-rsn-007", "lan-ref-005", "trv-002"]
qs = {json.loads(l)["id"]: json.loads(l) for l in open("$BOAR_WS/boar-eval/bench/v0.1/questions.public.jsonl")}
rows = {r["id"]: r for r in map(json.loads, open(sys.argv[1])) if r["set"] == "v0.1"}
npass = 0
for i in TARGETS:
    r = rows[i]; q = qs[i]
    if q["grading"].get("type") == "judge-only":
        st, why = "no-precheck (judge-only)", ""
    else:
        st, why = grade(q, {"answer": r["answer"]} if r["fired"] else None) if r["fired"] else ("not-fired", "")
    npass += st == "pass"
    print(f"{i}\t{'FIRE' if r['fired'] else '-'}\t{st}\t{why}")
print(f"G2 pass {npass}/{len(TARGETS)} = {npass/len(TARGETS):.1%} (bar >= 75%)")
