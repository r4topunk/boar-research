"""WARNSPEC-PATCH v2: the parity goldens for src/routing/warn.test.ts from aggregates/feats.jsonl + aggregates/warnspec.json (0 LLM).
No answer text (REVIEW-warn-patch SHOULD-FIX 6): each row keeps the rule's inputs except the text, which it replaces with
nonEmpty and the reference coverage of the content sentences (tools/warnspec.py coverage()), and kept sources as their host.
HEALTHGAP: traces run without the layer carry the v1.2 scan class (hgScan); the engine emits it as healthgap:<cls>, so it is
written as that code. Rows the layer would take off the model (X2b, hgScan dose/poison/co) carry projected = true and no WARN.
One row per line. Usage: python3 -I mk_warn_goldens.py <arm dir> <out.json>"""
import json, re, sys, io, contextlib
A = sys.argv[1]; OUT = sys.argv[2]
g = {"__name__": "warnspec"}; argv = sys.argv; sys.argv = ["x", f"{A}/aggregates/feats.jsonl", "/dev/null"]
with contextlib.redirect_stdout(io.StringIO()): exec(open(f"{A}/tools/warnspec.py").read(), g)
sys.argv = argv
F = [json.loads(l) for l in open(f"{A}/aggregates/feats.jsonl") if l.strip()]
W = {(r["model"], r["set"], r["id"]): r for r in json.load(open(f"{A}/aggregates/warnspec.json"))["rows"]}
GROUPS = ["4B|probes64", "4B-cut7|probes64", "2B-cut7|probes64", "2B+HG|probes64", "4B|v01", "4B+X2b|st180", "1.7B+X2b|st180"]
KEEP = ("answer:", "detector:", "healthgap:", "grounding:health-")
def host(s):
    m = re.search(r"https?://([^\s/)]+)(/details/army-)?", s or ""); return (m.group(1) + (m.group(2) or "")) if m else ""
out = []
for r in F:
    gname = f'{r["model"]}|{r["set"]}'
    if gname not in GROUPS: continue
    w = W[(r["model"], r["set"], r["id"])]
    codes = [c for c in r["codes"] if c.startswith(KEEP) or c == "instant:final" or "declined" in c]
    if r.get("hgScan") and not any(c.startswith("healthgap:") for c in codes) and not w["hg_projected"]: codes.append(f'healthgap:{r["hgScan"]}')
    unc, n, first = g["coverage"](r)
    # A row no model wrote (or one the layer takes off the model) gets no WARN whatever it kept: its kept list and coverage are not needed.
    if not w["model_generated"] or w["hg_projected"]: r = {**r, "kept": []}; unc, n, first = [], 0, False
    out.append({"g": gname, "id": r["id"], "q": r["q"], "codes": codes, "modelId": r["modelId"], "outcome": r["outcome"], "nonEmpty": bool(r["text"].strip()),
                "kept": [host(s) for _, s in r["kept"]], "cited": len(r["cited"]), "cov": [n, len(unc), first], "projected": w["hg_projected"], "hgScan": r.get("hgScan"), "expect": w["tier"]})
with open(OUT, "w") as o:
    o.write("[\n" + ",\n".join(json.dumps(x, ensure_ascii=False, separators=(",", ":")) for x in out) + "\n]\n")
import collections; print(len(out), collections.Counter(x["g"] for x in out))
