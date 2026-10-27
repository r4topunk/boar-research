import json, sys
sys.argv = ["x"]
exec(open("<workspace>/rnd/research/sonar/tools/key_in_context.py").read().split('if __name__ == "__main__":')[0])
R = "<workspace>/boar-eval/runs/night-2026-10-01/"
qs = {json.loads(l)["id"]: json.loads(l) for l in open("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl")}
res = Resolver(True); out = {}
for run in ["ios-main-v5-t0", "ios-main-s42"]:
    for l in open(R + run + ".traces.jsonl"):
        t = json.loads(l); q = qs.get(t["itemId"])
        if not q or not (q["grading"].get("must_any") or q["grading"].get("must_k")): continue
        for s in t["retrieval"]["raw"]:
            tx = res.text(s)
            if tx is not None: out[f"{t['itemId']}|{s['title']}"] = key_hit(tx, q["grading"])
print(json.dumps(out))
