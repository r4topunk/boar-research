"""U5: LONGSESSION OFF plan from the ON replay (criterion rule). python3 -I tools/plan_ls_off.py -> ../u5/ls_off_plan.json; prints one 'pack ids' line per group."""
import json, os, collections
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); B = "<workspace>"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
qs = {d["id"]: d for d in rd(B + "/boar-eval/bench/slices/longsession-v1/questions.jsonl")}
R = {r["id"]: r for r in rd(D + "/replays/longsession.on.jsonl")}
pk = lambda c: c["chunkId"].split(":")[1].removeprefix("local-") if c["chunkId"].startswith("pack:") else None
FU = sorted(i for i in qs if qs[i]["followup"] and 2 <= int(i.split("-t")[1]) <= 5)
pairs, why = {}, {}
for i in FU:
    refs = [x.lower() for x in qs[i]["referent"]]; p = R[i]["prevId"]
    cand = [pk(c) for c in R[p]["keptFull"] if any(x in (c["title"] + " " + c["body"]).lower() for x in refs)]
    cand = [c for c in cand if c]
    if cand:
        cnt = collections.Counter(cand); top = max(cnt.values()); pairs[i] = next(c for c in cand if cnt[c] == top); why[i] = "prev-referent"
    else:
        f = [pk(c) for c in R[i]["keptFull"] if pk(c)]
        pairs[i] = f[0] if f else None; why[i] = "followup-first" if f else "fullkit"
json.dump({"pairs": pairs, "why": why}, open(D + "/ls_off_plan.json", "w"), indent=1)
g = collections.defaultdict(list)
for i, p in pairs.items(): g[p or "fullkit"] += [R[i]["prevId"], i]
order = [r["id"] for r in rd(D + "/replays/longsession.on.jsonl")]
for p, ids in g.items(): print(p, ",".join(sorted(set(ids), key=order.index)))
