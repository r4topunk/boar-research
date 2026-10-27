#!/usr/bin/env python3
"""L1 targeted slices on bench v0.1 (dev set only: 60 public + 12 safety-track items; the held-out split is never read).

Per front (retrieval/in-kit, routing/chat, out-of-kit answer quality, safety) pick ~24 items where the base
(Android 4B main, and-qwen s42/s43/s44) is furthest below the Opus reference answer, or where past v0.1 arms flipped
the judge label. Writes l1-slices.json + l1-items.tsv (all 72 items with every signal, for audit).

Run: python3 compass/fast-loop/build_l1_slices.py   (from rnd/research; reads boar-eval runs, no model, no network)
"""
import importlib.util, json, re, statistics as st, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
RND = HERE.parent.parent                       # rnd/research
BOAR = RND.parent.parent                       # boar/
EVAL = BOAR / "boar-eval"
RUNS = EVAL / "runs"
sys.path.insert(0, str(EVAL))
from scorers.score import judge_label, judge_pairs  # noqa: E402

BENCH = EVAL / "bench/v0.1"
QS = [json.loads(l) for l in open(BENCH / "questions.public.jsonl")]
SAF = [json.loads(l) for l in open(BENCH / "safety/track.v0.3.jsonl")]
ITEMS = {q["id"]: q for q in QS + SAF}
PUB = [q["id"] for q in QS]
COVER = json.load(open(RND / "sonar/exp/16-deep35-coverage/classes-kitA-v01.json"))  # Sonar, kit A, 60 public items
TAXO = json.load(open(RND / "compass/exp/error-taxonomy/rows.json"))                # base s42/s43 loss class per item

N = RUNS / "night-2026-10-01"
BASE = [(N / "and-qwen-s42.traces.jsonl", N / "and-qwen-s42.judgments.jsonl"),
        (N / "and-qwen-s43.traces.jsonl", N / "and-qwen-s43.judgments.jsonl"),
        (RUNS / "and-qwen-s44/and-qwen-s44.traces.jsonl", RUNS / "and-qwen-s44/and-qwen-s44.judgments.jsonl")]
# v0.1 arms on the same 4B Android base. "pipeline" = same model, one engine/config knob; "model" = model swap.
ARMS = {
    "main-v5":    ("pipeline", [N / "and-main-v5-s42", N / "and-main-v5-s43"]),
    "persona-p2": ("pipeline", [N / "and-persona-p2-s42", N / "and-persona-p2-s43"]),
    "p1-keepkey": ("pipeline", [RUNS / "p1/and-p1-s42-kic", RUNS / "p1/and-p1-s43-kic"]),
    "p2g":        ("pipeline", [RUNS / "p2g/and-p2g-s42", RUNS / "p2g/and-p2g-s43"]),
    "p5-fromto":  ("pipeline", [RUNS / "p5/and-p5-s42-kic", RUNS / "p5/and-p5-s43-kic"]),
    "ios8":       ("pipeline", [RUNS / "ios8/ios8-s42", RUNS / "ios8/ios8-s43"]),
    "gemma":      ("model",    [N / "and-gemma-s42", N / "and-gemma-s43"]),
    "deep35":     ("model",    [N / "deep35/and-deep35-s42", N / "deep35/and-deep35-s43"]),
    "maple":      ("model",    [N / "maple/and-maple-s42", N / "maple/and-maple-s43"]),
}
ANCHOR = RUNS / "anchors-2026-10-02/opus.judgments.jsonl"  # Opus 5.5 no-web answering the bench, vs the same refs

spec = importlib.util.spec_from_file_location("sc7", RND / "compass/exp/safety-v07/safety_check.v0.7.py")
sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
S7 = sc.load(rules_path=RND / "compass/exp/safety-v07/rules.v0.7.json", overlay_path=RND / "compass/exp/safety-v07/overlay.v0.4.json")


def traces(p):
    return {t["itemId"]: t for t in map(json.loads, open(p))}


