#!/usr/bin/env python3
"""score.py <traces.jsonl> [items.jsonl]: scorer for the cut 4 fresh lookup set (items.jsonl, kind lookup|control).
Works on stub-replay traces (only instant answers are real) and on real-model traces (any tier).
Per item: tier, correct = normalised `expected` (alternatives split on '|') found in answer.text. Controls have no expected answer:
they must NOT finish instant with a one-line extract (instant on a control = fail), whatever the text.
Prints a table, then: lookups total, instant, instant-correct, instant-WRONG (the failure INSTANT-FRAG targets), model-path correct, controls instant.
Exit code 1 when any instant-wrong or control-instant exists."""
import json, re, sys, unicodedata
tr = {t["itemId"]: t for t in map(json.loads, open(sys.argv[1]))}
items = [json.loads(l) for l in open(sys.argv[2] if len(sys.argv) > 2 else __file__.rsplit("/", 1)[0] + "/items.jsonl")]
def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"(?<=\b[a-z])\.(?=[a-z]\b)", "", s)  # D.C. -> dc
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s)).strip()
n = dict(lookup=0, instant=0, instant_ok=0, instant_wrong=0, model=0, model_ok=0, control=0, control_instant=0, missing=0)
bad = []
for it in items:
    t = tr.get(it["id"])
    if not t: n["missing"] += 1; continue
    tier, text = t["route"]["tier"], t["answer"]["text"]
    ok = any(norm(e) and norm(e) in norm(text) for e in it["expected"].split("|")) if it["expected"] else None
    if it["kind"] == "control":
        n["control"] += 1
        if tier == "instant": n["control_instant"] += 1; bad.append((it["id"], "control finished instant", text[:100]))
    else:
        n["lookup"] += 1
        if tier == "instant":
            n["instant"] += 1; n["instant_ok" if ok else "instant_wrong"] += 1
            if not ok: bad.append((it["id"], f"instant WRONG (expected {it['expected']})", text[:100]))
        else:
            n["model"] += 1; n["model_ok"] += bool(ok)
    print(f"{it['id']} {it['kind']:7} {tier:8} {'ok' if ok else ('--' if ok is None else 'NO'):2} {it['question'][:60]}")
print(json.dumps(n)); [print("FAIL", *b) for b in bad]
sys.exit(1 if bad else 0)
