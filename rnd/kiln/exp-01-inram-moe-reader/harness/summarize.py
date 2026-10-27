#!/usr/bin/env python3
"""Summarize exp-01/02 runs: speed + memory per model, deterministic pre-check (Lantern), v2 judge.

Usage: python3 summarize.py <exp dir> <boar root> model-id [model-id ...]
Writes <exp dir>/results/summary.md and summary.json.
"""
import json, math, os, random, subprocess, sys, statistics as st

exp, root, models = sys.argv[1], sys.argv[2], sys.argv[3:]
os.makedirs(f"{exp}/results", exist_ok=True)
slices = json.load(open(f"{exp}/questions/slices.lantern52.json"))
PRECHECK = os.environ.get("KILN_PRECHECK", f"{root}/rnd/lantern/tools/precheck.py")  # v1 disagreed with hand labels (7/10); use v2
QUESTIONS = f"{root}/rnd/lantern/handoff/questions.vitalik-lantern.jsonl"


def pct(xs, p):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    k = (len(xs) - 1) * p
    lo, hi = math.floor(k), math.ceil(k)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0, c - h), min(1, c + h))


def precheck(rows, ids):
    tmp = f"{exp}/results/.pre.jsonl"
    with open(tmp, "w") as f:
        for r in rows:
            f.write(json.dumps({"queryId": r["queryId"], "answer": r["answer"]}) + "\n")
    sub = f"{exp}/results/.sub.json"
    json.dump({"ids": sorted(ids)}, open(sub, "w"))
    js = f"{exp}/results/.pre.json"
    subprocess.run(["python3", PRECHECK, tmp, "--questions", QUESTIONS, "--subset", sub, "--json", js],
                   capture_output=True, text=True, check=True)
    # precheck v2: status in pass / refused (why ok|not-ok) / confident-wrong / fail-missing / empty / missing
    return {x["id"]: (x["status"], x["why"], x["counts_as_pass"]) for x in json.load(open(js))}


def judge(m):
    p = f"{exp}/judge/kiln-{m}__vs__claude-code__opus.jsonl"
    if not os.path.exists(p):
        return None
    rows = [json.loads(l) for l in open(p) if l.strip()]
    rows = [r for r in rows if r.get("ok")]
    by = {}
    for r in rows:
        by.setdefault(r["queryId"], []).append(r["mapped"])
    pairs = []
    for q, v in by.items():
        if len(v) < 2:
            continue
        w = v[0]["winner"] if v[0]["winner"] == v[1]["winner"] else "tie"
        mean = lambda s: sum(s.values()) / len(s)
        pairs.append({"q": q, "winner": w, "consistent": v[0]["winner"] == v[1]["winner"],
                      "boar": (mean(v[0]["boar"]) + mean(v[1]["boar"])) / 2, "ref": (mean(v[0]["ref"]) + mean(v[1]["ref"])) / 2})
    if not pairs:
        return None
    score = lambda ps: sum(1 if p["winner"] == "boar" else 0.5 if p["winner"] == "tie" else 0 for p in ps) / len(ps)
    rng = random.Random(2026)
    boots = sorted(score([rng.choice(pairs) for _ in pairs]) for _ in range(2000))
    return {"n": len(pairs), "winScore": score(pairs), "ci": (boots[50], boots[1949]),
            "wins": sum(p["winner"] == "boar" for p in pairs), "ties": sum(p["winner"] == "tie" for p in pairs),
            "losses": sum(p["winner"] == "ref" for p in pairs), "consistent": sum(p["consistent"] for p in pairs),
            "qualityRatio": sum(p["boar"] for p in pairs) / sum(p["ref"] for p in pairs), "pairs": pairs}


summary = {}
for m in models:
    rows = [json.loads(l) for l in open(f"{exp}/runs/{m}.jsonl")]
    meta = json.load(open(f"{exp}/runs/{m}.jsonl.meta.json"))
    llm = [r for r in rows if r["route"] == "llm"]
    lan = [r for r in rows if r["set"] == "lantern52"]
    lan_ids_all = {r["queryId"] for r in lan}
    lan_ids_llm = {r["queryId"] for r in lan if r["route"] == "llm"}
    v = precheck(lan, lan_ids_all)
    def score(ids):
        vs = [v[i] for i in ids if i in v]
        n = len(vs)
        k = sum(x[2] for x in vs)
        rf = sum(x[0] == "refused" for x in vs)
        cw = sum(x[0] == "confident-wrong" for x in vs)
        return {"n": n, "pass": k, "passRate": k / n if n else None, "passCi": wilson(k, n),
                "refused": rf, "refusedRate": rf / n if n else None,
                "confidentWrong": cw, "cwRate": cw / n if n else None, "cwCi": wilson(cw, n)}
    pre = {"all52": score(lan_ids_all), "llmRouted": score(lan_ids_llm),
           "b1-competitor-app": score({i for i in lan_ids_all if slices.get(i) == "b1-competitor-app"}),
           "b2-boar": score({i for i in lan_ids_all if slices.get(i) == "b2-boar"})}
    cats = {}
    for r in lan:
        cats.setdefault(r["category"], set()).add(r["queryId"])
    pre["byCategory"] = {c: score(ids) for c, ids in sorted(cats.items())}
    summary[m] = {
        "meta": meta,
        "nLlm": len(llm),
        "contaminatedFinal": sum(r.get("contaminated", False) for r in llm),
        "reruns": sum(r.get("rerun", False) for r in llm),
        "promptTokensP50": pct([r["promptN"] for r in llm], 0.5),
        "ttftP50": pct([r["ttftMs"] for r in llm], 0.5), "ttftP90": pct([r["ttftMs"] for r in llm], 0.9),
        "totalP50": pct([r["totalMs"] for r in llm], 0.5), "totalP90": pct([r["totalMs"] for r in llm], 0.9),
        "prefillTokSP50": pct([r["prefillTokPerS"] for r in llm], 0.5),
        "decodeTokSP50": pct([r["decodeTokPerS"] for r in llm], 0.5),
        "answerTokensP50": pct([r["predictedN"] for r in llm], 0.5),
        "inlineThink": sum(r.get("inlineThink", False) for r in llm),
        "reasoningNonEmpty": sum(bool(r.get("reasoning")) for r in llm),
        "empty": sum(not r["answer"].strip() for r in llm),
        "precheck": pre, "precheckVerdicts": v, "judgeV2": judge(m),
    }

