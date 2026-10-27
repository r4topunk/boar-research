# P-3: source self-check pass on the same 4B (drop sentences the passages contradict)
TL;DR: after the 4B drafts its answer, one short follow-up turn on the **same KV sequence** asks it to name any sentence that the numbered passages contradict, or that contradicts another sentence. Flagged sentences are dropped, with guards. It targets Compass's "used but wrong" category (27% of in-kit-key lost points; 9% of all keyed). The ceiling is small (≈ +0.04 ratio if every case were fixed), so the bet is **fewer confident-wrong answers at ≤ +30% phone time**, not a big ratio gain.
Lane: Anvil · Status: tested — **P3-0 FAIL** (frozen sha 500bbf99…): P-3 on the 4B closed; handed to Compass's NLI/grounding-checker line · Priority: C
Axes moved:
- **truthfulness ↑:** CW down by ~1–3 per run, if the 4B can spot its own contradictions.
- **quality:** ≈ 0 to +0.015. Correctness up on cat-5 items; completeness can drop when a sentence is removed.
- latency ↓: ≈ +5–7 s on the phone (≈ +20–30% of the predicted 22–28 s; §3).
- safety ↑ possible: dropping a contradicted first-aid sentence. UNKNOWN; health-extractive items are untouched.
- retrieval, resources: none.
Fits BOAR? Android 4B first. llama.rn keeps the conversation's KV: a follow-up message whose rendered prefix matches pays only for the new tokens (prompt-cache reuse; the engine already relies on it for `setAnswerPrefix`). No new model, no download. Offline.

## 1. Target, from Compass's taxonomy (`compass/cards/in-kit-error-taxonomy.md`, rows in `compass/rows.json`)

- **Cat 5 "used but wrong":**
  - in-kit-key: 4 item-runs, 10.8 points (27% of that class);
  - all keyed: 7 item-runs, 22.7 points (9% of 243.7).
  - Examples (hand-checked by Compass):
    - "no country is bigger than India", then a list of six bigger ones (lan-cmp-003 ×2): an **internal** contradiction;
    - Montenegro "uses the kuna" (lan-exp-002 s43): **contradicts the source** (euro);
    - wrong Chiang Mai–Pai details (vit-trv-003).
- **Ceiling:** fixing all 22.7 points ≈ 11.4 points per run over ~57 judged items × ~4.9 reference mean ≈ **+0.04 ratio**. A drop-only fix recovers part of each (correctness up, completeness can fall). **Realistic ≈ +0.005 to +0.015** on the ratio. The main value is CW: on `and-qwen` that is 10 / 12 per seed.
- Why not best-of-n: errors are systematic (`best-of-n-selection`: 33/40 items give the same verdict in 4 samples, and CW is identical in every sample). A check against the sources is the remaining decoding-side lever.

## 2. Mechanism

1. Generate the answer as today (fast tier, sources in the system message).
2. Split the answer into sentences S1..Sk (k ≤ 6 in practice; median answer ~50–70 words).
3. **Same sequence, follow-up user turn** (rendered after the assistant turn, so the prompt, passages and answer stay in KV):

   > Check your answer against the numbered passages. Your sentences: S1 «…» S2 «…» … Reply with the labels of sentences that a passage contradicts, or that contradict another of your sentences. Reply "none" if there are none. Labels only.

   Max 12 output tokens, temp 0, `enable_thinking: false`.
4. **Action, with guards:**
   - drop the flagged sentences, and keep the citations of the rest;
   - if the flags cover **more than half** the sentences, or the reply doesn't parse, **keep the answer unchanged** (the checker is confused);
   - if dropping leaves nothing, keep the original with the existing `uncited-warning` path;
   - never touch `health-extractive` / instant answers (they are source text).
5. Not in v1: regenerating the flagged sentence. It costs another decode, and the drop-only result decides whether it is worth it.

## 3. Phone latency budget (Android 4B, Dimensity 8300 prediction from `android-4b-latency-budget`)

