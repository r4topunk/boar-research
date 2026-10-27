# HEADPASS-ST: does appending the top pack article's neighbour chunks (and dense extra slots) without displacement and outside the keep step convert ORACLE-ST's headroom on the 180? (frozen 2026-10-14 00:3x, coordinator; a parallel session; drafted by the design agent in proposals/NEXT-RETRIEVAL-ARMS-2026-10-13.md §4)

## Tags
Tags: none

## Question
On the 180 public self-test items (one pack installed, claim kit, cut 7) the fact chunk is in the prompt on 35 (cut-7 replay) / 43 (ST2 OFF); ORACLE-ADD shows +0.095 when it is. Diagnosis (h8st/tools/diag/diag137.json): 56/137 misses have the fact article in the pack's BM25 top-80 but the wrong chunk wins; SE fact chunks sit at article position 1 on 59/90, <= 2 on 83/90. Arm X1 = settings.packHeadPass "a2": after grounding, append the chunks at positions 1-2 (by start) of the article of the first raw passage from a non-kit format-2 pack, skipping chunks already kept (ORACLE-ADD append path; no displacement; not subject to onSubject/compressContext; health-strict items: appended chunks must pass onHealthTopic; never multipass; never for boar-crypto / boar-wikivoyage-en). X2 = "a2+dense": X1 plus ST2's dense extra-2 (packdense2-only.cut7.patch two-stage path, non-kit sidecars only), appended the same way (<= 4 appended). Control C = S (cut 7, settings absent). Use: rank-1 retrieval-conversion lever; product setting default off.

## Fixed inputs
- Tree kiln-local/be-0cfd4a77-cut7-headpass = cut 7 + headpass.vs-cut7.patch (sha <..>) [+ packdense2-only.cut7.patch sha <..> for X2]; settings absent = byte-identical (raw, kept, prompt sha) on 180/180, v0.1 60/60, v0.2 110/110.
- Control rows: arms/packs/selftest-runs/st-<pack>-cut7-s42.{traces,judgments,judgments.opus}.jsonl (S; Haiku + Opus exist).
- Replays: copy of arms/h8st/tools/replay-h8.ts with --modes off,x1,x2,off; v0.1 public kit-only and v0.1 + boar-simplewiki-en installed; v0.2 kit-only script-only (identity counts only; EXPOSURES row).
- Generation: 4B cut 7 on the MacBook (run_oracle.sh pattern), deterministic (SEEDGEN), prompt dump on.

## Power
expected_delta: +0.03 raw (X1) / +0.05 raw (X2) (source: per-item conversion 0.11-0.17 per newly-present fact chunk from ORACLE-ST ADD (+0.095 x 180/152) and DENSECHUNK-ST2 (+0.017 x 180/18); projected fact-present X1 35 -> 75 (cut 7), X2 43 -> 117 (ST2 tree), h8st/tools/diag/{arthead_cut7,union_st2}.py)
n: 180
seeds: 1 (deterministic generation, SEEDGEN)
mde: ~0.03 raw paired at n 180 (Opus); X1 alone sits at the MDE and cannot be decided unless its step-0 present-gain is >= +40; X2 clears it
slice: n/a (no Haiku cap; all 180 judged)
l1_futility: n/a (any Haiku delta > 0 -> Opus N=4 both orders on all 180 ON rows)
reopen: R46 (dense extra parked at +0.017: here the appended chunks bypass the keep step that dropped 47/108 reached), R47 (keep relaxations: here nothing is relaxed; neighbours are appended), SECTIONHIT (LEDGER-FIXES row 70, provisional: v0.2 misses were article-level; on the 180 the article is found on 56/137)
split: paired delta by "fact chunk newly present under ON (absent in S)" vs "ON appended only non-fact chunks" vs "unchanged prompt"; expected: gain on the first (~0.11-0.17 per item), ~0 or slightly negative on the second (distractor cost), 0 on the third

## Stages and rules
0. Step 0 (0 judge calls, MacBook replays).
   - G1 reach/present (180): fact chunk in raw ∪ appended >= 90 AND fact chunk present in the final context (kept ∪ appended) >= OFF + 15. Power line: present >= OFF + 40, else the arm runs as a component estimate only (Haiku, no Opus, verdict capped at "not decidable at MDE 0.03").
   - G2 no-harm: kit-only v0.1/v0.2 byte-identical to OFF (required); v0.1 + simplewiki: lost-context 0 (append-only by construction), fire share and added tokens reported; health-strict items: 0 appended chunks failing onHealthTopic.
   - G3 cost: retrieval + keep p50 <= 1.1 x OFF (X1), <= 1.5 x OFF (X2); prompt tokens p50 <= OFF + 450 (ORACLE-ADD: +168).
   - Variant entering stage 1: X1 if it passes G1 incl. the power line and G2/G3; else X2; both fail -> FAIL at step 0 (D0 classes recorded).
1. Generation: chosen variant on the 180; v0.1 + simplewiki OFF and ON (57 judged each).
2. Haiku 5.5-low N=4 both orders vs S Haiku rows; precheck >= 20 % changed prompts (else do not judge); same_answer.py field (RULE 27).
3. Verdict on Opus (N=4 both orders, 360 ON calls; S Opus rows exist): LEVER = CI low > 0 and delta >= +0.03; SMALL = CI low > 0 and delta < 0.03; NO otherwise; |delta| < MDE with CI through 0 = "not decided at MDE 0.03". Any adoption statement also needs v0.1 + simplewiki Haiku ON - OFF CI high >= -0.03.
- One generation per stage; no rerun except an infrastructure error before the first token.

## Stop rules and budget
0 paid API. MacBook: generation + replays, disk >= 8 GiB, never two 4B jobs at once. Mini: X2 only, sidecar rebuild <= 3 h (int8 caches if present, else bge-small re-embed), disk >= 25 GiB, never restart Docker. Judge caps: Haiku 360 + 228; Opus <= 360. Stop if step 0 fails or the precheck fails.

## Outputs and exposure
arms/headpass-st/{HEADPASS-ST.md (cites this sha), GATE.md, tools/, runs/, aggregates/, headpass.vs-cut7.patch + .sha256}; v0.2 identity counts under blind/bench-v02/runs-packs/ (script-only) + one EXPOSURES row; QUEUE rows per stage.

## Freeze note
X2 (dense) runs only if X1 fails the power line AND the int8 caches or a bge-small re-embed are available on the MacBook (never the mini while SFT4B runs); otherwise X1 alone. Step 0 may be run by an agent; stages 1–3 need the coordinator's QUEUE row after step 0.
