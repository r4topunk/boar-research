#!/usr/bin/env python3
"""WARN-KEPT (0 LLM). python3 -I warnkept.py -> ../warnkept.json (+ stdout). Rules per WARN-KEPT-criterion.md (sha d5b5436d)."""
import json, re, glob, os
U = "<workspace>/rnd/research/coordinator/arms/uxmatrix"; SF = "<workspace>/rnd/research/coordinator/arms/coverage-map/sefix"
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
STOP = set("the this that these those it in on at for and but or if when while with from to by as yes no however also not found model".split())
def body(text):
    t = text[len(W):] if text.startswith(W) else text
    return re.sub(r"\s*\[\d+\]", "", t).strip()
def specifics(text, question):
    b = body(text); qt = {w.lower() for w in re.findall(r"[A-Za-z0-9][\w'\-]*", question)}
    nums = [n.replace(",", "").replace(" ", "") for n in re.findall(r"\d[\d, ]*(?:\.\d+)?", b)]
    nums = [n.rstrip(".") for n in nums if n]
    names = []
    for sent in re.split(r"(?<=[.!?:])\s+|\n+", b):
        toks = re.findall(r"[A-Za-zÀ-ɏ][\w'\-À-ɏ]*", sent)
        for k, w in enumerate(toks):
            if k == 0 or len(w) < 3 or not w[0].isupper(): continue
            if w.lower() in STOP or w.lower() in qt: continue
            names.append(w)
    return list(dict.fromkeys(nums)), list(dict.fromkeys(names))
def present(spec, chunk, isnum):
    c = chunk.replace(",", "").replace(" ", "") if isnum else chunk
    return re.search(r"(?<![\w.])" + re.escape(spec) + r"(?![\w])" if isnum else r"\b" + re.escape(spec) + r"\b", c, re.I) is not None
def decide(text, question, cited_text, has_cite):
    nums, names = specifics(text, question)
    warned = text.startswith(W)
    pn = [present(n, cited_text, True) for n in nums]; pm = [present(n, cited_text, False) for n in names]
    allp = pn + pm; share = sum(allp) / len(allp) if allp else None
    base = (not warned) and has_cite
    return dict(nums=nums, names=names, n_spec=len(allp), share=share, missing=[s for s, p in zip(nums + names, allp) if not p],
                R=base and bool(allp) and share < 0.5, R_any=base and bool(allp) and not all(allp), R_num=base and bool(pn) and sum(pn) / len(pn) < 0.5)
def blocks(prompts):
    out = []
    for p in prompts:
        for m in p["messages"]:
            if m["role"] != "system" or "\nContext:\n" not in m["content"]: continue
            for b in re.split(r"\n\n(?=\[\d+\] )", m["content"].split("\nContext:\n", 1)[1].strip()):
                mm = re.match(r"\[\d+\] ([^\n]*)\n?(.*)", b, re.S)
                if mm: out.append((mm.group(1).strip(), mm.group(2).strip()))
    return out
def why(t, cited):
    rc = t["route"]["reasonCodes"]
    if cited: return "cited-kept"
    if any(c.startswith("grounding:health") or c.startswith("grounding:fa-card") for c in rc): return "health-route"
    return "other-uncited"
ux = json.load(open(U + "/aggregates/uxmatrix.json"))["per_item"]
res = {"criterion_sha256": open(U + "/WARN-KEPT-criterion.sha256").read().split()[0], "A": {}, "B": {}}
rowsA = []
for mode in ("succinct", "detailed"):
    for d in sorted(glob.glob(f"{U}/gen/{mode}/*/")):
        g = os.path.basename(d.rstrip("/")); st = "on" if g == "on" else "off"
        PR = {}
        for p in rd(d + "prompts.jsonl"): PR.setdefault(p["itemId"], []).append(p)
        for t in rd(d + "traces.jsonl"):
            i = t["itemId"]; a = t["answer"]; cited = list(a.get("cited") or []); lab = ux[f"{mode}|{st}|{i}"]["label"]
            bl = blocks(PR.get(i, [])); ctext = "\n".join(b for ti, b in bl if ti in cited)
            dd = decide(a["text"], t["question"], ctext, bool(cited))
            rc = t["route"]["reasonCodes"]
            rowsA.append(dict(mode=mode, state=st, id=i, cls=ux[f"{mode}|{st}|{i}"]["cls"], label=lab, warned=a["text"].startswith(W), cited=cited, n_shown=len(a.get("shown") or []),
                              cite_origin=("engine-attributed" if any(c.startswith("citations:added") for c in rc) else "model") if cited else None,
                              removed=[c for c in rc if c.startswith("citations:removed")], release=[c for c in rc if "released" in c or c.startswith("grounding:uncited") or c.startswith("grounding:health")],
                              why=why(t, cited), cited_chars=len(ctext), text=a["text"][:300], **dd))
