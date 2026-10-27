#!/usr/bin/env python3
"""NOTE2-TRANSFER (0 LLM): apply NOTE-2's refuse-by-default rule to Pixel bench rows and to desktop LITEPACKS traces.
Criterion: ../NOTE2-TRANSFER-criterion.md (sha in ../NOTE2-TRANSFER-criterion.sha256, rnd b6b1f787).
  python3 -I note2_apply.py                      -> ../aggregates/note2-transfer.json + table on stdout (+ ../aggregates/haiku-todo.json)
  python3 -I note2_apply.py --rc DIR [DIR ...]   -> device-day RC rows (results/rc-*): line presence vs the bench engine on the same ids,
                                                    hide rate P1, seconds hidden; writes ../aggregates/rc-<name>.json
Never reads blind/, rnd/veil or bench v0.4."""
import json, os, re, sys, glob, hashlib, collections
ROOT = "<workspace>"; CO = f"{ROOT}/rnd/research/coordinator"; A = f"{CO}/arms"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = f"{HERE}/aggregates"
PH = f"{ROOT}/handoff/pixel8-2026-10-20/bench/results"
crit = open(f"{HERE}/NOTE2-TRANSFER-criterion.sha256").read().split()[0]
assert hashlib.sha256(open(f"{HERE}/NOTE2-TRANSFER-criterion.md", "rb").read()).hexdigest() == crit, "criterion changed"
sys.path.insert(0, f"{A}/null-cal/tools"); from labels import is_decline, W  # noqa: E402  (same W and decline test as NOTE-2's numbers)
CITE = re.compile(r"\[\d+\]")
V01 = [l.strip() for l in open(f"{A}/litepacks/data/v01-57.ids") if l.strip()]
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
sha = lambda t: hashlib.sha256(t.encode()).hexdigest()
health = lambda codes: any(c.startswith("grounding:health-") or c.startswith("grounding:fa-card") for c in codes)

def norm_phone(r):
    rec = r.get("receipt") or {}; codes = r.get("reasonCodes") or rec.get("reasonCodes") or []
    cfg = (r.get("configId") or "").split(":", 1)[-1]; model = r.get("modelId") or rec.get("modelId") or cfg
    ot = r.get("tokensGenerated") or rec.get("tokens") or 0
    text = r.get("answer") if isinstance(r.get("answer"), str) else (r.get("text") or "")
    return dict(id=r.get("queryId") or r.get("id"), text=text or "", declined=bool(r.get("declined")), ot=ot,
                kept=len(r.get("retrievedTitles") or []), codes=codes, llm=(model == cfg) or ot > 0,
                total=(r.get("totalLatencyMs") or rec.get("totalMs") or r.get("wallMs") or 0) / 1000,
                retr=(rec.get("retrievalMs") or r.get("retrievalMs") or 0) / 1000, persona=r.get("personalityId"))
def norm_desk(t):
    d = [e for e in t.get("events", []) if e.get("type") == "done"]; rec = (d[-1].get("receipt") if d else {}) or {}
    tm = t["timing"]; ot = tm.get("outputTokens") or 0
    return dict(id=t["itemId"], text=t["answer"]["text"] or "", declined=bool(t["answer"]["declined"]), ot=ot,
                kept=len(t["retrieval"]["kept"]), codes=t["route"]["reasonCodes"], llm=(rec.get("modelId") == t["config"]["modelId"]) or ot > 0,
                total=(tm.get("totalMs") or 0) / 1000, retr=(tm.get("retrievalMs") or 0) / 1000, persona=None)

def classify(x, compact):
    """P1 = NOTE-2 rule on the text as is; P2 = P1 + the compact release decisions for a non-compact row (criterion)."""
    dec = is_decline(x["text"], x["declined"]); w = x["text"].startswith(W); nokept = x["ot"] > 0 and x["kept"] == 0
    p1 = x["llm"] and (dec or w or nokept)
    eq = (not compact) and x["llm"] and x["ot"] > 0 and not health(x["codes"]) and not dec and (
        "grounding:no-source-memory" in x["codes"] or (x["kept"] > 0 and not CITE.search(x["text"])))
    p2 = p1 or eq
    return dict(dec=dec, w=w, nokept=nokept, eq=eq, P1=p1, P2=p2, health=health(x["codes"]))

