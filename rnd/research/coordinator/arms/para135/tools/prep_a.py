# PARA135 set A prep (0 LLM; frozen with PARA135-criterion.md): split the 3 arms' answers into paragraphs/sentences (tools/para.py), attach each answer's own
# dumped context (TOPICS27 prep.py rule; replay keptFull fallback; else the fixed no-chunks string), count absent numbers, and draw the audit sample.
# Sample (outcome-blind: depends only on sentence counts per paragraph position, never on text or labels): budget 430 primary calls (cap 450 incl. retries).
# Arm p1 first: all sentences if <= 150 else a stratified sample of 150; the remainder is split p3 = floor(R/2), p5 = R - p3; an arm whose sentences fit its
# budget is audited in full and its slack moves to the other arm (p5 first). Strata = paragraph position 1, 2, 3, 4, 5, 6+; proportional allocation by largest
# remainder, every non-empty stratum gets >= 1; within a stratum uniform without replacement, numpy default_rng(135 + N). Output judge/prep.json.
import json, re, sys
import numpy as np
sys.path.insert(0, "tools"); from para import paragraphs
T27 = "../topics27/"
rp = {json.loads(l)["id"]: json.loads(l) for l in open(T27 + "replay/t27.replay.jsonl")}
topics = json.load(open(T27 + "in/topics.json"))
NUM = re.compile(r"\d+(?:[.,]\d+)?%?")
def pos_label(p): return str(p) if p <= 5 else "6+"
out = {"arms": {}}
for N in (1, 3, 5):
    run = f"p135-a-p{N}-s42"
    tr = {json.loads(l)["itemId"]: json.loads(l) for l in open(f"gen/{run}/traces.jsonl")}
    pr = {}
    for l in open(f"gen/{run}/prompts.jsonl"):
        d = json.loads(l); pr.setdefault(d["itemId"], []).append(d)
    units, items = [], []
    for r in topics:
        k = r["key"]; t = tr[k]; text = t["answer"]["text"] or ""; ctx, src = None, None
        for d in reversed(pr.get(k, [])):
            sysm = next((m["content"] for m in d.get("messages", []) if m["role"] == "system"), d.get("prompt", ""))
            if "\nContext:\n" in sysm: ctx = sysm.split("\nContext:\n", 1)[1]; src = "dump"; break
        if ctx is None and rp[k]["keptFull"]:
            ctx = "\n\n".join(f"[{i+1}] {c['title']}\n{c['body']}" for i, c in enumerate(rp[k]["keptFull"])); src = "replay"
        banner, paras = paragraphs(text)
        cl = (ctx or "").lower(); cnums = set(n.rstrip("%").replace(",", "") for n in NUM.findall(cl))
        idx = 0
        for pi, ps in enumerate(paras, 1):
            for s in ps:
                na = sum(1 for n in NUM.findall(s) if n.rstrip("%").replace(",", "") not in cnums and not re.fullmatch(r"\[?\d\]?", n))
                units.append(dict(key=f"p{N}:{k}#{idx}", arm=f"p{N}", topic=k, idx=idx, para=pi, pos=pos_label(pi), num_absent=na, question=r["en"],
                                  chunks=ctx if ctx else "(no source chunks were given to the model)", sentence=s)); idx += 1
        tm = t["timing"]
        items.append(dict(key=k, area=r["area"], ctx_src=src, banner=banner, n_para=len(paras), n_sent=idx, words=len(text.split()),
                          out_tokens=tm.get("outputTokens"), total_ms=tm.get("totalMs"), declined=t["answer"].get("declined"),
                          kept=[s["title"] for s in t["retrieval"]["kept"]], persona_sha=t["runtime"]["versions"].get("persona.sha256")))
    out["arms"][f"p{N}"] = dict(units=units, items=items)
BUDGET = 430
def alloc(units, b, N):
    if len(units) <= b: return [u["key"] for u in units]
    strata = {}
    for u in units: strata.setdefault(u["pos"], []).append(u)
    keys = sorted(strata, key=lambda x: (len(x), x)); tot = len(units)
    q = {s: len(strata[s]) * b / tot for s in keys}; a = {s: max(1, int(q[s])) for s in keys}
    while sum(a.values()) < b:
        s = max((s for s in keys if a[s] < len(strata[s])), key=lambda s: (q[s] - a[s], -keys.index(s))); a[s] += 1
    while sum(a.values()) > b:
        s = max((s for s in keys if a[s] > 1), key=lambda s: (a[s] - q[s], keys.index(s))); a[s] -= 1
    rng = np.random.default_rng(135 + N); pick = []
    for s in keys:
        ix = rng.choice(len(strata[s]), size=a[s], replace=False); pick += [strata[s][i]["key"] for i in sorted(ix)]
    return pick
U = {a: out["arms"][a]["units"] for a in ("p1", "p3", "p5")}
b1 = min(150, len(U["p1"])); R = BUDGET - b1
b3, b5 = R // 2, R - R // 2
if len(U["p5"]) < b5: b3 += b5 - len(U["p5"]); b5 = len(U["p5"])
if len(U["p3"]) < b3: b5 = min(len(U["p5"]), b5 + b3 - len(U["p3"])); b3 = len(U["p3"])
out["budget"] = {"p1": b1, "p3": b3, "p5": b5}
out["sample"] = {"p1": alloc(U["p1"], b1, 1), "p3": alloc(U["p3"], b3, 3), "p5": alloc(U["p5"], b5, 5)}
json.dump(out, open("judge/prep.json", "w"), indent=1)
for a in ("p1", "p3", "p5"):
    import collections
    c = collections.Counter(u["pos"] for u in U[a]); cs = collections.Counter(u["pos"] for u in U[a] if u["key"] in set(out["sample"][a]))
    print(a, "sentences", len(U[a]), "budget", out["budget"][a], "by pos", dict(sorted(c.items())), "sampled", dict(sorted(cs.items())))
