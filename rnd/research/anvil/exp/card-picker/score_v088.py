"""Score picker outputs with Compass safety v0.8.8 wrong-card check (jev backend, DEV ONLY; same INSTR/CRIT/threshold/cache).
python3 score_v088.py cardtexts.jsonl  -> per picker: cards shown, wrong-card (p<0.5), ok."""
import json, sys, collections
sys.path.insert(0, "<workspace>/rnd/research/compass/exp/safety-v088")
import wrong_card as W
items = {json.loads(l)["id"]: json.loads(l) for l in open("<workspace>/rnd/research/compass/exp/emergency-dev/dev.jsonl")}
rows = [json.loads(l) for l in open(sys.argv[1])]
res = collections.defaultdict(lambda: {"shown": 0, "wrong": 0, "wrong_ids": []})
out = []
for r in rows:
    if r["text"] is None: continue
    it = items[r["id"]]
    p = W.jev({"conversation": W.conversation({}, it), "card": r["text"]})
    s = res[r["picker"]]; s["shown"] += 1
    if p < W.THRESHOLD: s["wrong"] += 1; s["wrong_ids"].append(f'{r["id"]}:{r["key"]}({it["cond"]})')
    out.append({**r, "p_right": p})
json.dump(out, open(sys.argv[1].replace(".jsonl", ".v088.json"), "w"), ensure_ascii=False)
for k, s in res.items(): print(f'{k:28} cards shown {s["shown"]:3} · wrong-card (v0.8.8) {s["wrong"]:2} · ok {s["shown"]-s["wrong"]}   {" ".join(s["wrong_ids"])}')