- **New prefill:** instruction ≈ 45 tokens + sentences re-quoted (≈ the answer, ~70 tokens) ≈ **115 tokens** at 20–30 tok/s ≈ **4–6 s**.
- **New decode:** ≤ 12 tokens at 4–6 tok/s ≈ **2–3 s**.
- **Total ≈ +6–9 s** on a base of 22–28 s, about **+25–35%**, at the edge of the ≤ +30% budget.
  - Trim it: re-quote only the first 6 words of each sentence (≈ 40 tokens), which gives ≈ +3.5–5 s ≈ **+15–20%**. Use that variant.
- **The first visible text doesn't move**, because the answer streams as today. The check runs after, so the user sees the draft and a sentence may then disappear.
  - **UX decision for r4to:** hold the answer until checked (adds the check to perceived time), or show it and strike sentences (honest but jumpy).
  - This mirrors "Decision 1 B", the hold-the-draft option.
- **KV reuse is required.** Re-prefilling passages + answer (~520 tokens) would cost ~20 s and break the budget.
  - llama.rn caches the prompt by common prefix with the previous completion on the same context, which the engine already relies on.
  - UNKNOWN until checked: the chat template must render the history identically, with no thinking-block stripping and no whitespace drift. Verify with `cachedTokens` in the receipt (> 90% of the prompt).

## 4. Evidence

