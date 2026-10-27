# FOLLOWUP: does expanding a short/referring follow-up's retrieval query with the previous user turn's content words (+ ranking the previous answer's kept titles first) put the follow-up's target chunk in the kept context more often, and does it move the judged turn-2 answer? (frozen 2026-10-16 10:1x by the FOLLOWUP agent, before any run; measurement arm, direction-only)

Frozen before any replay, generation or judge call. Inputs fixed by sha below.

## Tags
Tags: none
Ruleset: 30

## Question
PHONEFAIL (2026-10-16): with history the 4B's turn-2 answers stayed on topic, but turn-2 sources equalled the no-history run on 4/4 pairs: answer() retrieves with the bare follow-up (searchQuery = req.query; matchQuery for compression/grounding = req.query). LONGSESSION measured history's value on answers (follow-up items ratio 1.716). The arm adds `deps.followupContext` (engine, off by default): when the conversation has an earlier user turn and the current turn has <= 8 words, a referring pronoun or an ellipsis opener, the previous user turn's content words (stopwords and words already in the turn removed, <= 12, in order) are appended to both the search query and the match query, reason code `followup:expanded`; when the previous assistant turn carries `sources` (titles; new optional ConversationTurn field), retrieved chunks with those titles are ranked first (stable), code `followup:title-boost-N`. Not applied to Portuguese turns or the today-in-history path. OFF (switch absent) = unchanged by construction; verified below. Use: direction for a post-10-20 engine patch (follow-up retrieval), and whether the app should pass the shown source titles in its history turns.

## Fixed inputs
- Pairs: `arms/followup/pairs.jsonl` sha256 5f687e26e899e7242623693350dad33c718bff0b84f69ba90eea8bb267e92aec, gold `gold.json` e81d771e84c776ac00f14063d7ab07813d329727c598b6c6f3a59652d16a7e78. 20 pairs from the 180 public self-tests, seed 999 draw (tools/draw.py; 2 per pack, +1 for boar-factbook and qa-ethereum-se), draw order kept, 1 skip logged (st-qa-travel-se-009: its only non-fact chunk is the question body; st-boar-factbook-019 not needed). Turn 1 = the self-test question; turn 2 = agent-written follow-up (<= 8 words) whose answer lives in a NEIGHBOUR chunk of the same article (not one of turn 1's fact chunks); gold = that chunk id; `t2_key_fact` = agent-written one-line key fact from the gold chunk (judge rubric). Written before any retrieval was run.
- Patch `tools/followup.patch` sha256 ad3a59b98cce194bd6618d4343830ef5f6d6ed4f06a55e7db093ec5b6010a497 vs wt/pr1 8ac9eb7a src (rag/pure.ts type field, routing/answer.ts, routing/followup.ts + followup.test.ts); tsc clean, src/routing vitest 709/709 + followup 4/4 on a scratch copy of wt/pr1. Eval switch `tools/followup-adapter.eval.patch` 71b6b933… (adapter FOLLOWUP=1 -> deps.followupContext; trace.ts answerContext passes assistant `sources`).
- Tree kiln-local/be-cut7-followup (ARM pr1+followup, COMMIT 8ac9eb7a, be/adapter.ts 2f425332…, be/trace.ts 515a894f…). Arm **ON** = FOLLOWUP=1; control **OFF** = same tree, FOLLOWUP unset.
- Replay: `tools/replay-fu.sh` (copy of packs/tk2-replay replay-tk2.ts; mode `fu` sets deps.followupContext; --gate search, --k 6, lexical detector, no LLM). Kit per pair = claim kit (boar-crypto + boar-wikivoyage-en) + the item's own pack (the 180 self-test protocol). Turn-2 history in the replay = [user: turn-1 question, assistant: fixed placeholder text + sources = the turn-1 OFF replay's kept titles] (retrieval reads only the user turn and the sources; the placeholder never reaches a model).
- Public sets only: the 180 self-tests (pairs above) and bench v0.1 questions.public (60). No blind/, no rnd/veil/; no EXPOSURES row needed (public).

## Power
expected_delta: unknown (no prior on follow-up expansion; PHONEFAIL 4/4 identical sources is the only input); the reach effect is the deciding quantity, the judged delta is direction-only
n: 20 turn-2 answers (judged), 20 + 20 + 60 replay items (gate)
seeds: 1
mde: ≈ 0.04 raw at n = 20 (Haiku, LITE3/LITE4); the judged stage cannot decide a small effect and gets no LEVER/SMALL/NO label
slice: pairs.jsonl (20 public pairs; not a random20 set)
l1_futility: n/a (measurement, direction-only; no Opus stage, no transfer)
reopen: n/a (new line; PHONEFAIL engine follow-up candidate)
split: target-gained = pairs where ON keeps the gold chunk and OFF does not (from the step-0 replay) vs the rest

## Ceiling (RULE 29; 0 calls, before the freeze)
ceiling: n/a (measurement arm; the reach gate below is the bound)
bar_ceiling: n/a (product-only: multi-turn is not in V-para / v0.2)
launch: measurement requested by the coordinator 2026-10-16 (MacBook lane)
transfer: product-only

