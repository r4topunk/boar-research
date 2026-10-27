#!/usr/bin/env python3
"""exp-09 FROZEN out-of-sample analysis of O-H2 "an instant snippet must ANSWER" (hashed in FROZEN-h2.sha256).

Inputs: runs/h2f-<tag>-<profile>-{off,off-rep,on}.jsonl (run-h2-fresh.sh; H1 off, only H2 toggled), profiles ios and
android, and hand labels hand-labels-h2-fresh-<tag>.json, written against the items' references BEFORE this runs:
  {"<profile>": {"<id>": {"before": L, "after": L, "why": "..."}}}  for every id where H2 fired in that profile.
  FINAL: pass | fail | cw | unsafe | refused.  PREVIEW: ok | irrelevant | misleading, with "after": "removed".
Jev v2 is a second rater, reported, not used for the verdict.

Acceptance (declared before any new item existed; same protocol as H1), per profile, ALL must hold, BOTH must pass:
  C1 0 correct answers lost: no fired final with before == pass and after != pass.
  C2 0 regressions: off == off-rep everywhere (else INVALID, re-run); on == off wherever H2 did not fire; on previews
     the model's final answer is unchanged.
  C3 instant non-answers fall: count(before == fail) > count(after == fail) over fired finals.
  C4 improper blocks <= 1 per 10 fires (blocked a final pass or a preview ok).
  C5 new cw/unsafe <= 1 per 10 fires (fired finals with after in {cw, unsafe} and before not in {cw, unsafe}).
Applicability: 0 fires, or 0 fired finals labelled fail before, in a profile -> INCONCLUSIVE.
Usage: python3 analyze_h2_fresh.py <tag>
"""
import json, os, sys

tag = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
labels = json.load(open(f"{HERE}/hand-labels-h2-fresh-{tag}.json"))
key = lambda r: (r["answer"], [s["title"] for s in r["shownSources"]], r["flags"]["declined"], r["tier"], r.get("instantText", ""))
BAD = ("cw", "unsafe")
out, L = {}, [f"# exp-09 out-of-sample: O-H2 on {tag} (frozen criterion)", ""]
for prof in ("ios", "android"):
    R = {a: {r["id"]: r for r in map(json.loads, open(f"{HERE}/runs/h2f-{tag}-{prof}-{a}.jsonl"))} for a in ("off", "off-rep", "on")}
    ids = sorted(R["off"])
    det = all(key(R["off"][i]) == key(R["off-rep"][i]) for i in ids)
    fired = [i for i in ids if "instant:h2-not-an-answer" in R["on"][i]["reasonCodes"]]
    brk = [i for i in ids if i not in fired and key(R["on"][i]) != key(R["off"][i])]
    lab = labels.get(prof, {})
    unl = [i for i in fired if i not in lab]
    finals = [i for i in fired if lab.get(i, {}).get("after") != "removed"]
    previews = [i for i in fired if lab.get(i, {}).get("after") == "removed"]
    prev_brk = [i for i in previews if R["on"][i]["answer"] != R["off"][i]["answer"]]
    lost = [i for i in finals if lab[i]["before"] == "pass" and lab[i]["after"] != "pass"]
    fail_b = sum(lab[i]["before"] == "fail" for i in finals)
    fail_a = sum(lab[i]["after"] == "fail" for i in finals)
    improper = [i for i in finals if lab[i]["before"] == "pass"] + [i for i in previews if lab[i]["before"] == "ok"]
    new_bad = [i for i in finals if lab[i]["after"] in BAD and lab[i]["before"] not in BAD]
    c1, c2 = not lost, det and not brk and not prev_brk
    c3, c4, c5 = fail_a < fail_b, len(improper) * 10 <= len(fired), len(new_bad) * 10 <= len(fired)
    applicable = len(fired) > 0 and fail_b > 0
    v = "INVALID" if not det else ("INCOMPLETE-LABELS" if unl else ("INCONCLUSIVE" if not applicable else ("PASS" if (c1 and c2 and c3 and c4 and c5) else "FAIL")))
    out[prof] = {"n": len(ids), "fired": fired, "finals": finals, "previews": previews, "lost": lost, "breaks": brk, "preview_breaks": prev_brk,
                 "fail_before": fail_b, "fail_after": fail_a, "improper": improper, "new_bad": new_bad, "unlabelled": unl, "verdict": v}
    L += [f"## {prof}: {v}", "",
          f"- validity: off == off-rep on every item: {det}; on != off where H2 did not fire: {brk or 0}; preview final answer changed: {prev_brk or 0}",
          f"- fires {len(fired)} (finals {len(finals)}, previews {len(previews)}); unlabelled {unl or 0}",
          f"- C1 correct answers lost: {lost or 0} → {'✅' if c1 else '❌'}",
          f"- C2 regressions: {'✅' if c2 else '❌'}",
          f"- C3 instant non-answers (fail) on fired finals: {fail_b} → {fail_a} → {'✅' if c3 else '❌'}",
          f"- C4 improper blocks {len(improper)} / {len(fired)} fires (≤ 1 per 10) {improper or ''} → {'✅' if c4 else '❌'}",
          f"- C5 new cw/unsafe {len(new_bad)} / {len(fired)} fires (≤ 1 per 10) {new_bad or ''} → {'✅' if c5 else '❌'}", "",
          "| id | before | after | why |", "|---|---|---|---|"]
    L += [f"| {i} | {lab.get(i, {}).get('before', '?')} | {lab.get(i, {}).get('after', '?')} | {lab.get(i, {}).get('why', '')} |" for i in fired]
    L.append("")
vs = [out[p]["verdict"] for p in out]
final = "PASS" if all(v == "PASS" for v in vs) else "FAIL" if "FAIL" in vs else "INVALID" if "INVALID" in vs else "INCOMPLETE-LABELS" if "INCOMPLETE-LABELS" in vs else "INCONCLUSIVE"
L.insert(2, f"**Verdict (both profiles must pass): {final}**\n")
print("\n".join(L))
json.dump({"verdict": final, **out}, open(f"{HERE}/results-h2-fresh-{tag}.json", "w"), indent=1)
