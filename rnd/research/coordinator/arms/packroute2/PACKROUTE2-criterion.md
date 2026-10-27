# PACKROUTE-2: can the shipped 4B, as a zero-shot classifier over the installed packs' descriptions, route a question to the one relevant pack well enough to recover the single-pack reach that peers lose? (frozen 2026-10-13 13:3x, coordinator)

## Tags
Tags: none

## Question
PACKROUTE step 0 (arms/packroute/STEP0.md): with all 9 packs + kit installed as peers (P, today's engine) the fact article is kept on 46/180 vs 68/180 with only the relevant pack installed (S = oracle route); the deterministic vote router scored 0.25 accuracy (FAIL). Arm **R4 = LLM router**: before `searchWikiPacks`, the shipped 4B (Qwen3-4B-Instruct-2507 Q4_K_M, the claim model; greedy, ≤ 16 output tokens, the pack list as a cacheable prefix) reads the installed packs' ids + one-line descriptions (from the cards' first "What it is" line, ≤ 25 words each) and answers one pack id or `none`; the engine then searches the kit packs + the chosen pack only (`none` → kit only). Declared second variant **R4Q**: as R4, but `none` → all packs as peers with the quota 2/6 (PACKROUTE Q). Control **P** = peers (all 9 installed, today's engine). Reference **S** = single pack (SELFTEST-SCORES OFF traces/judgments). Use: the routing rule of the STACK criterion and the product answer to "small packs + router vs one giant pack".

## Fixed inputs
- Items: the 180 public self-test items (own pack = label); kit items for the `none` label: the 9 v0.1 + 15 v0.2 items whose gold is in no wave pack (step0.json G1_none; v0.2 script-only: the classifier script reads the question text and writes id + choice only), plus the route distribution on all 60 + 110.
- Model/backend: the claim 4B via the adapter's server path (llama-server CPU build spikes/llama-b11010-cpu, `-np 1`, seed 42, greedy for this call: temperature 0) on the MacBook; prompt = the same string the engine would send (system + pack list + question), so the measured accuracy is the engine's.
- Engine: wt/packs PACKROUTE patch extended with `packRoute: "llm"` (route decision supplied by the adapter/replay from a routes file for step 0; in the product path by a `routePack(question)` 4B call before retrieval) and `"llmq"`; default off byte-identical. Replay = arms/packroute/tools/replay-pr.ts + `--routes <file>` (id → pack | none).
- Pack descriptions: fixed text committed as `tools/pack_descriptions.json` before the accuracy run (one line per installed pack; the kit packs are always searched and are not listed).

## Power
expected_delta: +0.04 raw R4 vs P on the 180 (source: PACKROUTE step 0 — oracle route S keeps the fact article on 68 vs P 46 (+22) and reaches the chunk on 67 vs 42; SELFTEST-SCORES: with-pack lift +0.032 tracks kept-from-pack share; at 85 % accuracy ≈ +17 article kept → +0.02…+0.05)
n: 180 (+ 24 kit `none` items; + 60/110 no-harm)
seeds: 1 (deterministic generation on this path, SEEDGEN)
mde: ≈ 0.03 raw paired at n 180
slice: n/a
l1_futility: n/a
reopen: n/a (PACKROUTE FAIL at step 0 was the deterministic vote router; this is the declared "learned router" follow-up named in its criterion)
split: paired Δ by pack family (SE vs topic) and router accuracy by family (declared; the only split)

## Stages and rules
0a. **Accuracy test (0 judge calls; ≈ 350 short 4B calls on the MacBook):** classifier choice on the 180 + the 24 kit `none` items + the remaining v0.1/v0.2 items (distribution only).
   - **G1 accuracy:** own pack on ≥ 153/180 (0.85) AND `none` on ≥ 21/24 kit items. Report the confusion matrix, per-family accuracy, ms per call (prefix-cached and cold) and the prompt sha.
   - FAIL → FAIL at step 0a; one declared retry only: a second prompt wording (descriptions with 3 example question stems per pack, fixed before the rerun) — report both; no further tuning.
0b. **Replays (0 calls) with the routes file:** R4 and R4Q on the 180 (all 9 + kit installed), v0.1 60, v0.2 110 (script-only).
   - **G2 reach:** R4 fact chunk raw6 ≥ 60 and fact article kept ≥ 61 (≥ 90 % of S) and ≥ P (42 / 46).
   - **G3 kit no-harm (RULE 26):** lost-context 0 vs kit-only on v0.1 and v0.2 (P has 1 + 3); empty-kept over OFF-retrieving items not up; v0.1 gold kept ≥ 12, v0.2 resolvable gold kept ≥ 4; p50 (retrieval, excluding the router call) ≤ 1.5 × P; router call latency reported separately (MacBook CPU ms; phone estimate ×3).
   Variant entering stage 1 = R4 if it passes G2/G3, else R4Q if it does; both FAIL → FAIL at step 0.
1. Generation (4B cut 7 on the MacBook, all 9 + kit installed): arms P and the chosen R variant on the 180 (route decisions = the 0a choices, cached in the routes file so generation does not re-run the classifier).
2. Haiku 5.5-low N=4 both orders on P and R; paired Δ R − P over 180 and by family; R − S (share of the single-pack upper bound recovered); same_answer.py field (RULE 27); precheck ≥ 20 % changed prompts.
3. Verdict: LEVER (CI low > 0, Δ ≥ +0.03), SMALL, NO, "not decided at MDE 0.03"; near-miss → Opus N=4 both orders on P and R (720). Whatever the verdict, the product statement to the app maintainer carries the step-0 numbers (crowding, oracle gap, router accuracy, latency).

## Stop rules and budget
0 paid API. MacBook only (no mini). Never two 4B jobs on the MacBook at once (check pgrep for llama-server Qwen3-4B / adapter.ts; the detector :8094 is not one); the GROUND-ST step 0 replays (no LLM) may run concurrently. Disk ≥ 8 GiB. Judge: Haiku 720 (+ 720 Opus on a near-miss).

## Outputs and exposure
arms/packroute2/{ACCURACY.md, STEP0.md, PACKROUTE2.md, tools/ (classifier script, pack_descriptions.json, routes files, replay wrapper), aggregates/, runs/, packroute2.vs-dt512.patch + .sha256}; v0.2 classifier choices and replay under blind/bench-v02/runs-packs/packroute2-* (script-only; EXPOSURES rows: the classifier script reads v0.2 question text and writes ids + choices only). QUEUE rows per stage.
