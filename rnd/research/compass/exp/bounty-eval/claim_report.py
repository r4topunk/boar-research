#!/usr/bin/env python3
"""Claim-grade report for poidh #31 ('>50% as good as internet + frontier AI'), Compass 2026-10-03.
Implements bench v0.2 analysis plan §3–§8 (frozen in boar-eval bench/v0.2/plan) by CALLING the frozen metric scripts
(floor_metrics.py, paired_gap.py) — no metric is reimplemented here — and lays the numbers out the way the post author or a
bounty contributor needs them: the raw ratio with its CI and a plain verdict vs 0.50; rubric-minimum-removed and
above-always-decline beside it at the same size; per category; per device tier; the 1B-class gap; the
Haiku/Sonnet/Opus/Fable no-web ladder for context; the the post author slice (his own questions) reported separately; speed
from device traces only (desktop-proxy timing is labelled and never the headline).
Run: python3 claim_report.py config.json > REPORT.md   (config schema: see example-config.v01.json)"""
import json, os, subprocess, sys, tempfile, statistics as st
from collections import defaultdict
from pathlib import Path
PLAN = Path("<workspace>/boar-eval/bench/v0.2/plan")
CFG = json.load(open(sys.argv[1])); Q = [json.loads(l) for l in open(CFG["questions"]) if l.strip()]
QCAT = {q["id"]: q["category"] for q in Q}; D = CFG.get("decline_ratio", 0.306); BAR = 0.50
# r4to 2026-10-03: this harness version is ENGLISH ONLY. The primary number is the EN subset; the full set is shown beside it.
PLANG = CFG.get("primary_lang", "en"); PRIMARY = [q["id"] for q in Q if q.get("lang", "en") == PLANG]; ALL_EN = len(PRIMARY) == len(Q)
TMP = Path(tempfile.mkdtemp(prefix="claim-"))

def stage(system):
    """Symlink a system's runs into one dir under unique names (the frozen scripts take --dir + basenames)."""
    names = []
    for i, prefix in enumerate(system["runs"]):
        n = f"{system['key']}-{i}"
        for ext in ("traces.jsonl", "judgments.jsonl"):
            src = Path(f"{prefix}.{ext}")
            if src.exists(): (TMP / f"{n}.{ext}").unlink(missing_ok=True); os.symlink(src.resolve(), TMP / f"{n}.{ext}")
        names.append(n)
    return names

def floor(names, ids=None, stratified=True):
    cmd = [sys.executable, str(PLAN / "floor_metrics.py"), "--dir", str(TMP), "--runs", *names, "--decline-ratio", str(D)]
    if stratified: cmd += ["--questions", CFG["questions"]]
    if ids is not None:
        f = TMP / f"ids-{abs(hash(tuple(sorted(ids))))}.txt"; f.write_text("\n".join(ids)); cmd += ["--ids", str(f)]
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode: return None
    return json.loads(out.stdout)

def gap(a, b):
    cmd = [sys.executable, str(PLAN / "paired_gap.py"), "--dir", str(TMP), "--a", *a, "--b", *b, "--questions", CFG["questions"], "--decline-ratio", str(D)]
    out = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(out.stdout) if out.returncode == 0 else None

fmt = lambda m: f"**{m['point']:.3f}** ({m['ci95'][0]:.3f}–{m['ci95'][1]:.3f})"
def verdict(m):
    lo, hi = m["ci95"]
    if lo > BAR: return "the 95% CI lies **above 0.50**: the bar is met on this set"
    if hi < BAR: return "the 95% CI lies **below 0.50**: the bar is not met on this set"
    return "the 95% CI **contains 0.50**: consistent with the bar, not shown above it" + ("; the point estimate is **below** 0.50" if m["point"] < BAR else "")

def item_scores(prefix):
    """Per item: mean rubric (both orders) of the system and the reference."""
    K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
    J = defaultdict(list)
    for l in open(f"{prefix}.judgments.jsonl"):
        r = json.loads(l)
        if r.get("ok"): J[r["queryId"]].append(r["mapped"])
    return {q: ((mr(v[0]["boar"]) + mr(v[1]["boar"])) / 2, (mr(v[0]["ref"]) + mr(v[1]["ref"])) / 2) for q, v in J.items() if len(v) == 2}

def timing(system):
    rows = []
    for p in system["runs"]:
        for l in open(f"{p}.traces.jsonl"):
            t = json.loads(l).get("timing") or {}
            if t: rows.append(t)
    def pct(k, q):
        v = sorted(x[k] for x in rows if isinstance(x.get(k), (int, float)))
        return v[min(len(v) - 1, int(q * len(v)))] if v else None
    return {"n": len(rows), "ttft_p50": pct("ttftMs", .5), "ttft_p90": pct("ttftMs", .9), "total_p50": pct("totalMs", .5), "total_p90": pct("totalMs", .9),
            "decode_p50": pct("decodeTokPerSec", .5)}

