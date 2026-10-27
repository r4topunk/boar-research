#!/usr/bin/env python3
"""B3 scoring (0 LLM). Per shard NN: merge pool.NN.json (pool rule on the shard) into coverage-pool.json, run tools/score_kfull.py unchanged
(label B3_NN, kit = K3 + shard), keep per-item stages. Then the union over shards and the verdict by PACK-BUILD-criterion (sha 50186b97).
Usage: python3 -I b3_score.py   (reads b3-fullwiki/{pool,replay}; writes b3-fullwiki/{score,b3.json})"""
import json, os, subprocess, glob, sys
C = "<workspace>/rnd/research/coordinator/arms/coverage-map/"; W = C + "b3-fullwiki/"
K3 = ["boar-crypto", "boar-wikivoyage-en", "boar-simplewiki-en", "boar-factbook", "boar-medlineplus-en", "boar-firstaid-en"]
base = json.load(open(C + "aggregates/coverage-pool.json"))
ORD = {"S1": 0, "S2": 1, "S3": 2, "K": 3}
shards = sorted(os.path.basename(f).split(".")[1] for f in glob.glob(W + "pool/pool.*.json") if os.path.exists(W + f"replay/main.B3_{os.path.basename(f).split('.')[1]}.jsonl"))
if len(sys.argv) > 2: shards = [s for s in shards if s in sys.argv[2].split(",")]
res = {"shards": {}, "items": {}}
for n in shards:
    sid = f"boar-wiki-en-{n}"; pool = json.load(open(W + f"pool/pool.{n}.json"))["items"]
    merged = json.loads(json.dumps(base))
    for i, e in pool.items():
        if sid in e["packs"]: merged["items"][i]["packs"][sid] = e["packs"][sid]
    mf = W + f"score/pool.merged.{n}.json"; json.dump(merged, open(mf, "w"))
    out = W + f"score/B3_{n}.json"
    subprocess.run(["python3", "-I", C + "tools/score_kfull.py", mf, out, f"B3_{n}={W}replay/main.B3_{n}.jsonl={','.join(K3 + [sid])}"], check=True, capture_output=True)
    r = json.load(open(out)); a = r["arms"][f"B3_{n}"]
    res["shards"][n] = dict(MAIN92=a["MAIN92"], v01_52=a["v01_52"], cm40=a["cm40"], mean_kept=round(a["mean_kept"], 2), wall_ms_mean=round(a["wall_ms_mean"]),
                            shard_kept_slots=a["kept_slots_by_pack"].get(sid, 0), total_kept_slots=sum(a["kept_slots_by_pack"].values()),
                            shard_in_pool=sum(1 for i in merged["items"] if sid in merged["items"][i]["packs"]))
    for i, e in r["items"].items():
        x = e[f"B3_{n}"]; d = res["items"].setdefault(i, dict(set=e["set"], tag=e["tag"], funnel_K3=e["funnel_K3"], shards={}))
        d["shards"][n] = dict(stage=x["stage"], inshard=sid in x["inpack"], shard_kept=sid in x["kept_packs"], n_kept=x["n_kept"])
# baseline K3 (mini control, identical to MacBook K3)
b = json.load(open(W + "score/K3mini.json")); bb = b["arms"]["K3mini"]
res["baseline_K3"] = dict(MAIN92=bb["MAIN92"], v01_52=bb["v01_52"], cm40=bb["cm40"])
bst = {i: e["K3mini"]["stage"] for i, e in b["items"].items()}
res["baseline_stage"] = bst
def cnt(ids, f): return sum(1 for i in ids if f(i))
MAIN = list(res["items"]); V01 = [i for i in MAIN if res["items"][i]["set"] == "v0.1"]
U = {}
for i, d in res["items"].items():
    st = [x["stage"] for x in d["shards"].values()]
    d["union_stage"] = max(st, key=lambda s: ORD[s]) if st else "S1"
    d["union_not_S1"] = any(s != "S1" for s in st)       # fact in candidates/pack of some shard (S2+)
    d["union_retrieved"] = any(ORD[s] >= 2 for s in st)  # S3 or K
    d["union_kept"] = any(s == "K" for s in st)          # kept in some single-shard kit
    d["in_some_shard_pool"] = any(x["inshard"] for x in d["shards"].values())
    d["kept_shards"] = [n for n, x in d["shards"].items() if x["stage"] == "K"]
    d["base_stage"] = bst[i]; d["base_kept"] = bst[i] == "K"
    d["gain_kept"] = d["union_kept"] and not d["base_kept"]; d["lost_in_all"] = d["base_kept"] and not d["union_kept"]
    d["lost_in"] = [n for n, x in d["shards"].items() if d["base_kept"] and x["stage"] != "K"]
    d["gain_in"] = [n for n, x in d["shards"].items() if (not d["base_kept"]) and x["stage"] == "K"]
    d["base_S1_now_S2plus"] = bst[i] == "S1" and d["union_not_S1"]
