#!/usr/bin/env python3
"""HEADPASS-X2b stage 1 requests (criterion HEADPASS-X2-criterion.md 1b70f6f3… + addendum 1 a66a3b79…). Run: python3 -I mkreq_x2b.py
- 180 ON: the S requests (arms/packs/selftest-runs/st-<pack>-cut7-s42.requests.jsonl) byte-for-byte except runId ->
  st-<pack>-cut7-headpassx2b-s42, config.arm -> cut7-headpass-x2 (tree ARM), settings += {packHeadPass "a2", packDense2 "append-budget"},
  and the item pack's kit sha256 -> its sidecar copy in shared-data/packs/v3proto (aggregates/sidecars.mini.sha256; the adapter finds
  it first via BOAR_EVAL_PACK_DIRS). Kit packs (crypto, wikivoyage) unchanged (no sidecars).
- v0.1 public 60 + boar-simplewiki-en (sidecar copy), OFF (settings as S) / ON (+ the two settings): runIds v01-sw-cut7-x2b-{off,on}-s42.
Out: gen-x2b/<runId>.requests.jsonl"""
import json, copy
ROOT = "$BOAR_WS"; A = f"{ROOT}/rnd/research/coordinator/arms"; H = f"{A}/headpass-st"; O = f"{H}/gen-x2b"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
SC = {l.split()[1].removesuffix(".sqlite"): l.split()[0] for l in open(f"{H}/aggregates/sidecars.mini.sha256") if l.strip()}
ON = {"packHeadPass": "a2", "packDense2": "append-budget"}; ARM = "cut7-headpass-x2"
def write(path, rows): open(path, "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
def sidecar_kit(kit, p):
    out = [dict(k) for k in kit]; hit = [k for k in out if k["id"] == p]; assert len(hit) == 1; hit[0]["sha256"] = SC[p]; return out
sw = None
for p in PACKS:
    rows = [json.loads(l) for l in open(f"{A}/packs/selftest-runs/st-{p}-cut7-s42.requests.jsonl") if l.strip()]
    assert len(rows) == 20 and all(r["runId"] == f"st-{p}-cut7-s42" and r["config"]["arm"] == "cut7" for r in rows)
    if p == "boar-simplewiki-en": sw = copy.deepcopy(rows[0])
    run = f"st-{p}-cut7-headpassx2b-s42"
    for r in rows:
        r["runId"] = run; r["config"]["arm"] = ARM; r["config"]["settings"] = {**r["config"]["settings"], **ON}; r["config"]["kit"] = sidecar_kit(r["config"]["kit"], p)
    write(f"{O}/{run}.requests.jsonl", rows); print(run, len(rows), [(k["id"], k["sha256"][:8]) for k in rows[0]["config"]["kit"]], rows[0]["config"]["settings"], rows[0]["seed"])
assert [k["id"] for k in sw["config"]["kit"]] == ["boar-crypto", "boar-wikivoyage-en", "boar-simplewiki-en"]
items = [json.loads(l) for l in open(f"{ROOT}/boar-eval/bench/v0.1/questions.public.jsonl") if l.strip()]
for tag, extra in (("off", {}), ("on", ON)):
    c = copy.deepcopy(sw["config"]); c["arm"] = ARM; c["settings"] = {**c["settings"], **extra}; c["kit"] = sidecar_kit(c["kit"], "boar-simplewiki-en")
    run = f"v01-sw-cut7-x2b-{tag}-s42"
    rows = [{"protocol": sw["protocol"], "runId": run, "item": {"id": it["id"], "question": it["question"], "lang": it.get("lang", "en"), **({"history": it["history"]} if it.get("history") else {})},
             "config": c, "seed": sw["seed"]} for it in items]
    write(f"{O}/{run}.requests.jsonl", rows); print(run, len(rows), [(k["id"], k["sha256"][:8]) for k in c["kit"]], c["settings"], sw["seed"])
