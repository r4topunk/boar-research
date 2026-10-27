#!/usr/bin/env python3 -I
"""DRY-RUN stand-in for label.mjs (NO LLM): writes deterministic fake labels in label.mjs's output format. usage: m34_fakelabel.py units.json labels.jsonl"""
import json, sys
LAB = ["CORRECT_WITH_SOURCE", "CORRECT_FROM_MEMORY", "HONEST_UNKNOWN", "REFUSED_WRONGLY", "WRONG_WARNED", "WRONG_CONFIDENT"]
with open(sys.argv[2], "w") as o:
    for n, u in enumerate(json.load(open(sys.argv[1]))["units"]):
        o.write(json.dumps(dict(key=u["key"], id=u["id"], call="A", label=LAB[n % 6], source_holds=n % 2 == 0, conf="clear", ok=True, tries=1)) + "\n")
