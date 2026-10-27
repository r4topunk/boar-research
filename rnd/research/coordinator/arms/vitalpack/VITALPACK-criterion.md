# VITALPACK-DEEP: do curated encyclopedic intros (Wikipedia Vital Articles level 5) fill the deep tier's empty-kit items without crowding the curated packs? (frozen 2026-10-11 12:3x, loop coordinator)

## Tags
Tags: none

## Question
LOSSMAP (tick 1): retrieval kept no source on 29/51 V-para and 54/110 v0.2 items under the recommended configuration H, and those items carry 55 % / 50 % of H's loss; the primary bucket is absent knowledge (0.59 / 0.55). DEEPWIKI (10-10) closed "corpus size as a plain pack" because the enwiki top-100k pack (2.54 GB, full articles by page views) crowded 26/28 kept slots and scored −0.034. Arm **V** adds the existing `wiki-vital5` pack (163,647,488 bytes, sha256 d3b87d562baba3489f6878bf99783f50d504db94c347029771e53f6d1aecc666, 49,832 intros / 115,813 chunks, same bge-small embedding, built 2026-09-24 by `boar-app/scripts/build-knowledge-pack.mjs`) to the deep thinking tier's kit; everything else = H.
reopen: DEEPWIKI closed crowd-ranked full text (top-100k by views, 4 M chunks); this is a 16× smaller, curated, intro-only pack whose chunks are short (lead sections), so the 400-token deep context can hold a curated chunk next to a vital intro. The step-0 gate below measures exactly the crowding that failed DEEPWIKI before any judge call.

## Fixed inputs
- Replay tool: `arms/deepcovfb/tools/replay-deep.sh` (unchanged; `--deep --gate rules --k 6 --pool 20`, tree `wt/cut7` 6d0b93b1, the deep tier's retrieval settings). Base kit = crypto + wikivoyage (+ seed corpus); arm V = base + `shared-data/packs/wiki-vital5.sqlite`.
- v0.1: base replay = `arms/deepcovfb/replay-base.jsonl` reused byte-identically; gold `boar-eval/bench/v0.1/gold/sources.json` (39 items).
- Blind sets (script-only scoped exception, as DEEPCOV-FB/NOTES35): V-para judged ids (51, `runs-cut6/judged.ids`) from `blind/V-para/items.jsonl`; v0.2 judged ids (110) from `blind/bench-v02/live/v0.2/questions.v02-new.jsonl`. Replay outputs (they contain query text) stay under `blind/<set>/runs-vitalpack/`; rnd gets counts and ids.
- Pack attribution (fallback.py rule): a chunk is the vital pack's if its source is labelled "Wikipedia" and its title is not an article of the curated crypto pack.
- Control for later stages: H = dt512 rows (Haiku slice rows, Opus s42/s43).

## Power
expected_delta: +0.02 raw on V-para (source: LOSSMAP no-kept items = 0.55 of H's loss with mean ratio 0.55; DEEPNORAG showed the packs are worth +0.045 to the deep tier; if the vital pack keeps a relevant chunk on a third of the no-kept items and those items gain what a kept source is worth, ≈ +0.015…+0.03)
n: 51 (V-para, two seeds) after direction on v0.2 (110, s42)
seeds: 2 on V-para, 1 on v0.2
mde: V-para two seeds ≈ 0.03; v0.2 one seed ≈ 0.025 — expected_delta ≈ mde on V-para: the arm can only decide a LEVER at the full two-seed stage, not at the slice
slice: random20-v02.ids (direction) then random20-vpara.ids
l1_futility: stop only if Haiku delta <= 0 AND h2h <= control; any Haiku delta > 0 -> Opus N=4 on the same 20 ids
reopen: see Question

## Stages and rules
0. **Replay gate (0 calls), all three must hold:**
   (a) v0.1: gold ENTERS the kept set on ≥ 5 of the 39 gold items (DEEPWIKI's peer pack: +7) and 0 items are emptied;
   (b) crowding: the vital pack's share of kept slots ≤ 40 % over the retrieving items on every set (DEEPWIKI's pack: 62 % on v0.1, 26/28 on the V-para slice);
   (c) coverage: of the base replay's empty-kept items on V-para and v0.2, ≥ 30 % keep ≥ 1 source with the pack.
   FAIL on any → closed at step 0, no judge call. Also report: retrieval p50 base vs V; overlap of the replay's empty-kept ids with the H traces' no-kept ids (lossmap aggregates).
1. Smoke on the mini (2 v0.1 items, dt512 tree + kit entry, as DEEPWIKI): pack resolves, 2/2 deep-thinking, 0 errors; retrieval time vs H's smoke.
2. L1 slice random20-v02 (Haiku N=4) vs H's v0.2 Haiku rows; rules above.
3. v0.2 full 110 s42 Haiku vs H → Opus N=4 (220) vs H (L2-H-1seed): direction.
4. V-para s42 + s43 Opus N=4 (204) vs H (two seeds, common-mode CI).
Verdict: LEVER (V-para two-seed Δ ≥ +0.03, CI low > 0) / SMALL (CI low > 0, Δ < 0.03) / NO. "not decided at MDE" when |Δ| < 0.03 with the CI through 0.

## Stop rules and budget
Disk ≥ 25 GiB on the mini (the pack is 163 MB; present on the mini as `<runner>/shared-data/packs/wiki-vital5.sqlite` → pinned d3b87d…), heavy lock, one MoE server, detector untouched. Judge calls only from Mon 2026-10-12 (week caps). Haiku ≤ 40 + 220; Opus ≤ 40 + 220 + 204.

## Outputs and exposure
`arms/vitalpack/VITALPACK.md`, `aggregates/replay-gate.json`, blind replay outputs under `blind/<set>/runs-vitalpack/`. EXPOSURES rows: one per blind set (replay only, 0 judge calls) at step 0; generation/judge rows later.
