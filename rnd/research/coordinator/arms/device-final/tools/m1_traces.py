#!/usr/bin/env python3
"""DEVICE-FINAL M1 judge inputs (0 LLM; never prints item or answer text): out/df-m1-v04-s<seed>.jsonl (phone rows, one per turn) ->
traces/dev-s<seed>.traces.jsonl in the RULER-FINAL format (native-rc/tools/rf_traces.py): answer = shownText (the chat's streamed text, or the fixed
text no model wrote); multi-turn items joined as [Turn n], a refused turn marked ' [declined]'; refusal z per turn = healthFixed; item z iff every
turn refused. usage: python3 -I m1_traces.py <seed> -> + aggregates/m1-gen-s<seed>.json (paths, latency, speed, memory)"""
import json, os, sys, hashlib, collections, statistics as S
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); seed = sys.argv[1]
rows = [json.loads(l) for l in open(f"{D}/out/df-m1-v04-s{seed}.jsonl") if l.strip()]
by = collections.defaultdict(list)
for r in rows: by[r["queryId"].split("#")[0]].append(r)
order = [json.loads(l)["id"] for l in open("<workspace>/boar-eval/bench/v0.4/items.jsonl")]
def path(r): return "health-fixed" if r.get("healthFixed") else "calc" if r.get("calculated") else "exposure" if r.get("exposureComputed") else "model" if r.get("outcome") == "success" else "error"
out = []; paths = collections.Counter()
for i in order:
    ts = sorted(by.get(i, []), key=lambda r: int(r["queryId"].split("#t")[1]) if "#t" in r["queryId"] else 1)
    if not ts: continue
    zs = [bool(t.get("healthFixed")) for t in ts]; txt = [t.get("shownText") or t.get("answer") or "" for t in ts]; paths.update(path(t) for t in ts)
    ans = txt[0] if len(ts) == 1 else "\n\n".join(f"[Turn {k + 1}]\n{x}{' [declined]' if z else ''}" for k, (x, z) in enumerate(zip(txt, zs)))
    out.append(dict(itemId=i, runId=f"df-m1-v04-s{seed}", answer=dict(text=ans), error=None if all(x.strip() for x in txt) else "empty answer",
                    engine=dict(arm=f"LABRAT-7788924a-pixel8a-s{seed}", commit="7788924a"),
                    ruler=dict(kept=all(len(t.get("retrievedTitles") or []) > 0 for t in ts), keptTurns=[len(t.get("retrievedTitles") or []) > 0 for t in ts],
                               refusedZ=all(zs), refusedTurns=zs, paths=[path(t) for t in ts], nTurns=len(ts), tokens=[t.get("tokensGenerated") for t in ts],
                               capHit=[t.get("stopReason") in ("limit", "length", "max_tokens") for t in ts])))
p = f"{D}/traces/dev-s{seed}.traces.jsonl"; open(p, "w").write("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in out))
m = [r for r in rows if path(r) == "model"]
q = lambda xs, f: round(sorted(xs)[min(len(xs) - 1, int(f * len(xs)))], 1) if xs else None
pick = lambda k, rs=m: [r[k] for r in rs if isinstance(r.get(k), (int, float))]
st = dict(seed=seed, items=len(out), turns=len(rows), missing=[i for i in order if i not in by], sha=hashlib.sha256(open(p, "rb").read()).hexdigest(),
          turn_paths=dict(paths), z_items=sum(x["ruler"]["refusedZ"] for x in out), kept_items=sum(x["ruler"]["kept"] for x in out),
          empty=sum(bool(x["error"]) for x in out), cap_hits=sum(sum(x["ruler"]["capHit"]) for x in out),
          model_turns=dict(n=len(m), total_s_p50=q([v / 1000 for v in pick("totalLatencyMs")], .5), total_s_p90=q([v / 1000 for v in pick("totalLatencyMs")], .9),
                           ttft_s_p50=q([v / 1000 for v in pick("userTtftMs")], .5), ttft_s_p90=q([v / 1000 for v in pick("userTtftMs")], .9),
                           decode_tps_p50=q(pick("decodeTokPerSec"), .5), tokens_p50=q(pick("tokensGenerated"), .5), prompt_tokens_p50=q(pick("promptTokens"), .5),
                           retrieval_s_p50=q([v / 1000 for v in pick("retrievalMs")], .5), peak_rss_gb_max=round(max(pick("peakRssBytes")) / 1e9, 2) if pick("peakRssBytes") else None,
                           batt_c_max=max(pick("batteryTempAfter")) if pick("batteryTempAfter") else None),
          model_load_s=[round(r["modelLoadMs"] / 1000, 1) for r in rows if r.get("modelResidency") == "cold" and r.get("modelLoadMs")])
os.makedirs(f"{D}/aggregates", exist_ok=True); json.dump(st, open(f"{D}/aggregates/m1-gen-s{seed}.json", "w"), indent=1); print(json.dumps(st, indent=1))
