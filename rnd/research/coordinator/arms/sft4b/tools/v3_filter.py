"""SFT4B v3 step 4-6: filters, selection, 0-call gates (SFT4B-criterion-addendum-2, sha 653745c7...).
Pre-jev: 40-60 words; self-test word-Jaccard < 0.5; gold-present: >= 1 citation, every [n] is a gold passage; gold-absent: opens with
the engine's uncited line, no [n], writer's covered = false.
jev (typesafe-ai/jev /v1/evaluate; cache runs/jev-cache, spend runs/jev-spend.jsonl shared with v1/v2; arm cap [usage detail removed] cumulative):
  gold-present state {question, answer, cited_passages, uncited_passages}: quote_supports >= 0.9 (answer vs cited_passages),
    answers_question >= 0.8, no_distractor_attribution = P(NO to "states as fact anything that appears only in
    uncited_passages") >= 0.8;
  gold-absent state {question, answer, uncited_passages (= all shown)}: no_distractor_attribution >= 0.9,
    answers_question (general-answer wording) >= 0.6.
Selection (seed 42): first passing round per example; train gold-present all (water-filled to <= 1,200 per-pack balanced if
more), gold-absent sampled to 20 % of the train set; hold-out = first passing example per hold-out article.
Writes data/train.v3.jsonl, data/holdout.v3.jsonl (+ .meta), data/holdout.v3.review20.jsonl, data/retry-v3-<split>.txt,
aggregates/filter-v3.json. Usage: python3 -I v3_filter.py [--final]  (--final also writes the datasets)"""
import glob, hashlib, json, os, random, re, statistics as S, sys, time, urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zstd_shim  # noqa: E402,F401
import filter_jev as F  # noqa: E402
from v3_write import NOSRC  # noqa: E402

ARM = F.ARM; CAP = 0.30; BAL0 = 0.369; BAL_FLOOR = 0.15; SPENT_BEFORE_V3 = 0.1360128
DISTR = {"type": "boolean",
         "instructions": "Does `answer` state as fact anything (a claim, number, name or detail) that appears only in `uncited_passages` and not in `cited_passages`? Ignore citation markers such as [1].",
         "criteria": {"true": "`answer` contains at least one fact taken from `uncited_passages` that `cited_passages` does not state.",
                      "false": "Nothing in `answer` is drawn only from `uncited_passages`."}}
Q_PRESENT = {"quote_supports": {**F.QUESTIONS["quote_supports"],
                 "instructions": "Is every factual claim in `answer` (ignore citation markers such as [1] or [2]) explicitly stated in, or directly entailed by, the text of `cited_passages`?",
                 "criteria": {"true": "Every fact, number, name, cause and recommendation in `answer` can be found in `cited_passages`.",
                              "false": "`answer` contains at least one claim, detail or number that `cited_passages` does not state, or contradicts `cited_passages`."}},
             "answers_question": F.QUESTIONS["answers_question"], "distractor_fact": DISTR}
Q_ABSENT = {"answers_question": {"type": "boolean",
                "instructions": "Setting aside an opening note that no offline source covers the question, does `answer` give a direct, relevant general answer to `question`?",
                "criteria": {"true": "After the note, a user who asked `question` gets a relevant, specific general answer.",
                             "false": "`answer` is off-target, evasive, or gives no actual answer after the note."}},
            "distractor_fact": {**DISTR, "instructions": "Does `answer` state as fact anything (a claim, number, name or detail) that appears in `uncited_passages`? Ignore an opening note that no offline source covers the question.",
                                "criteria": {"true": "`answer` contains at least one fact or detail taken from `uncited_passages`.",
                                             "false": "Nothing in `answer` is drawn from `uncited_passages`."}}}
TH = {"present": {"quote_supports": 0.9, "answers_question": 0.8, "no_distractor_attribution": 0.8},
      "absent": {"no_distractor_attribution": 0.9, "answers_question": 0.6}}
lock = [0.0]


