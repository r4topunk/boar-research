#!/usr/bin/env python3
"""LITE5 requests (0 LLM). Run: python3 -I mkreq_lite5.py
ON  = headpass-st/gen-x2b/st-<pack>-cut7-headpassx2b-s42.requests.jsonl (the 4B X2b requests: arm cut7-headpass-x2, settings + packHeadPass a2 +
      packDense2 append-budget, item pack -> sidecar copy) filtered to lite2/selftest20.ids, modelId -> qwen3-1.7b-q4km, runId lite5-on-st20-<pack>-s42.
OFF = the same rows with the two X2b settings removed (= LITE2's settings), runId lite5-off-st20-<pack>-s42: a 0-judge host identity check
      (MacBook vs the mini's LITE2 l-st20 traces); never judged.
Checks: each ON row equals the LITE2 l-st20 request except runId, config.arm, config.settings (the two keys), the item pack's kit sha256."""
import json, copy
A = "<workspace>/rnd/research/coordinator/arms"; O = f"{A}/lite5/runs"
ids = [l.strip() for l in open(f"{A}/lite2/selftest20.ids") if l.strip()]; want = set(ids)
packs = sorted({i[3:].rsplit("-", 1)[0] for i in ids}); X2B = ("packHeadPass", "packDense2")
w = lambda p, rows: open(p, "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
n = 0
for p in packs:
    on = [json.loads(l) for l in open(f"{A}/headpass-st/gen-x2b/st-{p}-cut7-headpassx2b-s42.requests.jsonl") if l.strip()]
    on = [r for r in on if r["item"]["id"] in want]
    l2 = {(x := json.loads(l))["item"]["id"]: x for l in open(f"{A}/lite2/runs/l-st20-{p}-s42.requests.jsonl") if l.strip()}
    assert [r["item"]["id"] for r in on] == list(l2), p
    offs = []
    for r in on:
        assert r["config"]["modelId"] == "qwen3-4b-instruct-2507-q4km" and r["seed"] == 42
        r["config"]["modelId"] = "qwen3-1.7b-q4km"; r["runId"] = f"lite5-on-st20-{p}-s42"
        b = l2[r["item"]["id"]]; a = copy.deepcopy(r)
        a["runId"] = b["runId"]; a["config"]["arm"] = b["config"]["arm"]; a["config"]["settings"] = {k: v for k, v in a["config"]["settings"].items() if k not in X2B}
        a["config"]["kit"] = [dict(k, sha256=kb["sha256"]) for k, kb in zip(a["config"]["kit"], b["config"]["kit"])]
        assert a == b, (p, r["item"]["id"])
        f = copy.deepcopy(r); f["runId"] = f"lite5-off-st20-{p}-s42"; f["config"]["settings"] = {k: v for k, v in f["config"]["settings"].items() if k not in X2B}; offs.append(f)
    w(f"{O}/lite5-on-st20-{p}-s42.requests.jsonl", on); w(f"{O}/lite5-off-st20-{p}-s42.requests.jsonl", offs); n += len(on)
    print(p, len(on), on[0]["config"]["settings"], [(k["id"], k["sha256"][:8]) for k in on[0]["config"]["kit"]])
print("rows", n)
