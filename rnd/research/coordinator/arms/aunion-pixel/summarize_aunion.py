#!/usr/bin/env python3
"""AUNION-PIXEL summary: one JSON per run dir (rows.jsonl, bench.json, telemetry.csv, logcat.txt optional), 0 LLM calls.
usage: summarize_aunion.py <packs_dir> <run_dir> [<run_dir> ...]  -> prints a table + writes <run_dir>/aunion-summary.json
Metrics (frozen in AUNION-PIXEL-criterion.md):
  answer = row totalLatencyMs over all rows (p50/p90); TTFT = row ttftMs over rows that generated (ttftMs > 0);
  promptN / prefill tok/s (promptN/promptMs*1000) / decode tok/s (predictedPerSecond or n/predictedMs) from bench.json
  completions or timeline llm-completion spans; retrieval wall = timeline 'retrieve' item ms; per-pack SQL ms = sum of
  'sql' spans by db file; PSS peak = max telemetry app_pss_kb; LMK = logcat lines 'lowmemorykiller'/'lmkd' naming the
  package (when logcat.txt exists); pack hits = retrievedTitles mapped to the pack whose articles table holds the title
  (label prefix stripped, source code checked), counted per question and per row-title."""
import csv, json, os, re, sqlite3, statistics, sys

def pct(xs, p):
    xs = sorted(x for x in xs if x is not None)
    if not xs: return None
    k = (len(xs) - 1) * p; f = int(k); c = min(f + 1, len(xs) - 1)
    return xs[f] + (xs[c] - xs[f]) * (k - f)

LABELS = {"Wikivoyage": 1, "Wikibooks": 2, "Appropedia": 3, "US government": 4, "Ethereum EIPs/ERCs": 5,
          "Ethereum specs": 6, "ethereum.org": 7, "Bitcoin BIPs": 8}

def pack_index(d):
    idx = {}
    for f in sorted(os.listdir(d)):
        if not f.endswith(".sqlite"): continue
        db = sqlite3.connect(f"file:{os.path.join(d, f)}?mode=ro", uri=True)
        for t, s in db.execute("SELECT title, source FROM articles"):
            idx.setdefault(t.lower(), []).append((f[:-7], s))
        db.close()
    return idx

def attribute(title, idx):
    src = None; t = title
    for lab, code in LABELS.items():
        if title.startswith(lab + ": "):
            t, src = title[len(lab) + 2:], code; break
    cands = idx.get(t.lower(), [])
    if src is not None: cands = [c for c in cands if c[1] == src]
    else: cands = [c for c in cands if c[1] not in LABELS.values()]  # unlabelled = enwiki code 0 or out-of-enum 10/11
    packs = sorted({c[0] for c in cands})
    return packs if packs else ["(not in A-union packs: bundled corpus or other)"]

def summarize(run, idx):
    rows = [json.loads(l) for l in open(os.path.join(run, "rows.jsonl")) if l.strip()]
    b = json.load(open(os.path.join(run, "bench.json")))
    comps = []
    for q in b.get("timeline") or []:
        for i in q["items"]:
            if i.get("kind") == "span" and i.get("name") == "llm-completion" and i.get("extra"):
                e = i["extra"]; pm = e.get("promptMs") or 0; pd = e.get("predictedMs") or 0
                comps.append({"promptN": e.get("promptN"), "prefillTps": e["promptN"] / pm * 1000 if pm and e.get("promptN") else None,
                              "decodeTps": i.get("n") / pd * 1000 if pd and i.get("n") else None})
    retr, sqlby = [], {}
    for q in b.get("timeline") or []:
        for i in q["items"]:
            if i.get("kind") == "retrieve": retr.append(i.get("ms"))
            if i.get("kind") == "span" and i.get("name") == "sql":
                db = (i.get("label") or "").split("|")[0]
                if db.endswith(".sqlite"): sqlby[db] = sqlby.get(db, 0) + (i.get("ms") or 0)
    pss = []
    tp = os.path.join(run, "telemetry.csv")
    temps, therm = [], []
    if os.path.exists(tp):
        for r in csv.DictReader(open(tp)):
            if r.get("app_pss_kb"): pss.append(int(r["app_pss_kb"]))
            if r.get("battery_temp_dC"): temps.append(int(r["battery_temp_dC"]) / 10)
            if r.get("thermal_status"): therm.append(int(r["thermal_status"]))
    lmk = None
    lp = os.path.join(run, "logcat.txt")
    if os.path.exists(lp):
        lmk = sum(1 for l in open(lp, errors="replace") if re.search(r"lowmemorykiller|lmkd", l, re.I) and "boarbench" in l and re.search(r"kill", l, re.I))
    hits_q, hits_t = {}, {}
    for r in rows:
        seen = set()
        for t in r.get("retrievedTitles") or []:
            for p in attribute(t, idx):
                hits_t[p] = hits_t.get(p, 0) + 1; seen.add(p)
        for p in seen: hits_q[p] = hits_q.get(p, 0) + 1
    gen = [r for r in rows if (r.get("ttftMs") or 0) > 0]
    s = {"run": os.path.basename(run.rstrip("/")), "rows": len(rows), "outcomes": {}, "generating": len(gen),
         "answer_p50_s": pct([r.get("totalLatencyMs") for r in rows], .5) / 1000, "answer_p90_s": pct([r.get("totalLatencyMs") for r in rows], .9) / 1000,
         "answer_total_s": sum(r.get("totalLatencyMs") or 0 for r in rows) / 1000,
         "ttft_p50_s": (pct([r["ttftMs"] for r in gen], .5) or 0) / 1000, "llm_calls": len(comps),
         "promptN_p50": pct([c["promptN"] for c in comps], .5), "promptN_max": max([c["promptN"] or 0 for c in comps], default=None),
         "prefill_tps_p50": pct([c["prefillTps"] for c in comps], .5), "decode_tps_p50": pct([c["decodeTps"] for c in comps], .5),
         "retrieval_ms_p50": pct(retr, .5), "retrieval_ms_p90": pct(retr, .9), "retrieval_ms_max": max(retr, default=None),
         "sql_ms_by_db": {k: round(v) for k, v in sorted(sqlby.items(), key=lambda x: -x[1])},
         "pss_peak_gb": max(pss) / 1e6 if pss else None, "pss_end_gb": pss[-1] / 1e6 if pss else None,
         "battery_c": [min(temps), max(temps)] if temps else None, "thermal_max": max(therm) if therm else None,
         "lmk_kills": lmk, "pack_hits_questions": hits_q, "pack_hits_titles": hits_t}
    for r in rows: s["outcomes"][r.get("outcome")] = s["outcomes"].get(r.get("outcome"), 0) + 1
    json.dump(s, open(os.path.join(run, "aunion-summary.json"), "w"), indent=1)
    return s

if __name__ == "__main__":
    idx = pack_index(sys.argv[1])
    for run in sys.argv[2:]:
        s = summarize(run, idx)
        print(json.dumps(s))
