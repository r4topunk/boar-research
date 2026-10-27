"""HEALTHDROP step 0 compare (criterion 63bfa747...). 0 LLM. Usage: python3 -I compare_hd.py <runs dir> <out json>"""
import json, sys, glob, os
R, OUT = sys.argv[1:3]
THE18 = "st-boar-firstaid-en-003 st-boar-firstaid-en-005 st-boar-firstaid-en-008 st-boar-firstaid-en-009 st-boar-firstaid-en-011 st-boar-firstaid-en-012 st-boar-firstaid-en-016 st-boar-firstaid-en-018 st-boar-medlineplus-en-006 st-boar-medlineplus-en-011 st-boar-medlineplus-en-017 st-qa-health-se-005 st-qa-health-se-012 st-qa-health-se-018 st-qa-health-se-020 st-qa-outdoors-se-001 st-qa-outdoors-se-011 st-qa-outdoors-se-018".split()
SETS = [os.path.basename(p)[3:-len("-on.traces.jsonl")] for p in sorted(glob.glob(f"{R}/hd-*-on.traces.jsonl"))]
DROP = {"timing", "resources", "createdAt", "runtime", "engine", "runId", "tMs", "ms", "ttftMs", "totalMs", "retrievalMs", "loadMs", "setupMs", "tokPerSec", "loadAvg1m"}
def norm(x):
    if isinstance(x, dict): return {k: norm(v) for k, v in x.items() if k not in DROP and not (k in ("arm", "commit"))}
    if isinstance(x, list): return [norm(v) for v in x]
    return x
def load(s, c): return {r["itemId"]: r for r in map(json.loads, filter(str.strip, open(f"{R}/hd-{s}-{c}.traces.jsonl")))}
def key(r): return (r["route"].get("task"), r["route"].get("tier"), tuple(r["route"]["reasonCodes"]), tuple(k["title"] for k in r["retrieval"]["kept"]), r["answer"]["text"])
agg = {"sets": {}, "rescues": [], "the18": []}
for s in SETS:
    on, off, base = load(s, "on"), load(s, "off"), load(s, "base")
    assert set(on) == set(off) == set(base), s
    changed = [i for i in on if key(on[i]) != key(off[i])]
    resc = [i for i in on if "healthdrop:kept" in on[i]["route"]["reasonCodes"]]
    offbase = [i for i in on if json.dumps(norm(off[i]), sort_keys=True) != json.dumps(norm(base[i]), sort_keys=True)]
    nosrc_off = [i for i in off if "grounding:health-no-source" in off[i]["route"]["reasonCodes"]]
    hg = [i for i in on if any(c.startswith("healthgap:") for c in on[i]["route"]["reasonCodes"])]
    agg["sets"][s] = {"n": len(on), "changed_on_vs_off": changed, "rescued": resc, "changed_not_rescued": [i for i in changed if i not in resc],
                      "off_vs_base_diff": offbase, "off_no_source": nosrc_off, "healthgap_turns": len(hg), "healthgap_rescued": [i for i in hg if i in resc],
                      "errors": sum(1 for r in on.values() if r.get("error"))}
    for i in resc:
        r = on[i]; c = r["route"]["reasonCodes"]
        agg["rescues"].append({"set": s, "id": i, "q": r["question"], "kept": [k["title"] for k in r["retrieval"]["kept"]], "kept_source": [k.get("source") for k in r["retrieval"]["kept"]],
                               "path": [x for x in c if x.startswith("grounding:health-") and x not in ("grounding:health-strict",) and "dropped" not in x], "modelId": r["answer"].get("modelId"),
                               "text": r["answer"]["text"][:400], "off_text": off[i]["answer"]["text"][:120], "off_codes": [x for x in off[i]["route"]["reasonCodes"] if "health" in x or "card" in x]})
    for i in THE18:
        if i in on:
            agg["the18"].append({"id": i, "q": on[i]["question"], "off_plain": off[i]["answer"]["text"].startswith("I don't have a reliable offline source"),
                                 "dropped": [d["title"] for d in off[i]["retrieval"]["dropped"]], "dropped_src": [d.get("source", "")[:60] for d in off[i]["retrieval"]["dropped"]],
                                 "rescued": "healthdrop:kept" in on[i]["route"]["reasonCodes"], "kept": [k["title"] for k in on[i]["retrieval"]["kept"]],
                                 "path": [x for x in on[i]["route"]["reasonCodes"] if x.startswith("grounding:health-") and "dropped" not in x and x != "grounding:health-strict"],
                                 "on_text": on[i]["answer"]["text"][:300]})
json.dump(agg, open(OUT, "w"), indent=1, ensure_ascii=False)
for s, v in agg["sets"].items():
    print(f"{s:24s} n={v['n']:3d} changed={len(v['changed_on_vs_off'])} rescued={len(v['rescued'])} changed_not_rescued={len(v['changed_not_rescued'])} off!=base={len(v['off_vs_base_diff'])} off_nosrc={len(v['off_no_source'])} hg={v['healthgap_turns']} hg_resc={len(v['healthgap_rescued'])} err={v['errors']}")
print("the18 present", len(agg["the18"]), "off plain", sum(x["off_plain"] for x in agg["the18"]), "rescued", sum(x["rescued"] for x in agg["the18"]))
