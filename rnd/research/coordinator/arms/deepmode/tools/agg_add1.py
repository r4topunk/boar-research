# DEEPMODE Addendum 1 (coordinator request after the freeze; 0 LLM, 0 extra Haiku). python3 -I tools/agg_add1.py
# (a) sub-questions per item: on-topic = shares >= 1 content word (>= 4 letters, not a stopword, 5-letter prefix match) with the question, or (set A) names an
#     expected/anchor title; Jaccard of content-word prefixes; chunks read by the pass that first introduced them (sub-question 1 vs 2-3).
# (b) PARA135 arm of matched length (output tokens p50 closest to DEEP's, per set): set A unsupported / invented; set B U and paired dU.
import json, re, sys, collections, numpy as np
A = "<workspace>/rnd/research/coordinator/arms/"; D = A + "deepmode/"; P135 = A + "para135/"
sys.path.insert(0, D + "tools"); from prep_a import blocks, load as loadgen
STOP = set("what which when where while does with from that this these those their there have into about between them they than then were your how why who whom whose role "
           "explain describe compare difference differ main some other more most also each such like over under after before during against being".split())
def cw(s): return {w[:5] for w in re.findall(r"[a-z][a-z'-]{3,}", s.lower()) if w not in STOP}
def subs(prompts):
    out = []; seen = set()
    for d in prompts:
        ms = d.get("messages") or []; sysm = next((m["content"] for m in ms if m["role"] == "system"), ""); user = next((m["content"] for m in ms if m["role"] == "user"), "")
        if "Answer the question in a short paragraph using the context." not in sysm: continue
        q = user.rsplit("Question: ", 1)[-1].strip(); ns = []
        if "Context:\n" in user:
            ns = [n for n, _, _ in blocks(user.split("Context:\n", 1)[1].rsplit("\n\nQuestion: ", 1)[0])]
        new = [n for n in ns if n not in seen]; seen.update(ns); out.append(dict(sub=q, read=len(ns), new=len(new)))
    return out
TI = {o["key"]: o for o in json.load(open(A + "topics27/aggregates/titles.json"))}
res = {}
for S, run in (("A", "dm-a-deep-s42"), ("B", "dm-b-deep-s42")):
    tr, pr = loadgen(S.lower(), run); rows = {}
    for k, t in tr.items():
        qw = cw(t["question"] if isinstance(t.get("question"), str) else t["question"]["text"] if isinstance(t.get("question"), dict) else "")
        titles = [x for g in TI[k]["groups"] for x in g] if S == "A" else []
        ss = subs(pr.get(k, []))
        for s in ss:
            sw = cw(s["sub"]); s["overlap"] = len(sw & qw); s["jaccard"] = round(len(sw & qw) / len(sw | qw), 3) if sw | qw else 0.0
            s["names_title"] = any(x.lower() in s["sub"].lower() for x in titles); s["on_topic"] = s["overlap"] >= 1 or s["names_title"]
        rows[k] = dict(question_words=sorted(qw), subs=ss)
    allss = [s for r in rows.values() for s in r["subs"]]; mp = [r for r in rows.values() if r["subs"]]
    first = sum(r["subs"][0]["new"] for r in mp); extra = sum(s["new"] for r in mp for s in r["subs"][1:])
    res[S] = dict(items=len(rows), multipass_items=len(mp), subq_total=len(allss), subq_per_item=dict(collections.Counter(len(r["subs"]) for r in rows.values())),
                  on_topic=sum(s["on_topic"] for s in allss), on_topic_share=round(sum(s["on_topic"] for s in allss) / len(allss), 3) if allss else None,
                  off_topic_examples=[(k, s["sub"]) for k, r in rows.items() for s in r["subs"] if not s["on_topic"]][:12],
                  jaccard_mean=round(float(np.mean([s["jaccard"] for s in allss])), 3) if allss else None,
                  subq_reading_nothing=sum(s["read"] == 0 for s in allss), chunks_first_pass=first, chunks_extra_passes=extra,
                  extra_share=round(extra / (first + extra), 3) if first + extra else None,
                  items_all_chunks_from_extra=sum(1 for r in mp if r["subs"][0]["new"] == 0 and sum(s["new"] for s in r["subs"][1:]) > 0), per_item=rows)
# (b) matched length
dA = json.load(open(D + "aggregates/setA.json")); dB = json.load(open(D + "aggregates/setB.json"))
pA = json.load(open(P135 + "aggregates/setA.json")); pB = json.load(open(P135 + "aggregates/setB.json"))
otA = dA["deep"]["total"]["out_tokens_p50"]; mA = min(("p1", "p3", "p5"), key=lambda a: abs(pA["arms"][a]["total"]["out_tokens_p50"] - otA))
otB = dB["arms"]["DEEP"]["out_tokens_p50"]; mB = min(("p1", "p3", "p5"), key=lambda a: abs(pB["arms"][a]["out_tokens_p50"] - otB))
tA = pA["arms"][mA]["total"]; dt = dA["deep"]["total"]
matchA = dict(arm=mA, deep_out_p50=otA, arm_out_p50=tA["out_tokens_p50"], deep_unsup=dt["unsup_share_est"], arm_unsup=tA["unsup_share_est"],
              deep_invented_est=dt["invented_est"], arm_invented_est=tA["invented_est"], deep_sentences=dt["sentences"], arm_sentences=tA["sentences"],
              deep_invented_per_sentence=round(dt["invented_est"] / dt["sentences"], 3), arm_invented_per_sentence=round(tA["invented_est"] / tA["sentences"], 3))
# set B paired vs the matched arm (PARA135 rows; identical texts to S17 reuse the K1 control rows, as PARA135 agg_b.py)
src = open(D + "tools/agg_b.py").read().split("# chunk-level delivered facts")[0]
g = {"__name__": "agg_b_head"}; exec(src.replace('json.dump(', '(lambda *a, **k: None)('), g)
TRm = {(j := json.loads(l)).get("itemId"): j for l in open(P135 + f"gen/p135-b-{mB}-s42/traces.jsonl")}
g["TR"]["M"] = TRm; g["TX"]["M"] = {q: TRm[q]["answer"]["text"] or "" for q in g["ids"]}
g["H"]["M"] = g["hk"]([P135 + f"judge/b/p135-b-{mB}-s42-v01.judgments.jsonl"], "M")
matchB = dict(arm=mB, deep_out_p50=otB, arm_out_p50=pB["arms"][mB]["out_tokens_p50"], arm_U=g["lv"]("M")["U"], deep_U=dB["arms"]["DEEP"]["U"],
              arm_ce_per100=pB["arms"][mB]["ce_per100"], deep_ce_per100=dB["arms"]["DEEP"]["ce_per100"], DEEP_vs_arm=g["pair"]("DEEP", "M"))
out = dict(subqueries=res, matched_length=dict(setA=matchA, setB=matchB))
json.dump(out, open(D + "aggregates/addendum1.json", "w"), indent=1)
print(json.dumps({S: {k: v for k, v in r.items() if k != "per_item"} for S, r in res.items()}, indent=1)); print(json.dumps(out["matched_length"], indent=1))