def pairs(p):
    return {x["queryId"]: x for x in judge_pairs(p, PUB)["pairs"]}


def codes(t):
    return list(t["route"].get("reasonCodes") or [])


def unsafe(t):
    q = ITEMS[t["itemId"]]
    rules = sc.rules_for_v06(q, S7)
    if not rules or t["answer"]["declined"]:
        return 0, 0
    hits = sc.check(t["answer"]["text"], rules, S7)
    return sum(h.get("status", "unsafe") == "unsafe" for h in hits), sum(h.get("status") == "review" for h in hits)


def run_file(stem, kind):
    p = Path(str(stem) + f".{kind}.jsonl")
    return p if p.exists() else None


# ---------------------------------------------------------------- base
bt = [traces(t) for t, _ in BASE]
bj = [pairs(j) for _, j in BASE]
anc = pairs(ANCHOR)
row = {}
for i, q in ITEMS.items():
    ts = [r[i] for r in bt if i in r]
    js = [r[i] for r in bj if i in r]
    tasks = Counter(t["route"]["task"] for t in ts)
    cs = [set(codes(t)) for t in ts]
    us = [unsafe(t) for t in ts]
    r = {"id": i, "cat": q["category"], "lang": q.get("lang"), "danger": bool(q.get("danger")),
         "track": "safety" if i.startswith("saf-") else "public", "cover": COVER.get(i),
         "task": tasks.most_common(1)[0][0] if tasks else None, "task_votes": dict(tasks),
         "retrieve_no": sum("retrieve:no" in c for c in cs), "shown": sum(bool(t["answer"]["shown"]) for t in ts),
         "declined": sum(bool(t["answer"]["declined"]) for t in ts), "runs": len(ts),
         "memory": sum(not t["answer"]["shown"] and not t["answer"]["declined"] for t in ts),
         "unsafe": sum(u for u, _ in us), "review": sum(v for _, v in us),
         "taxo": Counter(x["cat"] for x in TAXO if x["id"] == i).most_common(1)[0][0] if any(x["id"] == i for x in TAXO) else None}
    if js:
        r["base_boar"] = round(st.mean(x["boarMean"] for x in js), 3)
        r["ref"] = round(st.mean(x["refMean"] for x in js), 3)
        r["base_ratio"] = round(r["base_boar"] / r["ref"], 3)
        r["gap"] = round(r["ref"] - r["base_boar"], 3)
        r["base_labels"] = dict(Counter(judge_label(x)[0] for x in js))
        r["base_spread"] = round(max(x["boarMean"] for x in js) - min(x["boarMean"] for x in js), 3)
    if i in anc:
        r["opus_noweb"] = round(anc[i]["boarMean"], 3)
    row[i] = r

# ---------------------------------------------------------------- arms: label flips vs base majority label, route flips
for i in row:
    row[i].update({"flips_pipeline": [], "flips_model": [], "route_flips": [], "unsafe_arms": []})
for arm, (kind, stems) in ARMS.items():
    for stem in stems:
        tp, jp = run_file(stem, "traces"), run_file(stem, "judgments")
        at = traces(tp) if tp else {}
        aj = pairs(jp) if jp else {}
        for i, r in row.items():
            if i in aj and r.get("base_labels"):
                base_lab = max(r["base_labels"], key=r["base_labels"].get)
                lab = judge_label(aj[i])[0]
                d = aj[i]["boarMean"] - r["base_boar"]
                if lab != base_lab or abs(d) >= 1.0:
                    r["flips_" + kind].append(f"{arm}/{Path(stem).name[-8:]}:{base_lab}->{lab}({d:+.2f})")
            if i in at:
                t = at[i]
                if t["route"]["task"] != r["task"] or ("retrieve:no" in codes(t)) != (r["retrieve_no"] > 0):
                    r["route_flips"].append(f"{arm}:{t['route']['task']}")
                u, _ = unsafe(t)
                if u:
                    r["unsafe_arms"].append(arm)

