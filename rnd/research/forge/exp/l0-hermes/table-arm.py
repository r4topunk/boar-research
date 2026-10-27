# Arm tree replay under Hermes -O: flags off vs vectorCache; per question min over reps; warm-up excluded.
import json, glob
def pct(v,p): v=sorted(v); return v[int(p*(len(v)-1)+.5)]
res={}
for cfg in ['none','vectorCache']:
    runs=[json.load(open(f)) for f in sorted(glob.glob(f'out/arm?-{cfg}.json'))]
    rows=[[x for x in r['rows'] if x['id']!='_warmup'] for r in runs]; n=len(rows[0])
    m={k:[min(rr[i][k] for rr in rows) for i in range(n)] for k in ['zstd','utf8','js','compress']}
    tot=[sum(m[k][i] for k in m) for i in range(n)]; res[cfg]=m
    print(f"{cfg:12s} reps {len(runs)} mismatches {[r['mismatch'] for r in runs]}  js p50 {pct(m['js'],.5)} p90 {pct(m['js'],.9)}  JS total p50 {pct(tot,.5)}")
d=[a-b for a,b in zip(res['none']['js'],res['vectorCache']['js'])]
print(f"vectorCache saves (other-JS bucket, Hermes M1): p50 {pct(d,.5)} ms, mean {sum(d)/len(d):.1f} ms per question")
