# DIVERGENCE-MAP (2026-10-21): where answers move. 40 % of the 72 phone ids never reach a model, and only 7 MAIN items stay correct in every K0 draw. A divergent stage 1 would have cost about 37 % of this week's generation and 43 % of its judge calls

TL;DR (0 LLM, 0 generation, 0 judge calls, 0 paid; existing traces, aggregates and judgments only; dev ids only, so no blind/, rnd/veil or bench/v0.4)
- **Deterministic (skip on the phone):** 30 of the 72 v0.1 phone ids, plus the warm-up, give the same text with 0 generated tokens on the 1.7B, Gemma and 4B phone runs. These are facts tables, the calculator, places, first-aid cards and health-strict refusals or extractive answers: 12 saf-*, 3 food-*, 15 v0.1. On the desktop pool, 40 of 277 never generate on the K0 or K1 controls. The phone 1.7B also skips generation on 8 more ids through its compact decline, where Gemma and the 4B do generate.
- **Seeds disagree about as much as models do on single items.** Per-item r on live MAIN items: 1.7B seed 42 vs 43 is 0.66 (16 CE flips of 77). Gemma seed 42 vs 43 is 0.81. MacBook vs mini at the same seed is 0.80. The 1.7B vs Gemma is 0.52, and 1.7B vs 4B is 0.49. Same 4B, Pixel vs POCO phone: 0.65. Reference: deep-tier 4B r 0.81 (SEEDVAR).
- **Judge floor:** the 40 deterministic items were re-judged as identical text across up to 15 runs. The median u range is 0.064 (p90 0.17), with 1 CE flip. Below about 0.17 an item's spread is judge noise. Haiku vs Opus on 85 answers: 11 CE-label flips. 11 items are flagged.
- **Divergent subsets (top D, live only):** 30 of MAIN 97 (D >= 0.78), 40 of the 180 (D >= 0.66) and 20 of the 72 phone ids (D >= 0.77). The st180 top 40 is led by factbook (11) and simplewiki (9), the pack-sensitive units. 19 of GATE v2's 50 screen2-K0 items are in the divergent pool.
- **Sentinels:** almost nothing is stable. Over the K0 family (every model, seed, host, null and phone draw), only 5 MAIN live items have 0 CE, 0 refusals and corr >= 3 in every draw, and 2 of those are divergent across pack sets. The files hold every item that qualifies under tiers 1-3, divergent items excluded: 7 MAIN, 10 st180 and 6 v0.1. Fewer than 10 exist for MAIN and v0.1. Single-draw sentinels, as in GATE v2, regress, which is consistent with its "sentinels worse" counts being noise.
- **Savings if stage 1 had run on divergent + sentinels only:** generation 11 426 -> 4 277 item-runs (-63 %), judge calls 14 322 -> 6 106 (-57 %), over the arms touched since 2026-10-19. Skipping only the deterministic items saves -13 % generation and -5 % calls. This is hindsight: the subset was picked from these same runs.

Script: `tools/divergence_map.py` (sha256 587a6551...); run `python3 -I tools/divergence_map.py .` from ruler/. Outputs: `divergence-map.json` (per item, conditions, pair stats, savings; its sha256 is in `divergence-map.json.sha256`, and the savings block is a snapshot of files on disk, so the hash changes while arms keep running), and `ids/*.ids` with `.sha256` (README in ids/).

## 1. Definitions (stated, not tuned)
| term | definition |
|---|---|
| condition | one judged answer set: LITEPACKS K0..K4 (MacBook 1.7B s42), mini 1.7B controls K0/K1 (MAIN, st180), 1.7B K0 s43, Gemma K0 s42/s43, Gemma K1, 4B K0, Gemma K0/K3 cand80, null-cal ws/s43 K0/K1 (screen2), phone Gemma, phone 4B Pixel, phone 4B POCO (23 in all; Haiku 5.5-low, both orders) |
| u | per-item s0 / sref (s = mean of 3 judge dims over both orders; s0 = 0 if declined) |
| labels | null-cal/tools/labels.py: decline never CE; CE = corr <= 1.5; R = decline or warned (refused in the default product) |
| **D** | **u_range + 0.25 [CE label not constant] + 0.25 [R not constant] + 0.25 [Haiku-vs-Opus CE flip or corr gap >= 1.5]**, over every judged condition of the item; NaN with < 2 conditions |
| deterministic | phone: identical text and 0 tokens on 1.7B, Gemma and 4B rows. Desktop: 0 generated tokens on the K0 and K1 mini controls and a single text across every desktop condition. reaches_model = not deterministic (per set: v0.1 uses the phone flag, MAIN/st180 the desktop flag) |
| in_pack | ruler/inpack-assignment.json (side == in); saf-*/food-* are not assigned (null) |
| sentinel | live, not divergent; in the K0 family: tier 1 = 0 CE, 0 R, min corr >= 3.0 (>= 3 draws); tier 2 = 0 CE, min corr >= 3.0, some R; tier 3 = <= 1 CE draw and median corr >= 3.5. Ranked by tier, CE draws, R share, u range, u mean |
Caveat: items with more conditions get wider ranges (MAIN median 15 conditions, st180 9, v0.1 15), so compare D within a set, not across sets.