# ---------------------------------------------------------------- selection
def flipn(r):
    return len(r["flips_pipeline"]) + 0.5 * len(r["flips_model"])


def pick(cands, key, n=24):
    return sorted(cands, key=key, reverse=True)[:n]


judged = [r for r in row.values() if "gap" in r]

# 1. retrieval / in-kit: every in-kit item (key or no-key) + not-in-kit items whose loss is retrieval-side
#    (key not retrieved / dropped before prompt / in context not used), ranked by gap + flips.
inkit = [r for r in judged if r["cover"] in ("in-kit-key", "in-kit-no-key")]
ret_side = [r for r in judged if r["cover"] == "not-in-kit" and r["taxo"] and r["taxo"][0] in "234"]
s_ret = inkit + pick([r for r in ret_side if r not in inkit], lambda r: r["gap"] + 0.4 * flipn(r), 24 - len(inkit))

# 2. routing / chat: v0.1 has no conversational items (chat-slice v0 covers those), and no v0.1 arm changed a route
#    (the task classifier is deterministic and untouched by every arm), so "flips" here are score flips. Every v0.1
#    item needs a search, so on v0.1 the router's failure mode is MISSED search. Pick: 8 danger items typed task:chat
#    (worst first: unsafe, memory answers, gap) + 16 non-danger items typed chat or answered from memory (most
#    memory answers, then gap): the items a model-driven router is most likely to stop searching for.
dchat = pick([r for r in row.values() if r["danger"] and r["task"] == "chat"],
             lambda r: r["unsafe"] + r["memory"] / 3 + 0.3 * (r.get("gap") or 0), 8)
nchat = pick([r for r in row.values() if not r["danger"] and (r["task"] == "chat" or r["memory"]) and "gap" in r],
             lambda r: r["memory"] / 3 + (r["task"] == "chat") * 0.5 + 0.3 * r["gap"] + 0.2 * len(r["flips_pipeline"]), 16)
s_route = dchat + nchat

# 3. out-of-kit answer quality: not-in-kit, non-danger, largest gap to the Opus ref, plus pipeline flips.
oof = [r for r in judged if r["cover"] == "not-in-kit" and not r["danger"]]
s_oof = pick(oof, lambda r: r["gap"] + 0.4 * flipn(r) + 0.5 * r["base_labels"].get("cw", 0))

# 4. safety: all 17 danger items + 7 guards = non-danger health/first-aid-adjacent items with any rule selected by topic
#    (false-hit guard) or the most review hits; then health items by gap.
danger = [r for r in row.values() if r["danger"]]
guards = [r for r in row.values() if not r["danger"] and (sc.rules_for_v06(ITEMS[r["id"]], S7) or r["cat"] in ("health",))]
guards = pick(guards, lambda r: r["review"] + r["unsafe"] + len(sc.rules_for_v06(ITEMS[r["id"]], S7)) + 0.1 * (r.get("gap") or 0), 24 - len(danger))
s_saf = danger + guards

FRONTS = {
    "retrieval-inkit": (s_ret, "every in-kit item (kit A: key or no-key) + the not-in-kit items whose base loss is retrieval-side (key not retrieved / dropped before prompt / in context not used), top gap to the Opus ref + arm flips; target metric: key-in-context and judge score"),
    "routing-chat": (s_route, "missed-search guard for a model-driven router: 8 danger items typed task:chat (worst unsafe/memory first) + 16 non-danger items typed chat or answered from memory by the base; every v0.1 item needs a search, so target = search kept on 24/24 + memory-answer rate down, guard = score. No v0.1 arm ever changed a route, so flips here are score flips. Pair with chat-slice v0 (64 conversational items, false-search side)"),
    "outofkit-quality": (s_oof, "not-in-kit non-danger items with the largest gap between the base and the Opus ref (judge.v1, s42/s43/s44), boosted by base cw and by pipeline-arm label flips; target: judge score and cw"),
    "safety": (s_saf, "all 17 v0.1 danger items (5 public + 12 safety track; base 10 unsafe hits / 3 runs under rules v0.7, on dng-002, saf-002, saf-004, vit-hlt-001) + every non-danger item that selects a v0.7 rule by topic or is health (only 6 exist in v0.1, hence 23) to catch false hits and over-warning; target: unsafe = 0, guard: no new unsafe/review on guards, no score loss"),
}


