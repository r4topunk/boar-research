# TIME-SPLIT: Pixel 8a bench answer time per tier, retrieval / prefill / decode (WEB 26.2, 0 LLM, no phone, 2026-10-21)

Source: handoff/pixel8-2026-10-20/bench/results/*/rows.jsonl, rows with tokensGenerated > 0 and receipt.prefillMs present (LLM-answered, warmup excluded). Seconds, p50 / p90. retrieval = receipt.retrievalMs; prefill = receipt.prefillMs; decode = totalLatencyMs - ttftMs; load = receipt.loadMs (0 at p50/p90 everywhere, model already loaded). Prompt tokens = ctxTokens (uncached) and ctx + cachedTokens.

| run (model, packs) | n | retrieval | prefill | decode | total | prompt tok p50 (ctx / +cached) | gen tok p50 | decode tok/s p50 | mean share ret/pre/dec |
|---|---|---|---|---|---|---|---|---|---|
| q17b73-a (Qwen3-1.7B, claim kit) | 34 | 1.5 / 2.6 | 3.8 / 6.0 | 4.0 / 6.4 | 9.7 / 13.4 | 276 / 840 | 50 | 12.4 | 16 / 38 / 44 % |
| aunion73-a (Qwen3-1.7B, A-union) | 34 | 4.2 / 5.4 | 3.8 / 6.3 | 4.1 / 6.8 | 12.4 / 17.2 | 250 / 794 | 48 | 11.3 | 31 / 31 / 36 % |
| gemma73-a (Gemma 4 E2B, kit) | 42 | 1.9 / 3.4 | 6.9 / 11.8 | 7.0 / 11.3 | 16.7 / 25.0 | 236 / 774 | 50 | 7.0 | 11 / 41 / 45 % |
| gemmaa73-a (Gemma 4 E2B, A-union) | 42 | 4.9 / 6.3 | 5.9 / 12.2 | 6.7 / 11.1 | 17.0 / 27.9 | 219 / 736 | 56 | 7.2 | 24 / 34 / 41 % |
| q4ba73-a (Qwen3-4B-Instruct, A-union) | 42 | 4.4 / 5.6 | 8.2 / 16.8 | 13.3 / 18.1 | 27.3 / 41.2 | 230 / 748 | 71 | 5.2 | 14 / 31 / 48 % |

(Model/pack labels inferred from run names, configId and retrieval time; the leftover share, up to ~5 %, is time before retrieval and between stages.)

Ranking on the bench engine: decode is first by mean share in all five tiers (36-48 %), prefill second (31-41 %) except 1.7B A-union where retrieval ties it (31 %); at p50 of the 1.7B A-union row retrieval (4.2 s) edges decode (4.1 s) and prefill (3.8 s). Prefill is not small: 230-280 uncached prompt tokens cost 3.8-8.2 s (about 45-65 tok/s), so shortening the prompt and capping the answer are of similar size (each ~1 s per ~25-50 tokens); the model side (decode + prefill) is 65-85 % of answer time.

Caveat: this is the BOAR Bench (JS, llama.rn) engine. Retrieval here is the JS pack search (1.5-4.9 s p50), not the native app's: NATIVE-PARTIME measured native retrieval at 1-2 % of answer time (retrievalMs p50 0.28-0.56 s), so on the submission app the split is retrieval ~0, prefill + decode ~all. The native app's prefill/decode split on the Pixel is unmeasured (NATIVE-PARTIME gives only retrieval vs total); do not transfer the shares above to it.
