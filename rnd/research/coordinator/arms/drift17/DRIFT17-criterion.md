# DRIFT17 criterion: do the 1.7B's confident errors rise in later session turns? (frozen 2026-10-21 before any generation; HON-5 DRIFT17)

Source: ruler/hypotheses-2026-10-21.json, id "HON-5 DRIFT17" (statement: with the 1.7B default, the CE-unwarned rate on later turns is at least 2x that on turn 1 on longsession-v1). Measurement + one pre-declared rule; no engine change.

## Tags
Tags: probe
Ruleset: 29
<!-- Haiku only, 0 Opus, 0 paid API; dev data only (no bench/v0.4, no blind/, no rnd/veil). -->

## Fixed inputs
- Items: boar-eval/bench/slices/longsession-v1/questions.jsonl (sha256 a73f1e644e5e163adf6c5c8887016706dc0606ba258d10595442356b4a466b08), ALL 80 items = 10 sessions x turns 1-5 (50) + the LONGSESSION addendum-1 extension turns 6-15 of ls02, ls06, ls08 (30). Agent-written dev data. 10 sessions (< 15, so no session cut).
- System = the lite tier as LITEPACKS froze it (arms/litepacks/LITEPACKS-criterion.md, K0): mini tree <runner>/kiln/be-0cfd4a77-cut7-litepacks (ARM cut7-headpass-x2+litepacks, answer.ts 0d1ac07dd1d664be, adapter be/adapter-litedecline.ts d53c14878ce4cbd3), LITEDECLINE_OFF=5 (compact declines released behind the warning line "Not found in this phone's offline library. From the model's memory, may be wrong:"), Qwen3-1.7B Q4_K_M, --reasoning off, llama-server b11010 CPU -t 4 on an OS-assigned port, detector :8094 used (never started/stopped), seed 42. Request config = byte copy of the config of arms/litepacks/runs/req/lp-K0-v01-s42.requests.jsonl row 1 (modelId qwen3-1.7b-q4km, settings quickFirst / packHeadPass a2 / packDense2 append-budget, kit K0 = boar-crypto ae9fbd2c + boar-wikivoyage-en ff8595e3), runId changed, config.arm unchanged.
- Run A d17-session-s42: 15 waves; wave k = turn k of every session that has it, item.history.turns = all turns 1..k-1 of that session (question + this run's own earlier answer), exactly the LONGSESSION tools' history construction (tools/mkreq_d17.py = longsession/tools/mkreq_ls.py with the config source swapped). Run B d17-standalone-s42: the 80 questions alone. Turn 1 A and B are identical requests (null check: report byte-identity, do not require it).
- Host: Mac mini, one gen slot (<runner>/kiln/slots gen1|gen2 lock as lp-screens mini_gen.sh), disk >= 25 GiB, never touch Docker/ollama/:8094.
- Smoke gate (in the driver, after wave 2): A and B rows non-empty with no errors on waves 1-2, and on turn-2 items that called the LLM A promptTokens > B promptTokens for at least half of them (history reached the prompt); else STOP FAIL-INFRA.

## Judge
boar-eval/harness/judge.mjs via arms/deepthink/tools/shard_judge.sh, N = 4, claude-haiku-5-5 --effort low (judge.v1-low), both orders, seed 7. Traces = run A. References = run B's answers (the 1.7B's own standalone answers) in arms/drift17/bench/ (questions.jsonl byte copy + refs/refs.jsonl + MANIFEST.json), so each call scores A and B on the same item against the item rubric (the LONGSESSION design). Preflight 1 item (2 calls) then 80 items (160 calls).
calls_cap: 200 Haiku / 0 Opus / 0 paid.

## Metrics (A = in session, B = standalone; per item, judge dims averaged over both orders)
- corr_A, corr_B = judge correctness (mean over orders); s = mean of correctness/completeness/usefulness.
- warned = answer text starts with the warning line above (or the 4B uncited preface "This answer is not from an offline source"); declined = trace answer.declined.
- CE-unwarned (item) = not declined AND not warned AND corr <= 1.5. CE-unwarned rate of a bucket = count / items in the bucket. Warned-CE (warned AND corr <= 1.5) reported beside it.
- U by bucket = sum s_A / sum s_B with s := 0 for declined answers (ratio vs the 1.7B's own standalone answer), plus mean s_A and mean corr_A.
- Refusal (decline) rate by bucket: answer.declined, plus answers whose text starts with "I don't have a reliable offline source" or "I don't know".
- Buckets: turn 1 (n 10), turns 2-3 (n 20), turns 4+ (n 50 = 20 base + 30 extension); primary bucket turns 4-5 (n 20, all 10 sessions).
- Topic-drift flag (LONGSESSION's definition: shape "switch" sessions ls05-ls07, post-switch turns >= 3; ls06 also has the arithmetic switch at turns 8-10): CE-unwarned and U on flagged vs unflagged items; plus counts of grounding:fa-card-from-history replays (the LONGSESSION history defect).
- Follow-up vs self-contained split (questions.jsonl followup flag), and the coreference heuristic of LONGSESSION (A names a referent string).
- Bootstrap: session-cluster (resample the 10 sessions, B 2000, seed 11), 2.5/97.5 percentiles.

## Decision rule (frozen)
r1 = CE-unwarned rate of A on turn 1 (n 10); r45 = CE-unwarned rate of A on turns 4-5 (n 20).
- DRIFT CONFIRMED iff (a) r45 >= 2 x r1, AND (b) at least 3 CE-unwarned items on turns 4-5, AND (c) the session-cluster bootstrap CI of r45 - r1 has its low end > 0.
- Otherwise KILLED: the claim keeps "no degradation detected over 5 turns" and extends it to the 1.7B with "at MDE ~0.2 on the CE rate" (a null is never written as "no drift"). If (a) and (b) hold but (c) fails, the report says "point estimate meets 2x, CI covers 0: not confirmed".
- Attribution check (reported, does not change the label): paired A - B CE-unwarned rate on the same turns 4-5 items and on follow-up turns 2-5 (session bootstrap). If CONFIRMED but the paired A - B CI covers 0, the rise is read as "later-turn items are harder for the 1.7B", not as session drift. Also reported: the hypothesis file's kill clause (A/B U ratio on turns 2-5, CI low >= 0.9; follow-up CE-unwarned A vs B).

## Comparison with the 4B (0 calls)
The 4B LONGSESSION runs on the same 80 items (arms/longsession/runs/ls-session-s42 + ls-ext15-session-s42 traces and judgments; Haiku, refs = the 4B's own standalone answers) give the same metrics per bucket. Cross-model numbers use different references (each model's own standalone answer) and are read as rubric-anchored correctness, not as a paired model delta.

## Budget and stops
wall_cap: 2 h mini generation (160 generations); kill_if: smoke fails, any wave errors, disk < 25 GiB. No rerun except an infrastructure error before the first token. Never two jobs in one slot; never Opus; never push.

## Outputs
arms/drift17/DRIFT17.md (TL;DR, verdict, tables per bucket, 4B comparison, worst examples), aggregates/drift17.json, tools/, runs/ (requests, traces, judgments), PLAN.md only if the run is queued; one QUEUE row via qrow.sh main; commit rnd own paths after each step.
