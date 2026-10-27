#!/usr/bin/env python3
"""prep_judge.py <dir> <seed>: seed the judgments files for judge.mjs resume. Reuses existing judge.v1-med verdicts (bench v0.1)
whose traced answer text for the same item is byte-identical (any earlier run, both orders present); judge.mjs then judges only the rest.
The arm also reuses the control's verdicts where its text equals the control's."""
import json, sys, glob, os
D, S = sys.argv[1], sys.argv[2]
KILN = "<workspace>/boar-eval/runs/kiln"
REFS = "bd235bb9811f"  # v0.1 refs sha prefix (judge log header); rows carry refsSha256
ld = lambda p: {t["itemId"]: t for t in map(json.loads, open(p))}
def rows(p): return [json.loads(l) for l in open(p) if l.strip()]
txt = lambda t: t["answer"]["text"]
# index: (item, text) -> {order: row}, preferring the same seed
idx = {}
for jp in sorted(glob.glob(f"{KILN}/**/*.judgments.v1-med.jsonl", recursive=True)):
    if "/speedpack-l1/" in jp: continue
    tp = jp.replace(".judgments.v1-med.jsonl", ".traces.jsonl")
    if not os.path.exists(tp): continue
    try: tr = ld(tp)
    except Exception: continue
    same_seed = f"s{S}" in os.path.basename(jp)
    for r in rows(jp):
        if not r.get("ok") or not r.get("refsSha256", "").startswith(REFS) or r["queryId"] not in tr: continue
        k = (r["queryId"], txt(tr[r["queryId"]]))
        slot = idx.setdefault(k, {})
        if r["order"] not in slot or same_seed: slot[r["order"]] = (r, jp)
def reuse(traces):
    out, src = [], {}
    for i, t in traces.items():
        slot = idx.get((i, txt(t)), {})
        if len(slot) == 2:
            for o, (r, jp) in slot.items(): out.append(r)
            src[i] = sorted({os.path.basename(jp) for _, jp in slot.values()})
    return out, src
ctl = ld(f"{D}/spctl-v01-s{S}.traces.jsonl"); arm = ld(f"{D}/spsp-v01-s{S}.traces.jsonl")
cj, csrc = reuse(ctl)
open(f"{D}/spctl-v01-s{S}.judgments.v1-med.jsonl", "w").write("".join(json.dumps(r) + "\n" for r in cj))
byq = {}
for r in cj: byq.setdefault(r["queryId"], []).append(r)
same_a = sorted(i for i in arm if i in ctl and txt(arm[i]) == txt(ctl[i]) and len(byq.get(i, [])) == 2)
aj = [r for i in same_a for r in byq[i]]
open(f"{D}/spsp-v01-s{S}.judgments.v1-med.jsonl", "w").write("".join(json.dumps(r) + "\n" for r in aj))
json.dump({"ctl_reused": csrc, "arm_reused_from_ctl": same_a}, open(f"{D}/prep-s{S}.json", "w"), indent=1)
print(f"s{S}: control verdicts reused for {len(csrc)}/{len(ctl)} items; arm reuses control verdicts for {len(same_a)}/{len(arm)} items")
