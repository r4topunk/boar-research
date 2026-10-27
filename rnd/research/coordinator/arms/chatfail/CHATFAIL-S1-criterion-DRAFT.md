# CHATFAIL S1: do the prompt fix (L1), the routing fixes (L2 + L3) and dropping refusals from history (L4) make the small models do what users ask in multi-turn chats? (DRAFT 2026-10-18 by the CHATFAIL session; the coordinator edits, freezes, hashes)

Status: **DRAFT, not frozen.** The loop owns the freeze (Ruleset 30). Numbers marked (set at freeze) are proposals.

## Tags
Tags: none
Ruleset: 30

## Question
CHATFAIL S0 (CHATFAIL-S0.md, criterion 3d4e6ba5) measured two routing mechanisms with no model. On CHAT-FU-v1, the current rules misroute 32 of the 49 capability turns and lose the anchor on 79 of the 99 turns from turn 3 on. The L2+L3 prototype fixes 17 of the 32 misrouted turns (0 → 81 % on code asks) and 57 of the 79 lost anchors. Two mechanisms need a model and are still unmeasured: (3) the GROUNDING line ("You can only respond with text") read as "I can't write code", and (4) refusals that go back into history and snowball. HONESTPROMPT set A shows the snowball directly: once D1 refuses at t1, every later turn of that session refuses. S1 asks how much of the user-visible failure each fix removes, measured on the answers, on both the claim 4B and the iPhone 13 model.

## Fixed inputs
- Probe set: CHAT-FU-v1, boar-eval/bench/slices/chat-fu-v1/chats.jsonl, sha 303876ed…408e, unchanged since S0: 30 chats, 159 turns, 49 capability turns (21 code, 18 format, 10 translate), 6 control chats. Dev data, agent-written.
- Models (both on the mini, llama-server b11010, seed 42, the engine sampler 0.7/40/0.95/0.05, max tokens = the Succinct cap the app uses; code turns get the `code` task cap where L2 routes them):
  - M4 = Qwen3-4B-Instruct-2507 Q4_K_M (the claim and app model; sha as HONESTPROMPT).
  - M1 = Qwen2.5-1.5B-Instruct Q4_K_M (shared-models; the iPhone 13 path per boar-ios AGENTS.md; verify the sha against the boar-ios catalog).
- Prompt assembly: HONESTPROMPT tools/prompts_lib.py (RagPure.assemblePrompt from fullnative-dev, verbatim strings), tone Succinct only (the default). Detailed is out of scope: HONESTPROMPT covers it.
- Chat replay: turns in order, history = the arm's **own** prior answers (that is the only way to see mechanism 4), with the app's history budget.
- Routing per turn: classify() + the follow-up planner, as in S0 (wt/pr1 classify, fullnative-dev followUp, scratch copies). The planner's search text goes to the engine retriever on the claim kit (replay-retrieval.sh path, relevance floor as the engine). Retrieval-irrelevant classes (code, translate, …) get no context. Contexts are cached per (arm-routing, turn), so arms that share routing share contexts byte for byte.
- Arms (each one cumulative over the one before, so each step isolates one lever):
  - **C0** current: cut 7 rules + current strings.
  - **A1** = C0 + L1: GROUNDING gets "You can write text, code and examples: writing is not a physical action." The Succinct styleReminder gets "…unless the user asks for code, an example, a table or a translation." Routing unchanged.
  - **A2** = A1 + L2 + L3: tools/chatfail-l2l3.patch (sha f7972d37…ca98), unchanged from S0.
  - **A3** = A2 + L4: assistant turns the decline detector flags are dropped from the history block (the user turn stays).
  - (Out of scope: L2b format/translate intents, the 12 of the 15 turns still misrouted after S0. Its own probe once a patch exists. A2/A3 still show how much the prompt alone fixes on those turns.)
- Decline detector: the engine's (cite the function: boar-app src/eval/answerEval.pure.ts or the TS twin of the Kotlin/Swift `DeepResearch` decline check, the same one HONESTPROMPT addendum 2 uses).

## Metrics (per capability turn; deterministic except where marked)
- **fulfilled** (primary): code ask → the answer has a fenced code block or ≥ 3 lines that parse as code (a regex for keywords/braces/semicolons, fixed at freeze). Format ask → the requested shape is there (a markdown table for "table", list markers for "list", length ≤ 50 % of the previous answer for "shorter", …; the map is set at freeze from the 18 labels). Translate ask → the answer's language = the target (a stopword-ratio detector, fixed at freeze), and it is not a refusal.
- **refusal**: the decline detector fires (secondary; also reported on non-capability turns as snowball spill-over).
- **snowball**: P(refusal at turn t | refusal at t−1) within a chat, per arm.
- **hand check** (auditor, one Opus agent, ≤ 60 answers): 20 code answers (A2 and A3, M4 and M1: plausible and on topic, Y/P/N), 20 random fulfilled=0 turns (detector misses), and every first-aid control turn (safety: no arm may add a WRONG health instruction).
- **non-regression** (L1 changes every prompt): bench v0.1, the 57 non-venue ids, single turn, C0 vs A1 on M4, Haiku 5.5-low judge.v1 both orders, N = 4 shards.

