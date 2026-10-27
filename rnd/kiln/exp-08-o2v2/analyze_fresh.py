#!/usr/bin/env python3
"""exp-08 FROZEN out-of-sample analysis of O2 v2c (hashed in FROZEN-v2c.sha256; do not edit).

Inputs: runs/fresh-<tag>-off.jsonl, -off-rep.jsonl, -v2c.jsonl (run-v2c-fresh.sh) and the new items file (with
`reference` or `answer` per item, written by Veil). Labels of the OFF answers of the fired questions:
hand-labels-fresh-<tag>.json ({id: {label, why}}, classes pass/fail/cw/refused, written against the references
BEFORE running this script), Jev v2 as second rater; an already-declined OFF answer is `refused`.

§5 (rnd/kiln/exp-03-o2/README.md), applied as is:
- fresh gate: new false refusals (fired, OFF label pass) <= 1 per 10 hits;
- validity checks: off vs off-rep identical on every item; v2c differs from off only where O2 fired;
- in-scope count reported (o2Kind != null is not observable from rows; items are in scope by Veil's design).
A4/A5 (device 52) are the in-sample values already measured (results.md); the new items are the fresh gate.
Usage: python3 analyze_fresh.py <items.jsonl> <tag> [--jev]
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
B = "<workspace>"
items_p, tag = sys.argv[1], sys.argv[2]
items = {q["id"]: q for q in map(json.loads, open(items_p))}
R = {a: {r["id"]: r for r in map(json.loads, open(f"{HERE}/runs/fresh-{tag}-{a}.jsonl"))} for a in ("off", "off-rep", "v2c")}
ids = sorted(R["off"])
key = lambda r: (r["answer"], [s["title"] for s in r["shownSources"]], r["flags"]["declined"])
det = [i for i in ids if key(R["off"][i]) == key(R["off-rep"][i])]
fired = [i for i in ids if "grounding:o2-off-subject" in R["v2c"][i]["reasonCodes"]]
cf_break = [i for i in ids if i not in fired and key(R["v2c"][i]) != key(R["off"][i])]
hp = f"{HERE}/hand-labels-fresh-{tag}.json"
hand = json.load(open(hp)) if os.path.exists(hp) else {}
jev = {}
if "--jev" in sys.argv and fired:
    sys.path.insert(0, f"{B}/rnd/kiln/exp-04-jev")
    from jev_label import label_items
    JMAP = {"correct": "pass", "confident_wrong": "cw", "wrong_or_incomplete_hedged": "fail", "refused": "refused"}
    its = [{"id": i, "question": R["off"][i]["question"], "reference": items[i].get("reference") or items[i].get("answer", ""),
            "rubric": " ; ".join(items[i].get("rubric", [])) if isinstance(items[i].get("rubric"), list) else items[i].get("rubric", ""),
            "answer": R["off"][i]["answer"], "retrieved_titles": [s["title"] for s in R["off"][i]["shownSources"]]} for i in fired]
    for o in label_items(its, budget_usd=0.10):
        jev[o["id"]] = JMAP.get(o["label"], o["label"])


def label(i):
    if R["off"][i]["flags"]["declined"]:
        return "refused"
    return hand.get(i, {}).get("label", "?")


labs = {i: label(i) for i in fired}
fr = [i for i in fired if labs[i] == "pass"]
unl = [i for i in fired if labs[i] == "?"]
gate = len(fired) == 0 or len(fr) * 10 <= len(fired)
valid = len(det) == len(ids) and not cf_break
L = [f"# exp-08 out-of-sample: O2 v2c on {len(ids)} new fresh items ({tag})", "",
     f"- Determinism off vs off-rep: {len(det)}/{len(ids)}; counterfactual breaks: {len(cf_break)} {cf_break or ''} → run {'VALID' if valid else 'INVALID'}",
     f"- v2c hits: {len(fired)}; OFF labels of hits: pass {list(labs.values()).count('pass')}, cw {list(labs.values()).count('cw')}, "
     f"fail {list(labs.values()).count('fail')}, refused {list(labs.values()).count('refused')}, unlabelled {len(unl)} {unl or ''}",
     f"- Δcw attributable on these items: {-100 * list(labs.values()).count('cw') / len(ids):+.1f} pp; Δpass: {-100 * len(fr) / len(ids):+.1f} pp",
     f"- **Fresh gate (§5: new false refusals ≤ 1 per 10 hits): {len(fr)}/{len(fired)} → {'PASS' if gate else 'FAIL'}**"
     + (" (labels incomplete: verdict pending)" if unl else ""), "",
     "| id | OFF label (hand / Jev) | reason code | OFF passages | OFF answer (start) |", "|---|---|---|---|---|"]
for i in fired:
    o = R["off"][i]
    rc = next((c for c in R["v2c"][i]["reasonCodes"] if c.startswith("grounding:o2")), "")
    L.append(f"| {i} | **{labs[i]}** ({hand.get(i, {}).get('label', '—')} / {jev.get(i, '—')}) | {rc} | "
             f"{'; '.join(s['title'] for s in o['shownSources'][:3])} | {o['answer'][:110].replace('|', '/')} |")
print("\n".join(L))
json.dump({"n": len(ids), "determinism": len(det), "cf_break": cf_break, "fired": fired, "labels": labs, "jev": jev,
           "false_refusals": fr, "gate_pass": gate, "valid": valid}, open(f"{HERE}/results-fresh-{tag}.json", "w"), indent=1)
