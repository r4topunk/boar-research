# LESPORT-FLASH: phone flash bound for LES expert streaming (0 calls, 2026-10-16 20:2x, coordinator; analytic, not a measurement)

Source: the fork's own `[moe-ssd]` counters in raw/s1/lesport-raw-s1/*.err (S1 runs, bank 1280, Qwen3.6-35B-A3B Q2_K_XL, 8 of 256 experts x 40 MoE layers).

| counter (per decode token) | value | note |
|---|---|---|
| expert reads | 320 (8 x 40) | `used=8 layers=40 unique/l=8` |
| cache hits / misses | **0 / 320** on every logged token | bank 1280 of 10,240 slots = 12.5 %; LRU gives ≈ 0 hits on this workload |
| bytes read | 314 MiB per token | 1,007,616 B per expert slot |
| pread wall on the mini | 23–46 ms per token (page cache, 7–13 GB/s) | the rest of the 60 ms/token is compute |

Bound for a phone (I/O-limited part only, compute excluded): tok/s ≤ flash throughput / 314 MiB.

| flash class | sustained read for 1 MiB parallel reads (assumed) | I/O-only bound | with compute ≈ 35 ms/token (M4 ≈ 25 ms; a phone big core ≈ 1.5x) |
|---|---|---|---|
| UFS 3.1 (Pixel 8 class) | 1.5 GB/s | 4.8 tok/s | ≈ 4 tok/s |
| UFS 4.0 (POCO X6 Pro class) | 2.5 GB/s | 8.0 tok/s | ≈ 6 tok/s |
| UFS 4.0 best case | 3.5 GB/s | 11 tok/s | ≈ 8 tok/s |

Reading: with 0 cache hits, LES on a phone is **flash-bound at ≈ 4–8 tok/s**, the same band as bmoe on the Pixel 8 Pro (4–6 tok/s, WEB-SWEEP 10-09), not the mini's 17 tok/s. The lever is **memory** (2.8 GiB RSS vs 7.9 GB), which is what opens 8 GB devices; speed is a wash until the expert cache gets hits (a larger bank: 4 GiB = 4,443 slots is above the fork's 1280 cap; or a predictor-aware eviction). Phone numbers remain unmeasured; this note replaces the "3–7 tok/s" guess in the critique with the counters behind it. Related: LESPORT-L1 TRANSFER (quality), S1 (cold/pressure).
