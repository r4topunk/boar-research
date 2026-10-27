# P3-NLI-0: offline probe of a separate small grounding checker (drop-only), frozen BEFORE any run
Author: Compass, 2026-10-02. Coordinator's brief: a separate small checker for "used-but-wrong" sentences, ≤ ~500 MB extra, ≤ ~2 s per answer on a mid Android, drop-only, never rewrite. Offline probe only.

## Items (reused unchanged from Anvil's frozen P3-0)
- `rnd/research/anvil/exp/p3-selfcheck/protocol.json` (sha256 114851347439…): 7 positives (run, id, target sentence indices) and 20 negatives.
- Answers: `answer.text` from `boar-eval/runs/night-2026-10-01/<run>.traces.jsonl`.
- Sentence split exactly as P3-0: `re.split(r'(?<=[.!?])\s+|\n+')`, stripped, empty removed.
- Passages: the s44 prompt dump `boar-eval/runs/and-qwen-s44/and-qwen-s44.prompts.jsonl`, system message of the same itemId. Exclusion as P3-0: exclude and report an item if the s44 trace's `retrieval.kept` titles differ from the labelled run's.

## Checker (one primary; no swapping after seeing results)
- Model: `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` @b5113eb3, MIT, `onnx/model_quantized.onnx` (339 MB, int8), labels {entailment, neutral, contradiction}. Multilingual (PT included). Runtime: onnxruntime CPU.
- **Why contradiction, not "unsupported":** correct answers here contain correct facts the passages don't state (the 4B's memory). An "unsupported" flag would drop them; Compass measured this in cycle 4 (LLM entailment check: no lift). The target class is "a passage contradicts the sentence".
- Premises: the passage text from the system message, split into numbered sources (the dump's "[n] …" blocks), then into windows of up to 3 consecutive sentences, each ≤ 400 tokens.
- Hypothesis: each answer sentence with [n] markers removed. Sentences shorter than 4 words are skipped.
- **Flag rule (frozen):** a sentence is flagged iff max over windows of P(contradiction) ≥ **0.90** AND, in that same window, P(contradiction) > P(entailment). The high threshold is chosen a priori because NLI models over-call contradiction on topically related but non-equivalent text. Drop-only: flagged sentences would be removed. If > half of an answer's sentences are flagged, the answer is kept unchanged (guard, as P3-0).

## Bar (frozen; coordinator's suggestion)
- **PASS iff positive hits ≥ 4/7** (a hit = at least one target sentence flagged) **AND negative false flags ≤ 2/20** (any sentence flagged in a correct answer).
- With exclusions: hits ≥ ceil(4/7·n_pos), false flags ≤ floor(2/20·n_neg).
- **Reported, not gating:**
  - effective drops after the guard;
  - desktop CPU time per answer (single process, M1);
  - a phone estimate (mDeBERTa-base ~86M backbone params + 190M embedding; int8);
  - a threshold sweep (0.5 / 0.7 / 0.9). The sweep is exploratory and never re-decides the verdict.
- Fail → no small-NLI grounding check from this model. The line stays closed unless a different, pre-registered checker is proposed.
