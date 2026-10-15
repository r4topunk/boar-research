# ORACLE-ST: retrieval ceiling — the known fact chunk injected into the 4B's context on the 180 self-tests (frozen 2026-10-13 20:4x)

## Tags
Tags: none

## Question
Every retrieval / pre-processing lever (dense extra slots R46, keep rules R47, routing R48, stack R49, H8 doc2query, QWRITE) is bounded by what the 4B reader does with the right passage once it is in context. The 180 public self-test items carry the fact's article and chunk per item (`in_pack_facts[].chunk_index`, `source.article_id` in the pack self-test files under shared-data/packs/*/selftest*.json / boar-eval/bench/selftest/<pack>). This arm measures the upper bound directly: OFF = today's build with the item's pack (the S traces), ORACLE-ADD = the known fact chunk appended as an extra kept slot (no displacement, same plumbing idea as packDense2 "extra" — R46), ORACLE-ONLY = the fact chunk + its article lead as the only kept context. Decision use (BACKLOG row ORACLE-ST): ADD − S ≤ +0.03 → the pre-processing family (H8-ST, QWRITE, categories, question matching) closes as product work, the reader is the wall and H10 SFT4B stays the only reader-side lever; ADD − S ≥ +0.08 → H8-ST becomes rank 1 with a PACKDENSE-style step-0 reach gate on the 180; between → H8-ST stays conditional (powered only with wave-3+ items).

## Fixed inputs
- Reader: the shipped 4B claim build (cut 7, `runner-local/be-0cfd4a77-cut7` as used by `arms/packs/tools/run_selftest.sh`), greedy, seed 42, claim kit + the item's pack (identical to the S runs). Engine change in a COPY tree (never wt/packs, never the claim tree itself): a setting, default off (byte-identical off), that reads a per-item oracle file (`BOAR_ORACLE_FILE=<json>`: queryId → {pack, article_id, chunk_index, mode}) and, for mode `add`, appends the named chunk's text (as the engine's own chunk record from the pack, same formatting as a kept passage) after the kept list; for mode `only`, replaces the kept list with [article lead, fact chunk]. Patch saved as `arms/oracle-st/oracle.vs-cut7.patch` + sha256.
- Control S rows: Haiku `arms/packs/selftest-runs/st-<pack>-cut7-s42.judgments.jsonl`, Opus `.judgments.opus.jsonl` (existing).
- Judge: Haiku 5.5-low N = 4 both orders (`shard_judge.sh … 4 haiku`) for both cells vs the S Haiku rows; then Opus judge.v1 N = 4 (`… 4 opus`) for both cells vs the S Opus rows (no near-miss condition needed). Aggregation as PACKS-L2 (paired bootstrap, B 2000, seed 11).
- Public items only (bench/selftest/*); no blind set.

## Power
expected_delta: +0.04 (ADD − S; source: ST2 put ≈ +18 fact chunks into kept for +0.017 Opus → ≈ +0.08 if all 137 missing fact chunks were kept and used alike; DEEPREAD shows the reader uses gold only partly, so halve it); ONLY − S unknown (could be negative: loses the kit's other kept context)
n: 180
seeds: 1 (deterministic generation, RULE 27)
mde: ≈ 0.02 raw at n 180 one seed (Opus); Haiku compresses (treat Haiku Δ as the sign only)
slice: none — measurement of a ceiling on a public dev set; 0 paid calls; all-180 generation ≈ 2 × 20–40 min on the MacBook
l1_futility: n/a (ceiling measurement, both judges run regardless)
reopen: none (new measurement; R46–R49 are cited as the levers it bounds)
split: pre-declared: items where the S run kept the fact chunk (43/180 per GROUND-ST OFF counts) vs did not (137/180) — expected: ≈ 0 on the first, the whole Δ on the second

## Stages and rules
0. Step 0, 0 judge calls: build the oracle file for the 180 items (fail if any item lacks article_id/chunk_index); patch + unit check on 3 items that the appended text is byte-equal to the pack's chunk text and that off = byte-identical traces to S on those 3 items (same prompt bytes).
1. Generate ORACLE-ADD (180) then ORACLE-ONLY (180) on the MacBook (one llama-server at a time; none other running). Record per item: kept count, prompt tokens, whether the fact chunk is in the final prompt.
2. Haiku N = 4 both cells (720 calls) → paired Δ vs S Haiku rows; Opus N = 4 both cells (720 calls) → paired Δ vs S Opus rows. Report pooled, per pack, the declared split.
3. Verdict (Opus rows decide; Haiku reported beside):
   - **READER-WALL**: ADD − S ≤ +0.03 (point estimate) → close the pre-processing family as product work.
   - **RETRIEVAL-HEADROOM**: ADD − S ≥ +0.08 and CI low > +0.03 → H8-ST rank 1.
   - **IN-BETWEEN**: otherwise.
   ONLY − S is descriptive (how much the kit's other context is worth once the fact is present).

## Stop rules and budget
≤ 720 Haiku + ≤ 720 Opus calls; 0 paid API. MacBook disk ≥ 8 GiB; one llama-server; never touch the mini; never stop :8094. Stop at a cell boundary if the Opus stage cannot finish (the Haiku stage alone is still a valid sign).

## Outputs and exposure
`arms/oracle-st/ORACLE-ST.md` (coordinator writes), `runs/` (traces, judgments), `aggregates/`, `tools/` (oracle-file builder, patch). Public items only → no EXPOSURES row; QUEUE row per stage.
