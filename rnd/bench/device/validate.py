#!/usr/bin/env python3
"""Validate device-metrics JSON files against device-metrics.schema.json.
Uses `jsonschema` (pip install jsonschema) when available; otherwise checks required keys and top-level types only.
Usage: python3 validate.py file.json [file.json ...]"""
import json, os, sys
schema = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "device-metrics.schema.json")))
try:
    import jsonschema
    V = jsonschema.Draft202012Validator(schema)
except ImportError:
    V = None
bad = 0
for f in sys.argv[1:]:
    d = json.load(open(f))
    if V:
        errs = sorted(V.iter_errors(d), key=lambda e: list(e.path))
        msgs = [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errs]
    else:
        msgs = [f"missing '{k}'" for k in schema["required"] if k not in d]
    bad += bool(msgs)
    print(("OK  " if not msgs else "FAIL") + f" {f}" + ("" if V else "  (minimal check: install jsonschema for full validation)"))
    for m in msgs[:10]:
        print("     ", m)
sys.exit(1 if bad else 0)
