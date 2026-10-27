# MATHROUTE: does skipping retrieval for math/unit questions (the app maintainer's "A3 router") recover most of the calculator path's advantage? (frozen 2026-10-15, coordinator subagent)

Measurement arm: no adoption verdict, no engine change committed. Context: the engine answers some arithmetic exactly with a calculator shortcut (modelId "calculator": calculate(), arithmeticAnswer(), travelDistanceAnswer() in src/routing/answer.ts); the app maintainer proposes instead an "A3 router" that lets the model reason with no sources (nothing to mis-cite). Note found while building: the engine already has a related rule (classify.ts isRetrievalIrrelevant: taskType "calculate" -> plan.retrieve false); the traces record route.task per arm, so how often the natural classifier already does A3 is reported.

## Tags
Tags: probe
Ruleset: 29
<!-- measurement arm: deterministic scorer first, Haiku only if the rule below opens it, 0 Opus, no verdict beyond the reading rules. -->

## Question
On math/unit questions, compare (A) cut 7 as is (calculator fires where it matches), (B) A3 emulation: calculator bypassed + retrieval forced off (model reasons alone), (C) calculator bypassed + retrieval forced on (the failure mode the app maintainer saw). Used for: the app maintainer's decision calculator vs A3 router (PR-1 discussion), and where the model still fails (arithmetic itself vs invented context).

## Fixed inputs
- Items: `boar-eval/bench/slices/mathroute-v1/questions.jsonl` (sha256 e42932199663e9c7e8059c1c976c5df877f23f2f8e187267ce630fbbf4d5128a) + `gold.jsonl` (sha256 b696a3631a8099e8ed4c99f28cdb93687a6e2e798d18f3197e242e5436c89e17); builder `tools/build_slice.py`. 26 EN items: vit-sci-003 and vit-trv-004 (the 2 v0.1 public items with modelId "calculator" in boar-eval/runs/device-poco-x6pro/final-cut7-v01/rows.jsonl) + 24 agent-written dev items (Claude Opus 5.5, 2026-10-15; 8 unit/temperature, 8 arithmetic word problems, 8 traps), written before reading calculators.ts/arithmetic.ts. blind/ and rnd/veil/ never read.
- Arm A: tree `kiln-local/be-0cfd4a77-cut7` (0cfd4a77 + cut7 patch 0fba26b8, adapter 6298e5d3, ARM cut7), no env.
- Arms B, C: tree `kiln-local/be-0cfd4a77-cut7-mathroute` = copy of the cut 7 tree + `tools/mathroute-env.patch` (sha256 bbee9f4a7b55e0be…; env-gated, inert without env; ARM "cut7+mathroute"; never committed to the engine). B: MATHROUTE_NOCALC=1 (calculate/arithmetic/travel-distance shortcuts skipped) + MATHROUTE_RETRIEVE=off (plan.retrieve forced false after planAnswer). C: MATHROUTE_NOCALC=1 + MATHROUTE_RETRIEVE=on. Other shortcuts (first-aid card, CO, emergency numbers, small talk, FACTS) untouched in all arms.
- Common: llama-server spikes/llama-b11010-cpu, --threads 4, server backend, ship profile, mmbert detector :8094, seed 42, config from arms/stack/runs/v01-cut7-stack-off-s42.requests.jsonl (quickFirst true, alwaysComplete false, claim kit boar-crypto + boar-wikivoyage-en). Runner `tools/run_mr.sh` (= longsession run_ls.sh with the tree as parameter, busy.sh guard), requests `tools/mkreq_mr.py`, driver `tools/gen_mr.sh`.

## Measured quantities (deterministic, `tools/score_mr.py` sha256 ba626febb69192ab…)
(i) correct: any number in the answer within the item tolerance of a gold value, or a gold pattern (clock time, "h min") matches; n/26 per arm and per group (v01/unit/arith/trap). Also "headline" (same test on the first sentence only).
(ii) extra-context rate: sentences > 2 (number + formula/one-line explanation allowed); mean sentence count.
(iii) cited-source rate: answer.cited non-empty or a [n] marker in the text.
(iv) latency: timing.totalMs p50 (all items, and model-answered items only).
(v) per arm: calculator fired (reason code answer:calculator-* / temperature-conversion), route.task, retrieval.raw non-empty, declined.

## Power
expected_delta: unknown (no prior on these items; the calculator is exact where it fires, so A - C = calculator fire count x model error rate on those items)
n: 26 items, paired, one seed
seeds: 1 (4B path byte-deterministic on the MacBook CPU path, RULE 27)
mde: paired binary at n = 26: a difference of <= 3 items is not distinguishable from item noise (McNemar needs ~5 discordant one-way for p < 0.05); reported as counts, no significance claimed below that.
slice: n/a (own dev slice)
l1_futility: n/a (measurement arm)
split: by group (v01 / unit / arith / trap) and by "calculator fired in A" (yes/no), pre-declared; none other.

## Ceiling (RULE 29; 0 calls)
ceiling: n/a (measurement arm)
bar_ceiling: n/a
launch: measurement arm tagged probe
transfer: n/a (dev slice; product/maintainer reading only)

## Budget (RULE 29)
wall_cap: 1.5 h MacBook generation (78 generations; A's calculator rows are instant)
calls_cap: <= 150 Haiku (claude-haiku-5-5 --effort low via arms/deepthink/tools/shard_judge.sh), 0 Opus, 0 paid API
smoke: 3 items (vit-sci-003, mr-u01, mr-t06) x 3 arms: non-empty answers, no errors; A shows the calculator code on >= 1 item; B and C show mathroute:nocalc and mathroute:retrieve-off / -on in route.reasonCodes; C has retrieval.raw non-empty on >= 1 item and B on none; else STOP (FAIL-INFRA).
kill_if: smoke fails; projected wall > 2.25 h
checkpoint: after the smoke

## Reading rules
- gap = correct_A - correct_C; closure = (correct_B - correct_C) / gap. gap <= 1 -> "no calculator advantage to close on this slice" (report counts only). Else closure >= 0.75 -> "A3 recovers most of the calculator's advantage"; 0.25-0.75 -> "partial"; < 0.25 -> "A3 does not recover it". Also reported: correct_B vs correct_A directly (A3 replacing the calculator outright) and on the "calculator fired in A" split.
- Failure attribution per wrong model answer (B and C): "arithmetic" (the model sets up the right operation but the number is off), "invented context / wrong setup" (wrong formula, wrong premise, number from a source, refusal), read from the answer text by the coordinator subagent and listed per item (no judge).
- Haiku (only if |correct_B - correct_A| <= 2, i.e. the deterministic score cannot separate A3 from the calculator): pairwise B vs A and C vs A, both orders, judge.v1-low, on the items where both arms of the pair are correct, refs = the gold note; cap 150 calls; reported as win/tie/loss (winner consistent in both orders, else tie). Otherwise no judge calls.
- One generation per arm; no rerun except an infrastructure error before the first token.

## Stop rules and budget
Disk >= 8 GiB free before each adapter call, never two llama-servers (busy.sh, wait up to 60 min), detector :8094 never stopped, never restart Docker.

## Outputs and exposure
`arms/mathroute/MATHROUTE.md` (cites this sha), `aggregates/`, `tools/`, `runs/`. Exposure: dev slice only (24 agent-written + 2 public v0.1 items already dev); no blind or held-out set touched. QUEUE entry.
