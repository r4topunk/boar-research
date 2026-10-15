#!/usr/bin/env python3
"""HEADPASS-X2b stage 1/2 precheck (0 LLM). Run: python3 -I precheck_x2b.py [--out aggregates/precheck-x2b.json] [--packs p1,p2]
- changed vs S (arms/packs/selftest-runs/st-<pack>-cut7-s42.traces.jsonl): retrieval.kept (title, section) differs OR timing.promptTokens
  differs; bar >= 0.20 (rc 8 below the bar, only when all 9 packs are present).
- codes from the ON traces: headpass:add / headpass:dense:add / headpass:budget:dropped (items, chunks); errors.
- reach from the traces (same chunk-id matching as gate_x2b.py): fact present = a fact chunk kept under S (replay split-x2b S_present: the
  kept list before the append is S's) OR a fact chunk among the appended ids (headpass:add / headpass:dense:add codes). Compared with the
  replay's x2b_present (102) per item; also kept (title, section) list of the trace == the replay's x2b kept list."""
import json, sys, re, collections, os
A = "$BOAR_WS/rnd/research/coordinator/arms"; H = f"{A}/headpass-st"; G = f"{H}/gen-x2b"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
if "--packs" in sys.argv: PACKS = sys.argv[sys.argv.index("--packs") + 1].split(",")
FACTS = json.load(open(f"{A}/oracle-st/tools/oracle-facts.json"))
CID = re.compile(r"^pack:(?:local-)?([^:]+):(\d+)$")
def own(ids, p): return {int(m.group(2)) for x in ids for m in [CID.match(x or "")] if m and m.group(1) == p}
tr = lambda p: {(t := json.loads(l))["itemId"]: t for l in open(p) if l.strip()}
kept = lambda t: [(s.get("title"), s.get("section")) for s in (t.get("retrieval") or {}).get("kept") or []]
pt = lambda t: (t.get("timing") or {}).get("promptTokens")
codes = lambda t: (t.get("route") or {}).get("reasonCodes") or []
split = {d["id"]: d for d in map(json.loads, open(f"{H}/runs-x2/split-x2b.jsonl"))}
rep = {}
for p in PACKS:
    L = [json.loads(l) for l in open(f"{H}/runs-x2/st-{p}.x2b.jsonl")]; seen = collections.Counter()
    for l in L:
        k = seen[l["id"]]; seen[l["id"]] += 1
        if k == 3: rep[l["id"]] = l  # pass order off,x1,x2,x2b,off2
c = collections.Counter(); per = {}; gsplit = {}
for p in PACKS:
    f = f"{G}/st-{p}-cut7-headpassx2b-s42.traces.jsonl"
    if not os.path.exists(f): continue
    S = tr(f"{A}/packs/selftest-runs/st-{p}-cut7-s42.traces.jsonl"); O = tr(f); pc = collections.Counter()
    for i in S:
        if i not in O: c["missing"] += 1; continue
        s, o = S[i], O[i]; c["n"] += 1; c["errors"] += bool(o.get("error"))
        d = kept(s) != kept(o) or pt(s) != pt(o); c["changed"] += d; pc["changed"] += d
        cs = codes(o); ax = [x.split(":add:")[1] for x in cs if x.startswith("headpass:add:")]; ad = [x.split(":add:")[1] for x in cs if x.startswith("headpass:dense:add:")]
        bd = [x[len("headpass:budget:dropped:"):] for x in cs if x.startswith("headpass:budget:dropped:")]
        c["fired"] += bool(ax or ad); c["x1_add_items"] += bool(ax); c["dense_add_items"] += bool(ad); c["budget_items"] += bool(bd)
        c["x1_add"] += len(ax); c["dense_add"] += len(ad); c["budget_dropped"] += len(bd)
        fcs = {int(x.rsplit(":", 1)[1]) for x in FACTS[i]["fact_chunks"]}
        pres = split[i]["S_present"] or bool(fcs & own(ax + ad, p)); c["present_gen"] += pres; pc["present_gen"] += pres
        c["present_replay"] += split[i]["x2b_present"]; c["present_agree"] += pres == split[i]["x2b_present"]
        c["appended_same_as_replay"] += (ax == (rep[i].get("appendedX1") or []) and ad == (rep[i].get("appendedDense") or []))
        c["kept_same_as_replay"] += kept(o) == [(x.get("title"), x.get("section")) for x in rep[i]["kept"]]
        gsplit[i] = ("unchanged" if not d else "present_x1" if pres and split[i]["X1_present"] else "newly_present_x2b" if pres and not split[i]["S_present"]
                     else "nonfact_only" if (ax or ad) and not pres else "other_changed")
    per[p] = dict(pc)
n = c["n"] or 1
out = {**dict(c), "share_changed": round(c["changed"] / n, 3), "bar": 0.2, "pass": c["changed"] / n >= 0.2, "per_pack": per,
       "gen_split": dict(collections.Counter(gsplit.values()))}
print(json.dumps(out))
if "--out" in sys.argv: json.dump(out, open(sys.argv[sys.argv.index("--out") + 1], "w"), indent=1)
json.dump(gsplit, open(f"{H}/aggregates/gen-split-x2b.json", "w"))
sys.exit(8 if len(PACKS) == 9 and not out["pass"] else 0)
