"""WARNSPEC feature dump (0 LLM): one row per finished turn from existing traces. Usage: python3 -I feats.py <boar root> <out.jsonl>"""
import json, re, sys, glob, subprocess, os
ROOT = sys.argv[1]; A = f"{ROOT}/rnd/research/coordinator/arms"
src = open(f"{A}/healthgap/tools/healthgap_scan_v12.py", encoding="utf8").read().split("# ---------- data ----------")[0]
g = {"__name__": "scan"}; sys_argv = sys.argv; sys.argv = ["x", ROOT]; exec(src, g); sys.argv = sys_argv
NOT_A_MODEL = {"grounding-guard", "extractive", "none", "places", "calculator", "small-talk"}
def jl(p): return [json.loads(l) for l in open(p) if l.strip()]
def done(t):
    d = [e for e in t.get("events", []) if e.get("type") == "done"]; return d[-1] if d else {}
def row(t, model, set_, src_):
    rc = t["route"]["reasonCodes"]; d = done(t); rec = d.get("receipt") or {}
    text = d.get("finalText") or (t.get("answer") or {}).get("text") or ""
    p = next((float(c.split("=")[1]) for c in rc if c.startswith("detector:p=")), None)
    turns = [m.get("content", "") for m in (t.get("history") or []) if m.get("role") == "user"] if isinstance(t.get("history"), list) else []
    return {"set": set_, "model": model, "src": src_, "id": t["itemId"], "q": t["question"], "codes": rc, "modelId": rec.get("modelId"),
            "outcome": t["route"].get("outcome"), "text": text, "cited": d.get("cited") or [], "kept": [(k["title"], k["source"]) for k in t["retrieval"]["kept"]],
            "p": p, "gens": sum(1 for e in t.get("events", []) if e.get("kind") == "generation"), "hgScan": (g["classify"](t["question"], turns) or {}).get("cls")}
R = []
H = f"{A}/healthgap/runs/r2"
# 4B probes, HEALTHGAP r2 ON: generation trace if generated, else the ON replay if the layer fired (deterministic), else cut 7 generation (= ON outside fires)
gen_on = {t["itemId"]: t for t in jl(f"{H}/hg2-gen-on-s42.traces.jsonl")}
rep_on = {t["itemId"]: t for t in jl(f"{H}/hg2-replay-probes-on.traces.jsonl")}
c7 = {t["itemId"]: t for t in jl(f"{A}/bonsai2/runs/q2-C-s42.traces.jsonl")}
t2 = {t["itemId"]: t for t in jl(f"{A}/bonsai2/runs/q2-T2-s42.traces.jsonl")}
for i, rt in rep_on.items():
    fired = any(c.startswith("healthgap:") for c in rt["route"]["reasonCodes"])
    if i in gen_on: R.append(row(gen_on[i], "4B", "probes64", "hg2-gen-on"))
    elif fired: R.append(row(rt, "4B", "probes64", "hg2-replay-on(deterministic)"))
    else: R.append(row(c7[i], "4B", "probes64", "q2-C cut7"))
    R.append(row(c7[i], "4B-cut7", "probes64", "q2-C cut7"))
    R.append(row(t2[i], "2B-cut7", "probes64", "q2-T2 cut7"))
    # 2B + HEALTHGAP projected: fired items take the ON route (deterministic, model-independent) except a sourced generation (h21: 2B text not generated -> keep the 2B cut 7 text, flagged)
    if fired and "grounding:health-survival-sourced" not in (gen_on.get(i) or rt)["route"]["reasonCodes"]: R.append(row(rt, "2B+HG", "probes64", "hg2-replay-on(deterministic)"))
    elif fired: r = row(t2[i], "2B+HG", "probes64", "q2-T2 cut7 text, ON route sourced (not generated)"); r["codes"] = (gen_on.get(i) or rt)["route"]["reasonCodes"]; r["kept"] = [(k["title"], k["source"]) for k in (gen_on.get(i) or rt)["retrieval"]["kept"]]; R.append(r)
    else: R.append(row(t2[i], "2B+HG", "probes64", "q2-T2 cut7"))
for t in jl(f"{A}/numguard/runs/v01-ng-off-s42.traces.jsonl"): R.append(row(t, "4B", "v01", "v01-ng-off cut7 (HG fires 0/60)"))
for t in jl(f"{H}/hg2-replay-st-on.traces.jsonl"): R.append(row(t, "4B-replay", "st180", "hg2-replay-st-on (stub text, claim kit)"))
for f in sorted(glob.glob(f"{A}/headpass-st/gen-x2b/st-*-cut7-headpassx2b-s42.traces.jsonl")):
    for t in jl(f): R.append(row(t, "4B+X2b", "st180", os.path.basename(f)))
for f in sorted(glob.glob(f"{A}/lite5/runs/180/lite5-180-on-*-s42.traces.jsonl")):
    for t in jl(f): R.append(row(t, "1.7B+X2b", "st180", os.path.basename(f)))
qs = sorted({r["q"] for r in R})
lex = json.loads(subprocess.run(["node", f"{os.path.dirname(__file__)}/lexicon.mts", f"{ROOT}/kiln-local/be-0cfd4a77-cut7-healthgap"], input=json.dumps(qs), capture_output=True, text=True).stdout)
L = {x["q"]: x for x in lex}
for r in R: r["lexHealth"] = L[r["q"]]["health"]; r["lexSafety"] = L[r["q"]]["safety"]
with open(sys.argv[2], "w") as o:
    for r in R: o.write(json.dumps(r, ensure_ascii=False) + "\n")
import collections; print(len(R), collections.Counter((r["model"], r["set"]) for r in R))
