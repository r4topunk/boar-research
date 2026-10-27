#!/usr/bin/env python3
"""RD1 divergence-first selection (0 LLM). python3 -I select_rd1_ids.py -> ../judge/changed.ids (judged, cut to the cap, targets first then id order), ../judge/changed.all.ids, ../judge/left.ids
Changed = RD1 answer text differs from the F1b answer text for the same item. Cap 100 calls = 50 items (2 orders)."""
import json
A = "<workspace>/rnd/research/coordinator/arms"; CM = A + "/coverage-map"; RD = CM + "/reader/rd1"
TARGETS = "st-qa-money-se-010 lan-hlt-003 lan-rsn-001 vit-hlt-003 st-qa-cooking-se-008 st-qa-cooking-se-001 st-qa-money-se-018 st-qa-cooking-se-012".split()
ld = lambda p: {json.loads(l)["itemId"]: json.loads(l) for l in open(p) if l.strip()}
ids = open(A + "/lp-screens/main-97.ids").read().split()
TF = ld(CM + "/sefix/ans-traces/f1b-main-s42.traces.jsonl"); TR = ld(RD + "/traces/rd1-main-s42.traces.jsonl")
chg = sorted(i for i in ids if TR[i]["answer"]["text"] != TF[i]["answer"]["text"])
order = [i for i in TARGETS if i in chg] + [i for i in chg if i not in TARGETS]
CAP = 50
j, left = order[:CAP], order[CAP:]
open(RD + "/judge/changed.all.ids", "w").write("\n".join(chg) + "\n"); open(RD + "/judge/changed.ids", "w").write("\n".join(sorted(j)) + "\n"); open(RD + "/judge/left.ids", "w").write("\n".join(left) + ("\n" if left else ""))
print(f"changed {len(chg)} judged {len(j)} left {len(left)} targets changed {[i for i in TARGETS if i in chg]} targets same {[i for i in TARGETS if i not in chg]}")
