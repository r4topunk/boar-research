# CITEFIX: does a citation-notation normaliser turn the GATE v2 NO-GOs of MINISTRAL3-3B, QWEN35-2B or FOTAPOL into GO? (frozen 2026-10-21, engine-side arm)

## Tags
Tags: probe
Ruleset: 30

## Question
Three candidates failed GATE v2 mostly because their answers went behind the warning line (counted as refusals). The hypothesis is that they cite in a notation the engine does not read. Arm X is the control engine plus a citation normaliser that runs before CT-1 and the compact release/decline rules. It is replayed on the stored screen outputs (0 generation). Answer used for: whether any of the three models reopens for stage 2.

## Fixed inputs
- Tree: kiln-local/be-0cfd4a77-cut7-litepacks (ARM cut7-headpass-x2+litepacks) + `citefix.patch` sha256 `9dcb6b183ac7e5ada0b37538bc302701f86eabd0f2e30817a43d7ee6d5051f47` (adds src/routing/citationNormalize.ts sha256 `e21387214b724b8b...`, called in answer.ts right before CT-1, only when not health and sources.length > 0; reason code `citations:normalized-<n>`). tsc --noEmit clean.
- Normaliser rules (only unambiguous references, numbers 1..sourceCount, no repeats, never inside `code`): `[1, 3]`/`[1; 3]` lists -> `[1][3]`; `[Source n]`, `[Passage n]`, `[Doc n]` (+lists) -> `[n]`; `(Source n)` -> `[n]`; `【n】` -> `[n]`; `[^n]` footnote marker (not a `[^n]:` definition) -> `[n]`. Not mapped: superscripts, bare `(n)`, `^n`, titles or prose ("according to the context"), ranges. It never adds a reference to a sentence the model left uncited.
- Gate: null-cal/GATE-V2.md sha256 34ada53f...; tools/screen_gate_v2.py fa726fc0...; tools/labels.py 0d93acec...; PARAMS K0 net >= 10, false refusals <= 2, U_cov >= -0.059; K1 net >= 9, false refusals <= 4, U_cov >= -0.071. Controls null-cal/control/pool-K{0,1}.json, screens null-cal/pool/screen2-K{0,1}.json.
- Candidate runs (10, frozen traces + aggregates, sha256 prefixes): min3v K0 1cee8ddc/79729e6b, K1 9f21b7da/980dc33a; min3e K0 722844a6/b11aee81, K1 7cace2a2/06c47d6e; q35v K0 7a9d0a5f/d33c1bea, K1 03eff5d5/60138e83; q35e K0 07fe3ca7/d79c4d2c, K1 df2ed1ab/ddd90911; fotapol K0 49b656b5/3ce4576f, K1 c8aad1d1/4857e061 (traces/aggregates).

## Precheck (measured before this freeze, 0 calls)
- What the traces store: answer.text is post-processed; the raw model text is stored only as the token stream, which the adapter elides above 64 token events (complete for 4-14 of 41-50 rows in the Ministral/Qwen3.5 runs, all rows in FOTAPOL). Source passage text is never stored (adapter trace.ts). An exact replay of CT-1 on a mapped citation therefore needs the passages (retrieval re-run) and a reconstructed raw text.
- Why the changed set is still exact without the replay: CT-1, attribution, the release rules and the warning prefix only touch `[n]` tokens and whole-answer prefixes. A normaliser form in the raw text survives verbatim into answer.text (after withoutModelReferences, which runs before the normaliser in the patch too). So "normaliser(answer.text without the warning line) != itself" is exactly the set of answers whose replay can differ.
- Identity (Qwen3-1.7B): normaliser applied with sourceCount 99 (strictest) to answer.text and the stored stream of every row of lp-screens/control/traces/lpctl-K{0,1}-main-s42 (97 + 97) and null-cal/control/traces/poolctl-K{0,1}-st180-s42 (180 + 180) = 554 rows: 0 changed. The screen controls are subsets of these. Post-processed text is therefore byte-identical for every Qwen3-1.7B control output.

## Procedure and decision rule
1. Changed set per run = rows where the normaliser (real sourceCount = the trace's last `sources` event) maps at least one reference (tools/apply.mjs).
2. Runs with 0 changed rows: post-processing is identical, so the GATE v2 line is the original one, recomputed from the frozen aggregate (must reproduce verbatim).
3. Runs with changed rows: first an optimistic BOUND with 0 calls (tools/bound_gate.py). Every changed row is set to its best case for the gate: shown (warning line dropped, not declined), corr 5.0, s 5.0, not CE. Every gate clause is monotone in this direction, since shown-and-correct is never worse for net, false refusals or U_cov than any other outcome. If the bound line is NO-GO, the run is NO-GO and nothing is judged.
4. Only if a bound line is GO: exact replay on the mini (stub generator returning the reconstructed raw text; retrieval re-run and its titles checked against the trace; rows whose raw text cannot be reconstructed exactly are reported and kept at the bound), Haiku 5.5-low judge.v1-low N = 4 both orders on the rows whose final text changed (all other judgments reused), then recompute the gate with screen_gate_v2.py.
5. Verdict per model: GO iff at least one of its frozen candidates (V or E for MINISTRAL/QWEN35; the single FOTAPOL run) passes GATE v2 on K0 after the fix (the arms' own stage-2 condition; K1 reported). Otherwise NO-GO.
6. Reported per run: changed answers, citation compliance before/after (shown live answers with a `[n]`, and answers whose citation-bearing raw text holds an engine-readable `[n]` before/after normalisation), false refusals before/after (bound or exact).

- Tools frozen with this file: tools/apply.mjs sha256 3ce1c4c26765c4a0..., tools/bound_gate.py 28d29a8f99aacefd... (imports screen_gate_v2.metrics/verdict unchanged).

## Power
expected_delta: n/a (deterministic replay; a gate re-read, not a new sample)
n: the GATE v2 screens (K0 50, K1 41)
seeds: 1 (the stored s42 runs)
mde: n/a (the decision is the frozen gate line)
slice: n/a
l1_futility: n/a
split: none

## Ceiling
ceiling: the bound in step 3 is the ceiling; NO-GO at the ceiling closes the run with 0 calls.

## Budget
wall_cap: 2 h
calls_cap: Haiku 100 (at most 10 changed rows x 2 orders x 2 judges per row, plus reserve). 0 Opus, 0 paid APIs, 0 generation.
