"""SEARCHPAR R5 scorer (0 LLM). python3 -I tools/score_r5.py -> r5.json (+ prints).
QFORM F8 (48, history = the F0 turn): gold hit = normalised gold quote in title+body of a kept chunk (sweep.py rule, quote only: merged chunk ids do not exist in the 13-pack kit).
LONGSESSION turns 2-5: no fact labels; proxy = a follow-up item's `referent` string in the title/body of a kept chunk; plus kept-list changes, sticky adds, junk."""
import json, re, os, sys, statistics, random, glob
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = "<workspace>/rnd/research/coordinator/arms"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s.lower())).strip()
items = {d["id"]: d for d in rd(A + "/qform/items/qform.jsonl")}
tok = lambda c: -(-len(f"{c['title']}\n{c['body']}") // 4)
def load(name):
    f = f"{D}/replays/{name}.jsonl"
    return {r["id"]: r for r in rd(f)} if os.path.exists(f) else None
def boot(va, vb, ids, B=2000, seed=11):
    rng = random.Random(seed); d = [va[i] - vb[i] for i in ids]; n = len(d); bs = sorted(sum(d[rng.randrange(n)] for _ in range(n)) for _ in range(B))
    return sum(d), bs[int(.025 * B)], bs[int(.975 * B) - 1]
def ghit(lst, it): q = norm(it["gold"]["quote"]); return any(q in norm(c["title"] + " " + c["body"]) for c in lst)
def sticky_ids(r): return [c[len("sticky:add:"):] for c in r["reasonCodes"] if c.startswith("sticky:add:")]
out = {}
# ---------------------------------------------------------------- QFORM F8
def qform(arms):
    F8 = sorted(i for i in items if i.endswith("-F8"))
    base = load("qform.off"); res = {"n": len(F8), "arms": {}}
    wide = {i: ghit(base[i]["wideFull"], items[i]) for i in F8}
    f0kept = {i: ghit(base[i[:-1] + "0"]["keptFull"], items[i]) for i in F8}
    for a in arms:
        R = load(a)
        if not R: continue
        kept = {i: int(ghit(R[i]["keptFull"], items[i])) for i in F8}; bk = {i: int(ghit(base[i]["keptFull"], items[i])) for i in F8}
        nk = {i: len(R[i]["keptFull"]) for i in F8}; bnk = {i: len(base[i]["keptFull"]) for i in F8}
        sk = {i: sticky_ids(R[i]) for i in F8}
        d, lo, hi = boot(kept, bk, F8)
        junk_fixed = lambda N: statistics.mean(N[i] for i in F8 if not wide[i])
        junk_arm = lambda K, N: statistics.mean(N[i] for i in F8 if not K[i])
        carried_gold = {i: f0kept[i] for i in F8}  # the previous turn's kept list holds the gold quote
        res["arms"][a] = dict(kept=sum(kept.values()), base=sum(bk.values()), delta=d, ci=[lo, hi],
            gained=[i for i in F8 if kept[i] > bk[i]], lost=[i for i in F8 if kept[i] < bk[i]],
            items_with_sticky_add=sum(1 for i in F8 if sk[i]), sticky_added_total=sum(len(sk[i]) for i in F8),
            sticky_added_chunk_is_gold=sum(1 for i in F8 for c in sk[i] if any(k["chunkId"] == c and norm(items[i]["gold"]["quote"]) in norm(k["title"] + " " + k["body"]) for k in R[i]["keptFull"])),
            prev_turn_kept_had_gold=sum(carried_gold.values()), prev_gold_and_f8_kept=sum(1 for i in F8 if carried_gold[i] and kept[i]),
            prev_gold_not_kept_f8=[i for i in F8 if carried_gold[i] and not kept[i]],
            mean_kept=statistics.mean(nk.values()), base_mean_kept=statistics.mean(bnk.values()),
            junk_fixed=junk_fixed(nk), base_junk_fixed=junk_fixed(bnk), junk_fixed_ratio=junk_fixed(nk) / junk_fixed(bnk),
            junk_arm=junk_arm(kept, nk), base_junk_arm=junk_arm(bk, bnk), junk_arm_ratio=junk_arm(kept, nk) / junk_arm(bk, bnk),
            kept_tokens=statistics.mean(sum(tok(c) for c in R[i]["keptFull"]) for i in F8), base_kept_tokens=statistics.mean(sum(tok(c) for c in base[i]["keptFull"]) for i in F8),
            kept_ids_changed=sum(1 for i in F8 if [c["chunkId"] for c in R[i]["keptFull"]] != [c["chunkId"] for c in base[i]["keptFull"]]),
            base_displaced_items=sum(1 for i in F8 if not {c["chunkId"] for c in base[i]["keptFull"]} <= {c["chunkId"] for c in R[i]["keptFull"]}),
            wall_ms_mean=statistics.mean(R[i]["wallMs"] for i in F8), base_wall_ms_mean=statistics.mean(base[i]["wallMs"] for i in F8),
            per_pack={p: [sum(kept[i] for i in F8 if items[i]["pack"] == p), sum(bk[i] for i in F8 if items[i]["pack"] == p)] for p in sorted({items[i]["pack"] for i in F8})})
    res["f0_kept_gold"] = sum(f0kept.values()); res["f8_gold_in_wide12_base"] = sum(wide.values())
    return res
# ---------------------------------------------------------------- LONGSESSION
def longsession(arms):
    qs = {d["id"]: d for d in rd("<workspace>/boar-eval/bench/slices/longsession-v1/questions.jsonl")}
    base = load("longsession.off"); T25 = sorted(i for i in base if int(i.split("-t")[1]) >= 2)
    res = {"n": len(T25), "followups": sum(qs[i]["followup"] for i in T25), "arms": {}}
    def reach(r, i):
        refs = [x.lower() for x in qs[i].get("referent", [])]
        txt = " ".join((c["title"] + " " + c["body"]).lower() for c in r["keptFull"]); return int(bool(refs) and any(x in txt for x in refs))
    FU = [i for i in T25 if qs[i]["followup"]]
    for a in arms:
        R = load(a)
        if not R: continue
        sk = {i: sticky_ids(R[i]) for i in T25}
        nk = {i: len(R[i]["keptFull"]) for i in T25}; bnk = {i: len(base[i]["keptFull"]) for i in T25}
        rc = {i: reach(R[i], i) for i in FU}; brc = {i: reach(base[i], i) for i in FU}
        res["arms"][a] = dict(referent_reach=sum(rc.values()), base_referent_reach=sum(brc.values()), n_followups=len(FU),
            reach_gained=[i for i in FU if rc[i] > brc[i]], reach_lost=[i for i in FU if rc[i] < brc[i]],
            items_with_sticky_add=[i for i in T25 if sk[i]], sticky_added_total=sum(len(sk[i]) for i in T25),
            kept_ids_changed=sum(1 for i in T25 if [c["chunkId"] for c in R[i]["keptFull"]] != [c["chunkId"] for c in base[i]["keptFull"]]),
            base_displaced_items=sum(1 for i in T25 if not {c["chunkId"] for c in base[i]["keptFull"]} <= {c["chunkId"] for c in R[i]["keptFull"]}),
            mean_kept=statistics.mean(nk.values()), base_mean_kept=statistics.mean(bnk.values()),
            kept_tokens=statistics.mean(sum(tok(c) for c in R[i]["keptFull"]) for i in T25), base_kept_tokens=statistics.mean(sum(tok(c) for c in base[i]["keptFull"]) for i in T25),
            junk_arm=statistics.mean(nk[i] for i in T25 if not (rc.get(i) or 0)), base_junk_arm=statistics.mean(bnk[i] for i in T25 if not (brc.get(i) or 0)),
            junk_selfcontained=statistics.mean(nk[i] for i in T25 if not qs[i]["followup"]), base_junk_selfcontained=statistics.mean(bnk[i] for i in T25 if not qs[i]["followup"]),
            sticky_adds_on_selfcontained=sum(len(sk[i]) for i in T25 if not qs[i]["followup"]), sticky_adds_on_followups=sum(len(sk[i]) for i in T25 if qs[i]["followup"]),
            empty_base_now_nonempty=[i for i in T25 if not bnk[i] and nk[i]],
            added_detail={i: [(c["title"][:60]) for c in R[i]["keptFull"] if c["chunkId"] in sk[i]] for i in T25 if sk[i]})
    return res
def identity():
    res = {"pairs": 0, "kept_identical": 0, "codes_identical": 0, "raw_identical": 0, "diffs": []}
    for st, ids in (("qform", "q"), ("longsession", "l")):
        h = load(f"{st}.h4"); b = load(f"{st}.off") or load(f"{st}.off")
        if not h: continue
        for i in h:
            res["pairs"] += 1; r = b[i]
            k = [c["chunkId"] for c in h[i]["keptFull"]] == [c["chunkId"] for c in r["keptFull"]] and [c["body"] for c in h[i]["keptFull"]] == [c["body"] for c in r["keptFull"]]
            cd = h[i]["reasonCodes"] == r["reasonCodes"]; rw = [c["chunkId"] for c in h[i]["rawFull"]] == [c["chunkId"] for c in r["rawFull"]]
            res["kept_identical"] += k; res["codes_identical"] += cd; res["raw_identical"] += rw
            if not (k and cd and rw): res["diffs"].append(i)
    return res
if __name__ == "__main__":
    arms = {"qform": ["qform.s1", "qform.s2"], "longsession": ["longsession.s1", "longsession.s2"]}
    if os.path.exists(f"{D}/replays/qform.off.jsonl"): out["qform"] = qform(arms["qform"])
    if os.path.exists(f"{D}/replays/longsession.off.jsonl"): out["longsession"] = longsession(arms["longsession"])
    out["identity"] = identity()
    json.dump(out, open(D + "/r5.json", "w"), indent=1)
    print(json.dumps({k: {a: {x: y for x, y in v.items() if x not in ("added_detail", "gained", "lost", "prev_gold_not_kept_f8", "per_pack", "items_with_sticky_add", "reach_gained")} for a, v in r["arms"].items()} for k, r in out.items() if "arms" in r}, indent=0))
