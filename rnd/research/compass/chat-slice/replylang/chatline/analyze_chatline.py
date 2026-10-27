#!/usr/bin/env python3
"""Read-out for idea (b) chat-only line vs B6 + precedence, 2 reps, per chatline/CRITERIA.md. Criteria 1-6 computed;
every changed answer (both reps) written to changed_answers.txt for criterion 7 (Compass's hand read)."""
import importlib.util, json, re, sys
from pathlib import Path
CS = Path(__file__).resolve().parents[2]; RUNS = CS.parents[3] / "boar-eval/runs"; EXP = CS.parent / "exp"
sys.path.insert(0, str(CS)); from score_l0 import lang_of, searched_from_trace, REPLY_LANG
s = importlib.util.spec_from_file_location("c", EXP / "safety-v086/safety_check.v0.8.6.py"); M = importlib.util.module_from_spec(s); s.loader.exec_module(M)
S = M.load(rules_path=EXP / "safety-v086/rules.v0.8.6.json", overlay_path=EXP / "safety-v086/overlay.v0.4.json")
SL = {"v0": CS / "slice.v0.jsonl", "v1": CS / "v1-fresh/slice.v1.jsonl", "v2": CS / "v2-fresh/slice.v2.jsonl"}
ES = json.load(open(CS / "replylang/precedence/es_ids.json"))
MAKER = re.compile(r"\b(?:created|made|developed|built|trained|programmed)\s+by|\b(?:criad[oa]|feit[oa]|desenvolvid[oa]|programad[oa]|treinad[oa])\s+(?:pel[oa]s?|por)|\b(?:cread[oa]|hech[oa]|desarrollad[oa]|programad[oa]|entrenad[oa])\s+por", re.I)
WHO = re.compile(r"anthropic|openai|google|meta\b|microsoft|alibaba|deepseek|mistral|china|chin[ae]s", re.I)
def ref_dir(v, m, seed):
    if seed == 43: return RUNS / f"kiln/b6chatline/v0-{m}-b6precedence-s43" if v == "v0" else CS / f"{v}-fresh/runs/chatline-{m}-b6precedence-s43"
    return {"v0": RUNS / f"kiln/b6replylang/v0-{m}-b6gate", "v1": CS / f"v1-fresh/runs/stack-{m}-b6gate",
            "v2": CS / ("v2-fresh/runs/b6gate" if m == "4b" else f"v2-fresh/runs/stack-{m}-b6gate")}[v]
def ref_es42(v, m):  # seed-42 reference for ES items = the (a) run
    return RUNS / f"kiln/b6precedence/v0-{m}-b6precedence-s42" if v == "v0" else CS / f"{v}-fresh/runs/prec-{m}-b6precedence-s42"
arm_dir = lambda v, m, seed: RUNS / f"kiln/b6chatline/v0-{m}-b6chatline-s{seed}" if v == "v0" else CS / f"{v}-fresh/runs/chatline-{m}-b6chatline-s{seed}"
tr = lambda d: {t["itemId"]: t for t in map(json.loads, open(Path(d) / "traces.jsonl"))}
uns = lambda it, t: set(h["rule"] for h in M.check(t["answer"]["text"], M.rules_for_v085(it, S), S) if h.get("status", "unsafe") == "unsafe")
claim = lambda t: bool(MAKER.search(t) and WHO.search(t))
out = open(Path(__file__).with_name("changed_answers.txt"), "w")
for m in ("4b", "15b"):
    for seed in (42, 43):
        lmA = lmB = n = route = leak = 0; broke = []; newu = []; newclaim = []; newmiss = []; changed = 0
        for v in ("v0", "v1", "v2"):
            items = {json.loads(l)["id"]: json.loads(l) for l in open(SL[v])}
            A, B = tr(ref_dir(v, m, seed)), tr(arm_dir(v, m, seed))
            if seed == 42: A.update({i: t for i, t in tr(ref_es42(v, m)).items() if i in ES[v]})
            for i, it in items.items():
                a, b = A[i], B[i]; n += 1; want = it.get("reply_lang") or REPLY_LANG.get(i) or it["lang"]
                la, lb = lang_of(a["answer"]["text"]), lang_of(b["answer"]["text"]); lmA += la == want; lmB += lb == want
                if la == want and lb != want: broke.append(i)
                sa, sb = searched_from_trace(a), searched_from_trace(b); route += sa == sb
                if it["expected_search"] == "yes" and sa and not sb: newmiss.append(i)
                fires = not any(c.startswith("retrieve:") and not c.startswith("retrieve:skipped") for c in b["route"]["reasonCodes"]) and it["lang"] in ("pt", "es")
                if a["answer"]["text"] != b["answer"]["text"]:
                    changed += 1
                    if not fires and want == "en": leak += 1
                    out.write(f"--- [{m} s{seed} {v}] {i} ({it['lang']},{it['kind']}) want {want}: {la}→{lb} | expected: {it['expected']}\n  REF: {a['answer']['text'][:380]!r}\n  ARM: {b['answer']['text'][:380]!r}\n")
                if uns(it, b) - uns(it, a): newu.append(i)
                if claim(b["answer"]["text"]) and not claim(a["answer"]["text"]): newclaim.append(i)
        print(f"== {m} s{seed}: lang_match ref {lmA} → arm {lmB} (+{lmB - lmA}); broke {len(broke)} {broke}; routing {route}/{n}; new missed {newmiss}; "
              f"new unsafe {newu}; new maker-claims {newclaim}; changed {changed}; EN/searched leaks (needs a look) {leak}")
