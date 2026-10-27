#!/usr/bin/env python3
"""LITE7 smoke check (0 LLM): OFF (lite7 tree, LITE_STYLE unset) vs LITE5-180 ON traces (promptTokens, kept, answer text); ON vs OFF prompt dumps
(the only difference must be the two style lines), prompt-token growth, lite:style code presence. Prints counts/numbers; -> runs/smoke/smoke-check.json"""
import json, difflib
A = "<workspace>/rnd/research/coordinator/arms"; S = f"{A}/lite7/runs/smoke"; P = ["boar-medlineplus-en", "qa-health-se"]
ld = lambda f: {(t := json.loads(l))["itemId"]: t for l in open(f) if l.strip()}
tm = lambda t: t.get("timing") or {}; txt = lambda t: (t.get("answer") or {}).get("text") or ""
kept = lambda t: [(s.get("title"), s.get("section")) for s in (t.get("retrieval") or {}).get("kept") or []]
codes = lambda t: t["route"]["reasonCodes"]
r = {"items": {}}
for p in P:
    ON, OFF, L5 = ld(f"{S}/lite7-smoke-on-{p}-s42.traces.jsonl"), ld(f"{S}/lite7-smoke-off-{p}-s42.traces.jsonl"), ld(f"{A}/lite5/runs/180/lite5-180-on-{p}-s42.traces.jsonl")
    dON = [json.loads(l) for l in open(f"{S}/lite7-smoke-on-{p}-s42.prompts.jsonl")]; dOFF = [json.loads(l) for l in open(f"{S}/lite7-smoke-off-{p}-s42.prompts.jsonl")]
    dq = {d["query"]: d["prompt"] for d in dOFF}; nq = {d["query"]: d["prompt"] for d in dON}
    for i in ON:
        on, off, l5 = ON[i], OFF[i], L5[i]; q = on["question"] if isinstance(on.get("question"), str) else (on.get("question") or {}).get("text", "")
        diff = None
        a, b = dq.get(q), nq.get(q)
        if a is not None and b is not None:
            sa, sb = json.dumps(a, ensure_ascii=False, indent=0).splitlines(), json.dumps(b, ensure_ascii=False, indent=0).splitlines()
            diff = [x for x in difflib.unified_diff(sa, sb, lineterm="", n=0) if x[:1] in "+-" and not x.startswith(("+++", "---"))]
        r["items"][i] = {"err": [bool(on.get("error")), bool(off.get("error"))], "lite_style_on": "lite:style" in codes(on), "lite_style_off": "lite:style" in codes(off),
            "pt_off_vs_l5": [tm(off).get("promptTokens"), tm(l5).get("promptTokens")], "pt_on": tm(on).get("promptTokens"),
            "kept_off_eq_l5": kept(off) == kept(l5), "kept_on_eq_off": kept(on) == kept(off), "text_off_eq_l5": txt(off) == txt(l5), "text_on_eq_off": txt(on) == txt(off),
            "words": [len(txt(off).split()), len(txt(on).split())], "reasoning": [tm(on).get("reasoningTokens"), tm(off).get("reasoningTokens")],
            "prompt_diff_lines": None if diff is None else len(diff), "prompt_dump": [a is not None, b is not None]}
        if diff: r.setdefault("diff_example", diff)
g = [v["pt_on"] - v["pt_off_vs_l5"][0] for v in r["items"].values() if v["pt_on"] is not None and v["pt_off_vs_l5"][0] is not None]
r["prompt_growth"] = g; r["prompt_growth_max"] = max(g) if g else None
json.dump(r, open(f"{S}/smoke-check.json", "w"), indent=1); print(json.dumps(r, indent=1, ensure_ascii=False))
