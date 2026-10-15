#!/usr/bin/env python3
"""HEADPASS-ST stage 1 requests (component estimate; coordinator decision 2026-10-14). Run: python3 -I mkreq.py
- 180 ON: the S requests (arms/packs/selftest-runs/st-<pack>-cut7-s42.requests.jsonl: claim config + kit + the pack, seed 42) byte-for-byte
  except runId -> st-<pack>-cut7-headpass-s42, config.arm -> cut7-headpass (tree label), config.settings += {packHeadPass: "a2"}.
- v0.1 public 60 + boar-simplewiki-en: the S simplewiki config (kit crypto, wikivoyage, simplewiki; seed 42), arm cut7-headpass, items =
  boar-eval/bench/v0.1/questions.public.jsonl (stack/tools/mkreq.py item shape); OFF (settings as S) / ON (+ packHeadPass "a2"),
  runIds v01sw-cut7-headpass-off-s42 / v01sw-cut7-headpass-on-s42. Out: gen/<runId>.requests.jsonl"""
import json, copy
ROOT = "$BOAR_WS"; A = f"{ROOT}/rnd/research/coordinator/arms"; O = f"{A}/headpass-st/gen"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
HP = {"packHeadPass": "a2"}
def write(path, rows): open(path, "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
sw = None
for p in PACKS:
    rows = [json.loads(l) for l in open(f"{A}/packs/selftest-runs/st-{p}-cut7-s42.requests.jsonl") if l.strip()]
    assert len(rows) == 20 and all(r["runId"] == f"st-{p}-cut7-s42" and r["config"]["arm"] == "cut7" for r in rows)
    if p == "boar-simplewiki-en": sw = copy.deepcopy(rows[0])
    run = f"st-{p}-cut7-headpass-s42"
    for r in rows: r["runId"] = run; r["config"]["arm"] = "cut7-headpass"; r["config"]["settings"] = {**r["config"]["settings"], **HP}
    write(f"{O}/{run}.requests.jsonl", rows); print(run, len(rows), [k["id"] for k in rows[0]["config"]["kit"]], rows[0]["config"]["settings"], rows[0]["seed"])
assert [k["id"] for k in sw["config"]["kit"]] == ["boar-crypto", "boar-wikivoyage-en", "boar-simplewiki-en"]
items = [json.loads(l) for l in open(f"{ROOT}/boar-eval/bench/v0.1/questions.public.jsonl") if l.strip()]
for tag, extra in (("off", {}), ("on", HP)):
    c = copy.deepcopy(sw["config"]); c["arm"] = "cut7-headpass"; c["settings"] = {**c["settings"], **extra}; run = f"v01sw-cut7-headpass-{tag}-s42"
    rows = [{"protocol": sw["protocol"], "runId": run, "item": {"id": it["id"], "question": it["question"], "lang": it.get("lang", "en"), **({"history": it["history"]} if it.get("history") else {})},
             "config": c, "seed": sw["seed"]} for it in items]
    write(f"{O}/{run}.requests.jsonl", rows); print(run, len(rows), [k["id"] for k in c["kit"]], c["settings"], sw["seed"])
