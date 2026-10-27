"""Writes the replay input (one row per trace with >= 1 source) for tools/replay.mts."""
import json, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from sets import load
with open(sys.argv[1], "w") as f:
    for name, rows in load().items():
        for r in rows:
            if r["sources"]: f.write(json.dumps({"set": name, **r}, ensure_ascii=False) + "\n")
