"""rerun check (0 LLM): kept-list identity first pass vs warm rerun, and the rerun's walls. Adds 'rerun' to compose.json. python3 -I tools/rerun_check.py"""
import json, os, statistics
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = json.load(open(D + "/compose.json")); out = {}
rd = lambda f: {json.loads(l)["id"]: json.loads(l) for l in open(f) if l.strip()}
keys = set(json.load(open(D + "/kfull.json"))["items"])
for lab in J["labels"]:
    n, v = lab[1:].split("."); f1 = D + f"/replays/main.N{n}.{v}.jsonl"; f2 = D + f"/replays/rerun/main.N{n}.{v}.jsonl"
    if not os.path.exists(f2) or sum(1 for _ in open(f2)) < 97: continue
    a, b = rd(f1), rd(f2); ids = sorted(keys)
    w = [b[i]["wallMs"] for i in ids if b[i].get("wallMs") is not None]; w1 = [a[i]["wallMs"] for i in ids if a[i].get("wallMs") is not None]
    out[lab] = dict(identical_kept_lists=sum([c["chunkId"] for c in a[i]["keptFull"]] == [c["chunkId"] for c in b[i]["keptFull"]] for i in a), of=len(a),
                    wall_ms_mean_pass1=statistics.mean(w1), wall_ms_mean_rerun=statistics.mean(w), wall_ms_p50_rerun=statistics.median(w))
J["rerun"] = out; json.dump(J, open(D + "/compose.json", "w"), indent=1)
for k, v in out.items(): print(k, v["identical_kept_lists"], "/", v["of"], round(v["wall_ms_mean_pass1"]), round(v["wall_ms_mean_rerun"]), round(v["wall_ms_p50_rerun"]))
