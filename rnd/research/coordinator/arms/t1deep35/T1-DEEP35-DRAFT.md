# T1 deep35 — DRAFT, NOT AUTHORISED (needs r4to: D3 reopen deep tier + D5 v0.2 used as dev). Prepared 2026-10-06 so it can start the same hour it is approved.

Source: coordinator/PIPELINE-AUDIT-2026-10-06.md §D3/T1. r4to's standing decision (2026-10-05) is "4B only"; this file does not change it.

## Readiness (checked 2026-10-06)
| Item | State |
|---|---|
| Model on mini | `<runner>/shared-models/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf` present (12.29 GB) |
| Mac mini | 16 GiB RAM, disk 38 GiB free (≥ 25 GiB rule ok during the run) |
| Desktop path | earlier deep35 desktop runs used llama-server + the 35B jinja template (deep/RESUME.md "prompt parity"); the 2026-10-01 overnight deep35 run had an arm mismatch and was never re-run (audit §2) → re-run from scratch, do not reuse |
| Engine | cut 6 (frozen claim build) with the deep model as the answer reader for research/compare routes; 4B unchanged elsewhere (O2 hybrid) |
| Judge | judge.v1, both orders, same as the claim runs |

## Proposed criterion (to freeze with sha only after approval)
- Sets: V-para (blind/V-para, 51 judged items; script-only access as in CLAIM-RUNS-cut6) and v0.2 (110 EN, declared burnt → dev by D5).
- Arms: cut 6 4B (existing claim-run answers, reused verdicts) vs cut 6 + deep35 reader; seeds s42 + s43; judge only items whose text changes (all research/compare items will).
- Report: raw, floor-adjusted, win-rate, items ≥ 3/5; paired Δ with two-level CI; time per answer on the mini (descriptive; phone speed is T2).
- Decision: D3 proceeds to device (T2) iff V-para floor-adjusted Δ ≥ +0.05 with CI90 low > 0 AND v0.2 raw CI90 low > 0.50 under deep35; otherwise the deep tier stays parked with a number.
- Cost estimate: ~320 judge calls, ~1 day of mini time (35B on 16 GiB = streamed/mmap; measure tok/s first on 3 items and abort if > 10 min/answer).
