# PROMPT3M criterion (frozen 2026-10-19 before any generation)

Question (r4to 2026-10-19: "testar os 3 com a mesma tecnica de prompt, e rodar testes menores de comparacao"; objective = fewer wrong claims): does one honesty prompt technique cut wrong claims on all three small models without raising refusals, and how do the three compare?

Models (llama-server b11010 CPU on the mini, -t 4 -c 4096 --jinja, port 8191, the app's sampler temp 0.7 top_k 40 top_p 0.95 min_p 0.05 seed 42, 1 seed):
- M4 = Qwen3-4B-Instruct-2507 Q4_K_M (app default). D0 and D4 answers REUSED from HONESTPROMPT (same harness, sampler, seed, server build); only D5 generated.
- LF = LFM2.5-8B-A1B Q4_0 (maintainer's fast tier). Reasoning as the model's template produces it, split out with --reasoning-format deepseek; only the visible answer is audited; reasoning tokens reported.
- Q17 = Qwen3-1.7B Q4_K_M (lite tier), thinking OFF (chat_template_kwargs enable_thinking=false, as in the lite line).

Prompts (HONESTPROMPT prompts_lib, chat-template path = RagPure.assembleChatMessages): D0 (current Detailed), D4 (recommended honest Detailed), D5 = D4 with the sentences "State only facts you are sure of. ... A shorter correct answer beats a longer one." replaced by the payoff rule (I-CALM, PROMPT-LIT section 2 point 2):
"Scoring: each correct fact earns one point, each wrong fact loses two, and a detail you leave out costs nothing. So give a name, number, date, place or quote only when you are confident it is right; otherwise describe it in general terms. Never invent names, numbers, dates, places or quotes. If you don't know, say so in one sentence."
D5's style reminder = D4's. Context instruction = D4's.

Items: HONESTPROMPT set A (15 Thorough longsession turns, proxy contexts, own-history) + set B (20 v0.1 no-retrieval ids) = 35 answers per arm. Capability gate: HONESTPROMPT GATE (49 capability turns of chat-fu-v1 inside 119 generations, max_tokens 512, no context), refusal = the engine decline detector + extended list (tools/score_a2.py).
New arms: M4-D5, LF-D0, LF-D4, LF-D5, Q17-D0, Q17-D4, Q17-D5 (7 x 35 answers + 7 x 119 gate generations).

Primary metric: wrong-claim rate = WRONG / (WRONG + RIGHT) over checkable claims, from the sentence audit (DETAILED-HALLU / AUDIT-SPEC method of HONESTPROMPT, Opus auditors, blind to arm and model); secondary: RIGHT claims per answer, answered turns (any factual claim), refusals on the gate, output tokens, p50 latency.
Paired CI: answer-level bootstrap over the 35 items (B 2000, seed 11).

Decision per model X:
- D4 transfers to X if wrong rate D4 - D0 has CI upper < 0, gate refusals D4 <= D0 + 2/49, and RIGHT per answer D4 >= 0.6 x D0.
- D5 beats D4 on X if wrong rate D5 - D4 has CI upper < 0, OR (|D5 - D4| < 0.02 and RIGHT per answer D5 >= 1.15 x D4); in both cases with gate refusals D5 <= D4 + 2/49 and answered turns D5 >= D4 - 2.
- Recommended prompt for X = the best arm passing these rules (D0 if neither D4 nor D5 transfers).
- "Same technique for all three" = YES if one arm is recommended for all three models, else per-model recommendation.
Comparison table (descriptive, no decision): model x prompt -> wrong rate, RIGHT per answer, refusals, tokens, p50 latency on the mini CPU.

kill_if: prompt assembly differs from HONESTPROMPT's for D0/D4 strings (diff the smoke prompt); > 3 empty answers per arm; LF visible answer empty because reasoning consumed max_tokens on > 3 items (then raise LF max_tokens to 2048 for all LF arms, logged); mini disk < 25 GiB; the :8094 detector must stay up.
Caps: mini generation <= 4 h; audit <= 7 Opus agents (opus/medium); 0 Haiku judge calls required; paid 0.
Out of scope: Succinct; the 1.5B; the Haiku ratio (optional addendum if judge auth is restored).