# ---------- labels: every existing judge.v1 (Opus) / judge.v1-low (Haiku) both-order pair, unit = id | sha256(text) ----------
def label_index():
    jf, tf = [], []
    for r in (f"{CO}/arms", f"{CO}/ruler", f"{ROOT}/boar-eval/runs", f"{ROOT}/rnd/kiln"):
        for dp, dn, fn in os.walk(r):
            if "veil" in dp or "/blind" in dp or ".shards" in dp or "v0.4" in dp: continue
            for f in fn:
                p = os.path.join(dp, f)
                if f.endswith(".jsonl") and "judgments" in f: jf.append(p)
                elif f.endswith("traces.jsonl"): tf.append(p)
    need = collections.defaultdict(list)
    for p in sorted(jf):
        try:
            for l in open(p):
                if '"ok":true' not in l.replace(" ", ""): continue
                r = json.loads(l); jm = str(r.get("judgeModel")); jv = r.get("judgeVersion")
                fam = "opus" if ("opus" in jm and jv == "judge.v1") else "haiku" if ("haiku" in jm and jv == "judge.v1-low") else None
                if fam and r.get("tracesSha256") and not r.get("floorScored") and r.get("mapped"):
                    need[r["tracesSha256"]].append((p, fam, r))
        except (ValueError, UnicodeDecodeError): pass
    th = {}
    for p in sorted(tf):
        try: h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        except OSError: continue
        if h in need and h not in th: th[h] = p
    pairs = collections.defaultdict(dict)  # (key, fam, file) -> {order: corr}
    for h, rs in need.items():
        if h not in th: continue
        T = {}
        for j in rd(th[h]): T[j.get("itemId") or j.get("queryId")] = j
        for p, fam, r in rs:
            t = T.get(r["queryId"])
            if not t or t.get("error") or not isinstance(t.get("answer"), dict): continue
            pairs[(f"{r['queryId']}|{sha(t['answer']['text'] or '')}", fam, p)].setdefault(r["order"], r["mapped"]["boar"]["correctness"])
    idx = collections.defaultdict(lambda: {"opus": [], "haiku": []})
    for (k, fam, p), v in pairs.items():
        if len(v) == 2: idx[k][fam].append(sum(v.values()) / 2)
    return idx
def lab(idx, i, text):
    u = idx.get(f"{i}|{sha(text)}")
    if not u: return None
    for fam in ("opus", "haiku"):
        if u[fam]: c = sum(u[fam]) / len(u[fam]); return dict(fam=fam, corr=c, correct=c >= 4, CE=c <= 1.5)
    return None

def tier_stats(rows, compact, idx, ids, proxy=None):
    """rows: {id: norm}. ids: the ids to count. proxy: {id: label} from the paired arm, for hidden rows with no text."""
    S = dict(n=0, llm=0, P1=0, P2=0, dec=0, w=0, nokept=0, eq=0, health_hidden=0, revealable=0, labelled=0, opus=0, haiku=0,
             correct=0, CE=0, partial=0, unlabelled=[], gen_s_hidden=0.0, wall_s_hidden=0.0, gen_rows_hidden=0, no_text_hidden=0,
             proxy_correct=0, proxy_CE=0, proxy_n=0, hidden_ids=[])
    for i in ids:
        x = rows.get(i)
        if x is None: continue
        S["n"] += 1; c = classify(x, compact)
        if not x["llm"]: continue
        S["llm"] += 1
        for k in ("P1", "P2", "dec", "w", "nokept", "eq"): S[k] += c[k]
        if not c["P2"]: continue
        S["hidden_ids"].append(i)
        if x["ot"] > 0:
            S["gen_rows_hidden"] += 1; S["gen_s_hidden"] += max(0.0, x["total"] - x["retr"]); S["wall_s_hidden"] += x["total"]
        if c["health"]: S["health_hidden"] += 1; continue
        if c["dec"] or x["ot"] == 0:
            S["no_text_hidden"] += 1
            if proxy is not None and proxy.get(i):
                S["proxy_n"] += 1; S["proxy_correct"] += proxy[i]["correct"]; S["proxy_CE"] += proxy[i]["CE"]
            continue
        S["revealable"] += 1; L = lab(idx, i, x["text"])
        if not L: S["unlabelled"].append(i); continue
        S["labelled"] += 1; S[L["fam"]] += 1; S["correct"] += L["correct"]; S["CE"] += L["CE"]; S["partial"] += not (L["correct"] or L["CE"])
    n = S["n"] or 1; m = S["llm"] or 1
    S.update(hide_P1=round(100 * S["P1"] / m, 1), hide_P2=round(100 * S["P2"] / m, 1), hidden_per100=round(100 * S["P2"] / n, 1),
             gen_s_per100=round(100 * S["gen_s_hidden"] / n, 1), wall_s_per100=round(100 * S["wall_s_hidden"] / n, 1),
             correct_hidden_per100=round(100 * S["correct"] / n, 1), CE_hidden_per100=round(100 * S["CE"] / n, 1),
             gen_s_per_hidden_answer=round(S["gen_s_hidden"] / S["gen_rows_hidden"], 1) if S["gen_rows_hidden"] else None)
    S["gen_s_hidden"] = round(S["gen_s_hidden"], 1); S["wall_s_hidden"] = round(S["wall_s_hidden"], 1)
    return S

