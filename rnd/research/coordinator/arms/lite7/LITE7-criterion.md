# LITE7: does a lite-only "3-4 short sentences; include each specific figure, name or step" style swap move the 1.7B + X2b on random20 (seed 616) by attacking LITE6's thin bucket? (frozen 2026-10-16 by the LITE7 agent; measurement arm, direction-only; Haiku, dev)

Frozen before the 180 generation and before any judge call. The only runs before the freeze are the 5-item patch smoke (runs/smoke/, ON + OFF, 0 calls), used for the prompt-growth check and this Precheck block.

## Tags
Tags: none
Ruleset: 30

## Question
LITE6: after X2b the 1.7B's largest residual loss vs the 4B + X2b is *thin* (7.96 of 14.97 points, 53 %, 71 items, 49 with the fact in context); it lands at ≤ 2 sentences on 83 % of answers (4B: 44 %), words p50 34.5 vs 52. The arm swaps the succinct persona's two style lines for the lite model only (deps.liteStyle, eval env LITE_STYLE=1): system "Answer in 2-3 short, direct sentences or a brief paragraph, no preamble." -> "Answer in 3-4 short, direct sentences, no preamble."; style reminder "Keep it short: 2-3 sentences." -> "Use 3-4 short sentences; include each specific figure, name or step the passages give for what was asked." No word count (COMPLETE lesson). Health routes keep the house lines; deterministic routes are untouched; the X2b append budget is still measured on the house lines (kept lists identical to OFF). Use: direction for the lite-tier prompt; a positive read licenses at most the 180 Haiku run (360 calls), never adoption.

## Fixed inputs
- ON: tree kiln-local/be-0cfd4a77-cut7-lite7 = the X2b tree (kiln-local/be-0cfd4a77-cut7-headpass-x2; PATCH_SHA256 0fba26b8…, HEADPASS_X2B_PATCH_SHA256 = sha of headpass-st/headpass-x2b.vs-cut7.patch) + tools/lite7.patch sha256 6ef9c0dbcde9591d1b1c079f238fc06a47582a55698da7a865a0568b9c800653 (src/routing/answer.ts: deps.liteStyle + 4 constants + reason code `lite:style`; be/adapter-lite7.ts = adapter-lite5.ts + the LITE_STYLE line, sha 9da2d01a5535b42996c6c2a7359b8342068f5777159fbda2f6c823c140c2a271); ARM cut7+lite7. tsc clean and src/routing vitest 603/603 on a scratch copy of wt/cut7 + this src (runs/tsc.txt, runs/vitest-routing.txt).
- Model Qwen3-1.7B Q4_K_M (shared-models/lite, sha b139949c…), b11010 llama-server `--reasoning off`, -t 4, seed 42, MacBook M1 Pro, mmbert detector :8094; runner tools/run_lite7_gen.sh <req> <out> on.
- Requests: tools/mkreq_lite7.py = lite5/runs/180/lite5-180-on-<pack>-s42 rows with only config.arm -> cut7+lite7 and runId -> lite7-180-on-<pack>-s42 (asserted).
- OFF / control = LITE5-180's ON arm (1.7B + X2b): traces lite5/runs/180/lite5-180-on-<pack>-s42.traces.jsonl and Haiku 5.5-low rows lite5-180-on-<pack>-s42.judgments.haiku55-low.jsonl (reused, not regenerated, not re-judged). OFF identity (smoke, lite7 tree with LITE_STYLE unset): 5/5 answer text, promptTokens and kept equal to those traces; ON vs OFF prompt dumps differ only in the two style lines (4 diff lines per item).
- Reference context (descriptive): 4B + X2b Haiku rows headpass-st/gen-x2b/st-<pack>-cut7-headpassx2b-s42.judgments.jsonl. Bench boar-eval/bench/selftest/<pack>, same reference answers as LITE5-180.

