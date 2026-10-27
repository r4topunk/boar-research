#!/usr/bin/env python3
"""NUMCHECK (B6) 0-call gate. Part 1 (jev, 0 Claude): are the wrong-primary items' faulted numbers/dates covered by the
FACTS r6 Wikidata table? Part 2 (script, no gateway): simplest answer-side matcher, false rewrites on the 20 best
non-wrong answers. Script-only on blind: reads judgments/traces, writes ids, labels, probabilities, table row keys only.
usage: numcheck_gate.py --judgments J --lossmap L.json --set vpara --facts facts.v1.json --out O.json [--dry-run]
"""
import argparse, json, os, re, sys
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lossmap", "tools"))
import lossmap as LM

MAX_ROWS = 20
NUM_PROPS = {"pop": "population", "area": "area_km2", "elev": "elevation_m", "height": "height_m", "len": "length_km",
             "depth": "depth_m", "inc": "inception_date", "end": "end_date"}
LIST_PROPS = {"cap": "capital", "cur": "currency", "lang": "official_language", "cont": "continent", "plug": "plug_type",
              "volt": "mains_voltage_V", "loc": "location", "ctry": "country"}
# matcher lexicon (from facts.ts FACT_LEXICON, numeric templates only)
KW = {"pop": ["population", "populous", "inhabitants", "residents", "people"],
      "area": ["area", "square kilomet", "sq km", "km2", "km²", "square miles", "sq mi"],
      "elev": ["high", "tall", "height", "elevation", "altitude", "summit"],
      "height": ["high", "tall", "height", "elevation", "storeys", "stories"],
      "len": ["long", "length"], "depth": ["deep", "depth"],
      "inc": ["built", "founded", "established", "constructed", "erected", "inception", "opened", "completed"],
      "end": ["came down", "fell", "fall of", "torn down", "demolished", "dissolved", "ended"]}
CONV = {"area": [1, 1 / 2.58999], "elev": [1, 3.28084], "height": [1, 3.28084], "len": [1, 1 / 1.609344], "depth": [1, 3.28084], "pop": [1]}

def B(instr, t, f): return {"type": "boolean", "instructions": instr, "criteria": {"true": t, "false": f}}

def questions(nrows):
    q = {
      "wrong_is_numeric_or_date": B("Do `rationale_1` or `rationale_2` say that `answer` states a wrong number, quantity, rate, price, dose or date?",
        "a rationale faults a specific number, quantity, rate, price, dose, year or date written in the answer as wrong or inaccurate",
        "the rationales fault something else (a name, a mechanism, a missing point, vagueness), or only say a number is missing, not wrong"),
      "table_covers": B("Does one row of `candidate_rows` give the correct value of exactly the quantity or date that `rationale_1` or `rationale_2` say is wrong in `answer` (same entity and same property)?",
        "a row has the same entity and the same property as the faulted number or date in the answer, so its value could replace it",
        "`candidate_rows` is empty, or no row has both the same entity and the same property as the faulted number or date, or the rationales fault no number or date"),
    }
    crit = {f"r{i}": f"row `candidate_rows.r{i}` is the entity and property of the number or date the rationales say is wrong" for i in range(nrows)}
    crit["none"] = "no row of `candidate_rows` matches the entity and property of the faulted number or date, or nothing numeric is faulted"
    q["which_row"] = {"type": "choice", "instructions": "Which row of `candidate_rows` holds the correct value for the number or date that `rationale_1` or `rationale_2` say is wrong in `answer`?", "criteria": crit}
    q["faulted_kind"] = {"type": "choice", "instructions": "What kind of number or date do `rationale_1` or `rationale_2` say is wrong in `answer`?", "criteria": {
      "geo_attribute": "a fixed attribute of a place or structure: population, area, height, length, elevation, founding date",
      "national_statistic": "a country or economy statistic: GDP, inflation, rate, budget, share",
      "crypto_protocol": "a blockchain or crypto protocol parameter, fee, supply, block or upgrade date",
      "health_dose": "a medical dose, threshold, duration or risk figure",
      "price_or_rule": "a current price, fee, legal limit or travel rule",
      "science_constant": "a physical, chemical or astronomical quantity or constant",
      "historical_date": "the date or year of a historical event, release or discovery",
      "computed_result": "the result of arithmetic or a calculation the answer performed",
      "none": "the rationales fault no number or date"}}
    q["is_computed"] = B("Is the number or date that `rationale_1` or `rationale_2` fault in `answer` the result of a calculation the answer performed, not a value it looked up or recalled?",
        "the faulted figure is derived by arithmetic, conversion or reasoning steps in the answer",
        "the faulted figure is a recalled fact, or no number or date is faulted")
    return q

def load_table(p):
    T = json.load(open(p)); ents = T["entities"]; snap = T["snapshot"]
    names = []  # (entity index, name, case-sensitive pattern, case-insensitive pattern)
    for i, e in enumerate(ents):
        for nm in [e["n"]] + (e.get("a") or []):
            if len(nm) < 4 or nm.isupper(): continue
            esc = r"(?<![\w])" + re.escape(nm) + r"(?![\w])"
            names.append((i, nm, re.compile(esc), re.compile(esc, re.I)))
    return ents, snap, names

