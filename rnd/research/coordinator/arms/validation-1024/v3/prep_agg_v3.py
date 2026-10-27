#!/usr/bin/env python3
"""V3 layer 2 units (0 LLM) and aggregate (V3L2-criterion.md). usage:
  python3 -I prep_agg_v3.py prep <out dir> S=night/fetched/v3-s [SP=night/fetched/v3-splus]   -> <out dir>/units.json (1 unit per follow-up answer = exact A calls)
  python3 -I prep_agg_v3.py agg <out dir> <labels.jsonl>                                          -> <out dir>/v3l2.json + table
Unit: q1 = turn-1 question, a1 = the assistant turn exactly as sent in the turn-2 request history (req/01-turn2), q2 = follow-up, a2 = follow-up answer text,
gold = retbench/items/f8-48.json gold_quote. Final label = A; borderline -> B; A != B (label or on_referent) -> C majority per field; three-way -> A.
Reported per persona: correct-any, on-referent, wrong-unwarned (WRONG_CONFIDENT), wrong-warned, honest-unknown shares (n 48; health = firstaid + medlineplus 16),
plus 0-LLM: follow-up banner/decline rates, kept-source survival (a turn-1 kept title also kept at turn 2), output tokens p50/p90, time p50, prompt tokens p50 turn 1 vs 2."""
import json, sys, os, hashlib, collections
A = "<workspace>/rnd/research/coordinator/arms"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
P48 = json.load(open(A + "/retbench/items/f8-48.json")); G = {x["id"]: x for x in P48}
HEALTH = ("boar-firstaid-en", "boar-medlineplus-en")
q = lambda v, p: sorted(v)[min(len(v) - 1, int(p * len(v)))] if v else None
W = ("Not found in this phone's offline library.", "The passages found don't support this answer.")
if sys.argv[1] == "prep":
    out = sys.argv[2]; units = []; zero = {}
    for tag, d in (a.split("=", 1) for a in sys.argv[3:]):
        T1 = {t["itemId"]: t for t in rd(d + "/out/00-turn1/traces.jsonl")}; T2 = {t["itemId"]: t for t in rd(d + "/out/01-turn2/traces.jsonl")}
        R2 = {r["item"]["id"]: r for r in rd(d + "/req/01-turn2.requests.jsonl")}
        PR2 = collections.defaultdict(str)
        for p in rd(d + "/out/01-turn2/prompts.jsonl"): PR2[p["itemId"]] += json.dumps(p.get("messages") or p.get("prompt"), ensure_ascii=False)
        for x in P48:
            i = x["id"]; h = R2[i]["item"]["history"]["turns"]; a1 = next((t["text"] for t in h if t["role"] == "assistant"), "")
            a2 = T2[i]["answer"]["text"]; key = hashlib.sha256(json.dumps([tag, i, a1, a2]).encode()).hexdigest()[:16]
            k1 = {(c["title"], c["source"]) for c in T1[x["turn1"]]["retrieval"]["kept"]}; k2 = {(c["title"], c["source"]) for c in T2[i]["retrieval"]["kept"]}
            units.append(dict(key=key, tag=tag, id=i, pack=x["pack"], q1=h[0]["text"], a1=a1, q2=T2[i]["question"], a2=a2, gold=x["gold_quote"],
                              z=dict(banner=a2.startswith(W), declined=bool(T2[i]["answer"].get("declined")), kept_survived=bool(k1 & k2), n_kept2=len(k2),
                                     outTok=T2[i]["timing"].get("outputTokens"), totalMs=T2[i]["timing"].get("totalMs"),
                                     pt1=T1[x["turn1"]]["timing"].get("promptTokens"), pt2=T2[i]["timing"].get("promptTokens"),
                                     hist_in_prompt=(json.dumps(a1[:80], ensure_ascii=False)[1:-1] in PR2[i]) if a1 else None)))
    os.makedirs(out, exist_ok=True); json.dump(dict(units=units), open(out + "/units.json", "w"))
    print("units", len(units), "per tag", dict(collections.Counter(u["tag"] for u in units)), "(= exact A calls)")
else:
    out, LF = sys.argv[2], sys.argv[3]; U = json.load(open(out + "/units.json"))["units"]
    L = collections.defaultdict(dict)
    for r in (rd(LF) if os.path.exists(LF) else []):
        if r["ok"]: L[r["key"]][r["call"]] = r
    def final(k):
        c = L.get(k)
        if not c or "A" not in c: return None, None
        a = c["A"]
        if a["conf"] != "borderline" or "B" not in c or ((c["B"]["label"], c["B"]["on_referent"]) == (a["label"], a["on_referent"])) or "C" not in c: return a["label"], a["on_referent"]
        v = [c[x] for x in "ABC"]
        lab = collections.Counter(x["label"] for x in v).most_common(1)[0]; ref = collections.Counter(x["on_referent"] for x in v).most_common(1)[0]
        return (lab[0] if lab[1] > 1 else a["label"]), ref[0]
    res = {}
    for tag in sorted({u["tag"] for u in U}):
        for sub, f in (("all", lambda u: True), ("health", lambda u: u["pack"] in HEALTH), ("non-health", lambda u: u["pack"] not in HEALTH)):
            us = [u for u in U if u["tag"] == tag and f(u)]; n = len(us); fl = [final(u["key"]) for u in us]; c = collections.Counter(l for l, _ in fl)
            sh = lambda k: round(k / n, 3) if n else None
            res[f"{tag}|{sub}"] = dict(n=n, unlabelled=c.get(None, 0), correct_any=sh(c["CORRECT"]), on_referent=sh(sum(r is True for _, r in fl)),
                                       wrong_unwarned=sh(c["WRONG_CONFIDENT"]), wrong_warned=sh(c["WRONG_WARNED"]), honest_unknown=sh(c["HONEST_UNKNOWN"]),
                                       banner=sh(sum(u["z"]["banner"] for u in us)), declined=sh(sum(u["z"]["declined"] for u in us)), kept_survived=sh(sum(u["z"]["kept_survived"] for u in us)),
                                       out_tokens_p50=q([u["z"]["outTok"] or 0 for u in us], .5), out_tokens_p90=q([u["z"]["outTok"] or 0 for u in us], .9),
                                       time_ms_p50=q([u["z"]["totalMs"] for u in us if u["z"]["totalMs"]], .5),
                                       prompt_tokens_p50_turn1=q([u["z"]["pt1"] for u in us if u["z"]["pt1"]], .5), prompt_tokens_p50_turn2=q([u["z"]["pt2"] for u in us if u["z"]["pt2"]], .5),
                                       history_in_prompt=f"{sum(u['z']['hist_in_prompt'] is True for u in us)}/{sum(u['z']['hist_in_prompt'] is not None for u in us)}")
    json.dump(res, open(out + "/v3l2.json", "w"), indent=1)
    for k, v in res.items(): print(k, v)
