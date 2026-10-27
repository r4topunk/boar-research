#!/usr/bin/env python3
"""Ids whose answer text differs between two trace files (ON vs arm), optionally restricted to an ids file. Usage: changed_ids.py <on traces> <arm traces> [ids]"""
import json, sys
rd = lambda f: {json.loads(l)["itemId"]: json.loads(l)["answer"]["text"] for l in open(f) if l.strip()}
a, b = rd(sys.argv[1]), rd(sys.argv[2]); keep = set(open(sys.argv[3]).read().split()) if len(sys.argv) > 3 else None
for i in a:
    if (keep is None or i in keep) and a[i] != b[i]: print(i)
