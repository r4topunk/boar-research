#!/usr/bin/env python3
"""Check downloaded trace files against TRACES.tsv (path, bytes, sha256). Missing files are reported, not errors."""
import hashlib, os, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ok = bad = missing = 0
for i, line in enumerate(open(os.path.join(root, "TRACES.tsv"))):
    if i == 0: continue
    path, size, sha = line.rstrip("\n").split("\t")
    p = os.path.join(root, path)
    if not os.path.exists(p): missing += 1; continue
    if hashlib.sha256(open(p, "rb").read()).hexdigest() == sha: ok += 1
    else: bad += 1; print("MISMATCH", path)
print(f"ok {ok}  mismatch {bad}  not downloaded {missing}")
sys.exit(1 if bad else 0)
