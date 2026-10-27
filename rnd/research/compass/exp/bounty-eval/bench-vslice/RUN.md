# Running the the post author slice (V-exact v1) — for Kiln
TL;DR: 11 items = the post author's own questions. Judge-graded (5): vx-001 'Tell me about Japan', vx-002 'Which signature algorithms are quantum resistant?', vit-hum-001 Mozi, vit-hum-004 Gríma/Saruman, vit-trv-004 Paris–Rome. Venue-graded (6): vegan in Berlin/Lisbon/Tokyo, named city (food-001/002/006) and **GPS** (vx-003/004/005: same question 'Tell me the best vegan restaurants in the city I am currently in', city only from `context.lat/lon`).

1. **Engine runs** (same configs as the main bench; seeds 42 and 43):
   - Android 12 GB 4B (the shipping stack) = the headline; iPhone 1.5B profile = 1B-class context.
   - Input: `bench-vslice/questions.jsonl`. The GPS items carry `context` (EvalItem.context, protocol schema), so check that the runner passes it to the engine (AnswerContext location).
2. **Anchors** (Haiku/Sonnet/Opus/Fable, no web, `harness/anchors.mjs`): only vx-001 and vx-002 are new. The other 3 judge items already have v0.1 anchor answers.
3. **Judge:** `node harness/judge.mjs --bench <this dir> --traces <run>.traces.jsonl --out <run>.judgments.jsonl`. It reads `bench.json` → `refs/refs.jsonl` (private). Venue-list items are not judged.
4. **Venue scorer** (wt/eval scripts/lib/venues.mjs, as for v0.1 food items) on the 6 vegan items against `gold/*.json` (OSM 2026-09-26). Report venues found / ≥ 3 real, and for GPS items whether the answer used the right city.
5. **Report:** `python3 ../claim_report.py vslice-config.json > VSLICE-REPORT.md` (fill in the run paths). The slice is reported **separately** from the main bench verdict.
