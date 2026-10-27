# DEEPNORAG result (coordinator, 2026-10-10 04:31–05:10; arm.sh). Criterion DEEPNORAG-criterion.md sha256 1c78caeaba596d4ef8af6dead79af333dda5b0c397c39327b3187f8f62b2bee6 (unchanged). Diagnostic, Haiku only.
**Reading: RETRIEVAL-MATTERS.** Deep + thinking 512 **without the knowledge packs** (N, `config.kit = []`) vs the same configuration with packs (H = DT512 slice), V-para slice 20, seed 42, Haiku 5.5-low N = 4 paired: Δ N − H ratio **−0.045 (−0.083…−0.011)**, floor-adj −0.056; h2h 3/8/9; N 0.481 (0.418–0.542) vs H 0.526. The CI excludes 0 and Δ ≤ −0.03, so stage 3 (full set) is not needed by the criterion: the packs still add on the order of +0.04–0.05 (triage scale) to the deep tier even with thinking. A device deep path should keep retrieval.

## Identity and gates
Tree `be-0cfd4a77-dt512` (cut 6 + deepthink + dt512 patches), runner `dt512-remote-run.sh <run> D` (places kit-vexact kept, detector v3b kept), persona succinct, thinking 512; requests = DT512's slice/smoke requests with `config.kit` emptied (slice sha f36f94b8…, smoke 8a8274e3…). Smoke (v0.1 vit-hum-001, lan-exp-001): 2/2 deep-thinking, 0 errors, 0 items with kept context, 1 `grounding:no-source-memory` → PASS. Slice route check (counts): N items with any kept context 1/20 (a places/area source), H 12/20; `no-source` codes N 11/20, H 7/20.

## Slice 20 (aggregates/L1-NvsH-slice.haiku55-low.json, think-N-slice.json)
| arm | Haiku ratio (CI) | floor-adj | Δ vs H (CI) | h2h >/=/< | budget hits /20 | answer tok | total p50 | ttft p50 |
|---|---|---|---|---|---|---|---|---|
| H with packs (DT512 slice) | 0.526 (0.474–0.575) | 0.392 | — | — | 17 | 94 | 67.7 s | 62.0 s |
| N no packs | 0.481 (0.418–0.542) | 0.336 | **−0.045 (−0.083…−0.011)** | 3 / 8 / 9 | 17 | 99 | 94.9 s | 83.4 s |
N was slower, not faster: without sources the model writes longer and the mini was under a different load (ttft 83 s vs 62 s; not a controlled timing comparison; the prompt is ≈ 400 tokens shorter so prefill cannot explain it).

## Reading
- Retrieval remains a real contributor for the deep tier with thinking on the bounty-style set (slice of the 20 weakest 4B items, 1 seed, Haiku scale; sign and size consistent with the 4B scorecard's +0.02 and the deep tier's gain pattern). The device plan keeps the packs and the embedder for the deep path; "skip RAG on deep" is closed.
- Cost: Haiku 40, Opus 0, mini 39 min.

## Exposures (script-only)
V-para: 1 slice generation (20 ids) + Haiku 20 ids (40); H slice Haiku rows re-read. Smoke on v0.1. Outputs `blind/V-para/runs-deepnorag/`, smoke `boar-eval/runs/kiln/deepnorag/`, aggregates here (no per-item).
