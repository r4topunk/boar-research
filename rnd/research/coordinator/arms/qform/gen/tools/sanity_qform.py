"""python3 -I sanity_qform.py  : merge gen/traces/qform-gen-{a,b} into gen/traces/qform-gen.traces.jsonl (all192.ids order) and run the sanity + replay-identity checks (0 LLM)."""
import json, collections, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
G = f"{ROOT}/gen"
T = {}
for s in "ab":
    for l in open(f"{G}/traces/qform-gen-{s}.traces.jsonl"):
        t = json.loads(l); T[t["itemId"]] = t
ids = open(f"{G}/req/all192.ids").read().split()
missing = [i for i in ids if i not in T]
with open(f"{G}/traces/qform-gen.traces.jsonl", "w") as f:
    for i in ids:
        if i in T: f.write(json.dumps(T[i], ensure_ascii=False) + "\n")
rep = {}
for l in open(f"{ROOT}/replay/qform.replay.jsonl"):
    d = json.loads(l); rep[d["id"]] = d
def loop(txt):
    w = txt.split(); c = collections.Counter(tuple(w[i:i+6]) for i in range(len(w) - 5)); return any(v >= 3 for v in c.values())
errs = [i for i in ids if i in T and T[i].get("error")]
empty = [i for i in ids if i in T and not (T[i]["answer"]["text"] or "").strip()]
loops = [i for i in ids if i in T and loop(T[i]["answer"]["text"] or "")]
same, diffs, rawsame, tasksame = 0, [], 0, 0
for i in ids:
    t, r = T[i], rep[i]
    a = [c["title"] for c in t["retrieval"]["kept"]]; b = [c["title"] for c in r["keptFull"]]
    ok = a == b; same += ok
    if not ok: diffs.append((i, a, b))
    rawsame += [c["title"] for c in t["retrieval"]["raw"]] == [c["title"] for c in r["rawFull"]]
    tasksame += t["route"]["task"] == r["task"]
out = dict(rows=len(T), expected=len(ids), missing=missing, errors=errs, empty=empty, loops=loops, kept_identical=same, kept_share=same / len(ids),
           raw_identical=rawsame, task_equal=tasksame, diffs=[d[0] for d in diffs])
json.dump(out, open(f"{G}/sanity.json", "w"), indent=1)
print({k: v for k, v in out.items() if k != "diffs"}); print("DIFF ids:", out["diffs"])
for d in diffs[:6]: print(d)
