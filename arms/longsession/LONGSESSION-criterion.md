# LONGSESSION: does answer quality drift across a 5-turn session, and how? (frozen 2026-10-14, coordinator subagent)

Measurement arm: no adoption verdict, no engine change. Why: the bounty judge's top criterion is "consistent answer quality across longer sessions"; the engine's `answer()` takes a conversation `history` and the desktop adapter passes `item.history.turns` as `AnswerContext.history = {summary: null, turns}`; nobody has measured drift across turns.

## Tags
Tags: probe
Ruleset: 29
<!-- measurement arm: Haiku only, 0 Opus, no verdict beyond the measured quantities and the reading rules below. -->

## Question
For the cut 7 claim configuration, compare each answer given INSIDE a 5-turn session (A: history = earlier turns' questions + the engine's own earlier answers) with the same question asked STANDALONE (B: no history). Used for: (1) a drift reading for the claim text / product, (2) the app's history policy (truncation / summary) if the data supports one.

## Fixed inputs
- Items: `boar-eval/bench/slices/longsession-v1/questions.jsonl` (sha256 f618808de77068f6e3dc5ac5c253dfdeb6c769338d989421107936212b1f97e3) + `sessions.jsonl`; 10 sessions x 5 turns = 50 items, English, **agent-written dev data** (Claude Opus 5.5, 2026-10-14; fresh, not copies of bench items; the private held-out dir and $HELDOUT_DIR/quarantine/ never read). Shapes: 4 coref sessions (ls01-ls04: follow-ups such as "the second one", "there", "it"), 3 abrupt topic switch at turn 3 (ls05-ls07), 3 same-topic deepening (ls08-ls10). 20 items are `followup: true` (need earlier turns to be understood; `referent` strings given), 30 are self-contained. Builder: `arms/longsession/tools/build_slice.py`.
- Tree: `runner-local/be-0cfd4a77-cut7` (0cfd4a77 + cut7 patch 04a2a999, adapter 6298e5d3, ARM cut7), llama-server `spikes/llama-b11010-cpu`, --threads 4, server backend, ship profile, mmbert detector :8094, seed 42, config copied from `arms/stack/runs/v01-cut7-stack-off-s42.requests.jsonl` (quickFirst true, alwaysComplete false, kit boar-crypto ae9fbd2c… + boar-wikivoyage-en ff8595e3…), config.arm "cut7". Runner `tools/run_ls.sh`, requests `tools/mkreq_ls.py`, driver `tools/gen_ls.sh`.
- Run A `ls-session-s42`: 5 waves, wave k = turn k of all 10 sessions with full history of turns 1..k-1. Deviation from the app, declared: ChatScreen keeps the last 6 messages verbatim (VERBATIM_MESSAGE_COUNT = 6) plus a background summary of older ones; turns 1-4 receive exactly what the app would send (<= 6 prior messages, no summary yet), turn 5 receives 8 messages (the app would send 6 + a summary). Run B `ls-standalone-s42`: each of the 50 questions alone.
- Turn 1 of A and B are identical requests: by RULE 27 (arms/seedgen/SEEDGEN.md, 4B path byte-deterministic on the MacBook CPU path) the answers must be byte-identical; that is the null check (if not identical, report it).
- Judge: `boar-eval/harness/judge.mjs` via `arms/deepthink/tools/shard_judge.sh` N = 4, haiku = claude-haiku-5-5 --effort low (judge.v1-low), both orders, seed 7; traces = run A; references = run B's answers written as `bench/slices/longsession-v1/refs/refs.jsonl` + `MANIFEST.json` (questions_sha256, jsonl_sha256). The judge sees the literal turn text plus the rubric; follow-up items carry a first rubric line giving the conversation context (so the judge can grade the follow-up answer; B cannot know the referent, so A is expected to win follow-ups if history works). Preflight 1 item (2 calls) before the full pass.

