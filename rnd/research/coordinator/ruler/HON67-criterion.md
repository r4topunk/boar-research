# HON-7 WARN-TRANSFER + HON-6 TIER-PER100 criterion (frozen 2026-10-21 before any count; 0 LLM, 0 judge, 0 generation, 0 paid)
Source of the hypotheses: ruler/hypotheses-round2-2026-10-21.json (ids "HON-7 WARN-TRANSFER", "HON-6 TIER-PER100"). This file is the addendum to criterion d641551b (WARNCAL-SHOWANYWAY-criterion.md) that HON-7's method asks for.

## Shared definitions (reused unchanged)
- Code: tools/warncal_showanyway.py (sha256 8e162ceae8fd...) is NOT edited. The new script tools/hon67.py checks that sha, then execs its definition blocks unchanged (row(), bucket(), labels via null-cal/tools/labels.py, cal(), cal_full(), bstats(), rev(), wilson(), cboot(), judg_lp(), WARNSPEC health rules) and only feeds them other traces/judgments.
- Labels (labels.py): decline; warned = text starts with the CMP30OFF line; CE = not decline and corr <= 1.5; correct = not decline and corr >= 4; partial = not decline and 1.5 < corr < 4. corr = mean Haiku 5.5-low judge.v1-low correctness over the 2 orders.
- Refuse-by-default (RU definition, arms/refuse-unsupported, as in the HON-2 code): hidden = decline OR warned OR (outputTokens > 0 AND retrieval.kept empty).
- CIs: item-cluster bootstrap, B 2000, seed 11, 2.5/97.5 pct (cboot unchanged); paired tier differences resample item ids and recompute both tiers on the same resample.

