# MOESCREEN-gemma4: Gemma 4 26B-A4B UD-Q2_K_XL closed-book, v0.1 EN 57, judge.v1 (Kiln, 2026-10-07 01:58–03:55)
**TL;DR: NO.** Ratio **0.613** (CI 0.559–0.666). Paired Δ vs the 4B closed-book is **+0.126** (CI +0.080…+0.171; bar +0.05 met). Paired Δ vs deep35 closed-book is **+0.018** (CI −0.025…+0.057; bar +0.03 not met).
Criterion `MOESCREEN-criterion.md` (a3667f51… + Addendum 1 386e983c…), same protocol as `MOESCREEN.md`. Eligibility: the Qwen3.5 judge finished at 01:55, before 05:00, and the disk gate passed. Dev only; 1 seed; no rescue.
## Settings (identical to MOESCREEN.md; no deviation from the Qwen3.5 run)
- Model: unsloth/gemma-4-26B-A4B-it-GGUF `gemma-4-26B-A4B-it-UD-Q2_K_XL.gguf`, 10,546,934,240 B, sha256 `2a1d26df…` (= HF lfs oid). llama-server b11010 (0.4.1-dev, 4bc272f).
- Same 4B-row protocol (anchor.v1, max 450, 0.7/40/0.95/0.05, seed 42, `enable_thinking=false`, `-t 4 -c 4096 -np 1 --jinja --no-webui`), runner `moescreen-anchors.py` ed1decad…, under `<runner>/bin/run-heavy`.
## Gates (frozen)
| gate | bar | result |
|---|---|---|
| free disk after download | ≥ 25 GiB | 27.8 GiB projected; 26.7 GiB measured (28,047,028 KiB) PASS |
| model loads (gemma4 on b11010) | loads | yes, /health in 27.2 s PASS |
| smoke decode, 3 items | ≥ 5 tok/s | 16.50 / 16.25 / 16.27 PASS |
| thinking/hidden tokens | 0 | 0 (no think/channel/turn tokens, 0 reasoning_content; smoke and all 57) PASS |
| non-empty answers | 3/3 | 3/3 (57/57 full) PASS |
| peak RSS | ≤ 13 GB | 7,350 MB smoke; 8,224 MB full PASS |
## Speed (Mac mini M4 CPU x4, contended: `smbd` 750–890 % CPU, load 11–14)
- Decode median **11.37** tok/s (range 7.7–17.1), aggregate 11.47. Prefill median 13.2, aggregate 13.2.
- Per item median 33.6 s; 57 items in 32.6 min. Tokens in / out median 143 / 272; 0 answers hit the 450 cap.
- RSS 5,932 MB idle, peak 8,224 MB. Load to /health 25.2 s.
- About 2.4× the Qwen3.5 decode under the same contention (4B active parameters vs 3B, but a smaller file that stays resident).
## Quality (judge-core summarize; `analysis-gemma4-vs-4b.json`, `analysis-gemma4-vs-deep35.json`)
| system | ratio (95% CI) | floor-adj (CI) | win / tie / loss | pass / cw / fail | C / Cm / U |
|---|---|---|---|---|---|
| **Gemma 4 26B-A4B closed** | **0.613 (0.559–0.666)** | 0.515 (0.448–0.578) | 0 / 1.8 / 98.2 % | 26 / 20 / 11 | 3.14 / 2.97 / 2.96 |
| deep35 Qwen3.6-35B-A3B closed (Add. 1) | 0.596 (0.540–0.648) | 0.492 (0.424–0.562) | 0 / 3.5 / 96.5 % | 15 / 27 / 15 | 2.72 / 3.18 / 2.87 |
| Qwen3.5-35B-A3B closed | 0.603 (0.548–0.659) | 0.501 (0.431–0.568) | 1.8 / 1.8 / 96.5 % | 17 / 25 / 15 | 2.79 / 3.17 / 2.90 |
| Qwen3-4B closed (ORACLE row) | 0.487 (0.433–0.541) | 0.357 (0.286–0.421) | 0 / 0 / 100 % | 10 / 30 / 17 | 2.44 / 2.45 / 2.32 |
**Paired vs 4B, n = 57:**
- Δratio **+0.126** (+0.080…+0.171); Δfloor-adj +0.158 (+0.102…+0.219).
- Better 41 / worse 8 / equal 8. Converted 1 (lan-ref-003), regressed 0.
- Median length 193 vs 177 words.
**Paired vs deep35 closed:**
- Δratio **+0.018** (−0.025…+0.057); Δfloor-adj +0.023 (−0.027…+0.075).
- Better 25 / worse 19 / equal 13. Converted 1 (lan-cmp-004), regressed 0.
- Correctness is the highest of the three MoEs (3.14 vs 2.72), with the most passes (26 vs 15) and the fewest cw (20 vs 27).
## Verdict (frozen rule, same as Qwen3.5)
- GO needs both:
  - Δ vs deep35 closed-book ≥ +0.03: **+0.018, not met**;
  - Δ vs 4B ≥ +0.05: **+0.126, met**.
- **Verdict: NO.**
## Judge
114/114 calls, judge.v1 / claude-opus-5-5, refs bd235bb9, seed 7, `--gap-ms 1000`; 0 errors, 0 rate limits, 15.0 min, [usage detail removed].
## Files and disk
- Run files in `boar-eval/runs/kiln/moescreen/`:
  - `moescreen-gemma4-v01-s42.traces.jsonl` (sha 19606f5a…), `.judgments.jsonl`, `.log`, `.server.log`;
  - `judge-moescreen-gemma4.log`, `smoke-gemma4.*`.
- The GGUF was deleted from the mini at 02:44; mini free space after deletion was 36.6 GiB (MODELS.md and DISK-LOG.md).
## UNKNOWN
- **Seed noise.** This is 1 seed, and the +0.018 vs deep35 sits inside its CI. A second seed could move it either way. Per the criterion, there is no rescue.
- **Phone speed and memory.** These were not measured. The 10.5 GB file is smaller than deep35 (12.3 GB), and its desktop decode was faster.
