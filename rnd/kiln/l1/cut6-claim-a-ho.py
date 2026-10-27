#!/usr/bin/env python3
"""Cut 6 claim run A: held-out (v0.2-new, 110 items) paired deltas vs cut3 / ship / e3 (same method as the cut 3 claim run's paired-ho: judgments restricted to the
v0.2-new ids, paired_gap.py stratified two-level). Aggregates only; writes blind/bench-v02/runs-cut6/paired-ho-cut6-vs-*.json."""
import json, subprocess, sys
from pathlib import Path
B = Path("<private held-out dir>"); OUT = B / "runs-cut6"; P = OUT / "paired-ho"; P.mkdir(exist_ok=True)
Q = B / "live/v0.2/questions.v02-new.jsonl"; ids = {json.loads(l)["id"] for l in open(Q) if l.strip()}
src = {f"cut6-s{s}": OUT / f"cut6-v02-s{s}" for s in (42, 43)} | {f"cut3-s{s}": B / f"runs-cut3/cut3-v02-s{s}" for s in (42, 43)} | {f"ship-s{s}": B / f"runs-ship/ship-v02-s{s}" for s in (42, 43)} | {f"e3-s{s}": B / f"runs-e3/v02all-s{s}" for s in (42, 43)}
for k, p in src.items():
    rows = [l for l in open(str(p) + ".judgments.jsonl") if l.strip() and json.loads(l)["queryId"] in ids]
    (P / f"{k}.judgments.jsonl").write_text("".join(rows)); print(k, len(rows), "rows")
PG = "<workspace>/boar-eval/bench/v0.2/plan/paired_gap.py"
for b in ("cut3", "ship", "e3"):
    r = subprocess.run([sys.executable, PG, "--dir", str(P), "--a", "cut6-s42", "cut6-s43", "--b", f"{b}-s42", f"{b}-s43", "--questions", str(Q), "--decline-ratio", "0.306"], capture_output=True, text=True)
    (OUT / f"paired-ho-cut6-vs-{b}.json").write_text(r.stdout); j = json.loads(r.stdout)
    print(b, j["n_items"], {k: (j[k]["gap_a_minus_b"], j[k]["ci95"]) for k in ("raw", "above_min", "above_decl")})
