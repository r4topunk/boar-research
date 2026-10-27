# RC1-SPEED: RC1 speed readout on the Pixel 8a (2026-10-21)

TL;DR: RC1 on the Pixel 8a ships only Qwen2.5-1.5B. 9 questions, Detailed, one run: answer p50 25.2 s, p90 42.9 s; decode p50 18.6 tok/s. Retrieval fired on 1 of 9. Measurement only, no verdict, not a frozen-band row. Internal: native absolute numbers stay internal until r4to's word.

## Setup
- App: team.sopa.aoair 2.0.0-rc1, versionCode 4, release (not debuggable); APK sha256 2ef43258...4f17 (full hash in aggregates/readout.json).
- Device: Pixel 8a, Android 17 (device.json), MemTotal 7.5 GB, airplane mode on, on AC, battery 100 %.
- Installed models: only qwen2.5-1.5b-instruct-q4km. The 1.7B request rc-speed9-17b failed ("matches no installed model"), so the 1.7B arm is closed for RC1 (runsheet row 2). No 4B installed.
- Persona Detailed (every row), maxTokens 1024, pipeline legacy, evalSetVersion dd1022-speed9, run id rc-speed9-15b (wall 244 s).
- Source: handoff/pixel8-2026-10-20/bench/results/rc-speed9-15b/ (rows.jsonl, summary.json, device.json, readout.json, telemetry.csv).

## n = 9 (warmup excluded)
Row 0 = warmup-000 ("What is the capital of France?", category warmup): it is the cold row (model load 1.27 s, TTFT 2.83 s, 264 tokens) and is not an eval question. summary.json counts all 10 rows (p50 20.5 s, p90 41.4 s); the numbers below use the 9 questions.

| metric | p50 | p90 / note |
|---|---|---|
| answer total | 25.2 s | p90 42.9 s (range 2.3-48.8 s) |
| TTFT | 1.08 s | p90 2.27 s (max 6.29 s, the retrieval row) |
| tokens generated | 376 | p90 651 (sum 3585) |
| decode tok/s | 18.6 | 22.0 first row to 14.8 last; first-3 mean 20.6, last-3 mean 15.5 |
| prompt tokens | 61 | max 324 (retrieval row) |
| retrievalMs | 0.06 s | p90 0.10 s |
| retrievalUsed | 1 of 9 | lan-exp-005 (Sahara): TTFT 6.3 s, prompt 324 tokens, 48.8 s total |

Generation is about 95 % of answer time; at Detailed the answer length is the time.

## Resources (one run)
- Peak RSS 2.55 GB (max over rows), PSS peak 2.3 GB (telemetry 2.41 GB max), 0 app deaths, 0 LMK lines.
- Battery temperature 27.2 C before, 32.1 C after (telemetry end 32.1; rise about 5 C over the run). Charging on AC, charge counter 4510000 to 4506000 uAh.
- Thermal status 0 before and after.

## Caveats
- Wrong model for the 8 GB claim (1.5B, not the 4B or 1.7B), retrieval on 1/10: outside the frozen band; descriptive only. Installed packs not read, so why retrieval fired once is open (PAGE-DRAFTS open item 13).
- One run, one seed, short questions (prompt p50 61 tokens). Not like-for-like with the bench note2 refs (aggregates/ has none; see note2-rc-ref-*.json in the source folder: line presence 0/5).
