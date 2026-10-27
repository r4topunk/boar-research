#!/usr/bin/env python3
"""RATIONALEPASS (T1): STALESPLIT axes + rationale_names_correction + recent_event + fact_type over the
LOSSMAP inputs of arm H, via jev (typesafe-ai/jev, Vercel AI Gateway). Reuses lossmap.py request shape/cache/retries.
Script-only on blind: reads judgments/traces/items, writes ids, labels, probabilities, aggregates only.
Also script-only checks: decline oracle (no gateway) and CITEMAP-REF domain histogram.
usage: rationalepass.py --judgments J --label H --set vpara --lossmap L.json --refs items.jsonl --out O.json [--dump-questions] [--dry-run]
"""
import argparse, json, os, sys, hashlib
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, Counter
from urllib.parse import urlparse
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lossmap", "tools"))
import lossmap as LM

def B(instr, t, f): return {"type": "boolean", "instructions": instr, "criteria": {"true": t, "false": f}}
QUESTIONS = {
  "stale": B("Do `rationale_1` or `rationale_2` say that a fact in the system answer (`answer`) was true once but is outdated or superseded?",
    "the judge says a claim in the answer is out of date, no longer true, or replaced by a newer value, version, rule, price or office-holder",
    "the judge does not describe any claim as outdated or superseded"),
  "numeric": B("Do `rationale_1` or `rationale_2` say that the system answer (`answer`) has a wrong or missing number, quantity, rate, price or dose?",
    "the judge faults a number, quantity, rate, price or dose in the answer, or says one that the reference gives is missing",
    "the judge does not fault or ask for any number, quantity, rate, price or dose"),
  "date": B("Do `rationale_1` or `rationale_2` say that the system answer (`answer`) has a wrong or missing date, year or period?",
    "the judge faults a date, year or time period in the answer, or says one that the reference gives is missing",
    "the judge does not fault or ask for any date, year or period"),
  "entity_swap": B("Do `rationale_1` or `rationale_2` say that the system answer (`answer`) names the wrong entity (person, place, product or organisation)?",
    "the judge says the answer names a different person, place, product or organisation than the correct one",
    "the judge does not say any named entity in the answer is wrong"),
  "overgeneralised": B("Do `rationale_1` or `rationale_2` say that the system answer (`answer`) gives a generic statement where a specific one was needed?",
    "the judge says the answer is generic, general or non-specific where the reference gives a specific fact, figure, name or rule",
    "the judge does not fault the answer for being generic where a specific statement was needed"),
  "fabricated": B("Do `rationale_1` or `rationale_2` say that the system answer (`answer`) states a fact that is invented, non-existent or unsupported?",
    "the judge calls a claim in the answer invented, fabricated, non-existent, hallucinated or unsupported",
    "the judge does not call any claim in the answer invented or unsupported"),
  "rationale_names_correction": B("Does at least one of `rationale_1` or `rationale_2` state what the correct fact IS, and not just that the answer is wrong or incomplete?",
    "a rationale states the correct value, name, date or fact that should have been in the answer",
    "the rationales only say the answer is wrong, incomplete, thin or generic without giving the correct fact"),
  "recent_event": B("Does the question, or the fact that is missing or wrong in `answer` according to `rationale_1` or `rationale_2`, concern something from 2024 or later (recent events, new releases, current office-holders, current prices)?",
    "the missing or wrong content concerns an event, release, office-holder or price from 2024 or later",
    "the missing or wrong content is timeless or from before 2024, or no missing or wrong content is named"),
  "fact_type": {"type": "choice",
    "instructions": "What kind of fact is missing or wrong in `answer` according to `rationale_1` and `rationale_2`?",
    "criteria": {
      "infobox_attribute": "a fixed attribute of an entity: population, founding date, height, capital, length",
      "country_number": "a national statistic: GDP, inflation, area, rate",
      "practical": "a how-to step, rule, procedure or threshold",
      "mechanism": "why or how something works",
      "other": "none of the above fits"}},
}
AXES = [q for q, s in QUESTIONS.items() if s["type"] == "boolean"]
SPLIT = ["stale", "numeric", "date", "entity_swap", "overgeneralised", "fabricated"]

def dump_questions():
    out = []
    for q, s in QUESTIONS.items():
        out.append(f"- `{q}` ({s['type']}): {s['instructions']}")
        for k, v in s["criteria"].items(): out.append(f"  - {k}: {v}")
    return "\n".join(out)

