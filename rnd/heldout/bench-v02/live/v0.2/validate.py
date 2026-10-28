#!/usr/bin/env python3
"""Validate bench v0.2-new (questions.v02-new.jsonl). Reuses bench/v0.1/validate.py (schema subset interpreter, precheck)
and scorers/vendor/safety/safety_check.v0.5.py (rules v0.5). Exit 1 on any failure.

Checks: 110 items, unique ids, category counts; v0.2 schema (subset interpreter; also jsonschema 2020-12 if installed);
each gold answer passes its own precheck; every precheck term compiles, no echo-only group; origin veil-v0.2, lang en,
http(s) sources; danger items carry safety_rules with known v0.5 ids, and each danger gold passes its own rules;
refs/MANIFEST.jsonl (if present) has known ids and matches refs.jsonl when that private file is present.
Usage (from boar-eval/): python3 bench/v0.2/validate.py
"""
import hashlib, json, re, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / "v0.1"))
from validate import schema_errors, grade, compile_term, is_echo, norm  # noqa: E402
import importlib.util  # noqa: E402
SAFETY = ROOT / "scorers/vendor/safety"
_spec = importlib.util.spec_from_file_location("safety_check_v05", SAFETY / "safety_check.v0.5.py")
sc = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(sc)

COUNTS = {"explanation": 21, "reasoning": 21, "comparison": 13, "crypto": 13, "honesty-refusal": 12, "health": 8,
          "danger": 10, "synthesis": 6, "travel-practical": 4, "travel-local": 2}
fails = []
def check(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f": {detail}" if detail else ""))
    if not ok: fails.append(name)


def main():
    items = [json.loads(l) for l in (HERE / "questions.v02-new.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    ids = [i["id"] for i in items]
    check("110 items, unique ids", len(items) == 110 and len(set(ids)) == 110, f"{len(items)} / {len(set(ids))}")
    cnt = dict(Counter(i["category"] for i in items))
    check("category counts", cnt == COUNTS, str(cnt))
    S = json.loads((HERE / "questions.schema.json").read_text())
    errs = [f"{i['id']}: {e}" for i in items for e in schema_errors(i, S, S)]
    try:
        import jsonschema
        errs += [f"{i['id']}: {e.message}" for i in items for e in jsonschema.Draft202012Validator(S).iter_errors(i)]
        how = "subset + jsonschema"
    except ImportError:
        how = "subset only (jsonschema not installed)"
    check(f"schema v0.2 ({how})", not errs, "; ".join(errs[:6]))
    st = [f"{i['id']}: {grade(i, i['answer'])}" for i in items if grade(i, i["answer"]) != "pass"]
    check("each gold answer passes its own precheck", not st, "; ".join(st))
    perr = []
    for it in items:
        g = it["grading"]
        if g["type"] != "precheck": perr.append(f"{it['id']}: {g['type']}"); continue
        for t in [t for grp in g.get("must_any", []) + g.get("forbid", []) for t in grp] + g.get("must_k", {}).get("terms", []):
            try: compile_term(t)
            except re.error as e: perr.append(f"{it['id']}: {t!r}: {e}")
        if any(all(is_echo(t, norm(it["question"])) for t in grp) for grp in g.get("must_any", [])): perr.append(f"{it['id']}: echo-only")
    check("precheck terms compile, no echo-only group", not perr, "; ".join(perr))
    oerr = [i["id"] for i in items if i["origin"] != "veil-v0.2" or i["lang"] != "en" or not i.get("answer")
            or not all(re.match(r"^https?://", u) for u in i["reference_sources"])]
    check("origin veil-v0.2, lang en, gold answer, URL sources", not oerr, str(oerr))
    SS = sc.load(rules_path=SAFETY / "rules.v0.5.json", overlay_path=SAFETY / "overlay.v0.4.json")  # no overlay.v0.5; overlay unused
    serr = []
    for it in items:
        if it["danger"]:
            if "safety_rules" not in it: serr.append(f"{it['id']}: missing"); continue
            unk = [r for r in it["safety_rules"] if r not in SS["meta"]]
            if unk: serr.append(f"{it['id']}: unknown {unk}")
            hit = sc.check(it["answer"], it["safety_rules"], SS)
            if hit: serr.append(f"{it['id']}: gold trips {[h['rule'] for h in hit]}")
        elif "safety_rules" in it: serr.append(f"{it['id']}: safety_rules on a non-danger item")
    nd = [i for i in items if i["danger"]]
    check("safety_rules (rules v0.5): known ids, golds pass", not serr,
          f"{len(nd)} danger items, {sum(bool(i['safety_rules']) for i in nd)} mapped, {sum(not i['safety_rules'] for i in nd)} need a new rule" + (f"; {serr}" if serr else ""))
    mp = HERE / "refs/MANIFEST.jsonl"
    if mp.exists():
        man = [json.loads(l) for l in mp.read_text().splitlines() if l.strip()]
        check("refs MANIFEST ids known", {m["id"] for m in man} <= set(ids), f"{len(man)}/{len(items)} rows")
        rp = HERE / "refs/refs.jsonl"
        if rp.exists():
            rows = {r["id"]: r for r in map(json.loads, rp.read_text(encoding="utf-8").splitlines())}
            q = {i["id"]: i["question"] for i in items}
            bad = [m["id"] for m in man if m["id"] not in rows or hashlib.sha256(rows[m["id"]]["answer"].encode()).hexdigest() != m["sha256"]
                   or rows[m["id"]]["question"] != q[m["id"]]]
            check("refs.jsonl hashes match MANIFEST and questions", not bad, str(bad))
    print(f"\n{'OK' if not fails else 'FAILED'}: {len(fails)} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
