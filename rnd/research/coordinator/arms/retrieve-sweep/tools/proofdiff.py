"""Switch-off identity: raw/wide/kept chunk ids + reason codes of an off-run vs the reference replay, per shared id."""
import json, sys
ref = {json.loads(l)["id"]: json.loads(l) for l in open(sys.argv[1]) if l.strip()}
run = [json.loads(l) for l in open(sys.argv[2]) if l.strip()]
same = {k: 0 for k in ("raw", "wide", "kept", "codes")}
for r in run:
    b = ref[r["id"]]
    ids = lambda x, k: [c["chunkId"] for c in x[k]]
    same["raw"] += ids(r, "rawFull") == ids(b, "rawFull")
    same["wide"] += ids(r, "wideFull") == ids(b, "wideFull")
    same["kept"] += ids(r, "keptFull") == ids(b, "keptFull")
    same["codes"] += r["reasonCodes"] == b["reasonCodes"]
print(json.dumps({"n": len(run), **{k: f"{v}/{len(run)}" for k, v in same.items()}}))
