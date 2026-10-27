# LITEPREFILL-DESKTOP result (probe 3a392929, 2026-10-16 18:4x): prefill ratio 1.7B/4B = 2.5x, decode 2.2x (mini M4, CPU build b11010, -t 4, 0 calls)

Host deviation: the criterion named the MacBook with an idle rule (load < 4.0); the rule never held (load 23 for 45 min, other sessions) → NOT RUN there (raw/run.log). The same script ran on the idle mini (load 1.5), CPU-only build, same prompts (raw/prompts.json, 5 x ~390 and 5 x ~737 tokens), n_predict 64, temperature 0.

| model | prompt tokens | pp tok/s (median) | tg tok/s (median) |
|---|---|---|---|
| Qwen3-4B Q4_K_M | 390 / 737 | 97.3 / 90.3 | 25.6 / 24.1 |
| Qwen3-1.7B Q4_K_M | 390 / 737 | 238.6 / 231.6 | 56.6 / 53.4 |
| ratio 1.7B / 4B | | **2.45 / 2.56** | **2.21 / 2.21** |

Reading: the "≥ 1.5x prefill" assumption of LITE-PREFILL (BACKLOG row 15) is replaced by a measured 2.5x on an M4 CPU; the X2b append (+413 prompt tokens) costs the 1.7B ≈ 40 % of what it costs the 4B. Projection for the POCO (4B phone prefill 47.6 tok/s → +8.7 s): **1.7B ≈ +3.4 s TTFT**. Desktop CPU ratio → phone is indicative only (the X6 decides; LITE-PREFILL device row stays). Files: summary-mini.txt, items-mini.csv, tools/bench-prefill-mini.sh.
