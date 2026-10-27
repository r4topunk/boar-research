"""HEALTHGAP-r2 request maker (0 LLM; public / agent-written inputs only) = tools/mkreq_hg.py (claim config from
arms/bonsai2/runs/b2-smoke-C-v01.requests.jsonl, config.arm = <arm>) with the rule v1.2 sets:
  probes = the 64 Q2 probes; v01 = the 60 public v0.1; st = the 180 self-tests of the 9 published packs (C12: qa-bitcoin-se and
  qa-ethereum-se left out); mlp = the 20 boar-medlineplus-en self-tests; r2 = the reviewer's 30 new probes (review/r2-probes.json)
  + the ES split follow-up "¿Cuánto paracetamol puedo tomar?" + "¿y para un niño de 20 kg?" (mt-es-para);
  gen = the 15 HEALTHGAP items (13 gap + n12, vit-hlt-003) + the follow-up forms p25 p26 p29 mt-es-para + the 10 frozen
  non-health v0.1 controls (rule v1.1 §5d); genmlp = st-boar-medlineplus-en-003 (vitamin D).
Kit: the claim kit, or a JSON list of {id, sha256} (mlp/genmlp: claim + boar-medlineplus-en; r2: + boar-firstaid-en, as the reviewer).
Usage: python3 -I mkreq_hg2.py <set> <runId> <arm> <out.requests.jsonl> [kit.json]"""
import json, re, sys, glob
R = "<workspace>"; A = f"{R}/rnd/research/coordinator/arms"; H = f"{A}/healthgap"; V1 = f"{R}/boar-eval/bench/v0.1/questions.public.jsonl"
GAP15 = "h01 h02 h08 h10 h15 h19 h21 h23 h24 h27 h28 n03 n06 n12 vit-hlt-003".split()
CONTROLS = "food-002 lan-cmp-004 lan-cmp-005 lan-exp-001 lan-exp-007 lan-ref-001 lan-ref-003 vit-cry-006 vit-hum-001 vit-sci-002".split()
FORMS = "p25 p26 p29 mt-es-para".split()
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
sts = [item(q) for d in sorted(glob.glob(f"{R}/boar-eval/bench/selftest/*/questions.jsonl")) if d.split("/")[-2] not in ("qa-bitcoin-se", "qa-ethereum-se") for q in jl(d)]
mlp = [item(q) for q in jl(f"{R}/boar-eval/bench/selftest/boar-medlineplus-en/questions.jsonl")]
r2 = [item({"id": i, "question": q, "turns": t}) for i, q, t, _e, _n in json.load(open(f"{H}/review/r2-probes.json"))]
r2.append(item({"id": "mt-es-para", "question": "¿y para un niño de 20 kg?", "turns": ["¿Cuánto paracetamol puedo tomar?"]}))
pool = {i["id"]: i for i in probes + v01 + r2}
items = {"probes": probes, "v01": v01, "st": sts, "mlp": mlp, "r2": r2, "gen": [pool[i] for i in GAP15 + FORMS + CONTROLS],
         "genmlp": [i for i in mlp if i["id"] == "st-boar-medlineplus-en-003"]}[st]
assert st != "st" or len(items) == 180, len(items)
rows = [{"protocol": base["protocol"], "runId": run, "item": it, "config": cfg, "seed": base["seed"]} for it in items]
assert len({r["item"]["id"] for r in rows}) == len(rows)
open(out, "w").write("".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in rows))
print(f"{out}: {len(rows)} requests ({sum('history' in r['item'] for r in rows)} with history)")
