#!/usr/bin/env python3
"""Judge-ready manifest for the morning (0 LLM; ADDENDUM-1 section 2: no judge call tonight). usage: python3 -I judge_ready.py   (after fetch + agg0.py)
Builds the label units where the protocol has a unit builder (V2, S5, S7: UXMATRIX protocol via prep_units.py; V3: v3/prep_agg_v3.py) and counts calls exactly
where the count is fixed before calling (A calls = units; pairwise judge = 2 x ids). B/C re-checks depend on A's borderline flags: given as an upper bound.
Writes night/judge-ready/JUDGE-READY.md + .json. Nothing here calls a model."""
import json, os, subprocess, sys
A = "<workspace>/rnd/research/coordinator/arms"; VD = A + "/validation-1024"; N = VD + "/night"; F = os.environ.get("FETCHED", N + "/fetched")
JR = N + "/judge-ready"; os.makedirs(JR, exist_ok=True)
done = lambda j: os.path.exists(f"{F}/{j}/DONE") or (os.path.exists(f"{F}/{j}/STATUS") and open(f"{F}/{j}/STATUS").read().strip().endswith("DONE"))
agg = lambda j: json.load(open(f"{N}/aggregates/{j}.json")) if os.path.exists(f"{N}/aggregates/{j}.json") else None
def units(out, *runs):
    r = subprocess.run([sys.executable, "-I", N + "/tools/prep_units.py", out, *runs], capture_output=True, text=True)
    return len(json.load(open(out + "/units.json"))["units"]) if r.returncode == 0 else f"prep failed: {r.stderr[-200:]}"
S = []
def row(suite, ready, a_exact, upper, cap, cmd, note=""): S.append(dict(suite=suite, ready=ready, a_calls_exact=a_exact, max_calls=upper, cap=cap, command=cmd, note=note))
# V2 (frozen cap 520)
if done("v2-s") and done("v2-splus"):
    n = units(VD + "/v2/judge", f"S={F}/v2-s/out", f"SP={F}/v2-splus/out")
    row("V2 UXMATRIX S vs S+", True, n, 3 * n if isinstance(n, int) else None, 520,
        f"LABEL_CAP=520 node {N}/tools/label.mjs {VD}/v2/judge/units.json {VD}/v2/judge/labels.jsonl && python3 -I {VD}/v2/agg_v2.py {VD}/v2/judge {VD}/v2/judge/labels.jsonl --out {VD}/v2/v2.json",
        "A on every unit, then B on borderline A, then C on A != B (UXMATRIX used 309 calls for 208 units)")
else: row("V2 UXMATRIX S vs S+", False, None, None, 520, "", "jobs v2-s / v2-splus not DONE")
# S4 MAIN s42 / s43: judge.v1 Haiku 5.5-low N 4 both orders on the items whose answer text differs from SEFIX-124 (divergence-first), 2 calls per id
for s in (42, 43):
    j = f"s4-main-s{s}"; g = agg(j)
    if done(j) and g:
        ids = g["pooled"]["text_differs_ids"]; f = f"{JR}/{j}.ids"; open(f, "w").write("\n".join(ids) + "\n")
        row(f"S4 MAIN s{s}", True, 2 * len(ids), 2 * len(ids), None,
            f"bash {A}/coverage-map/sefix/ans-tools/judge_s43.sh {F}/{j}/out/00-main/traces.jsonl {f} {JR}/{j}-judge rc-s{s}",
            f"{len(ids)} of 97 answers differ from sefix124-main-s{s}; compare with that run's judgments on the same ids (coverage-map/sefix/ans-judge)")
    else: row(f"S4 MAIN s{s}", False, None, 194, None, "", "not DONE / not aggregated (upper bound 2 x 97)")
# V3 layer 2 (frozen cap 220, V3L2-criterion.md)
if done("v3-s"):
    runs = [f"S={F}/v3-s"] + ([f"SP={F}/v3-splus"] if done("v3-splus") else [])
    r = subprocess.run([sys.executable, "-I", VD + "/v3/prep_agg_v3.py", "prep", VD + "/v3/judge", *runs], capture_output=True, text=True)
    row("V3 layer 2", r.returncode == 0, 48, 144, 220,
        f"LABEL_CAP=220 node {VD}/v3/label_v3.mjs {VD}/v3/judge/units.json {VD}/v3/judge/labels.jsonl S  (add ,SP only if V2 ADOPTs S+: +48 A, cut at 220) && python3 -I {VD}/v3/prep_agg_v3.py agg {VD}/v3/judge {VD}/v3/judge/labels.jsonl",
        r.stdout.strip()[-200:] + " | first check history_in_prompt in the agg output (FAIL-INFRA rule)")
