# Q8SCREEN (2026-10-20): Qwen3-1.7B Q8_0 vs Q4_K_M on GATE v2 (sha 34ada53f): NO-GO on K0 and K1, stage 2 not run
Criterion Q8-criterion.md sha256 661d27eff663d95b22324129a27cf17bfd4428e7546309be435d7316bb5de931 (frozen, committed 6036429e before generation). Candidate q8.patch sha 7266eef7...; mini, slot lock, Haiku 5.5-low N 4.
```
screen2 K0: problems 30 | fixed_u 10 (by refusal 4) | new CEu 1 | net 9 (bar 10) | false refusals 1/20 (max 2) | sentinels worse 5 (report only) | U_cov -0.0378 [-0.0772, -0.0022] (min -0.059) | changed 49 | dead changed 0 -> NO-GO
screen2 K1: problems 21 | fixed_u 8 (by refusal 5) | new CEu 1 | net 7 (bar 9) | false refusals 1/20 (max 4) | sentinels worse 2 (report only) | U_cov -0.0568 [-0.1066, -0.0087] (min -0.071) | changed 38 | dead changed 0 -> NO-GO
```
| | K0 Q4 -> Q8 | K1 Q4 -> Q8 |
|---|---|---|
| CE-unwarned (screen) | 30 -> 21 | 21 -> 14 |
| warned | 0 -> 5 | 0 -> 6 |
| answer tokens/item | 41.2 -> 41.6 | 44.0 -> 42.3 |
| mini decode tok/s (mean) | 56.5 -> 37.1 (x0.66) | 53.5 -> 36.1 (x0.67) |
| mini wall ms/item | 2130 -> 2164 | 3625 -> 3284 |
Mini wall is confounded by the shared mini (other jobs at different loads; prefill got faster under Q8, i.e. load differs); decode ratio is the cleaner speed signal. Q8 fixes are in the null band (net 9 vs null 6-8 K0; 7 vs 6-7 K1): no detectable effect of the quant.
Phone cost: file +0.73 GB (1.834 vs 1.107 GB) => RSS about +0.7 GB. Projected (not measured) Pixel 8a decode: Q4 12-16 tok/s x 0.604 (weight-bytes ratio) = 7.2-9.7 tok/s; measured mini decode ratio 0.66 gives 7.9-10.6.
Haiku calls: K0 98 + K1 ~80 (see runs/logs/*.calls). 0 Opus, 0 paid. Process note: a first background loop and a second driver overlapped (K0 preflight lock collision, harmless; K1 mini job ran once).
