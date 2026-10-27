#!/usr/bin/env python3
"""Paired A (flags off) vs B (vectorCache + sqlBatch) report for the iOS 24-item session (IOS-SESSION.md).

  python3 paired_report.py --a A1_DIR A2_DIR --b B1_DIR B2_DIR

Pairs rows by queryId. Per stage: median of A, median of B, median of per-item B/A ratios, and how many items got
faster in B. Then the guards: retrieved titles and answer text identical per item (the arms change no output on the
desktop: Kiln step 0, 72/72). The first item of each block is listed apart (cold DB / cache fill).
"""
import json, pathlib, statistics, sys

STAGES = ["retrievalMs", "zstdMs", "utf8Ms", "sqlMs", "sqlCalls", "corpusSqlMs", "corpusScoreMs", "embedMs", "ttftMs"]

def rows(d):
    p = pathlib.Path(d)
    f = p / "rows.jsonl" if p.is_dir() else p
    return [json.loads(l) for l in f.read_text().splitlines() if l.strip()]

def stage(r, k):
    rc = r.get("receipt") or {}
    if k in ("retrievalMs", "ttftMs"):
        return rc.get(k)
    return (rc.get("retrievalStages") or {}).get(k)

def main(argv):
    ia, ib = argv.index("--a"), argv.index("--b")
    a_dirs = argv[ia + 1:ib] if ia < ib else argv[ia + 1:]
    b_dirs = argv[ib + 1:ia] if ib < ia else argv[ib + 1:]
    A, B, firsts = {}, {}, []
    for dirs, side in ((a_dirs, A), (b_dirs, B)):
        for d in dirs:
            rs = rows(d)
            if rs:
                firsts.append((d, rs[0]["queryId"], stage(rs[0], "retrievalMs")))
            for r in rs:
                side[r["queryId"]] = r
    ids = [q for q in A if q in B]
    print(f"pairs {len(ids)} (A {len(A)}, B {len(B)})")
    perf_b = {json.dumps((B[q].get("receipt") or {}).get("retrievalStages", {}).get("perf"), sort_keys=True) for q in ids}
    perf_a = {json.dumps((A[q].get("receipt") or {}).get("retrievalStages", {}).get("perf"), sort_keys=True) for q in ids}
    print(f"perf A {sorted(perf_a)}\nperf B {sorted(perf_b)}")
    print(f"{'stage':14s} {'A p50':>9s} {'B p50':>9s} {'B/A med':>8s} {'B<A':>6s}")
    for k in STAGES:
        pa = [(stage(A[q], k), stage(B[q], k)) for q in ids]
        pa = [(x, y) for x, y in pa if isinstance(x, (int, float)) and isinstance(y, (int, float))]
        if not pa:
            continue
        ratios = [y / x for x, y in pa if x > 0]
        print(f"{k:14s} {statistics.median(x for x, _ in pa):9.0f} {statistics.median(y for _, y in pa):9.0f} "
              f"{(statistics.median(ratios) if ratios else float('nan')):8.2f} {sum(y < x for x, y in pa):3d}/{len(pa)}")
    same_src = sum(A[q].get("retrievedTitles") == B[q].get("retrievedTitles") for q in ids)
    same_ans = sum(A[q].get("answer") == B[q].get("answer") for q in ids)
    print(f"guard: retrievedTitles identical {same_src}/{len(ids)}; answer text identical {same_ans}/{len(ids)}")
    for q in ids:
        if A[q].get("retrievedTitles") != B[q].get("retrievedTitles"):
            print(f"  sources differ: {q}")
    print("first item per block (cold path, inside the table above too):")
    for d, q, ms in firsts:
        print(f"  {pathlib.Path(d).name}: {q} retrievalMs {ms}")

if __name__ == "__main__":
    main(sys.argv[1:])
