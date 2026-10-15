# HEADPASS-X2: does feeding the dense chunk candidates into the same post-grounding append path (no displacement, outside onSubject/compression) lift the fact-present count past the power line and the quality past the MDE? (frozen 2026-10-14 03:0x, coordinator)

## Tags
Tags: none

## Question
HEADPASS-ST X1 (append the retrieved pack article's chunks 1–2 after grounding) put the fact chunk in the final context on 72/180 and measured +0.033 (+0.016…+0.050) Opus, +0.119 on the 37 items where the chunk became present, ≈ 0 elsewhere; the mechanism converts, reach limits (HEADPASS-ST.md). DENSECHUNK-ST2 reached the fact chunk in raw top-8 on 108/180 but the keep step dropped 47 of them (ST2-GATE.md). Arm **X2 = X1 + dense extra via the append path**: the ST2 two-stage dense candidates (lead top-50 → chunk cosine top-12 at ≥ 0.55, sidecar chunk vectors) supply up to D = 2 chunks that are appended AFTER grounding through the HEADPASS path (skip already-kept, no displacement, not subject to onSubject/compressContext, health-strict rule as X1), instead of entering the raw list as in ST2. Control **S** = single pack (cut 7; Haiku + Opus rows exist); reference **X1** (HEADPASS-ST ON traces + rows). Use: the pack line's retrieval recommendation and the last step of the stack on the 180.

## Fixed inputs
- Tree runner-local/be-0cfd4a77-cut7-headpass (X1) + the dense-candidate code of packdense2-only.cut7.patch (sha 40a259be…) rewired so the dense top-D feed the append path (new setting `packDense2: "append"`), default absent byte-identical (180/180, 60/60, 110/110). Sidecars: rebuilt on the mini with arms/densechunk-st/tools/sidecar_embed.mjs + run_sidecars.sh (bge-small q8, same rule `title\nsection: text`, int8; ≈ 1–3 h; shas logged), copied to the MacBook only if ≥ 8 GiB remain (else X2 replays/generation run on the mini's adapter copy).
- Items: the 180 public self-test items; no-harm: v0.1 public kit-only (must stay byte-identical: the kit packs get no sidecars in X2) and v0.1 + boar-simplewiki-en (lost-context 0; fires/added tokens reported); v0.2 kit-only identity counts (script-only; EXPOSURES row).
- Judge: Haiku 5.5-low N=4 both orders (360) then Opus N=4 both orders on all 180 ON rows (360) — declared now: the Opus pass runs if the Haiku Δ > 0 (no power-line cap this time; the step-0 power line gates the LAUNCH of generation instead).

## Power
expected_delta: +0.05 raw X2 − S on the 180 (source: HEADPASS-ST conversion +0.119 per newly-present item on 37 → +0.033 pooled; projected present 72 → ≈ 117 (ST2 reach 108 ∪ X1 72, NEXT-RETRIEVAL-ARMS union_st2) → ≈ +45 more newly-present items × 0.11–0.17 ≈ +0.025…+0.040 on top of X1, i.e. +0.05…+0.07 vs S)
n: 180
seeds: 1 (deterministic generation, SEEDGEN)
mde: ≈ 0.03 raw paired at n 180 (Opus)
slice: n/a
l1_futility: Haiku Δ ≤ 0 AND h2h ≤ S → stop (no Opus)
reopen: R46 (dense extra slots in raw: +0.017 not decided — here the dense chunks bypass the keep step that dropped 47/108 of them)
split: paired Δ by "fact chunk newly present under X2 (absent in S)" vs "present under X1 already" vs "only non-fact chunks appended" vs "unchanged" (declared; expected gain on the first, X1's +0.119 on the second, ≈ 0 on the rest)

## Stages and rules
0. Step 0 (0 judge calls; replays): **G1** fact chunk present in the final context ≥ **102/180** (= X1's 72 + 30; the power line for +0.05) AND ≥ X1 on every family; **G2** kit-only v0.1/v0.2 byte-identical (required); v0.1 + simplewiki lost-context 0, gold kept not lower; health-strict: 0 appended chunks failing onHealthTopic; **G3** retrieval + keep + dense p50 ≤ 2.0 × S (ST2 was ×1.44), simplewiki scan ≤ 300 ms, prompt tokens p50 ≤ S + 600. FAIL → FAIL at step 0 (D0 classes: which of the 137 remain unreached and why).
1. Generation X2 on the 180 (4B cut 7, MacBook or mini adapter copy); v0.1 + simplewiki OFF/ON (57 judged).
2. Haiku N=4 both orders vs S; precheck ≥ 20 % changed prompts; same_answer field; declared split.
3. Opus N=4 both orders on the 180 ON rows (360) if Haiku Δ > 0. Verdict: LEVER (CI low > 0, Δ ≥ +0.03), SMALL (CI low > 0), NO, not decided. A LEVER also needs v0.1 + simplewiki ON − OFF CI high ≥ −0.03. Product statement: X1 + X2 as the pack line's retrieval recommendation, with the engine-scope rule (same tree for reach and quality) and the format-v3 cost (+≈ 60 % pack size for the sidecars) stated.

## Stop rules and budget
0 paid API. Mini: sidecar rebuild ≤ 3 h, disk ≥ 25 GiB, one heavy job at a time (after TEACHER-PROBE), never restart Docker, :8094 up. MacBook: disk ≥ 8 GiB, one 4B job at a time. Judge: Haiku 360 + 228; Opus ≤ 360.

## Outputs and exposure
arms/headpass-st/{X2-GATE.md, HEADPASS-X2.md, tools/, runs/, aggregates/, headpass-x2.vs-cut7.patch + .sha256}; v0.2 identity counts under $HELDOUT_DIR/bench-v02/runs-packs/ (script-only; EXPOSURES row). QUEUE rows per stage; CLOSED/EXPOSURES rows with the verdict (RULE 28).
