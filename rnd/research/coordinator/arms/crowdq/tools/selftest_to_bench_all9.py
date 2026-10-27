#!/usr/bin/env python3
"""CROWDQ (criterion sha 71603c60…): copy of arms/packs/tools/selftest_to_bench.py for arm P (all 9 published packs installed as peers).
Usage: python3 -I selftest_to_bench_all9.py <pack> [--seed 42]
  config.kit = claim kit (boar-crypto, boar-wikivoyage-en) + ALL 9 published packs (ids + sha256 from shared-data/packs/{wave2,wave1}/<id>.sqlite.json, wave2 first).
  runId st-<pack>-cut7-all9-s<seed>; out arms/crowdq/runs/<runId>.requests.jsonl.
  Bench dir boar-eval/bench/selftest/<pack>/ is NOT rewritten: the would-be questions/refs bytes are built in memory and their sha256
  compared with the existing files (assert equal)."""
import hashlib, json, sys, os
B = "<workspace>"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
a = sys.argv[1:]; pack = a[0]; assert pack in PACKS
seed = int(a[a.index("--seed") + 1]) if "--seed" in a else 42
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
shab = lambda b: hashlib.sha256(b).hexdigest()
items = [json.loads(l) for l in open(f"{B}/rnd/research/packs/selftest/{pack}.jsonl") if l.strip()]
assert len(items) == 20 and len({i["id"] for i in items}) == 20, "expected 20 unique items"
bd = f"{B}/boar-eval/bench/selftest/{pack}"
qs = [{"id": i["id"], "category": i["category"], "question": i["question"], "lang": "en", "danger": False, "rubric": i["rubric"],
       "origin": "pack-selftest (agent-written, public, dev)", "provenance": f"rnd/research/packs/selftest/{pack}.jsonl",
       "selftest": {"pack": i["pack"], "style": i.get("style"), "in_pack_facts": i["in_pack_facts"], "source": i["source"]}} for i in items]
refs = [{"id": i["id"], "category": i["category"], "lang": "en", "question": i["question"], "ok": True, "answer": i["answer"],
         "sources": [i["source"]["url"]], "modelId": "selftest-gold (agent-written)", "promptVersion": "selftest.v1"} for i in items]
enc = lambda rows: "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows).encode("utf-8")
assert shab(enc(qs)) == sha(f"{bd}/questions.jsonl"), f"bench questions differ for {pack}"
assert shab(enc(refs)) == sha(f"{bd}/refs/refs.jsonl"), f"bench refs differ for {pack}"
cfg = json.load(open(f"{B}/rnd/research/coordinator/repro/claim-config-cut7.json")); cfg.pop("seed", None)
assert [k["id"] for k in cfg["kit"]] == ["boar-crypto", "boar-wikivoyage-en"], cfg["kit"]
for p in PACKS:
    pd = next(d for d in (f"{B}/shared-data/packs/wave2", f"{B}/shared-data/packs/wave1") if os.path.exists(f"{d}/{p}.sqlite.json"))  # wave2 first, then wave1
    cfg["kit"].append({"id": p, "sha256": json.load(open(f"{pd}/{p}.sqlite.json"))["sha256"]})
run = f"st-{pack}-cut7-all9-s{seed}"
rq = [{"protocol": "1.0.0", "runId": run, "item": {"id": i["id"], "question": i["question"], "lang": "en"}, "config": cfg, "seed": seed} for i in items]
od = f"{B}/rnd/research/coordinator/arms/crowdq/runs"; os.makedirs(od, exist_ok=True); rp = f"{od}/{run}.requests.jsonl"
open(rp, "w").write(enc(rq).decode("utf-8"))
print(f"bench {bd} unchanged (questions {sha(bd + '/questions.jsonl')[:12]}, refs {sha(bd + '/refs/refs.jsonl')[:12]})\nrequests {rp} ({len(rq)} items, kit {len(cfg['kit'])}: {[k['id'] for k in cfg['kit']]})")
