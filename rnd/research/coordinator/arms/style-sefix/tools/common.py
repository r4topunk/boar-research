"""STYLE-SEFIX shared loaders (0 LLM). Cache of judged Haiku rows keyed by (id, text), built exactly as coverage-map/sefix/ans-tools/agg_124.py (read-only sources)."""
import json, glob
A = "<workspace>/rnd/research/coordinator/arms"; CM = A + "/coverage-map"; SF = CM + "/sefix"; D = A + "/style-sefix"
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ld = lambda p: {t["itemId"]: t for t in rd(p)}
ids = open(A + "/lp-screens/main-97.ids").read().split()
KEYS = ("s", "sref", "corr", "declined", "warned")
dim = lambda m, k: sum(m[k].values()) / 3
def jby(JD):
    by = {}
    for f in sorted(glob.glob(JD + "/*.judgments.jsonl")):
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    return by
def jrow(by, i):
    ms = list(by[i].values())
    return dict(s=sum(dim(m, "boar") for m in ms) / 2, sref=sum(dim(m, "ref") for m in ms) / 2, corr=sum(m["boar"]["correctness"] for m in ms) / 2)
def build_cache():
    r42 = json.load(open(SF + "/answers-sefixall.json")); r43 = json.load(open(SF + "/answers-sefixall-s43.json")); pool = json.load(open(A + "/null-cal/control/pool-K1.json"))["items"]
    TG = ld(CM + "/compose/screen/traces/cmp-G-K10-main-s42.traces.jsonl")
    TR = {42: dict(X=ld(SF + "/ans-traces/sefix124-main-s42.traces.jsonl"), F=ld(SF + "/ans-traces/sefixall-main-s42.traces.jsonl")),
          43: dict(X=ld(SF + "/ans-traces/sefix124-main-s43.traces.jsonl"), C=ld(SF + "/ans-traces/ctlk1-main-s43.traces.jsonl"), F=ld(SF + "/ans-traces/sefixall-main-s43.traces.jsonl"))}
    cache = {}
    def put(i, txt, row): cache[(i, txt)] = {k: row.get(k) for k in KEYS}
    for i in ids:
        put(i, pool[i]["text"], r42["rows"]["control"][i]); put(i, TG[i]["answer"]["text"], r42["rows"]["G"][i]); put(i, TR[42]["F"][i]["answer"]["text"], r42["rows"]["ALL"][i])
        for arm, nm in (("C", "ctl"), ("F", "ALL")):
            if r43["items"][i][nm]["judgment"] != "proxy": put(i, TR[43][arm][i]["answer"]["text"], r43["items"][i][nm])
    for s in (42, 43):
        for arm in ("X", "C"):
            NJ = jby(f"{SF}/ans-judge/S124/{s}.{arm}")
            for i, by in NJ.items():
                if len(by) == 2:
                    t = TR[s][arm][i]; row = jrow(NJ, i); row.update(declined=bool(t["answer"].get("declined")), warned=t["answer"]["text"].startswith(W)); put(i, t["answer"]["text"], row)
    return cache
