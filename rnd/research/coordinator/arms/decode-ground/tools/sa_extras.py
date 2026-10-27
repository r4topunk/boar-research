#!/usr/bin/env python3
"""DG-SA extras (0 LLM): citation rate vs control, warned, changed, NO_EVIDENCE vs S1, picks, tokens/time. Usage: python3 -I sa_extras.py  -> aggregates/sa-summary.json + markdown."""
import json
H = "<workspace>/rnd/research/coordinator/arms/decode-ground"; A = H + "/.."; R = A + "/.."
ld = lambda p: {json.loads(l)["itemId"]: json.loads(l) for l in open(p)}
FN = json.load(open(R + "/ruler/RAG-FUNNEL-2026-10-21.json"))["items"]
sc = json.load(open(A + "/null-cal/pool/screen2-K1.json")); P, S = sc["problems"], sc["sentinels"]
ctl = {}
for f in (A + "/lp-screens/control/traces/lpctl-K1-main-s42.traces.jsonl", A + "/null-cal/control/traces/poolctl-K1-st180-s42.traces.jsonl"): ctl.update(ld(f))
ctlj = json.load(open(A + "/null-cal/control/pool-K1.json"))["items"]
sT = ld(f"{H}/screens/SA/traces/dg-SA-screen2-K1-s42.traces.jsonl"); sAg = json.load(open(f"{H}/screens/SA/aggregates/dg-SA-screen2-K1-s42.json"))["items"]
M = ld(f"{H}/runs/traces/dg-SA-K1-main-s42.traces.jsonl")
Sold = ld(f"{H}/screens/S/traces/dg-S-screen2-K1-s42.traces.jsonl"); Mold = ld(f"{H}/runs/traces/dg-S-K1-main-s42.traces.jsonl")
cit = lambda t: bool(t["answer"]["cited"])
def rate(T, ids):
    c = [i for i in ids if cit(ctl[i])]; return dict(n_ctl_cited=len(c), cand_cited_of_those=sum(cit(T[i]) for i in c), cand_cited_all=sum(cit(T[i]) for i in ids), ctl_cited_all=sum(cit(ctl[i]) for i in ids), n=len(ids))
out = {"screen41": {"SA": rate(sT, P + S), "S": rate(Sold, P + S)}, "main97": {"SA": rate(M, list(M)), "S": rate(Mold, list(M))}}
live = [i for i in M if (M[i]["retrieval"].get("dg") or {}).get("select")]
out["main97"]["live_with_menu"] = len(live)
mc = [i for i in M if (ctl[i]["timing"].get("outputTokens") or 0) > 0]
# the 23 MAIN items of the coordinator's finding: control cited, S lost the citation
lost = [i for i in M if cit(ctl[i]) and not cit(Mold[i])]
out["main97"]["S_lost_of_ctl_cited"] = len(lost); out["main97"]["SA_kept_on_those"] = sum(cit(M[i]) for i in lost)
for nm, T, ids in (("screen41", sT, P + S), ("main97", M, list(M))):
    w = [i for i in ids if "Not found in this phone" in T[i]["answer"]["text"]]
    out[nm]["warned_text_SA"] = len(w); out[nm]["warned_text_ctl"] = sum("Not found in this phone" in ctl[i]["answer"]["text"] for i in ids)
    out[nm]["changed_vs_ctl"] = sum(T[i]["answer"]["text"] != (ctlj[i]["text"]) for i in ids)
dgs = lambda t: (t["retrieval"].get("dg") or {}).get("select") or {}
out["main97"]["no_evidence"] = sum("dg:no-evidence" in t["route"]["reasonCodes"] for t in M.values())
out["main97"]["picks_in_dropped"] = sum(bool(dgs(t).get("inDropped")) for t in M.values()); out["main97"]["picks_in_kept"] = sum(bool(dgs(t).get("inKept")) for t in M.values())
out["screen41"]["no_evidence"] = sum("dg:no-evidence" in t["route"]["reasonCodes"] for t in sT.values()); out["screen41"]["picks_in_dropped"] = sum(bool(dgs(t).get("inDropped")) for t in sT.values())
s1 = {i for i, v in FN.items() if (v.get("K1") or {}).get("vstage") == "S1"}
ne = [i for i, t in M.items() if "dg:no-evidence" in t["route"]["reasonCodes"]]
out["main97"]["ne_in_S1"] = sum(i in s1 for i in ne)
# answers where the first source is the pick and the pick was not already first in the control's kept
out["main97"]["answers_equal_to_ctl_with_pick"] = sum(1 for i, t in M.items() if dgs(t) and t["answer"]["text"] == ctlj[i]["text"])
json.dump(out, open(H + "/aggregates/sa-summary.json", "w"), indent=1); print(json.dumps(out, indent=1))