def rows_of(e, snap):
    out = []
    for p, lab in NUM_PROPS.items():
        if p not in e: continue
        if p == "pop": out.append({"key": f"{e['q']}:pop", "entity": e["n"], "property": lab, "value": e["pop"][0], "as_of": e["pop"][1] or snap})
        else: out.append({"key": f"{e['q']}:{p}", "entity": e["n"], "property": lab, "value": e[p], "as_of": snap})
    for p, lab in LIST_PROPS.items():
        if e.get(p): out.append({"key": f"{e['q']}:{p}", "entity": e["n"], "property": lab, "value": ", ".join(map(str, e[p])), "as_of": snap})
    if e.get("win"):
        ys = sorted(e["win"])[-5:]
        out.append({"key": f"{e['q']}:win", "entity": e["n"], "property": "winners_by_year", "value": "; ".join(f"{y}: {', '.join(e['win'][y])}" for y in ys), "as_of": snap})
    return out

def find_entities(texts_hi, texts_lo, names):
    """Entities whose label/alias (>= 4 chars) appears case-insensitively; rank: in rationales, case-exact, longer name."""
    best = {}
    for i, nm, cs, ci in names:
        in_r = any(ci.search(t) for t in texts_hi); in_a = any(ci.search(t) for t in texts_lo)
        if not (in_r or in_a): continue
        exact = any(cs.search(t) for t in texts_hi + texts_lo)
        sc = (2 if in_r else 0) + (1 if exact else 0) + min(len(nm), 30) / 100
        if sc > best.get(i, -1): best[i] = sc
    return sorted(best, key=lambda i: -best[i])

def candidate_rows(ents, snap, idxs):
    rows = []
    for i in idxs:
        for r in rows_of(ents[i], snap):
            if len(rows) >= MAX_ROWS: return rows
            rows.append(r)
    return rows

# ---- part 2: answer-side matcher (no gateway) ----
NUM_RE = re.compile(r"(\d[\d,]*(?:\.\d+)?)\s*(million|billion|thousand|k\b|m\b(?=\s*(?:people|inhabitants|residents)))?", re.I)

def numbers(s):
    out = []
    for m in NUM_RE.finditer(s):
        try: v = float(m.group(1).replace(",", ""))
        except ValueError: continue
        mul = {"million": 1e6, "billion": 1e9, "thousand": 1e3, "k": 1e3, "m": 1e6}.get((m.group(2) or "").lower(), 1)
        out.append(v * mul)
    return out

def sentences(t): return [s for s in re.split(r"(?<=[.!?])\s+|\n+", t) if s.strip()]