def desk_rows(path): return {t["itemId"]: norm_desk(t) for t in rd(path) if not t.get("error")}
def phone_rows(run): return {x["id"]: x for x in map(norm_phone, rd(f"{PH}/{run}/rows.jsonl")) if x["id"] and not x["id"].startswith("warmup")}

PAIRS = [  # tier, phone run, phone compact?, desktop trace, deciding
    ("1.7B kit", "q17b73-a", True, f"{A}/lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl", True),
    ("1.7B A-union", "aunion73-a", True, f"{A}/coverage-matrix/q17/traces/q17-KA-main-97-s42.traces.jsonl", True),
    ("Gemma kit", "gemma73-a", False, f"{A}/gemma4-e2b/stage2/traces/gemma4-e2b-eng-K0-main-s42.traces.jsonl", True),
    ("Gemma A-union", "gemmaa73-a", False, f"{A}/gemma4-e2b/stage2/traces/gemma4-e2b-eng-K0-main-s42.traces.jsonl", False),
    ("4B A-union", "q4ba73-a", False, f"{A}/gemma4-e2b-vs4b/traces/gemma4-e2b-vs4b-K0-main-s42.traces.jsonl", False),
]
REPL = ("1.7B kit (MacBook LP K0 replication)", f"{A}/litepacks/traces/lp-K0-v01-s42.traces.jsonl")

def p2_validation(D):
    """On desktop (compact, line on) the non-compact predicate must mark the same rows as the line: report agreement."""
    agree = tot = 0; dis = []
    for i, x in D.items():
        if not x["llm"] or x["ot"] == 0 or health(x["codes"]): continue
        c = classify(x, compact=False); line = c["w"]; pred = ("grounding:no-source-memory" in x["codes"]) or c["nokept"] or (x["kept"] > 0 and not CITE.search(x["text"]))
        if is_decline(x["text"], x["declined"]): continue
        tot += 1; agree += (line or c["nokept"]) == pred
        if (line or c["nokept"]) != pred: dis.append(i)
    return dict(n=tot, agree=agree, disagree_ids=dis)

def main():
    idx = label_index(); res = {"criterion_sha256": crit, "label_units": len(idx), "tiers": {}, "haiku_todo": []}
    shared = V01
    for tier, run, compact, dpath, deciding in PAIRS:
        P = phone_rows(run); D = desk_rows(dpath)
        dprox = {i: lab(idx, i, D[i]["text"]) for i in D}
        ph = tier_stats(P, compact, idx, shared, proxy=dprox); dk = tier_stats(D, True, idx, shared)
        ph_all = tier_stats(P, compact, idx, sorted(P))
        delta = round(ph["hide_P2"] - dk["hide_P2"], 1); delta1 = round(ph["hide_P1"] - dk["hide_P1"], 1)
        res["tiers"][tier] = dict(phone_run=run, desktop_trace=os.path.relpath(dpath, ROOT), deciding=deciding, compact_on_phone=compact,
                                  phone=ph, desktop=dk, phone_all72=ph_all, delta_pp_P2=delta, delta_pp_P1=delta1,
                                  over_10pp_P2=abs(delta) > 10, over_10pp_P1=abs(delta1) > 10, p2_validation_desktop=p2_validation(D))
        for i in ph_all["unlabelled"]: res["haiku_todo"].append(dict(tier=tier, run=run, id=i))
    # 4B: the cap left room for a seeded sample of 9 of its unlabelled hidden units (judge/q4b-sample.json): expansion estimate
    sp = f"{HERE}/judge/q4b-sample.json"
    if os.path.exists(sp):
        Q = json.load(open(sp)); P = phone_rows("q4ba73-a"); v = res["tiers"]["4B A-union"]["phone"]
        sl = [lab(idx, i, P[i]["text"]) for i in Q["q4b_sample"]]; sl = [x for x in sl if x]
        pop = len(Q["q4b_population"]); old_lab = v["labelled"] - len(sl); w = pop / len(sl) if sl else 0
        kc = sum(x["correct"] for x in sl); kce = sum(x["CE"] for x in sl)
        prev = [lab(idx, i, P[i]["text"]) for i in v["hidden_ids"] if i not in Q["q4b_population"] and lab(idx, i, P[i]["text"])
                and not classify(P[i], False)["dec"] and P[i]["ot"] > 0]
        pc = sum(x["correct"] for x in prev); pce = sum(x["CE"] for x in prev)
        res["tiers"]["4B A-union"]["sample_estimate"] = dict(population=pop, sampled=len(sl), sample_correct=kc, sample_CE=kce, prior_labelled=len(prev),
            correct_hidden_per100_est=round(100 * (pc + kc * w) / v["n"], 1), CE_hidden_per100_est=round(100 * (pce + kce * w) / v["n"], 1))
    D = desk_rows(REPL[1]); res["replication"] = {REPL[0]: tier_stats(D, True, idx, shared)}
    kill = [t for t, v in res["tiers"].items() if v["deciding"] and v["over_10pp_P2"]]
    p1c = [t for t, v in res["tiers"].items() if v["deciding"] and v["over_10pp_P1"] and not v["over_10pp_P2"]]
    res["verdict"] = dict(killed=bool(kill), killing_pairs=kill, p1_config_clause_fires=p1c)
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(f"{OUT}/note2-transfer.json", "w"), indent=1)
    json.dump(res["haiku_todo"], open(f"{OUT}/haiku-todo.json", "w"), indent=1)
    print("tier | hide P2 phone / desk (d pp) | hide P1 phone / desk | hidden/100 ph | gen s hidden/100 ph (per answer) | correct / CE hidden per 100 ph (labelled/revealable) | desk correct / CE per 100 | unlabelled")
    for t, v in res["tiers"].items():
        p, d = v["phone"], v["desktop"]
        print(f"{t} | {p['hide_P2']} / {d['hide_P2']} ({v['delta_pp_P2']:+}) | {p['hide_P1']} / {d['hide_P1']} | {p['hidden_per100']} | {p['gen_s_per100']} ({p['gen_s_per_hidden_answer']}) | "
              f"{p['correct_hidden_per100']} / {p['CE_hidden_per100']} ({p['labelled']}/{p['revealable']}; no-text {p['no_text_hidden']}, proxy {p['proxy_correct']}/{p['proxy_CE']} of {p['proxy_n']}) | "
              f"{d['correct_hidden_per100']} / {d['CE_hidden_per100']} ({d['labelled']}/{d['revealable']}) | {p['unlabelled']} | val {v['p2_validation_desktop']['agree']}/{v['p2_validation_desktop']['n']}")
    print("4B sample", res["tiers"]["4B A-union"].get("sample_estimate"))
    print("verdict", res["verdict"], "haiku todo", len(res["haiku_todo"]))

