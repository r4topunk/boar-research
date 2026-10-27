# FACTS r4 criterion (frozen 2026-10-06 22:4x, before any code). r4to GO (T1 of HANDOFF-2026-10-07).

Scope (code only; asset facts table unchanged, sha f4d3ab2e…; base wt/facts 45d5d058 = r3):
1. SAFE-LOWERCASE rule for multi-word names: a lowercase (or mixed-case) n-gram of ≥ 2 words resolves only when the
   whole n-gram, case-folded, equals exactly one label/alias of exactly one entity in the table, no word of it is on the
   risk list (homonym/common-word list of r3), and the glue guard of r3 still applies to any capitalised neighbour.
   One-word lowercase names keep the r3 rule (countries/capitals only). Optional leading "the" allowed ("the philippines").
2. TYPO-TOLERANT "the": the tokens thw, teh, hte, tje, th are read as "the" only when immediately followed by a name that
   resolves under rule 1 or the r3 rules. No other typo tolerance.
Nothing else changes (no template, data, or property change). Time box 3 h of agent time.

Scorer: tools/recall_score.mts v2 = v1 + transliteration fold (đ→d, ł→l, ø→o, ß→ss, æ→ae, œ→oe) applied to both sides.
Pre-registered because set 2 had 2 artefacts (đồng, złoty). v2 must reproduce r3 on set 2 as 27/40 (the 2 artefacts now
correct) and on set 1 as 30/40, before scoring r4. Any other scorer change invalidates the run.

Dev measures (after code; sets 1 and 2 are DEV now, set 2 burnt by r3's fix selection):
- recall-set.jsonl (414e4de2…) and recall-set-2.jsonl (d0dc7512…): recall, precision, FP; expected set 2 ≈ 85–90 %.
- Gates: G1 tsc 0 + full vitest green; 13 DATA-REVIEW probes 0 fires and output identical to r3; G2 precheck 7/8 with the
  8 target answers byte-identical to r3; G3 0/52 v0.1, 0/12 safety, 0/11 V-exact, dev chat 2/192 (same two items);
  G4 replay non-target raw lists 52/52 identical to cut 6; G5 warm p95 ≤ 1 ms.
- Fresh precision probes written by the r4 agent itself (≥ 15, lowercase homonyms: "paris hilton", "new york times",
  "lake wobegon", "mont blanc pen", "amazon prime", "georgia tech" ...): 0 fires. Dev only.

Blind set 3 (recall-set-3.jsonl, 40 fact + 20 near-miss): written by a SEPARATE agent that has not read arms/facts/*,
wt/facts, or this file beyond the schema block given to it; sha256 recorded in recall-set-3.sha256 BEFORE the r4 code is
run on it. The r4 agent never sees set 3 before its final build is committed. ONE run on set 3. No edit after.

Verdict on set 3 (scorer v2, frozen rule):
- PASS: recall ≥ 85 % (≥ 34/40) AND FP 0/20 AND precision ≥ 90 % AND all gates green.
- PARTIAL: recall 75–84 % AND FP 0/20 AND gates green → r4 kept as the FACTS head; cut-7 decision deferred to r4to.
- FAIL: FP ≥ 1/20, or recall < 75 %, or any gate red → r4 NOT adopted, report the cause, no rescue, no r5 same day.
Set 3 is burnt after this run whatever the verdict. Judge: none (deterministic arm). Dev only: no blind/, no v0.2, no V-para.

## Addendum 1 (2026-10-06 22:38, before any r4 code, set 3 unseen by the r4 agent)
Scorer v2 reproduction measured on r3 (45d5d058): set 1 30/40 (as expected); set 2 **26/40**, not 27/40. The second set-2
artefact (r2-f33, expect "Polish zloty", answer "złoty") is an expect-wording issue, not a transliteration one. Decision:
NO scorer v3; the frozen scorer rule stays v2 as written; the expected reproduction for set 2 is corrected to 26/40.
r4 dev numbers on set 2 are compared against 26/40. Nothing else in this criterion changes.
