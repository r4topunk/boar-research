#!/usr/bin/env python3
"""ADDENDUM-3 job 17 gate scorer (0 LLM). python3 -I score_carry_gate.py -> replays/RCST/gate.json + table.
Identity: rs-RC-STICKY with RS_STICKY unset vs rs-RC (replays/RC): kept chunk ids in order on MAIN 97 and F8 96 (48 F0 + 48 F8).
Carry (RS_STICKY=2): F8 and LONGSESSION survival / recovered / off-subject multiplier with the U5 rules, imported verbatim from uxmatrix/u5/tools/score_u5.py
(fhit/fon/f8_rows, lhit/lon/ls_rows, agg; the part of that file before its result loop), base = replays/RC (no carry), carry = replays/RCST/*.c2."""
import json, os
A = "<workspace>/rnd/research/coordinator/arms"; VD = A + "/validation-1024"; R0 = VD + "/replays/RC"; R1 = VD + "/replays/RCST"
src = open(A + "/uxmatrix/u5/tools/score_u5.py").read(); src = src[:src.index("res = {")]
g = {"__file__": A + "/uxmatrix/u5/tools/score_u5.py"}; exec(compile(src, "score_u5_head", "exec"), g)
by = lambda f: {r["id"]: r for r in g["rd"](f)}
ids = lambda r: [c["chunkId"] for c in (r.get("keptFull") or [])]
out = {}
for s in ("main", "f8"):
    a, b = by(f"{R0}/{s}.jsonl"), by(f"{R1}/{s}.jsonl")
    same = sum(ids(a[i]) == ids(b[i]) for i in a if i in b)
    out[f"identity_{s}"] = dict(n=len(a), same=same, diff=sorted(i for i in a if i in b and ids(a[i]) != ids(b[i])), missing=sorted(set(a) - set(b)))
f8 = g["agg"](g["f8_rows"](by(f"{R0}/f8.jsonl"), by(f"{R1}/f8.c2.jsonl")))
ls = g["agg"](g["ls_rows"](by(f"{R0}/ls.jsonl"), by(f"{R1}/ls.c2.jsonl")))
LSR, LSC = by(f"{R0}/ls.jsonl"), by(f"{R1}/ls.c2.jsonl")
sc = [i for i in g["SC"] if i in LSR and i in LSC]
out["f8"] = {k: v for k, v in f8.items() if not k.endswith("_ids")}; out["ls"] = {k: v for k, v in ls.items() if not k.endswith("_ids")}
out["ls_selfcontained_kept_mult"] = round(sum(len(LSC[i]["keptFull"] or []) for i in sc) / max(1, sum(len(LSR[i]["keptFull"] or []) for i in sc)), 3)
out["gate_identity_pass"] = out["identity_main"]["same"] == 97 and out["identity_f8"]["same"] == 96
json.dump(out, open(R1 + "/gate.json", "w"), indent=1)
print(json.dumps({k: (v if not isinstance(v, dict) else {x: y for x, y in v.items() if x in ("n", "same", "diff", "K1", "S", "survival", "LOST", "R", "carry_K2", "junk", "junk_carry", "carry_mult")}) for k, v in out.items()}, indent=1))
