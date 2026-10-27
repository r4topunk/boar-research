#!/usr/bin/env python3
"""COVERAGE-MATRIX: KA (A-union) requests (0 LLM). Usage: python3 -I mk_ka_req.py (run from arms/). KA = the LITEPACKS K3 requests with boar-simplewiki-en
replaced in place by boar-visa-en (wave4, sha d1dd0ffb...); every other byte (items, settings, seed 42, the other 5 pack pins) unchanged except runId."""
import json
LP = "litepacks/runs/req"; CM = "coverage-matrix/req"
VISA = {"id": "boar-visa-en", "sha256": "d1dd0ffb58a8e4f9b50a6a21cb164bdb314a7181eb2803c952db21e21359ad20"}
for s in ("v01", "cm", "st"):
    with open(f"{CM}/lp-KA-{s}-s42.requests.jsonl", "w") as f:
        for l in open(f"{LP}/lp-K3-{s}-s42.requests.jsonl"):
            r = json.loads(l); r["runId"] = f"lp-KA-{s}-s42"
            r["config"]["kit"] = [VISA if p["id"] == "boar-simplewiki-en" else p for p in r["config"]["kit"]]
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("ok")
