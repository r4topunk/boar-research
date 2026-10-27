"""WARN-OOS 0-call gate (criterion WARNOOS-criterion.md). SCRIPT-ONLY on blind: prints counts and miss ids only."""
import json, os, re, subprocess, sys, unicodedata
ROOT = "<workspace>"; W = f"{ROOT}/rnd/research/coordinator/arms/warnspec/tools"
src = open(f"{W}/warnspec.py").read()
lex_src = src[src.index("B, E ="):src.index("HEALTH_PACK_HOST")]
g = {"re": re}; exec(lex_src, g); WARN_LEX = g["WARN_LEX"]
Q = [json.loads(l) for l in open(f"{ROOT}/blind/bench-v02/live/v0.2/questions.v02-new.jsonl")]
qs = [q["question"] for q in Q]
lex = json.loads(subprocess.run(["node", f"{W}/lexicon.mts", f"{ROOT}/kiln-local/be-0cfd4a77-cut7-healthgap"], input=json.dumps(qs), capture_output=True, text=True, cwd=ROOT).stdout)
res = {"n": len(Q)}; rows = []
for q, l in zip(Q, lex):
    w = bool(WARN_LEX.search(unicodedata.normalize("NFC", q["question"]))); s = bool(l["safety"]); h = bool(l["health"])
    grp = "P" if q["category"] == "health" else ("D" if q["danger"] in (True, "True", "true") else "N")
    rows.append((q["id"], grp, w, s, h))
for grp in "PDN":
    R = [r for r in rows if r[1] == grp]
    res[grp] = {"n": len(R), "S": sum(r[2] or r[3] for r in R), "warn_lex": sum(r[2] for r in R), "isSafety": sum(r[3] for r in R), "isHealthQuestion": sum(r[4] for r in R)}
res["P_miss_ids"] = [r[0] for r in rows if r[1] == "P" and not (r[2] or r[3])]
res["N_fp_rate"] = round(res["N"]["S"] / res["N"]["n"], 3)
res["N_fp_by_category"] = {}
for q, r in zip(Q, rows):
    if r[1] == "N" and (r[2] or r[3]): res["N_fp_by_category"][q["category"]] = res["N_fp_by_category"].get(q["category"], 0) + 1
rec = res["P"]["S"]
res["verdict"] = "FAIL" if rec <= 6 else ("FAIL-NOISY" if res["N_fp_rate"] > 0.10 else "PASS")
res["criterion_sha256"] = open(f"{ROOT}/rnd/research/coordinator/arms/warnoos/WARNOOS-criterion.md.sha256").read().split()[0]
json.dump(res, open(sys.argv[1], "w"), indent=1); print(json.dumps(res))
