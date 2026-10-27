#!/usr/bin/env python3
"""DEVICE-DAY 2026-10-22: 0-LLM readouts of the maintainer-RC runs (rows.jsonl written by handoff/.../bench/rc_eval.py).
  python3 -I dd_check.py speed  <rc rows.jsonl> <bench rows.jsonl>          # DEV-SPEED17: paired vs q4ba73-a / q17b73-a on SPEED9
  python3 -I dd_check.py layer  <rc rows.jsonl>                               # DEV-LAYERPAR: layer ids vs cut 7 Pixel rows (final-cut7-v01)
  python3 -I dd_check.py t1     <rc rows.jsonl> [<rc rows.jsonl> ...]          # DEV-GEMMA-T1: thinking markers + token bound
  python3 -I dd_check.py aunion <rc rows.jsonl> [<base rows.jsonl>]            # DEV-AUNION-NATIVE: retrieved titles -> packs
  python3 -I dd_check.py press  <rc result dir> [...]                          # DEV-4B-PRESSURE: kills, PSS peak, MemAvailable per cycle
Thresholds are the hypothesis texts (hypotheses-round3-2026-10-21.json); the coordinator freezes them (sha) before the run.
Prints JSON; never prints answer text except the 2 probe answers' class."""
import json, re, sqlite3, statistics, sys
from pathlib import Path
B = "<workspace>"; RES = B + "/handoff/pixel8-2026-10-20/bench/results/"
IDS = B + "/rnd/research/coordinator/ruler/ids/"
load = lambda p: {r["queryId"]: r for r in map(json.loads, open(p)) if r.get("queryId") != "warmup-000"}
ids = lambda f: open(IDS + f).read().split()
p50 = lambda xs: round(statistics.median(xs), 2) if xs else None
norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", (s or "").lower())).strip()

def speed(rc, bench):
    R, Bn = load(rc), load(bench); S = [q for q in ids("dd1022-speed9.ids") if q in R and q in Bn]
    a = [R[q]["totalLatencyMs"] / 1000 for q in S]; b = [Bn[q]["totalLatencyMs"] / 1000 for q in S]
    ratio = p50(a) / p50(b) if a and b else None
    lmk = Path(rc).with_name("lmk.txt"); kills = sum(1 for _ in open(lmk)) if lmk.exists() else None
    v = "PASS" if ratio is not None and ratio <= 1.5 and not kills else "MARGINAL" if ratio is not None and ratio <= 2 and not kills else "FAIL"
    return {"n": len(S), "rc_answer_p50": p50(a), "bench_answer_p50": p50(b), "ratio": round(ratio, 2) if ratio else None,
            "rc_ttft_p50": p50([R[q]["ttftMs"] / 1000 for q in S if R[q].get("ttftMs")]), "rc_decode_p50": p50([R[q]["tokPerSec"] for q in S if R[q].get("tokPerSec")]),
            "bench_decode_p50": p50([Bn[q]["tokPerSec"] for q in S if Bn[q].get("tokPerSec")]),
            "rc_peakRss_gb": round(max(R[q].get("peakRssBytes") or 0 for q in S) / 1e9, 2), "lmk_lines": kills,
            "personality": sorted({str(R[q].get("personalityId")) for q in S}), "verdict_rule_1.5x_2x": v}

def layer(rc):
    R = load(rc); C = load(RES + "final-cut7-v01/rows.jsonl"); out = {}
    for q in ["trv-002", "vit-sci-003", "saf-004", "vit-hlt-002"]:
        r, c = R.get(q), C.get(q)
        if not r: out[q] = "missing"; continue
        same = norm(r["answer"]) == norm(c["answer"]); det = (r.get("tokensGenerated") or 0) == 0
        out[q] = {"rc_tokens": r.get("tokensGenerated"), "cut7_tokens": c.get("tokensGenerated"), "rc_deterministic": det,
                  "text_identical_normalised": same, "match": det and same}
    e = R.get("epi-1021"); g = R.get("geo-dev-1022")
    out["epi-1021"] = None if not e else {"tokens": e.get("tokensGenerated"), "says_thigh": "thigh" in e["answer"].lower(),
                                          "says_arm": bool(re.search(r"\barm\b|forearm|deltoid", e["answer"].lower()))}
    if g:
        t = g["answer"].lower()
        cls = "place-list" if len(re.findall(r"^\s*\d+[.)]", g["answer"], re.M)) >= 3 else "refuse" if re.search(r"can't|cannot|don't have|no (offline )?(place|location)|which city|not able", t) else "generic"
        out["geo-dev-1022"] = {"class": cls, "tokens": g.get("tokensGenerated")}
    m = sum(1 for q in ["trv-002", "vit-sci-003", "saf-004", "vit-hlt-002"] if isinstance(out[q], dict) and out[q]["match"])
    out["layers_matched_of_4"] = m
    out["note"] = "epi-1021 reaches the model in cut 7 too (port row 13 is a candidate): it counts as the 5th layer only if the RC answers it with a fixed card (0 tokens)."
    out["matched_of_5"] = m + (1 if e and (e.get("tokensGenerated") or 0) == 0 and "thigh" in e["answer"].lower() else 0)
    return out

