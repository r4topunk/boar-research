# SUPPORT criterion (FROZEN before any Haiku call, 2026-10-23): does a JUDGED support flag separate good from bad answers on real dev items?

Follow-up to B-TABLE (lexical chunk-level "fact delivered" flag: delivered cell U 0.420 vs 0.419, NOT PUBLISHABLE). Existing traces only: 0 generation, Opus 0, paid 0, phone 0, no pushes, no commits. Never read blind/, rnd/veil/, bench/v0.4.

## Flag
SUPPORT = YES iff at least ONE single kept chunk states, or directly entails, a central answer-bearing claim of the gold answer (judged by Haiku 5.5-low); otherwise NO. A kept list with 0 chunks is NO without a call.
Inputs per unit: question, gold answer (v0.1: boar-eval/bench/v0.1/refs/refs.jsonl `answer`; cm: selftest refs.jsonl `answer`), rubric (questions.public.jsonl / selftest questions.jsonl `rubric` list), kept chunks as `[n] Title\nbody` blocks.
Kept chunk texts = the matching REPLAY keptFull (the same source the lexical flag uses): arm = coverage-map/sefix/replays/main.F1F2F4.jsonl (gidf+F1F2F4 on K13), control = retrieve-sweep/replay/B0.main.jsonl (as B-TABLE's control flag). Live-title parity with the replay (arm 93/97, control 91/97 at prep) is reported; sensitivity on parity items.
Unit = (item, ordered kept-chunk bodies); arm and control share a unit (one call) when identical. Seeds 42 and 43 share kept lists (97/97 identical titles, checked at prep), so one label per unit serves both seeds (labels are made once; "seed 42 only" = one call per unit, applied to both).
Prep: tools/prep.py (0 LLM). Prep result before any call: 133 units (arm 77 + control 63 non-empty, 7 shared; 20 arm / 34 control items have 0 kept chunks).

## Calls (tools/label.mjs; Haiku 5.5-low via boar-eval eval-lib runClaude = judge.mjs client; tools none; JSON schema output)
Call A: chunks in original order. Output {label: SUPPORTS|NOT_SUPPORTS, confidence: clear|borderline}.
Call B (only when A's confidence = borderline): chunks reversed (renumbered 1..n), same prompt. If A.label != B.label -> call C (original order, same prompt as A); majority of A/B/C (GATE17S tie-break). If B agrees with A, the label stands.
Retry an errored call once; unresolved -> stop and report. Ledger: arms/night-1023/CALLS.md (created now). Cap Haiku <= 250 in total tonight for this task. Order of spending: all A calls first, then B, then C; if the next call would take the total over 245, remaining B/C calls are skipped, the first label stands and the unit is flagged `single` (count reported).

System prompt (exact): "You are a strict support auditor. You only judge whether the source chunks contain the information a reference answer needs. Whether anything is true in the real world is irrelevant."
User prompt (exact; {Q}, {GOLD}, {RUBRIC} one `- ` line per point, {CHUNKS} substituted):
"QUESTION:\n{Q}\n\nREFERENCE ANSWER:\n{GOLD}\n\nRUBRIC (what a good answer must contain):\n{RUBRIC}\n\nSOURCE CHUNKS:\n{CHUNKS}\n\nLabel SUPPORTS only if at least one single source chunk states, or directly entails, a central answer-bearing claim of the reference answer, that is, a claim that one of the non-'Penalize' rubric points asks for and without which the question cannot be answered well. Label NOT_SUPPORTS if the chunks only share the topic or keywords, give only background, contain only claims peripheral to the question, or if the needed claim is spread over several chunks so that no single chunk states it. Ignore your own knowledge of whether the reference answer or the chunks are true. Set confidence to \"clear\" when the label is unambiguous and \"borderline\" when a reasonable auditor could label it the other way. Reply with the JSON {\"label\": \"SUPPORTS\" | \"NOT_SUPPORTS\", \"confidence\": \"clear\" | \"borderline\"}."

## Reads (tools/support_agg.py; 0 LLM; reuses b_agg.py machinery: judged correctness rows, U = ratio of sums with declined -> 0, CE = answered with corr <= 1.5, band = mean judged correctness >= 3.5)
1. 2x2 (support yes/no x band) with n, U, CE per cell and gap U(yes) - U(no) with item bootstrap CI (B 2000, random.Random(11), both groups resampled together), per set (MAIN 97 = 92 keyed + 5 unkeyed; MAIN 92 keyed; v0.1 57 (= 52 keyed + 5 unkeyed); cm 40), per arm (arm rows split by the arm's support flag; control rows by the control's), per seed (42 primary, 43, pooled = per-item mean of the two seeds as b_agg). Also the band-share gap.
2. Support share (yes / n) per arm and set.
3. Agreement with the lexical chunk-level flag (FLAG 'sefix F1F2F4' for the arm, 'B0 stock (retrieve-sweep)' for the control), on the 92 keyed items (also v0.1 52, cm 40): 2x2 confusion matrix, raw agreement, Cohen kappa.
4. Within-item arm-minus-control dU (paired, as b_agg pair) split by the arm's support flag (yes / no), seeds 42, 43, pooled, MAIN 97; plus the count of items whose support flips control NO -> arm YES.
5. Sensitivity: live-title parity subset (items whose live kept titles equal the replay's, per arm); lexical-yes x support-yes cross cells (U of each).

## Rule (frozen)
The research claim HOLDS on real items iff, on MAIN 97 at seed 42, the support-yes cell beats the support-no cell by >= +0.2 U with bootstrap CI low > 0 in BOTH arms (arm and control). Seed 43 and pooled are reported as replication (same labels), not part of the rule. Otherwise it does NOT hold (a one-arm pass is reported as PARTIAL, still not HOLDS).
Prediction (frozen): support flags 30-40 % of items; gap +0.15...+0.3; agreement with the lexical flag about 70 %.
Caveats to state: Haiku labels (judge strictness untested against a human), dev items only, replay chunk texts (not the live prompt), observational split (item difficulty confounds).