## 2. Per set
| set | n | deterministic | live | in-pack | D p50 / p75 / p90 (live) | CE flips / R flips (live) | judge flags / judged by both |
|---|---|---|---|---|---|---|---|
| MAIN 97 | 97 | 20 | 77 | 72 | 0.66 / 0.85 / 1.00 | 49 / 57 | 8 / 39 |
| st180 | 180 | 20 | 160 | 180 | 0.50 / 0.66 / 0.85 | 79 / 109 | 3 / 23 |
| v0.1 phone 72 | 72 | 30 (phone) | 42 phone-live | 32 (+15 unassigned) | 0.72 / 0.86 / 1.06 | 29 / 38 | 5 / 20 |

## 3. Pair dispersion (live items; r = per-item Pearson on u)
| pair | n live | same text | r | mean abs du | CE flips | R flips | moves >= 0.3 |
|---|---|---|---|---|---|---|---|
| 1.7B K0 s42 vs s43 (mini, MAIN) | 77 | 7 | 0.66 | 0.067 | 16 | 6 | 1 |
| Gemma K0 s42 vs s43 (MAIN) | 77 | 4 | 0.81 | 0.059 | 5 | 1 | 0 |
| 1.7B K0 MacBook vs mini (MAIN / st180) | 77 / 160 | 9 / 20 | 0.80 / 0.86 | 0.056 / 0.055 | 12 / 21 | 7 / 12 | 1 / 1 |
| null-cal K0 s43 / ws vs control (screen2) | 50 | 3 / 5 | 0.89 / 0.81 | 0.054 / 0.066 | 11 / 11 | 3 / 3 | 1 / 1 |
| null-cal K1 s43 vs control | 41 | 0 | 0.83 | 0.074 | 6 | 4 | 2 |
| 1.7B K0 vs K1 / K3 pack set (277) | 237 | 43 / 30 | 0.73 / 0.60 | 0.067 / 0.089 | 45 / 55 | 83 / 93 | 4 / 12 |
| 1.7B vs Gemma / 4B (K0 s42 mini) | 77 | 2 / 2 | 0.52 / 0.49 | 0.102 / 0.130 | 18 / 19 | 13 / 7 | 3 / 7 |
| phone Gemma vs desktop Gemma s42 (57) | 44 | 4 | 0.83 | 0.059 | 7 | 15 | 1 |
| phone 4B Pixel vs POCO (57) | 44 | 6 | 0.65 | 0.087 | 4 | 0 | 1 |
Reading: a 1.7B seed flips CE on about 1 in 5 live items (16/77), so CE counts on any one draw carry heavy item-level noise. Pack sets flip R (the warning) on 35-39 % of items because they change retrieval. Model swaps decorrelate u the most (r about 0.5).

## 4. Top-divergent subsets (ids files; D in brackets)
- **MAIN 30** (21 in-pack; 18 v0.1, 8 money, 4 cooking): lan-cmp-003 (1.39), lan-exp-007 (1.30), vit-sci-002 (1.24), lan-rsn-004, lan-cmp-005, st-qa-money-se-007, vit-cry-003, vit-cry-006, lan-rsn-006, lan-rsn-001, ... down to st-qa-money-se-011 (0.78). 29/30 flip CE, 30/30 flip R, 6 have a judge flag.
- **st180 40** (factbook 11, simplewiki 9, outdoors 5, medlineplus 4, bitcoin 3, health 3, ethereum 2, firstaid 2, travel 1): led by st-boar-simplewiki-en-011 (1.09), st-boar-factbook-001/006/009, st-boar-medlineplus-en-012. These items move with the pack set, so they belong in a pack-lever screen.
- **v0.1 phone 20** (10 in-pack): the v0.1 part of the MAIN list, plus trv-004 and vit-hum-005. All 20 reach a model on the phone.
- Overlap with GATE v2 screen2-K0: 19 of its 50 ids, with 8 from MAIN and 11 from st180.

