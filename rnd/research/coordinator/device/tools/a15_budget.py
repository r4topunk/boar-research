#!/usr/bin/env python3
"""A15 latency budget for cut 4 (read-only helper; no engine/phone/mini access).

Inputs (all local files):
  - cut 4 desktop control traces (instsubj4 = cut 4 final, v0.1 EN s44+s45):
      boar-eval/runs/kiln/speedpack-l1/spctl-v01-s4{4,5}.traces.jsonl
    fields used: route.task/tier/reasonCodes, retrieval.kept, timing.promptTokens/outputTokens/retrievalMs
    (cache_prompt=false on the desktop server, so promptTokens = the full prompt; the desktop adapter has NO route gate,
     so the gate call is added from the phone model).
  - phone smoke rows: rnd/research/coordinator/device/a15-smoke-2026-10-05/rows.jsonl (cut 3, 9 items)
  - tokcounts.json (tools/tokcounts.mts): gate fixed tokens, answer prefix tokens.
usage: python3 a15_budget.py [--json out.json]
"""
import json, sys, statistics as st, collections
ROOT = "<workspace>"
TR = [f"{ROOT}/boar-eval/runs/kiln/speedpack-l1/spctl-v01-s{s}.traces.jsonl" for s in (44, 45)]
PHONE = f"{ROOT}/rnd/research/coordinator/device/a15-smoke-2026-10-05/rows.jsonl"
TOK = json.load(open(f"{ROOT}/rnd/research/coordinator/device/tools/tokcounts.json"))
GATE_FIXED = 429          # phone log: cachedTok 460 - 1 generated - newTok 30 (our tokenizer says 427)
ANS_PREFIX = TOK["answerPrefixTokens"]  # 230: ChatML head + persona + CONTEXT_INSTRUCTION + GROUNDING_INSTRUCTION
NOSRC = TOK["answerNoSourceSystemTokens"]  # 190
INSTR_ONLY = TOK["answerInstructionOnlyTokens"]  # 65: shared head when the prompt has no sources
REUSED_NOPREFIX = 5       # phone: prompt_total(desktop promptTokens) - ctxTokens = 5 on all 3 model rows (cut 3, no restore)

# ---- calibration from the 9 phone rows (derived in the .md, section 3) ----
phone = [json.loads(l) for l in open(PHONE, encoding="utf-8")]
mrows = [r for r in phone if r["receipt"].get("ctxTokens")]
pf_tps = sum(r["receipt"]["ctxTokens"] for r in mrows) / (sum(r["receipt"]["prefillMs"] for r in mrows) / 1000)
dec = [(r["tokensGenerated"], (r["totalLatencyMs"] - r["ttftMs"]) / 1000) for r in mrows]
dec_tps = sum(a for a, _ in dec) / sum(b for _, b in dec)
retr = sorted(r["receipt"]["retrievalMs"] / 1000 for r in phone if r["receipt"].get("retrievalMs") and r["queryId"] != "warmup-000")
P = {  # (fast, central, slow)
    "prefill_tps": (12.6, round(pf_tps, 2), 10.8),
    "decode_tps": (2.88, round(dec_tps, 2), 2.04),
    "retrieval_s": (retr[0], st.median(retr), retr[-1]),
    "gate_small_s": (2.9, 3.0, 5.0),     # 29 new tokens + 1 step; 2.9-3.0 s (stage starts of probe-co-alarm, vit-cry-001), 5.0 s (logcat item 9)
    "detector_s": (0.05, 0.07, 0.3),     # rule rows total 0.067-0.22 s incl. detector
    "restore_s": (0.5, 1.0, 3.0),        # UNKNOWN: no device measurement of loadSession (60 MB gate / 33 MB answer prefix)
}

