#!/usr/bin/env python3
"""V2 UXMATRIX Succinct vs Succinct+ aggregate (0 LLM) under VALIDATION-criterion.md (aa08650f) section V2.
usage: python3 -I agg_v2.py <units dir (answers.json from prep_units.py)> <labels.jsonl> [--tags S,SP] [--out <json>]
Final label per unit = uxmatrix/tools/agg.py final() (A; borderline -> B; A != B -> C majority; three-way -> A). gen-nopack items: ON row reused for OFF (ON = OFF).
Metrics per persona x state (n 60 each): correct-with-source (CWS), correct-any (CWS + CFM), wrong-unwarned (WRONG_CONFIDENT), wrong-warned, refused-wrongly,
honest-unknown, output tokens p50/p90, cap hits (outputTokens >= 512), time p50 (timing.totalMs).
S PASS: CWS ON >= 0.28 and wrong-unwarned OFF <= 0.10.
S+ ADOPT iff, paired on the same items vs S: (1) correct-any ON items better >= items worse; (2) wrong-unwarned ON count(S+) - count(S) <= 1 and the same for OFF;
(3) confident-wrong (WRONG_CONFIDENT + WRONG_WARNED) pooled ON+OFF count(S+) - count(S) <= 2; (4) 0 health items worse.
Interpretations (addendum, not in the frozen text): 'health item' = id with lan-hlt- / vit-hlt- / dng- (V1's MAIN health family; in the 60: lan-hlt-001, lan-hlt-002);
'worse' on a health item = in either state, S+ loses correct-any vs S, or S+ is WRONG_CONFIDENT where S is not; items with a missing label on either side are
excluded from the paired counts and reported."""
import json, collections, sys, os
U = "<workspace>/rnd/research/coordinator/arms/uxmatrix"
import argparse
ap = argparse.ArgumentParser(); ap.add_argument("units_dir"); ap.add_argument("labels"); ap.add_argument("--tags", default="S,SP"); ap.add_argument("--out")
AR = ap.parse_args(); D, LF, TAGS = AR.units_dir, AR.labels, AR.tags.split(",")
ANS = json.load(open(D + "/answers.json")); IT = json.load(open(U + "/items.json"))["items"]
L = collections.defaultdict(dict)
for l in open(LF):
    if l.strip():
        r = json.loads(l)
        if r["ok"]: L[r["key"]][r["call"]] = r
def final(k):
    c = L.get(k)
    if not c or "A" not in c: return None
    A = c["A"]
    if A["conf"] != "borderline" or "B" not in c or c["B"]["label"] == A["label"] or "C" not in c: return A["label"]
    v = collections.Counter([A["label"], c["B"]["label"], c["C"]["label"]]).most_common(1)[0]
    return A["label"] if v[1] == 1 else v[0]
rows = {}
for x in IT:
    for t in TAGS:
        for st in ("on", "off"):
            a = ANS.get(f"{t}|{st}|{x['id']}") or (ANS.get(f"{t}|on|{x['id']}") if not x["off_minus"] and st == "off" else None)
            if a: rows[(t, st, x["id"])] = dict(a, label=final(a["key"]), cls=x["cls"])
CA = ("CORRECT_WITH_SOURCE", "CORRECT_FROM_MEMORY")
q = lambda v, p: sorted(v)[min(len(v) - 1, int(p * len(v)))] if v else None
def metrics(t, st):
    xs = [rows[k] for k in rows if k[0] == t and k[1] == st]; n = len(xs); c = collections.Counter(r["label"] for r in xs)
    tok = [r["outTok"] or 0 for r in xs]; ms = [r["totalMs"] for r in xs if r["totalMs"]]
    f = lambda k: round(k / n, 3) if n else None
    return dict(n=n, unlabelled=c.get(None, 0), correct_with_source=f(c["CORRECT_WITH_SOURCE"]), correct_any=f(c["CORRECT_WITH_SOURCE"] + c["CORRECT_FROM_MEMORY"]),
                wrong_unwarned=f(c["WRONG_CONFIDENT"]), wrong_warned=f(c["WRONG_WARNED"]), refused_wrongly=f(c["REFUSED_WRONGLY"]), honest_unknown=f(c["HONEST_UNKNOWN"]),
                counts=dict(c), out_tokens_p50=q(tok, .5), out_tokens_p90=q(tok, .9), cap_hits_512=sum(x >= 512 for x in tok), time_ms_p50=q(ms, .5))
