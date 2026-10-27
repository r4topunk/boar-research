"""CV5-PER100-OPUS shared loader (0 calls): exec hon67.py's data section UNCHANGED (up to its HON-7 header) to get the desktop MAIN 97 K0 rows D
of the three tiers, and its HON-6 definitions (per100, pboot, table, decide) unchanged. Returns the namespace G and the trace texts per tier."""
import json, os, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); H67 = f"{HERE}/hon67.py"
H67SHA = "9718fe37"  # prefix quoted in HON6-TIER-PER100-2026-10-21.md
def load():
    src = open(H67).read(); sha = hashlib.sha256(src.encode()).hexdigest(); assert sha.startswith(H67SHA), sha
    G = {"__file__": H67, "__name__": "hon67_defs"}
    exec(src[:src.index("# ---------------- HON-7")], G)
    seg = src[src.index("# ---------------- HON-6"):src.index("PAIRS = ")]; exec(seg, G)
    seg2 = src[src.index("def decide"):src.index("oa = ")]; exec(seg2, G)
    A = G["A"]; GE = f"{A}/gemma4-e2b"; CO = f"{A}/lp-screens/control"
    TRF = {"4B": f"{GE}/vs4b/traces/gemma4-e2b-vs4b-K0-main-s42.traces.jsonl", "Gemma": f"{GE}/stage2/traces/gemma4-e2b-eng-K0-main-s42.traces.jsonl",
           "1.7B": f"{CO}/traces/lpctl-K0-main-s42.traces.jsonl"}
    TX = {t: {(j := json.loads(l)).get("itemId") or j.get("queryId"): j["answer"]["text"] for l in open(f)} for t, f in TRF.items()}
    return G, TRF, TX, sha
def bench_of(i):
    B = "<workspace>/boar-eval/bench/"
    if i.startswith("st-qa-cooking-se"): return "qa-cooking-se", B + "selftest/qa-cooking-se"
    if i.startswith("st-qa-money-se"): return "qa-money-se", B + "selftest/qa-money-se"
    return "v01", B + "v0.1"