## Power
expected_delta: +0.020…+0.032 raw on random20 (source: LITE6: thin = 1.60 of the random20 slice's points, recover 25–40 %, minus a share of the big_error mechanism; +0.011…+0.018 on the 180)
n: 20 (random20 seed 616 = lite6/aggregates/lite6.json random20_seed616; in-sample of the LITE6 map)
seeds: 1
mde: ≈ 0.04 raw at n = 20 (LITE3/LITE4; Haiku): expected_delta < mde, so the arm cannot decide; it runs as a direction-only measurement (as LITE4) and gets no LEVER/SMALL/NO label
slice: random20 seed 616 of the 180 public self-tests (ids: st-boar-factbook-007, -018, st-boar-firstaid-en-015, st-boar-medlineplus-en-006, -011, -013, st-boar-simplewiki-en-014, st-qa-bitcoin-se-006, -008, st-qa-ethereum-se-015, st-qa-health-se-014, -016, -018, st-qa-outdoors-se-015, -019, st-qa-travel-se-004, -005, -009, -010, -017)
l1_futility: n/a (measurement, direction-only; no Opus stage, Opus 0)
reopen: n/a (new family: lite-tier style; LITE4 was a source-bound rule, not length)
split (declared): LITE6 bucket of the item. **thin** (12: factbook-007, firstaid-en-015, medlineplus-en-013, simplewiki-en-014, ethereum-se-015, health-se-014, health-se-016, outdoors-se-015, outdoors-se-019, travel-se-009, travel-se-010, travel-se-017) vs **rest** (8: factbook-018, medlineplus-en-006, -011, health-se-018 [deterministic, byte-identical by design], bitcoin-se-006, -008 [small_more_complete], travel-se-004 [big_error], travel-se-005 [not_read]). Per bucket: mean of per-item ratio (LITE3 estimator, Σ boar / Σ ref over 3 dims × both orders) ON vs OFF. Descriptive only: changed-answer subset (16 LLM items).

## Ceiling (RULE 29; 0 calls, before the freeze)
ceiling: thin loss on random20 1.60 points / 20 = 0.080 if every thin item reached the 4B + X2b ratio (upper bound; the 4B is the reference for "complete")
bar_ceiling: n/a (pack self-tests, lite tier; not a bounty-bar lever)
launch: coordinator brief 2026-10-16 (LITE7; MacBook generation lane mac-gen)
transfer: product-only (lite-tier prompt)

## Budget (RULE 29)
wall_cap: 1.5 h (180 generations ≈ 6 s + 9 server loads ≈ 25 min; judge 40 calls ≈ 5 min)
calls_cap: Haiku 40 / Opus 0
smoke: the 5-item patch smoke (runs/smoke: medlineplus-en 001–004 + health-se 001; ON + OFF): 0 errors, 0 empty, 0 reasoning tokens; prompt growth +10 tokens on each of the 4 LLM items; `lite:style` on 4/4 LLM items, absent on the deterministic item (byte-identical). smoke.verdict.json = smoke-project.py on the 4 LLM ON traces (runs/smoke/smoke-on-llm.traces.jsonl), --n-full 180 --marker lite:style
kill_if: any error/empty answer, reasoning tokens > 0 or `<think>`, projected wall > 2.25 h, the 0-call gate below fails (then 0 Haiku)
checkpoint: after the first pack (qa-travel-se): KILL if `lite:style` is missing on any LLM item of that run or the run's words p50 ≤ its OFF words p50 (the option did not change length)
subset_step0: n/a

## Precheck (S2 of the smoke ladder; 0 calls)
token_projection: 829.5 (mean timing.promptTokens of the 4 LLM ON smoke traces) / token_budget: 834.5 (OFF mean 819.5 on the same 4 items + 15)
disk_peak_gib: 0.02 (traces + logs; no new model; MacBook free 6.9 GiB, floor 4)
off_baseline: lite5-180-on-<pack>-s42 (LITE5-180 ON traces, MacBook); smoke identity 5/5 (answer text, promptTokens, kept)
call_pattern: Haiku 5.5-low N=4 shards, both orders, ON vs gold on the 20 random20 ids only (per pack via deepthink/tools/shard_judge.sh, preflight probe disabled PREFLIGHT_PROBE_IDS=0): 40 calls; OFF rows reused; 0 Opus; 0 paid
lane: mac-gen
opus_clause: none
wall_cap_h: 1.5
parallelism: 1
run_type: 4b-patch

## Stages and rules
1. Generate the 180 ON on the MacBook, one llama-server at a time (busy.sh + no other adapter-lite job), per pack in the X2b chain order (travel, ethereum, bitcoin, health-se, outdoors, firstaid, medlineplus, factbook, simplewiki). Per-run gate: 20 rows, 0 errors, 0 empty, 0 reasoning tokens, no `<think>`. FAIL -> stop. Checkpoint after pack 1 (Budget).
2. **0-call gate on the 180 (tools/gate7.py; ON vs OFF = LITE5-180 ON traces; sentence count = lite3 nsent, words = whitespace split, as LITE6):**
   - G0 infra: 0 errors / empty / reasoning tokens / `<think>` on the 180.
   - G1 share of answers with > 2 sentences (over the 180, as LITE6's 0.167) ≥ 0.45.
   - G2 words p50 (over the 180, as LITE6's 34.5) within 42–60.
   - G3 ends-open answers (last char not in .!?)"'* , lite3 rule) ≤ OFF + 2, and 0 length-cap hits (outputTokens ≥ 200, the lowest fast cap).
   - G4 hedge/refusal answers (LITE4 gate0.py HEDGE regex, app no-source notice removed) over the 152 LLM items ≤ OFF + 2.
   - G5 the 28 deterministic items (OFF outputTokens 0: health extractive/cards, facts) byte-identical answer text; `lite:style` on all 152 LLM items and on none of the 28. (No health route generates in this set: 0 LLM items carry grounding:health-* codes in OFF.)
   - G6 prompt tokens p50 over the 152 LLM items ≤ OFF p50 + 15, max paired growth ≤ +15.
   - G7 retrieval identity: kept (title, section) and headpass:* codes equal to OFF on ≥ 178/180.
   FAIL of any -> stop, report, 0 Haiku.
3. Haiku 5.5-low N=4 both orders on the 20 random20 ids (ON traces; fail-closed check_judgments.py; 40 calls). OFF = LITE5-180 ON judgments on the same ids (both orders present, asserted).
4. Estimator: packs-l2/tools/l2_agg.py (load/setstats/paired: ratio-of-sums, per-item bootstrap B 2000, seed 11, paired on queryId) for Δ(ON − OFF) raw + CI and b/w; per-bucket means of the per-item ratio (thin / rest; changed subset descriptive); hedging count, words p50, > 2 sentence share and p50 total/ttft latency ON vs OFF on the 20 and on the 180; descriptive ON − 4B X2b on the 20.
5. **Verdict (frozen, direction-only; no LEVER/SMALL/NO label):** **DIRECTION-POSITIVE** if paired Δ ratio (ON − OFF) on random20 > 0 AND the thin-bucket mean ratio ON > OFF; **DIRECTION-NEGATIVE** if Δ < 0; **FLAT** otherwise (Δ = 0, or Δ > 0 with the thin mean not up). The CI is reported, not used for the label. A DIRECTION-POSITIVE read with Δ ≥ +0.03 and CI low > 0 licenses the 180 Haiku run (360 calls, new freeze); none licenses adoption.
- One generation per pack. No rerun, except after an infrastructure error before the first token.

## Stop rules and budget
MacBook disk ≥ 4 GiB, one llama-server at a time (busy.sh), never stop the :8094 detector or anything else; none left running at the end. Haiku ≤ 40, Opus 0, 0 paid. No git push; `git -C rnd commit` of the arm files allowed.

## Outputs and exposure
`arms/lite7/LITE7.md` (≤ 50 lines, cites this sha), `aggregates/{lite7.json, gate7.json}`, `tools/*`, traces + judgments under `runs/`. Self-tests are public (bench/selftest); blind/ and rnd/veil/ are not read, so no EXPOSURES row. QUEUE row (tools/qrow.sh, tag main), BACKLOG LITE-TIER row.
