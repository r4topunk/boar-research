"""H3 stage attribution on QFORM (0 LLM): where is the gold lost for the items whose gold is in rawFull but not in B0's kept list (compress vs grounding),
and what the switch does at the compress stage. python3 -I tools/h3_stage_report.py <stage.jsonl from tools/h3-stage.mts>"""
import json, re, sys, collections
R = "<workspace>/rnd/research/coordinator/arms/retrieve-sweep"; QF = R + "/../qform"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
items = {d["id"]: d for d in rd(QF + "/items/qform.jsonl")}
facts = {f["fact_id"]: f for f in json.load(open(QF + "/items/facts.json"))}
norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s.lower())).strip()
cid = lambda x: int(re.search(r":(\d+)$", x).group(1)) if re.search(r":(\d+)$", x) else None
def hit(titles, bodies, ids, f):
    q = norm(f["gold"]["quote"]); g = f["gold"]["merged_chunk_id"]
    return any(q in norm(t + " " + b) or cid(i) == g for t, b, i in zip(titles, bodies, ids))
st = {r["id"]: r for r in rd(sys.argv[1])}
b0 = {r["id"]: r for r in rd(QF + "/replay/qform.replay.jsonl")}
h3 = {r["id"]: r for r in rd(R + "/replay/H3.qform.jsonl")}
cnt = collections.Counter(); rows = []
for i, r in b0.items():
    f = facts[items[i]["fact_id"]]
    raw = hit([c["title"] for c in r["rawFull"]], [c["body"] for c in r["rawFull"]], [c["chunkId"] for c in r["rawFull"]], f)
    kb = hit([c["title"] for c in r["keptFull"]], [c["body"] for c in r["keptFull"]], [c["chunkId"] for c in r["keptFull"]], f)
    s = st[i]
    c_off = hit(s["off"]["titles"], s["off"]["bodies"], s["off"]["ids"], f)
    c_on = hit(s["on"]["titles"], s["on"]["bodies"], s["on"]["ids"], f)
    k3 = hit([c["title"] for c in h3[i]["keptFull"]], [c["body"] for c in h3[i]["keptFull"]], [c["chunkId"] for c in h3[i]["keptFull"]], f)
    if raw and not kb:
        stage = "compress" if not c_off else "grounding"
        cnt["dropped25_" + stage] += 1
        rows.append((i, stage, c_on, k3))
    if raw: cnt["gold_in_raw"] += 1
    if raw and kb: cnt["raw_and_kept_B0"] += 1
    cnt["compress_flag_on"] += s["on"]["flag"]
    cnt["compress_gold_off"] += c_off; cnt["compress_gold_on"] += c_on
    cnt["compress_gold_gain_on"] += (c_on and not c_off); cnt["compress_gold_loss_on"] += (c_off and not c_on)
    cnt["raw_gold_in_raw_but_compress_off_misses"] += (raw and not c_off)
    cnt["raw_gold_missed_compress_off_recovered_on"] += (raw and not c_off and c_on)
print(json.dumps(dict(cnt), indent=1))
for r in rows: print(r)