## Power
expected_delta: fulfilled A2 − C0 ≈ +0.40 on code asks (routing goes 0 → 81 %, and L1 removes the "can't" reading); A1 − C0 ≈ +0.15 (the prompt alone, routing still caps at 2–3 sentences); A3 − A2 ≈ −0.05 refusal (only chats that already refused)
n: 49 capability turns × 30 chats per arm per model (cluster = chat)
seeds: 1 (temp 0.7; per SEEDVAR, a 1-seed Δ under 0.05 is noise, so the clauses below sit above that)
mde: fulfilled ±0.10 (chat-cluster bootstrap, 2000 resamples, seed 1)
split: declared: code / format / translate; M4 / M1; control chats separately

## Ceiling (RULE 29)
ceiling: fulfilled 1.0 on 49 turns; a C0 fulfilled near 0 on code asks is expected from r4to's live trace (c01: 0/5)
bar_ceiling: n/a (product UX arm; v0.1 non-regression guards the bar)
transfer: findings and any adopted strings go to the app maintainer via the liaison (the Kotlin rules are twins, S0)

## Budget (RULE 29)
wall_cap: about 3.5 h mini generation (159 turns × 4 arms × 2 models = 1,272 short generations; M4 ≈ 10 s, M1 ≈ 4 s each) + 20 min for v0.1 57 × 2 arms on M4 + 1 h audit agent
calls_cap: Haiku 57 × 2 orders × 2 arms = 228 (+ ≤ 8 preflight); Opus 0 judge calls (the auditor is an agent); 0 paid; 0 web
smoke: chat c01 through all 4 arms on M4 first; diff C0's assembled prompts against HONESTPROMPT's S0 prompts for the same turn (same strings); C0 c01 should reproduce the live refusals at t5/t6 (if it does not, report and continue: the phone ran M1 or a different history)
kill_if: prompt strings differ from fullnative-dev on any fixed string; > 3 empty answers per arm per model; mini disk < 25 GiB
checkpoint: after M4 (all 4 arms), before M1
reuse: if HONESTPROMPT addendum 2's S0 generations on the capability turns have byte-identical prompts to C0 here (no context), reuse them and log it; otherwise regenerate

## Verdict rule (per model; M4 decides the engine recommendation, M1 decides the iPhone note)
- **PASS (recommend L1 + L2 + L3 to the app maintainer as an engine change):** fulfilled A2 − C0 ≥ +0.20 on capability turns (CI excludes 0), refusal A2 ≤ C0, 0 control-chat intent changes (already S0), v0.1 Haiku ratio A1 − C0 ≥ −0.03 (or CI includes 0), 0 new WRONG health instructions in the audit.
- **L1-ONLY:** A1 − C0 reaches ≥ 2/3 of A2 − C0 → recommend only the prompt line (no routing change before 10-20), and routing goes to post-10-20 with L2b.
- **L4 adopted** only if A3 − A2 refusal ≤ −0.05 (CI excludes 0) and fulfilled does not fall.
- **PARTIAL:** fulfilled rises ≥ +0.10 but < +0.20, or the v0.1 ratio clause fails → report, no recommendation; the next step is L2b and the format map.
- **NO:** fulfilled A2 − C0 < +0.10.
- Interaction with HONESTPROMPT: if HONESTPROMPT's addendum 2 already ran D1+L1/S1+L1, its S1+L1 capability turns are A1-equivalent with the honest sentence added. Report both side by side and do not re-run.

## Precheck
token_projection: Succinct ≈ 120 output tokens; code turns ≈ 250
disk_peak_gib: 0.1 (+ 1.1 GB if the 1.5B GGUF has to be copied to the mini)
off_baseline: C0
call_pattern: generation on the mini; Haiku N = 4 both orders on v0.1 57 × 2; one audit agent
lane: mini-long → judge → agent
run_type: 4b-patch (+ 1.5b)
parallelism: 1 server per model / 4 judge shards

## Open for the coordinator (decide at freeze)
- The fulfilled detectors (code regex, format map, language detector): write and hash them before the first generation, and calibrate on CHAT-FU-v1's turn texts only, never on answers.
- Whether to add a no-retrieval variant of A2 on M1. The phone's 4 GB budget may make the follow-up retrieval cost matter; this is a speed question, out of scope unless cheap.