## Measured quantities
(i) Per-turn paired quality: per item s_A, s_B = mean of correctness/completeness/usefulness over both orders (agg_device.py estimator); per turn index t = 1..5: ratio_t = sum s_A / sum s_B (raw) and win/tie/loss of A vs B (winner consistent in both orders, else tie); also pooled turns 2-5 and the one pre-declared split below.
(ii) Prompt tokens per turn (`timing.promptTokens` of the A traces; p50/max per turn) and a projection of the turn at which 4,096 tokens (the phone's n_ctx) would be exceeded: linear fit of max and mean promptTokens on turn index (t = 1..5), extrapolated; reported as "turn ~N" (mean and worst session).
(iii) Latency per turn: `timing.totalMs` p50/max per turn, A and B.
(iv) Reason codes indicating history effects: counts per turn in A vs B of codes containing `history`, `fa-card-from-history`, route/task changes (A route.task != B route.task), `grounding:no-good-source` / decline flags (answer.declined), and kept-source differences (A retrieval kept titles != B).
(v) Coreference heuristic (script, no judge): for every `followup` item, does the A answer contain any `referent` string (case-insensitive)? Same for B. Coreference failure = A does not name the referent.

## Power
expected_delta: 0 (no prior: no multi-turn measurement exists; the chat-slice v0 baseline (reports/runner-2026-10-02/chat-slice-baseline.md) checked validity, not drift)
n: 50 items (10 per turn index), paired A vs B, one seed
seeds: 1 (the 4B path is byte-deterministic per RULE 27, arms/seedgen/SEEDGEN.md; a second seed adds nothing on this path)
mde: per-turn-index contrast (10 vs 10 items, session-cluster bootstrap) ~0.10-0.12 raw (per-item SD ~0.09 from the v0.2 one-seed 0.025 MDE at 110 ids; 2.8 x 0.094 x sqrt(2/10)); pooled turns 2-5 vs 1 ~0.09. The requested reading "no drift detected at MDE 0.05" is only claimed if the drift CI half-width is <= 0.05; otherwise "no drift detected (CI covers 0) at the realised CI width".
slice: n/a (own dev slice, 50 items; no random20 stage)
l1_futility: n/a (measurement arm, Haiku only, no Opus, no verdict)
split: followup (20 items: needs history) vs self-contained (30 items), paired ratio A/B in each; expected: A > B on followup (history used), A ~= B on self-contained (drift / contamination would show as A < B here). None other allowed post hoc.

## Ceiling (RULE 29; 0 calls, before the freeze)
ceiling: n/a (measurement arm)
bar_ceiling: n/a
launch: measurement arm tagged probe
transfer: n/a (dev slice; product reading only)

## Budget (RULE 29)
wall_cap: 3 h MacBook generation (100 generations ~ 10-20 s each + 6 server starts)
calls_cap: <= 120 Haiku (expected 2 preflight + 100 full), 0 Opus, 0 paid API
smoke: session ls01 both ways (5 + 5 items): non-empty answers, no errors, and A's promptTokens grow with the turn index on turns 2-5 relative to turn 1 (proof that history reached the prompt); else STOP (FAIL-INFRA)
kill_if: smoke fails; projected wall > 4.5 h
checkpoint: after the smoke
subset_step0: n/a

## Reading rules
- drift = ratio_5 - ratio_1 (raw), bootstrap over sessions (10 clusters, B 2000, seed 11). CI covers 0 -> "no drift detected" (+ "at MDE 0.05" only if half-width <= 0.05). CI below 0 -> "drift: quality falls by turn 5". Also reported: slope of ratio_t over t = 1..5 with the same bootstrap, and pooled turns 2-5 ratio.
- Because turn 1 A == B by construction, ratio_1 ~ 1.0 (judge noise only); drift therefore equals "turn-5 in-session vs standalone" minus judge noise at turn 1.
- Coreference: failures counted on A; quoted per item in the report.
- Overflow: projected turn reported for mean and worst session; "not reached by turn 5" if max promptTokens at turn 5 < 4,096.
- A history-policy recommendation is written only if the data supports it (e.g. A < B on self-contained items at late turns, or overflow within ~10 turns); else "none supported".
- One generation per run; no rerun except an infrastructure error before the first token.

## Stop rules and budget
Disk >= 8 GiB free before each adapter call (MacBook; 25 GiB policy is the mini's), never two llama-servers (busy.sh, wait up to 60 min), detector :8094 never stopped, never restart Docker.

## Outputs and exposure
`arms/longsession/LONGSESSION.md` (cites this sha), `aggregates/`, `tools/`, `runs/` (traces, requests, judgments). Exposure: dev slice only, agent-written; no blind or held-out set touched. QUEUE entry.
