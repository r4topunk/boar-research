"""SFT4B stage 0, steps 4-5: render -> map citations -> jev filter -> data/train.jsonl + data/holdout.jsonl.

Per raw example (data/raw-<split>*.jsonl):
  1. render the engine's exact prompt (render_prompt.render: cut-7 compressContext + assembleChatMessages) for the question;
  2. map the writer's [A]/[B] to the rendered [n] (compression may reorder or drop a chunk) -> drop if a cited chunk is not
     in the prompt, if the answer has no citation, or > 60 words;
  3. jev (typesafe-ai/jev via the AI Gateway /v1/evaluate, one request per example, 2 boolean questions) on
     state {passages: the rendered context block, question, answer}: quote_supports >= 0.9 AND answers_question >= 0.8.
  4. leakage guard: drop if word-Jaccard >= 0.5 with any of the 220 self-test questions (counted).
Every jev verdict is cached on disk (runs/jev-cache/<sha256 of request body>.json); spend = providerMetadata.gateway.marketCost
summed over uncached requests and appended to runs/jev-spend.jsonl; HARD CAP [usage detail removed] cumulative (stops before exceeding, reports).
Train selection: all passing train examples, water-filled to <= 1,200 across packs (seed 42). Hold-out: first passing example
per reserved article (round 1, then later rounds), 100.
Writes data/train.jsonl, data/holdout.jsonl (mlx-lm chat format: {"messages": [system, user, assistant]}), data/*.meta.jsonl,
aggregates/filter.json. Usage: python3 -I filter_jev.py [--dry] (dry: no jev calls, cached verdicts only)"""
import glob, hashlib, json, os, random, re, sys, time, urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_prompt import render  # noqa: E402

ARM = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ST = "<workspace>/rnd/research/packs/selftest"
CACHE = f"{ARM}/runs/jev-cache"; SPEND = f"{ARM}/runs/jev-spend.jsonl"
CAP = 0.20; TH_QS, TH_AQ = 0.9, 0.8; TARGET = 1200; N_HOLD = 100
KEY = os.environ.get("VERCEL_AI_GATEWAY") or os.environ.get("AI_GATEWAY_API_KEY")
QUESTIONS = {
    "quote_supports": {"type": "boolean",
        "instructions": "Is every factual claim in `answer` (ignore citation markers such as [1] or [2]) explicitly stated in, or directly entailed by, the text of `passages`?",
        "criteria": {"true": "Every fact, number, name, cause and recommendation in `answer` can be found in `passages`.",
                     "false": "`answer` contains at least one claim, detail or number that `passages` does not state, or contradicts `passages`."}},
    "answers_question": {"type": "boolean",
        "instructions": "Does `answer` directly and specifically answer `question`?",
        "criteria": {"true": "A user who asked `question` gets the specific information they asked for.",
                     "false": "`answer` is off-target, evasive, only partly related, or says the information is not available."}},
}
lock_spent = [0.0]


def spent_total():
    return sum(json.loads(l)["cost"] for l in open(SPEND)) if os.path.exists(SPEND) else 0.0


