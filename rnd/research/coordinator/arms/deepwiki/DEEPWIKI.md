# DEEPWIKI result (coordinator-run, 2026-10-10 16:32–17:1x). Criterion DEEPWIKI-criterion.md sha256 88de2099e2ff5e6dbb2e9dcab39467fbfb50d8af88ffedf8459de1c8a1d3e8c0 (not edited)
**Verdict: NO at the slice.** Adding the enwiki top-100k pack (2.54 GB, 98k full articles) to the deep thinking tier's kit (W) vs the recommended configuration (H), 20-item V-para slice, Haiku 5.5-low N = 4 paired: W 0.485 (0.427–0.538) vs H 0.519, Δ **−0.034 (−0.082…+0.003)**, floor −0.044, h2h 4/8/8, wins 0/0 → NO, not a near-miss for promotion; no full set, no Opus. The larger corpus crowds the k = 6 / 400-token context: Wikipedia-labelled chunks fill 26 of the 28 kept source slots (H: 15 of 24, from the crypto pack's Wikipedia articles) and 11/20 items keep at least one chunk from the new pack, while the answers score lower; retrieval p50 1.19 s vs 0.46 s (2.6×). Corpus size is closed as a desktop lever for the deep tier, as it was for the 4B (enwiki-top100k v1, 10-01).

## Identity
| item | value |
|---|---|
| tree / runner | `be-0cfd4a77-dt512` and `dt512-remote-run.sh` unchanged (cut 6 824e0b35… + deepthink eb3f464b… + dt512 f9a1979b…; thinking 512, succinct, ctx 400, k = 6; `--deep-model`, `--places` kit-vexact, detector v3b, `--timeout-ms 600000`) |
| pack | `<runner>/shared-models/../shared-data/packs/boar-wiki-en-top100k.sqlite` sha 9123b372…, 2,542,215,168 bytes, 98,389 articles, lead vectors for 50,000 (manifest), sha-checked by the adapter at run start |
| requests | smoke 04a08d49… (dh-smoke-H + kit entry), slice 896288d4… (H's slice requests + kit entry; signal20-vpara 6e707734…); `config.arm` dt512, kit = crypto + wikivoyage + wiki-en-top100k |
| smoke | 2/2 deep-thinking, reasoning 441 / 522, 0 errors, pack resolved; ttft 43 s / total 88.6 s (H's smoke 78 / 87 s) → PASS |

## Slice 20 (seed 42; Haiku 5.5-low N = 4 vs H's slice rows)
| arm | kit | ratio (CI) | floor-adj | Δ vs H (CI) | h2h >/=/< | kept sources (Wikipedia-labelled) | items with a new-pack chunk | retrieval p50 | total p50 (p90) |
|---|---|---|---|---|---|---|---|---|---|
| H | crypto + wikivoyage | 0.519 (0.466–0.567) | 0.384 | — | — | 24 (15) | — | 0.46 s | 77.6 s (97.6) |
| W | + enwiki top-100k | 0.485 (0.427–0.538) | 0.340 | **−0.034 (−0.082…+0.003)** | 4 / 8 / 8 | 28 (26) | 11/20 | 1.19 s | 78.5 s (89.2) |
20/20 generated, 0 errors, reasoning median 522 (18/20 at the cap); mini ≈ 30 min; Haiku 40, Opus 0.

## Reading
- With a fixed k = 6 and 400 context tokens, a general corpus displaces the curated packs' chunks on bounty-style questions (travel, crypto, synthesis), and the deep reader does not recover the loss; DEEPCTX showed that more context does not help either. A corpus lever would need retrieval changes (per-pack quotas, reranking) that are closed for the 4B and out of scope for the deep tier on the desktop. a competitor team's full-text-Wikipedia gain (their own 31 deep-detail questions) is on a different question style and corpus scale (30 GB) and does not transfer here.
- Device plan: kit unchanged (crypto + wikivoyage + places); no wiki pack.

## Exposures (script-only; no blind content in any context)
V-para: 1 slice generation (20 ids, seed 42) + Haiku 20 ids (40 calls); H slice rows re-read. Smoke on v0.1 (dev). Outputs: `blind/V-para/runs-deepwiki/`, smoke in `boar-eval/runs/kiln/deepwiki/`, aggregates here. Cost: Haiku 40, Opus 0, mini ≈ 35 min.
