"""Where the gold is lost between raw and kept (0 LLM): reasonCodes grounding:* of the replay for items with gold in raw but not kept.
python3 -I tools/keep_loss.py"""
import json, os, collections, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
m = {r["id"]: r for r in json.load(open(os.path.join(ROOT, "aggregates/matrix.json")))["items"]}
rep = {}
for l in open(os.path.join(ROOT, "replay/qform.replay.jsonl")):
    d = json.loads(l); rep[d["id"]] = d
out = {"gold_in_raw_not_kept": 0, "by_form": {}, "codes": {}, "all_items_codes_by_form": {}}
c = collections.Counter(); byf = collections.Counter()
allc = collections.defaultdict(collections.Counter)
for i, r in m.items():
    cs = rep[i]["reasonCodes"]
    for x in cs:
        if x.startswith("grounding:"): allc[r["form"]][re.sub(r"-\d+$", "", x)] += 1
    if r["hit_raw"] and not r["hit_kept"]:
        out["gold_in_raw_not_kept"] += 1; byf[r["form"]] += 1
        for x in cs:
            if x.startswith(("grounding:", "instant:off")): c[re.sub(r"-\d+$", "", x)] += 1
out["by_form"] = dict(byf); out["codes"] = dict(c)
out["all_items_codes_by_form"] = {k: dict(v) for k, v in sorted(allc.items())}
json.dump(out, open(os.path.join(ROOT, "aggregates/keep_loss.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