def matcher(answer, ents, names, tol=0.10):
    fired = []
    for s in sentences(answer):
        low = s.lower(); nums = numbers(s)
        if not nums: continue
        for i, nm, cs, ci in names:
            if not ci.search(s): continue
            e = ents[i]
            for p in NUM_PROPS:
                if p not in e or not any(k in low for k in KW[p]): continue
                if p in ("inc", "end"):
                    y = int(str(e[p])[:4]); yrs = [n for n in nums if 1000 <= n <= 2100 and n == int(n)]
                    if yrs and all(abs(n - y) > 1 for n in yrs): fired.append(f"{e['q']}:{p}")
                    continue
                v = e["pop"][0] if p == "pop" else e[p]
                if not v: continue
                cands = [n for n in nums if not (1000 <= n <= 2100 and n == int(n) and p != "pop")]  # skip bare years
                if not cands: continue
                ok = any(abs(n - v * c) <= tol * v * c for n in cands for c in CONV[p])
                if not ok: fired.append(f"{e['q']}:{p}")
    return sorted(set(fired))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judgments", required=True); ap.add_argument("--traces")
    ap.add_argument("--lossmap", required=True); ap.add_argument("--set", required=True)
    ap.add_argument("--facts", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--threshold", type=float, default=0.6); ap.add_argument("--n-correct", type=int, default=20)
    ap.add_argument("--workers", type=int, default=4); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    key = os.environ.get("VERCEL_AI_GATEWAY") or os.environ.get("AI_GATEWAY_API_KEY")
    if not key and not a.dry_run: sys.exit("no gateway key")
    ents, snap, names = load_table(a.facts)
    J = [r for r in LM.read_jsonl(a.judgments) if r.get("ok")]
    tp = a.traces or LM.find_traces(J, a.judgments)
    T = {t["itemId"]: t for t in LM.read_jsonl(tp)}
    L = {i["id"]: i for i in json.load(open(a.lossmap))["items"]}
    by = defaultdict(list)
    for r in J: by[r["queryId"]].append(r)
    cache_dir = os.path.join(os.path.dirname(os.path.abspath(a.judgments)), "numcheck-cache"); os.makedirs(cache_dir, exist_ok=True)
    wrong_ids = sorted(i for i, x in L.items() if x["primary"] == "wrong")
    correct_ids = [x["id"] for x in sorted((x for x in L.values() if x["primary"] != "wrong"), key=lambda x: -x["ratio"])][:a.n_correct]
    ans_of = lambda q: ((T.get(q, {}).get("answer") or {}).get("text") or "")
    items = []
    for qid in wrong_ids:
        rows = sorted(by[qid], key=lambda r: r["order"])
        r1 = rows[0]["verdict"]["rationale"]; r2 = rows[-1]["verdict"]["rationale"] if len(rows) > 1 else ""
        ans = ans_of(qid)[:2500]
        idxs = find_entities([r1, r2], [ans], names)
        cr = candidate_rows(ents, snap, idxs)
        st = {"rationale_1": r1, "rationale_2": r2, "answer": ans,
              "candidate_rows": {f"r{i}": {k: v for k, v in r.items() if k != "key"} for i, r in enumerate(cr)}}
        items.append({"id": qid, "category": L[qid]["category"], "loss": L[qid]["loss"], "n_entities_matched": len(idxs),
                      "row_keys": [r["key"] for r in cr], "_state": st, "_nrows": len(cr)})
    print(f"{a.set}: {len(items)} wrong items, rows/item {[i['_nrows'] for i in items]}", file=sys.stderr)
    cost = 0.0; cached = 0
    if not a.dry_run:
        def work(it): return it, *LM.call({"model": LM.MODEL, "state": it["_state"], "questions": questions(it["_nrows"])}, key, cache_dir)
        with ThreadPoolExecutor(a.workers) as ex:
            for it, res, hit in ex.map(work, items):
                an = res["answers"]
                it["p"] = {q: round(an[q]["probability"], 3) for q in ("wrong_is_numeric_or_date", "table_covers")}
                it["labels"] = {q: it["p"][q] >= a.threshold for q in it["p"]}
                wr = an["which_row"]["choice"]; it["which_row"] = wr; it["which_row_conf"] = round(an["which_row"].get("confidence", 0) or 0, 3)
                it["which_row_key"] = it["row_keys"][int(wr[1:])] if wr.startswith("r") and wr[1:].isdigit() and int(wr[1:]) < len(it["row_keys"]) else None
                it["covered"] = it["labels"]["table_covers"] and it["which_row_key"] is not None and it["_nrows"] > 0
                it["faulted_kind"] = an["faulted_kind"]["choice"]; it["p_is_computed"] = round(an["is_computed"]["probability"], 3)
                if hit: cached += 1
                else: cost += float(((res.get("providerMetadata") or {}).get("gateway") or {}).get("marketCost") or 0)
    for it in items: del it["_state"]; it["n_rows"] = it.pop("_nrows")
    # part 2: matcher on top-N correct answers (gate), and on the wrong items (reach, informational)
    fr = [{"id": q, "ratio": round(L[q]["ratio"], 3), "primary": L[q]["primary"], "fired_keys": matcher(ans_of(q), ents, names)} for q in correct_ids]
    for it in items: it["matcher_fired_keys"] = matcher(ans_of(it["id"]), ents, names)
    n_cov = sum(1 for i in items if i.get("covered")); n_num = sum(1 for i in items if (i.get("labels") or {}).get("wrong_is_numeric_or_date"))
    out = {"set": a.set, "arm": "H", "model": LM.MODEL, "threshold": a.threshold, "facts_asset": os.path.basename(a.facts),
           "facts_build": json.load(open(a.facts)).get("build"), "facts_entities": len(ents), "gateway_cost_usd": round(cost, 5), "cached": cached,
           "part1": {"n_wrong": len(items), "n_wrong_is_numeric_or_date": n_num, "n_table_covers": n_cov,
                     "n_items_with_any_candidate_row": sum(1 for i in items if i["n_rows"]),
                     "covered_ids": [i["id"] for i in items if i.get("covered")],
                     "faulted_kind_of_numeric": Counter(i.get("faulted_kind") for i in items if (i.get("labels") or {}).get("wrong_is_numeric_or_date")).most_common(),
                     "category_of_numeric": Counter(i["category"] for i in items if (i.get("labels") or {}).get("wrong_is_numeric_or_date")).most_common(),
                     "n_numeric_computed": sum(1 for i in items if (i.get("labels") or {}).get("wrong_is_numeric_or_date") and i.get("p_is_computed", 0) >= a.threshold)},
           "part2": {"n_correct": len(fr), "min_ratio": min((x["ratio"] for x in fr), default=None), "n_rewrites": sum(1 for x in fr if x["fired_keys"]),
                     "fired_keys": Counter(k for x in fr for k in x["fired_keys"]).most_common(),
                     "matcher_fires_on_wrong_items": sum(1 for i in items if i["matcher_fired_keys"]),
                     "items": fr},
           "items": items}
    json.dump(out, open(a.out, "w"), indent=1)
    print(a.set, "cost", out["gateway_cost_usd"], "cached", cached, "part1", out["part1"], "part2 rewrites", out["part2"]["n_rewrites"], out["part2"]["fired_keys"], "matcher on wrong", out["part2"]["matcher_fires_on_wrong_items"])

if __name__ == "__main__": main()
