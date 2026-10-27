#!/usr/bin/env python3
"""RD3 replay comparison (0 LLM). python3 -I replay_cmp.py -> ../replay-cmp.json
off = reader/replays/main.RD3off.jsonl (switch unset), on = main.RD3on.jsonl (BOAR_READ_KEEPANS=1), base = sefix/replays/main.v3-extra.jsonl (F1b replay).
Prompt-token proxy = engine approxTokens (ceil(chars/4)) of title+body over the kept sources (the part this switch changes)."""
import json, sys
CM = "<workspace>/rnd/research/coordinator/arms/coverage-map"
rd = lambda f: {r["id"]: r for r in (json.loads(l) for l in open(f) if l.strip())}
base, off, on = rd(CM + "/sefix/replays/main.v3-extra.jsonl"), rd(CM + "/reader/replays/main.RD3off.jsonl"), rd(CM + "/reader/replays/main.RD3on.jsonl")
ids = open("<workspace>/rnd/research/coordinator/arms/lp-screens/main-97.ids").read().split()
tok = lambda s: -(-len(s) // 4)
kt = lambda r: sum(tok(c["title"] + "\n" + c["body"]) for c in r["keptFull"])
kid = lambda r: [c["chunkId"] for c in r["keptFull"]]
res = dict(n=len(ids))
res["off_vs_base_identical_kept"] = sum(kid(off[i]) == kid(base[i]) and [c["body"] for c in off[i]["keptFull"]] == [c["body"] for c in base[i]["keptFull"]] for i in ids)
res["off_vs_base_identical_reasonCodes"] = sum(off[i]["reasonCodes"] == base[i]["reasonCodes"] for i in ids)
changed = [i for i in ids if [(c["chunkId"], c["body"]) for c in on[i]["keptFull"]] != [(c["chunkId"], c["body"]) for c in off[i]["keptFull"]]]
res["changed_replay"] = len(changed); res["changed_ids"] = changed
res["kept_tok_off_mean"] = round(sum(kt(off[i]) for i in ids) / len(ids), 1); res["kept_tok_on_mean"] = round(sum(kt(on[i]) for i in ids) / len(ids), 1)
res["kept_tok_rel_increase"] = round(res["kept_tok_on_mean"] / res["kept_tok_off_mean"] - 1, 4)
res["kept_tok_increase_on_changed_mean"] = round(sum(kt(on[i]) - kt(off[i]) for i in changed) / max(1, len(changed)), 1)
res["max_item_increase"] = max((kt(on[i]) - kt(off[i]) for i in ids), default=0)
res["codes"] = {i: [c for c in on[i]["reasonCodes"] if c.startswith("keepans:")] for i in ids if any(c.startswith("keepans:") for c in on[i]["reasonCodes"])}
res["by_kind"] = dict(whole=sum(c.startswith("keepans:whole") for v in res["codes"].values() for c in v), thread=sum(c.startswith("keepans:thread") for v in res["codes"].values() for c in v))
# thread/whole restored chunks dropped again by the topic guard? (code present but chunk not in kept)
dropped = {}
for i, v in res["codes"].items():
    for c in v:
        cid = c.split(":", 2)[2]
        if cid not in kid(on[i]): dropped.setdefault(i, []).append(c)
res["restored_then_dropped_by_guard"] = dropped
def ev(i):
    r = on[i]; return [(c["chunkId"], len(c["body"])) for c in r["keptFull"]]
res["money-016"] = dict(off=[(c["chunkId"], len(c["body"])) for c in off["st-qa-money-se-016"]["keptFull"]], on=ev("st-qa-money-se-016"), has_430K_off=any("$430K" in c["body"] or "430K" in c["body"] for c in off["st-qa-money-se-016"]["keptFull"]), has_430K_on=any("430K" in c["body"] for c in on["st-qa-money-se-016"]["keptFull"]))
res["money-020"] = dict(off=[c["chunkId"] for c in off["st-qa-money-se-020"]["keptFull"]], on=[c["chunkId"] for c in on["st-qa-money-se-020"]["keptFull"]], has_136998_on=any(c["chunkId"].endswith(":136998") for c in on["st-qa-money-se-020"]["keptFull"]), codes=res["codes"].get("st-qa-money-se-020", []), guard_codes=[c for c in on["st-qa-money-se-020"]["reasonCodes"] if c.startswith("grounding") or c.startswith("context")])
for t in ("st-qa-money-se-018", "st-qa-cooking-se-001"):
    res[t] = dict(off=[(c["chunkId"], len(c["body"])) for c in off[t]["keptFull"]], on=ev(t), codes=res["codes"].get(t, []), guard_codes=[c for c in on[t]["reasonCodes"] if c.startswith("grounding") or c.startswith("context")])
json.dump(res, open(CM + "/reader/rd3/replay-cmp.json", "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "codes"}, indent=1)[:7000])
