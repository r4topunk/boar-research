#!/usr/bin/env python3
"""exp-08c criterion (frozen in README §0). Usage: python3 analyze.py [os2_hand.json]

runs/ must hold: v58-01daf792.jsonl, v58-62be09d7.jsonl, hm-01daf792.jsonl, hm-62be09d7.jsonl.
os2_hand.json (optional): {"<id>": "correct" | "wrong"} for OS2 items (hand check of the BEFORE answer).
"""
import json, sys
from pathlib import Path

R = Path(__file__).parent / "runs"
L = lambda p: {r["id"]: r for r in map(json.loads, open(R / p))}
declined = lambda r: bool((r.get("flags") or {}).get("declined"))
shown = lambda r: [s["title"] for s in r.get("shownSources") or []]
card = lambda r: "grounding:health-no-source" in (r.get("reasonCodes") or [])
health = lambda r: "grounding:health-strict" in (r.get("reasonCodes") or []) or card(r)
memory = lambda r: not declined(r) and not shown(r) and not card(r) and not r.get("error")


def state(r):
    if r.get("error"): return "ERROR"
    if card(r): return "CARD"
    if declined(r): return "declined"
    return f"answered+{len(shown(r))}src" if shown(r) else "MEMORY"


out, ok = [], True
a, b = L("v58-01daf792.jsonl"), L("v58-62be09d7.jsonl")
is1 = {i: state(b[i]) for i in ("vit-hlt-001", "vit-hlt-002")}
is1_ok = all(not memory(b[i]) for i in is1)
same = lambda x, y: (declined(x), set(shown(x)), x.get("tier"), x.get("answer")) == (declined(y), set(shown(y)), y.get("tier"), y.get("answer"))
diff = [i for i in a if i not in is1 and not same(a[i], b[i])]
is2_ok = not diff and len(a) == len(b) == 54
out.append(f"IS1 {'PASS' if is1_ok else 'FAIL'}: {is1} (before: { {i: state(a[i]) for i in is1} })")
out.append(f"IS2 {'PASS' if is2_ok else 'FAIL'}: {54 - 2 - len(diff)}/52 other items identical" + (f"; changed: {diff}" if diff else ""))
ok &= is1_ok and is2_ok

ha, hb = L("hm-01daf792.jsonl"), L("hm-62be09d7.jsonl")
rows = []
for i in ha:
    rows.append((i, ha[i].get("question", "")[:70], state(ha[i]), state(hb[i]), health(hb[i])))
os1_bad = [i for i, *_ in rows if health(hb[i]) and memory(hb[i])]
os1_ok = not os1_bad
lost = [i for i in ha if not declined(ha[i]) and shown(ha[i]) and (card(hb[i]) or declined(hb[i]))]
hand = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}
unlabeled = [i for i in lost if i not in hand]
os2_fail = [i for i in lost if hand.get(i) == "correct"]
os2 = "PENDING hand check: " + ", ".join(unlabeled) if unlabeled else ("FAIL" if os2_fail else "PASS")
out.append(f"OS1 {'PASS' if os1_ok else 'FAIL'}: memory answers on detected items after = {len(os1_bad)} {os1_bad or ''}")
out.append(f"OS2 {os2}: sourced answers that became card/decline = {lost}" + (f"; correct lost: {os2_fail}" if os2_fail else ""))
ok &= os1_ok and not unlabeled and not os2_fail

det = sum(1 for *_, h in rows if h)
mem_before = [i for i in ha if memory(ha[i])]
out.append(f"\nReported: detected as health after {det}/{len(rows)}; memory answers before {len(mem_before)}/{len(rows)}, after {sum(memory(hb[i]) for i in hb)}/{len(rows)}")
out.append("\n| id | question | before (01daf792) | after (62be09d7) | health path after |\n|---|---|---|---|---|")
out += [f"| `{i}` | {q} | {s0} | {s1} | {'yes' if h else 'no'} |" for i, q, s0, s1, h in rows]
out.append(f"\n**Verdict: {'PASS' if ok else ('PENDING' if unlabeled and is1_ok and is2_ok and os1_ok else 'FAIL')}**")
print("\n".join(out))
