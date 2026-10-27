# RELGATE criterion (frozen 2026-10-19, before any classifier run)

Question: can Qwen3-4B-Instruct-2507 (Q4_K_M, the 8 GB phone's main model) work as an in-harness relevance / sufficiency classifier chained before the main answer, measured against GROUND TRUTH (verified in-pack fact quotes), not against another model?
Public data only (bench/selftest/* items + their X2b prompt dumps + safepack oracle passages). Never blind/ or rnd/veil/. 0 judge calls, 0 paid API.

## Sets (built by tools/build_sets.py, deterministic)
- Source: arms/headpass-st/gen-x2b/st-<pack>-cut7-headpassx2b-s42.prompts.jsonl (9 packs, cut 7 + X2b engine prompts), matched to bench/selftest/<pack>/questions.jsonl by exact question text. Prompts without a "Context:" block are excluded (reported).
- Chunk set C: the "Context:" block of the system message split into numbered sources [1], [2], ... (title line + body). POSITIVE iff any selftest.in_pack_facts[].quote of the item appears in the chunk: (a) normalised substring (lowercase, unicode quotes/dashes folded, whitespace collapsed); or (b) fuzzy: quote has >= 8 tokens and >= 80 % of its word tokens (multiset) occur in the chunk. Count of labels that needed (b) is reported.
- Context set K: one row per item; POSITIVE iff any chunk of its context is POSITIVE. Secondary label K_all: every in_pack_fact quote is found in the context (reported, no rule).
- Primary scope = all matched items (~150); the packread-v1 54 ids (arms/packread/ids-54.ids) are reported as a subset, no rule.
- Safety set S: 30 items of bench/selftest/safepack/questions.jsonl; positive = the item's oracle passage (arms/safepack/oracle-ctx.json); negative = the oracle passage of a different item with a different title (deterministic: next item in file order whose title differs). 30 pos + 30 neg.
- Split: half A iff int(sha256(item_id)[:8], 16) % 2 == 0, else half B (chunks follow their item). Thresholds and wording choices are tuned on A only; every rule is read on B.

## Classifiers (temperature-free next-token probabilities, llama-server /completion, n_predict 1, n_probs 100, raw ChatML prompt, cache_prompt true)
- Models: M4 = Qwen3-4B-Instruct-2507-Q4_K_M (primary); Q17 = Qwen3-1.7B-Q4_K_M, thinking off (empty `<think>\n\n</think>\n\n` after the assistant tag), comparison only.
- Score p = P(yes) / (P(yes) + P(no)), summing all single-token variants of yes/no (yes, Yes, YES, " yes", " Yes"; same for no) that appear in the top-100; a variant absent from the top-100 counts 0; if both sums are 0, p = 0.5 (counted and reported). Label tokenisation is printed by tools/tokcheck.
- G1 per-chunk (prompt: system "You check whether a passage contains information needed to answer a question." / user "Question: <q>\n\nPassage:\n<chunk incl. title line>\n\n<wording>"), three wordings sharing the question+passage prefix:
  - W1 bare: "Does this passage contain the specific fact needed to answer the question? Reply yes or no."
  - W2 criteria (jev-style): "Does this passage contain the specific fact needed to answer the question?\n- yes: the passage states the concrete fact, figure, name, step or mechanism the question asks for\n- no: the passage is about something else, only touches the topic in general terms, or lacks that specific content\nReply yes or no."
  - W3 definition: "A specific fact means the concrete value, name, date, step or explanation the question asks for, not just the topic. Does this passage contain the specific fact needed to answer the question? Reply yes or no."
  The G1 wording carried to the rules is the one with the highest AUC on half A (per model).
- G2 context sufficiency, shared prefix: the exact engine prompt from the dump (system with context + user turn with question and style line), then `<|im_end|>\n<|im_start|>user\nBefore answering: does the context above contain the answer to my question? Reply yes or no.<|im_end|>\n<|im_start|>assistant\n`. The main-answer prefix (up to the end of the first user turn's text) is evaluated first, so the timed G2 call carries only the extra tokens.
- G3 source selection, same shared prefix, appended user line "Before answering: which source number above contains the answer to my question? Reply with one number, or 0 if none." Read P over the single-digit tokens 0..9 (renormalised over digits). G3 pick = argmax over 1..N (N = number of sources); G3 none-score = P(0).
- Safety: G1 (selected wording) on S passages; G2 on an engine-shaped prompt (dump system prompt of a firstaid item with its context replaced by "[1] <title>\n<passage>") + the S question.
- Baseline for G1/G3: retrieval rank (score = 1/rank of the chunk within its context; G3 baseline = always source [1]).

## Metrics (on half B unless stated)
- AUC (Mann-Whitney, ties 0.5) with 95 % CI by item-cluster bootstrap (2,000 resamples, seed 31); precision / recall / F1 at the threshold that maximises F1 on half A; calibration bins [0,.1) [.1,.3) [.3,.5) [.5,.7) [.7,.9) [.9,1] with n and positive rate (all items); share of outputs in the end bins.
- Latency: prompt tokens and server prompt_ms / predicted_ms on the host CPU (named in the report); phone estimate = extra prompt tokens / 47.6 tok/s (4B phone prefill, LITE6 record) + 1 decode step. For G1 every chunk prompt is new tokens (no sharing with the main prompt).

## Decision rules (per model; M4 decides, Q17 is reported against the same bars)
- G1 PASS iff B-AUC >= 0.85 AND B-F1 (at the A threshold) >= 0.70 AND B-AUC >= rank-baseline B-AUC + 0.05.
- G2 PASS (usable as an abstain / re-search trigger) iff B-AUC >= 0.80 AND, at the threshold t* = the largest t on half A that keeps recall of K-positives >= 0.90 (positive = P(yes) >= t), half B shows K-positive recall >= 0.85 AND K-negative catch rate (P(yes) < t*) >= 0.40.
- G3 PASS iff on half-B K-positive items the argmax source is a positive chunk on >= 0.70 AND that rate beats the always-[1] baseline by >= 0.10.
- SAFETY clause (needed before any engine use of G1 or G2): on S, AUC >= 0.90 and at most 1 of 30 oracle positives falls below the gate's threshold (G1 at its A threshold; G2 at t*). A gate that passes its own rule but fails SAFETY is "PASS, health/danger path excluded".
- Q17 "substitutes" iff its B-AUC on the gate is within 0.03 of M4's.
- Label-noise audit (reported, does not change a verdict): the 20 highest-p half-B negatives for the selected G1 wording (M4) are read by the agent and marked "actually answers / partial / no".
- Verdict words: PASS / FAIL per gate; overall "BUILD G<x>" only for passing gates.
