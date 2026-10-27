# PROMPT-LIT 2026-10-18: verified evidence for the HONESTPROMPT-2 wordings

TL;DR: The raw leads mostly hold up. Two need corrections: 2601.20126 is OVERSTATED for Qwen3-4B, and SkillShield's numbers check out but it is not a "direct match" for us. The pass found two new sources that matter. In **I-CALM (2604.03904)**, a plain "say I don't know" prompt on Llama-3-8B answered only 0.2 % of long-tail questions. A prompt that spelled out the payoff (+1 correct, +0.4 IDK, −1 wrong) and added norms answered 45 %, with fewer errors among those answers. In **XSTest**, a cautious system prompt raised full refusals on safe prompts from 14 % to 38 %. Together these suggest we keep the honesty rule but limit it to factual specifics, and give capability requests their own explicit permission.
Input: PROMPT-LIT-2026-10-18-raw.md (Haiku). Method: full-text WebFetch (arXiv HTML) of each source plus 10 web searches. [F] = numbers read in the paper; [S] = search snippet only. No commits.

## §1 Verified sources

| Source | Measured | Sizes | Number that matters for us | Raw line |
|---|---|---|---|---|
| Laban et al., Lost in multi-turn, 2505.06120 [F] | 6 tasks, Full vs Sharded, 200k sims; aptitude (P90) vs unreliability (P90−P10); Recap/Snowball and temperature fixes | 15 models: Llama3.1-8B, OLMo-2-13B, Phi-4 … Gemini 2.5 Pro | −39 % avg; aptitude −16 %, unreliability **+112 %**. Snowball (restate shards every turn) 50.4→61.8 (GPT-4o-mini), recovers 15–20 % of the loss. Temp 0 does not help multi-turn. Fixes tested only on GPT-4o(-mini) | **CONFIRMED** (the "fixes insufficient" claim holds: they help only partly) |
| Rewarding Intellectual Humility, 2601.20126 [F] | RLVR ternary reward; MedMCQA, MATH; Acc / Wrong / IDK | Granite-3.3-2B, **Qwen3-4B-Instruct** | **Prompt-only IDK row, Qwen3-4B MedMCQA:** Acc 67.5→65.4, Wrong 32.5→27.3, IDK 7.3 %. Every RL setting loses ≥ 7 acc points on Qwen (r_abs 0.3: Acc 48.0, Wrong 10.3, IDK 41). Prompt: "Answer only if you are certain, else choose I Don't Know." | **OVERSTATED**: "without severe accuracy loss" fails for Qwen3-4B. The prompt row is the useful datum |
| FaithfulRAG, ACL 2025, 2506.08938 [F] | Faithfulness under context conflict; prompting baselines (Opin, ATTR, KRE) and decoding (CAD) | Llama3.1-8B, Qwen2.5-7B, Mistral-7B (+3B/13B appx) | Non-conflict golden contexts (Llama3.1-8B): strict KRE prompt SQuAD 95.2→81.4, MuSiQue 84→**38.3 (refusal-driven)**; ATTR −1…−3.6. FaithfulRAG +1.3/+1.4 | **CONFIRMED** (harm depends on the prompt; Opin is neutral) |
| SkillShield, 2608.25817 [F] | Safety refusals on 731 benign SWE-Bench Pro tasks under safety-skill system prompts | Ministral-3-8B, Nemotron-Nano-9B, Qwen3-Coder-Next (size n/s), DeepSeek V3.2, Seed 1.6 Flash, GPT-oss-120B | 32/36 configs ≤ 0.68 %; Reactive (broad, intent-level) per-bundle mean 1.49 %, **Qwen3 B4 16.3 % vs 0.27 % Proactive** (concrete, checkable signals) | Numbers **CONFIRMED**; "direct match" **OVERSTATED**: safety skills in a coding agent, not a 4B and not honesty wording |
| Huang et al., ACL 2024, 2402.04315 [F] | ALCE (ASQA/QAMPARI/ELI5) correctness + citation rec/prec | LLaMA-2-7B vs ChatGPT | ICL 7B citation recall **14.1** vs ChatGPT 74.7 (ASQA); distil + fine-grained RS+RL 77.8 / 76.3 prec; EM 34.2→40.1 | **CONFIRMED** |
| I-CALM, 2604.03904 [F] (new) | Selective answering: coverage + false-answer rate (FAR) among answered; IDK prompt vs payoff + norms prompt | **Llama-3-8B-Instruct**, GPT-5 mini, Gemini-3.1-Flash-Lite | PopQA: baseline cov 0.963 / FAR 0.683; **explicit IDK prompt cov 0.002**; payoff only cov 0.775 / FAR 0.650; payoff + norms **cov 0.447 / FAR 0.515**. TriviaQA (model knows more): cov 0.952 / FAR 0.280 | new; fills gap (a) for short QA |
| XSTest, 2308.01263 [S, numbers in the paper's text] | Full refusal on 250 safe prompts, ± system prompt | Llama-2-70b-chat, Mistral-7B | Default (cautious) system prompt **38 % vs 14 %** without; Mistral + guardrail prompt 9.6 % | new; nearest to gap (b) |
| MS-XSB, 2510.08158 [F] | Exaggerated refusal single vs multi-turn; post-hoc mitigation | Multi-turn: R1, Llama-3.3-70B, Qwen2-VL-7B, DS-Coder-Lite-16B; mitigation: Llama-2-7B/13B, Llama-3(.1)-8B | Llama-3-8B safe compliance 88.4→96.8 with prompt rephrasing (unsafe compliance rises too). Multi-turn drop shown only in figures (R1 compliance ~70→56 %). Paper is internally inconsistent (Qwen2-VL 57.2 vs 27.4) | **OVERSTATED** (Llama-8B only in mitigation; multi-turn numbers figure-only) |
| Over-Searching, 2601.05503 [F] | Abstention over 1–9 turns; prompt strategies | 10 models incl. Llama-3.2-3B, Hermes3-3B | All-unanswerable history keeps or raises abstention, answerable history erodes it. Abstention-aware prompt: abstention acc 50.2→60.2, answer acc 71.4→69.9 (avg) | **CONFIRMED** |
| FaithEval, 2410.03727 [F] | Unanswerable / inconsistent / counterfactual contexts | Llama-3(.1)-8B, Mistral-7B, Phi-3(.5)-mini, Gemma-2-9B … | Unanswerable acc: Phi-3-mini 6.3, Llama-3.1-8B 37.6, Gemma-2-9B 50.3. The "say unknown" conflict instruction lowers normal-context acc (Claude 0.90→0.85, GPT-4o 0.85→0.83). No wording variants | **CONFIRMED** |
| Zhao et al., ACL Findings 2025, 2505.23295 [F] | Precision vs length ("Generate with around x words"), BAFE | **GPT-4o only** | Bios 94.5 % (100 words) → 90.5 % (~500 words); splitting one budget across 2 subtopics raises precision +2.3–2.9 (facts exhaustion) | **OVERSTATED** for us: the size is now known and it is not small |
| Cacioli, 2604.24070 [F, abstract] | Verbal confidence after confidence-conditioned SFT | Gemma 3 4B-it | Pre-registered phase negative (AUROC2 0.554→0.509); exploratory fine-tune 0.774 vs self-consistency 0.999 | **OVERSTATED**: negative only for the pre-registered phase; base-model verbal tags still low-validity |
| Qwen3-4B-Instruct-2507 card [F] | Vendor settings | 4B | temp 0.7, top_p 0.8, top_k 20, min_p 0; presence_penalty 0–2; non-thinking only; "use prompts to standardize outputs". Nothing on system prompts or hallucination | **CONFIRMED** |

Gaps (3+ searches each):
- **(a)** Partly filled. Abstention wording with both answer rate and errors at ≤ 8B is covered by I-CALM (8B) and the 2601.20126 prompt row (4B), but only for short QA. No long-form study.
- **(b)** Not filled for Qwen3 / 8B with wording variants. The nearest evidence is XSTest (Llama-2-70b) and a STAR-S snippet: on Qwen3-14B a "plain prompt" raised XSTest over-refusal from 4.4 % to 14.0 % [S, not opened]. Llama-3-8B XSTest baseline is 8.4 % [S].
- **(c)** Empty beyond the card. No Qwen system-prompt guidance for 2507.
- **(d)** Empty at ≤ 8B. Only GPT-4o (Zhao), plus a LongFact snippet: "prompted shorter → higher precision" [S].

## §2 What the evidence supports for our case

1. **The D1 collapse is a known small-model effect, and it is worst on long-tail questions.** The explicit IDK prompt cut Llama-3-8B to 0.2 % coverage on PopQA. On questions the model knows, the same kind of prompt barely bites: Qwen3-4B on MedMCQA abstained on only 7 % (2601.20126); I-CALM on TriviaQA kept 95 % coverage. Our 15 Thorough turns (local Lisbon/Porto specifics, burns, rollups) sit at the long-tail end. (I-CALM, 2601.20126)
2. **A graded trade-off beats an absolute "only if sure" rule.** Correct > skip > wrong, with norms, kept 45 % coverage on PopQA and cut errors among answered from 68 % to 52 % (I-CALM). The model should leave out the uncertain *detail*, not the whole answer.
3. **Broad, intent-level rules spread to unrelated requests; narrow, concrete rules do not.** SkillShield: Reactive 16.3 % vs Proactive 0.27 %. XSTest: a cautious system prompt took safe refusals from 14 % to 38 %. Our D1 refusing code and a computation given in the question fits this pattern. The rule should name only factual specifics and explicitly exempt capability tasks.
4. **"If the context doesn't cover it, say so and stop" is the wrong direction for RAG.** Strict prompts on 7–8B collapse on good contexts (KRE MuSiQue 84 → 38, refusal-driven; FaithfulRAG), and the "say unknown" instruction lowers normal-context accuracy (FaithEval). This argues for context first, then general knowledge, with no stop clause.
5. **Refusals carry across turns, and a per-turn restatement helps only partly.** All-unanswerable history sustains abstention (Over-Searching). Unreliability doubles in multi-turn, and Snowball (restating the rules each turn) recovers 15–20 % of the loss (Laban). So the capability permission belongs in the per-turn style reminder too, and we should still expect some carry-over.
6. **Length breeds errors, and inline confidence or citations are weak levers at 4–7B.** Precision falls with length; spending the same budget on separate subtopics helps (Zhao; GPT-4o only). DETAILED-HALLU fits this: 28/40 errors were mid-answer and none were in the summary. Prompt-only citations at 7B are poor (Huang), and verbal confidence at 4B has low validity (Cacioli). Count "(not sure)" marks; do not trust them.

## §3 Five wordings for the Detailed style, ranked by evidence

1. **W1, honest + capability (scoped rule).** Motivated by SkillShield (concrete signals), XSTest, I-CALM and our D1 data. Appended to the Detailed systemPrompt:
   > "Be accurate about facts: never invent names, numbers, dates, places or quotes. Leave out any specific detail you are not sure of and keep the rest of the answer. This rule covers facts only. Always do what the user asks: write code, give examples, make tables, and calculate from numbers given in the question."
2. **W2, graded payoff.** Motivated by I-CALM (payoff + norms) and the 2601.20126 ternary reward expressed as text:
   > "Answer as fully as you can. A correct detail helps the user, a skipped detail costs little, a wrong detail can harm them. So include what you know well, skip specifics you are unsure of, and say you don't know only when you know nothing useful about the question."
3. **W3, grounded first, then general knowledge, uncertainty marked inline.** Motivated by FaithfulRAG and FaithEval; the inline mark is weak per Cacioli. Replaces CONTEXT_INSTRUCTION's second sentence:
   > "Use the numbered sources first and cite them like [1]. If they do not cover part of the question, answer that part from general knowledge and begin that sentence with \"Generally,\". Write \"(not sure)\" after any figure or name you are unsure of. Never stop just because the sources are incomplete."
4. **W5, per-turn reminder (anti-snowball).** Motivated by Laban's Snowball and Over-Searching's history effect. Replaces the Detailed styleReminder:
   > "(Response style: detailed. Answer this question on its own, even if earlier answers said something was unknown. Leave out facts you are unsure of. Code, examples, tables and calculations: always do them.)"
5. **W4, length shape.** Motivated by Zhao (facts exhaustion, split budget; GPT-4o only) and DETAILED-HALLU (mid-answer errors). Replaces "Explain in depth … 3–5 paragraphs":
   > "Give a detailed answer: 3–5 short paragraphs, each on a different aspect of the question. Use the length to explain how and why, not to add more names, numbers or dates. End with a one-line summary."

Each wording drops "A shorter correct answer beats a longer one": in D1 that line was a brevity pressure that pushed one-sentence refusals.

## §4 Proposed arm HONESTPROMPT-2 (freeze a sha256 criterion before running)

- **Arms.** All arms run on the desktop 4B with the app's prompt assembly and the v1 chat-template harness.
  - **D0**: Detailed-current (control).
  - **D1**: v1 honest prompt; reuse the v1 answers where the harness matches, else regenerate.
  - **D3** = W1 + W4 + W5 (with-sources instruction = v1 variant (a)).
  - **D4** = W2 + W4 + W5.
  - **D5** = D3 + W3. It differs from D3 only on turns with context.
  - **S0**: Succinct-current, as the WRONG floor.
- **Sets.**
  - (A) the 15 Thorough turns in session order, with history = each arm's own prior answers.
  - (C) the CHAT-FU-v1 capability turns (49 asks), replayed with the arm's own history.
  - Optional: v0.1 73 standalone for the ratio.
- **Metrics.**
  - Primary: sentence-level WRONG rate (DETAILED-HALLU method, one Opus auditor, set A).
  - Answer rate (Y/P/N per answer, set A).
  - Capability-refusal rate: the engine's decline detector plus a 20-turn hand check (set C).
  - Haiku L1 ratio vs D0, both orders.
  - Tertiary: "not sure / not covered" sentences, the "(not sure)" mark count (D5), and length.
- **Verdict rule (proposal).** A candidate is adoptable only if all four hold:
  - WRONG ≤ 0.08 (D0 0.19; S0 ≈ 0.10 on the same audit)
  - answer rate ≥ 13/15
  - capability refusal ≤ S0 + 5 pts
  - Haiku ratio ≥ D0 − 0.03

  WRONG falling but answers going emptier = PARTIAL, as in v1.
- **Expected effects (each is a prior, not a promise).**
  - **D3 vs D1:** capability refusals fall to about S0's level, because the scoped rule plus the explicit exemption should stop the spread (SkillShield, XSTest). The answer rate recovers to most of 15, and WRONG lands between D1 and D0 (I-CALM: coverage up means FAR up).
  - **D4:** coverage sits between D1 and D0, and fewer errors among answered (I-CALM PopQA 0.45 / FAR −25 % rel). It is at risk of keeping too many refusals on long-tail turns.
  - **D5 vs D3:** on with-context turns, no "say so and stop" refusals (FaithfulRAG KRE, FaithEval). The "(not sure)" marks will be noisy (Cacioli), so do not credit them.
  - **W5 (in D3/D4/D5):** refusal carry-over from turn 3 onward shrinks but does not vanish (Laban Snowball +15–20 % recovery; Over-Searching history effect). Measure it as answer rate on turns 3–5 vs turns 1–2.
  - **W4:** WRONG per answer falls slightly at equal length (Zhao split-budget +2–3 pts; GPT-4o only, weakest prior).
- **Cost.**
  - Generation: 4 new arms × (15 + 49) turns on the mini.
  - Audit: about 60 answers.
  - Haiku: 2 × arms × N.
  - 0 paid API.

## §5 UNKNOWN

- No ≤ 8B source tests long-form honesty wording. Every transfer from short QA (I-CALM, 2601.20126) to 3–5 paragraph answers is our inference.
- Whether the "Qwen-3-4B-Instruct" in 2601.20126 is the 2507 build is not stated (its Fig. 2 caption also mislabels the model).
- No Qwen3 refusal-by-wording data at 4B. The XSTest 38/14 figure is Llama-2-70b-chat.
- Sampler confound: the app/harness uses top_k 40 / top_p 0.95 / min_p 0.05, while the Qwen card says top_k 20 / top_p 0.8 / min_p 0. The arm should keep the app's sampler and log this; refusal and WRONG rates may shift with it.
- I-CALM's TriviaQA vs PopQA gap suggests the D1 collapse depends on how long-tail the turns are. Our 15 turns may not represent v0.1.
- Whether feeding prior refusals back verbatim in history (last-6 window) is itself the snowball cause is an engine question, not a prompt one. Not tested here.
- STAR-S (Qwen3-14B, 4.4 → 14.0 %) and LongFact (shorter → more precise) are snippet-level only.