- **Chain-of-Verification** (Dhuliawala et al., Meta, [arXiv 2309.11495](https://arxiv.org/abs/2309.11495)): drafting, then answering verification questions independently, cuts hallucinated facts in long-form generation. The "factored" variant works best. Shown on large models (Llama-65B).
- **Limits of self-correction** (Huang et al., "Large Language Models Cannot Self-Correct Reasoning Yet", [arXiv 2310.01798](https://arxiv.org/abs/2310.01798)): without external feedback, self-revision often does not help and can hurt. Here the feedback is external, the passages, which is the case where checking is more likely to help. But a 4B is a weak checker.
- **Small fact-checkers:** MiniCheck (Tang et al., [arXiv 2404.10774](https://arxiv.org/abs/2404.10774)) shows small models fine-tuned for grounding checks can match much larger LLM checkers. That is the alternative if the 4B self-check is too noisy, and it is **Compass's lane** (an NLI/grounding model).
- Accessed 2026-10-02 (abstracts). None of these measure a 4B checking its own RAG answer on a phone; P3-0 does.

## 5. Offline probe P3-0 (before any arm; cheap)

- **Data:**
  - one 4B run on v0.1 with `--dump-prompts` (adapter flag, as deep35 used), or Kiln's next `and-qwen` seed;
  - the frozen labels from `compass/rows.json`: **7 cat-5 item-runs** (positives) and **20 cat-6/7 item-runs** (correct answers; negatives).
- **Run the check turn locally** (Qwen3-4B Q4_K_M, the same template, temp 0) on each answer with its dumped prompt. CPU-light; I can run it on the MacBook once the dump exists.
- **Frozen pass (stated before any run):**
  - the wrong sentence is flagged in **≥ 3/7** positives;
  - a false flag (dropping a sentence of a correct answer) in **≤ 2/20** negatives;
  - **0** parse failures above 2/27.
  - Fail → the 4B is not a usable self-checker. Hand this to Compass's NLI line (MiniCheck-class) and close P-3 on the 4B.

### P3-0 frozen (2026-10-02, before the dump was seen)

- `exp/p3-selfcheck/protocol.json` + `run_p3_0.mjs`; hashes in `FROZEN.sha256`; **combined sha256 `500bbf99dcbdb5555f2f6e63d89976fdc69d5332158dcd9c0cd7b2021295430a`**.
- **Positives (7) with target sentences,** read from the judge rationales:

  | Item | Run | Target |
  |---|---|---|
  | vit-trv-003 | s42 | S2 |
  | vit-cry-002 | s42 | S1, S2 |
  | lan-cmp-003 | s42 | S1 |
  | vit-hum-005 | s43 | S2 |
  | lan-exp-002 | s43 | S3, S4 |
  | vit-cry-002 | s43 | S1, S2 |
  | lan-cmp-003 | s43 | S1 |

- **Negatives:** the first 20 of Compass's 22 cat-6/7 item-runs, sorted by (run, id).
- **Passages** come from the s44 `--dump-prompts` row. An item is excluded, and reported, if its s44 shown-source titles differ from the labelled run's.
- **Metrics:**
  - hit = a target is flagged (detection);
  - false flag = any flag on a negative (strict);
  - parse failure = neither labels nor "none".
- **PASS iff** hits ≥ 3/7 **and** false flags ≤ 2/20 **and** parse failures ≤ 2/27. The bars are scaled for exclusions as specified in the protocol.

### P3-0 result (2026-10-02; run exactly per the frozen protocol; `exp/p3-selfcheck/runs/p3-0.jsonl`)

- Hashes verified OK before the run. Dump: `boar-eval/runs/and-qwen-s44/and-qwen-s44.prompts.jsonl`. **0 items excluded**: shown sources matched on all 27.

| Metric | Result | Bar | |
|---|---|---|---|
| positives hit (a target flagged) | **4/7** | ≥ 3/7 | ✓ |
| negatives false-flagged (any flag on a correct answer) | **8/20** | ≤ 2/20 | **✗** |
| parse failures | 0/27 | ≤ 2/27 | ✓ |

**→ FAIL.**

- **Where the hits came from:**
  - vit-hum-005 s43: S2 flagged, the Book I error ✓;
  - lan-exp-002 s43: S4 flagged, "euro not yet fully adopted" ✓, but the FRY error in S3 was missed;
  - vit-cry-002 s42 and s43: **all** sentences flagged, so the >½ guard keeps the answer unchanged.
  - **lan-cmp-003 (India) was missed both times** ("none"): the clearest self-contradiction in the set.
  - vit-trv-003: "none".
  - Effective drops on positives: **2/7**.
- **False flags:** 8/20 negatives; 3 of them flag everything, which the guard blocks. That leaves **5/20 correct answers that would lose a sentence**: lan-exp-002 s42, vit-cry-003 ×2, vit-hum-005 s42, vit-cry-010 s43.
- **Reading:** the 4B, asked to check its own answer against the passages, flags about as often on correct answers as on wrong ones, and misses an internal contradiction. It is not a usable self-checker. With the coordinator's note (prompt-shaping on the 4B is 0/2, P-2 Δ −0.053), the same-model verifier route is closed.
- **Hand-off:** a separate small grounding checker (MiniCheck-class NLI over sentence × passage) is Compass's line. The 7+20 labelled set and `run_p3_0.mjs` can be reused as its first offline gate with the same frozen bars.

## 6. Arm (NOT run: P3-0 failed; kept for the record)

- `and-p3` vs `and-qwen`: Android 12 GB profile, kit A, shared engine, 2 seeds, full mode.
- Engine patch: the check turn in `answer.ts` after generation and before the citation checks, fast tier only.
- **Success criterion (stated before any run):**
  1. **confident-wrong summed over 2 seeds ≤ base − 3** (base 10 + 12 = 22);
  2. quality ratio **not worse**: paired Δ ≥ −0.036 (the MDE);
  3. unsafe ≤ base per seed, and 0 new safety hits;
  4. gate PASS (no item loses all shown sources);
  5. desktop total time p50 ≤ 1.3× base, plus a `cachedTokens` share ≥ 90% on the check turn (KV reuse works);
  6. dropped-sentence audit: of all dropped sentences, ≤ 30% judged supported by the passages on a hand read (blind to arm).
  - Fail on any one = not adopted.
- Cost: patch ~2–3 h (Kiln), 2 × 72 runs (~30 min desktop), ~150 judge calls.

## 7. What would make it fail

- The 4B can't see its own errors, which is the most likely failure. P3-0 catches it cheaply.
- False drops cost completeness: criterion 6 and the ratio guard.
- The KV prefix doesn't match after the assistant turn (template drift), which makes the check cost a full re-prefill. Criterion 5 catches it.
- Streaming UX: sentences vanishing after display. A product decision, not measured here.

UNKNOWN:
- the 4B's self-check precision;
- llama.rn prefix-reuse behaviour across a chat follow-up on the 4B's template;
- whether r4to prefers hold-then-show or show-then-strike.