MARK = re.compile(r"<think>|</think>|<\|channel\|?>|<channel\|>|\bthought\b|Thinking Process|<\|?start_of_turn\|?>\s*model\s*\n\s*thinking|^\s*(Okay|Alright|Let me think|Let's think)\b", re.I | re.M)
def t1(*files):
    rows = [r for f in files for r in load(f).values()]
    hits = [r["queryId"] for r in rows if MARK.search(r.get("answer") or "")]
    over_cap = [r["queryId"] for r in rows if r.get("maxTokens") and (r.get("tokensGenerated") or 0) >= int(r["maxTokens"]) - 1]
    over_120 = [r["queryId"] for r in rows if (r.get("tokensGenerated") or 0) > 120]
    return {"n": len(rows), "models": sorted({str(r.get("modelId")) for r in rows}), "personality": sorted({str(r.get("personalityId")) for r in rows}),
            "marker_hits": hits, "at_maxTokens": over_cap, "over_120_tokens(2x our p90 60)": over_120,
            "max_tokens_seen": max((r.get("tokensGenerated") or 0) for r in rows) if rows else None,
            "verdict": "FAIL" if hits or len(over_cap) > 1 else "PASS (markers 0, <= 1 at cap)"}

PACKDIR = B + "/shared-data/packs/persona-a-union/"
PACKS = ["boar-wikivoyage-en", "boar-crypto", "boar-firstaid-en", "boar-factbook", "boar-medlineplus-en", "boar-visa-en"]
def aunion(rc, base=None):
    R = load(rc); exp = json.load(open(Path(__file__).with_name("aunion10-expected.json")))["kept_by_id"]
    dbs = {p: sqlite3.connect(f"file:{PACKDIR}{p}.sqlite?mode=ro", uri=True) for p in PACKS}
    def packs_of(t):
        t0 = re.sub(r"^[^:]{2,40}:\s*", "", t)  # drop a "Source: " label if the app shows one
        return [p for p, d in dbs.items() if d.execute("select 1 from articles where title = ? collate nocase limit 1", (t0,)).fetchone()]
    per, hit = {}, set()
    for q in exp:
        r = R.get(q)
        if not r: per[q] = "missing"; continue
        got = sorted({p for t in r.get("retrievedTitles") or [] for p in packs_of(t)}); hit |= set(got)
        per[q] = {"expected": sorted(k for k in exp[q] if k != "null"), "rc_packs": got, "titles": len(r.get("retrievedTitles") or []), "retrieval_s": round((r.get("retrievalMs") or 0) / 1000, 2)}
    out = {"distinct_packs_hit": sorted(hit), "n_packs_hit": len(hit), "per_id": per,
           "rc_retrieval_p50": p50([(R[q].get("retrievalMs") or 0) / 1000 for q in exp if q in R]),
           "rc_peakRss_gb": round(max((R[q].get("peakRssBytes") or 0) for q in exp if q in R) / 1e9, 2) if R else None,
           "label_check": "PackSource labels: read them on screen or in the rows' source fields if the RC logs them; titles alone cannot prove the label"}
    if base:
        Bs = load(base)
        out["base_retrieval_p50"] = p50([(Bs[q].get("retrievalMs") or 0) / 1000 for q in exp if q in Bs])
        out["base_peakRss_gb"] = round(max((Bs[q].get("peakRssBytes") or 0) for q in exp if q in Bs) / 1e9, 2) if Bs else None
    return out

def press(*dirs):
    out = []
    for d in map(Path, dirs):
        s = json.load(open(d / "summary.json")); dev = json.load(open(d / "device.json"))
        out.append({"run": d.name, "rows": s["rows"], "of": len(json.load(open(d / "request.json"))["questions"]), "pss_peak_gb": s["pss_peak_gb"],
                    "memAvailable_before_gb": round(int(dev.get("memAvailableKb") or 0) / 1048576, 2), "lmk_lines": s["lmk_lines"],
                    "app_died_samples": s["app_died_samples"], "killed": bool(s["lmk_lines"]) or bool(s["app_died_samples"]) or s["rows"] < len(json.load(open(d / "request.json"))["questions"])})
    return out

if __name__ == "__main__":
    fn = {"speed": speed, "layer": layer, "t1": t1, "aunion": aunion, "press": press}[sys.argv[1]]
    print(json.dumps(fn(*sys.argv[2:]), indent=1))
