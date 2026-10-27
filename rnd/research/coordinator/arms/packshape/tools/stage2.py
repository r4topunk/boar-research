#!/usr/bin/env python3
"""PACKSHAPE stage 2 (0 LLM here). prep: python3 -I stage2.py prep -> ../judge/units.json ; agg: python3 -I stage2.py agg -> ../stage2.json
Units: PACKPROOF prep.py construction (Context blocks of the generation prompt, '[n] Title (cited)'); key = sha256(id, answer, sources)."""
import json, sys, os, re, hashlib, importlib.util
CO = "<workspace>/rnd/research/coordinator/arms/"; PP = CO + "packproof/"; D = CO + "packshape/"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
src = open(PP + "tools/prep.py").read(); g = {}; exec(src[:src.index("units, ans = {}, {}")], g)  # REF, Q, blocks
g2 = {}; s2 = open(PP + "tools/agg.py").read(); exec(s2[:s2.index("L = resolve(")], g2)
SFX = os.environ.get("PS_SEED", "")  # "" = seed 42; "43" = Addendum 1
G = D + f"gen/on-k13s{SFX}/"; J = D + ("judge/" if not SFX else f"judge-s{SFX}/")
def prep():
    PR = {}
    for p in rd(G + "prompts.jsonl"): PR.setdefault(p["itemId"], []).append(p)
    units, ans = {}, {}
    for t in rd(G + "traces.jsonl"):
        i = t["itemId"]; a = t["answer"]; cited = set(a.get("cited") or []); bl = g["blocks"](PR.get(i, []))
        srcs = "\n\n".join(f"[{n+1}] {ti}{' (cited)' if ti in cited else ''}\n{b}" for n, (ti, b) in enumerate(bl)) or "(none)"
        rev = "\n\n".join(f"[{n+1}] {ti}{' (cited)' if ti in cited else ''}\n{b}" for n, (ti, b) in enumerate(bl[::-1])) or "(none)"
        key = hashlib.sha256(json.dumps([i, a["text"], srcs]).encode()).hexdigest()[:16]
        units[key] = dict(key=key, id=i, question=g["Q"][i]["question"], gold=g["REF"][i], rubric=g["Q"][i]["rubric"], answer=a["text"], sources=srcs, sources_rev=rev, n_src=len(bl))
        ans[i] = dict(key=key, text=a["text"], shown=a.get("shown") or [], cited=sorted(cited), kept=[(k["title"], k["source"]) for k in t["retrieval"]["kept"]],
                      raw=[(k["title"], k["source"]) for k in t["retrieval"]["raw"]], totalMs=t["timing"].get("totalMs"), host=t["runtime"]["host"])
    os.makedirs(J, exist_ok=True)
    json.dump(dict(units=list(units.values())), open(J + "units.json", "w")); json.dump(ans, open(J + "answers.json", "w")); print("units", len(units))
def agg():
    C = g2["CORR"]; OWN = json.load(open(PP + "in/own.json"))
    LS = {r["key"]: r["label"] for r in rd(J + "labels.jsonl") if r["ok"] and r["call"] == "A"}
    AS = json.load(open(J + "answers.json"))
    LB = g2["resolve"](PP + "judge/labels.jsonl"); LBA = {r["key"]: r["label"] for r in rd(PP + "judge/labels.jsonl") if r["ok"] and r["call"] == "A"}
    AB = json.load(open(PP + "judge/answers.json")); PS = json.load(open(D + "packshape.json"))["selftests"]
    rep = {r["id"]: [c["title"] for c in r["keptFull"]] for r in rd(D + "replay/st.SHAPED.on-k13.jsonl")}
    rows = {}
    for i in sorted(AS):
        b = AB[f"on|{i}"]; s = AS[i]
        rows[i] = dict(base=LB.get(b["key"], (None,))[0], baseA=LBA.get(b["key"]), shaped=LS.get(s["key"]),
                       base_fact=PS["BASE"]["fb20_items"][i]["fact"], shaped_fact=PS["SHAPED"]["fb20_items"][i]["fact"],
                       live_kept_eq_replay=[t for t, _ in s["kept"]] == rep[i], live_own_kept=g2["match"] and any(g2["match"](OWN[i], t, so) for t, so in s["kept"]),
                       base_banner=b["text"].startswith(g2["BANNER"]), shaped_banner=s["text"].startswith(g2["BANNER"]), totalMs=s["totalMs"])
    n = len(rows); ca = lambda k: sum(r[k] in C for r in rows.values())
    rr = lambda k, f: (sum(r[k] in C for r in rows.values() if r[f]), sum(1 for r in rows.values() if r[f]))
    from collections import Counter
    out = dict(n=n, labelled=sum(r["shaped"] is not None for r in rows.values()), correct_any=dict(base=ca("base"), baseA=ca("baseA"), shaped=ca("shaped")),
               read_right_when_delivered=dict(base=rr("base", "base_fact"), shaped=rr("shaped", "shaped_fact")),
               labels=dict(base=Counter(r["base"] for r in rows.values()), shaped=Counter(r["shaped"] for r in rows.values())),
               live_kept_eq_replay=sum(r["live_kept_eq_replay"] for r in rows.values()), live_own_kept=sum(r["live_own_kept"] for r in rows.values()),
               banner=dict(base=sum(r["base_banner"] for r in rows.values()), shaped=sum(r["shaped_banner"] for r in rows.values())), rows=rows)
    pb = g2["boot"]([(r["shaped"] in C, r["base"] in C) for r in rows.values()]); out["d_correct_any_ci"] = pb
    k, m = out["read_right_when_delivered"]["shaped"]
    lever = out["correct_any"]["shaped"] >= out["correct_any"]["base"] + 5 and m and k / m >= 0.6
    out["decision"] = "LEVER-CANDIDATE" if lever else "DELIVERY-ONLY"
    json.dump(out, open(D + (f"stage2-s{SFX}.json" if SFX else "stage2.json"), "w"), indent=1); print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=0, default=str))
    for i, r in rows.items(): print(i[-3:], r)
{"prep": prep, "agg": agg}[sys.argv[1]]()