json.dump(summary, open(f"{exp}/results/summary.json", "w"), indent=1, default=str)

f = lambda x, d=0: "—" if x is None else f"{x:,.{d}f}"
pc = lambda s: "—" if s["passRate"] is None else f"{s['pass']}/{s['n']} = {s['passRate']:.0%} ({s['passCi'][0]:.0%}–{s['passCi'][1]:.0%})"
cw = lambda s: "—" if s["cwRate"] is None else f"{s['confidentWrong']}/{s['n']} = {s['cwRate']:.0%} ({s['cwCi'][0]:.0%}–{s['cwCi'][1]:.0%})"
L = ["# exp summary (generated by harness/summarize.py)", "",
     "## Speed and memory (LLM-routed items, M4 CPU -t 4, full prefill every request)", "",
     "| Model | n | prompt tok p50 | TTFT p50 / p90 (s) | total p50 / p90 (s) | prefill tok/s p50 | decode tok/s p50 | answer tok p50 | peak RSS (GiB) | peak footprint (GiB) | reruns / still flagged |",
     "|---|---:|---:|---|---|---:|---:|---:|---:|---:|---|"]
for m, s in summary.items():
    me = s["meta"]
    L.append(f"| {m} | {s['nLlm']} | {f(s['promptTokensP50'])} | {f(s['ttftP50']/1000,1)} / {f(s['ttftP90']/1000,1)} | "
             f"{f(s['totalP50']/1000,1)} / {f(s['totalP90']/1000,1)} | {f(s['prefillTokSP50'],1)} | {f(s['decodeTokSP50'],1)} | "
             f"{f(s['answerTokensP50'])} | {f((me['peakRssSampledBytes'] or 0)/2**30,2)} | {f((me['peakFootprintBytes'] or 0)/2**30,2)} | {s['reruns']} / {s['contaminatedFinal']} |")
L += ["", "## Deterministic pre-check (Lantern `precheck.py` v2), pass% (refusal counts only where refuse_ok), refused%, confident-wrong%, Wilson 95% CI", "",
      "| Model | pass, all 52 | pass, LLM-routed only | pass, b1 a competitor team verbatim | pass, b2 BOAR-style | refused (all 52) | confident-wrong (all 52) |", "|---|---|---|---|---|---|---|"]
for m, s in summary.items():
    p = s["precheck"]
    L.append(f"| {m} | {pc(p['all52'])} | {pc(p['llmRouted'])} | {pc(p['b1-competitor-app'])} | {pc(p['b2-boar'])} | {p['all52']['refused']}/{p['all52']['n']} = {p['all52']['refusedRate']:.0%} | {cw(p['all52'])} |")
L += ["", "### By category (pass / n)", "", "| Category | " + " | ".join(summary) + " |", "|---|" + "---|" * len(summary)]
for c in next(iter(summary.values()))["precheck"]["byCategory"]:
    L.append(f"| {c} | " + " | ".join(f"{s['precheck']['byCategory'][c]['pass']}/{s['precheck']['byCategory'][c]['n']}" for s in summary.values()) + " |")
L += ["", "## v2 judge (blind pairwise vs Opus+web, both orders, disagreement = tie)", "",
      "| Model | n | win score (bootstrap 95% CI) | W / T / L | order-consistent | quality ratio |", "|---|---:|---|---|---:|---:|"]
for m, s in summary.items():
    j = s["judgeV2"]
    if j:
        L.append(f"| {m} | {j['n']} | {j['winScore']:.2f} ({j['ci'][0]:.2f}–{j['ci'][1]:.2f}) | {j['wins']} / {j['ties']} / {j['losses']} | {j['consistent']}/{j['n']} | {j['qualityRatio']:.2f} |")
    else:
        L.append(f"| {m} | — | not judged yet | | | |")
open(f"{exp}/results/summary.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