def load_items():
    out = []
    for p in TR:
        for l in open(p):
            x = json.loads(l); t = x["timing"]; rc = x["route"]["reasonCodes"]
            task = x["route"].get("task")
            gen = (t.get("promptTokens") or 0) > 0
            gated = any(c.startswith("task:") for c in rc) and task != "places"
            ctx = [c for c in rc if c.startswith("context:") and "->" in c]
            ctxtok = int(ctx[-1].split("->")[1]) if ctx else 0
            out.append(dict(seed=("s44" if "s44" in p else "s45"), id=x["itemId"], task=task, tier=x["route"]["tier"], gated=gated, gen=gen,
                            prompt=t.get("promptTokens") or 0, out=t.get("outputTokens") or 0, kept=len(x["retrieval"]["kept"]),
                            ctxtok=ctxtok, retr_desktop_ms=t.get("retrievalMs"), rc=rc))
    return out

def simulate(items, mode, k, skip_gate=None, ctx_cap=None, out_cap=None, retr_scale=1.0, ctx_cap_all=False, overlap=None, nosrc_cache=False):
    """mode: 'cold' (no KV file restore: cut 3 behaviour / first question) or 'warm' (KVFIX works).
    Items run in trace order (bench order). The single llama context holds one thing at a time (kv state):
      'gate'   = gate prefix + last gate query (set by the gate call; LlamaEngine.nextTokenProbsNow)
      'answer' = the answer prefix + last answer (set by a generation whose system message starts with the prefix)
      'other'  = anything else (a no-source generation).
    A gate with kv != 'gate' pays a restore (warm) or the 429-token fixed prefill (cold); an answer with sources and
    kv != 'answer' pays a restore (warm) or the full prefill (cold); with kv == 'answer' the prefix is simply resident."""
    pf, dc, rt, gs, dt, rs = (P[n][k] for n in ("prefill_tps", "decode_tps", "retrieval_s", "gate_small_s", "detector_s", "restore_s"))
    kv = "other"
    res = []
    for it in items:
        c = collections.OrderedDict(detector=dt, gate=0.0, retrieval=0.0, answer_restore=0.0, answer_prefill=0.0, decode=0.0)
        if it["gated"] and not (skip_gate and skip_gate(it)):
            if kv != "gate":
                c["gate"] += (GATE_FIXED / pf) if mode == "cold" else rs
            c["gate"] += gs
            kv = "gate"
        if it["gated"]:
            c["retrieval"] = rt * retr_scale
        if it["gen"]:
            prompt = it["prompt"]
            if ctx_cap is not None and (ctx_cap_all or it["task"] != "lookup"):
                prompt -= max(0, it["ctxtok"] - ctx_cap)
            has_src = it["kept"] > 0
            if has_src:
                if kv == "answer":
                    shared = ANS_PREFIX
                elif mode == "warm":
                    shared = ANS_PREFIX
                    c["answer_restore"] = rs
                else:
                    shared = REUSED_NOPREFIX
            elif nosrc_cache:
                # second session key for the static no-source system message (190 tok, identical tokens, zero quality surface)
                if kv == "nosrc":
                    shared = NOSRC
                elif mode == "warm":
                    shared = NOSRC
                    c["answer_restore"] = rs
                else:
                    shared = REUSED_NOPREFIX
            else:
                shared = INSTR_ONLY if kv == "answer" else REUSED_NOPREFIX
            c["answer_prefill"] = max(0, prompt - shared) / pf
            c["decode"] = (it["out"] if out_cap is None else min(it["out"], out_cap)) / dc
            kv = "answer" if has_src else ("nosrc" if nosrc_cache else "other")
        if overlap is not None and c["gate"] > 0 and c["retrieval"] > 0:
            # retrieval started while the gate runs (speculative; dropped if the gate says ANSWER); overlap = fraction of the shorter stage hidden
            c["retrieval"] -= overlap * min(c["gate"], c["retrieval"])
        res.append(c)
    return res