sysmap = {s["key"]: s for s in CFG["systems"] + CFG.get("anchors", [])}
staged = {k: stage(s) for k, s in sysmap.items()}
head = sysmap[CFG["headline"]]
H = floor(staged[head["key"]], PRIMARY); HF = H if ALL_EN else floor(staged[head["key"]])
# Guard (2026-10-03, V-exact): a category with 1 judged item has no within-category item variance, so the stratified
# CI is too narrow. Then the verdict uses the plain two-level CI (same frozen script, --questions omitted) and says so.
JUDGED = set().union(*(item_scores(p).keys() for p in head["runs"])); NCAT = defaultdict(int)
for i in PRIMARY:
    if i in JUDGED: NCAT[QCAT[i]] += 1
THIN = sorted(c for c, n in NCAT.items() if n < 2)
# The main bench keeps the frozen stratified CI (plan §3–§8) and only gets a warning; a slice config opts in with "thin_strata": "plain".
PLAIN = bool(THIN) and CFG.get("thin_strata") == "plain"
if PLAIN: H = floor(staged[head["key"]], PRIMARY, stratified=False); HF = H if ALL_EN else floor(staged[head["key"]], stratified=False)
P = []
P.append(f"# {CFG['title']}\n")
P.append(f"_Bench: {CFG['bench']} · {H['n_items']} judged items · judge `judge.v1` (pairwise, blind, both orders) vs frozen references "
         f"(frontier model **with web**: {CFG.get('reference_recipe', 'see dataset card')}) · seeds: {', '.join(Path(r).name for r in head['runs'])} · generated by `claim_report.py`._\n")
P.append("## Headline\n")
P.append(f"**{head['label']}** ({head['tier']}), **English questions** (n = {H['n_items']}): raw quality ratio vs internet + frontier AI = {fmt(H['raw'])}. Reading: {verdict(H['raw'])}.\n")
P.append("_The full set (all languages) is identical: every item is English._\n" if ALL_EN else f"_Full set, all languages (n = {HF['n_items']}): raw {fmt(HF['raw'])}, {verdict(HF['raw'])}. English is primary for this harness version (r4to, 2026-10-03)._\n")
P.append("| scale | value (95% CI) | what it means |\n|---|---|---|")
P.append(f"| raw ratio (the bar) | {fmt(H['raw'])} | Σ judge rubric of BOAR ÷ Σ judge rubric of the internet+frontier reference |")
P.append(f"| rubric minimum removed | {fmt(H['above_min'])} | same, after subtracting the judge's 1-point floor from both |")
P.append(f"| above an always-decline system | {fmt(H['above_decl'])} | (raw − D) ÷ (1 − D), D = {D} (a system that refuses everything scores {D} raw) |\n")
P.append(f"_CI: plain two-level bootstrap (items, then runs), 2,000 resamples, seed 11 (`floor_metrics.py`, frozen, without `--questions`). "
         f"The stratified CI is not used because {len(THIN)} categor{'y has' if len(THIN) == 1 else 'ies have'} a single judged item ({', '.join(THIN)}), which makes it too narrow. "
         f"The system table below still shows the stratified CIs._\n" if PLAIN else
         f"_CI: stratified two-level bootstrap (items within category, then runs), 2,000 resamples, seed 11 (`floor_metrics.py`, frozen)._"
         + (f" _Warning: {len(THIN)} categor{'y has' if len(THIN) == 1 else 'ies have'} a single judged item ({', '.join(THIN)}); the stratified CI is somewhat too narrow there._" if THIN else "") + "\n")
P.append("## Every system on the same items\n")
P.append("| system | tier | n (EN) | raw, EN (CI) | min removed, EN (CI) | above decline, EN (CI) | verdict vs 0.50 (EN) | raw, full set (CI) |\n|---|---|---|---|---|---|---|---|")
res = {}
for k, s in sysmap.items():
    m = floor(staged[k], PRIMARY); res[k] = m
    mf = m if ALL_EN else floor(staged[k])
    if not m: P.append(f"| {s['label']} | {s.get('tier','context')} | — | not judged on these items | | | | |"); continue
    P.append(f"| {s['label']} | {s.get('tier', 'context')} | {m['n_items']} | {fmt(m['raw'])} | {fmt(m['above_min'])} | {fmt(m['above_decl'])} | {verdict(m['raw']).split(':')[0].replace('the 95% CI ', '')} | {fmt(mf['raw']) if mf else '—'}{' (= EN)' if ALL_EN else ''} |")
P.append("\n_Ladder rows (no web, single run) are context: they show where frontier models without internet land on the same judge. "
         "A system above Haiku-no-web but below Opus-no-web is a different claim from 'above the bar'._\n")