## Data (desktop primary = MAIN 97 K0 s42, mini frame of GEMMA-VS-4B)
- 4B: arms/gemma4-e2b/vs4b (gemma4-e2b-vs4b-K0-main-s42; aggregate items judgment 'judged' or 'control' = byte-identical reuse of the control row; text asserted equal to the trace).
- Gemma E2B: arms/gemma4-e2b/stage2 (gemma4-e2b-eng-K0-main-s42; same rule).
- 1.7B PRIMARY: lp-screens/control lpctl-K0-main-s42 (the VS4B control; same host, engine frame and judge as the 4B and Gemma rows; 97/97 judged).
- 1.7B REPLICATION: litepacks LP K0 MacBook s42 MAIN 97 (judg_lp('K0')), reported next to the primary, never mixed into the decision.
- Rows with no complete judgment are dropped and counted.
- Pixel replication (57 v0.1 ids of the phone judge, Haiku-low, same labels): 4B final-cut7-v01 and Gemma gemma73-a (boar-eval/runs/device-pixel8a/*/judgments.haiku.jsonl). Both are cut 7 behaviour: no text warning line, no declines. Proxy flag (frozen here): flagged = warned OR (outputTokens > 0 AND (retrieval.kept empty OR answer.weakSources)) = the cut 7 weak-sources banner or no kept source; phone hidden = decline OR flagged. The 1.7B phone row is cmp30off-q17 (26 judged ids, real warning line), with the 4B and Gemma restricted to the same ids for the paired view. q17b73-a is not judged: no 57-id phone 1.7B row (named, not estimated; 0 judge here).
- Deterministic ids: desktop = MAIN 97 ids in ruler/ids/deterministic-pool.ids; phone = ruler/ids/deterministic-v01.ids. Every table is reported on all ids, deterministic only and divergent (= the rest); the decision uses ALL ids, the divergent split is reported next to it.

## HON-7 WARN-TRANSFER (statement, method and kill verbatim from the hypothesis file)
Statement: "The warning line and refuse-by-default results measured on the 1.7B (WARNCAL precision 0.39, recall 0.67, P(correct|warned) 0.05) hold for the 4B and for Gemma E2B on the same MAIN 97 K0 traces: precision >= 0.30, recall >= 0.55, P(correct|warned) <= 0.10. If so, the refuse-by-default + show-anyway note applies to the app maintainer's actual default, not only to the 1.7B entry."
Kill: "If the 4B's warning precision has CI-high < 0.30, or recall < 0.50, or P(correct|warned) > 0.15, the note says refuse-by-default is validated for the 1.7B only. For the 4B default it recommends 'show with the warning line' (current behaviour), not hiding. The claim's honesty section then names the model every number comes from."
Per model (4B, Gemma, 1.7B primary; 1.7B LP as replication), population = non-decline answers:
- HOLDS iff precision >= 0.30 AND recall >= 0.55 AND P(correct|warned) <= 0.10 (points).
- KILL iff precision cluster CI-high < 0.30 OR recall (point) < 0.50 OR P(correct|warned) (point) > 0.15.
- Otherwise INDETERMINATE. The note's scope follows HOLDS only: KILL and INDETERMINATE both mean "refuse-by-default is validated for the 1.7B only" for that model; the report says which of the two it was.
Reported per model: precision, recall, P(corr|w), P(corr|u), ratio, warned n, reveal correct:CE (rev(), hidden = RU set) and health reveals (count, CE ids), with cluster CIs. Secondary signal row: refuse signal = warned OR (outputTokens > 0 AND kept empty) (as WARNCAL). Pixel: same table with the proxy flag (replication of direction only, n 57 / 26; no decision).

## HON-6 TIER-PER100 (statement and kill verbatim)
Statement: "Under refuse-by-default, the 1.7B shows at least 3 fewer confident errors per 100 questions than the 4B (CE-shown/100), and its correct-shown/100 is no more than 5 below the 4B's. Under show-all, the 4B dominates on both. If so, the app maintainer note can say: 1.7B + refuse-by-default = the honest fast default; 4B = the more-complete default with more visible errors."
Kill: "Frozen rule. If, under refuse-by-default, the 4B's CE-shown/100 is within 3 of the 1.7B's (paired CI includes 0) and the 4B's correct-shown/100 is at least 5 higher, the 4B dominates. The note then recommends keeping the 4B default (refuse-by-default on) and frames the 1.7B entry only as the low-RAM/fast option. No 'more honest' wording for the 1.7B anywhere."
Per tier x mode, per 100 questions (denominator = all ids of the set, declines included):
- show-all: shown = every non-decline answer; hidden = declines (no answer text).
- refuse-by-default: shown = rows not in the RU hidden set; hidden = the RU hidden set.
- correct-shown (shown and corr >= 4), CE-shown (shown and corr <= 1.5), partial-shown (shown, rest), hidden; U = sum s(shown) / sum sref(all); floor-adjusted U = sum (s - 1)(shown) / sum (sref - 1)(all) (hidden rows count as the floor, contribution 0).
- p50 complete time per tier from ruler/SPEED-PRECHECK-2026-10-21.json primary Pixel runs (S1 answered and S3 all rows), copied, not recomputed.
- Paired differences (4B - 1.7B, 4B - Gemma, Gemma - 1.7B) with item-cluster bootstrap CIs.
Decision (on the desktop primary, ALL 97 ids; dCE = CE-shown/100 4B - 1.7B, dK = correct-shown/100 4B - 1.7B, refuse mode unless stated):
- STATEMENT SUPPORTED iff dCE >= +3 with paired CI-low > 0, AND dK <= +5 (point), AND under show-all the 4B has correct-shown >= the 1.7B's and CE-shown <= the 1.7B's + 3 (point; "dominates on both").
- KILL = "4B DOMINATES" iff dCE < +3 (point) with its paired CI including 0 or lying wholly below 0 (4B shows no more, or fewer, confident errors), AND dK >= +5 (point).
- Otherwise MIXED: no default-tier honesty line in the note; the table is quoted as a trade-off, and no "more honest" wording for the 1.7B.
- Gemma vs the 1.7B and Gemma vs the 4B: same rule applied pairwise, reported, not deciding.
- Pixel 57 (4B vs Gemma, proxy hidden) and the 26-id 1.7B subset: replication tables, no decision.

## Caveats fixed in advance
Post-hoc on existing judgments (shape partly known from VS4B: refused R 46/41/47); one seed per tier; Haiku-low judge (compresses gaps, over-calls CE vs Opus); dev ids only; desktop proxy of the engine (lite compact tier for every model, not the 4B's own product tier); phone runs are cut 7 behaviour, so the phone hidden set is a proxy, not the line.
Outputs: ruler/HON7-WARN-TRANSFER-2026-10-21.{md,json}, ruler/HON6-TIER-PER100-2026-10-21.{md,json}, script ruler/tools/hon67.py.
