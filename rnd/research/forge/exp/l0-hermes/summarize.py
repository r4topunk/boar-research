# Summarize replay outputs: per-stage p50/p90 per question and share of the pack+corpus JS total (warm-up row excluded).
import json, sys, statistics as st
def pct(v, p): v = sorted(v); return v[min(len(v) - 1, int(p * (len(v) - 1) + 0.5))]
for f in sys.argv[1:]:
    d = json.load(open(f)); r = [x for x in d["rows"] if x["id"] != "_warmup"]
    work = [x["total"] - x["sqlReplay"] - x["embedReplay"] for x in r]
    print(f"{f}: engine={d['engine']} polyTextDecoder={d['poly']} n={len(r)} mismatches={d['mismatch']} sqlMiss={sum(x['sqlMiss'] for x in r)}")
    tot = sum(work) + sum(x["compress"] for x in r)
    for k in ["zstd", "utf8", "js", "compress"]:
        v = [x[k] for x in r]
        print(f"  {k:9s} p50 {pct(v,.5):8.1f}  p90 {pct(v,.9):8.1f}  mean {st.mean(v):8.1f}  share {100*sum(v)/tot:5.1f}%")
    print(f"  {'JS total':9s} p50 {pct([a+x['compress'] for a,x in zip(work,r)],.5):8.1f}  p90 {pct([a+x['compress'] for a,x in zip(work,r)],.9):8.1f}  mean {st.mean([a+x['compress'] for a,x in zip(work,r)]):8.1f}")
    print(f"  harness   sqlReplay p50 {pct([x['sqlReplay'] for x in r],.5):.1f}  calls/q p50 {pct([x['sqlCalls'] for x in r],.5)}  zstd blocks/q p50 {pct([x['nZstd'] for x in r],.5)}  utf8 MB/q p50 {pct([x['utf8Bytes'] for x in r],.5)/1e6:.2f}")
