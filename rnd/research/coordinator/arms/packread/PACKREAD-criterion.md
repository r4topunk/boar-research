# PACKREAD criterion (frozen 2026-10-19 before any generation)

Question (r4to 2026-10-19: "melhorar nossos testes com fonte, considerando que o usuario vai ter a knowledge pack do que ele esta perguntando ... focar nessa linha para a finalizacao da bounty"): when the user has the matching pack installed, which small model and which prompt answer best and state the fewest wrong claims?

Condition: the pack self-tests (public dev items written from each pack) with the context the engine (cut 7 + HEADPASS-X2b) actually retrieved, taken byte-identical from arms/headpass-st/gen-x2b/st-*-cut7-headpassx2b-s42.prompts.jsonl. Only the style part of the system message (persona + context instruction, the text before " You are BOAR, an offline AI research app") and the user's "(Response style: ...)" reminder change per prompt arm; identity text, context block and question are unchanged.
Items: the first 6 ids (sorted) of each of the 9 packs with X2b prompts (factbook, firstaid-en, medlineplus-en, simplewiki-en, qa bitcoin/ethereum/health/outdoors/travel) = 54. Audit slice: the first 2 of those 6 per pack = 18.
Models and server: as PROMPT3M (criterion 50da1b4b): M4 Qwen3-4B-Instruct-2507 Q4_K_M, LF LFM2.5-8B-A1B Q4_0 (max_tokens 2048, reasoning split, visible answer judged), Q17 Qwen3-1.7B Q4_K_M (thinking off); llama-server b11010 CPU, -c 4096, app sampler (0.7/40/0.95/0.05, seed 42), 1 seed.
Prompt arms: D0, D4, D5 exactly as PROMPT3M (HONESTPROMPT prompts_lib + D5 payoff rule); max_tokens 1024 (LF 2048). 9 arms x 54 = 486 generations.
Anchor (not an arm): the existing cut 7 + X2b engine answers (4B, Succinct engine prompt) and their Haiku judgments on the same ids.

Metrics:
- Q (co-primary) = Haiku 5.5-low judge ratio vs each pack's self-test references (boar-eval bench/selftest/<pack>), judge.v1, both orders, N = 4 shards, 54 items per arm; paired item-bootstrap CI (B 2000, seed 11).
- W (co-primary) = wrong-claim rate WRONG/(WRONG+RIGHT) from a blind Opus sentence audit (HONESTPROMPT AUDIT method; a claim is WRONG if contradicted by the context or by well-established fact; unsupported-but-true counted separately as UNSUPPORTED) on the 18-item audit slice; RIGHT per answer reported.
- Also: answered vs declined, output tokens, p50 latency (mini CPU), LF truncations.

Decision (per model X):
- Best prompt for X = the arm with the lowest W among arms whose Q is not below D0's by more than 0.03 (paired CI upper end not below -0.03 counts as not below); ties within 0.02 W -> higher Q.
- Model ranking under the pack condition = by Q of each model's best prompt, W reported beside it; a model is "pack-ready" if its best arm has Q CI overlapping the M4 best arm's Q and W <= M4's W + 0.03.
- Same technique for all three = YES if one prompt arm is best for all three.
Descriptive: per-pack Q table (does any model fail a pack type, e.g. qa vs topic, health vs crypto).

kill_if: any item's context differs from the source prompts file; > 3 empty answers per arm; LF truncations > 10 of 54 in an arm (then report LF as "budget-limited", no re-run today); mini disk < 25 GiB; :8094 stays up.
Caps: generation <= 5 h; Haiku judge uncapped (~ 486 x 2 calls); audit <= 6 Opus agents (opus/medium), 162 answers; paid 0.
Relation to PROMPT3M: PROMPT3M is paused after its Q17 main set (r4to's priority switch); its data are kept and may be completed later.
