#!/usr/bin/env python3
"""ORACLE-ST requests = the S runs' requests (arms/packs/selftest-runs/st-<pack>-cut7-s42.requests.jsonl: claim config + kit + the pack, seed 42)
byte-for-byte except runId -> st-<pack>-cut7-<cell>-s42 and config.arm -> cut7-oracle (tree label). Usage: python3 -I mkreq.py <cell: oracleadd|oracleonly|off3>"""
import json, sys
ROOT = "$BOAR_WS"; SR = f"{ROOT}/rnd/research/coordinator/arms/packs/selftest-runs"; OUT = f"{ROOT}/rnd/research/coordinator/arms/oracle-st/runs"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
cell = sys.argv[1]
for p in PACKS:
    rows = [json.loads(l) for l in open(f"{SR}/st-{p}-cut7-s42.requests.jsonl") if l.strip()]
    assert len(rows) == 20 and all(r["runId"] == f"st-{p}-cut7-s42" for r in rows)
    run = f"st-{p}-cut7-{cell}-s42"
    for r in rows: r["runId"] = run; r["config"]["arm"] = "cut7-oracle"  # the adapter checks config.arm == tree ARM (label only)
    open(f"{OUT}/{run}.requests.jsonl", "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    print(run, len(rows), [k["id"] for k in rows[0]["config"]["kit"]])
