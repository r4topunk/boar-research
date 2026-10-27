#!/usr/bin/env python3
"""CB17 requests (0 LLM). python3 -I mkreq_cb17.py <out requests.jsonl>
= the LP-SCREENS K0 MAIN-97 requests (arms/lp-screens/tools/mkreq.py K0 main-97.ids: LITEPACKS K0 rows, Qwen3-1.7B, seed 42, quickFirst +
packHeadPass a2 + packDense2 append-budget) with runId cb17-main-s42, config.arm cut7-headpass-x2+litepacks+cb17 and config.kit = [] (no pack installed).
Everything else is byte-for-byte the K0 control request."""
import json, sys, subprocess
A = "<workspace>/rnd/research/coordinator/arms"; out = sys.argv[1]; tmp = out + ".k0tmp"
subprocess.run(["python3", "-I", f"{A}/lp-screens/tools/mkreq.py", "K0", f"{A}/lp-screens/main-97.ids", "cb17-main-s42", "cut7-headpass-x2+litepacks+cb17", tmp], check=True)
rows = [json.loads(l) for l in open(tmp)]
assert len(rows) == 97
for r in rows:
    assert [k["id"] for k in r["config"]["kit"]] == ["boar-crypto", "boar-wikivoyage-en"] and r["seed"] == 42 and r["config"]["modelId"] == "qwen3-1.7b-q4km"
    r["config"]["kit"] = []
open(out, "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
import os; os.remove(tmp); print(f"{len(rows)} requests -> {out}")
