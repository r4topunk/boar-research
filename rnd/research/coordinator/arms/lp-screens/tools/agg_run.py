#!/usr/bin/env python3
"""LP-SCREENS per-run aggregate (0 LLM). Usage: python3 -I agg_run.py <traces.jsonl> <ids file> <out.json> <judgments glob> [--control <control agg.json>]
Per item (agg.py definitions, LITEPACKS): s = mean of the 3 judge dims averaged over both orders; sref likewise; corr = correctness averaged over orders;
declined = trace answer.declined; CE = not declined and corr <= 1.5; warned = text starts with the CMP30OFF warning line; refusal_like = declined or a
short (< 300 chars) answer matching a don't-know pattern. Items whose answer text is byte-identical to the control's reuse the control's judgment
(LITEPACKS rule; they are not re-judged). Summary: Q = sum s / sum sref, U = Q with s := 0 for declined, CE count/rate, decline, warned.
With --control: paired deltas (cand - control) for U, Q, CE, decline with item bootstrap B 2000 seed 11 (2.5/97.5 pct), changed-answer count."""
import json, sys, glob, re, random
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
RX = re.compile(r"\b(i (do not|don't) know|i'?m not sure|i cannot answer|i can'?t answer|i don'?t have (enough |reliable )?information|not able to answer)\b", re.I)
a = sys.argv[1:]; ctl = None
if "--control" in a: k = a.index("--control"); ctl = json.load(open(a[k + 1])); a = a[:k] + a[k + 2:]
TRF, IDF, OUT, JG = a[:4]
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
TR = {t["itemId"]: t for t in rd(TRF)}; ids = [x for x in open(IDF).read().split() if x]
by = {}
for f in sorted(glob.glob(JG)):
    for r in rd(f):
        if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
items, missing = {}, []
for i in ids:
    t = TR[i]; txt = t["answer"]["text"]; d = bool(t["answer"].get("declined"))
    c = ctl["items"].get(i) if ctl else None
    if c and c["text"] == txt: j = dict(s=c["s"], sref=c["sref"], corr=c["corr"]); src = "control"
    elif i in by and len(by[i]) == 2:
        ms = list(by[i].values()); mean = lambda x: sum(x.values()) / 3
        j = dict(s=sum(mean(m["boar"]) for m in ms) / 2, sref=sum(mean(m["ref"]) for m in ms) / 2, corr=sum(m["boar"]["correctness"] for m in ms) / 2); src = "judged"
    else: missing.append(i); continue
    items[i] = dict(j, text=txt, declined=d, CE=(not d and j["corr"] <= 1.5), warned=txt.startswith(W), refusal_like=d or (len(txt) < 300 and bool(RX.search(txt))),
                    errored=bool(t.get("error")), judgment=src)
if missing: sys.exit(f"MISSING judgments for {len(missing)} ids: {','.join(missing)}")
def summ(xs):
    it = [items[i] for i in xs]; sr = sum(x["sref"] for x in it); nd = [x for x in it if not x["declined"]]
    return dict(n=len(it), Q=sum(x["s"] for x in it) / sr, U=sum(0 if x["declined"] else x["s"] for x in it) / sr, ce_count=sum(x["CE"] for x in it),
                CE=sum(x["CE"] for x in it) / len(nd) if nd else 0.0, decline=sum(x["declined"] for x in it) / len(it), refusal_like=sum(x["refusal_like"] for x in it),
                warned=sum(x["warned"] for x in it), corr_mean=sum(x["corr"] for x in it) / len(it))
res = dict(traces=TRF, n=len(ids), summary=summ(ids), items=items, judged_here=sum(x["judgment"] == "judged" for x in items.values()))
if ctl:
    common = [i for i in ids if i in ctl["items"]]
    def m(src, xs):
        it = [src[i] for i in xs]; sr = sum(x["sref"] for x in it); nd = [x for x in it if not x["declined"]]
        return dict(U=sum(0 if x["declined"] else x["s"] for x in it) / sr, Q=sum(x["s"] for x in it) / sr, CE=sum(x["CE"] for x in it) / len(nd) if nd else 0.0,
                    decline=sum(x["declined"] for x in it) / len(it))
    rnd = random.Random(11); B = 2000; bs = {k: [] for k in ("U", "Q", "CE", "decline")}
    for _ in range(B):
        s = [rnd.choice(common) for _ in common]; x, y = m(items, s), m(ctl["items"], s)
        for k in bs: bs[k].append(x[k] - y[k])
    x, y = m(items, common), m(ctl["items"], common)
    res["vs_control"] = dict(n=len(common), changed_answers=sum(items[i]["text"] != ctl["items"][i]["text"] for i in common),
                             deltas={k: dict(d=round(x[k] - y[k], 4), ci=[round(sorted(v)[int(0.025 * B)], 4), round(sorted(v)[int(0.975 * B) - 1], 4)]) for k, v in bs.items()},
                             ce_count=[sum(items[i]["CE"] for i in common), sum(ctl["items"][i]["CE"] for i in common)])
json.dump(res, open(OUT, "w"), indent=1, ensure_ascii=False)
s = res["summary"]; print(f"{OUT.split('/')[-1]}: n={s['n']} U={s['U']:.4f} Q={s['Q']:.4f} CE={s['ce_count']} ({s['CE']:.3f}) declined={s['decline']:.3f} refusal_like={s['refusal_like']} warned={s['warned']} judged_here={res['judged_here']}")
if ctl: print("vs control:", json.dumps(res["vs_control"]))
