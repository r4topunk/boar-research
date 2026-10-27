# RV1-HON8 criterion: RV1-DECLINE-CU + HON-8 REVEAL-RULE (frozen 2026-10-21, before any number below is computed)

0 LLM, 0 judge, 0 generation, 0 paid. Inputs are existing judge.v1 rows (Haiku 5.5-low, both orders; Opus judge.v1 rows of WARN-OPUS and CE-OPUS-RU) and existing dev traces. No blind/, no rnd/veil, no bench/v0.4 file is read.

## RV1-DECLINE-CU (verbatim from hypotheses-round2-2026-10-21.json)

Statement: judge.v1 does not need a prompt change to pass the decline check. FLOOR shows the leak sits only in the correctness dimension: completeness and usefulness are exactly 1.0 for all three decline variants. Proposed fix: compute U from completeness + usefulness only (U_CU) and keep correctness for the CE label only. Under that rule (a) all three decline variants score U 0, (b) system gaps (4B-1.7B, Gemma-1.7B, 1.7B-1.5B) move by less than 0.03 with no rank flip, and (c) item test-retest SD is at most judge.v1's 0.0206 on the same 20 ids. The CE labels cannot flip, because the correctness bytes and the CE rule are untouched. This beats both v1.1 (7 CE flips) and the alternative 'v1 + decline subtraction', U' = (U - U_dec)/(1 - U_dec). That alternative carries the decline arm's own CI (0.037-0.081) into every row.

Method: 0-LLM. Freeze a criterion (sha) first. Inputs, all existing Haiku 5.5-low judge.v1 rows (both orders), with per-dimension scores read by floor_agg.py: FLOOR decline a/b/c (30 ids); the v1 retest-20 repeats 1-2; MAIN 97 K0 for 1.7B, Gemma and 4B (GEMMA-VS-4B); and the v0.1 57 for the 1.5B closed-book and the 1.7B K0 control. Compute U_full, U_CU and U' (subtraction) per arm, the paired gaps with a cluster bootstrap, item-level Spearman U_CU vs U_full, and retest item SD under U_CU. Skip the deterministic ids (ruler/ids/deterministic-*.ids) for the SD and gap sensitivity rows. Report the same table for the Opus rows that exist (CE-OPUS-RU 38 answers) as a family check.

Kill criterion: Do NOT adopt U_CU if any of these holds: a decline variant's U CI high > 0.05; retest item SD under U_CU > 0.0206; any pairwise system gap moves by >= 0.03 against U_full, or any rank flips; item Spearman < 0.85. If killed, R1 picks v1.1c if it passed its frozen rule. Otherwise R1 picks 'judge.v1 + decline subtraction', with U_dec and its CI printed in every row and the decline arm marked 'invalid as a floor, used as an offset'. U_CU is then never quoted.

## HON-8 REVEAL-RULE (verbatim from hypotheses-round2-2026-10-21.json)

Statement: A reason-code subset of hidden answers exists whose reveal is net-useful: correct:CE >= 1.0 and no health-tagged CE. Example: warned but cited, first content sentence cited, health excluded, all-citations-removed excluded. If so, show-anyway can be kept for that subset only, with health never revealable. The current all-hidden button returns 7 correct, 35 CE and 59 partial per 100 (SHOWANYWAY, kill met).

Method: 0-LLM, select-then-confirm. Freeze the criterion and the candidate list first: at most 6 reason-code subsets from WARNSPEC tiers and RU hide reasons, with health always excluded. Select on LP (LITEPACKS K0/K1/K3 x 277) the subset with the best correct:CE that keeps >= 15 % of revealable rows. Confirm on MINI (null-cal pool controls, untouched by selection) with the same frozen rule. Also report per-tier for the 4B traces if HON-7 runs. Same script family as HON-2.

Kill criterion: If no pre-listed subset reaches correct:CE >= 1.0 on LP with >= 15 % of revealable rows, or the selected subset's MINI correct:CE has CI-high < 1.0, or it contains any health CE, the note recommends show-anyway behind a second confirmation with 'unverified, often wrong' for non-health only, and removal for health (the HON-2 fallback). No subset rule ships.

## Operational rules fixed here (RV1)

Definitions (s, r per item = mean over both orders; n = (s - 1)/4; U = sum(s - 1)/sum(r - 1), the floor_agg.py ratio-of-sums):
- U_full: s = mean(correctness, completeness, usefulness) of the answer, r the same for the reference (judge.v1 as is).
- U_CU: s = mean(completeness, usefulness), r = mean(completeness, usefulness) of the reference (both sides drop correctness).
- U_Z (the "zero correctness only on an engine decline" variant): as U_full, but correctness := 1 for the answer when the trace carries the engine's own decline signal: answer.declined true OR the answer text matches labels.py ENGINE_DECLINE (engine refusal / notice strings). No model-text regex. The FLOOR decline traces carry declined=false and none of the engine strings, so U_Z = U_full on them by construction; this is reported, not patched. Sensitivity (no rule): U_Z' = same with labels.py is_decline (adds short model abstentions).
- U' (subtraction): (U_full - 0.058)/(1 - 0.058), FLOOR decline (a).
- CE under U_CU: CE stays defined on the correctness dimension exactly as today (correctness averaged over both orders <= 1.5; correct >= 4), read from the same judge.v1 rows. The correctness bytes are unchanged, so CE flips from U_full to U_CU are 0 by construction; the script asserts this. Diagnostic only: how often a CU-only proxy (mean(completeness, usefulness) <= 1.5) agrees with CE (shows whether U_CU still sees errors).

