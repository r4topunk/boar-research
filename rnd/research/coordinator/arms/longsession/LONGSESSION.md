# LONGSESSION: answer quality across a 5-turn session (cut 7, MacBook, 2026-10-14)

TL;DR: **There is no drop in quality across turns.** Answers given inside a session score the same as or higher than the same question asked standalone, at every turn index (Haiku L1, dev data, 1 seed). Pooled turns 2-5: ratio A/B **1.397 (1.187-1.673)**, W/T/L 19/17/4. On the 30 self-contained items the ratio is 1.128 (1.017-1.285), so history does not contaminate these answers in aggregate. History adds about 81 prompt tokens per turn. The largest turn-5 prompt is 821 tokens, so 4,096 is far away: a linear projection puts it at about turn 64 (mean) and about turn 40 (worst case), and the app already caps verbatim history at 6 messages. Three history-specific defects were seen (3/50 items), listed in §5.

Criterion: `LONGSESSION-criterion.md` sha256 `20faabff614c5ccd045d9d96ca37ab6ff845f3f98af800dbf388878e2b4046c1` (frozen before any run; Tags: probe, a measurement arm with no verdict).
Items: `boar-eval/bench/slices/longsession-v1/` (questions sha256 f618808d…, 10 sessions × 5 turns, **agent-written dev data**; blind/ and veil/ never read). References = run B answers (`refs/refs.jsonl` sha256 702017bc…).
Runs: A = `runs/ls-session-s42` (5 waves, full history = questions + the engine's own earlier answers), B = `runs/ls-standalone-s42`. Tree kiln-local/be-0cfd4a77-cut7 (adapter 6298e5d3), llama-b11010-cpu, -t 4, seed 42, kit boar-crypto + boar-wikivoyage-en.
Wall: smoke 134 s (ls01 both ways) + full 747 s (100 generations, 6 server starts). Judge: **102 Haiku calls** (claude-haiku-5-5, judge.v1-low; 2 preflight + 100 full, N = 4 shards, both orders, seed 7, 0 failures), 0 Opus, 0 paid API.
Smoke: 10/10 non-empty, 0 errors. A's prompt tokens rose with the turn (403/639/468/–/571; B 403/537/278/–/245), which proves the history reached the prompt. Null check: on turn 1, A and B gave byte-identical answers in **10/10** items (RULE 27 holds).

## 1. Per turn index (A = in-session, B = standalone; ratio = Σ s_A / Σ s_B, item bootstrap B 2000 seed 11)
| turn | n | ratio A/B (95 % CI) | W/T/L (A vs B) | A promptTokens p50 / max | B p50 / max | A totalMs p50 | B totalMs p50 |
|---|---|---|---|---|---|---|---|
| 1 | 10 | 1.000 (1.000-1.000) | 0/10/0 | 527 / 638 | 527 / 638 | 9.1 s | 9.3 s |
| 2 | 10 | 1.965 (1.301-2.851) | 7/2/1 | 428 / 892 | 346 / 783 | 7.4 s | 6.1 s |
| 3 | 10 | 0.970 (0.726-1.278) | 2/5/3 | 534 / 877 | 440 / 718 | 8.6 s | 7.1 s |
| 4 | 10 | 1.328 (1.031-1.949) | 3/7/0 | 806 / 928 | 486 / 694 | 5.1 s | 2.5 s |
| 5 | 10 | 1.537 (1.208-2.155) | 7/3/0 | 660 / 821 | 366 / 511 | 10.6 s | 6.0 s |
| 2-5 | 40 | 1.397 (1.187-1.673) | 19/17/4 | | | | |

The token columns count only items that called the LLM. Instant, card and extractive items have no promptTokens: 2/2/3/5/2 per turn in A.
Pre-declared split: follow-up items (20) **1.716 (1.292-2.288)**, W/T/L 12/5/3. Self-contained items (30) **1.128 (1.017-1.285)**, 7/22/1; on turns 2-5 alone 1.205 (1.010-1.467). By shape: coref 1.216 (0.993-1.512), switch 1.373 (1.117-1.848), deepen 1.281 (1.005-1.677).
Turn 3 is the topic-switch turn in ls05-ls07, and its ratio is 0.97 (a tie in practice, CI 0.73-1.28). The switch does not hurt the answer.

## 2. Drift reading (session-cluster bootstrap, 10 sessions, B 2000, seed 11)
- drift = ratio_5 − ratio_1 = **+0.537 (+0.208…+1.155)**. On self-contained items only it is +0.282 (+0.063…+0.708). The slope over turns is +0.044 per turn (−0.104…+0.245).
- Reading under the frozen rule: the CI does not cover 0 and lies **above** it, so quality does not fall by turn 5. Turn-5 in-session answers beat their standalone twins. "No drift at MDE 0.05" cannot be claimed: the CI half-width is about 0.47 at n = 10 per turn. The honest statement is **no degradation detected over 5 turns**, with the direction favouring the session.
- Caveat: ratio_1 ≡ 1 by construction, because A and B are byte-identical on turn 1. The reference is the engine's own standalone answer, not a frontier answer. These are ratios against the same model, not bar numbers.

## 3. Context budget (4,096 n_ctx on the phone)
- History overhead (A − B promptTokens on the same item): +92 / +168 / +303 / +323 tokens on turns 2-5. That is about **81 tokens per turn**, because the 4B answers are short.
- Projection: a linear fit of A's mean promptTokens gives 451 + 57·t, which crosses 4,096 at **turn ~64**. A fit of A's max gives turn ~84. Worst case (the largest standalone prompt, 783, plus the steepest session's history slope, 86 tokens per turn) reaches 4,096 at **turn ~40**. The output tokens also need room in n_ctx, so subtract about 2-4 turns. Not reached by turn 5: the maximum is 928 tokens, on turn 4.
- The app keeps only the last 6 messages verbatim (VERBATIM_MESSAGE_COUNT = 6) plus a background summary. Verbatim history is therefore bounded at about 3 turns, roughly 250-350 tokens here, and overflow from verbatim turns cannot happen. This run sent 8 messages on turn 5, one turn more than the app would.

## 4. Coreference heuristic (script: does the answer contain a `referent` string?), 20 follow-up items
- A fails **6/20**; B fails 17/20 (B has no history, so it is expected to fail).
- A's failures, by cause:
  - ls04-t2, -t3 and -t5: **error propagation**. Turn 1 answered "Brazil, Colombia, Venezuela" (wrong). The session then followed Colombia ("second one" → Colombia), so the coreference resolved correctly but onto a wrong fact.
  - ls01-t4: the Wikivoyage instant path (`instant:final`, no LLM) gave the same junk answer with or without history.
  - ls02-t4 and ls03-t4: correct answers that never name the referent ("validator offline", "outer thigh"). These are heuristic false positives.
- Real coreference failures attributable to history handling: **0**. One failure comes from the history-blind instant path, and three come from a propagated turn-1 error.

## 5. Reason codes, history effects and the 3 worst items
- Route task changed A vs B: 0/50. Declines: 0 in both runs. `grounding:no-good-source`: equal counts in A and B on every turn. Kept-sources differ in 2/50 items. Errors: 0.
- `grounding:fa-card-from-history` fired 3 times (ls03-t2, ls03-t5, ls10-t5):
  - ls03-t2 is right: "Is that different for a small child?" got the bee-sting card (A 3.67 vs B 1.00).
  - ls03-t5 and ls10-t5 are **replays of an earlier card for a different question**. "How long should we wait at the hospital after using it [the epinephrine pen]?" got the bee-sting card. "How much water per hour when hiking?" got the heatstroke card. They still beat B (2.33 vs 1.50; 2.17 vs 1.50) because B declined or answered weakly, but both are off-question.
- History raised the emergency detector score: on ls10-t3 the detector moved from p = 0.000 to 0.196, which switched on `grounding:health-strict` / `health-extractive` and produced an extractive Wikivoyage snippet instead of a generated answer.
- Worst 3 (s_A − s_B):
  1. **ls10-t3** (−1.83) "What is the difference between heat exhaustion and heat stroke?" A: "From the offline source: Stay safe > Deserts: The southwest and much of the interior west can become exceedingly hot during the day, leading to heat exhaustion…" B: "Heat exhaustion is a less severe condition where the body overheats but still functions partially, often with symptoms like heavy sweating, weakness, and nausea…" (cause: history-raised detector → health-strict extractive path)
  2. **ls04-t2** (−1.17) "What is the capital of the second one?" A: "…The second-largest country in South America by area is Colombia, and it…" B: "…I don't know which "second one" you're referring to. Please clarify the…" (cause: turn-1 factual error propagated)
  3. **ls04-t3** (−0.83) "How far is it from there to Santiago de Chile?" A: "There is no direct distance from Colombia to Santiago, Chile, as they are separated by thousands of kilometers across South America…" B: "I don't know the distance from where you're referring to Santiago de Chile, as your location isn't specified…" (same propagated error)
- Latency: in-session answers are slower on later turns. The p50 gap is +1.3 s on turn 2 and +4.6 s on turn 5, from the longer prefill (CPU desktop; the phone gap will be larger).

## 6. Recommendation for the app
**Truncation/summary policy: none supported.** Quality does not degrade over 5 turns, and prompts stay under 1k tokens. The existing 6-message verbatim window plus summary already bounds the context, far below n_ctx. Two narrow history defects are seen, but on 3/50 items, too few for a fix in PR-1 under the closing-sprint rule ("a history fix only if a drop is measured"):
- (a) `fa-card-from-history` replays an earlier first-aid card for a new, different health question (2 items).
- (b) DETMAX's history window can push a non-emergency comparison onto the health-strict extractive path (1 item).
Candidate later fixes: let the card replay fire only when the current turn has no health topic of its own, and score the detector on the current turn when history raises p below the threshold. A larger multi-turn health slice should confirm both before any fix.

## Files
`tools/` (build_slice.py, mkreq_ls.py, run_ls.sh, gen_ls.sh, make_refs.py, agg_ls.py, peek.py), `runs/` (requests, traces, prompts, judgments, preflight), `aggregates/longsession.json`. Exposure: dev slice only, no blind or held-out set touched.

## Addendum 1: 15-turn extension (2026-10-14)

TL;DR: **No drop in quality up to turn 15.** In turns 6-15, in-session answers score 1.136 (0.993-1.320) of their standalone twins; on self-contained items the ratio is 1.017 (0.950-1.095), which is parity. The full-history prompt grows by about 74 tokens per turn and peaks at 1,658 tokens (turn 14). A linear fit crosses 4,096 at **turn ~50**. The cost of long sessions is latency: on the desktop CPU, the in-session p50 goes from 11 s at turn 1 to **22 s at turns 14-15**, against about 8 s standalone. The app's 6-message window would carry about 3× less history than the adapter did.

Criterion addendum: `LONGSESSION-criterion-addendum1.md`, sha256 `cec210c295052dc22472b7b0eed21e43cd61df5bd6df0b9782f76c70f853456d`, frozen before the extension runs.
Items: ls02 (coref, crypto), ls06 (switch: Kyoto, then arithmetic at t8-t10, back to Japan at t11), ls08 (deepen, Iceland), turns 6-15. That is 30 new agent-written dev items, 13 of them follow-ups. They are appended to the slice: questions sha256 a73f1e64…, the first 50 lines are byte-identical, and refs were rebuilt over 80 items (sha256 8f1ca9ac…).
Runs: A = `runs/ls-ext15-session-s42` (10 waves; history = turns 1-5 from `ls-session-s42` plus earlier extension waves, all previous turns), B = `runs/ls-ext15-standalone-s42`. Same tree, seed, server and kit. Wall 932 s, which includes about 4 min waiting for another agent's llama-server (busy.sh guard).
Judge: **62 Haiku calls** (2 preflight on ls02-t8 + 60 full, N = 4, both orders, seed 7, 0 failures), 0 Opus, 0 paid. Arm total: 164 Haiku calls.

### A1. Per turn block (same 3 sessions; ratio = Σ s_A / Σ s_B, item bootstrap B 2000 seed 11)
| turns | n | ratio A/B (95 % CI) | W/T/L | A promptTokens p50 / max | A totalMs p50 (B) |
|---|---|---|---|---|---|
| 1-5 (base run, same 3 sessions) | 15 | 1.417 (1.156-1.839) | 9/6/0 | 584 / 928 | 7.6-11.2 s (6.4-10.5 s) |
| 6-10 | 15 | 1.099 (0.959-1.294) | 4/10/1 | 926 / 1,186 | 12.5-15.1 s (0.5-8.4 s) |
| 11-15 | 15 | 1.175 (0.939-1.509) | 6/8/1 | 1,415 / 1,658 | 18.1-22.4 s (4.7-9.5 s) |
| 6-15 | 30 | 1.136 (0.993-1.320) | 10/18/2 | | |

Turns 6-15 split: follow-ups (13) 1.398 (0.978-1.944), 7/5/1; self-contained (17) **1.017 (0.950-1.095)**, 3/13/1. Per session, turns 6-15: ls02 1.355 (0.86-2.10), ls06 1.067 (0.92-1.33), ls08 1.088 (1.015-1.186).
Reading under the addendum: no block's CI lies wholly below 1, so **no drop detected up to turn 15**. The CI widths are about ±0.17 for turns 6-10 and ±0.29 for turns 11-15. The advantage of being in-session shrinks after turn 5 (1.42 → 1.10-1.18), because fewer late items need the history. On self-contained items it is parity, with no contamination.
The latency ranges are the per-turn p50s within each block. Zero errors.

### A2. Prompt-token curve to turn 15 and the app window
Per turn, the A promptTokens of the three sessions are listed (– = no LLM call). The history overhead is measured as A − B on the same item. The window columns are estimates (tokens ≈ 0.259 × characters, fitted on 133 dumped prompts of this arm).

| turn | A promptTokens (ls02, ls06, ls08) | measured history overhead (A − B) | adapter history, est. | app window, est. (last 6 msgs + summary from t8) |
|---|---|---|---|---|
| 1 | 638, 584, 516 | 0 | 0 | 0 |
| 3 | 417, 459, 534 | 144-184 | 167-185 | same |
| 5 | 647, 551, 738 | 312-324 | 240-364 | **135-256 (first truncation)** |
| 8 | 885, 836, – | 493-599 | 515-544 | 314-425 |
| 10 | 934, 1,009, 919 | 650-737 | 577-721 | 279-393 |
| 12 | 1,263, 1,551, 1,301 | 794-891 | 720-884 | 317-407 |
| 15 | 1,431, 1,543, 1,496 | 1,019-1,144 | 987-1,124 | 362-419 |

(The full per-turn values are in `aggregates/longsession.json` → `ext15.token_curve` and `ext15.history_window`.)

- **What the desktop adapter passes:** ALL previous turns, as `{summary: null, turns}`. In this arm, turn 15 therefore had 28 messages, about 1,000-1,140 history tokens.
- **What the app passes:** ChatScreen (cut 7 tree) sends the last 6 messages verbatim. After a turn completes with more than 6 turns in total (historyTurnThreshold 6, autoSummarize on), it writes a summary of the older messages (nPredict 150).
  - The window first truncates at **turn 5**: 8 prior messages, of which the app keeps 6, about 135-256 history tokens, against 240-364 passed by the adapter.
  - At turns 5-7 the app sends no summary, so the oldest turns are dropped with nothing replacing them. Turn-1 content is invisible on those turns.
  - From turn 8 on, the app sends a ≤ 150-token summary plus 6 messages. At turn 15 that is about 360-420 tokens, against about 1,000-1,120 in the adapter.
- **Not measured:** the app policy (dropped turns 5-7, then the summary) was not run here. Every number in this arm uses full history.
  - Any reference to turn 1 on turns 5-7 rests on the app's unmeasured gap. Example: ls06-t5, "the city I asked about first".
  - In the app this reference works only if a later message repeats the entity.
- **Projection:** full history fits as 379 + 74·t, which crosses 4,096 at **turn ~50**, before output tokens. Under the app window, history stays at about 400-450 tokens, so the prompt stays at about 1k tokens at any turn.

### A3. Coreference and card reuse (turns 6-15)
- Coreference heuristic: A fails **3/13** (B fails 9/13).
  - ls02-t6, "Who created it?", was answered with Peercoin. The engine's own turn-5 answer had drifted to Peercoin ("Peercoin allows staking…"), so "it" resolved to the last-mentioned coin. This is error propagation from the session's own earlier answer.
  - ls02-t7, "And the other one?", got a health decline. The emergency detector fires p = 0.928 on this 4-word question **with or without history**, giving `detector:fire` → health-strict → no source. This is a detector false positive, not a history effect.
  - ls02-t11, "…which one would I use for it?", resolved "it" to Ethereum (Etherscan) instead of Bitcoin.
- Card reuse: `grounding:fa-card-from-history` fired 0 times in turns 6-15. No first-aid card appeared in A that was absent from B, and no health-strict path was switched on by history. No-LLM items: 5 in A. Text byte-identical between A and B: 6/30. Errors: 0.

### A4. Worst 3, turns 6-15 (s_A − s_B)
1. **ls02-t14** (−2.33) "What does a missed attestation cost me?" A: "Missing an attestation results in a penalty of 0.5% of your staked ETH per epoch, with the penalty increasing if multiple attestations are missed in sequence…" B: "If you miss an attestation, you lose the associated staking rewards for that epoch…" A made up an inflated figure. The history held the earlier validator-penalty turns, so this is a hallucination primed by context.
2. **ls06-t10** (−1.17) "How many kilometres is 26.2 miles?" A: "…26.2 miles is approximately 42.1 kilometers. This is the standard dis…" B: "…approximately 42.18 kilometers. This is the standard di…" Both are close; this is judge noise at the decimal level.
3. **ls06-t6** (−0.33) "What is the best way to get around Kyoto?" A: "…by train or the Raku Bus, which skips non-tourist stops…" B: "…depends on your destination: take the Raku Bus (#100 or #101)…" A small difference.

### A5. Recommendation (addendum)
**Truncation/summary for quality: none supported.** Quality holds to turn 15 with full history, and self-contained answers are at parity. **Latency is the measured cost of long sessions:** p50 doubles to about 22 s at turns 14-15 on the desktop CPU, from prefill of about 1.0-1.1k history tokens. The app's existing 6-message window already avoids this, at about 400 tokens. If anything changes before PR-1, it should be on the app side and limited to the turn 5-7 gap, where older turns are dropped before any summary exists, for example by summarising from turn 5. That gap is unmeasured here, and it would need its own paired run of the app policy (adapter with a 6-message window + summary) before a claim. Two side findings belong to other lines, not history policy:
- the detector fires on "And the other one?" (p 0.93);
- the engine's own drifted answers (Peercoin) propagate through coreference.
