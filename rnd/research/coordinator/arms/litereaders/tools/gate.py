#!/usr/bin/env python3
"""LITEREADERS 0-call gate. Usage: python3 -I tools/gate.py <slice: smoke|r20>  -> aggregates/gate-<slice>.json, rc 0 PASS / 8 FAIL.
Per reader x item vs the 4B ADD trace + prompt dump (oracle-st/runs/st-<pack>-cut7-oracleadd-s42.*):
 G0 0 errors, non-empty answer text, reasoningTokens 0, no '<think>' in the answer; modelId = the reader (receipt + generate code).
 G1 prompt identity: the dumped prompt (messages) is byte-equal (json) to the 4B ADD dump for the same query after replacing the
    device-date line ("Today is <date> (this device's date).") by a placeholder (criterion v2); date-only diffs are listed; items with no LLM call
    must be no-LLM for the 4B too (same tier); kept list (title, section/chunk ids) equal to the 4B ADD trace.
Also reports per reader: p50 total s, ttft, decode tok/s, prompt tokens, output tokens, peak RSS (2 s sampler .rss + trace peakRssMb)."""
import json, sys, os, statistics as st, glob
A = "<workspace>/rnd/research/coordinator/arms"; H = f"{A}/litereaders"; R = f"{H}/runs"; SL = sys.argv[1]
READERS = {"q17": "qwen3-1.7b-q4km", "lfm": "lfm2-1.2b-q4km", "g1": "gemma-3-1b-it-q4km"}
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()] if os.path.exists(f) else []
ids = open(f"{H}/{'smoke3' if SL == 'smoke' else 'random20'}.ids").read().split()
REF, REFP = {}, {}
for f in glob.glob(f"{A}/oracle-st/runs/st-*-cut7-oracleadd-s42.traces.jsonl"):
    for t in rd(f): REF[t["itemId"]] = t
    for p in rd(f.replace(".traces.jsonl", ".prompts.jsonl")): REFP[p["query"]] = p["prompt"]
import re
DATE = re.compile(r"(Today is|Hoje é) [^()]*\((this device's date|data deste aparelho)\)\.")
norm = lambda m: DATE.sub("<DEVICE-DATE>", json.dumps(m, ensure_ascii=False)) if m is not None else None  # criterion v2: the device-date line is a clock artefact
kept = lambda t: [json.dumps(k, sort_keys=True) for k in t["retrieval"]["kept"]]
out = {"slice": SL, "readers": {}}; ok = True
for k, m in READERS.items():
    T, P, rss = {}, {}, []
    for X in [x for x in open(f"{R}/RUNS").read().split() if x.startswith(f"lr-{k}-{SL}-")]:
        for t in rd(f"{R}/{X}.traces.jsonl"): T[t["itemId"]] = t
        for p in rd(f"{R}/{X}.prompts.jsonl"): P[p["query"]] = p["prompt"]
        rss += [int(l.split()[1]) for l in open(f"{R}/{X}.traces.rss") if len(l.split()) == 2] if os.path.exists(f"{R}/{X}.traces.rss") else []
    fails, datediff = [], []
    for i in ids:
        t = T.get(i); r = REF[i]
        if t is None: fails.append((i, "missing")); continue
        txt = (t["answer"] or {}).get("text") or ""
        if t.get("error"): fails.append((i, "error", str(t["error"])[:80]))
        if not txt.strip(): fails.append((i, "empty"))
        if (t["timing"].get("reasoningTokens") or 0) > 0 or "<think>" in txt: fails.append((i, "reasoning"))
        if t["runtime"]["model"] != m: fails.append((i, "model", t["runtime"]["model"]))
        if kept(t) != kept(r): fails.append((i, "kept-diff"))
        rp, mp = REFP.get(r["question"]), P.get(t["question"])
        if (rp is None) != (mp is None): fails.append((i, "llm-call-mismatch", rp is None, mp is None))
        elif rp is not None and norm(rp) != norm(mp): fails.append((i, "prompt-diff"))
        elif rp is not None and json.dumps(rp, ensure_ascii=False) != json.dumps(mp, ensure_ascii=False): datediff.append(i)
    g = [t for i, t in T.items() if i in ids and t["route"]["tier"] != "instant"]
    md = lambda xs: round(st.median(xs), 2) if xs else None
    s = {"n": len([i for i in ids if i in T]), "llm_items": len(g), "prompt_identical": sum(1 for i in ids if i in T and REFP.get(REF[i]["question"]) is not None and norm(REFP[REF[i]["question"]]) == norm(P.get(T[i]["question"]))),
         "reasoning_tokens_max": max([t["timing"].get("reasoningTokens") or 0 for t in T.values()] or [0]),
         "p50_total_s": md([t["timing"]["totalMs"] / 1000 for t in g]), "p50_ttft_s": md([t["timing"]["ttftMs"] / 1000 for t in g if t["timing"].get("ttftMs")]),
         "p50_decode_tok_s": md([t["timing"]["decodeTokPerSec"] for t in g if t["timing"].get("decodeTokPerSec")]),
         "mean_prompt_tokens": round(st.mean([t["timing"]["promptTokens"] for t in g if t["timing"].get("promptTokens")]), 1) if g else None,
         "p50_output_tokens": md([t["timing"]["outputTokens"] for t in g]), "p50_words": md([len(((t["answer"] or {}).get("text") or "").split()) for t in g]),
         "rss_peak_mb_sampler": round(max(rss) / 1024) if rss else None, "rss_median_mb_sampler": round(st.median(rss) / 1024) if rss else None,
         "fails": fails, "device_date_line_only_diff": datediff}
    out["readers"][k] = s; ok &= not fails
out["verdict"] = "PASS" if ok else "FAIL"
json.dump(out, open(f"{H}/aggregates/gate-{SL}.json", "w"), indent=1)
for k, s in out["readers"].items(): print(k, {x: v for x, v in s.items() if x != "fails"}, "fails", s["fails"][:6])
print("GATE", SL, out["verdict"]); sys.exit(0 if ok else 8)