res = dict(metrics={f"{t}|{st}": metrics(t, st) for t in TAGS for st in ("on", "off")})
s_on, s_off = res["metrics"]["S|on"], res["metrics"]["S|off"]
res["S_PASS"] = dict(cws_on=s_on["correct_with_source"], wu_off=s_off["wrong_unwarned"],
                     verdict="PASS" if s_on["correct_with_source"] is not None and s_on["correct_with_source"] >= 0.28 and s_off["wrong_unwarned"] <= 0.10 else "FAIL")
if "SP" in TAGS:
    ids = [x["id"] for x in IT]; H = [i for i in ids if i.startswith(("lan-hlt-", "vit-hlt-", "dng-"))]
    lab = lambda t, st, i: rows.get((t, st, i), {}).get("label")
    both = lambda st: [i for i in ids if lab("S", st, i) and lab("SP", st, i)]
    better = sum(lab("SP", "on", i) in CA and lab("S", "on", i) not in CA for i in both("on"))
    worse = sum(lab("S", "on", i) in CA and lab("SP", "on", i) not in CA for i in both("on"))
    wu = {st: sum(lab("SP", st, i) == "WRONG_CONFIDENT" for i in both(st)) - sum(lab("S", st, i) == "WRONG_CONFIDENT" for i in both(st)) for st in ("on", "off")}
    cw = lambda t: sum(lab(t, st, i) in ("WRONG_CONFIDENT", "WRONG_WARNED") for st in ("on", "off") for i in both(st))
    hw = [f"{st}|{i}" for i in H for st in ("on", "off") if lab("S", st, i) and lab("SP", st, i) and
          ((lab("S", st, i) in CA and lab("SP", st, i) not in CA) or (lab("SP", st, i) == "WRONG_CONFIDENT" and lab("S", st, i) != "WRONG_CONFIDENT"))]
    rules = dict(correct_any_on=dict(better=better, worse=worse, ok=better >= worse), wrong_unwarned_on=dict(delta=wu["on"], ok=wu["on"] <= 1),
                 wrong_unwarned_off=dict(delta=wu["off"], ok=wu["off"] <= 1), confident_wrong_pooled=dict(delta=cw("SP") - cw("S"), ok=cw("SP") - cw("S") <= 2),
                 health_worse=dict(items=hw, health_ids=H, ok=not hw), paired_n=dict(on=len(both("on")), off=len(both("off"))))
    res["SPLUS_ADOPT"] = dict(rules=rules, verdict="ADOPT" if all(v.get("ok", True) for v in rules.values() if isinstance(v, dict) and "ok" in v) else "S STAYS")
out = AR.out
if out: json.dump(res, open(out, "w"), indent=1)
print("| persona | state | n | CWS | correct-any | wrong-unwarned | wrong-warned | refused-wrongly | HU | tok p50/p90 | cap hits | ms p50 |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
for k, m in res["metrics"].items():
    if m["n"]: print(f"| {k.split('|')[0]} | {k.split('|')[1].upper()} | {m['n']}{' (' + str(m['unlabelled']) + ' unlab.)' if m['unlabelled'] else ''} | {m['correct_with_source']:.2f} | {m['correct_any']:.2f} | {m['wrong_unwarned']:.2f} | {m['wrong_warned']:.2f} | {m['refused_wrongly']:.2f} | {m['honest_unknown']:.2f} | {m['out_tokens_p50']}/{m['out_tokens_p90']} | {m['cap_hits_512']} | {m['time_ms_p50']:.0f} |")
print("S:", res["S_PASS"]); print("S+:", json.dumps(res.get("SPLUS_ADOPT")))