def pct(v, q):
    v = sorted(v); i = (len(v) - 1) * q; lo = int(i); hi = min(lo + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (i - lo)

def summarize(items, res, label):
    tot = [sum(c.values()) for c in res]
    ttft = [sum(v for kk, v in c.items() if kk != "decode") for c in res]
    g = [i for i, it in enumerate(items) if it["gen"]]
    gated = [i for i, it in enumerate(items) if it["gated"]]
    comp = {kk: sum(c[kk] for c in res) / len(res) for kk in res[0]}
    compg = {kk: sum(res[i][kk] for i in g) / len(g) for kk in res[0]}
    return dict(label=label, all_total_p50=pct(tot, .5), all_total_p90=pct(tot, .9),
                gen_total_p50=pct([tot[i] for i in g], .5), gen_total_p90=pct([tot[i] for i in g], .9),
                gen_ttft_p50=pct([ttft[i] for i in g], .5), gen_ttft_p90=pct([ttft[i] for i in g], .9),
                gated_total_p50=pct([tot[i] for i in gated], .5),
                mean_total=sum(tot) / len(tot), comp_all=comp, comp_gen=compg, n=len(res), n_gen=len(g), n_gated=len(gated))

def validate_cut3(items_by_id):
    """Replay of the phone smoke (cut 3, cold) with the model: predicted vs measured for the 5 gated rows."""
    out = []
    pf, dc, rt, gs, dt = (P[n][1] for n in ("prefill_tps", "decode_tps", "retrieval_s", "gate_small_s", "detector_s"))
    res = []
    resident = False
    for r in phone:
        q = r["queryId"]
        rc = r["receipt"]; st_ = {s["stage"]: s["atMs"] / 1000 for s in r["stages"]}
        gated = any(c.startswith("route-gate:") and c not in () for c in r["reasonCodes"])
        if q == "warmup-000":
            continue
        pre = 0.0
        if gated:
            pre = dt + (0 if resident else GATE_FIXED / pf) + gs
            resident = True
        gen = bool(rc.get("ctxTokens"))
        pred_total = pre + (rc.get("retrievalMs", 0) / 1000 if gated else 0)
        if gen:
            pred_total += rc["ctxTokens"] / pf + r["tokensGenerated"] / dc
            resident = False
        out.append((q, round(pre, 1), st_.get("retrieving"), round(pred_total, 1), round(r["totalLatencyMs"] / 1000, 1)))
    return out

if __name__ == "__main__":
    items = load_items()
    print("calibration:", json.dumps({k: v for k, v in P.items()}), f"| pooled prefill {pf_tps:.2f} tok/s over {len(mrows)} rows, decode {dec_tps:.2f} tok/s")
    print("validation (cut 3 cold replay): item, pred pre-retrieval, measured 'retrieving' at, pred total, measured total")
    for r in validate_cut3({}): print("  ", r)
    gen = [i for i in items if i["gen"]]
    print("items", len(items), "gated", sum(i["gated"] for i in items), "generating", len(gen), "tier/task", dict(collections.Counter((i["tier"], i["task"]) for i in items)))
    for q in ("prompt", "out"): print(q, "p50/p90/mean", pct([i[q] for i in gen], .5), pct([i[q] for i in gen], .9), round(st.mean(i[q] for i in gen), 1))
    sh = [i["prompt"] - (ANS_PREFIX if i["kept"] else REUSED_NOPREFIX) for i in gen]
    print("new tokens with KVFIX warm: p50/p90/mean", pct(sh, .5), pct(sh, .9), round(st.mean(sh), 1), "| has_src", sum(i["kept"] > 0 for i in gen), "/", len(gen))
    out = {}
    for name, k in (("fast", 0), ("central", 1), ("slow", 2)):
        for mode in ("warm", "cold"):
            out[f"{mode}-{name}"] = summarize(items, simulate(items, mode, k), f"{mode}-{name}")
    # candidates (central parameters, warm)
    elig = lambda it: it["task"] in ("lookup", "research", "compare") and not any(c.startswith(("detector:fire", "grounding:health")) for c in it["rc"])
    cands = {
        "base": simulate(items, "warm", 1),
        "C1 skip gate (rule type lookup/research/compare, no detector fire)": simulate(items, "warm", 1, skip_gate=elig),
        "C1b skip gate for all gated items": simulate(items, "warm", 1, skip_gate=lambda it: True),
        "C2 non-lookup context cap 450 tok": simulate(items, "warm", 1, ctx_cap=450),
        "C2b context cap 300 tok, all tasks (what-if)": simulate(items, "warm", 1, ctx_cap=300, ctx_cap_all=True),
        "C3 forge perf retrieval -65% (extrapolated)": simulate(items, "warm", 1, retr_scale=0.35),
        "C4 answer cap 120 tok (n_predict)": simulate(items, "warm", 1, out_cap=120),
        "C5 gate overlapped with retrieval (100% hidden, ideal)": simulate(items, "warm", 1, overlap=1.0),
        "C5b gate overlapped with retrieval (50% hidden)": simulate(items, "warm", 1, overlap=0.5),
        "C6 second KV prefix for no-source prompts": simulate(items, "warm", 1, nosrc_cache=True),
        "ALL = C1 + C3 + C6": simulate(items, "warm", 1, skip_gate=elig, retr_scale=0.35, nosrc_cache=True),
    }
    base = summarize(items, cands["base"], "base")
    out["candidates"] = {}
    for n, r in cands.items():
        s = summarize(items, r, n)
        out["candidates"][n] = dict(gen_total_p50=s["gen_total_p50"], gen_total_p90=s["gen_total_p90"], mean_total=s["mean_total"],
                                    save_gen_p50=base["gen_total_p50"] - s["gen_total_p50"], save_mean=base["mean_total"] - s["mean_total"])
    # also under cold (KVFIX broken) for the gate skip
    out["candidates"]["C1 under cold"] = dict(
        save_mean=summarize(items, simulate(items, "cold", 1), "")["mean_total"] - summarize(items, simulate(items, "cold", 1, skip_gate=elig), "")["mean_total"])
    # sensitivity: restore cost 3 s (slow loadSession) and a device-rate what-if (prefill and decode x1.25), warm central
    P["restore_s"] = (0.5, 3.0, 3.0)
    out["sens_restore_3s"] = summarize(items, simulate(items, "warm", 1), "")
    P["restore_s"] = (0.5, 1.0, 3.0)
    P["prefill_tps"] = (12.6, round(pf_tps * 1.25, 2), 10.8); P["decode_tps"] = (2.88, round(dec_tps * 1.25, 2), 2.04)
    out["whatif_rate_x1.25"] = summarize(items, simulate(items, "warm", 1), "")
    P["prefill_tps"] = (12.6, round(pf_tps, 2), 10.8); P["decode_tps"] = (2.88, round(dec_tps, 2), 2.04)
    out["eligible_gate_skip_items"] = sum(1 for i in items if i["gated"] and elig(i))
    out["ctx_cap_items_affected"] = sum(1 for i in items if i["gen"] and i["task"] != "lookup" and i["ctxtok"] > 450)
    out["out_cap_items_affected"] = sum(1 for i in items if i["gen"] and i["out"] > 120)
    print(json.dumps(out, indent=1, default=lambda x: round(x, 2)))
    if "--csv" in sys.argv:
        import csv
        w_, c_ = simulate(items, "warm", 1), simulate(items, "cold", 1)
        with open(sys.argv[sys.argv.index("--csv") + 1], "w", newline="") as f:
            cw = csv.writer(f)
            cw.writerow(["seed", "item", "tier", "task", "gated", "llm_calls_phone", "llm_calls_desktop", "prompt_tokens", "cacheable_kvfix", "new_tokens", "gen_tokens", "kept_sources", "warm_total_s", "cold_total_s"])
            for it, a, b in zip(items, w_, c_):
                cache = (ANS_PREFIX if it["kept"] else REUSED_NOPREFIX) if it["gen"] else 0
                cw.writerow([it["seed"], it["id"], it["tier"], it["task"], int(it["gated"]), int(it["gated"]) + int(it["gen"]), int(it["gen"]),
                             it["prompt"], cache, max(0, it["prompt"] - cache), it["out"], it["kept"], round(sum(a.values()), 1), round(sum(b.values()), 1)])
    if "--json" in sys.argv:
        json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1, default=lambda x: round(x, 3))
