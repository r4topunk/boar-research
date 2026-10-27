#!/usr/bin/env python3
"""DENSECHUNK-ST2 stage 1: adapter requests for one self-test pack, packDense2 "extra" on the cut-7 dense2 tree.
Usage: python3 -I st2_requests.py <pack> [--seed 42]
Same items/config as arms/packs/tools/selftest_to_bench.py (claim config cut 7) except: arm "cut7-dense2",
settings {quickFirst: true, alwaysComplete: false, packDense2: "extra"}, and every kit pack (crypto, wikivoyage, <pack>)
pinned to the v3proto sidecar copy's sha256 (shared-data/packs/v3proto/<id>.sqlite.json). Does not rewrite the bench dir
(boar-eval/bench/selftest/<pack>/ from the OFF run is reused as-is).
Out: arms/densechunk-st/runs/gen/st2-<pack>-cut7-s<seed>.requests.jsonl"""
import json, sys
B = "<workspace>"; V = f"{B}/shared-data/packs/v3proto"
a = sys.argv[1:]; pack = a[0]; seed = int(a[a.index("--seed") + 1]) if "--seed" in a else 42
items = [json.loads(l) for l in open(f"{B}/rnd/research/packs/selftest/{pack}.jsonl") if l.strip()]
assert len(items) == 20 and len({i["id"] for i in items}) == 20
cfg = json.load(open(f"{B}/rnd/research/coordinator/repro/claim-config-cut7.json")); cfg.pop("seed", None)
cfg["arm"] = "cut7-dense2"
cfg["settings"] = {"quickFirst": True, "alwaysComplete": False, "packDense2": "extra"}
cfg["kit"] = [{"id": k, "sha256": json.load(open(f"{V}/{k}.sqlite.json"))["sha256"]} for k in [x["id"] for x in cfg["kit"]] + [pack]]
run = f"st2-{pack}-cut7-s{seed}"
rp = f"{B}/rnd/research/coordinator/arms/densechunk-st/runs/gen/{run}.requests.jsonl"
open(rp, "w").write("".join(json.dumps({"protocol": "1.0.0", "runId": run, "item": {"id": i["id"], "question": i["question"], "lang": "en"},
                                        "config": cfg, "seed": seed}, ensure_ascii=False) + "\n" for i in items))
print(f"requests {rp} (20 items, kit {[k['id'] for k in cfg['kit']]})")
