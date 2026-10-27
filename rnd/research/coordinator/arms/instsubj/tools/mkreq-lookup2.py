#!/usr/bin/env python3
"""mkreq-lookup2.py: stub-replay requests for lookup set #2 (arms cut4, instsubj) -> l0/L2.<arm>.requests.jsonl. Prints only counts."""
import json, copy
B = "<workspace>"; R = B + "/rnd/research"; I = R + "/coordinator/arms/instsubj"
tpl = json.loads(open(R + "/coordinator/arms/travelsel/tools/requests71.jsonl").readline())
items = [json.loads(l) for l in open(I + "/lookup2/items.jsonl") if l.strip()]
for arm in ("cut4", "instsubj"):
    with open(f"{I}/l0/L2.{arm}.requests.jsonl", "w") as f:
        for d in items:
            r = copy.deepcopy(tpl); r["runId"] = "c4l2"; r["config"]["arm"] = arm
            r["item"] = {"id": d["id"], "question": d["question"], "lang": "en"}
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(arm, len(items))
