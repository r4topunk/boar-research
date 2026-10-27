#!/usr/bin/env python3
"""DG stage-1 summary (0 LLM): per arm gate line numbers + extras + MAIN-97 sanity + NO_EVIDENCE vs S1 label. Writes aggregates/stage1-summary.json and prints markdown rows."""
import json, re, collections
H = "<workspace>/rnd/research/coordinator/arms/decode-ground"; A = H + "/.."; R = A + "/.."
ld = lambda p: {json.loads(l)["itemId"]: json.loads(l) for l in open(p)}
FN = json.load(open(R + "/ruler/RAG-FUNNEL-2026-10-21.json"))["items"]
sc = json.load(open(A + "/null-cal/pool/screen2-K1.json")); P, S = sc["problems"], sc["sentinels"]
ctl = {}
for f in (A + "/lp-screens/control/traces/lpctl-K1-main-s42.traces.jsonl", A + "/null-cal/control/traces/poolctl-K1-st180-s42.traces.jsonl"): ctl.update(ld(f))
CJK = re.compile(r"[぀-ヿ㐀-鿿가-힯]")
arms = [("S", "S", "S"), ("SB", "SB", "SBb4"), ("SCp01", "SC", "SCp01"), ("C1p01", "C1", "C1p01")]
out = {}
for d, code, mainrun in arms:
    g = json.load(open(f"{H}/screens/{d}/aggregates/dg-{d}-screen2-K1-s42.gate2.json"))
    ag = json.load(open(f"{H}/screens/{d}/aggregates/dg-{d}-screen2-K1-s42.json"))["items"]
    T = ld(f"{H}/screens/{d}/traces/dg-{d}-screen2-K1-s42.traces.jsonl")
    sn = json.load(open(f"{H}/aggregates/sanity-main-{mainrun}.json"))
    M = ld(f"{H}/runs/traces/dg-{mainrun}-K1-main-s42.traces.jsonl")
    ne = [i for i in P + S if "dg:no-evidence" in T[i]["route"]["reasonCodes"]]
    dgs = lambda t: (t["retrieval"].get("dg") or {}).get("select") or {}
    w = [i for i in P + S if ag[i]["warned"]]
    unc = [i for i in w if any("uncited-with-sources" in r for r in T[i]["route"]["reasonCodes"])]
    ne_main = [i for i, t in M.items() if "dg:no-evidence" in t["route"]["reasonCodes"]]
    s1 = {i for i, v in FN.items() if (v.get("K1") or {}).get("vstage") == "S1"}
    keyed = {i for i, v in FN.items() if (v.get("K1") or {}).get("vstage")}
    live_main = [i for i, t in M.items() if "dg:select" in " ".join(t["route"]["reasonCodes"]) or "dg:no-evidence" in t["route"]["reasonCodes"]]
    out[d] = dict(arm=code, net=g["net"], fixed_u=len(g["fixed_u"]), fixed_by_refusal=len(g["fixed_by_refusal"]), new_CEu=len(g["new_CEu"]), false_ref=len(g["false_ref"]), U_cov_delta=g["U_cov_delta"], U_cov_ci=g["U_cov_ci"],
        verdict=g["verdict"], ceu_ctl=g["ceu_ctl"], ceu_cand=g["ceu_cand"], sent_worse=len(g["sent_worse"]), changed=g["changed"], warned_cand=g["warned_cand"], warned_uncited_with_sources=len(unc),
        no_evidence_screen=len(ne), no_evidence_screen_problems=sum(i in P for i in ne), sel_in_dropped_screen=sum(bool(dgs(T[i]).get("inDropped")) for i in P + S),
        cjk_answers_screen=sum(bool(CJK.search(T[i]["answer"]["text"])) for i in T), cited_screen=sum(bool(T[i]["answer"]["cited"]) for i in P + S), cited_ctl_screen=sum(bool(ctl[i]["answer"]["cited"]) for i in P + S), main_cjk_ctl=sum(bool(CJK.search(ctl[i]["answer"]["text"])) for i in M),
        main_changed_vs_ctl=sn["changed_vs_ctl_all"], main_live=sn["live"], main_no_evidence=sn["no_evidence"], main_sel_in_dropped=sn["selected_in_dropped"], main_sel_in_kept=sn["selected_in_kept"], main_out_tok=sn["mean_out_tok_cand_all"], ctl_out_tok=sn["mean_out_tok_ctl_all"],
        main_totalMs=sn["mean_totalMs_cand_all"], ctl_totalMs=sn["mean_totalMs_ctl_all"], main_ratio=sn["totalMs_ratio_all"], main_cjk=sum(bool(CJK.search(t["answer"]["text"])) for t in M.values()),
        ne_main_in_S1=sum(i in s1 for i in ne_main), ne_main_n=len(ne_main), s1_keyed_total=len(s1), s1_in_ne=sum(i in set(ne_main) for i in s1), main_keyed=len(keyed & set(M)))
json.dump(out, open(H + "/aggregates/stage1-summary.json", "w"), indent=1)
for d, r in out.items(): print(d, json.dumps(r))
