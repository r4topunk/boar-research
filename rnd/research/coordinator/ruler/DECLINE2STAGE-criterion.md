# DECLINE2STAGE criterion (frozen 2026-10-21 before any call; revisit-closed-2026-10-21.json entry "JUDGE v1.1 / v1.1b / RV1 U_CU")

## Design
- Stage 1: one Haiku 5.5-low call per answer (claude-haiku-5-5, --effort low, claude -p, no tools, structured output {attempted: yes|no}). Input = the question and the answer only (no references, no checklist, no rubric notes).
  Tool: ruler/tools/decline2stage_stage1.mjs (sha256 9599c1baa3cabdada00c1566d01356bc1074575b297dc2baf781bfe5c00e49d8), stage1Version decline2stage.s1.v1. Not inside judge.mjs.
- Exact prompt line (verbatim): "Does the answer attempt to answer the question (give any substantive claim about it)? yes/no"
  System prompt: "You are a strict binary classifier. You read a question and an answer and return the requested JSON field only."
  User prompt = the line above, a blank line, <question>…</question>, <answer>…</answer>, then: Reply "yes" if the answer attempts to answer the question, "no" if it does not.
- Temperature: claude -p exposes no temperature setting, so temperature 0 is NOT controllable; stated per spec §6 ("otherwise stated as not controllable"). Test-retest on 20 texts measures the residual noise.
- Stage 2: judge.v1 unchanged (bytes untouched). Score: s = 0 (true zero; s-1 = 0 on the 1-5 scale in U) if stage 1 says "no", else the v1 score.
- Inputs (0-call prep ruler/tools/decline2stage_prep.py sha256 bb27aaacf033f09d101ca38cd929dfc782f63e7c3c6bd272481c2cc71d0e341b): ruler/decline2stage/in/units.jsonl (sha256 ff4c714fa549c7166ecb33b9f0e64c0b091e3014ac0b2d1f0fcd43479ab3a235), retest.keys (822d4c5b55d1...).
  FLOOR a/b/c: 30 ids x 3 frozen variants (arms/floor-anchors/traces). MAIN: the 97 K0 1.7B control answers (arms/lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl, the MAIN 97 control used by RV1/CV5; arms/null-cal/control holds the st180 pool, not MAIN). WARN: the 51 warned units of WARN-OPUS (W-nh 20 + W-h 31).
  Reference correctness: Opus judge.v1 corr (mean of both orders). MAIN: all 97 have Opus rows on the identical (id, text) (mean over available pairs), so the Haiku fallback is not needed (Haiku corr kept beside it). WARN: WARN-OPUS unit corr.
- Calls: 238 first-pass + 20 repeats (retest.keys: 2 per FLOOR variant, 7 MAIN, 7 WARN; Random('2110-retest')) = 258, hard cap 260 (ledger). 0 Opus, 0 generation, 0 paid, 0 phone, 0 mini. Dev sets only. Primary label = rep 1.

## Bars (all must pass)
- (a) not-attempted recall >= 0.95 on the 90 FLOOR texts (>= 86/90) AND >= 0.90 on variant c alone (>= 27/30).
- (b) false not-attempted <= 1 of the MAIN answers with Opus corr >= 3 (n 49) AND <= 3 of the WARN units with Opus corr >= 3 (n 27).
- (c) CE flips on non-declines = 0 by construction: for every unit stage 1 calls attempted, the DECLINE2STAGE score and CE label (corr <= 1.5) equal the v1 ones (asserted in the analysis script).
- (d) report only (no bar): per-rung correction on the CV5 v0.1 51 ladder from existing v1 rows (Haiku same frame and Opus, via cv5_ladder.py's loaders), 0 extra calls: zero s for detected not-attempted answers; U_D2S next to U and U_net = (U - 0.058)/0.942, plus pair gaps.
  Detection on ladder texts: the stage-1 rep-1 label when the identical (id, text) was classified here (all 51 1.7B texts are MAIN texts; 9 Gemma and 9 4B texts too); otherwise (135 texts, none classified, cap) the existing 0-call labeller arms/null-cal/tools/labels.is_decline as a stated stand-in (it flags 2 of them: Gemma vit-cry-009, 1.5B dng-005).
- Retest: report label agreement on the 20 repeats (no bar).

## Decision
- (a), (b), (c) pass -> PASS: R1 = judge.v1 + DECLINE2STAGE, named in spec §6 (sentence in the report).
- Fails (a) or (b) -> FAIL: stop, no second wording; kill clause: JUDGE-V2.1-NI is the backup, else judge.v1 + U_net with D and the decline-share bias stated in the ruler limits.
