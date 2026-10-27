# QUANT17: Qwen3-1.7B Q4_K_M is NOT numerically adequate vs BF16 by the frozen rule (top-1 91.2 % < 95 %, KLD 0.148 > 0.05); Q8_0 is (97.2 %, 0.0068). Queue a gate-v2 K0 screen of Q8_0 (2026-10-20, mini, 0 judge, 0 paid)

Criterion `QUANT17-criterion.md` sha ea483229eeff7075261678c0262755ffe795e833758a731b34bb84c1d71d3f40 (frozen before any measurement).

## Inputs
- 30 first prompts of arms/gate17/traces/gate17dump-K0-main-s42.prompts.jsonl (K0 MAIN, the 1.7B's exact messages), rendered ChatML with the empty think block (--reasoning off). Check: server prompt_n 275/291/298 for items 0-2 = the trace's promptTokens (275 for item 0). The app's "Not found in this phone's offline library" label is added after generation, so there is no model-side prefix.
- unsloth/Qwen3-1.7B-GGUF @ d7f544eead698dbd1f15126ef60b45a1e1933222: Q4_K_M sha b139949c5bd74937ad8ed8c8cf3d9ffb1e99c866c823204dc42c0d91fa181897 (the lite file); Q8_0 sha 0becaa825564295d82e9af4d008bca5f8b7f5f73bf1c6a0b58f7c53ef26b47fd; BF16 sha 3412cc86f04dd7b49cb5fe05249690a95d643ee0f1f980cd5e777a8f40eb37f9 (3.45 GB, deleted after the test). Full list: models.SHA256.
- llama.cpp b11010 CPU (engine build), 4 threads, slot gen2, free disk 30 GiB.
- Deviation from the criterion text: none in the rule; tools/kld3.cpp is a custom libllama tool (needed because llama-perplexity scores the second half of each chunk, prompt tail + answer mixed). Sanity: Q8 vs BF16 KLD 0.007 is the expected magnitude, so the tool is not broken.

## A. Teacher-forced KLD vs BF16, answer tokens only (+ `<|im_end|>`)
| text set | model | tokens | mean KLD (+- s.e.) | top-token agreement | mean delta-p |
|---|---|---|---|---|---|
| primary (Q4 greedy answers) | Q4_K_M | 1370 | **0.1484 +- 0.0129** | **91.17 %** | +3.38 % |
| primary | Q8_0 | 1370 | 0.0068 +- 0.0006 | 97.23 % | -0.17 % |
| secondary (Q8 greedy answers) | Q4_K_M | 1433 | 0.1795 +- 0.0194 | 90.65 % | -4.48 % |
| secondary | Q8_0 | 1433 | 0.0063 +- 0.0006 | 97.70 % | -0.09 % |
Q4 is 22x (primary) / 29x (secondary) further from BF16 than Q8 in KLD, and the two text sets agree, so the verdict is not an artefact of scoring on Q4's own text. Per-token rows: kld-q4.tsv (primary), kld-q8.tsv (secondary); logs kld-q*.log.

## B. Greedy generations, 30 prompts (temperature 0, seed 42, n_predict 512, no judge)
- Text differs Q4 vs Q8: **27 / 30** items (3 identical). All stop on EOS.
- First divergence at token position: median 7, min 0 (1 item differs from the first token), max 41; so by token 7 most answers have forked.
- Length: Q4 mean 45.7 tokens, Q8 47.8; |length difference| among the 27 differing: mean 7.7, max 26 tokens. After the fork the tails are not shared (mean 34.5 Q4 tokens beyond the common prefix per differing item).
- Caveat: greedy forks amplify any tiny logit change, so 27/30 is expected for even a 97 %-agreement pair; the KLD/top-1 numbers are the evidence, this is descriptive. gen-Q4_K_M.jsonl, gen-Q8_0.jsonl hold text + token ids.

## Verdict
**Rule: Q4_K_M top-1 91.17 % < 95 % and KLD 0.148 > 0.05 -> Q4 NOT shown adequate -> queue a gate-v2 K0 screen of Q8_0 (not run here).** This contradicts the comfortable reading of QUANTLITE (Q8 - Q4 = -0.003 on n 20 selftests, Haiku): that test had power only for a gain >= 0.02 on 20 items, while the numerical gap is real and large for a 1.7B at 4 bits. Numerical distance is not quality distance; the screen decides. Phone cost to weigh: Q8 file 1.83 GB vs 1.11 GB, mini decode 0.68x, RSS 1.40x (QUANTLITE).
Caveats: 30 prompts, 1370/1433 tokens, one revision (unsloth Q4_K_M, check whether it carries an imatrix: not inspected), CPU b11010 only, short answers (mean 46 tokens), K0 (no-source) prompts only; no quality claim.

## Files
QUANT17-criterion.md(+.sha256), QUANT17.md, models.SHA256, STATUS, gen-*.jsonl, kld-q4.tsv/kld-q8.tsv/*.log, items/ (30 rendered prompts + ids), tools/{kld3.cpp, mkitems.py, gen.py, mkanswers.py, run.sh}. Mini: Q8_0 kept in <runner>/kiln/quant17/models for the queued screen, BF16 deleted, free 30 GiB, slot released, no servers left.