## 5. Sentinels (ids/sentinels-*.ids)
| set | ids (tier) |
|---|---|
| MAIN (7) | dng-002 (1), lan-exp-003 (1), lan-ref-002 (1), lan-hlt-002 (2), lan-ref-003 (2), lan-exp-005 (3), lan-exp-004 (3) |
| st180 (10) | st-boar-medlineplus-en-014, st-qa-health-se-011, st-boar-medlineplus-en-015, st-boar-medlineplus-en-020, st-qa-health-se-003, st-qa-health-se-014, st-boar-firstaid-en-014, -007, -004, st-qa-ethereum-se-011 (all tier 1, but only 3-5 K0-family draws each) |
| v0.1 phone (6) | lan-exp-003, lan-ref-002 (1), lan-hlt-002, lan-ref-003 (2), lan-exp-005, lan-exp-004 (3) (dng-002 is deterministic on the phone) |
The 10 per set requested is not reached for MAIN or v0.1 without accepting items that go CE. A false-refusal check on these needs its own null, as GATE v2 §3 did.

## 6. Savings on this week's arms (trace rows and merged judgment rows touched since 2026-10-19, ids in the three sets)
| arm | item-runs generated | in divergent + sentinels | judge calls | calls in divergent + sentinels |
|---|---|---|---|---|
| retfloor (retrieval replay, 0 LLM) | 2240 | 712 | 0 | 0 |
| litepacks | 1400 | 445 | 2118 | 822 |
| gemma4-e2b | 937 | 389 | 1296 | 640 |
| litedecline | 720 | 231 | 678 | 230 |
| null-cal | 616 | 224 | 1160 | 424 |
| gemma4-e2b-confirm | 582 | 234 | 880 | 440 |
| packread | 540 | 180 | 1080 | 360 |
| lite17 | 514 | 140 | 1028 | 280 |
| [private correspondence with the app maintainer, or a result of a run on his device, removed] |
| granite4-1b / jan-v1-edge / ministral3-3b / qwen35-2b / smollm3-3b | 279 / 182 x4 | 129 / 90 x4 | 514 / 394 / 384 / 384 / 374 | 256 / 204 / 196 / 196 / 188 |
| lp-screens, chainwhen, min3cite, citesup, occdecl, judge-v2 and 20 smaller arms (26) | 2360 | 1017 | 3192 | 1438 |
| **total** | **11 426** | **4 277 (37 %)** | **14 322** | **6 106 (43 %)** |
Deterministic-skip only: 9 931 item-runs (87 %), 13 610 calls (95 %); judged arms mostly already skip byte-identical answers. Per-arm rows: divergence-map.json savings_since_2026_10_19.
Limits of this table: (1) hindsight, since D was computed from these runs. (2) Decision runs (LITEPACKS, CONFIRM, VS4B) must stay on the full set; the rule applies to stage-1 screens. (3) A divergent screen needs its own null calibration: GATE v2 bars are for screen2 and do not transfer. (4) Concentrating on high-D items raises per-item variance, so the stage-1 noise per item goes up while the volume goes down.

## 7. How to use (details in ids/README.md)
- Desktop screen: `bash arms/null-cal/tools/run_pool.sh <arm> K0 rnd/research/coordinator/ruler/ids/stage1-pool.ids <patch>`; leave SCREEN_JSON unset until a null is run on this ids file.
- Phone: `python3 -I ruler/tools/phone_request_from_ids.py <base.request.json> <id> --skip ruler/ids/deterministic-v01.ids` gives 43 questions with the warm-up. `--keep ruler/ids/stage1-v01-phone.ids` gives 27.

UNKNOWN: whether D is stable to adding conditions (one seed for most arms; the 4B and the pack sets have one draw each); whether the divergent subset ranks levers the same way as the full set (needs one retro-check on an existing arm, 0 calls, next iteration).
