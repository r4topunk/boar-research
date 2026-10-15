# DEVICE-X6 — cut 7 on a 12 GB-class phone: device = desktop? (measurement, pre-declared 2026-10-14)

Status: measurement only (no adoption decision). Written before any judge call.

## Inputs (frozen)
- Phone run A: BOAR Bench 0.2.0, request `final-cut7-v01`, engine commit 0cfd4a77 arm cut7 (patch 04a2a999…), kit = boar-crypto + boar-wikivoyage-en (claim kit), Xiaomi 2311DRK48G (POCO X6 Pro, MT6897, 10.7 GiB RAM, Android 16), airplane mode, no INTERNET permission. Rows: boar-eval/runs/device-poco-x6pro/final-cut7-v01/rows.jsonl → traces.jsonl (converted field-for-field, answers untouched).
- [Redacted for the public release: a secondary product-comparison run B (different app, corpus and pipeline; no decision rides on it).]
- Desktop reference D: arms/stack/runs/v01-cut7-stack-off-s42.traces.jsonl (cut 7, same 2-pack kit, MacBook llama-server, seed 42; the stack arm's OFF run = cut 7 unchanged).
- Items: the 57 non-venue public v0.1 ids of arms/headpass-st/gen-x2b/v01-sw-cut7-x2b-off-s42.jids (same list as every v0.1 L1 run).
- Judge: Haiku 5.5-low, judge.v1, refs bd235bb9…, questions 568b3ece…, both orders, seed 7, shard_judge.sh N = 4 (L1-PROTOCOL). Desktop rows reused only if an existing judgments file has the same provenance (tracesSha256 of D); otherwise judged now. Budget ≤ 342 Haiku calls; 0 paid API.

## Readings (declared up front)
- Primary: per-item mean ratio over both orders; paired Δ(phone − desktop) with a 1000-resample bootstrap CI (seed 7) over the 57 items.
- "Device = desktop within noise" (as DEEPPAR/cut-6 A15): |Δ| ≤ 0.03 AND the CI inside ±0.05. Otherwise: report the Δ and the per-item disagreement (answers differ on the items where retrieval differs; byte-identical answers carry the same verdict copy).
- [Redacted for the public release: secondary B-vs-A product comparison.]
- Speed and memory are reported from the device telemetry as-is (no bar).

> Release note: this public copy differs from the frozen original (the .sha256 pins the private original); two lines about the secondary product-comparison run are redacted.
