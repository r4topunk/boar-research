# DENSECHUNK-ST2 step 0 gate — **FAIL at step 0 on G2 (empty-kept count, by the letter)**; G1 and G3 PASS (2026-10-13 11:5x; criterion sha 6c7b12dd…; 0 judge/LLM/paid calls; MacBook)

| gate | rule | OFF → extra (D = 2) | verdict |
|---|---|---|---|
| G1 reach (180 self-test) | fact chunk raw top-8 ≥ 84; chunk kept ≥ 51; article kept ≥ 68 | chunk raw 67 (raw6) → **108** (raw8); chunk kept 43 → **61**; article kept 68 → **100**; empty kept 48 → 34 | **PASS** |
| G2 v0.1 public (60; 39 gold) | gold kept ≥ 12; empty-kept ≤ 11 | gold raw 13 → 19, gold kept 12 → **17**; **empty-kept 11 → 12** | FAIL (+1) |
| G2 v0.2 resolvable (9 of 110) | gold raw ≥ 6, kept ≥ 4; empty-kept ≤ 28 | gold raw 6 → **7**, kept 4 → **6**; **empty-kept 28 → 31** (all 86 gold, descriptive: raw 18 → 24, kept 15 → 21) | FAIL (+3) |
| G2 kit slot share | appended dense chunks' share of kit kept slots ≤ 0.40 | **0.372** (v0.1 41/123 = 0.333; v0.2 83/210 = 0.395) | pass |
| G3 cost | p50 ≤ 2 × OFF; simplewiki scan ≤ 300 ms | p50 209 ms vs warm OFF 145 ms (**×1.44**); simplewiki scan p50 108, p95 171, max 178 ms (first load 473) | **PASS** |

Per pack (fact chunk raw OFF6 → extra8 / chunk kept / article kept / empty kept / appended share of kept): travel 8→13 / 1→3 / 6→12 / 7→4 / .33; ethereum 3→7 / 2→4 / 5→10 / 5→3 / .33; bitcoin 1→4 / 1→3 / 2→8 / 5→4 / .51; health 4→14 / 1→6 / 5→10 / 10→7 / .44; outdoors 8→10 / 5→6 / 10→14 / 7→4 / .46; firstaid 1→7 / 1→4 / 3→5 / 6→5 / .33; medlineplus 14→19 / 10→10 / 11→12 / 4→4 / .35; factbook 13→15 / 10→11 / 13→13 / 1→1 / .35; simplewiki 15→19 / 12→14 / 13→16 / 3→2 / .28.
Family: SE article kept 28 → 54, chunk kept 10 → 22; topic 40 → 46, 33 → 39. Enter/leave on the 180: chunk kept +18/−0, article kept +32/−0.

Identity: OFF list is an exact prefix of the extra raw list 180/180, 60/60, 110/110 (nothing displaced in raw). OFF (new tree) = DENSECHUNK-ST OFF 180/180, 60/60, 110/110; fusion "on" = DENSECHUNK-ST on 60/60 and 110/110; OFF vs warm OFF2 identical everywhere. vitest src/rag 33 files / 220 tests pass, tsc clean.

**Why empty-kept rises although nothing is displaced:** the count is "items with raw ≠ ∅ and kept = ∅". Split (gate-st2.json `empty_kept_split`): items OFF already retrieved for that end empty: v0.1 11 → 9, v0.2 28 → 20; items whose OFF kept was non-empty and now empty: **0 and 0**. The increase is entirely items where OFF retrieved nothing at all (raw = ∅, not in OFF's count) and extra now retrieves only appended dense chunks that grounding drops (v0.1 3, v0.2 11; another 2 / 8 such items now keep a source). For the user these items look the same as OFF (no source). On a fixed denominator (OFF-retrieving items) G2 would read 9 ≤ 11 and 20 ≤ 28 → pass; that reading is not the frozen statistic, so the verdict stays FAIL unless the coordinator rules otherwise in an addendum.

Caveats: (1) compression budget: appended chunks cost kept slots of OFF chunks on 8/60 v0.1 items, 1/110 v0.2, 11/180 self-test (an OFF-kept chunk is cut), with no item going empty; (2) appended share 0.51 / 0.46 / 0.44 on bitcoin / outdoors / health self-test packs (kit share is the gated number); (3) replays on wt/packs (dt512 base), not the cut 7 tree; (4) v0.2 read script-only (counts). Files: aggregates/d0-st2.json, gate-st2.json, runs/st2-*.jsonl, runs/v01-kit.st2.jsonl, blind/bench-v02/runs-packs/densechunk-st2-v02-kit.jsonl; tools/run_st2.sh, d0_st2.py, gate_st2.py; engine patch packdense2.vs-dt512.patch (sha 302fc5cd…; ST fusion copy packdense2-fusion.vs-dt512.patch ea74d8ab…).
