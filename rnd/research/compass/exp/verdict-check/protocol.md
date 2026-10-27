# V-0: offline gate for a verdict-consistency check on the Android 4B (frozen before any run)
Author: Compass, 2026-10-02. Idea: on verdict-shaped questions only (`shape.py`: yes/no or binary comparison), the 4B sometimes opens with a verdict its own next sentences contradict ("No, astronauts did not walk on the Moon before 1970. The first moonwalk occurred in 1969"). A short check turn asks the same 4B whether a later sentence contradicts sentence 1. If YES, **drop sentence 1** (drop-only, never rewrite; never drop if the answer has < 2 sentences).
Not a prompt-shaping arm: the answer prompt is unchanged. It's a post-generation check, like P-3 but narrower (internal consistency, not passage grounding).

## Set (labels frozen in `labels.json`, written before any run)
- 30 answers: the 10 verdict-shaped v0.1 items × and-qwen s42/s43/s44 (answer.text from the traces).
- **Positives 9** (3 items × 3 seeds); **negatives 21**.
- Caveat: the positives cluster in 3 items, and the shape regex and labels are in-sample.

## Check (frozen)
- Model: Qwen3-4B-Instruct-2507 Q4_K_M (`shared-models/`), node-llama-cpp from boar-app's node_modules; temp 0, maxTokens 4, fresh context per answer (no same-KV reuse; dumps exist only for s44).
- Preprocess: remove the app's memory-label prefix ("This answer is not from an offline source on this phone; check it before relying on it.") and `[n]` markers. Split with P3-0's split; S1..Sk.
- System: "You check answers for internal consistency."
- User: "Question: {question}\n\nAnswer:\n{S1: …\nS2: …}\n\nDoes any later sentence contradict what S1 says? Reply with exactly YES or NO."
- Parse: first token YES/NO (case-insensitive); anything else = parse failure (counted as NO, reported).

## Bar (frozen)
- **PASS iff flags on positives ≥ 7/9 AND false flags on negatives ≤ 1/21 AND parse failures ≤ 2/30.**
- Reported: per-item hits; check latency on the M1 (prefill + 4 tokens); answers with < 2 sentences (never dropped).
- **Fail → no verdict check from the 4B. PASS → a card for a seeded arm** (whole-bench, all three seeds; verdict-shaped items only; criterion stated then).
