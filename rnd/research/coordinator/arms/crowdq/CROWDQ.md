# CROWDQ — cost of installing all 9 packs as peers (P) vs the one relevant pack (S), 180 public self-test items (2026-10-13 15:4x)

Criterion sha 71603c60… (frozen, unedited). 4B claim build cut 7, seed 42, deterministic. 0 paid calls, 0 Opus. **Haiku 5.5-low: 360 calls** (9 × 20 × 2 orders, N = 4 shards, 36/36 shard exits 0, no reruns).

## TL;DR
- **Pooled Δ P − S raw −0.016 (−0.033…−0.001)**, above_min −0.021 (−0.042…−0.001); items better/worse/same 48/74/58. S 0.493 → P 0.476.
- **Family (declared split): SE −0.033 (−0.055…−0.011)**, above_min −0.041; **topic +0.004 (−0.017…+0.026)**. The cost sits in the SE packs, as expected.
- **Reading (strict rule): cost small.** |Δ| = 0.016 < 0.03. The CI high is below 0, so the cost is real but under the MDE. It is not a near-miss (Δ > −0.02), so no Opus pass is recommended. Per the rule, the top-1 router line closes at the product level (prize below MDE), and the STACK line reduces to the keep rule + quota. Caveat for STACK: the SE family alone shows −0.033 with its CI below 0, so a keep rule/quota aimed at SE items is where any prize is left.

## Reach check (traces, URL match of the fact article; ruling QUEUE 15:0x: band 40 ± 4 = 36–44)
- Fact article kept: **S 59/180 → P 41/180 (in band)**. Replay (PACKROUTE step 0, wt/packs tree, chunkId): S 68 → P 46; same ratio (0.69 vs 0.68).
- SE 29 → 24, topic 30 → 17. Kept slots from the item's own pack 201 → 118 (SE 120 → 72, topic 81 → 46).
- Bare-title matching was rejected because it gives false positives (factbook "Austria" vs kit "Wikivoyage: Austria": S would read 67).
- Installed-pack list: config.kit = 11 entries on all 180 traces (kit 2 + 9 packs); 0 errors; foreign wave-pack passages are kept on every SE pack, so the 9 packs were live.
- Crowding attribution: foreign (not the item's pack) kept slots S 72 (all kit: wikivoyage 64, other 8) → P 164: **simplewiki 66 (40 %)**, wikivoyage kit 42 (26 %, was 64 under S), qa-travel-se 16 (10 %), qa-ethereum-se 11, kit/other 8. Kept share under P (all kept slots, 282): simplewiki 36 %, wikivoyage 15 %, qa-ethereum-se 13 %.
- raw/kept per item: raw 646 → 682, kept 273 → 282, empty kept 51 → 54 items. Per-item rows are in aggregates/reach.json.

## Precheck / RULE 27 (same_answer.py S vs P)
- Changed vs S (kept list or promptTokens differ): **89/180 = 49 %** (≥ 20 %, passed before any judge call); kept list differs on 85.
- kept_unchanged 102: same answer 90/102. **kept_unchanged_prompt_same 90/91** (one item: same kept titles and prompt length, different answer). All items: same answer 92/180.

## Per pack (Haiku raw, paired Δ with CI, items better/worse/same; fact article kept S → P; own-pack kept slots S → P; changed)
| pack | S | P | Δ (CI) | b/w/s | fact | own kept | changed |
|---|---|---|---|---|---|---|---|
| qa-travel-se | 0.423 | 0.439 | +0.016 (−0.027…+0.060) | 7/6/7 | 6→5 | 15→11 | 6 |
| qa-ethereum-se | 0.516 | 0.454 | −0.062 (−0.113…−0.017) | 2/11/7 | 7→7 | 31→26 | 8 |
| qa-bitcoin-se | 0.469 | 0.428 | −0.040 (−0.081…0.000) | 2/8/10 | 2→2 | 32→15 | 14 |
| qa-health-se | 0.525 | 0.501 | −0.024 (−0.053…+0.008) | 7/10/3 | 5→4 | 19→7 | 15 |
| qa-outdoors-se | 0.518 | 0.463 | −0.056 (−0.122…+0.005) | 6/9/5 | 9→6 | 23→13 | 9 |
| boar-firstaid-en | 0.471 | 0.465 | −0.006 (−0.034…+0.021) | 5/10/5 | 2→1 | 11→5 | 5 |
| boar-medlineplus-en | 0.508 | 0.517 | +0.009 (−0.043…+0.072) | 8/8/4 | 11→3 | 25→4 | 15 |
| boar-factbook | 0.438 | 0.454 | +0.016 (−0.030…+0.068) | 7/7/6 | 5→1 | 7→1 | 14 |
| boar-simplewiki-en | 0.566 | 0.561 | −0.005 (−0.025…+0.015) | 4/5/11 | 12→12 | 38→36 | 3 |

Note: medlineplus and factbook lose most of their own passages (largely to simplewiki) with no measured quality loss. On these items simplewiki seems to stand in for the specialist pack; the SE packs have no such substitute.

## Caveats
Dev data (public, agent-written gold); Haiku compresses gaps (L1, not a claim number); one deterministic seed (90/91 same-answer floor); S Haiku rows were judged in an earlier session (same judge model, settings and bench bytes; system label differs); per-pack CIs at n = 20 are wide; ethereum's −0.062 has 7/7 fact kept, so its loss comes from crowded supporting passages, not the fact article.

Files: tools/{selftest_to_bench_all9.py, run_all9.sh, chain.sh, reach.py, judge_all9.sh, crowdq_agg.py}; runs/st-<pack>-cut7-all9-s42.{requests,traces,judgments}.jsonl (+ .ids, .shards, logs); aggregates/{reach.json, crowdq.json, st-*-all9-s42.floor_metrics.txt}. P traces + judgments = STACK control.
