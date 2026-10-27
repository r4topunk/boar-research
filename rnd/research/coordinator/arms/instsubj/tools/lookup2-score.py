#!/usr/bin/env python3
"""lookup2-score.py <items.jsonl> <label=traces.jsonl> [<label=traces.jsonl> ...]: scorer for the INSTANT-SUBJ lookup set #2.
Items: {id, kind: lookup|control, question, expected}. Traces: stub-replay or real-model traces (route.tier, answer.text).
Per arm it reports: instant-final count, WRONG instant-final count, CORRECT instant-final count (lookups), controls finishing instant,
and the list of wrong instant-final items. Correct = a normalised `expected` alternative ('|' separated) is found in answer.text.
Criterion (INSTSUBJ): wrong instant-final = 0 for the INSTANT-SUBJ arm; correct instant lost vs the baseline arm <= 1.
With >= 2 arms the first is the baseline: prints instant-correct lost / gained and wrong removed relative to it. Exit 1 when the LAST arm has any wrong instant-final."""
import json, re, sys, unicodedata
items = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
arms = [a.split("=", 1) for a in sys.argv[2:]]
def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"(?<=\b[a-z])\.(?=[a-z]\b)", "", s)  # D.C. -> dc
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s)).strip()
def correct(it, text):
    return any(norm(e) and norm(e) in norm(text) for e in (it.get("expected") or "").split("|"))
res = {}
for label, path in arms:
    tr = {t["itemId"]: t for t in (json.loads(l) for l in open(path) if l.strip())}
    r = dict(instant=0, wrong=0, correct=0, control_instant=0, missing=0, ok_ids=set(), wrong_ids=[])
    for it in items:
        t = tr.get(it["id"])
        if not t: r["missing"] += 1; continue
        if t["route"]["tier"] != "instant": continue
        if it["kind"] == "control": r["control_instant"] += 1; continue
        r["instant"] += 1
        if correct(it, t["answer"]["text"]): r["correct"] += 1; r["ok_ids"].add(it["id"])
        else: r["wrong"] += 1; r["wrong_ids"].append((it["id"], it["question"][:60], t["answer"]["text"][:100]))
    res[label] = r
    print(f"{label}: instant-final {r['instant']} | wrong {r['wrong']} | correct {r['correct']} | control-instant {r['control_instant']} | missing {r['missing']}")
    for w in r["wrong_ids"]: print("   WRONG", *w)
if len(arms) > 1:
    b, l = res[arms[0][0]], res[arms[-1][0]]
    print(f"vs baseline {arms[0][0]}: correct instant lost {sorted(b['ok_ids'] - l['ok_ids'])}, gained {sorted(l['ok_ids'] - b['ok_ids'])}, wrong {b['wrong']} -> {l['wrong']}")
sys.exit(1 if res[arms[-1][0]]["wrong"] else 0)
