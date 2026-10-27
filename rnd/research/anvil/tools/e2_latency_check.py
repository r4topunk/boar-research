#!/usr/bin/env python3
"""E2 latency check (Anvil card android-4b-latency-budget): EvalTrace jsonl -> the card's numbers + decision branch.

Reads boar-eval EvalTrace files (desktop-node traces, or device rows converted by scorers/convert_device.py).
Only LLM-generated answers count (route.tier fast|deep, outputTokens > 0): instant/places/health-extractive rows
have no model latency. Read-only; prints a small report. Stdlib only.

  python3 e2_latency_check.py TRACES.jsonl [TRACES2.jsonl ...] [--label NAME] [--device d8300|g75]

Fields used (first one present wins):
  first visible  timing.firstVisibleMs | event other/first-token tMs | timing.ttftMs
  total          timing.totalMs
  prefill rate   (promptTokens - cachedTokens) / prefillMs   (cachedTokens from a receipt event, else 0)
  decode rate    timing.decodeTokPerSec
  first sources  event other/first-sources tMs (for the 'does the preview count' question)
"""
import json, statistics as st, sys

# Frozen 2026-10-02 before E2 (card android-4b-latency-budget §2): Qwen3-4B on the Dimensity 8300.
PREDS = {
    "d8300": {"first_visible_p50": (10.0, 13.0), "total_p50": (22.0, 28.0), "prefill_tok_s": (20.0, 30.0), "decode_tok_s": (4.0, 6.0)},
    # frozen 2026-10-02 ~18:45 before any run on r4to's moto g75 5G (Snapdragon 6 Gen 3, 8 GB) (card §2b)
    "g75": {"first_visible_p50": (15.0, 21.0), "total_p50": (33.0, 45.0), "prefill_tok_s": (12.0, 18.0), "decode_tok_s": (2.5, 3.8)},
}
PRED = PREDS["d8300"]
BAR = {"first_visible_p50": 8.0, "total_p50": 15.0}   # S1 E2 bar
K3 = 25.0


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(p * len(xs)))] if xs else None


def event_ms(r, kind):
    for e in r.get("events") or []:
        if e.get("type") == "other" and e.get("kind") == kind and isinstance(e.get("tMs"), (int, float)):
            return e["tMs"]
    return None


def cached_tokens(r):
    for e in r.get("events") or []:
        if e.get("type") == "other" and e.get("kind") == "receipt":
            v = e.get("cachedTokens") or (e.get("receipt") or {}).get("cachedTokens")
            if isinstance(v, (int, float)):
                return v
    return 0


def rows_of(paths):
    for p in paths:
        for line in open(p):
            if line.strip():
                yield json.loads(line)


def main(argv):
    label = None
    global PRED
    if "--device" in argv:
        i = argv.index("--device"); PRED = PREDS[argv[i + 1]]; argv = argv[:i] + argv[i + 2:]
    if "--label" in argv:
        i = argv.index("--label"); label = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    fv, tot, pre, dec, src, n_all = [], [], [], [], [], 0
    for r in rows_of(argv):
        n_all += 1
        t = r.get("timing") or {}
        tier = (r.get("route") or {}).get("tier")
        if tier not in ("fast", "deep") or not (t.get("outputTokens") or 0) > 0 or r.get("error"):
            continue
        f = t.get("firstVisibleMs") or event_ms(r, "first-token") or t.get("ttftMs")
        if f: fv.append(f / 1000)
        if t.get("totalMs"): tot.append(t["totalMs"] / 1000)
        if t.get("prefillMs") and t.get("promptTokens"):
            new = t["promptTokens"] - cached_tokens(r)
            if new > 0: pre.append(new / (t["prefillMs"] / 1000))
        if t.get("decodeTokPerSec"): dec.append(t["decodeTokPerSec"])
        s = event_ms(r, "first-sources")
        if s: src.append(s / 1000)
    m = {
        "first_visible_p50": st.median(fv) if fv else None, "first_visible_p90": pct(fv, 0.9),
        "total_p50": st.median(tot) if tot else None, "total_p90": pct(tot, 0.9),
        "prefill_tok_s": st.median(pre) if pre else None, "decode_tok_s": st.median(dec) if dec else None,
        "first_sources_p50": st.median(src) if src else None,
    }
    print(f"# {label or ', '.join(argv)}: {len(fv)} LLM answers of {n_all} rows")
    for k, v in m.items():
        rng = PRED.get(k)
        tag = "" if v is None or not rng else ("  within prediction" if rng[0] <= v <= rng[1] else f"  OUTSIDE prediction {rng}")
        print(f"{k:20s} {('%.2f' % v) if v is not None else 'n/a':>8s}{tag}")
    fvp, totp = m["first_visible_p50"], m["total_p50"]
    if fvp is None or totp is None:
        print("branch: n/a (missing timing)"); return
    if fvp <= BAR["first_visible_p50"] and totp <= BAR["total_p50"]:
        branch = "1: meets the E2 bar; the 4B stays as is"
    elif totp <= K3:
        branch = "2: misses the bar, total <= 25 s; run pinning (threads = big cores) + k=3 as one P3a variant"
    else:
        branch = "3: K3 (total > 25 s); latency becomes front 1: stack pinning + k=3 + Q4_0 (Maple closed by K4); state latency honestly in the claim"
    print("branch:", branch)
    if m["first_sources_p50"] is not None:
        print(f"note: sources/preview visible at p50 {m['first_sources_p50']:.2f} s (counts as 'first visible' only if r4to says so)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