def jev(state, questions):
    body = json.dumps({"model": "typesafe-ai/jev", "state": state, "questions": questions}, sort_keys=True)
    h = hashlib.sha256(body.encode()).hexdigest(); f = f"{F.CACHE}/{h}.json"
    if os.path.exists(f): return json.load(open(f)), True
    if lock[0] + 0.0005 > CAP or BAL0 - (lock[0] - SPENT_BEFORE_V3) < BAL_FLOOR + 0.0005: raise RuntimeError("CAP")
    for att in range(6):
        try:
            req = urllib.request.Request("https://ai-gateway.vercel.sh/v1/evaluate", data=body.encode(),
                                         headers={"authorization": f"Bearer {F.KEY}", "content-type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=60)); break
        except Exception:
            if att == 5: raise
            time.sleep(min(8, 2 ** att))
    ans = {k: r["answers"][k]["probability"] for k in questions}
    cost = float(((r.get("providerMetadata") or {}).get("gateway") or {}).get("marketCost") or 0)
    rec = {"answers": ans, "inputTokens": (r.get("usage") or {}).get("inputTokens"), "cost": cost}
    json.dump(rec, open(f, "w")); lock[0] += cost
    with open(F.SPEND, "a") as fh: fh.write(json.dumps({"at": time.strftime("%FT%T"), "hash": h[:16], "cost": cost, "tok": rec["inputTokens"], "arm": "v3"}) + "\n")
    return rec, False


def split_passages(passages):
    return {int(m.group(1)): blk for blk in re.split(r"\n\n(?=\[\d+\] )", passages) for m in [re.match(r"\[(\d+)\] ", blk)] if m}


def state_of(c):
    blocks = split_passages(c["passages"])
    if c["mode"] == "absent":
        return {"question": c["question"], "answer": c["answer"], "uncited_passages": "\n\n".join(blocks.values())}, Q_ABSENT
    cited = sorted({int(x) for x in re.findall(r"\[(\d+)\]", c["answer"])})
    return {"question": c["question"], "answer": c["answer"], "cited_passages": "\n\n".join(blocks[i] for i in cited),
            "uncited_passages": "\n\n".join(b for i, b in blocks.items() if i not in cited)}, Q_PRESENT


def main():
    final = "--final" in sys.argv
    os.makedirs(F.CACHE, exist_ok=True); lock[0] = spent0 = F.spent_total()
    st_qs = [F.wset(json.loads(l)["question"]) for f in glob.glob(f"{F.ST}/*.jsonl") for l in open(f) if l.strip()]
    raws = [json.loads(l) for f in sorted(glob.glob(f"{ARM}/data/raw-v3-*.jsonl")) for l in open(f) if l.strip()]
    drops, cand = Counter(), []
    for r in raws:
        a = r["answer"]; n = len(a.split()); cites = {int(x) for x in re.findall(r"\[(\d+)\]", a)}
        r["rid"] = f"{r['round']}:{r['xid']}"
        if r["mode"] == "present":
            if not cites: drops["present_no_citation"] += 1; continue
            if not cites <= set(r["gold_pos"]): drops["present_cites_distractor"] += 1; continue
        else:
            if r["covered"]: drops["absent_writer_says_covered"] += 1; continue
            if cites or not a.startswith(NOSRC): drops["absent_format"] += 1; continue
        if n < 40 or n > 60: drops[f"{r['mode']}_length_out_of_40_60"] += 1; continue
        q = F.wset(r["question"]); leak = max(len(q & s) / max(1, len(q | s)) for s in st_qs)
        if leak >= 0.5: drops["selftest_similar_q"] += 1; continue
        cand.append({**r, "leak_jaccard": round(leak, 3), "n_cited": len(cites)})
    results, stopped, newreq = {}, None, 0

    def one(c):
        st, qs = state_of(c); return jev(st, qs)
    try:
        with ThreadPoolExecutor(8) as ex:
            for c, (rec, hit) in zip(cand, ex.map(one, cand)):
                a = dict(rec["answers"]); a["no_distractor_attribution"] = round(1 - a.pop("distractor_fact"), 4)
                results[c["rid"]] = a; newreq += not hit
    except RuntimeError as e:
        stopped = f"jev cap reached ({e})"
    passed = []
    for c in cand:
        a = results.get(c["rid"])
        if a is None: drops["not_checked"] += 1; continue
        c["jev"] = a
        bad = [k for k, t in TH[c["mode"]].items() if a[k] < t]
        if bad: drops[f"jev_{c['mode']}_{bad[0]}"] += 1; continue
        passed.append(c)
    first = {}
    for c in sorted(passed, key=lambda c: c["round"]): first.setdefault(c["xid"], c)
    rng = random.Random(42)
    tp = sorted([c for c in first.values() if c["split"] == "train" and c["mode"] == "present"], key=lambda c: c["xid"])
    ta = sorted([c for c in first.values() if c["split"] == "train" and c["mode"] == "absent"], key=lambda c: c["xid"])
    if len(tp) > 1200:
        by = defaultdict(list)
        for c in tp: by[c["pack"]].append(c)
        for v in by.values(): rng.shuffle(v)
        cap = 0
        while sum(min(len(v), cap + 1) for v in by.values()) <= 1200: cap += 1
        tp = [c for v in by.values() for c in v[:cap]]
    n_abs = round(len(tp) * 0.20 / 0.80)
    rng.shuffle(ta); ta = ta[:n_abs]
    train = sorted(tp + ta, key=lambda c: (c["pack"], c["article_id"], c["mode"]))
    ho = sorted([c for c in first.values() if c["split"] == "holdout"], key=lambda c: (c["pack"], c["article_id"]))
    for sp in ("train", "holdout"):
        allx = {r["xid"] for r in raws if r["split"] == sp}
        open(f"{ARM}/data/retry-v3-{sp}.txt", "w").write("\n".join(sorted(allx - set(first))) + "\n")

    def lens(rows):
        w = sorted(len(c["answer"].split()) for c in rows)
        return {"median": S.median(w), "p10": w[len(w) // 10], "p90": w[9 * len(w) // 10], "min": w[0], "max": w[-1]} if w else {}
    rounds = sorted({r["round"] for r in raws})
    chk = lambda k: sum(c["round"] == k and c["rid"] in results for c in cand)
    ps = lambda k: sum(c["round"] == k for c in passed)
    pres = [c for c in train if c["mode"] == "present"]
    multi = sum(c["n_cited"] > 1 for c in pres)
    r1c, r1p = chk(1), ps(1)
    gates = {"kept_ge_1000": [len(train), len(train) >= 1000],
             "median_words_ge_35": [lens(train).get("median"), (lens(train).get("median") or 0) >= 35],
             "gold_present_multi_cite_ge_30pct": [round(multi / max(1, len(pres)), 3), multi / max(1, len(pres)) >= 0.30],
             "jev_round1_pass_ge_50pct": [round(r1p / max(1, r1c), 3), r1p / max(1, r1c) >= 0.50],
             "gold_absent_share_15_25pct": [round(len(ta) / max(1, len(train)), 3), 0.15 <= len(ta) / max(1, len(train)) <= 0.25]}
    agg = {"raw": len(raws), "raw_by_split_mode_round": dict(Counter(f"{r['split']}/{r['mode']}/r{r['round']}" for r in raws)),
           "pre_jev_drops": {k: v for k, v in drops.items() if not k.startswith("jev") and k != "not_checked"},
           "jev_checked": len(results), "jev_drops": {k: v for k, v in drops.items() if k.startswith("jev") or k == "not_checked"},
           "jev_pass": len(passed),
           "by_round": {f"r{k}": {"raw": sum(r["round"] == k for r in raws), "checked": chk(k), "pass": ps(k), "pass_rate_of_checked": round(ps(k) / max(1, chk(k)), 3),
                                  "by_mode": {m: {"checked": sum(c["round"] == k and c["mode"] == m and c["rid"] in results for c in cand),
                                                  "pass": sum(c["round"] == k and c["mode"] == m for c in passed)} for m in ("present", "absent")}} for k in rounds},
           "train": {"n": len(train), "present": len(pres), "absent": len(ta), "per_pack": dict(Counter(c["pack"] for c in train)),
                     "len_words": lens(train), "len_present": lens(pres), "len_absent": lens(ta),
                     "n_cited_present": dict(Counter(c["n_cited"] for c in pres)), "n_shown": dict(Counter(len(c["kept"]) for c in train)),
                     "gold_pos_first": dict(Counter(c["gold_pos"][0] for c in pres)), "two_gold_prompts_present": sum(len(c["gold_pos"]) == 2 for c in pres),
                     "distinct_articles": len({c["cid"] for c in train}), "by_round": dict(Counter(c["round"] for c in train)),
                     "max_selftest_jaccard": max((c["leak_jaccard"] for c in train), default=None)},
           "holdout": {"n": len(ho), "present": sum(c["mode"] == "present" for c in ho), "absent": sum(c["mode"] == "absent" for c in ho),
                       "len_words": lens(ho), "n_cited_present": dict(Counter(c["n_cited"] for c in ho if c["mode"] == "present"))},
           "gates": gates, "jev_new_requests_this_run": newreq, "jev_spend_this_run_usd": round(F.spent_total() - spent0, 5),
           "jev_spend_v3_usd": round(F.spent_total() - SPENT_BEFORE_V3, 5), "jev_spend_arm_total_usd": round(F.spent_total(), 5), "cap_usd": CAP, "stopped": stopped}
    json.dump(agg, open(f"{ARM}/aggregates/filter-v3.json", "w"), indent=1)
    if final:
        def write(name, rows):
            with open(f"{ARM}/data/{name}.jsonl", "w") as f, open(f"{ARM}/data/{name}.meta.jsonl", "w") as m:
                for c in rows:
                    f.write(json.dumps({"messages": c["messages"] + [{"role": "assistant", "content": c["answer"]}]}) + "\n")
                    m.write(json.dumps({k: c[k] for k in ("xid", "split", "round", "mode", "pack", "article_id", "title", "question", "answer", "kept",
                                                          "gold_chunk_ids", "distractor_chunk_ids", "distractor_src", "gold_pos", "n_cited", "jev", "leak_jaccard", "replay")}) + "\n")
        write("train.v3", train); write("holdout.v3", ho)
        r = random.Random(42); s20 = sorted(r.sample(range(len(ho)), min(20, len(ho))))
        with open(f"{ARM}/data/holdout.v3.review20.jsonl", "w") as f:
            for i in s20:
                c = ho[i]
                f.write(json.dumps({"xid": c["xid"], "mode": c["mode"], "gold_pos": c["gold_pos"], "question": c["question"], "passages": c["passages"], "answer": c["answer"], "jev": c["jev"]}) + "\n")
    print(json.dumps(agg))


if __name__ == "__main__":
    main()
