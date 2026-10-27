# LITE17: can a cheap intervention narrow the 1.7B reading gap with the pack installed?

Criterion `LITE17-criterion.md`, sha256 `453826c0…` (checked with shasum before any generation, not edited). Set: the 150 RELGATE contexts (9 public pack self-tests, X2b engine contexts, prompt D4 as in PACKREAD). Model: Qwen3-1.7B Q4_K_M, llama-server b11010 (`4bc272f`) CPU on the MacBook, :8192, `-t 4`, seed 42, app sampler 0.7/40/0.95/0.05. Judge: Haiku 5.5-low (judge.v1-low), N = 4, both orders, uncapped, 1,028 calls, 0 missing. Paid API: none. No blind/ or veil/ reads.

## TL;DR

| Arm | n (decision set) | Q arm vs B | Δ (paired 95 % CI) | Worst family Δ | Gap closed vs 4B (all 150) | Tokens/item p50 / p90 | Verdict |
|---|---|---|---|---|---|---|---|
| B (thinking off) | 150 | 0.496 (0.470–0.521) | — | — | — | 292 / 365 | baseline |
| T (thinking, budget 256) | 150 | 0.494 vs 0.496 | **−0.002 (−0.023…+0.019)** | reference −0.040 | −2 % | 542 / 613 (×1.9) | **NO** |
| Q (quote, then answer) | 150 | 0.499 vs 0.496 | **+0.002 (−0.018…+0.024)** | outdoors-travel-se −0.006 | +2 % | 407 / 534 (×1.4; pass 1 152 / 200) | **NO** |
| S (drop SE question-only chunks) | 64 | 0.443 vs 0.442 | **+0.001 (−0.028…+0.032)** | crypto-se −0.015 | +1 % | 302 / 379 (S items) | **NO** |
| 4B + D4 (CHAINWHEN OFF, comparator) | 150 | 0.608 (0.577–0.639) | 4B − B = **+0.112 (+0.089…+0.135)** | — | 100 % | — | report only |

- None of the three cheap interventions moves the 1.7B. All deltas are within ±0.003 of zero and every CI sits inside ±0.035. The gap to the 4B stays at 0.11.
- The gap is **not** confined to technical packs at n 150. 4B − 1.7B by pack: firstaid +0.19, outdoors +0.14, ethereum +0.14, health-se +0.13, bitcoin +0.12, medlineplus +0.11, simplewiki +0.10, travel +0.07, factbook +0.06 (CI crosses 0). The exploratory claim from the n 54 PACKREAD slice (~0 on factbook, medlineplus and health-se) does not reproduce. The gap is broad: model capacity, not one pack type.
- Correctness mean (1–5, averaged over both orders): B 2.33, T 2.24, Q 2.48, S 2.29 (on its 64 items: 1.99 vs 2.08), 4B 2.82. Q raises correctness by +0.15, but the ratio does not move. A readout only, no rule.
- Lite-tier conclusion: prompt and context tricks at this cost don't buy back the 4B's reading. The lite line closes for reading levers; only a bigger model closes the gap.

## Per pack family (Δ arm − B, paired CI; families fixed in tools/agg.py before any judgment)

| Family (packs) | n | 4B − B gap | T | Q | S (n) |
|---|---|---|---|---|---|
| crypto-se (bitcoin, ethereum) | 40 | +0.130 (+0.086…+0.175) | −0.000 (−0.043…+0.044) | +0.009 (−0.033…+0.052) | −0.015 (−0.055…+0.026) (33) |
| health (firstaid, medlineplus, health-se) | 36 | +0.136 (+0.090…+0.187) | +0.014 (−0.018…+0.045) | +0.010 (−0.026…+0.044) | +0.000 (−0.055…+0.054) (10) |
| outdoors-travel-se | 36 | +0.104 (+0.062…+0.147) | +0.019 (−0.019…+0.055) | −0.006 (−0.046…+0.040) | +0.028 (−0.021…+0.088) (21) |
| reference (factbook, simplewiki) | 38 | +0.079 (+0.032…+0.128) | −0.040 (−0.089…+0.008) | −0.005 (−0.050…+0.037) | — (0) |

Gap closed by family (arm − B) / (4B − B): T crypto 0 %, health +10 %, outdoors-travel +19 %, reference −50 %; Q +7 / +7 / −6 / −6 %; S −10 / 0 / +16 / n.a. All of these are inside the noise. Per-pack deltas are in `aggregates/lite17.json` (`by_pack`).

## Arm mechanics