# Set B: exec agg_124.py unchanged up to the row build
src = open(SF + "/ans-tools/agg_124.py").read(); src = src[:src.index("def U(src, xs)")]
ns = {"__name__": "agg124"}; exec(compile(src, "agg_124.py", "exec"), ns)
SX = ns["S"][42]["X"]; TX = ns["TR"][42]["X"]; ids = ns["ids"]
REP = {r["id"]: r for r in rd(SF + "/replays/main.F1F2F4.jsonl")}
rowsB = []
for i in ids:
    t = TX[i]; a = t["answer"]; r = SX[i]; cited = list(a.get("cited") or [])
    rep = REP[i]; parity = [k["title"] for k in t["retrieval"]["kept"]] == [k["title"] for k in rep["keptFull"]]
    ctext = "\n".join(k["body"] for k in rep["keptFull"] if k["title"] in cited)
    missing_cited = [c for c in cited if c not in {k["title"] for k in rep["keptFull"]}]
    dd = decide(a["text"], t["question"], ctext, bool(cited)); rc = t["route"]["reasonCodes"]
    rowsB.append(dict(id=i, corr=r["corr"], declined=r["declined"], warned=r["warned"], judgment=r["judgment"], CE=r["CE"], parity=parity, missing_cited=missing_cited,
                      cited=cited, cite_origin=("engine-attributed" if any(c.startswith("citations:added") for c in rc) else "model") if cited else None,
                      removed=[c for c in rc if c.startswith("citations:removed")], release=[c for c in rc if "released" in c or c.startswith("grounding:uncited") or c.startswith("grounding:health")],
                      why=why(t, cited), text=a["text"][:300], **dd))
def gate(rows, wu, cor):
    W_ = [r for r in rows if wu(r)]; C_ = [r for r in rows if cor(r)]
    out = {}
    for k in ("R", "R_any", "R_num"):
        out[k] = dict(WU=len(W_), WU_warned=sum(r[k] for r in W_), recall=round(sum(r[k] for r in W_) / len(W_), 3) if W_ else None,
                      correct=len(C_), correct_warned=sum(r[k] for r in C_), cost=round(sum(r[k] for r in C_) / len(C_), 3) if C_ else None,
                      fires=sum(r[k] for r in rows), n=len(rows))
    return out
wcA = lambda r: r["label"] == "WRONG_CONFIDENT"; corA = lambda r: r["label"] in ("CORRECT_WITH_SOURCE", "CORRECT_FROM_MEMORY")
for st in ("on", "off"):
    rs = [r for r in rowsA if r["state"] == st]
    res["A"][st] = dict(all=gate(rs, wcA, corA), **{m: gate([r for r in rs if r["mode"] == m], wcA, corA) for m in ("succinct", "detailed")})
res["B"]["primary"] = gate(rowsB, lambda r: r["CE"] and not r["warned"], lambda r: (not r["declined"]) and r["corr"] >= 3.5)
res["B"]["sens_noncE"] = gate(rowsB, lambda r: r["CE"] and not r["warned"], lambda r: (not r["declined"]) and r["corr"] > 1.5)
res["B"]["flags"] = dict(proxy=sum(r["judgment"] == "proxy" for r in rowsB), parity_false=sum(not r["parity"] for r in rowsB), cited_title_missing=sum(bool(r["missing_cited"]) for r in rowsB))
pA = res["A"]["on"]["all"]["R"]; pB = res["B"]["primary"]["R"]
res["verdict"] = "LEVER-CANDIDATE" if all(x["recall"] is not None and x["recall"] >= 0.5 and x["cost"] <= 0.15 for x in (pA, pB)) else "NO"
res["rowsA"] = rowsA; res["rowsB"] = rowsB
json.dump(res, open(U + "/warnkept.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in res.items() if not k.startswith("rows")}, indent=1))