Checks and bars (the RV1 kill clause, operationalised):
1. Decline validity: FLOOR decline a/b/c, decline-30.ids, floor_agg bootstrap (B 2000, default_rng(11), item resample). PASS iff U CI high <= 0.05 for all three. Computed for U_full, U_CU, U_Z, U'.
2. Consistency 40 (v1_1/data/controls-40.tsv, v1 repeats 1-3 as in agg_v1_1.py): mean over items of |n_CU - n_full| (each the mean over the 3 repeats); CE-label flips (0 by construction). Bar (JUDGE-V1_1 bars, report): mean |dn| <= 0.05 and flips <= 2. Also U_full vs U_CU on the 40.
3. Test-retest (v1_1/data/retest-20.ids, v1 repeats 1-2): mean over items of the sample SD (ddof 1) of n_CU over the two repeats. PASS iff <= 0.0206. Sensitivity: the same without deterministic ids (ruler/ids/deterministic-pool.ids and deterministic-v01.ids).
4. Gaps and ranks. (i) Tier ladder v0.1 51 (rv2_ladder.py rungs and ids: L0 1.5B closed-book, L1 1.7B K0 2 seeds, L2 Gemma E2B desktop 2 seeds, L3 4B phone cut 7): every pairwise dU under U_CU vs U_full; adjacent-pair separability by the RV24 rule (dU >= 0.05 and CI low > 0). (ii) MAIN 97 K0 s42 (q42 lp-screens control, g42 gemma4-e2b/stage2, b42 gemma4-e2b-vs4b; byte-identical unjudged texts reuse the control rows): 4B-1.7B, Gemma-1.7B, 4B-Gemma. Item-cluster bootstrap, B 2000, default_rng(11), paired draws. PASS iff every |dU_CU - dU_full| < 0.03 and the rank order of the arms is identical in each block. Sensitivity (no rule): MAIN 97 minus deterministic-pool.ids.
5. Item Spearman: per arm, Spearman of item n_CU vs n_full; PASS iff min over the 7 arm series (4 ladder rungs on 51, 3 MAIN arms on 97) >= 0.85.
6. Opus family check (no rule): CE-OPUS-RU 38 answers, Opus judge.v1 rows: U_full vs U_CU, Spearman, CU-proxy vs CE.
Verdict: ADOPT U_CU iff 1 (for U_CU), 3, 4 and 5 all pass and 2 is within its bars; else NO-ADOPT and the kill clause's fallback applies verbatim (v1.1c failed its frozen rule (JUDGE-V1_1B.md), so R1 = judge.v1 + decline subtraction, U_dec and CI in every row). U_Z is reported with the same checks; it can be recommended only if it passes every check that U_CU must pass.

## Operational rules fixed here (HON-8)

Rows: exactly the WARNCAL/SHOWANYWAY rows (tools/warncal_showanyway.py row() unchanged, imported by exec of its data section): LP = LITEPACKS K0/K1/K3 x 277 (selection), MINI = null-cal pool controls K0/K1 x 277 (confirmation). Revealable = hidden (decline OR warned OR LLM answer with no kept source) AND generated tokens > 0. Labels: CE = corr <= 1.5, correct = corr >= 4 (Haiku). Health = WARNSPEC health_reasons non-empty (as SHOWANYWAY).
Opus labels: a row has an Opus label when id|sha256(text)[:16] is a WARN-OPUS unit key (warn-opus/in/set.json + out/), or it is an LP K3 row whose id is in CE-OPUS-RU (ce-opus-ru/out). Opus corr = mean correctness over both orders; same thresholds.

Pre-listed candidate subsets (6; all subsets of revealable rows; "nh" = health excluded):
- C1 warned-but-cited-nh: warned, bucket not W:all-citations-removed, final cited list non-empty, not health.
- C2 warned-first-cited-nh: C1 AND the first content sentence is cited (WARNSPEC coverage() 'first' true). (The hypothesis' example.)
- C3 first-aid: item is a first-aid item (id starts st-boar-firstaid-en, or v0.1 category first-aid / dng-*). Health is NOT excluded here because the brief names it; the safety clause applies to it in full.
- C4 no-source-no-warning-nh: bucket U:no-kept(banner) (hidden only by the RU no-kept clause, no warning line), not health.
- C5 warned-no-source-nh: bucket W:no-source, not health.
- C6 union C1 or C4 (nh).
Statistic: correct:CE = k/c with k correct, c CE among the subset's rows; CI = Wilson 95 % on p = k/(k + c), mapped to p/(1-p) (rows treated as independent; item-cluster bootstrap B 2000 seed 11 as sensitivity). Coverage = subset rows / all LP revealable rows.
Selection (LP, Haiku): eligible = point correct:CE >= 1.0 AND coverage >= 15 %; select the eligible subset with the highest point ratio (tie: larger coverage). If none eligible: kill clause.
Confirmation, all required for PASS ("net useful under both judges"):
(a) MINI, Haiku: correct:CE CI-high >= 1.0 (the hypothesis kill clause) AND point >= 1.0.
(b) Opus, where labels exist: on the selected subset's Opus-labelled rows (LP + MINI, units counted once per unique text) the point correct:CE >= 1.0. If fewer than 10 Opus-labelled units fall in the subset, (b) is UNMEASURED and the verdict can be at most "PASS-HAIKU-ONLY", which does not ship a rule.
(c) Safety: 0 health-tagged CE rows in the subset in LP and MINI under Haiku, and 0 under Opus labels.
Every candidate is reported on LP, MINI and Opus with these statistics and by set (MAIN / ST-cand / ST-SE), whatever is selected.
Outcome: PASS -> write the reveal rule the app maintainer note may carry (subset definition in engine terms + numbers, health never revealable except as C3 allows if C3 passes). Otherwise the kill-clause fallback verbatim.