- **T:** b11010 caps reasoning per request. The request sends `chat_template_kwargs.enable_thinking=true` plus `thinking_budget_tokens: 256`, which drives the server's reasoning-budget sampler: when the budget runs out it forces the end-of-thinking tag and the model goes on to the answer. The server flag `--reasoning-budget N` does the same thing globally. `--reasoning-format deepseek` puts the thinking in `reasoning_content`, and only `content` is judged. Checked with `/tokenize`: reasoning was 255 tokens on 144/150 items and ≤ 255 on all of them (`data/t-reasoning-tokens.json`), so the budget binds on 96 %. 0 empty answers; 149 stop / 1 length. `max_tokens` = 1024 + 256 + 8, so the answer keeps its 1024.
- **Q:** pass 1 uses the B system message unchanged (D4 + context). The user turn is the question + blank line + the criterion's instruction, verbatim. Thinking off, max 200 tokens. 7/150 pass-1 outputs were NONE and 13 hit the 200 cap. For pass 2, the B user turn gets `\nRelevant quote: <pass-1 output, whitespace collapsed to one line>` appended.
- **S:** the rule applies only to sources in qa-*-se packs (text only, `tools/build.py`). A source is a *document* if its title carries a source label (`Wikivoyage:`, `ethereum.org:`, `Ethereum EIPs/ERCs:`, `Wikipedia:`) or its body opens with a wiki section path (`A > B: …`). Any other source is an SE post. It is *answer text* only when the body opens with `Answers > Answer` (the pack chunker prefixes every answer chunk this way). Every other SE post chunk is question-only and is dropped: either a head chunk `Tags: …` or an unprefixed continuation of the question body, including `Edit:` notes and code. The kept sources are renumbered in order. Drops: 110 chunks on 64 items (bitcoin 27 chunks / 15 items, ethereum 32/18, health-se 20/10, outdoors 9/9, travel 22/12). Two items where every source was question-only keep B (st-qa-bitcoin-se-010, st-qa-outdoors-se-015). Examples:
  - st-qa-bitcoin-se-001 [4] (dropped): "How can I prove that I destroyed some bit coins?\nTags: proof-of-destruction, destroy-bitcoins\n\nIf I wanted to destroy bitcoins, and prove that it was done …"
  - st-qa-bitcoin-se-020 [2] (dropped, unprefixed question continuation): "Why doesn't BTC reward miners for confirmations, too?\nbtc_reward = ZEROS_DISCOVER_REWARD for transaction in confirmations: …"
  - Kept for contrast: "Stablecoin\nLegislation and regulation > Bahrain: …" (wiki section) and "Wikivoyage: France\nGet in > …" (labelled).

## Cost (phone time = tokens ÷ the phone decode rate; the 1.7B phone rate is unmeasured, so tokens are reported)

Generated tokens per item p50 / p90: B 292 / 365, T 542 / 613 (+250, all of it the capped thinking), Q 407 / 534 (pass 1 152 / 200 + pass 2 265 / 360, plus a second prefill of about 950 prompt tokens, partly reusable from the KV), S 302 / 379. MacBook wall time (shared with another session's 4B server, load 16–40) is indicative only; p50 per generation was 10–40 s.

## Deviations

1. **Pack families** are not defined in the criterion. Four families were fixed in `tools/agg.py` before any judgment: health (firstaid, medlineplus, health-se), crypto-se (bitcoin, ethereum), outdoors-travel-se, reference (factbook, simplewiki). Per-pack deltas are also reported. No family reaches −0.05 under any arm, and the verdicts do not depend on this grouping.
2. **B was regenerated** rather than reused from PACKREAD Q17-D4: different machine (MacBook M1 vs mini) and 150 items vs 54. On the 54 shared ids, B is 0.523 vs PACKREAD Q17-D4 0.529, Δ −0.006 (−0.040…+0.026): consistent.
3. **Judge bench** = `boar-eval/bench/slices/chainwhen-v1`: the same 150 ids, with questions and refs copied verbatim from bench/selftest/<pack>. No new slice was built.
4. **Server context** `-c 6144` (PACKREAD used 4096) so T fits prompt + 256 + 1024. This does not change outputs.
5. **S on unchanged items** = B (same answer and judgment) by construction. The S decision set is the 64 changed items, as the criterion specifies. The two all-question-only items kept as B are counted as unchanged.
6. The T reasoning-token check needed a brief server restart, `/tokenize` only. Generation had already finished.

## Files

`tools/` (serve.sh, build.py, gen.py, to_traces.py, judge.sh, agg.py), `data/` (prompts.jsonl, s-drops.json, ids, t-reasoning-tokens.json), `answers/answers-Q17.jsonl` (664 rows: B/T/Q1/Q2 150 each, S 64; T rows keep `reasoning`), `traces/lite17-{B,T,Q,S}`, `judgments/lite17-{B,T,Q,S}.judgments.jsonl`, `aggregates/lite17.json`. The comparator is read from `../chainwhen/judgments/chainwhen-OFF.judgments.jsonl` (150/150, Haiku judge.v1-low). Server stopped.
