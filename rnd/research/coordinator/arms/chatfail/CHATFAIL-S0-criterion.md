# CHATFAIL S0: multi-turn intent failures in the reference engine — probe set + deterministic replay (frozen 2026-10-18 00:5x, coordinator; r4to's instruction 10-18 via the CHATFAIL session: "step 0 now, 0 calls")

## Tags
Tags: probe
Ruleset: 30

## Question
From CHATFAIL-PLAN.md: a 6-turn chat ends with two refusals to write code and a repeated definition. Four rules are blamed: (1) FollowUp anchor = only the previous user turn (FollowUp.kt:80-86 / TS equivalent), (2) the code-intent regex matches only "write (a|some) code" (classify.ts:18 / Classify.kt:39), (3) GROUNDING "You can only respond with text…" read as "I can't write code", (4) refusals re-enter the history. Step 0 measures (1) and (2) deterministically on a public probe set and prototypes L2 (intent) + L3 (anchor); (3) and (4) need generation (step 1 / HONESTPROMPT addendum 2). Mechanism seen / not seen; 0 judge calls.

## Fixed inputs
- Probe set CHAT-FU-v1 (new, public, agent-written → dev data; boar-eval/bench/slices/chat-fu-v1/chats.jsonl): 30 chats × 4–6 turns, topics the claim kit covers (crypto, travel, first aid, general science), turn 1 a normal question, turns 2+ follow-ups whose intent changes: code/example ("write it", "show me the code", "not even an example?"), "what does it look like", "in a table", "shorter", "in Portuguese", "compare with X", plus 6 control chats whose follow-ups stay lookup. Each turn carries labels: expected_intent ∈ {lookup, chat, code, format, translate, compare}, expected_anchor (the turn index whose subject applies), capability_request (bool). sha256 recorded.
- Engine: the TS reference engine at wt/pr1 (cut 7 + PR #85 patches) for classify() and the follow-up planner; the Kotlin twins on UPSTREAM_REPO/boar-app upstream/fullnative-dev (read-only via git show) for a string-level diff of the rules (not executed).
- Replay: a node script calling classify() and the follow-up plan function per turn with the chat history as the engine would hold it (user turns + a placeholder assistant answer; no model), before vs after a prototype patch L2 (+code/example/show-me intents, "what does it look like" after a technical turn) + L3 (anchor = latest user turn naming a subject or with sources).

## Power
expected_delta: n/a (mechanism probe)
n: 30 chats, ≈ 150 turns, ≈ 60 capability/format turns
seeds: n/a (deterministic)
mde: n/a
slice: n/a
l1_futility: n/a
reopen: n/a
split: none

## Ceiling (RULE 29; 0 calls, before the freeze)
ceiling: n/a
bar_ceiling: n/a (product UX arm, not a bar lever)
launch: probe, 0 calls, mac-cpu
transfer: findings go to the app maintainer via the liaison (Kotlin rules are twins)

## Budget (RULE 29)
wall_cap: 2 h agent
calls_cap: Haiku 0 / Opus 0; 0 paid; 0 web
smoke: 3 chats through the replay before the full 30
kill_if: the TS engine at wt/pr1 cannot be imported for classify/follow-up without a model (then report the rules by code reading only)
checkpoint: n/a
subset_step0: n/a

## Precheck
token_projection: n/a / token_budget: n/a
disk_peak_gib: 0.05
off_baseline: current rules
call_pattern: 0 calls
lane: mac-cpu
opus_clause: none
wall_cap_h: 2
parallelism: 1
run_type: latency

## Stages and rules
1. Write CHAT-FU-v1 (+ NOTICE.md: agent-written dev data, never a claim set) and its labels; sha256.
2. Replay current rules: per turn, intent class and anchor turn; tables: intent accuracy vs expected (overall and on capability_request turns), anchor accuracy from turn 3 on, how many capability turns would go to lookup with the Succinct 2–3-sentence cap.
3. Prototype L2 + L3 as a patch on a scratch copy of wt/pr1 (never commit to wt/pr1; patch file + sha256 in tools/); replay again; the same tables after; regressions on the 6 control chats (must be 0 intent changes) and on the v0.1 60 public questions as single turns (classify unchanged on ≥ 58/60, list any change).
4. Verdict: SEEN if the current rules misroute ≥ 50 % of capability_request turns or lose the anchor on ≥ 50 % of turns ≥ 3, AND the prototype fixes ≥ 80 % of them with 0 control regressions and ≤ 2 v0.1 classify changes; PARTIAL if fixed < 80 % or regressions; NOT SEEN if the current rules already route ≥ 80 % correctly. Output arms/chatfail/CHATFAIL-S0.md (≤ 60 lines, tables), the slice, tools/, the patch. Step 1 (generation: refusal rate with current vs L1 vs L1+L2+L3+L4, 4B and 1.5B/1.7B) is frozen separately after S0.
