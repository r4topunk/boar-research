# GROUND-ST: the keep step on the pack-matched set — does grounding/compression drop the fact passage the retriever already reached, and does keeping it move quality? (frozen 2026-10-13 13:2x, coordinator)

## Tags
Tags: none

## Question
On the 180 public self-test items (one pack installed, claim kit, k = 6) the 4B claim build reaches the fact chunk in raw top-6 on 67 items but keeps it on 43, and reaches the fact article on 107 but keeps it on 68 (ST2-GATE OFF column). The keep step (onSubject grounding + compressContext + the health filter) loses ≈ 36 % of the reached chunks. Arm **X = packGround** (PACKCOND P4 patch `arms/packcond/packground.vs-dt512.patch`, ported to wt/packs, default off = byte-identical): (a) a pack passage is judged on-topic on its full text, not only on the sentences compression kept; (b) the best-ranked pack passage that compression cut and whose full text is on topic is pinned back at the same budget; (c) when nothing is on topic, the pack's two best passages after compression are kept (never an empty context); gated off for health, history, lexicon-name and multipass questions as in P4. Declared second variant **X2 = packGround + keepTop1**: in addition, the first pack hit of the raw list (the pack's top-ranked passage) is never dropped by grounding when its full text shares ≥ 1 query term (same gates). Control **C = OFF** (the published build; OFF traces and judgments exist: arms/packs/selftest-runs/st-<pack>-cut7-s42.*). Use: the keep rule for the STACK criterion (router + ground [+ dense extra as a declared component]); on its own this arm is a component estimate.

## Fixed inputs
- Items: the 180 public self-test items (9 packs × 20; fact article + chunk per item from in_pack_facts, as d0_st2.py); kit no-harm: v0.1 public 60 (gold sources.json) and v0.2 110 (script-only on blind; counts/ids only).
- Tree: wt/packs (dt512 + T-K2 + packDense2 off + packRoute off) + the ported packGround patch with the keepTop1 flag (settings.packGround: true | "top1"; absent = byte-identical). vitest src/ + tsc must pass; OFF raw and kept lists identical to ST2's OFF replays (180/180, 60/60, 110/110).
- Replay: copy of arms/densechunk-st/tools/replay-st.ts (`--modes off,ground,top1,off`), gate search, k 6, single pack installed per self-test pack (kit = boar-crypto + boar-wikivoyage-en published files, packs = the published wave1/wave2 files, no sidecars).
- Generation (stage 1): 4B cut 7 on the MacBook via arms/packs/tools/run_selftest.sh with the patched tree (same pattern as run_selftest_dense2.sh: a tree copy kiln-local/be-0cfd4a77-cut7-ground = cut 7 + the packGround-only patch); judge Haiku 5.5-low N=4 both orders vs the existing OFF judgments; same_answer.py field (RULE 27).

## Power
expected_delta: +0.02 raw on the 180 (source: SELFTEST-SCORES — the with-pack lift tracks kept-from-pack share, packs with passages kept on 15–16/20 items gain +0.05…+0.10, those kept on 3–5/20 gain 0; ST2: +18 chunk kept / +32 article kept → Opus +0.017; this arm targets the 24 chunk / 39 article losses in the keep step, so +12…+20 chunk kept → +0.01…+0.03)
n: 180
seeds: 1 (generation is deterministic on this path, SEEDGEN; seeds add nothing)
mde: ≈ 0.03 raw paired at n 180 (Opus; Haiku compresses)
slice: n/a
l1_futility: n/a (no Haiku cap; both arms judged on all 180)
reopen: PACKCOND P4 FAIL at step 0 was on the v0.2 in-pack subset (n 32) where the loss was retrieval (F0 article not in the top-20 pool on 14/15); on the self-tests the fact is reached on 67/107 items and lost in the keep step — a different loss class on a set with power
split: paired Δ by OFF reach class of the item — "reached-not-kept" (fact chunk in OFF raw6 but not in OFF kept, 24 items; or article reached-not-kept, 39) vs the rest; expected: the gain sits in reached-not-kept, ≈ 0 elsewhere (declared; the only split)
NOTE: expected_delta < mde → this arm cannot be decided alone at n 180; its deciding measurement is the STACK criterion (adoption Δ ≥ +0.05 vs peers). Here: step 0 decides whether the keep rule enters the STACK; stage 1–2 give the component estimate (reported as such unless it clears LEVER).

## Stages and rules
0. Step 0 (0 judge calls, MacBook): D0 loss classes on OFF (grounding / compression / health filter / other, per the replay's reconstruction as P4 --diag) for the 24 chunk and 39 article losses; then replays off,ground,top1,off on the 180, v0.1 and v0.2.
   - **G1 keep (180):** fact chunk in kept ≥ 55 (OFF 43; ceiling 67 = raw6 reach) AND fact article in kept ≥ 85 (OFF 68; ceiling 107); fact chunk in raw6 unchanged (67; the lever must not touch retrieval).
   - **G2 no-harm (RULE 26):** v0.1 and v0.2 kit items: lost-context 0 (no item with a kept source under OFF ends with none); empty-kept over OFF-retrieving items not up (≤ 11 / ≤ 28); v0.1 gold kept ≥ 12, v0.2 resolvable gold kept ≥ 4; kept lists change on ≤ 15 % of kit items (P4 allowed 4/20) — a change that only ADDS a pack passage on a kit item counts as harmless but is reported; context tokens per item never above the cap (budget unchanged by construction).
   - **G3 cost:** p50 ≤ 1.2 × OFF.
   Variant entering stage 1 = the one with the higher fact-chunk-kept that passes G2 (declared here, chosen at 0 calls). Both FAIL → FAIL at step 0; the D0 loss classes become the next hypothesis.
1. Generation: 4B cut 7 + packGround-only patch, the 180 items, one pack installed (as SELFTEST-SCORES OFF); OFF traces reused.
2. Haiku 5.5-low N=4 both orders on ON; paired Δ raw/above_min over 180, by the declared split and by pack family (descriptive); same_answer.py field; precheck (arm.sh precheck pattern: ≥ 20 % of items must have a changed prompt — else do not judge).
3. Verdict: LEVER (CI low > 0 and Δ ≥ +0.03), SMALL (CI low > 0, Δ < 0.03), NO, "not decided at MDE 0.03"; near-miss (Haiku Δ > 0 with CI through 0) → Opus N=4 both orders on ON only (OFF Opus rows exist from ST2 L2: arms/packs/selftest-runs/st-<pack>-cut7-s42.judgments.opus.jsonl) = 360 Opus. Whatever the verdict, the keep rule that passed step 0 is carried into the STACK criterion as a component.

## Stop rules and budget
0 paid API. MacBook only (no mini). Disk ≥ 8 GiB. Never two 4B generation jobs at once (check pgrep for llama-server Qwen3-4B / adapter.ts before launching; the detector :8094 is not a 4B job). Judge: Haiku 360 (+ 360 Opus on a near-miss).

## Outputs and exposure
arms/groundst/{GATE.md, D0.md, GROUND-ST.md, tools/, aggregates/, runs/, packground2.vs-dt512.patch + .sha256}; v0.2 replay under blind/bench-v02/runs-packs/groundst-v02-kit.jsonl (script-only; EXPOSURES row); QUEUE rows per stage.
