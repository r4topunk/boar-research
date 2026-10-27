#!/usr/bin/env python3
"""precheck.py <arm.traces> <control.traces> <idsFile|-> <min> <markers...>: did the arm change the model input vs its control? Prints counts/ids only. rc 0 ok, 8 fail, 2 usage."""
import json, re, sys
NOISE = re.compile(r'^(context:\d+->\d+|detector:p=.*|(timing|latency|ttft|elapsed|wall|tok|tps|ms)[:=].*|.*[:=]\d+(\.\d+)?\s*(ms|s)$)', re.I)
def load(p):
    d = {}
    for ln in open(p):
        ln = ln.strip()
        if ln:
            r = json.loads(ln); d[r.get("itemId")] = r
    return d
def codes(r): return {c for c in ((r.get("route") or {}).get("reasonCodes") or []) if not NOISE.match(c)}
def kept(r): return sorted(k.get("title") if isinstance(k, dict) else str(k) for k in ((r.get("retrieval") or {}).get("kept") or []))
def main():
    if len(sys.argv) < 5: print("usage: precheck.py arm ctl ids|- min [markers...]", file=sys.stderr); return 2
    a, c, ids, mn = load(sys.argv[1]), load(sys.argv[2]), sys.argv[3], float(sys.argv[4]); mk = sys.argv[5:]
    want = None if ids == "-" else [x.strip() for x in open(ids) if x.strip()]
    pool = sorted(set(a) & set(c)) if want is None else [i for i in want if i in a and i in c]
    n = len(pool); ch = []; kd = cd = mc = 0; un = []
    for i in pool:
        ra, rc = a[i], c[i]
        k = kept(ra) != kept(rc); co = codes(ra) != codes(rc)
        m = any(x.startswith(p) for x in (ra.get("route") or {}).get("reasonCodes") or [] for p in mk)
        kd += k; cd += co; mc += m
        (ch if (k or co or m) else un).append(i)
    share = len(ch) / n if n else 0.0
    print(f"precheck: n={n} changed={len(ch)} ({share:.2f}) kept-diff={kd} codes-diff={cd} marker={mc}")
    if 0 < len(un) <= 20: print("unchanged: " + " ".join(un))
    if want is not None and n < len(want): print(f"note: {len(want)-n} ids missing from one of the files")
    if n == 0 or share < mn: print(f"PRECHECK FAIL: input changed on {share:.2f} < {mn:.2f} — do not judge"); return 8
    return 0
sys.exit(main())