def slim(r):
    keep = ("id", "cat", "lang", "danger", "cover", "task", "base_ratio", "base_boar", "ref", "gap", "base_labels",
            "base_spread", "opus_noweb", "memory", "unsafe", "review", "taxo")
    out = {k: r.get(k) for k in keep if r.get(k) is not None}
    out["base_score"] = r.get("base_ratio") if "base_ratio" in r else {"unsafe_hits_3runs": r["unsafe"], "review_3runs": r["review"], "memory_answers": r["memory"]}
    out["flips"] = r["flips_pipeline"] + r["flips_model"]
    if r["route_flips"]: out["route_flips"] = r["route_flips"]
    if r["unsafe_arms"]: out["unsafe_arms"] = r["unsafe_arms"]
    return out


res = {"version": "l1-slices.v0", "created": "2026-10-02", "owner": "compass",
       "bench": "boar-eval bench v0.1, dev set only (questions.public.jsonl 60 + safety/track.v0.3.jsonl 12); held-out never read",
       "base": {"system": "Android 4B main (qwen3-4b-instruct-2507-q4km, commit 0cfd4a77)", "runs": [str(t.relative_to(BOAR)) for t, _ in BASE],
                "score": "base_ratio = mean judge.v1 boar score / mean Opus-ref score per item over the 3 seeds (same per-item unit as the bench quality ratio); items with no ref (safety track, venue gold) carry unsafe/memory counts instead",
                "safety_rules": "rules v0.7 + overlay v0.4 (topic selection for unmapped items); unsafe = status unsafe, review counted apart"},
       "flip_rule": "an arm run flips an item when its judge label (pass/fail/cw) differs from the base majority label or |boarMean - base mean| >= 1.0; pipeline arms (same 4B) weigh 1, model swaps 0.5",
       "arms": {k: v[0] for k, v in ARMS.items()},
       "use": "L1 per fast-loop.md: 1 rep, full engine via the desktop adapter, deterministic scorer + read every changed answer. Development data: any item that drives a design choice is named in the card; L2 is the first honest number. No freeze at L1 (log commit + slice ids).",
       "slices": {}}
for name, (sel, why) in FRONTS.items():
    ids = [r["id"] for r in sel]
    br = [r["base_ratio"] for r in sel if "base_ratio" in r]
    res["slices"][name] = {"n": len(ids), "rationale": why,
                           "base_mean_ratio": round(st.mean(br), 3) if br else None, "n_judged": len(br),
                           "ids": ids, "items": [slim(r) for r in sel]}
(HERE / "l1-slices.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")

cols = ["id", "cat", "cover", "task", "danger", "base_ratio", "gap", "opus_noweb", "memory", "unsafe", "review", "taxo"]
with open(HERE / "l1-items.tsv", "w") as f:
    f.write("\t".join(cols + ["n_flip_pipe", "n_flip_model", "route_flips", "fronts"]) + "\n")
    for i, r in row.items():
        fr = [n for n, (sel, _) in FRONTS.items() if r in sel]
        f.write("\t".join(str(r.get(c, "")) for c in cols) + f"\t{len(r['flips_pipeline'])}\t{len(r['flips_model'])}\t{len(r['route_flips'])}\t{','.join(fr)}\n")
for name, s in res["slices"].items():
    print(f"{name:18s} n={s['n']:2d} judged={s['n_judged']:2d} base_mean_ratio={s['base_mean_ratio']}")
print("overlap:", Counter(i for s in res["slices"].values() for i in s["ids"]).most_common(5))
