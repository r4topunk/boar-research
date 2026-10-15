"""LONGSESSION request maker (0 LLM calls). Config (commit, modelId, settings, kit + shas, device, seed 42) copied from the first row of
arms/stack/runs/v01-cut7-stack-off-s42.requests.jsonl, with config.arm = "cut7" (the plain cut 7 tree runner-local/be-0cfd4a77-cut7).
  standalone: python3 -I mkreq_ls.py standalone <questions.jsonl> <runId> <out.requests> [session,...]
      -> one request per item, no history.
  session:    python3 -I mkreq_ls.py session <questions.jsonl> <runId> <out.requests> <turn k> <prev traces.jsonl or -> [session,...]
      -> one request per session for turn k; item.history.turns = turns 1..k-1 of that session: user = the question text,
         assistant = the engine's own answer.text from <prev traces> (all earlier waves concatenated). Aborts if an earlier answer is missing/errored."""
import json, sys
SRC = "$BOAR_WS/rnd/research/coordinator/arms/stack/runs/v01-cut7-stack-off-s42.requests.jsonl"
base = json.loads(open(SRC).readline()); cfg = dict(base["config"]); cfg["arm"] = "cut7"
mode, qp, run, out = sys.argv[1:5]
Q = [json.loads(l) for l in open(qp) if l.strip()]
def req(item): return {"protocol": base["protocol"], "runId": run, "item": item, "config": cfg, "seed": base["seed"]}
rows = []
if mode == "standalone":
    keep = set(sys.argv[5].split(",")) if len(sys.argv) > 5 else None
    for q in Q:
        if keep and q["session"] not in keep: continue
        if not (int(__import__("os").environ.get("MIN_TURN", "1")) <= q["turn"] <= int(__import__("os").environ.get("MAX_TURN", "99"))): continue
        rows.append(req({"id": q["id"], "question": q["question"], "lang": "en"}))
else:
    k = int(sys.argv[5]); prev = sys.argv[6]; keep = set(sys.argv[7].split(",")) if len(sys.argv) > 7 else None
    ans = {}
    if prev != "-":
        for l in open(prev):
            if not l.strip(): continue
            t = json.loads(l)
            if t.get("error") or not (t.get("answer") or {}).get("text", "").strip(): continue
            ans[t["itemId"]] = t["answer"]["text"]
    by = {(q["session"], q["turn"]): q for q in Q}
    for s in sorted({q["session"] for q in Q}):  # (MIN_TURN/MAX_TURN env filter standalone items; session mode skips sessions without turn k)
        if keep and s not in keep: continue
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
