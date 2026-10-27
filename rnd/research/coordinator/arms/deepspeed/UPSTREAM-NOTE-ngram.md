# bmoe v0.28.0: `--ngram` output is not token-identical to plain greedy decode

## Summary
The `--ngram` help text says "Greedy verification makes the output token-identical to plain decode". On v0.28.0 it is not: with greedy sampling, 8 of 10 prompts produce different text with `--ngram` than without it, diverging after 34 to 353 characters. `--ngram` was also slower (7.36 vs 8.69 tok/s median), because only 70 of 210 drafts were accepted.

## Environment
- bmoe v0.28.0, commit 374f562c920e2209b093f3349dad8ecbae439956 (the binary prints `engine=0.27.0`)
- llama.cpp fork submodule pin dce9698510b76746db625b644ef2af899517d0ad
- macOS arm64, Apple M4, 16 GB; host CPU-only build: `-DCMAKE_BUILD_TYPE=Release -DBMOE_BUILD_TESTS=OFF -DGGML_NATIVE=OFF -DGGML_OPENMP=OFF -DLLAMA_CURL=OFF -DGGML_METAL=OFF -DGGML_BLAS=OFF`
- Model: Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf, sha256 96b9c0af5c77a4ecaabe3983175112b5ece763261c1ece12b2494b692a70dad7
- Base flags: `-n 128 -c 4096 -t 4 --ubatch 512 --moe-stream --overlap --dense-weights anon --cache-mb 1500 --io-threads 4`, greedy (no `--temp`; the metrics header shows temp=0)

## Steps to reproduce
Use any chat prompt of about 600 tokens (ours were 667 tokens). Ours were rendered with the model's jinja chat template and passed raw with `-p` (no `--chatml`, no `--no-think`). Each run is a fresh process.
```
K0: bmoe-cli -m <model.gguf> -p "$(cat prompt.txt)" -n 128 -c 4096 -t 4 --ubatch 512 --moe-stream --overlap --dense-weights anon --cache-mb 1500 --io-threads 4 --csv k0.csv
K1: same command plus --ngram
```
Also run K2 (`--ngram --draft 6`) and K4 (`--ngram --prefetch 2`). The K1 metrics header shows `spec=ngram spec_draft_max=3 ngram_min_match=3`; K0 shows `spec=off`.

## Observed
Generated text is stdout minus the echoed prompt, cut at the `generation:` trailer.
- K1 text equals K0 on 2/10 prompts (07 and 08, the two with the fewest drafts). It differs on the other 8. First differing character index vs K0: 353, 125, 178, 96, 34, 88, 237, 90 (prompts 00, 01, 02, 03, 04, 05, 06, 09).
- Prompt 04, index 34 (K0, then K1):
  - `The Berlin Wall was built in 1961 [2]. It came down in 1989, following the`
  - `The Berlin Wall was built in 1961 and came down in 1989 [2]. It served as `
- Prompt 01, index 125 (K0, then K1):
  - `ak ECDSA today, meaning funds are safe from immediate quantum attacks [2]. In th`
  - `ak ECDSA today, meaning funds are safe for now [2]. In the future, the network p`
- K1, K2 (`--draft 6`) and K4 (`--ngram --prefetch 2`) texts are byte-identical to each other on 10/10 prompts, although the draft width differs (3 vs 6). Draft width and prefetch do not change the text. The shift from K0 therefore looks like it comes from the batched verify decode itself rather than from accepted drafts. We did not test this. On prompt 05 only one decode step drafted anything, and the text still diverged.
- Draft stats (10 prompts, sums): K1 70/210 accepted (33.3 %), K2 79/366 (21.6 %). On prompt 04, K1 accepted 7 of 33 drafts (`mtp_drafted=33 mtp_accepted=7`).
- Speed (medians): decode 8.69 tok/s (K0), 7.36 (K1), 5.89 (K2), 6.96 (K4); prefill about 21 s in all configs.

## Expected
With greedy verification, K1 output should be byte-identical to K0 on every prompt, with only the speed changing.

## Side observation
`--prefetch 2` alone (K3) gave text identical to K0 on 10/10 prompts. It ran at 0.94x K0 decode speed (8.18 vs 8.69 tok/s median) with the same memory footprint, so no gain on this setup (SSD-backed, desktop).

## Caveats
One machine, one model and quant, 10 prompts, one run per cell. Raw outputs (`<workdir>/arms/deepspeed/raw/`) and the per-item table (`<workdir>/arms/deepspeed/items.csv`) are available on request. We have not checked whether another CPU kernel path or build gives identical text.
