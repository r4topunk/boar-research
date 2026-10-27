# Danger detector v2: embedding head + resident-LLM yes/no for the uncertain band (fixes PT recall)
TL;DR: v1's bge-small-en head is English-bound (blind PT recall 8/12). v2 keeps v1 for confident scores and asks the chat model BOAR already has loaded a grammar-constrained yes/no only when 0.25 < p < 0.80. On my sets that lifts PT recall from 21/28 to 28/28 at 0–2/236 false positives, with an LLM call on ~14 % of questions.
Lane: Compass · Status: ready-to-test (frozen, needs a new blind set) · Priority: A
Axes moved: safety ↑ / truthfulness ↑ (PT danger questions stop falling through to memory answers in arm A1); latency: +1 short LLM prefill (~150 tokens) on the ~14 % of questions in the band, and only where A1 acts (an answer about to be generated with 0 sources); resources ~0 (reuses the resident model and the shared query vector); quality ~0.
Fits BOAR? Yes on both tiers, with no new model or download. In A1 the gate sits just before generation, so the chat model is already loaded (or is being loaded for the answer anyway). Desktop cost per call: Qwen2.5-1.5B 373 ms, Qwen3-4B 1131 ms (M1 Ultra, Metal, 303 calls). UNKNOWN: on-device prefill time for ~150 tokens. Estimate ~0.5–1.5 s on iPhone 13 (1.5B) and ~1–3 s on Android (4B), only in the band. llama.rn supports GBNF grammars (`completion({ grammar })`), so the yes/no constraint ports.
Evidence:
- **The problem, measured blind:** v1 on hm-fresh3 caught EN 12/12 but PT only 8/12 (QUEUE #4b, coordinator).
- **Local diagnosis (this cycle, `exp/pt-recall/`):** I wrote PT translations of the 25 EN danger items + 3 unaccented variants (the "pt-mirror", 28 items). Same content, different language. v1: **EN 25/25 vs PT mirror 21/28**, confirming a ~25-point language gap. bge-small-en-v1.5 is an English model (BAAI model card, https://huggingface.co/BAAI/bge-small-en-v1.5, accessed 2026-10-01).
- **Cheap fixes tried first (rejected):**

  | Fix | PT mirror (28) | eval PT danger (14) | FP (236) |
  |---|---|---|---|
  | v1 alone | 21 | 12 | 0 |
  | + app's PT→EN anchors (`englishSearchTerms` + `englishNamesIn` over the bundled 173k-entry `pt-en.json`) appended to the text | 22 | 12 | 0 |
  | + 25 PT positive / 20 PT negative prototypes (retrained head) | 23 | 12 | 0 |

  The anchors are noisy for this purpose ("dedos brancos" → "White people", "aparelho" → "Brickwork", "pilha de relógio" → "Clock").
- **LLM as classifier (zero-shot, prompt written once, not iterated; `llm-prompt.txt`):**

  | Detector | PT mirror | eval PT danger | eval EN danger | FP PT (77) | FP EN (159) | LLM calls |
  |---|---|---|---|---|---|---|
  | Qwen2.5-1.5B alone | 27/28 | 13/14 | 22/25 | 1 | 2 | 100 % |
  | Qwen3-4B alone | 28/28 | 14/14 | 25/25 | 0 | 0 | 100 % |
  | **v2 band (0.25, 0.80), 1.5B** | **27/28** | **13/14** | **25/25** | 1 | 1 | **39/275** |
  | **v2 band (0.25, 0.80), 4B** | **28/28** | **14/14** | **25/25** | 0 | 0 | **39/275** |

  The 1.5B's FPs are trivia about death or medicine ("Chernobyl year", "Titanic deaths", "who discovered penicillin"). Its misses alone are short EN imperative items (nosebleed, earthquake), which v1 catches with confidence, so the band keeps them.
- Background: LLM cascades that call the expensive model only when the cheap one is unsure (FrugalGPT, Chen et al., arXiv 2305.05176, 2023, https://arxiv.org/abs/2305.05176); instruction-following LLMs as zero-shot safety classifiers (Llama Guard, Inan et al., arXiv 2312.06674, 2023, https://arxiv.org/abs/2312.06674); small embedding routers vs LLM routers (Guarded Query Routing, arXiv 2505.14524).
- **Strength: moderate-to-weak for the exact numbers.** Every set here is in-sample for me: the mirror is my own translation, and the band was chosen after seeing these results. My track record so far: v1 in-sample 37/39 → blind 20/24. Expect a similar drop.
Test in boar-eval:
- **Frozen:** `exp/pt-recall/FROZEN.sha256`, combined `305fadbde851f6606e48804a73e94ebfc75c237ad7d9b02db62c969aa90f1cf6`. It covers `detector-v2.json` (rule + per-tier model), `llm-prompt.txt`, the v1 head `health-lr.v1.json` (unchanged), and `llm.mjs` (the reference implementation: node-llama-cpp `LlamaChatSession`, system = prompt file, user = `Message: <q>`, grammar yes|no, temperature 0).
- **Detection-only check first (cheap, as for #4/#4b):** on a **new** blind set (hm-fresh4: ≥ 24 danger with ≥ 12 PT, ≥ 25 hard negatives, ≥ 25 ordinary), run both tiers' LLM.
- **Criterion proposal (coordinator freezes it):**
  - D1: recall ≥ 20/24 overall and ≥ 10/12 PT;
  - D2: hard negatives ≤ 2/25 (v1 had 4/25; the band's upper half exists to catch these), ordinary ≤ 2 %;
  - report the LLM call rate and per-call ms;
  - then D3/D4 as in QUEUE #4 (A1 on the engine, 0 sourced answers lost).
- **Expected outcome, stated before the run** (the rule from the v0 lesson):
  - 4B tier: D1 PASS likely; D2 hard negatives 0–2.
  - 1.5B tier: PT recall 9–11/12; hard negatives 1–3, so it could fail D2.
  - Public sets I can check now: bench public non-danger 0/55 for both tiers. hm-fresh2's outcome on v2 is UNKNOWN to me (never opened).
Cost to try: engine patch ~half a day over v1's A1 patch (one extra grammar-constrained completion on the resident context; llama.rn `completion` with `grammar`, `n_predict: 2`); detection-only check ~10 min on the MacBook; Veil ~2 h for hm-fresh4. No downloads.

## Body

### Why the LLM, and why only in the band
- The LLM is multilingual where bge-small-en is not, and BOAR already pays for it to be in memory at the A1 decision point.
- Calling it on every question would add 0.4–1.1 s desktop (more on the phone) everywhere, and the 1.5B alone misses confident EN items. The band keeps v1's strengths (cheap, EN-confident) and spends the LLM only where v1 is unsure.
- The upper half of the band (0.5–0.8) targets v1's blind failure: 4/25 hard negatives, presumably borderline scores. UNKNOWN: whether those scored above 0.8, in which case the band can't veto them. The coordinator knows v1's blind scores, so they can check this without telling me the items.

### What would make it fail
- **Prompt/model coupling:** the prompt was written for Qwen-family instruction models. A different reader (Gemma 4 E4B, Anvil's QUEUE #2) needs a re-check, so the prompt must be frozen per model.
- **Context interference in the engine:** if the yes/no call shares the KV/sequence with the answer, it must be cleared or run on a separate sequence. Otherwise the classification text leaks into the answer prompt.
- **Latency on device:** if band calls cost > 2 s on iPhone, that's TTFT on a safety path. Mitigation: run it in parallel with retrieval (it only needs the question), or keep the system prompt's KV prefix cached.
- **Hard negatives about death/medicine** (the 1.5B said yes to Titanic/penicillin trivia when asked alone). In the band they reach the LLM only if v1 scores them 0.25–0.8 (Titanic 0.32, penicillin 0.37), so the 1.5B tier can still FP on them. The 4B did not.

### Files
`exp/pt-recall/`: `pt-mirror.jsonl` (my PT translations), `aug.mjs` (+ copies of upstream `ptQuery.ts`, `ptLexicon.ts`), `embed.mjs`, `score.py`, `prototypes.v2pt.json` + `v2pt.py` (rejected PT-prototype variant), `llm.mjs`, `llm-prompt.txt`, `llm.json`, `llm-4b.json`, `cascade.py`, `band.py`, `results.txt`, `detector-v2.json`, `FROZEN.sha256`.