# ---------- device day (10-22): RC rows ----------
BENCH_REF = {"17b": "aunion73-a", "1.7b": "aunion73-a", "4b": "q4ba73-a", "gemma": "gemmaa73-a"}
REF = None  # --ref <bench run> overrides the name-based bench reference
def rc(dirs):
    for d in dirs:
        rows = {}
        for f in sorted(glob.glob(f"{d}/rows.jsonl")) or sorted(glob.glob(f"{d}/eval-out/**/*.jsonl", recursive=True)):
            for r in rd(f):
                x = norm_phone(r)
                if x["id"] and not x["id"].startswith("warmup"): rows[x["id"]] = x
        name = os.path.basename(d.rstrip("/")); ref = REF or next((v for k, v in BENCH_REF.items() if k in name.lower()), None)
        B = phone_rows(ref) if ref else {}
        bench_warns = [i for i in rows if i in B and classify(B[i], ref == "aunion73-a")["P2"]]
        line_on = [i for i in bench_warns if rows[i]["text"].startswith(W) or "may be wrong" in rows[i]["text"].lower()]
        ids = sorted(rows); m = sum(x["llm"] for x in rows.values()) or 1
        p1 = [i for i in ids if classify(rows[i], True)["P1"]]
        personas = sorted({str(x["persona"]) for x in rows.values()})
        out = dict(dir=d, rows=len(rows), bench_ref=ref, personas=personas, not_like_for_like="detailed" in personas,
                   bench_warn_ids=bench_warns, rc_line_on_ids=line_on, line_presence=f"{len(line_on)}/{len(bench_warns)}",
                   premise_fails=len(bench_warns) >= 10 and len(line_on) <= 3, premise_fails_scaled=bool(bench_warns) and len(line_on) / len(bench_warns) <= 0.3,
                   hide_P1=round(100 * len(p1) / m, 1), hidden_gen_s=round(sum(max(0, rows[i]["total"] - rows[i]["retr"]) for i in p1 if rows[i]["ot"] > 0), 1))
        os.makedirs(OUT, exist_ok=True); json.dump(out, open(f"{OUT}/rc-{name}.json", "w"), indent=1)
        print(json.dumps({k: v for k, v in out.items() if k != "dir"}))

if __name__ == "__main__":
    a = sys.argv[1:]
    if "--ref" in a: k = a.index("--ref"); REF = a[k + 1]; del a[k:k + 2]
    if len(a) > 1 and a[0] == "--rc": rc(a[1:])
    else: main()
