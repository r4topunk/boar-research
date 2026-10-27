#!/usr/bin/env python3
"""LITE5-180 requests (0 LLM). Run: python3 -I mkreq_180.py
ON  = headpass-st/gen-x2b/st-<pack>-cut7-headpassx2b-s42.requests.jsonl (4B X2b, 20 per pack) with modelId -> qwen3-1.7b-q4km, runId lite5-180-on-<pack>-s42.
OFF = the same rows minus the two X2b settings, runId lite5-180-off-<pack>-s42.
Checks: ON == 4B X2b request apart from runId + modelId; OFF == 4B plain request (packs/selftest-runs/st-<pack>-cut7-s42) apart from runId, arm, modelId, item-pack kit sha;
on the selftest20 ids ON/OFF == LITE5's lite5-{on,off}-st20 rows apart from runId."""
import json, copy
A = "<workspace>/rnd/research/coordinator/arms"; O = f"{A}/lite5/runs/180"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
X2B = ("packHeadPass", "packDense2"); M = "qwen3-1.7b-q4km"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
w = lambda p, rows: open(p, "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
L5 = {}
for m in ("on", "off"):
    for p in PACKS:
        try: L5.update({(m, r["item"]["id"]): r for r in rd(f"{A}/lite5/runs/lite5-{m}-st20-{p}-s42.requests.jsonl")})
        except FileNotFoundError: pass
n = s20 = 0
for p in PACKS:
    x = rd(f"{A}/headpass-st/gen-x2b/st-{p}-cut7-headpassx2b-s42.requests.jsonl"); s = {r["item"]["id"]: r for r in rd(f"{A}/packs/selftest-runs/st-{p}-cut7-s42.requests.jsonl")}
    assert len(x) == 20 and [r["item"]["id"] for r in x] == list(s), p
    on, off = [], []
    for r in x:
        assert r["config"]["modelId"] == "qwen3-4b-instruct-2507-q4km" and r["seed"] == 42
        a = copy.deepcopy(r); a["config"]["modelId"] = M; a["runId"] = f"lite5-180-on-{p}-s42"
        f = copy.deepcopy(a); f["runId"] = f"lite5-180-off-{p}-s42"; f["config"]["settings"] = {k: v for k, v in f["config"]["settings"].items() if k not in X2B}
        b = s[r["item"]["id"]]; c = copy.deepcopy(f)
        c["runId"] = b["runId"]; c["config"]["arm"] = b["config"]["arm"]; c["config"]["modelId"] = b["config"]["modelId"]
        c["config"]["kit"] = [dict(k, sha256=kb["sha256"]) for k, kb in zip(c["config"]["kit"], b["config"]["kit"])]
        assert c == b, ("off vs 4B plain", p, r["item"]["id"])
        for m, q in (("on", a), ("off", f)):
            if (m, q["item"]["id"]) in L5:
                y = copy.deepcopy(q); y["runId"] = L5[(m, q["item"]["id"])]["runId"]; assert y == L5[(m, q["item"]["id"])], ("vs LITE5", m, q["item"]["id"]); s20 += 1
        on.append(a); off.append(f)
    w(f"{O}/lite5-180-on-{p}-s42.requests.jsonl", on); w(f"{O}/lite5-180-off-{p}-s42.requests.jsonl", off); n += len(on)
    print(p, len(on), on[0]["config"]["settings"], off[0]["config"]["settings"])
print("rows per arm", n, "| equal to LITE5 st20 rows:", s20, "of 40")
