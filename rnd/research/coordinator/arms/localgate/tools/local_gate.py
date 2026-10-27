#!/usr/bin/env python3
"""LOCALGATE harness entry point (local replacement candidate for jev boolean gates).

usage: local_gate.py --type has_fact|quote_supports --in requests.jsonl --out verdicts.jsonl [--th 0.7] [--model GGUF]
input  JSONL: {"rid": str, "state": {"rationale_1": str, "rationale_2": str, "text": str}, ...}  (type taken from --type)
output JSONL: {"rid", "type", "p_local", "mass", "ms", "verdict"(p_local >= th)}; resumable (rids already in --out are skipped).
Runs Qwen3-4B-Instruct-2507 Q4_K_M via node-llama-cpp (Metal) in local_gate.mjs. Prints counts/timings only.
"""
import argparse, json, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument("--type", required=True, choices=["has_fact", "quote_supports"])
ap.add_argument("--in", dest="inp", required=True); ap.add_argument("--out", required=True); ap.add_argument("--th", type=float, default=0.7)
ap.add_argument("--model"); a = ap.parse_args()
with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, dir=os.path.dirname(os.path.abspath(a.out))) as tf:
    n = 0
    for l in open(a.inp):
        if not l.strip(): continue
        r = json.loads(l)
        if r.get("type", a.type) != a.type: continue
        tf.write(json.dumps(dict(rid=r["rid"], type=a.type, state=r["state"]), ensure_ascii=False) + "\n"); n += 1
raw = a.out + ".raw"
cmd = ["node", f"{HERE}/local_gate.mjs", "--in", tf.name, "--out", raw] + (["--model", a.model] if a.model else [])
rc = subprocess.call(cmd); os.unlink(tf.name)
if rc: sys.exit(f"local_gate.mjs failed rc={rc}")
with open(a.out, "w") as fo:
    for l in open(raw):
        r = json.loads(l); r["verdict"] = r["p_local"] >= a.th; fo.write(json.dumps(r) + "\n")
print(json.dumps(dict(type=a.type, requests=n, out=os.path.basename(a.out))))