def summ(ids):
    return dict(n=len(ids), base_S1=cnt(ids, lambda i: bst[i] == "S1"), base_kept=cnt(ids, lambda i: bst[i] == "K"),
                union_S1=cnt(ids, lambda i: not res["items"][i]["union_not_S1"] and bst[i] == "S1"),  # S1 in K3 and still S1 in every shard
                S1_to_S2plus_union=cnt(ids, lambda i: res["items"][i]["base_S1_now_S2plus"]),
                union_fact_in_shard_pool=cnt(ids, lambda i: res["items"][i]["in_some_shard_pool"]),
                union_retrieved=cnt(ids, lambda i: res["items"][i]["union_retrieved"]), union_kept_any_shard=cnt(ids, lambda i: res["items"][i]["union_kept"]),
                gained_kept_any_shard=cnt(ids, lambda i: res["items"][i]["gain_kept"]), base_kept_lost_in_every_shard=cnt(ids, lambda i: res["items"][i]["lost_in_all"]),
                gained_ids=sorted(i for i in ids if res["items"][i]["gain_kept"]), lost_all_ids=sorted(i for i in ids if res["items"][i]["lost_in_all"]))
res["union"] = dict(MAIN92=summ(MAIN), v01_52=summ(V01), cm40=summ([i for i in MAIN if i not in V01]))
# per-shard vs baseline kept delta and S1 drop
for n, s in res["shards"].items():
    s["S1_drop_MAIN"] = res["baseline_K3"]["MAIN92"]["S1"] - s["MAIN92"]["S1"]; s["kept_delta_MAIN"] = s["MAIN92"]["K"] - res["baseline_K3"]["MAIN92"]["K"]
    s["S1_drop_v01"] = res["baseline_K3"]["v01_52"]["S1"] - s["v01_52"]["S1"]; s["kept_delta_v01"] = s["v01_52"]["K"] - res["baseline_K3"]["v01_52"]["K"]
    s["gained_kept_ids"] = sorted(i for i in MAIN if res["items"][i]["shards"][n]["stage"] == "K" and bst[i] != "K")
    s["lost_kept_ids"] = sorted(i for i in MAIN if res["items"][i]["shards"][n]["stage"] != "K" and bst[i] == "K")
# verdict by the frozen rule, applied per shard (single-shard kit) and to the union of kept (upper bound, not a shippable kit)
base = res["baseline_K3"]
def verdict(main_k, v01_k, s1drop):
    if main_k >= base["MAIN92"]["K"] + 3 and v01_k >= base["v01_52"]["K"] and s1drop >= 3: return "PASS"
    return "COVERAGE-ONLY" if s1drop >= 3 else "FAIL"
for n, s in res["shards"].items(): s["verdict"] = verdict(s["MAIN92"]["K"], s["v01_52"]["K"], s["S1_drop_MAIN"])
u = res["union"]
res["union_verdict_upper_bound"] = verdict(base["MAIN92"]["K"] + u["MAIN92"]["gained_kept_any_shard"] - u["MAIN92"]["base_kept_lost_in_every_shard"],
                                           base["v01_52"]["K"] + u["v01_52"]["gained_kept_any_shard"] - u["v01_52"]["base_kept_lost_in_every_shard"], u["MAIN92"]["S1_to_S2plus_union"])
res["shards_scored"] = shards
OUTN = sys.argv[1] if len(sys.argv) > 1 else "b3.json"
json.dump(res, open(W + OUTN, "w"), indent=1)
print("shards", shards)
for n, s in res["shards"].items(): print(n, "MAIN", s["MAIN92"], "v01", s["v01_52"], "S1drop", s["S1_drop_MAIN"], "keptD", s["kept_delta_MAIN"], "v01keptD", s["kept_delta_v01"], "pool", s["shard_in_pool"], "slots", s["shard_kept_slots"], s["verdict"])
print("baseline", base["MAIN92"], base["v01_52"]); print(json.dumps(res["union"]["MAIN92"])); print(json.dumps(res["union"]["v01_52"])); print(res["union_verdict_upper_bound"])
