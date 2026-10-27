# LITE17 criterion (frozen 2026-10-19 23:1x before any generation)

Question: where does Qwen3-1.7B lose to the 4B when the right pack is installed, and does a cheap intervention narrow the gap?
Exploratory basis (0 LLM, PACKREAD 54, D4): gap 4B - 1.7B is ~0.11 at every source position (fact@1 0.108, elsewhere 0.110, no-fact 0.154) and ~0 on factbook / medlineplus / qa-health-se but 0.16-0.25 on technical packs (ethereum-se 0.251, outdoors-se 0.21, bitcoin-se 0.187): background knowledge, not position.

Set: the 150 RELGATE contexts (arms/relgate/data/contexts.jsonl; public pack self-tests, X2b prompts). No blind/ or veil/ reads.
Model: Qwen3-1.7B Q4_K_M (shared-models/lite), llama-server b11010 CPU on the MacBook, port 8192 (never touch :8094), seed 42, max_tokens 1024 for the answer.
Arms (all with prompt D4 exactly as PACKREAD):
- B (baseline): thinking off (enable_thinking=false).
- T: thinking on, reasoning budget 256 tokens (cap by max reasoning tokens; if the server cannot cap, stop thinking at 256 tokens and force the answer; record how).
- Q: two passes. Pass 1: "Quote the sentence(s) from the sources that answer the question, with their source number, or write NONE." (max 200 tokens). Pass 2: the normal D4 answer prompt with one appended line "Relevant quote: <pass-1 output>".
- S: deterministic filter: drop Stack Exchange source chunks that are the question post only (no answer text), renumber; identical to B for non-SE packs and where nothing is dropped.
Comparator (report only): CHAINWHEN OFF arm = 4B + D4 on the same 150 contexts.
Judge: Haiku 5.5-low judge.v1-low N=4 both orders uncapped; score = PACKREAD agg (ratio Q, bootstrap B 2000).
Decision per arm vs B (paired over items where the arm differs from B):
- CANDIDATE: delta >= +0.03 and paired 95 % CI low > 0, and no pack family with delta <= -0.05.
- Also report: gap closed vs the 4B (fraction of 4B-B), by pack family, generated tokens per item p50/p90 (phone time = tokens / measured phone decode rate; 1.7B phone rate unmeasured -> report tokens), correctness mean.
- NO otherwise.
