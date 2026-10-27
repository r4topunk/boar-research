#!/usr/bin/env python3
"""Read-out for idea (a) precedence-only vs B6 alone, per precedence/CRITERIA.md. Prints criteria 1-4 and every changed
answer (criterion 5 = Compass's hand read). Paths per Kiln (2026-10-03)."""
import importlib.util, json, sys
from pathlib import Path
CS = Path(__file__).resolve().parents[2]; RUNS = CS.parents[3] / "boar-eval/runs"; EXP = CS.parent / "exp"
sys.path.insert(0, str(CS)); from score_l0 import lang_of, searched_from_trace
s = importlib.util.spec_from_file_location("c", EXP / "safety-v086/safety_check.v0.8.6.py"); M = importlib.util.module_from_spec(s); s.loader.exec_module(M)
S = M.load(rules_path=EXP / "safety-v086/rules.v0.8.6.json", overlay_path=EXP / "safety-v086/overlay.v0.4.json")
ES = json.load(open(Path(__file__).with_name("es_ids.json")))
SL = {"v0": CS / "slice.v0.jsonl", "v1": CS / "v1-fresh/slice.v1.jsonl", "v2": CS / "v2-fresh/slice.v2.jsonl"}
REF = {("v0", "4b"): RUNS / "kiln/b6replylang/v0-4b-b6gate", ("v0", "15b"): RUNS / "kiln/b6replylang/v0-15b-b6gate",
       ("v1", "4b"): CS / "v1-fresh/runs/stack-4b-b6gate", ("v1", "15b"): CS / "v1-fresh/runs/stack-15b-b6gate",
       ("v2", "4b"): CS / "v2-fresh/runs/b6gate", ("v2", "15b"): CS / "v2-fresh/runs/stack-15b-b6gate"}
ARM = {("v0", m): RUNS / f"kiln/b6precedence/v0-{m}-b6precedence-s42" for m in ("4b", "15b")}
ARM.update({(v, m): CS / f"{v}-fresh/runs/prec-{m}-b6precedence-s42" for v in ("v1", "v2") for m in ("4b", "15b")})
tr = lambda d: {t["itemId"]: t for t in map(json.loads, open(Path(d) / "traces.jsonl"))}
uns = lambda it, t: sorted(h["rule"] for h in M.check(t["answer"]["text"], M.rules_for_v085(it, S), S) if h.get("status", "unsafe") == "unsafe")
for m in ("4b", "15b"):
    ident = route = 0; changed = []; newu = []
    for v in ("v0", "v1", "v2"):
        items = {json.loads(l)["id"]: json.loads(l) for l in open(SL[v])}; A, B = tr(REF[(v, m)]), tr(ARM[(v, m)])
        for i in ES[v]:
            a, b = A[i], B[i]; route += searched_from_trace(a) == searched_from_trace(b)
            if a["answer"]["text"] == b["answer"]["text"]: ident += 1
            else: changed.append((v, i, lang_of(a["answer"]["text"]), lang_of(b["answer"]["text"]), a["answer"]["text"][:300], b["answer"]["text"][:300]))
            if set(uns(items[i], b)) - set(uns(items[i], a)): newu.append(i)
    print(f"== {m}: identical {ident}/48 (crit 1 expects 46 + the 2 targets changed); routing {route}/48; new unsafe {newu}")
    for c in changed: print("   CHANGED", c[:4], "\n     B6 :", repr(c[4]), "\n     ARM:", repr(c[5]))
for m in ("4b", "15b"):
    for kind in ("b6precedence", "b6gate"):
        d = CS / f"v2-fresh/runs/prec-{m}-{kind}-s43"
        if d.exists():
            T = tr(d); print(f"== s43 {m} {kind}:", {i: lang_of(T[i]['answer']['text']) for i in ("v2-038", "v2-039") if i in T})
            for i in ("v2-038", "v2-039"):
                if i in T: print(f"     {i}: {T[i]['answer']['text'][:300]!r}")
