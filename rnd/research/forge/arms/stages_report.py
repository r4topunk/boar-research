#!/usr/bin/env python3
"""Per-run retrieval stage table from device rows (receipt.retrievalStages, arm build), plus ratios vs a reference run
and the M1-Hermes -> phone calibration of the L0 scaling (x2.4).

  python3 stages_report.py RUN_DIR [RUN_DIR ...] [--ref RUN_DIR]
RUN_DIR = an android-run.sh output dir (rows.jsonl inside) or a rows.jsonl path. Rows without retrievalStages
(no retrieval, or a build without the arm) are skipped and counted.
"""
import json, pathlib, statistics, sys

L0_M1_HERMES = {"zstdMs_p50": 499.0, "utf8Ms_p50": 32.0}  # forge/README.md §1 (hbc -O, M1 Pro)
KEYS = ["retrievalMs", "ttftMs", "zstdMs", "zstdBlocks", "zstdFallbacks", "utf8Ms", "sqlMs", "sqlCalls", "corpusSqlMs",
        "corpusScoreMs", "embedMs", "b.lexical", "b.semantic", "b.packs", "b.wiki"]

def rows_of(p):
    p = pathlib.Path(p)
    f = p / "rows.jsonl" if p.is_dir() else p
    return f, [json.loads(l) for l in f.read_text().splitlines() if l.strip()]

def pct(v, q):
    v = sorted(v)
    return v[min(len(v) - 1, int(q * (len(v) - 1) + 0.5))] if v else float("nan")

def table(path):
    f, rows = rows_of(path)
    out, skipped, perf, mb = {k: [] for k in KEYS}, 0, set(), []
    for r in rows:
        rc = r.get("receipt") or {}
        s = rc.get("retrievalStages")
        if not s:
            skipped += 1
            continue
        perf.add(json.dumps(s.get("perf"), sort_keys=True))
        out["retrievalMs"].append(rc.get("retrievalMs", float("nan")))
        out["ttftMs"].append(rc.get("ttftMs", float("nan")))
        for k in KEYS[2:11]:
            out[k].append(s.get(k, 0))
        for b in ("lexical", "semantic", "packs", "wiki"):
            out["b." + b].append(s.get("branches", {}).get(b, 0))
        if s.get("zstdOutBytes"):
            mb.append(s["zstdMs"] / (s["zstdOutBytes"] / 1e6))
    return {"file": str(f), "n": len(out["retrievalMs"]), "skipped": skipped, "perf": sorted(perf), "v": out,
            "zstd_ms_per_MB_p50": pct(mb, 0.5) if mb else None}

def main(argv):
    ref = None
    if "--ref" in argv:
        i = argv.index("--ref"); ref = table(argv[i + 1]); argv = argv[:i] + argv[i + 2:]
    runs = [table(a) for a in argv]
    for t in runs:
        print(f"\n{t['file']}  n={t['n']} (skipped {t['skipped']})  perf={' | '.join(t['perf'])}")
        print(f"  {'stage':14s} {'p50':>9s} {'p90':>9s} {'mean':>9s}" + ("   p50/ref" if ref else ""))
        for k in KEYS:
            v = t["v"][k]
            if not v:
                continue
            line = f"  {k:14s} {pct(v, .5):9.1f} {pct(v, .9):9.1f} {statistics.mean(v):9.1f}"
            if ref and ref["v"][k] and pct(ref["v"][k], .5):
                line += f"   {pct(v, .5) / pct(ref['v'][k], .5):6.2f}x"
            print(line)
        if t["zstd_ms_per_MB_p50"] is not None:
            print(f"  zstd ms per MB out p50: {t['zstd_ms_per_MB_p50']:.1f}")
        zp50 = pct(t["v"]["zstdMs"], .5)
        if zp50 == zp50 and zp50 > 0 and not any('"nativeZstd": true' in p for p in t["perf"]):
            print(f"  calibration: phone fzstd p50 {zp50:.0f} ms / M1 Hermes L0 {L0_M1_HERMES['zstdMs_p50']:.0f} ms = x{zp50 / L0_M1_HERMES['zstdMs_p50']:.2f}"
                  "  (L0 assumed x2.4; only meaningful on the 64 KB packs; a release run gives the Hermes ratio, a dev run the dev ratio)")

if __name__ == "__main__":
    main(sys.argv[1:])
