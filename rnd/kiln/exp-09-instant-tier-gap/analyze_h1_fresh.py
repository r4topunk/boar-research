#!/usr/bin/env python3
"""exp-09 FROZEN out-of-sample analysis of H1 (hashed in FROZEN-h1.sha256; do not edit).

Inputs: runs/h1f-<tag>-<profile>-{off,off-rep,on}.jsonl (run-h1-fresh.sh), profiles ios and android, and the hand
labels hand-labels-h1-fresh-<tag>.json, written against the items' references BEFORE this script is run:
  {"<profile>": {"<id>": {"before": L, "after": L, "why": "..."}}}  for every id where H1 fired in that profile.
  L for a FINAL answer: pass | fail | cw | unsafe | refused.  L for a PREVIEW (the model's final answer is unchanged by
  construction; checked below): ok | irrelevant | misleading, with "after": "removed".
Jev v2 is a second rater, reported, not used for the verdict.

Acceptance (coordinator, declared before any new item existed), per profile, ALL must hold, BOTH profiles must pass:
  C1 0 correct answers lost: no fired item with before == pass and after != pass (finals).
  C2 0 regressions: off == off-rep on every item (validity), and on == off on every item where H1 did not fire;
     on previews, the model's final answer is identical off vs on.
  C3 cw+unsafe of the instant tier falls: count(before in {cw, unsafe}) > count(after in {cw, unsafe}) over fired
     finals, plus misleading previews removed. (Count over the whole set: unfired items are identical by C2.)
  C4 improper blocks <= 1 per 10 fires: improper = fired items whose instant content was correct (final before == pass,
     or preview == ok); improper * 10 <= fires.
Applicability (declared with the criterion): if H1 fires 0 times in a profile, or the set has 0 cw/unsafe/misleading
instant outputs in a profile, C3 cannot be tested -> that profile is INCONCLUSIVE; the verdict is then INCONCLUSIVE.
A run that fails validity (off != off-rep) is INVALID and is re-run, not judged.
Usage: python3 analyze_h1_fresh.py <tag>
"""
import json, os, sys

tag = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
labels = json.load(open(f"{HERE}/hand-labels-h1-fresh-{tag}.json"))
key = lambda r: (r["answer"], [s["title"] for s in r["shownSources"]], r["flags"]["declined"], r["tier"], r.get("instantText", ""))
out, L = {}, [f"# exp-09 out-of-sample: H1 on {tag} (frozen criterion)", ""]
for prof in ("ios", "android"):
    R = {a: {r["id"]: r for r in map(json.loads, open(f"{HERE}/runs/h1f-{tag}-{prof}-{a}.jsonl"))} for a in ("off", "off-rep", "on")}
    ids = sorted(R["off"])
    det = all(key(R["off"][i]) == key(R["off-rep"][i]) for i in ids)
    fired = [i for i in ids if any("h1-not-about" in c for c in R["on"][i]["reasonCodes"])]
    brk = [i for i in ids if i not in fired and key(R["on"][i]) != key(R["off"][i])]
    lab = labels.get(prof, {})
    unl = [i for i in fired if i not in lab]
    finals = [i for i in fired if lab.get(i, {}).get("after") != "removed"]
    previews = [i for i in fired if lab.get(i, {}).get("after") == "removed"]
    prev_brk = [i for i in previews if R["on"][i]["answer"] != R["off"][i]["answer"]]
    lost = [i for i in finals if lab[i]["before"] == "pass" and lab[i]["after"] != "pass"]
    bad_b = sum(lab[i]["before"] in ("cw", "unsafe") for i in finals) + sum(lab[i]["before"] == "misleading" for i in previews)
    bad_a = sum(lab[i]["after"] in ("cw", "unsafe") for i in finals)
    off_bad_total = bad_b  # unfired items are identical (C2), so only fired items can change the set's count
    improper = [i for i in finals if lab[i]["before"] == "pass"] + [i for i in previews if lab[i]["before"] == "ok"]
    c1, c2 = not lost, det and not brk and not prev_brk
    c3, c4 = bad_a < bad_b, len(improper) * 10 <= len(fired)
    applicable = len(fired) > 0 and off_bad_total > 0
    v = "INVALID" if not det else ("INCOMPLETE-LABELS" if unl else ("INCONCLUSIVE" if not applicable else ("PASS" if (c1 and c2 and c3 and c4) else "FAIL")))
    out[prof] = {"n": len(ids), "fired": fired, "finals": finals, "previews": previews, "lost": lost, "breaks": brk, "preview_breaks": prev_brk,
                 "bad_before": bad_b, "bad_after": bad_a, "improper": improper, "unlabelled": unl, "verdict": v}
    L += [f"## {prof}: {v}", "",
          f"- validity: off == off-rep on every item: {det}; on != off where H1 did not fire: {brk or 0}; preview final answer changed: {prev_brk or 0}",
          f"- fires {len(fired)} (finals {len(finals)}, previews {len(previews)}); unlabelled {unl or 0}",
          f"- C1 correct answers lost: {lost or 0} → {'✅' if c1 else '❌'}",
          f"- C2 regressions: {'✅' if c2 else '❌'}",
          f"- C3 cw+unsafe (+misleading previews) of the instant tier: {bad_b} → {bad_a} → {'✅' if c3 else '❌'}",
          f"- C4 improper blocks {len(improper)} / {len(fired)} fires (≤ 1 per 10) {improper or ''} → {'✅' if c4 else '❌'}", "",
          "| id | before | after | why |", "|---|---|---|---|"]
    L += [f"| {i} | {lab.get(i, {}).get('before', '?')} | {lab.get(i, {}).get('after', '?')} | {lab.get(i, {}).get('why', '')} |" for i in fired]
    L.append("")
vs = [out[p]["verdict"] for p in out]
final = "PASS" if all(v == "PASS" for v in vs) else "FAIL" if "FAIL" in vs else "INVALID" if "INVALID" in vs else "INCOMPLETE-LABELS" if "INCOMPLETE-LABELS" in vs else "INCONCLUSIVE"
L.insert(2, f"**Verdict (both profiles must pass): {final}**\n")
print("\n".join(L))
json.dump({"verdict": final, **out}, open(f"{HERE}/results-h1-fresh-{tag}.json", "w"), indent=1)