def jev(state, dry=False):
    body = json.dumps({"model": "typesafe-ai/jev", "state": state, "questions": QUESTIONS}, sort_keys=True)
    h = hashlib.sha256(body.encode()).hexdigest(); f = f"{CACHE}/{h}.json"
    if os.path.exists(f): return json.load(open(f)), 0.0, True
    if dry: return None, 0.0, False
    if lock_spent[0] + 0.0005 > CAP: raise RuntimeError("CAP")
    for att in range(6):
        try:
            req = urllib.request.Request("https://ai-gateway.vercel.sh/v1/evaluate", data=body.encode(),
                                         headers={"authorization": f"Bearer {KEY}", "content-type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=60))
            break
        except Exception as e:
            if att == 5: raise
            time.sleep(min(8, 2 ** att))
    ans = {k: r["answers"][k]["probability"] for k in QUESTIONS}
    cost = float(((r.get("providerMetadata") or {}).get("gateway") or {}).get("marketCost") or 0)
    rec = {"answers": ans, "inputTokens": (r.get("usage") or {}).get("inputTokens"), "cost": cost}
    json.dump(rec, open(f, "w"))
    lock_spent[0] += cost
    with open(SPEND, "a") as fh: fh.write(json.dumps({"at": time.strftime("%FT%T"), "hash": h[:16], "cost": cost, "tok": rec["inputTokens"]}) + "\n")
    return rec, cost, False


WORD = re.compile(r"[a-z0-9]+")
def wset(s): return set(WORD.findall(s.lower()))


def main():
    dry = "--dry" in sys.argv
    os.makedirs(CACHE, exist_ok=True); lock_spent[0] = spent_total()
    st_qs = [wset(json.loads(l)["question"]) for f in glob.glob(f"{ST}/*.jsonl") for l in open(f) if l.strip()]
    raws = []
    for f in sorted(glob.glob(f"{ARM}/data/raw-train*.jsonl") + glob.glob(f"{ARM}/data/raw-holdout*.jsonl")):  # v1 only (not raw-v2-*)
        raws += [json.loads(l) for l in open(f) if l.strip()]
    for i, r in enumerate(raws): r["xid"] = f"{r['split']}:{r['round']}:{r['pack']}:{r['article_id']}"
    rendered = {o["id"]: o for o in render([{"id": r["xid"], "question": r["question"], "chunks": [(r["pack"], c) for c in r["chunk_ids"]]} for r in raws])}
    drops = Counter(); cand = []
    for r in raws:
        o = rendered[r["xid"]]
        num = {c: i + 1 for i, c in enumerate(o["kept"])}  # kept ids are "pack:<pack>:<chunk id>"
        letters = {L: f"pack:{r['pack']}:{c}" for L, c in zip("AB", r["chunk_ids"])}
        cited = set(re.findall(r"\[([AB])\]", r["answer_letters"]))
        if not cited: drops["no_citation"] += 1; continue
        if any(letters.get(L) not in num for L in cited): drops["cited_chunk_not_in_prompt"] += 1; continue
        ans = re.sub(r"\[([AB])\]", lambda m: f"[{num[letters[m.group(1)]]}]", r["answer_letters"])
        ans = re.sub(r"\[(\d)\](\s*)\[\1\]", r"[\1]", ans)
        if re.search(r"\[[^\]0-9]*\]", ans): drops["bad_marker"] += 1; continue
        if len(ans.split()) > 60: drops["over_60_words"] += 1; continue
        q = wset(r["question"]); leak = max((len(q & s) / max(1, len(q | s)) for s in st_qs), default=0)
        if leak >= 0.5: drops["selftest_similar_q"] += 1; continue
        sysm = o["messages"][0]["content"]
        passages = sysm.split("\n\nContext:\n", 1)[1]
        cand.append({**r, "answer": ans, "messages": o["messages"], "passages": passages, "leak_jaccard": round(leak, 3)})
    calls = {"cached": 0, "new": 0}; stopped = None

    def check(c):
        return jev({"passages": c["passages"], "question": c["question"], "answer": c["answer"]}, dry)
    results = {}
    try:
        with ThreadPoolExecutor(8) as ex:
            for c, res in zip(cand, ex.map(lambda c: (c, check(c)), cand)):
                rec, cost, hit = res[1]
                if rec is None: continue
                calls["cached" if hit else "new"] += 1; results[c["xid"]] = rec["answers"]
    except RuntimeError as e:
        stopped = f"jev cap ${CAP} reached ({e})"
    passed = []
    for c in cand:
        a = results.get(c["xid"])
        if a is None: drops["not_checked"] += 1; continue
        c["jev"] = a
        if a["quote_supports"] < TH_QS: drops["jev_quote_supports"] += 1; continue
        if a["answers_question"] < TH_AQ: drops["jev_answers_question"] += 1; continue
        passed.append(c)
    # selection
    rng = random.Random(42)
    tr, seen_tr = [], set()
    for c in sorted([c for c in passed if c["split"] == "train"], key=lambda c: c["round"]):
        if (c["pack"], c["article_id"]) not in seen_tr: seen_tr.add((c["pack"], c["article_id"])); tr.append(c)
    by = defaultdict(list)
    for c in tr: by[c["pack"]].append(c)
    for v in by.values(): rng.shuffle(v)
    cap, sel = 0, []
    while True:  # water-filling: largest per-pack cap with total <= TARGET
        tot = sum(min(len(v), cap + 1) for v in by.values())
        if tot > TARGET or cap + 1 > max((len(v) for v in by.values()), default=0): break
        cap += 1
    for v in by.values(): sel += v[:cap]
    left = TARGET - len(sel); extra = [c for v in by.values() for c in v[cap:cap + 1]]; rng.shuffle(extra); sel += extra[:max(0, left)]
    ho, seen = [], set()
    for c in sorted([c for c in passed if c["split"] == "holdout"], key=lambda c: (c["round"], c["pack"], c["article_id"])):
        k = (c["pack"], c["article_id"])
        if k in seen: continue
        seen.add(k); ho.append(c)
    ho = ho[:N_HOLD]
    def write(name, rows):
        with open(f"{ARM}/data/{name}.jsonl", "w") as f, open(f"{ARM}/data/{name}.meta.jsonl", "w") as m:
            for c in rows:
                f.write(json.dumps({"messages": c["messages"] + [{"role": "assistant", "content": c["answer"]}]}) + "\n")
                m.write(json.dumps({k: c[k] for k in ("split", "round", "pack", "article_id", "title", "chunk_ids", "question", "answer", "fact_quote", "jev", "leak_jaccard")}) + "\n")
    if not dry:
        write("train", sorted(sel, key=lambda c: (c["pack"], c["article_id"]))); write("holdout", ho)
    per = {}
    for p in sorted({r["pack"] for r in raws}):
        rr = [c for c in cand if c["pack"] == p and c["xid"] in results]
        per[p] = {"raw": sum(r["pack"] == p for r in raws), "jev_checked": len(rr),
                  "jev_pass": sum(c in passed for c in rr), "pass_rate": round(sum(c in passed for c in rr) / max(1, len(rr)), 3),
                  "train_selected": sum(c["pack"] == p for c in sel), "holdout": sum(c["pack"] == p for c in ho)}
    checked = sum(v["jev_checked"] for v in per.values()); npass = len(passed)
    agg = {"raw": len(raws), "pre_jev_drops": {k: v for k, v in drops.items() if not k.startswith("jev") and k != "not_checked"},
           "jev_checked": checked, "jev_drops": {k: drops[k] for k in ("jev_quote_supports", "jev_answers_question", "not_checked")},
           "jev_pass": npass, "jev_pass_rate": round(npass / max(1, checked), 3),
           "pass_rate_of_raw": round(npass / max(1, len(raws)), 3),
           "train": len(sel), "holdout": len(ho), "per_pack_cap": cap, "per_pack": per,
           "jev_requests": calls, "jev_spend_usd_total": round(spent_total(), 5), "cap_usd": CAP, "stopped": stopped,
           "thresholds": {"quote_supports": TH_QS, "answers_question": TH_AQ}}
    # retry lists: articles with no passing example yet (any round) -> write_examples.py --round N+1 --ids-from
    okk = {(c["split"], c["pack"], c["article_id"]) for c in passed}
    for sp in ("train", "holdout"):
        fail = sorted({f"{r['pack']}:{r['article_id']}" for r in raws if r["split"] == sp and (sp, r["pack"], r["article_id"]) not in okk})
        if not dry: open(f"{ARM}/data/retry-{sp}.txt", "w").write("\n".join(fail) + "\n")
        agg[f"retry_{sp}"] = len(fail)
    rounds = sorted({r["round"] for r in raws})
    agg["by_round"] = {f"r{k}": {"raw": sum(r["round"] == k for r in raws), "checked": sum(c["round"] == k and c["xid"] in results for c in cand),
                                 "pass": sum(c["round"] == k for c in passed)} for k in rounds}
    if not dry: json.dump(agg, open(f"{ARM}/aggregates/filter.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in agg.items() if k != "per_pack"}))


if __name__ == "__main__":
    main()