else: row("V3 layer 2", False, None, 144, 220, "", "v3-s not DONE")
# S5 PACKPROOF, S7 seed 44: UXMATRIX protocol units (cap to be named by the coordinator)
for j, name in (("s5-packproof", "S5 PACKPROOF ON/OFF"), ("s7-uxm-on-s44", "S7 seed 44 UXMATRIX ON")):
    if done(j):
        n = units(f"{N}/judge/{j}", f"S={F}/{j}/out")
        row(name, True, n, 3 * n if isinstance(n, int) else None, "name it", f"LABEL_CAP=<cap> node {N}/tools/label.mjs {N}/judge/{j}/units.json {N}/judge/{j}/labels.jsonl",
            "aggregate: S5 with packproof/tools/agg.py logic on answers.json; S7 = agg_v2.py --tags S on the ON rows vs V2 S ON (seed 42)")
    else: row(name, False, None, None, None, "", "not DONE")
# S10 topics: TOPICS27-SUCCINCT sentence-support audit (per sentence; batched keys reduce it)
if done("s10-topics"):
    sys.path.insert(0, A + "/topics27/tools"); from split import split
    T = [json.loads(l) for l in open(f"{F}/s10-topics/out/00-topics/traces.jsonl") if l.strip()]
    ns = sum(len(split(t["answer"]["text"] or "")[1]) for t in T)
    row("S10 topics", True, None, ns, "name it", f"copy topics27/tools/prep_succinct.py with gen-succinct -> {F}/s10-topics/out/00-topics, then node {A}/topics27/tools/audit_succinct.mjs <prep.json> <out.jsonl> primary",
        f"{ns} answer sentences over 27 topics (TOPICS27-SUCCINCT used 53 calls for 46 sentences + 7 batched)")
else: row("S10 topics", False, None, None, None, "", "not DONE")
# B-k4comp40: 19 changed MAIN answers, judge.v1 both orders = 38 calls
if done("b-k4comp40-19"):
    f = f"{JR}/b-k4comp40-19.ids"; open(f, "w").write("\n".join(sorted(json.loads(l)["itemId"] for l in open(f"{F}/b-k4comp40-19/out/00-main19/traces.jsonl") if l.strip())) + "\n")
    row("B-k4comp40 19", True, 38, 38, None, f"bash {A}/coverage-map/sefix/ans-tools/judge_s43.sh {F}/b-k4comp40-19/out/00-main19/traces.jsonl {f} {JR}/b19-judge b19",
        "paired against sefix124-main-s42's judgments on the same 19 ids")
else: row("B-k4comp40 19", False, None, 38, None, "", "not DONE")
# ADDENDUM-2 extension (stability columns; the S+ ADOPT rule stays on seed 42)
for tag, js in (("V2 seed 43 S vs S+", ("v2-s-s43", "v2-splus-s43")), ("V2 seed 44 S vs S+ (ON only)", ("v2-s-s44", "v2-splus-s44"))):
    if all(done(j) for j in js):
        out = f"{N}/judge/{js[0]}"; n = units(out, f"S={F}/{js[0]}/out", f"SP={F}/{js[1]}/out")
        row(tag, True, n, 3 * n if isinstance(n, int) else None, "name it", f"LABEL_CAP=<cap> node {N}/tools/label.mjs {out}/units.json {out}/labels.jsonl && python3 -I {VD}/v2/agg_v2.py {out} {out}/labels.jsonl",
            "stability column; units identical to an already-labelled unit can reuse its label by key")
    else: row(tag, False, None, None, None, "", "not DONE (s44 runs only if it starts before 2026-10-24 08:30)")
if done("s5-packproof-splus"):
    n = units(f"{N}/judge/s5-packproof-splus", f"SP={F}/s5-packproof-splus/out")
    row("S5 PACKPROOF ON with S+", True, n, 3 * n if isinstance(n, int) else None, "name it", f"LABEL_CAP=<cap> node {N}/tools/label.mjs {N}/judge/s5-packproof-splus/units.json {N}/judge/s5-packproof-splus/labels.jsonl")