## Budget (RULE 29)
wall_cap: 1.5 h (MacBook: replay ≈ 5 min; 60 generations ≈ 27 server starts ≈ 25 min; judge ≈ 5 min)
calls_cap: Haiku 40 / Opus 0 (0 paid, 0 jev)
smoke: fu-01 generated t1 + t2 OFF + t2 ON before the rest (infra only: rc 0, non-empty, 0 errors, `followup:expanded` present on t2 ON and absent on OFF) -> smoke.verdict.json for this sha
kill_if: any generation error/empty answer; the 0-call gate FAIL (-> stop, 0 generation, 0 Haiku); free disk below the runner floor (5325 MiB) -> stop generation, report the 0-call step
checkpoint: the 0-call gate, before any generation or judge call
subset_step0: n/a

## Precheck (S2 of the smoke ladder; 0 calls)
token_projection: 600 (turn-2 prompt tokens with history; LONGSESSION turn-2 A p50 428 / max 892) / token_budget: 1100
disk_peak_gib: 0.05 (traces + prompt dumps; tree 18 MB already on disk)
off_baseline: the OFF cell of this arm (same tree, FOLLOWUP unset) + wt/pr1 replay for OFF byte-identity
call_pattern: Haiku 5.5-low N=4 shards, both orders, ON turn-2 answers vs the OFF turn-2 answers as reference (slice followup-v1 refs = OFF), 40 calls, preflight probe disabled (PREFLIGHT_PROBE_IDS=0)
lane: mac-gen
opus_clause: none
wall_cap_h: 1.5
parallelism: 1
run_type: 4b-patch

## Stages and rules
1. **Step 0 (0 LLM; tools/gate0.py over replay outputs):**
   - G0 infra: every replay cell 0 errors, repeat identity (OFF,OFF and fu,fu passes) on all items.
   - G1 OFF byte-identity: the OFF cell on kiln-local/be-cut7-followup = the same replay on wt/pr1 (raw ids, kept ids, promptSha) on the 20 turn-2s and the 60 v0.1.
   - G2 turn-1 identity: ON vs OFF identical (raw ids, kept ids, promptSha, reason codes) on the 20 turn-1s and on the 60 v0.1 single-turn questions (claim kit), and `followup:expanded` fires on 0 of these 80.
   - **G3 reach: gold chunk in kept context on the 20 turn-2s, OFF count vs ON count; PASS if ON >= OFF + 6.**
   - Descriptive: gold article kept, gold chunk in raw top 6, losses (OFF kept, ON not), fire count, title-boost count.
   - Gate = G0 AND G1 AND G2 AND G3. FAIL -> stop, report, 0 generation, 0 Haiku.
2. Gate PASS and free disk >= 5325 MiB -> generation on the MacBook (one llama-server, busy.sh guard, detector :8094, 4B Qwen3-4B-Instruct-2507 Q4_K_M, b11010 server, threads 4, seed 42, maxTokens 512, succinct persona, quickFirst true / alwaysComplete false, per-pack kit): wave t1 (20, FOLLOWUP unset), then wave t2 OFF and t2 ON with history = [user: t1 question, assistant: the t1 answer text + sources = the t1 trace's kept titles] (LONGSESSION/PHONEFAIL multi-turn format). Smoke first (fu-01). Descriptive per arm: route/reason codes, gold article kept (title), gold-chunk sentence in the dumped prompt (any >= 40-char sentence of the gold chunk as a substring), prompt tokens, latency.
3. Haiku 5.5-low N=4 both orders: slice boar-eval/bench/slices/followup-v1 (questions = turn-2 text; rubric = [conversation context line with the turn-1 question, the t2_key_fact]; refs = the OFF turn-2 answers, MANIFEST shas), traces = ON turn-2, 40 calls. Score per item s_ON, s_OFF from the judge rows; ratio = Σ s_ON / Σ s_OFF, item bootstrap B 2000 seed 11; W/T/L; split above.
4. **Verdict (frozen, direction-only, as LITE4):** **DIRECTION-POSITIVE** if ratio ON/OFF > 1 (paired Δ > 0) AND the target-gained mean s_ON > mean s_OFF; **DIRECTION-NEGATIVE** if Δ < 0; **FLAT** otherwise. CI reported, not used. A DIRECTION-POSITIVE read licenses at most a larger multi-turn slice post-10-20, never adoption.
- One generation per arm. No rerun except an infrastructure error before the first token.

## Stop rules and budget
MacBook: runner disk floor 5325 MiB, one llama-server at a time (busy.sh), never stop the detector :8094, none of our servers left running. Haiku <= 40, Opus 0, 0 paid. No git push; commit arm files in rnd.

## Outputs and exposure
`arms/followup/FOLLOWUP.md` (cites this sha), `aggregates/`, `tools/` (patch + sha), `runs/` (replay lines, small traces). Public sets only: no EXPOSURES row; one QUEUE row (tools/qrow.sh, tag main) + a BACKLOG row.
<!-- END FROZEN -->
