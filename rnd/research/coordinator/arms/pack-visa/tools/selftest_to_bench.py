#!/usr/bin/env python3
"""T-K4c: pack self-test jsonl -> (1) a judge.mjs bench dir, (2) adapter requests (claim kit + the pack).
Usage: python3 -I selftest_to_bench.py <pack> [--seed 42] [--no-pack] [--run-id ID]
  in : rnd/research/packs/selftest/<pack>.jsonl, shared-data/packs/{wave2,wave1}/<pack>.sqlite(.json: sha256) (wave2 first),
       rnd/research/coordinator/repro/claim-config-cut7.json (claim config: commit, arm, model, settings, kit, device)
  out: boar-eval/bench/selftest/<pack>/{bench.json, questions.jsonl, refs/refs.jsonl, refs/MANIFEST.json}
       rnd/research/coordinator/arms/pack-visa/selftest-runs/<runId>.requests.jsonl  (runId = st-<pack>-cut7[-nopack]-s<seed>)
Field mapping (self-test item -> bench question / reference / request item):
  id -> id (all three) | question -> question (all three) | category -> category (question, ref) | "en" -> lang
  rubric (list, incl. the "Penalize:" bullet) -> question.rubric (judge.mjs joins it with " / " as the item notes)
  answer (gold) -> refs.answer with ok=true (the judge's reference side) | style, in_pack_facts, source -> question.selftest{} (not read by the judge)
  request.config = claim config with kit + {id: <pack>, sha256} (unless --no-pack); request.seed = --seed; item = {id, question, lang}.
"""
import hashlib, json, sys, os
B = "<workspace>"
a = sys.argv[1:]; pack = a[0]
seed = int(a[a.index("--seed") + 1]) if "--seed" in a else 42
nopack = "--no-pack" in a
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
items = [json.loads(l) for l in open(f"{B}/rnd/research/coordinator/arms/pack-visa/selftest/{pack}.jsonl") if l.strip()]
assert len(items) == 20 and len({i["id"] for i in items}) == 20, "expected 20 unique items"
bd = f"{B}/boar-eval/bench/selftest/{pack}"; os.makedirs(f"{bd}/refs", exist_ok=True)
qs = [{"id": i["id"], "category": i["category"], "question": i["question"], "lang": "en", "danger": False, "rubric": i["rubric"],
       "origin": "pack-selftest (agent-written, public, dev)", "provenance": f"rnd/research/coordinator/arms/pack-visa/selftest/{pack}.jsonl",
       "selftest": {"pack": i["pack"], "style": i.get("style"), "in_pack_facts": i["in_pack_facts"], "source": i["source"]}} for i in items]
refs = [{"id": i["id"], "category": i["category"], "lang": "en", "question": i["question"], "ok": True, "answer": i["answer"],
         "sources": [i["source"]["url"]], "modelId": "selftest-gold (agent-written)", "promptVersion": "selftest.v1"} for i in items]
w = lambda p, rows: open(p, "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
w(f"{bd}/questions.jsonl", qs); w(f"{bd}/refs/refs.jsonl", refs)
json.dump({"bench": f"selftest-{pack}", "questions": "questions.jsonl", "refs": "refs/refs.jsonl",
           "_note": "public pack self-test (T-K4b), agent-written gold answers as the reference side; dev only, never pooled with bench/claim rows"},
          open(f"{bd}/bench.json", "w"), indent=1)
json.dump({"bench": f"selftest-{pack}", "frozen": True, "n_items": 20, "n_ok": 20, "source_sha256": sha(f"{B}/rnd/research/coordinator/arms/pack-visa/selftest/{pack}.jsonl"),
           "questions_sha256": sha(f"{bd}/questions.jsonl"), "jsonl_sha256": sha(f"{bd}/refs/refs.jsonl")}, open(f"{bd}/refs/MANIFEST.json", "w"), indent=1)
cfg = json.load(open(f"{B}/rnd/research/coordinator/repro/claim-config-cut7.json")); cfg.pop("seed", None)
if not nopack:
    pd = next(d for d in (f"{B}/shared-data/packs/wave4", f"{B}/shared-data/packs/wave3", f"{B}/shared-data/packs/wave2", f"{B}/shared-data/packs/wave1") if os.path.exists(f"{d}/{pack}.sqlite.json"))  # wave3, then wave2, then wave1
    meta = json.load(open(f"{pd}/{pack}.sqlite.json"))
    cfg["kit"] = cfg["kit"] + [{"id": pack, "sha256": meta["sha256"]}]
run = (a[a.index("--run-id") + 1] if "--run-id" in a else f"st-{pack}-cut7{'-nopack' if nopack else ''}-s{seed}")
rq = [{"protocol": "1.0.0", "runId": run, "item": {"id": i["id"], "question": i["question"], "lang": "en"}, "config": cfg, "seed": seed} for i in items]
rp = f"{B}/rnd/research/coordinator/arms/pack-visa/selftest-runs/{run}.requests.jsonl"; w(rp, rq)
print(f"bench {bd} (questions {sha(bd + '/questions.jsonl')[:12]}, refs {sha(bd + '/refs/refs.jsonl')[:12]})\nrequests {rp} ({len(rq)} items, kit {[k['id'] for k in cfg['kit']]})")
