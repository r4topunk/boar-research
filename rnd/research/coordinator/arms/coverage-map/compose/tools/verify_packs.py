"""sha256 of every pack file used vs its manifest sidecar (<file>.json 'sha256', or <file-stem>.sha256 for wave4). python3 -I tools/verify_packs.py -> verify.json"""
import json, hashlib, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kits
files = sorted({f for n in (0, 2, 4, 6, 8, 10) for f in kits.kit(n)})
out = {}
for f in files:
    h = hashlib.sha256()
    with open(f, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 22), b""): h.update(b)
    man = None
    if os.path.exists(f + ".json"): man = json.load(open(f + ".json")).get("sha256")
    side = None
    if os.path.exists(f + ".sha256"): side = open(f + ".sha256").read().split()[0]
    ok = [x == h.hexdigest() for x in (man, side) if x]
    out[f] = dict(sha256=h.hexdigest(), manifest=man, sha_sidecar=side, size=os.path.getsize(f), verdict=("OK" if ok and all(ok) else "MISMATCH" if ok else "NO-MANIFEST"))
    print(os.path.basename(f), out[f]["verdict"], h.hexdigest()[:12])
json.dump(out, open(os.path.dirname(os.path.abspath(__file__)) + "/../verify.json", "w"), indent=1)
