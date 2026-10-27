# 24-item iOS subset (r4to 2026-10-03: <= 20 min on device). Deterministic: the 68 items that retrieved in BOTH
# iPhone P1 reps (be-ios-q15-quick-r1/r2, 2026-10-02), in questions72 order, every 68/24-th; plus 1 warm-up (unmeasured).
# Blocks: items 1-12 = block 1, 13-24 = block 2. Writes ios-items24.jsonl, ios-b1.jsonl, ios-b2.jsonl, ios-warmup.jsonl.
import hashlib, json, pathlib
BE = pathlib.Path("<workspace>/boar-eval")
Q = [json.loads(l) for l in open(BE / "devices/requests/questions72.device.jsonl")]
runs = [BE / f"runs/devices/2026-10-02/ios/be-ios-q15-quick-r{i}/rows.jsonl" for i in (1, 2)]
retrieved = set.intersection(*[{r["queryId"] for r in map(json.loads, open(p)) if r.get("retrievalUsed")} for p in runs])
pool = [q for q in Q if q["id"] in retrieved]
pick = [pool[round(i * len(pool) / 24)] for i in range(24)]
rest = [q for q in pool if q not in pick]
warm = rest[0]
out = pathlib.Path(__file__).parent
def w(name, items):
    p = out / name; p.write_text("".join(json.dumps(q, ensure_ascii=False) + "\n" for q in items))
    print(hashlib.sha256(p.read_bytes()).hexdigest()[:16], name, len(items), " ".join(q["id"] for q in items))
print("pool", len(pool))
w("ios-items24.jsonl", pick); w("ios-b1.jsonl", pick[:12]); w("ios-b2.jsonl", pick[12:]); w("ios-warmup.jsonl", [warm])
from collections import Counter; print(Counter(q.get("category") for q in pick))
