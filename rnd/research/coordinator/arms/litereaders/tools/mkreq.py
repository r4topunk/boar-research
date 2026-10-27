#!/usr/bin/env python3
"""LITEREADERS requests (0 LLM). Run: python3 -I tools/mkreq.py
random20 = random.Random(777).sample(sorted(180 self-test ids), 20); smoke3 = 3 ids outside random20 whose 4B ADD trace is tier fast (random.Random(778), one SE, one topic, one more).
Rows = ORACLE-ST ADD requests (oracle-st/runs/st-<pack>-cut7-oracleadd-s42.requests.jsonl) byte-equal apart from config.modelId and runId
(lr-<reader>-<slice>-<pack>-s42). One file per pack (one config per file)."""
import json, random, copy
A = "<workspace>/rnd/research/coordinator/arms"; H = f"{A}/litereaders"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
READERS = {"q17": "qwen3-1.7b-q4km", "lfm": "lfm2-1.2b-q4km", "g1": "gemma-3-1b-it-q4km"}
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ROWS = {}
for p in PACKS:
    for r in rd(f"{A}/oracle-st/runs/st-{p}-cut7-oracleadd-s42.requests.jsonl"):
        assert r["config"]["modelId"] == "qwen3-4b-instruct-2507-q4km" and r["seed"] == 42; ROWS[r["item"]["id"]] = (p, r)
ids = sorted(ROWS); assert len(ids) == 180
r20 = sorted(random.Random(777).sample(ids, 20)); rest = [i for i in ids if i not in r20]
FAST = {t["itemId"] for p in PACKS for t in rd(f"{A}/oracle-st/runs/st-{p}-cut7-oracleadd-s42.traces.jsonl") if t["route"]["tier"] == "fast"}
rest = [i for i in rest if i in FAST]  # smoke items must reach the LLM in the 4B ADD trace
rng = random.Random(778); se = [i for i in rest if i.startswith("st-qa-")]; tp = [i for i in rest if not i.startswith("st-qa-")]
a, b = rng.choice(se), rng.choice(tp); s3 = sorted([a, b, rng.choice([i for i in rest if i not in (a, b)])])
open(f"{H}/random20.ids", "w").write("\n".join(r20) + "\n"); open(f"{H}/smoke3.ids", "w").write("\n".join(s3) + "\n")
runs = []
for sl, sel in (("smoke", s3), ("r20", r20)):
    for k, m in READERS.items():
        for p in PACKS:
            rows = []
            for i in sel:
                if ROWS[i][0] != p: continue
                x = copy.deepcopy(ROWS[i][1]); x["config"]["modelId"] = m; x["runId"] = f"lr-{k}-{sl}-{p}-s42"; rows.append(x)
            if rows:
                open(f"{H}/runs/lr-{k}-{sl}-{p}-s42.requests.jsonl", "w").write("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows)); runs.append(f"lr-{k}-{sl}-{p}-s42")
open(f"{H}/runs/RUNS", "w").write("\n".join(runs) + "\n")
print("random20", r20); print("smoke3", s3); print(len(runs), "runs")
