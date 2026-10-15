# FACTS r6 criterion (frozen 2026-10-06 22:56, before any code/data). Coordinator decision (autonomous loop). Last FACTS round of
# this line: if r6 FAILs on set 4, the line closes at r5 (safe, recall 60–75 %) and cut-7 input = r5, pending the maintainer.
Why: set 3 FAIL was 8/16 coverage, 5/16 trigger, 3/16 data disagreement; precision is solved (0/60 adversarial fires).
Scope (base wt/facts 802c28bb = r5):
A. ASSET expansion via tools/fetch_wikidata.py + build_asset.py, same build-time data gates as r2 (population dated ≥ 2020,
   no country/city founding dates, former/unbuilt dropped, unit range checks, ambiguous same-label names refused): add cities
   with population ≥ 300k (all, not top-300), mountains: 500 highest by elevation + all with prominence ≥ 1,500 m, rivers: 300
   longest, buildings/towers: 300 tallest + the 100 largest dams by height, lakes: 200 largest. Asset ≤ 1.5 MB, new sha recorded.
   Each new entity keeps the existing alias rules; no hand-written aliases.
B. TRIGGER (5 fixes only): opener typos limited to {whta, waht, wat, hwo, whats'} → what/how; property-first openers "official
   language of X", "continent of X", "what continent is X in/on", "what country/countries border(s)/surround(s) X"; compare_elevation
   /compare_height for "taller/higher" when both entities are mountains or both buildings. Nothing else.
C. DATA REVIEW of new rows: an Opus agent reads a random 60-row sample (seeded, seed 46) of the NEW entities and flags wrong/odd
   values (unit, magnitude, stale year, wrong entity type); bar: ≤ 2/60 flags, and every flagged class gets a build gate before
   the final asset. Same as DATA-REVIEW.md (r2).
Gates: G1 tsc + vitest; 13 DATA-REVIEW probes 0 fires identical to r3; r4 fresh probes 1/22; nearmiss-lc.jsonl (dev now) FP 0/40;
G2 7/8 identical; G3 0/52, 0/12, 0/11, dev chat (new entities may add TRUE-slot fires: report each, must be correct, ≤ 4/192);
G4 replay non-target 52/52; G5 warm p95 ≤ 1 ms; cold index load ≤ 250 ms (asset is bigger). Dev sets 1–3: report vs r5.
Blind sets, written by separate agents that see only the entity-class spec (not the table): recall-set-4.jsonl (40 fact + 20
near-miss, distribution like set 3, entities not used in sets 1–3) and nearmiss-lc2.jsonl (40 lowercase adversarial, must
include product/brand/person senses of mountain, river, dam, building and mid-size city names). Shas frozen before the final build.
nearmiss-lc2 run once by the r6 agent after its final commit (FP 0/40 or FAIL). Set 4 run once by the coordinator.
Verdict on set 4: PASS recall ≥ 85 % AND FP 0/20 AND precision ≥ 90 %; PARTIAL 75–84 % AND FP 0/20; FAIL otherwise. No rescue,
no r7. Both sets burnt after. Judge: none. Dev only (no the private held-out dir, v0.2, V-para). Time box 4 h agent time.
