#!/usr/bin/env python3
"""Acceptance check for an O2 implementation on rnd/lantern/o2/o2-testset.jsonl (spec §5.1).
Input: the test set + a decisions file {case_id: "refuse"|"keep"} from the implementation under test
(default: run the non-normative reference o2_reference.decide)."""
import sys, json, argparse, collections, os
sys.path.insert(0, os.path.dirname(__file__))
ap = argparse.ArgumentParser(); ap.add_argument("--testset", default=os.path.join(os.path.dirname(__file__), "..", "o2", "o2-testset.jsonl"))
ap.add_argument("--decisions", help="JSON {case_id: refuse|keep}; omit to use o2_reference"); a = ap.parse_args()
rows = [json.loads(l) for l in open(a.testset)]
if a.decisions:
    dec = json.load(open(a.decisions))
else:
    import o2_reference as o, refusal_audit as ra
    ra.configure(["boar-crypto", "boar-wikivoyage-en", "wiki-vital5"]); P = ra.Packs()
    def text(t):
        bare = ra.strip_prefix(t)
        order = ["boar-wikivoyage-en"] if t.startswith("Wikivoyage: ") else ["boar-crypto"] if bare != t else ["boar-crypto", "wiki-vital5"]
        for pk in order:
            x = P._v1_text(pk, bare) if pk in ra.V1_PACKS else P._v2_text(pk, bare)
            if x: return x
    dec = {r["case_id"]: o.decide(r["question"], [{"title": t, "text": text(t)} for t in dict.fromkeys(r["citedTitles"] or r["promptTitles"])])["action"] for r in rows}
by = collections.defaultdict(list)
for r in rows: by[r["bucket"]].append((r, dec[r["case_id"]]))
def cnt(b, act): return sum(1 for r, d in by[b] if d == act)
mr, mk, gt, nu, oor = by["must_refuse"], by["must_keep"], by["gate_must_not_worsen"], by["neutral_right_unsupported"], by["cw_out_of_reach"]
print(f"must_refuse   recall  {cnt('must_refuse','refuse')}/{len(mr)}   (gate A1: >= {len(mr)-1}/{len(mr)})")
print(f"must_keep     kept    {cnt('must_keep','keep')}/{len(mk)}   (gate A2: all)")
print(f"gate cases    kept    {cnt('gate_must_not_worsen','keep')}/{len(gt)}   (gate A3: all)")
print(f"neutral (right answer, off-subject source) refused {cnt('neutral_right_unsupported','refuse')}/{len(nu)}   (reported, not gated; counts in A4)")
print(f"out of reach (cw with on-subject source) refused {cnt('cw_out_of_reach','refuse')}/{len(oor)}   (reported)")
fails = [(r['case_id'], r['bucket'], d) for r, d in mr + mk + gt if d != r["expected_o2"]]
for f in fails: print("  MISS", *f)
ok = cnt('must_refuse','refuse') >= len(mr) - 1 and cnt('must_keep','keep') == len(mk) and cnt('gate_must_not_worsen','keep') == len(gt)
print("TEST-SET GATES (A1-A3):", "PASS" if ok else "FAIL")
