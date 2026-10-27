"""DRIFT17 request maker (0 LLM calls) = arms/longsession/tools/mkreq_ls.py with the config source swapped to the LITEPACKS K0 lite config
(cfg.json = protocol/config/seed of arms/litepacks/runs/req/lp-K0-v01-s42.requests.jsonl row 1). History construction unchanged.
  standalone: python3 -I mkreq_d17.py <cfg.json> standalone <questions.jsonl> <runId> <out>
  session:    python3 -I mkreq_d17.py <cfg.json> session <questions.jsonl> <runId> <out> <turn k> <prev traces.jsonl or ->"""
import json, sys
cp, mode, qp, run, out = sys.argv[1:6]
base = json.load(open(cp)); cfg = base["config"]
Q = [json.loads(l) for l in open(qp) if l.strip()]
def req(item): return {"protocol": base["protocol"], "runId": run, "item": item, "config": cfg, "seed": base["seed"]}
rows = []
if mode == "standalone":
    rows = [req({"id": q["id"], "question": q["question"], "lang": "en"}) for q in Q]
else:
    k = int(sys.argv[6]); prev = sys.argv[7]; ans = {}
    if prev != "-":
        for l in open(prev):
            if not l.strip(): continue
            t = json.loads(l)
            if t.get("error") or not (t.get("answer") or {}).get("text", "").strip(): continue
            ans[t["itemId"]] = t["answer"]["text"]
    by = {(q["session"], q["turn"]): q for q in Q}
    for s in sorted({q["session"] for q in Q}):
        if (s, k) not in by: continue
        turns = []
        for j in range(1, k):
            pj = by[(s, j)]
            if pj["id"] not in ans: sys.exit(f"missing earlier answer {pj['id']} in {prev}")
            turns += [{"role": "user", "text": pj["question"]}, {"role": "assistant", "text": ans[pj["id"]]}]
        q = by[(s, k)]; item = {"id": q["id"], "question": q["question"], "lang": "en"}
        if turns: item["history"] = {"turns": turns}
        rows.append(req(item))
open(out, "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
print(f"{mode} {out}: {len(rows)} requests")
