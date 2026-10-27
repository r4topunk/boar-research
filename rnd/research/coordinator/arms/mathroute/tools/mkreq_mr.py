"""MATHROUTE request maker (0 LLM calls). Config copied from arms/stack/runs/v01-cut7-stack-off-s42.requests.jsonl (as LONGSESSION's
mkreq_ls.py: quickFirst true, alwaysComplete false, claim kit boar-crypto + boar-wikivoyage-en, seed 42), config.arm = <arm label>.
Usage: python3 -I mkreq_mr.py <questions.jsonl> <runId> <config.arm> <out.requests.jsonl> [id,id,...]"""
import json, sys
SRC = "<workspace>/rnd/research/coordinator/arms/stack/runs/v01-cut7-stack-off-s42.requests.jsonl"
base = json.loads(open(SRC).readline()); cfg = dict(base["config"])
qp, run, arm, out = sys.argv[1:5]; cfg["arm"] = arm
keep = set(sys.argv[5].split(",")) if len(sys.argv) > 5 else None
rows = [{"protocol": base["protocol"], "runId": run, "item": {"id": q["id"], "question": q["question"], "lang": "en"}, "config": cfg, "seed": base["seed"]}
        for q in map(json.loads, open(qp)) if not keep or q["id"] in keep]
open(out, "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)); print(f"{out}: {len(rows)} requests")
