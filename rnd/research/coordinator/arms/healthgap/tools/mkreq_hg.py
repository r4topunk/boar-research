"""HEALTHGAP request maker (0 LLM calls; public/agent-written inputs only). Config = the first row of
arms/bonsai2/runs/b2-smoke-C-v01.requests.jsonl (cut 7 claim config: kit boar-crypto + boar-wikivoyage-en, quickFirst true,
alwaysComplete false, seed 42, qwen3-4b-instruct-2507-q4km) with config.arm = <arm> (the tree's ARM file).
Sets: probes = the 64 Q2 probes (numguard/review/*.jsonl + v0.1 dng-001/002/005, vit-hlt-001/002/003; multi-turn ones carry
item.history.turns = their earlier user turns, as mkreq_q2.py); v01 = the 60 public v0.1; st = the 220 self-tests (11 packs);
gen = the 15 HEALTHGAP items + the 10 frozen controls (rule v1.1 §5d). Optional kit override: a JSON list of {id, sha256}.
Usage: python3 -I mkreq_hg.py <set> <runId> <arm> <out.requests.jsonl> [kit.json]"""
import json, re, sys, glob
R = "<workspace>"; A = f"{R}/rnd/research/coordinator/arms"; V1 = f"{R}/boar-eval/bench/v0.1/questions.public.jsonl"
GAP15 = "h01 h02 h08 h10 h15 h19 h21 h23 h24 h27 h28 n03 n06 n12 vit-hlt-003".split()
CONTROLS = "food-002 lan-cmp-004 lan-cmp-005 lan-exp-001 lan-exp-007 lan-ref-001 lan-ref-003 vit-cry-006 vit-hum-001 vit-sci-002".split()
st, run, arm, out = sys.argv[1:5]
base = json.loads(open(f"{A}/bonsai2/runs/b2-smoke-C-v01.requests.jsonl").readline()); cfg = dict(base["config"]); cfg["arm"] = arm
if len(sys.argv) > 5: cfg["kit"] = json.load(open(sys.argv[5]))
def jl(p): return [json.loads(l) for l in open(p) if l.strip()]
def item(q):
    it = {"id": q["id"], "question": q["question"], "lang": "en"}
    if q.get("turns"): it["history"] = {"turns": [{"role": "user", "text": t} for t in q["turns"]]}
    return it
probes = [item(q) for f in ["health", "multiturn", "final-probes", "final-probes-mt"] for q in jl(f"{A}/numguard/review/{f}.jsonl")]
probes += [item(q) for q in jl(V1) if re.match(r"^(dng-|vit-hlt-)", q["id"])]
v01 = [item(q) for q in jl(V1)]
sts = [item(q) for d in sorted(glob.glob(f"{R}/boar-eval/bench/selftest/*/questions.jsonl")) for q in jl(d)]
pool = {i["id"]: i for i in probes + v01}
items = {"probes": probes, "v01": v01, "st": sts, "gen": [pool[i] for i in GAP15 + CONTROLS]}[st]
rows = [{"protocol": base["protocol"], "runId": run, "item": it, "config": cfg, "seed": base["seed"]} for it in items]
assert len({r["item"]["id"] for r in rows}) == len(rows)
open(out, "w").write("".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in rows))
print(f"{out}: {len(rows)} requests ({sum('history' in r['item'] for r in rows)} with history)")
