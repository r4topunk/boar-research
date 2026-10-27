"""R5 chain files (0 LLM). python3 -I tools/build_chains.py
qform.chain.jsonl: per fact, the F0 item (no history) then its F8 fragment with prevId = the F0 id and history = [user F0 question, assistant K1 answer text from
  arms/qform/gen/traces where it exists]. longsession.chain.jsonl: the 50 turns 1-5 of LONGSESSION (ls-session-s42 requests: history = questions + the engine's own
  earlier answers), prevId = the previous turn of the same session."""
import json, glob, os
A = "<workspace>/rnd/research/coordinator/arms"; D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ans = {}
for f in sorted(glob.glob(A + "/qform/gen/traces/qform-gen*.traces.jsonl")):
    for l in open(f):
        t = json.loads(l); a = (t.get("answer") or {}).get("text")
        if a: ans[t["itemId"]] = a
qs = {q["id"]: q for q in map(json.loads, open(A + "/qform/items/qform.questions.jsonl"))}
out = []; noans = 0
for fid in sorted({q["fact_id"] for q in qs.values()}):
    f0, f8 = qs[fid + "-F0"], qs[fid + "-F8"]
    turns = [{"role": "user", "text": f0["question"]}]
    if f0["id"] in ans: turns.append({"role": "assistant", "text": ans[f0["id"]]})
    else: noans += 1
    out.append({"id": f0["id"], "question": f0["question"]})
    out.append({"id": f8["id"], "question": f8["question"], "prevId": f0["id"], "history": {"turns": turns}})
open(D + "/qform.chain.jsonl", "w").write("".join(json.dumps(o) + "\n" for o in out)); print("qform", len(out), "F0 without answer text", noans)
req = [json.loads(l)["item"] for l in open(A + "/longsession/runs/ls-session-s42.requests.jsonl")]
req.sort(key=lambda it: (it["id"].split("-t")[0], int(it["id"].split("-t")[1])))
out = []
for it in req:
    s, t = it["id"].split("-t"); o = {"id": it["id"], "question": it["question"]}
    if int(t) > 1: o["prevId"] = f"{s}-t{int(t) - 1}"
    if it.get("history"): o["history"] = it["history"]
    out.append(o)
open(D + "/longsession.chain.jsonl", "w").write("".join(json.dumps(o) + "\n" for o in out)); print("longsession", len(out))
