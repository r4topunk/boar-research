# HEADPASS-X3: does a cross-encoder reranker choosing the appended chunks (over BM25 ∪ dense ∪ top-article candidates) reach the fact chunk where the positional (X1) and cosine (X2) rules do not? (frozen 2026-10-14 12:3x, coordinator; proposed by r4to via the side session 12:2x)

## Tags
Tags: none

## Question
HEADPASS X1 (append chunks 1–2 of the top retrieved pack article after grounding, no displacement) measured +0.033 Opus on the 180 with fact present 35 → 72; X2 (frozen 1b70f6f3…) adds the ST2 dense top-2 through the same path (projected present ≈ 117). Both choose the appended chunks by a fixed rule (position; cosine). The loss class on the 180 is ordering, not coverage: 56/137 misses have the fact article in the pack's BM25 top-80 with the wrong chunk winning, and the fact chunk sits at raw position 1–3 behind another pack passage (NEXT-RETRIEVAL-ARMS; GROUND-ST D0). Arm **X3 = the same append path, D = 2 chunks chosen by bge-reranker-v2-m3 (shared-models/bge-reranker-v2-m3-q4km.gguf, sha e186a244…; llama-server --rerank) over the candidate union: the pack's BM25 top-80 chunks ∪ the ST2 dense top-12 ∪ the top article's chunks, scored against the engine's search query**; skip already kept/appended; health-strict rule as X1; cap 4 appended with X1's two (declared variant X3a = reranker only, no X1 chunks; X3b = X1 + reranker top-2). Second mode (crowding), same replay: all 9 packs + kit installed, the fused top-20 reranked pack-agnostically before the keep step (M2) — recovery of the 22 crowded items. Control for quality: S (single pack; Haiku + Opus rows exist); references X1 and X2 (their traces/rows). Use: the last retrieval lever of the pack line before TK2-FIX; device cost decides default vs optional.

## Fixed inputs
- Tree kiln-local/be-0cfd4a77-cut7-headpass-x2 + the reranker call (new setting `packRerank: "x3a" | "x3b" | "m2"`, default absent byte-identical); reranker served by llama-server --rerank -ub 2048 on the MacBook CPU (arms/deeprerank/tools/rerank-replay.ts shows the call), candidates built from X2's step-0 replay outputs (reuse: same items, same tree, same sidecars).
- Items: the 180 public self-test items (one pack installed); crowding mode: the 180 with all 9 + kit; no-harm: v0.1 kit-only (byte-identical required: the kit packs are not reranked unless M2 fires — report), v0.1 + simplewiki (lost-context 0), v0.2 kit-only identity counts (script-only; EXPOSURES row).
- Judge: Haiku N=4 both orders (360) then Opus N=4 both orders on all 180 ON rows (360), declared now; Opus runs if the Haiku Δ vs S > 0.

## Power
expected_delta: +0.02 raw over X2 (+0.07 over S) on the 180 (source: HEADPASS conversion 0.11–0.17 per newly-present fact chunk; the reranker's reach gain over X2 is the 56 wrong-chunk items minus those X2 already covers ≈ +15…+25 present; bge-reranker AUC 0.912 vs cosine 0.773 (Sonar scan 10-02; Anthropic contextual-retrieval note: most of its gain comes with rerank))
n: 180
seeds: 1 (deterministic generation)
mde: ≈ 0.03 raw paired at n 180 (Opus) — the X3 − X2 increment is below it; the decidable comparison is X3 − S (expected +0.07) and the declared split
slice: n/a
l1_futility: Haiku Δ vs S ≤ 0 AND h2h ≤ S → stop
reopen: R30 DEEPRERANK (+2/39 at step 0) and R14 RETHURT ran on the claim kit only (v0.1/v0.2, coverage-bound: gold in the top-20 pool on 12/39 items, 10 already in the top-6); no reranker was tested with the packs or on the 180, whose loss class is ordering (56/137 wrong chunk wins)
split: paired Δ by "fact chunk newly present under X3 (absent under X2)" vs "present under X2" vs "non-fact appended only" vs "unchanged" (declared; the first bucket carries the expected gain)

## Stages and rules
0. Step 0 (0 judge calls; MacBook replays, after X2 step 0 so its candidate sets and tree are reused): **G1** fact chunk present in the final context ≥ **X2's present + 15** on the 180 (power line ≥ X2 + 25 for an Opus-decidable X3 − X2) and ≥ X2 on every family; **M2** crowding: fact article kept ≥ 46 + 11 (= 57; half of the 22 crowded items recovered) with all 9 installed, lost kit contexts 0; **G2** kit-only v0.1/v0.2 byte-identical unless M2 fires (then lost-context 0, gold kept not lower); v0.1 + simplewiki lost-context 0; health-strict 0 failures; **G3** cost: reranker p50 per item (pairs scored, ms) reported as a device cost (≈ 570 MB RAM; ≈ 3.7 s per 20 pairs on a contended M1 CPU) — not a gate for the research verdict, but a LEVER is "optional setting" unless rerank p50 ≤ 1.0 s per item on the MacBook; prompt tokens p50 ≤ S + 600. FAIL → FAIL at step 0.
1. Generation of the variant that passes with the highest present (X3b expected) on the 180 (one pack installed); v0.1 + simplewiki OFF/ON (57 judged); M2 generation only if M2 passes (180, all 9 installed, vs P = CROWDQ's peers rows).
2. Haiku N=4 both orders vs S (and vs P for M2); precheck ≥ 20 % changed prompts; same_answer field; declared split; X3 − X2 descriptive on the same items.
3. Opus N=4 both orders on the ON rows (360; + 360 for M2 if run). Verdict vs S: LEVER (CI low > 0, Δ ≥ +0.03), SMALL, NO, not decided; v0.1 + simplewiki ON − OFF CI high ≥ −0.03 required; default-vs-optional per G3.

## Stop rules and budget
0 paid API. MacBook: replays + reranker server + generation, one 4B job at a time, the reranker server stopped between phases, disk ≥ 8 GiB; no mini. Judge: Haiku 360 (+ 228 + 360 M2); Opus ≤ 720 declared.

## Outputs and exposure
arms/headpass-st/{X3-GATE.md, HEADPASS-X3.md, tools/, runs/, aggregates/, headpass-x3.vs-cut7.patch + .sha256}; v0.2 identity counts under blind/bench-v02/runs-packs/ (script-only; EXPOSURES row); QUEUE rows per stage; CLOSED/EXPOSURES rows with the verdict (RULE 28).
