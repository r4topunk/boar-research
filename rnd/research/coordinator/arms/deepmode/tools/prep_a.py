# DEEPMODE set A prep (0 LLM; frozen with DEEPMODE-criterion.md). Splits the DEEP answers into paragraphs/sentences (para135/tools/para.py = TOPICS27 split.py
# sentence rules), builds each answer's audit context from its own dumped prompts, counts absent numbers, records hit/kept, draws the audit sample.
# Context rule: (1) a single-pass generation (system message holds "\nContext:\n", e.g. the health no-multipass path) -> its context block, as PARA135;
# (2) else the union of the sub-question contexts of the multi-pass research stages (user message "Context:\n" ... "\n\nQuestion: "), deduplicated by the global
# source number [n], ordered by n = every chunk the pipeline read; (3) else the fixed "(no source chunks were given to the model)" string.
# Sample (outcome-blind, depends only on sentence counts per paragraph position): all sentences if <= 430, else stratified by position 1..5, 6+ with
# proportional largest-remainder allocation, >= 1 per non-empty stratum, uniform without replacement numpy default_rng(2048). Output judge/prep.json.
import json, re, sys, collections
import numpy as np
D = "<workspace>/rnd/research/coordinator/arms/deepmode/"; T27 = D + "../topics27/"
sys.path.insert(0, D + "../para135/tools"); from para import paragraphs
topics = json.load(open(T27 + "in/topics.json")); TI = {o["key"]: o for o in json.load(open(T27 + "aggregates/titles.json"))}
NUM = re.compile(r"\d+(?:[.,]\d+)?%?"); BLK = re.compile(r"(?m)^\[(\d+)\] ")
def pos_label(p): return str(p) if p <= 5 else "6+"
def blocks(ctx):
    m = list(BLK.finditer(ctx)); out = []
    for i, x in enumerate(m):
        seg = ctx[x.end(): m[i + 1].start() if i + 1 < len(m) else len(ctx)].rstrip()
        title, _, body = seg.partition("\n"); out.append((int(x.group(1)), title.strip(), body.strip()))
    return out
def stages(prompts):
    """-> dict(kind counts, single ctx or None, sub blocks {n: (title, body)})"""
    kinds = collections.Counter(); single = None; sub = {}
    for d in prompts:
        ms = d.get("messages") or []; sysm = next((m["content"] for m in ms if m["role"] == "system"), d.get("prompt", "") or "")
        user = next((m["content"] for m in ms if m["role"] == "user"), "")
        if sysm.startswith("You plan research."): kinds["decompose"] += 1
        elif "You are synthesizing multiple research perspectives" in sysm: kinds["synthesize"] += 1
        elif "Answer the question in a short paragraph using the context." in sysm:
            kinds["research"] += 1
            if "Context:\n" in user:
                c = user.split("Context:\n", 1)[1].rsplit("\n\nQuestion: ", 1)[0]
                for n, t, b in blocks(c): sub.setdefault(n, (t, b))
        elif "\nContext:\n" in sysm: kinds["single"] += 1; single = sysm.split("\nContext:\n", 1)[1]
        else: kinds["other"] += 1
    return kinds, single, sub
def load(set_, run):
    tr = {json.loads(l)["itemId"]: json.loads(l) for l in open(D + f"gen/{run}/traces.jsonl")}
    pr = collections.defaultdict(list)
    for l in open(D + f"gen/{run}/prompts.jsonl"):
        d = json.loads(l); pr[d["itemId"]].append(d)
    return tr, pr
def context_of(prompts):
    kinds, single, sub = stages(prompts)
    if single is not None: return single, "single", [t for _, t, _ in blocks(single)], kinds
    if sub: return "\n\n".join(f"[{n}] {t}\n{b}" for n, (t, b) in sorted(sub.items())), "multipass", [t for _, (t, _) in sorted(sub.items())], kinds
    return None, "none", [], kinds
if __name__ == "__main__":
    tr, pr = load("a", "dm-a-deep-s42"); units, items = [], []
    for r in topics:
        k = r["key"]; t = tr[k]; text = t["answer"]["text"] or ""
        ctx, src, titles, kinds = context_of(pr.get(k, []))
        anchors = {x.lower() for g in TI[k]["groups"] for x in g}
        banner, paras = paragraphs(text); cl = (ctx or "").lower(); cnums = set(n.rstrip("%").replace(",", "") for n in NUM.findall(cl)); idx = 0
        for pi, ps in enumerate(paras, 1):
            for s in ps:
                na = sum(1 for n in NUM.findall(s) if n.rstrip("%").replace(",", "") not in cnums and not re.fullmatch(r"\[?\d\]?", n))
                units.append(dict(key=f"deep:{k}#{idx}", arm="deep", topic=k, idx=idx, para=pi, pos=pos_label(pi), num_absent=na, question=r["en"],
                                  chunks=ctx if ctx else "(no source chunks were given to the model)", sentence=s)); idx += 1
        tm = t["timing"]; raw = [s["title"] for s in t["retrieval"]["raw"]]; kept = [s["title"] for s in t["retrieval"]["kept"]]
        items.append(dict(key=k, area=r["area"], ctx_src=src, stages=dict(kinds), mode=t["route"].get("mode"), tier=t["route"].get("tier"), banner=banner,
                          n_para=len(paras), n_sent=idx, words=len(text.split()), out_tokens=tm.get("outputTokens"), total_ms=tm.get("totalMs"),
                          retrieval_ms=tm.get("retrievalMs"), declined=t["answer"].get("declined"), read_titles=titles, n_read=len(titles), kept=kept, raw=raw,
                          hit=any(x.lower() in anchors for x in (titles or kept)), in_raw=any(x.lower() in anchors for x in raw),
                          persona_sha=t["runtime"]["versions"].get("persona.sha256"), error=t.get("error")))
    BUDGET = 430
    if len(units) <= BUDGET: sample = [u["key"] for u in units]
    else:
        st = collections.defaultdict(list); [st[u["pos"]].append(u) for u in units]
        keys = sorted(st, key=lambda x: (len(x), x)); q = {s: len(st[s]) * BUDGET / len(units) for s in keys}; a = {s: max(1, int(q[s])) for s in keys}
        while sum(a.values()) < BUDGET:
            s = max((s for s in keys if a[s] < len(st[s])), key=lambda s: (q[s] - a[s], -keys.index(s))); a[s] += 1
        while sum(a.values()) > BUDGET:
            s = max((s for s in keys if a[s] > 1), key=lambda s: (a[s] - q[s], keys.index(s))); a[s] -= 1
        rng = np.random.default_rng(2048); sample = []
        for s in keys: sample += [st[s][i]["key"] for i in sorted(rng.choice(len(st[s]), size=a[s], replace=False))]
    json.dump(dict(units=units, items=items, sample=sample), open(D + "judge/prep.json", "w"), indent=1)
    c = collections.Counter(u["pos"] for u in units); cs = collections.Counter(u["pos"] for u in units if u["key"] in set(sample))
    print("sentences", len(units), "sampled", len(sample), dict(sorted(c.items())), dict(sorted(cs.items())), "hit", sum(i["hit"] for i in items), "ctx", dict(collections.Counter(i["ctx_src"] for i in items)))