def domain(u):
    try: h = urlparse(u if "//" in u else "//" + u).netloc.lower()
    except Exception: return None
    return h[4:] if h.startswith("www.") else (h or None)

def main():
    if "--dump-questions" in sys.argv: print(dump_questions()); return
    ap = argparse.ArgumentParser()
    ap.add_argument("--judgments", required=True); ap.add_argument("--traces")
    ap.add_argument("--label", default="H"); ap.add_argument("--set", required=True)
    ap.add_argument("--lossmap", required=True); ap.add_argument("--refs", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--threshold", type=float, default=0.6)
    ap.add_argument("--workers", type=int, default=4); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--dump-questions", action="store_true"); ap.add_argument("--criterion-sha")
    a = ap.parse_args()
    if a.dump_questions: print(dump_questions()); return
    key = os.environ.get("VERCEL_AI_GATEWAY") or os.environ.get("AI_GATEWAY_API_KEY")
    if not key and not a.dry_run: sys.exit("no gateway key")
    J = [r for r in LM.read_jsonl(a.judgments) if r.get("ok")]
    tp = a.traces or LM.find_traces(J, a.judgments)
    T = {t["itemId"]: t for t in LM.read_jsonl(tp)}
    L = {i["id"]: i for i in json.load(open(a.lossmap))["items"]}
    cache_dir = os.path.join(os.path.dirname(os.path.abspath(a.judgments)), "rationalepass-cache"); os.makedirs(cache_dir, exist_ok=True)
    by = defaultdict(list)
    for r in J: by[r["queryId"]].append(r)
    items = []
    for qid, rows in sorted(by.items()):
        rows = sorted(rows, key=lambda r: r["order"]); t = T.get(qid, {}); lm = L[qid]
        ans = (t.get("answer") or {}).get("text") or ""
        kept = [k.get("title") for k in ((t.get("retrieval") or {}).get("kept") or []) if k.get("title")]
        st = {"rationale_1": rows[0]["verdict"]["rationale"], "rationale_2": rows[-1]["verdict"]["rationale"] if len(rows) > 1 else "",
              "answer": ans[:2500], "kept_source_titles": kept, "answer_declined": bool((t.get("answer") or {}).get("declined"))}
        # ratio per order then mean (judge ratio), script-only
        ratios = [sum(r["mapped"]["boar"][d] for d in LM.DIMS) / max(1e-9, sum(r["mapped"]["ref"][d] for d in LM.DIMS)) for r in rows]
        refpts = sum(sum(r["mapped"]["ref"][d] for d in LM.DIMS) for r in rows) / len(rows)
        items.append({"id": qid, "category": lm["category"], "primary": lm["primary"], "loss": lm["loss"], "ratio": sum(ratios) / len(ratios),
                      "ref_points": refpts, "declined": st["answer_declined"], "_state": st})
    print(f"{len(items)} items", file=sys.stderr)
    if a.dry_run: return
    cost = 0.0; cached = 0
    def work(it): return it, *LM.call({"model": LM.MODEL, "state": it["_state"], "questions": QUESTIONS}, key, cache_dir)
    with ThreadPoolExecutor(a.workers) as ex:
        for it, res, hit in ex.map(work, items):
            ans = res["answers"]; it["p"] = {q: round(ans[q]["probability"], 3) for q in AXES}
            it["labels"] = {q: ans[q]["probability"] >= a.threshold for q in AXES}
            it["fact_type"] = ans["fact_type"]["choice"]; it["fact_type_conf"] = round(ans["fact_type"].get("confidence", 0) or 0, 3)
            if hit: cached += 1
            else: cost += float(((res.get("providerMetadata") or {}).get("gateway") or {}).get("marketCost") or 0)
            del it["_state"]
    tot = sum(i["loss"] for i in items) or 1e-9
    wrong = [i for i in items if i["primary"] == "wrong"]; wl = sum(i["loss"] for i in wrong) or 1e-9
    prims = sorted({i["primary"] for i in items})
    def cell(its): return {"n": len(its), "loss_share": round(sum(i["loss"] for i in its) / tot, 3)}
    axes = {}
    for q in AXES:
        sel = [i for i in items if i["labels"][q]]
        axes[q] = {**cell(sel), "share_of_wrong_loss": round(sum(i["loss"] for i in sel if i["primary"] == "wrong") / wl, 3),
                   "n_in_wrong": sum(1 for i in sel if i["primary"] == "wrong"),
                   "by_primary": {p: cell([i for i in sel if i["primary"] == p]) for p in prims}}
    def combo(qs, pool, den):
        sel = [i for i in pool if any(i["labels"][q] for q in qs)]
        return {"n": len(sel), "share": round(sum(i["loss"] for i in sel) / den, 3)}
    combos = {"stale_of_wrong": combo(["stale"], wrong, wl), "numeric_or_date_of_wrong": combo(["numeric", "date"], wrong, wl),
              "entity_or_fabricated_of_wrong": combo(["entity_swap", "fabricated"], wrong, wl),
              "any_split_axis_of_wrong": combo(SPLIT, wrong, wl),
              "correction_named_n_of_wrong": sum(1 for i in wrong if i["labels"]["rationale_names_correction"]),
              "recent_of_wrong": combo(["recent_event"], wrong, wl), "recent_of_all": combo(["recent_event"], items, tot)}
    cmp_ = [i for i in items if i["category"] in ("comparison", "synthesis")]
    cl = sum(i["loss"] for i in cmp_) or 1e-9
    ft = {}
    for f in QUESTIONS["fact_type"]["criteria"]:
        s = [i for i in cmp_ if i["fact_type"] == f]
        ft[f] = {"n": len(s), "share_of_cmp_syn_loss": round(sum(i["loss"] for i in s) / cl, 3)}
    # oracle: replace wrong-primary ratio with decline ratio
    dec = [i for i in items if i["declined"]]
    if dec: dec_ratio = sum(i["ratio"] for i in dec) / len(dec); src = f"mean ratio of {len(dec)} declined items"
    else: dec_ratio = None; src = "rubric floor 3/ref_points"
    def new_ratio(i): return dec_ratio if dec_ratio is not None else 3.0 / max(1e-9, i["ref_points"])
    wset = {i["id"] for i in wrong}
    base = sum(i["ratio"] for i in items) / len(items)
    rep = sum((new_ratio(i) if i["id"] in wset else i["ratio"]) for i in items) / len(items)
    oracle = {"decline_source": src, "n_wrong": len(wrong), "mean_ratio_wrong_items": round(sum(i["ratio"] for i in wrong) / max(1, len(wrong)), 3),
              "mean_ratio_decline_substitute": round(sum(new_ratio(i) for i in wrong) / max(1, len(wrong)), 3),
              "mean_ratio_all_before": round(base, 4), "mean_ratio_all_after": round(rep, 4), "paired_delta": round(rep - base, 4),
              "n_wrong_items_where_decline_better": sum(1 for i in wrong if new_ratio(i) > i["ratio"])}
    # CITEMAP-REF
    refs = {json.loads(l)["id"]: json.loads(l).get("reference_sources") for l in open(a.refs) if l.strip()}
    ids = {i["id"] for i in items}; dom = Counter(); nitems = 0; nurls = 0; noref = 0
    for k in ids:
        rs = refs.get(k)
        if not rs: noref += 1; continue
        nitems += 1; ds = set()
        for u in rs:
            nurls += 1; d = domain(u)
            if d: ds.add(d)
        dom.update(ds)
    citemap = {"items_with_refs": nitems, "items_without_refs": noref, "urls": nurls, "unit": "items citing the domain at least once", "top15": dom.most_common(15)}
    out = {"arm": a.label, "set": a.set, "n": len(items), "threshold": a.threshold, "model": LM.MODEL, "criterion_sha256": a.criterion_sha,
           "gateway_cost_usd": round(cost, 5), "cached": cached, "total_loss_points": round(tot, 2), "primary_loss": {p: cell([i for i in items if i["primary"] == p]) for p in prims},
           "axes": axes, "combos": combos, "fact_type_cmp_syn": {"n_items": len(cmp_), "categories_used": sorted({i["category"] for i in cmp_}), **ft},
           "decline_oracle": oracle, "citemap_ref": citemap, "items": items}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True); json.dump(out, open(a.out, "w"), indent=1)
    print(a.set, "cost", out["gateway_cost_usd"], "cached", cached, "combos", combos, "oracle", oracle["paired_delta"])

if __name__ == "__main__": main()
