# Stage table across reps: per question, each stage's MIN over the 3 reps (the MacBook is shared; min = least-interfered),
# then p50 / mean over the 68 retrievals. Shares are of the summed JS work (zstd + utf8 + js + compress).
import json, glob, statistics as st
def pct(v, p): v = sorted(v); return v[min(len(v) - 1, int(p * (len(v) - 1) + 0.5))]
STAGES = ["zstd", "utf8", "js", "compress"]
res = {}
for cfg in ["node-jit", "node-jit-poly", "node-jitless", "hermes-hbc-O", "hermes-src-lazy"]:
    runs = [json.load(open(f)) for f in sorted(glob.glob(f"out/r?-{cfg}.json"))]
    assert all(r["mismatch"] == 0 for r in runs), cfg
    rows = [[x for x in r["rows"] if x["id"] != "_warmup"] for r in runs]
    n = len(rows[0])
    m = {s: [min(rr[i][s] for rr in rows) for i in range(n)] for s in STAGES}
    m["total"] = [sum(m[s][i] for s in STAGES) for i in range(n)]
    res[cfg] = m
    tot = sum(m["total"])
    print(f"\n{cfg} (reps {len(runs)}, n {n}, TextDecoder {'Expo JS polyfill' if runs[0]['poly'] else 'native'})")
    for s in STAGES + ["total"]:
        print(f"  {s:9s} p50 {pct(m[s], .5):8.1f}  p90 {pct(m[s], .9):8.1f}  mean {st.mean(m[s]):8.1f}  share {100 * sum(m[s]) / tot:5.1f}%")
h, v = res["hermes-hbc-O"], res["node-jit-poly"]
print("\nratios (sum over questions):")
for a, b in [("hermes-hbc-O", "node-jit"), ("hermes-hbc-O", "node-jit-poly"), ("hermes-src-lazy", "hermes-hbc-O"), ("node-jitless", "node-jit")]:
    print(f"  {a} / {b}: total {sum(res[a]['total']) / sum(res[b]['total']):.1f}x  zstd {sum(res[a]['zstd']) / sum(res[b]['zstd']):.1f}x  js {sum(res[a]['js']) / sum(res[b]['js']):.1f}x")
json.dump({k: {s: v for s, v in m.items()} for k, m in res.items()}, open("out/table.json", "w"))
