"""SFT4B stage 0, v2 targets filter: same frozen jev filters as v1 (quote_supports >= 0.9, answers_question >= 0.8, same
questions/criteria text, same cache + spend file, same cumulative [usage detail removed] arm cap) on data/raw-v2-*.jsonl.
Pre-jev checks: 35-60 words; >= 1 citation; every [n] is a shown passage; word-Jaccard < 0.5 vs the 220 self-test questions.
Selection: train = first passing round per article, water-filled to <= 1,200 across packs (seed 42); hold-out = the same 100
articles as v1, first passing round. Writes data/train.v2.jsonl, data/holdout.v2.jsonl (+ .meta), data/retry-v2-<split>.txt,
aggregates/filter-v2.json. Usage: python3 -I filter_v2.py"""
import glob, json, os, random, re, statistics as S, sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import filter_jev as F  # noqa: E402

ARM = F.ARM


def main():
    os.makedirs(F.CACHE, exist_ok=True); F.lock_spent[0] = spent0 = F.spent_total()
    st_qs = [F.wset(json.loads(l)["question"]) for f in glob.glob(f"{F.ST}/*.jsonl") for l in open(f) if l.strip()]
    raws = [json.loads(l) for f in sorted(glob.glob(f"{ARM}/data/raw-v2-*.jsonl")) for l in open(f) if l.strip()]
    for r in raws: r["xid"] = f"{r['split']}:{r['round']}:{r['pack']}:{r['article_id']}"
    drops, cand = Counter(), []
    for r in raws:
        a = r["answer"]; n = len(a.split()); cites = {int(x) for x in re.findall(r"\[(\d+)\]", a)}
        if not cites: drops["no_citation"] += 1; continue
        if not cites <= set(range(1, len(r["kept"]) + 1)): drops["cites_unshown_passage"] += 1; continue
        if n < 35 or n > 60: drops["length_out_of_35_60"] += 1; continue
        q = F.wset(r["question"]); leak = max(len(q & s) / max(1, len(q | s)) for s in st_qs)
        if leak >= 0.5: drops["selftest_similar_q"] += 1; continue
        cand.append({**r, "leak_jaccard": round(leak, 3)})
    results, stopped, newreq = {}, None, 0
    try:
        with ThreadPoolExecutor(8) as ex:
            for c, (rec, cost, hit) in zip(cand, ex.map(lambda c: F.jev({"passages": c["passages"], "question": c["question"], "answer": c["answer"]}), cand)):
                results[c["xid"]] = rec["answers"]; newreq += not hit
    except RuntimeError as e:
        stopped = f"jev cap ${F.CAP} reached ({e})"
    passed = []
    for c in cand:
        a = results.get(c["xid"])
        if a is None: drops["not_checked"] += 1; continue
        c["jev"] = a
        if a["quote_supports"] < F.TH_QS: drops["jev_quote_supports"] += 1; continue
        if a["answers_question"] < F.TH_AQ: drops["jev_answers_question"] += 1; continue
        passed.append(c)
    first = {}
    for c in sorted(passed, key=lambda c: c["round"]):
        first.setdefault((c["split"], c["pack"], c["article_id"]), c)
    rng = random.Random(42); by = defaultdict(list)
    for c in first.values():
        if c["split"] == "train": by[c["pack"]].append(c)
    for v in by.values(): v.sort(key=lambda c: c["article_id"]); rng.shuffle(v)
    cap = 0
    while cap + 1 <= max((len(v) for v in by.values()), default=0) and sum(min(len(v), cap + 1) for v in by.values()) <= F.TARGET: cap += 1
    sel = [c for v in by.values() for c in v[:cap]]
    extra = [c for v in by.values() for c in v[cap:cap + 1]]; rng.shuffle(extra); sel += extra[:max(0, F.TARGET - len(sel))]
    ho = sorted([c for c in first.values() if c["split"] == "holdout"], key=lambda c: (c["pack"], c["article_id"]))[:F.N_HOLD]

    def write(name, rows):
        with open(f"{ARM}/data/{name}.jsonl", "w") as f, open(f"{ARM}/data/{name}.meta.jsonl", "w") as m:
            for c in rows:
                f.write(json.dumps({"messages": c["messages"] + [{"role": "assistant", "content": c["answer"]}]}) + "\n")
                m.write(json.dumps({k: c[k] for k in ("split", "round", "v1_round", "pack", "article_id", "title", "chunk_ids", "kept", "question", "answer", "jev", "leak_jaccard")}) + "\n")
    write("train.v2", sorted(sel, key=lambda c: (c["pack"], c["article_id"]))); write("holdout.v2", ho)
    okk = set(first)
    for sp in ("train", "holdout"):
        fail = sorted({f"{r['pack']}:{r['article_id']}" for r in raws if r["split"] == sp and (sp, r["pack"], r["article_id"]) not in okk})
        open(f"{ARM}/data/retry-v2-{sp}.txt", "w").write("\n".join(fail) + "\n")

    def lens(rows):
        w = sorted(len(c["answer"].split()) for c in rows)
        return {"median": S.median(w), "p10": w[len(w) // 10], "p90": w[9 * len(w) // 10]} if w else {}

    def cites(rows):
        return dict(Counter("+".join(sorted(set(re.findall(r"\[(\d)\]", c["answer"])))) for c in rows))
    rounds = sorted({r["round"] for r in raws})
    agg = {"raw": len(raws), "pre_jev_drops": {k: v for k, v in drops.items() if not k.startswith("jev") and k != "not_checked"},
           "jev_checked": len(results), "jev_drops": {k: drops[k] for k in ("jev_quote_supports", "jev_answers_question", "not_checked")},
           "jev_pass": len(passed), "jev_pass_rate": round(len(passed) / max(1, len(results)), 3),
           "by_round": {f"r{k}": {"raw": sum(r["round"] == k for r in raws), "checked": sum(c["round"] == k and c["xid"] in results for c in cand),
                                  "pass": sum(c["round"] == k for c in passed),
                                  "pass_rate_of_checked": round(sum(c["round"] == k for c in passed) / max(1, sum(c["round"] == k and c["xid"] in results for c in cand)), 3)}
                        for k in rounds},
           "train_v2": len(sel), "holdout_v2": len(ho), "per_pack_cap": cap,
           "per_pack_train": dict(Counter(c["pack"] for c in sel)),
           "train_len_words": lens(sel), "holdout_len_words": lens(ho), "train_cites": cites(sel), "holdout_cites": cites(ho),
           "train_two_passage_prompts": sum(len(c["kept"]) == 2 for c in sel),
           "jev_new_requests_this_run": newreq, "jev_spend_this_run_usd": round(F.spent_total() - spent0, 5),
           "jev_spend_arm_total_usd": round(F.spent_total(), 5), "cap_usd": F.CAP, "stopped": stopped}
    json.dump(agg, open(f"{ARM}/aggregates/filter-v2.json", "w"), indent=1)
    print(json.dumps(agg))


if __name__ == "__main__":
    main()