else: row("S5 PACKPROOF ON with S+", False, None, None, None, "", "not DONE")
g = agg("s4-main-splus-s42")
if done("s4-main-splus-s42") and g:
    ids = g["pooled"]["text_differs_ids"]; f = f"{JR}/s4-main-splus-s42.ids"; open(f, "w").write("\n".join(ids) + "\n")
    row("S4 MAIN S+ s42", True, 2 * len(ids), 2 * len(ids), None, f"bash {A}/coverage-map/sefix/ans-tools/judge_s43.sh {F}/s4-main-splus-s42/out/00-main/traces.jsonl {f} {JR}/s4-main-splus-s42-judge rc-splus-s42",
        f"{len(ids)} of 97 differ from the S run on ENGINE-RC (s4-main-s42)")
else: row("S4 MAIN S+ s42", False, None, 194, None, "", "not DONE / not aggregated")
if done("v3-s-s43"):
    r = subprocess.run([sys.executable, "-I", VD + "/v3/prep_agg_v3.py", "prep", N + "/judge/v3-s-s43", f"S={F}/v3-s-s43"], capture_output=True, text=True)
    row("V3 layer 2 seed 43", r.returncode == 0, 48, 144, "name it (V3L2 cap 220 covers seed 42)", f"LABEL_CAP=<cap> node {VD}/v3/label_v3.mjs {N}/judge/v3-s-s43/units.json {N}/judge/v3-s-s43/labels.jsonl S", r.stdout.strip()[-120:])
else: row("V3 layer 2 seed 43", False, None, 144, None, "", "not DONE")
if done("s10-topics-splus"):
    sys.path.insert(0, A + "/topics27/tools"); from split import split
    ns = sum(len(split(json.loads(l)["answer"]["text"] or "")[1]) for l in open(f"{F}/s10-topics-splus/out/00-topics/traces.jsonl") if l.strip())
    row("S10 topics S+", True, None, ns, "name it", "as S10, on fetched/s10-topics-splus", f"{ns} answer sentences")
else: row("S10 topics S+", False, None, None, None, "", "not DONE")
# ADDENDUM-3: 17 v3-s-carry (frozen V3L2 protocol, S), 18 v2-p2 (UXMATRIX protocol next to S, reported only)
if done("v3-s-carry"):
    r = subprocess.run([sys.executable, "-I", VD + "/v3/prep_agg_v3.py", "prep", N + "/judge/v3-s-carry", f"S={F}/v3-s-carry"], capture_output=True, text=True)
    row("V3 layer 2 with subject carry (RS_STICKY=2)", r.returncode == 0, 48, 144, "name it", f"LABEL_CAP=<cap> node {VD}/v3/label_v3.mjs {N}/judge/v3-s-carry/units.json {N}/judge/v3-s-carry/labels.jsonl S", r.stdout.strip()[-120:])
else: row("V3 layer 2 with subject carry (RS_STICKY=2)", False, None, 144, None, "", "not DONE")
if done("v2-p2") and done("v2-s"):
    out = f"{N}/judge/v2-p2"; n = units(out, f"S={F}/v2-s/out", f"SP={F}/v2-p2/out")
    row("V2 two-paragraph (P2) vs S", True, n, 3 * n if isinstance(n, int) else None, "name it", f"LABEL_CAP=<cap> node {N}/tools/label.mjs {out}/units.json {out}/labels.jsonl && python3 -I {VD}/v2/agg_v2.py {out} {out}/labels.jsonl  (SP column = P2; ADOPT rule not applicable)",
        "S units identical to the V2 run's reuse their labels by key")
else: row("V2 two-paragraph (P2) vs S", False, None, None, None, "", "not DONE")
json.dump(S, open(JR + "/JUDGE-READY.json", "w"), indent=1)
md = ["# JUDGE-READY (0 calls made; r4to picks on 10-24)", "", "| suite | ready | A calls exact | max calls | cap | note |", "|---|---|---|---|---|---|"]
md += [f"| {r['suite']} | {r['ready']} | {r['a_calls_exact']} | {r['max_calls']} | {r['cap']} | {r['note']} |" for r in S]
md += ["", "## Commands"] + [f"- {r['suite']}: `{r['command']}`" for r in S if r["command"]]
open(JR + "/JUDGE-READY.md", "w").write("\n".join(md) + "\n"); print("\n".join(md))
