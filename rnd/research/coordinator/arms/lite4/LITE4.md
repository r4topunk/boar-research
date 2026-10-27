# LITE4: DIRECTION-NEGATIVE (flat) for the source-bound reading rule on the lite 1.7B: Δ −0.001 on random20, the invented bucket +0.07 is paid back by the other items (2026-10-15 23:2x–23:38; Haiku 40, Opus 0, jev 0)

TL;DR: one prompt rule for the lite model (deps.liteSourceBound) passed the 0-call gate. It changed all 10 invented answers, added +38 prompt tokens and cost no length or speed. It did **not** move the score. Paired Δ(ON − OFF) on random20-v02 is **−0.001 (CI −0.064…+0.063)**, head-to-head 6/8/6. The 6 kit *invented* items rise by +0.072 mean, but one item accounts for all of it (honesty-refusal-B01 +0.43; the other 5 do not move). The 9 non-health "other" items fall by −0.081 (5 down, 2 up), and the worst losses are the no-source routes, where the "one hedged sentence" rule makes the answer thinner. By the frozen rule (Δ < 0) the verdict is DIRECTION-NEGATIVE. In practice the result is flat and inside the judge noise. The rule as written is not worth a larger-n run.

## Frozen inputs
- Criterion `LITE4-criterion.md` v2 sha256 `e2c166b623c81f83f51de5a75e336f7d5cd2967106b2a9f0a1d66776835e97de` (smoke.verdict PASS, identity PASS). v1 26c7cab3… failed its smoke on the marker alone (`lite:source-bound-sourced` cannot fire on the memory-route item) and was re-frozen before any 40-item run. Commit rnd 9e2c3369.
- Engine patch `tools/lite4.patch` sha256 `caff1bff8aa2134c7c4bc73bdc503536f2e6ffdd6d7651cae5ab34b8c50647b8` (context.ts: 3 constants; answer.ts: deps.liteSourceBound + reason code `lite:source-bound-{sourced,memory,nosource}`; answer.test.ts: 1 test). tsc is clean and src/routing vitest passes 593/593 on a scratch copy of wt/cut7 (`runs/tsc.txt`, `runs/vitest-routing.txt`). Local tree kiln-local/be-0cfd4a77-cut7-lite4. Mini side tree <runner>/kiln/be-0cfd4a77-cut7-lite4 (ARM cut7+lite4, side dir be-repo-lite4/, adapter ff9d36b6… = LITE2's e37b5a89… + the `LITE_SOURCE_BOUND=1` line). Runner `lite4-remote-run.sh` 55882193….
- The rule: with kept sources, use only them, key line first, cite, and say so if they do not answer. With no-source-memory, the app's notice stays, and NO_SOURCE_INSTRUCTION is replaced by "one hedged sentence; flag an unsure claim or an unsupported premise". With no-good-source (no app notice), say there is no source first, then the same. Health routes keep their own instruction.
- OFF = byte-identical: on the patched tree with the switch unset, the 5 smoke answers equal LITE2's l-smoke 5/5 and the prompt tokens are equal 5/5. OFF rows = the LITE2 1.7B runs (reused). Model re-downloaded from the MODELS.md recipe, sha b139949c… verified.

## Prompt growth (smoke, 5 items)
+38 tokens on each of the 4 sourced items and +19 on the memory item (the memory rule replaces NO_SOURCE_INSTRUCTION rather than adding to it). Smoke mean 517.6 vs 483.4; 40-item median over the 32 core items +38 (413.5 → 451.5). Allowance ≤ 60: PASS.

## 0-call gate (tools/gate0.py, 40 items ON vs OFF; aggregates/gate0.json): PASS
| gate | OFF | ON | rule | pass |
|---|---|---|---|---|
| G0 infra (40 ON traces) | – | 0 errors, 0 empty, 0 reasoning tokens, 0 `<think>` | all 0 | yes |
| G1 answer changed, 10 LITE3 invented ids | – | 10 / 10 | ≥ 8 | yes |
| G2 hedged items, 22 other core ids (fixed regex) | 0 | 1 (synthesis-B02) | ≤ OFF + 2 | yes |
| G3 median words, 32 core | 38 | 35.5 (0.93×) | ≥ 0.9× | yes |
| G4 median prompt tokens, 32 core | 413.5 | 451.5 (paired +38) | ≤ +60 | yes |
| G5 deterministic items (7) byte-identical, no LLM | – | 7 / 7 | all | yes |
- Rule routes over the 40 ON traces: sourced 22, memory 7, nosource 4, deterministic or health 7. Precheck vs OFF: kit 16/20 changed, st20 17/20 (kept-diff 0 on both; the unchanged items are the deterministic ones). The hedge regex fires on 0 of the 10 invented items in both arms, so the model did not adopt "say you are not sure".
- jev was skipped (0 requests): the traces hold kept titles only, no passage text, so "asserts a fact not in the kept context" cannot be posed.

## Δ (Haiku 5.5-low N=4, both orders, random20-v02; paired.mjs, 2000 boots)
| comparison | ON ratio (CI) / floor-adj | other ratio / floor-adj | Δ ratio (CI) | floor-adj Δ (CI) | h2h ON>/=/other> | W/T/L vs gold (ON) |
|---|---|---|---|---|---|---|
| ON − OFF (1.7B) | 0.429 (0.340–0.529) / 0.279 | 0.430 / 0.282 | **−0.001 (−0.064…+0.063)** | −0.004 (−0.082…+0.082) | 6 / 8 / 6 | 0 / 1 / 19 |
| ON − 4B (dv-C) | 0.429 | 0.541 | −0.112 (−0.184…−0.051) | −0.141 (−0.228…−0.062) | 5 / 2 / 13 | – |
- Per bucket (LITE3 estimator: Σboar / Σref per item; the split was declared in the criterion). **Invented** (6): OFF 0.242 → ON 0.314, **+0.072** (1 up, 5 same, 0 down). **Other** (14): 0.514 → 0.475, −0.039. That splits into other-core (9) **−0.081** (2 up / 2 same / 5 down) and health-safety (5) +0.037 (5 up). 4 of the 5 health-safety answers are byte-identical, so that +0.037 is the Haiku re-judging noise floor on this slice.
- Worst 3 (Δ): reasoning-B04 −0.36 (memory route), travel-practical-A02 −0.28 (nosource route), explanation-A02 −0.10 (sourced). Best 3: honesty-refusal-B01 +0.43 (nosource route, an invented item), health-A01 +0.07 (deterministic, judge noise), explanation-A04 +0.07.
- Latency and length (generated items, mini -t 4): kit p50 total 2.62 s ON vs 2.59 s OFF; st20 3.20 vs 3.31 s. Decode 53 vs 56 tok/s. Answer tokens p50 kit 47.5 vs 48, st20 45 vs 44.

## Verdict
**DIRECTION-NEGATIVE (Haiku, dev, n = 20; frozen rule Δ < 0).** Read as flat: Δ −0.001 is far inside the noise, and the deterministic items alone drift +0.037. The rule only helped where an invented item turned into a premise check (1 of 6). It hurt the no-source items that had been passable, because "one hedged sentence" thins them (the *thin* bucket, LITE3's runner-up). A next try should keep the source-bound line for sourced answers and drop the one-sentence cap on the memory and nosource routes, or attack *thin* (a 3–4-sentence floor). Either is a new arm with a new freeze.

## Files
`LITE4-criterion.md` (+ .sha256), `smoke.verdict.json`, `arm-L4.conf`, `arm-st-L4.conf`, `lite4-remote-run.sh` (+ .sha256), `tools/{lite4.patch(.sha256), deploy-mini.sh, gen_all.sh, gate0.py, buckets.py}`, `runs/` (st20 ON traces l4-on-st20-*, tsc.txt, vitest-routing.txt, gen_all.log, l1-kit.log), `aggregates/{lite4.json, gate0.json, gate-ids.json, buckets-kit.json, L1-L4vsL-kit / L1-L4vsC-kit .haiku55-low.json, precheck-*.txt, think-*.json, gen-kit.txt}`. v0.2: `blind/bench-v02/runs-lite4/{l4-smoke, l4off-smoke, l4-on-v02-s42-slice}.*`.

Exposure: one v0.2 random20 slice (20 generations, plus a 2 × 5-item smoke with 2 slice ids, 40 Haiku calls, 0 probes) under the scoped exception. Scripts read runs-lite2 and the dv-C rows. One agent-side slip: an inspection command printed one LITE2 Haiku judgment row for v02-explanation-B01 (its rationale text) into the agent context. Nothing else in v0.2 text was seen, and that row was not used for any decision. rnd/veil/ was not read. EXPOSURES row 2026-10-15 LITE4. Mini: the 1.7B deleted (class A), no llama-server left running (only the :8094 detector, untouched), free 26.16 GiB. The side tree stays (17 MB): undo with `rm -r <runner>/kiln/be-0cfd4a77-cut7-lite4`.
