# VEXACT-ACCEPT criterion (frozen 2026-10-19, before the baseline run)

Purpose: an acceptance test that every new asset (knowledge pack, facts table, prompt or engine change) must pass before it ships. The test set is the 11 public bounty example questions (V-exact, bench-vslice): 5 judged items plus 6 vegan venue items. Three of the venue items get only a GPS fix and no city name.

Fixed test harness (tools/run.sh). Engine: kiln tree be-0cfd4a77-cut7-headpass-x2, which is cut 7 + HEADPASS-X2b with the 8dd1faff adapter. Model: Qwen3-4B-Instruct-2507 Q4_K_M on llama-server b11010 CPU on the mini, port 8193. Prompt: D4, i.e. HONESTPROMPT prompts_lib D4 swapped into the engine's answer request in the same way PACKREAD built it, max_tokens 1024. Kit: the claim kit, boar-crypto + boar-wikivoyage-en. Settings: X2b packHeadPass a2 + packDense2 append-budget. Places: kit-vexact (gazetteer + Berlin/Lisbon/Tokyo tiles), meaning device location + the user's area tile. Seeds: 42 and 43. Judge: Haiku 5.5-low, judge.v1, N = 4 shards, both orders, against the frozen web+frontier references. Venues: rnd/kiln/l1/vexact-venues.mjs (scoreFoodAnswer, at least 3 real OSM vegan venues). Baseline = the run labelled `baseline`, which uses this harness with no new asset.

Judged ratio = sum of BOAR rubric scores / sum of reference rubric scores, over both orders, the 5 items and the 2 seeds (the raw ratio as computed by claim_report.py).

Judge reuse: if a candidate's answer to a judged item is byte-identical to the baseline's answer (same seed), the baseline's judgment rows are reused. Only changed answers are judged. This keeps judge noise out of items the asset did not touch.

A candidate asset is ACCEPTED only if all of the following hold on a valid run:
- A1: its judged ratio is not more than 0.03 below the baseline's (delta >= -0.03).
- A2: venues pass 6/6 on each seed.
- A3: its own frozen gate (the asset's arm criterion) passes.

Valid run: 11 traces per seed, 0 errored traces, and, under D4, every model-answered item has its prompt rewritten (rewrite count = model-answered count). An invalid run is fixed and run again; it is never scored.

Reported but not part of the decision: per-item ratios per seed, the paired item-bootstrap CI of the delta (B 2000, seed 11), whether GPS answers name the city, tiers, and the comparison to the earlier V-exact cut 2 numbers (Opus judge: 0.510 on the 5 judged items, venues 6/6).

Caveats, fixed now: n = 5 judged items, so one item can swing the ratio by about 0.1, and A1 is a guard against regressions, not evidence of a gain. The questions are public and the team has seen them, so these numbers do not support a claim. The Haiku judge is not the Opus judge used for the 0.510 figure, which is why a Haiku re-judge of the cut 2 traces is reported next to it.
