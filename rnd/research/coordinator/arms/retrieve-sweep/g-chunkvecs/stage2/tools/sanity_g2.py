"""python3 -I sanity_g2.py : sanity + replay identity + changed-context set for the two generation runs (0 LLM). Writes stage2/sanity.json and stage2/changed.ids.
Rows/empty/errors/loops as arms/qform/gen/tools/sanity_qform.py. Kept-list identity vs the replay (ctl3.jsonl for ctl, dense2-true.jsonl for arm): the traces carry no chunk
ids, so identity = the (title, section, source) sequence of retrieval.kept (the QFORM secondary's test) plus, as a stronger proxy, the context:a->b reasonCode.
Changed-context item = ANY of: run kept sequences differ between ctl and arm; replay chunk-id lists (ctl3 vs dense2-true) differ; promptTokens differ between the two runs."""
import json, collections, os
S2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); G = os.path.dirname(S2)
ids = [json.loads(l)["id"] for l in open(f"{G}/q3.jsonl") if l.strip()]
T = {w: {} for w in ("ctl", "arm")}
for w in T:
    for l in open(f"{S2}/traces/g2-{w}.traces.jsonl"):
        t = json.loads(l); T[w][t["itemId"]] = t
REP = {"ctl": "ctl3", "arm": "dense2-true"}
rep = {w: {json.loads(l)["id"]: json.loads(l) for l in open(f"{G}/{REP[w]}.jsonl")} for w in T}
def loop(txt):
    w = txt.split(); c = collections.Counter(tuple(w[i:i+6]) for i in range(len(w) - 5)); return any(v >= 3 for v in c.values())
seq = lambda t: [(c["title"], c.get("section"), c.get("source")) for c in t["retrieval"]["kept"]]
rseq = lambda r: [(c["title"], None, None) for c in r["keptFull"]]
ctxcode = lambda codes: next((c for c in codes if c.startswith("context:")), None)
out = {}
for w in T:
    t_, r_ = T[w], rep[w]
    missing = [i for i in ids if i not in t_]
    errs = [i for i in ids if i in t_ and t_[i].get("error")]
    empty = [i for i in ids if i in t_ and not (t_[i]["answer"]["text"] or "").strip()]
    loops = [i for i in ids if i in t_ and loop(t_[i]["answer"]["text"] or "")]
    same = []; diffs = {}
    for i in ids:
        if i not in t_: continue
        a = [x[0] for x in seq(t_[i])]; b = [c["title"] for c in r_[i]["keptFull"]]
        (same.append(i) if a == b else diffs.update({i: dict(run=a, replay=b)}))
    rawsame = sum([c["title"] for c in t_[i]["retrieval"]["raw"]] == [c["title"] for c in r_[i]["rawFull"]] for i in ids if i in t_)
    tasks = sum(t_[i]["route"]["task"] == r_[i]["task"] for i in ids if i in t_)
    ctxsame = sum(ctxcode(t_[i]["route"]["reasonCodes"]) == ctxcode(r_[i]["reasonCodes"]) for i in ids if i in t_)
    empty_kept_run = [i for i in diffs if not diffs[i]["run"]]
    out[w] = dict(rows=len(t_), expected=len(ids), missing=missing, errors=errs, empty=empty, loops=loops, kept_identical=len(same), kept_share=len(same) / len(ids),
                  raw_identical=rawsame, task_equal=tasks, context_code_equal=ctxsame, diffs=diffs, diff_run_kept_empty=empty_kept_run)
# changed-context set
chg = []; why = {}
for i in ids:
    r = []
    if seq(T["ctl"][i]) != seq(T["arm"][i]): r.append("run-kept")
    if [c["chunkId"] for c in rep["ctl"][i]["keptFull"]] != [c["chunkId"] for c in rep["arm"][i]["keptFull"]]: r.append("replay-chunks")
    if T["ctl"][i]["timing"].get("promptTokens") != T["arm"][i]["timing"].get("promptTokens"): r.append("promptTokens")
    if r: chg.append(i); why[i] = r
cnt = collections.Counter(x for v in why.values() for x in v)
same_txt = sum(T["ctl"][i]["answer"]["text"] == T["arm"][i]["answer"]["text"] for i in ids if i not in why)
out["changed"] = dict(n=len(chg), by_reason=dict(cnt), unchanged=len(ids) - len(chg), unchanged_identical_text=same_txt, why=why)
json.dump(out, open(f"{S2}/sanity.json", "w"), indent=1)
open(f"{S2}/changed.ids", "w").write("\n".join(chg) + "\n")
for w in ("ctl", "arm"):
    o = out[w]; print(w, {k: (len(v) if isinstance(v, (list, dict)) else v) for k, v in o.items()})
print("changed", len(chg), dict(cnt), "unchanged", len(ids) - len(chg), "of which identical text", same_txt)
