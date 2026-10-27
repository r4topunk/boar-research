# Dump the zstd blocks the app actually decompressed (cache misses) per question from the L0 recording:
# blobs.bin = [u32 len][bytes]..., blobs.json = per-question lists of blob indexes (warm-up excluded).
import json, base64, struct
d = json.load(open("../l0-hermes/rec/rec.json"))
blobs, idx, per = [], {}, []
for w in d["work"]:
    if w["id"] == "_warmup": continue
    q = []
    for c in w["calls"]:
        if c["sql"].startswith("SELECT zdata FROM blocks"):
            z = base64.b64decode(d["store"][c["h"]]["zdata"]["$b64"])
            key = (c["db"], c["p"][0])
            if key not in idx: idx[key] = len(blobs); blobs.append(z)
            q.append(idx[key])
    per.append(q)
with open("blobs.bin", "wb") as f:
    for b in blobs: f.write(struct.pack("<I", len(b)) + b)
json.dump(per, open("blobs.json", "w"))
print(len(blobs), "unique blobs,", sum(map(len, blobs)) / 1e6, "MB compressed;", sum(map(len, per)), "decompressions over", len(per), "questions")