if CFG.get("one_b_baseline"):
    g = gap(staged[head["key"]], staged[CFG["one_b_baseline"]])
    if g:
        rows = [(k, {"point": v["gap_a_minus_b"], "ci95": v["ci95"]}) for k, v in g.items() if isinstance(v, dict) and "gap_a_minus_b" in v]
        P.append(f"## Gap to the 1B-class configuration ({sysmap[CFG['one_b_baseline']]['label']}), paired (n = {g['n_items']}{', all English' if ALL_EN else ', FULL SET: paired_gap.py has no language filter'})\n")
        P.append("| scale | headline minus 1B-class (95% CI) |\n|---|---|"); P += [f"| {k} | {fmt(v)} |" for k, v in rows]; P.append("")
P.append("## Per category (headline system, English questions)\n")
P.append("| category | n | raw (CI) | min removed (CI) | above decline (CI) |\n|---|---|---|---|---|")
cats = defaultdict(list)
for q in Q:
    if q.get("lang", "en") == PLANG: cats[q["category"]].append(q["id"])
for c, ids in sorted(cats.items()):
    m = floor(staged[head["key"]], ids, stratified=False)
    if m and m["n_items"]: P.append(f"| {c} | {m['n_items']} | {fmt(m['raw'])} | {fmt(m['above_min'])} | {fmt(m['above_decl'])} |")
P.append("\n_Per-category CIs are wide at these n; read them as where the gap is, not as separate claims._\n")
P.append("## Per device tier\n")
P.append("| tier | system | raw (CI) | speed source | first token p50 / p90 | full answer p50 / p90 | decode tok/s p50 |\n|---|---|---|---|---|---|---|")
for k, s in sysmap.items():
    if s.get("kind") != "boar" or not res.get(k): continue
    t = timing(s); sec = lambda v: f"{v/1000:.1f} s" if v else "—"
    P.append(f"| {s['tier']} | {s['label']} | {fmt(res[k]['raw'])} | {s.get('timing_source', 'unknown')} | {sec(t['ttft_p50'])} / {sec(t['ttft_p90'])} | {sec(t['total_p50'])} / {sec(t['total_p90'])} | {t['decode_p50'] or '—'} |")
P.append("\n_Speed is a headline only when `speed source` is **device**. Desktop-proxy timing is shown for completeness and labelled._\n")
ninst = {k: sum(1 for p in s["runs"] for l in open(f"{p}.traces.jsonl") if (json.loads(l).get("route") or {}).get("tier") == "instant") for k, s in sysmap.items() if s.get("kind") == "boar"}
ntr = {k: sum(1 for p in s["runs"] for l in open(f"{p}.traces.jsonl") if l.strip()) for k, s in sysmap.items() if s.get("kind") == "boar"}
if any(ninst.values()): P.append("_Timings pool every trace, including instant-tier answers (no model generation): " + "; ".join(f"{sysmap[k]['label']} {ninst[k]}/{ntr[k]}" for k in ninst) + ". Percentiles are low when the slice is mostly instant answers._\n")
for sl in CFG.get("slices", []):
    ids = [l.strip() for l in open(sl["ids"]) if l.strip()]
    P.append(f"## {sl['title']} (reported separately)\n")
    P.append(sl.get("note", "") + "\n")
    m = floor(staged[head["key"]], ids, stratified=False)
    if m and m["n_items"]: P.append(f"Headline system on this slice: raw {fmt(m['raw'])}, min removed {fmt(m['above_min'])}, above decline {fmt(m['above_decl'])} (n = {m['n_items']}; plain two-level bootstrap).\n")
    if sl.get("per_item"):
        P.append("| item | question | " + " | ".join(sysmap[k]["label"] for k in sl["per_item"]) + " |\n|---|---|" + "---|" * len(sl["per_item"]))
        sc = {k: {} for k in sl["per_item"]}
        for k in sl["per_item"]:
            for p in sysmap[k]["runs"]:
                for q, v in item_scores(p).items(): sc[k].setdefault(q, []).append(v)
        qtext = {q["id"]: q["question"] for q in Q}
        for i in ids:
            cells = []
            for k in sl["per_item"]:
                v = sc[k].get(i)
                cells.append(f"{st.mean(x[0] for x in v) / st.mean(x[1] for x in v):.2f}" if v else "—")
            P.append(f"| {i} | {qtext.get(i, '')[:70]} | " + " | ".join(cells) + " |")
        P.append("\n_Per-item ratio = mean system rubric ÷ mean reference rubric for that item (1.00 = judged as good as internet + frontier)._\n")
P.append("## Method and caveats\n")
P += [f"- {x}" for x in CFG.get("caveats", [])]
print("\n".join(P))
