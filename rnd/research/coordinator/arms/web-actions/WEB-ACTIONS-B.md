# WEB-ACTIONS-B: five 0-LLM trace analyses from WEB-LOG-2026-10-21 (T1.4, T3.3, T4.1, T10.1, T12.1) — 2026-10-21

0 LLM, 0 judge, 0 generation, 0 paid, 0 phone. Existing traces and judgments only; no blind/, rnd/veil or bench/v0.4 file opened; engine tree read-only.
Scripts in tools/ (python3 -I / node), outputs in aggregates/: b1 da95f5f8, b2 57d43898, b3 e713b4a9, b4 5c7a1425, b5 6807e171 (sha256 prefixes of the JSON).
Labels: CE = corr <= 1.5, correct = corr >= 4 (null-cal/tools/labels.py). No criterion was frozen: these are descriptive re-cuts, not decisions.

## 1. T1.4 (W3): is the warning line an answerability signal or a correctness signal?
Split of warned answers by trace fact: "no source kept" (retrieval.kept = 0; answerability proxy) vs "source kept, low support" (kept >= 1; correctness proxy).
The split matches the reason codes 1:1 (W:no-source 164/164 kept = 0; the other two released codes all kept >= 1). Haiku judge.v1-low; Wilson CIs; diff CI = item-cluster bootstrap.

| pool (Haiku) | warned no-source: n, P(CE), P(correct) | warned kept-low-support: n, P(CE), P(correct) | P(CE) diff (CI) | share of all CEs: no-src / kept |
|---|---|---|---|---|
| LP pooled K0/K1/K3 (WARNCAL frame) | 87, 0.34 (0.25-0.45), 0.09 | 297, 0.40 (0.35-0.46), 0.04 | -0.06 (-0.21..+0.09) | 0.13 / 0.54 |
| MINI replication | 77, 0.34, 0.04 | 191, 0.41, 0.03 | -0.07 (-0.20..+0.07) | 0.17 / 0.50 |
| LP MAIN 97 | 37, **0.19** (0.10-0.34), 0.05 | 98, **0.49** (0.39-0.59), 0.05 | **-0.30 (-0.45..-0.11)** | 0.10 / 0.69 |
| LP ST-SE 100 | 30, 0.57, 0.17 | 127, 0.46, 0.02 | +0.11 (-0.19..+0.34) | 0.15 / 0.52 |
| LP ST-cand 80 | 20, 0.30, 0.05 | 72, 0.19, 0.07 | +0.11 (-0.13..+0.35) | 0.14 / 0.33 |

Comparators (LP pooled, unwarned): no-kept banner-only P(CE) 0.19; kept and unwarned 0.26.
Per tier (HON-7 frame: MAIN 97 K0 s42, mini; n is small):

| tier | no-source share of warned | no-source CE | kept-low CE | diff (CI) |
|---|---|---|---|---|
| 4B | 0.60 | 6/24 | 5/16 | -0.06 (-0.36..+0.23) |
| Gemma E2B | 0.75 | 8/24 | 3/8 | -0.04 (-0.44..+0.36) |
| 1.7B ctl | 0.62 | 8/24 | 8/15 | -0.20 (-0.52..+0.14) |

Opus (WARN-OPUS warned units, unweighted, direction only): no-source 8 units = CE 2, correct 3; kept-low 43 units = CE 15, correct 15.
- **Reading.** Pooled, the two halves have the same error rate (CI spans 0), so the line does not mix two very different signals. By volume it is a support (correctness) signal: 77 % of warned rows have a kept source, and those rows carry 4 of every 5 warned CEs.
- **On MAIN (real questions) the axes split:** no-source warned answers err at 0.19, close to unwarned LLM answers on MAIN (0.17; 15/90). There the no-source half only says "the library cannot answer this" and carries no error information. The kept-low-support half is the error signal (0.49).
- **For NOTE-2:** quote precision on the kept-low-support subset (0.40 pooled, 0.49 MAIN) and describe no-source warnings as an answerability notice. The 4B/Gemma rows warn mostly for no-source (0.60-0.75), so on those tiers the line is mostly an answerability notice. This fits HON-7's weaker 4B precision. n is too small to call it per tier.

## 2. T3.3 (W10): retest flip rate of CE verdicts, and what it means for CE counts of 12-14 per 100
Data: 3 existing repeats of judge.v1-low (Haiku 5.5-low, N 4, both orders; the instrument behind X2B-OFF-MAIN's Haiku rows) on the same 97 MAIN answers (mini K0 control).
The repeats are the lp-screens control plus judge-v2 rep2/rep3. CEu = CE on an unwarned shown answer.

| label | count per repeat | per 100 | label flip, all items (pairwise) | items ever labelled / flipping | flip on deciding items | P(CE again \| CE) | judge-only SD per 100 | two identical arms: P(\|diff\| >= 2) / >= 3 |
|---|---|---|---|---|---|---|---|---|
| CE | 27 / 31 / 27 | 29.2 | 7.6 % | 34 / 11 | **21.6 %** | 0.87 | 2.0 | 0.50 / 0.26 |
| CEu | 11 / 14 / 12 | **12.7** | 3.4 % | 15 / 5 | **22.2 %** | 0.87 | **1.3** | **0.31 / 0.09** |

- The 5 CEu flippers are all cooking/money-se items (cooking-005/007/017, money-005/012). The same half carried X2B-OFF's s42 rise.
- **Implication.** At 12-14 CEu per 100, the Haiku judge alone moves the count by about ±1.3 (1 SD) and ±3 (95 %), with identical answers.
  - X2B-OFF's "+2 allowed" clause sits inside judge noise: two arms with identical answers differ by 2 or more 31 % of the time.
  - The s42 "+3" is at the 9 % tail before any seed noise. Seed noise is larger: 16 CE flips of 77 between s42 and s43.
  - A CE-count clause at this n needs 2 or more seeds, or Opus on the flip items. That is what addendum 1 did.
- **Page rule:** print "CEu n (judge retest ±1.3 per 100, Haiku)" next to every headline CE count.
- **Opus:** no dev-id per-item CE retest exists. JUDGEVAR (V-para) reports Opus correctness identical on 40/51 items and σ_judge 0.003 on the ratio, so the Opus flip rate is probably lower. UNKNOWN on dev.

## 3. T4.1 (W12): DILUTION-K extras split into same-article siblings vs other-article related chunks
Article id = kept passage source URL in the R (ORACLE-REAL) trace; passage [1] = gold. k2/k3 contexts are prefixes of R (29/29). Per-item scores come from aggregates/dilution-k.json (Haiku); dU = sum ds / sum sref; item bootstrap CI.
W12 was marked dropped (RD-4 KILL); it was run here as asked.
- **Siblings are rare:** of 124 extra passages on 28 items, 19 are siblings (15 %) and 105 other-article. Items: all-other 17, mixed 10, all-sibling 1 (plus 1 with no extras and 1 with no kept list).

| contrast | sibling class | other-article class |
|---|---|---|
| R - k1 (all extras), by sibling share >= 0.5 vs < 0.5 | **+0.068 (+0.017..+0.117)**, n 4, 3 up / 0 down | -0.004 (-0.051..+0.041), n 24, 9 up / 11 down |
| R - k1 by mix (all-other / mixed) | mixed +0.032 (-0.024..+0.090), n 10 | all-other -0.008 (-0.067..+0.048), n 17 |
| passage 2 added (k2 - k1), by class of [2] | +0.036 (-0.07..+0.15), n 6 | +0.013 (-0.03..+0.06), n 22 |
| passage 3 added (k3 - k2), by class of [3] | -0.034, n 2 | -0.023 (-0.066..+0.023), n 25; CEu 3 -> 1 |

- **Reading.** The direction matches the prior for siblings: sibling-rich contexts gain when the extras are kept (+0.07, n 4, indicative only). Other-article related chunks are **neutral, not harmful**: "The Power of Noise" style harm is not seen with the 1.7B at k <= 6.
- This agrees with RD-1 (siblings +0.35 conversion) and DILUTION's KILL. Extras do not dilute the 1.7B. If anything, same-article neighbours help, which is the X2b head-pass idea. No action: n 4-6 per sibling cell.

## 4. T10.1 (W23): customs/etiquette questions naming a country or city, and where the router sends them
Replay of detectGeoIntent (kiln-local/be-0cfd4a77-cut7-litepacks src/routing/geo.ts, unchanged, node type-stripping) on 526 unique public dev questions: v0.1 60, 13 self-test sets, rivalset, 4 slices. Existing traces were checked for the route field.
- **Count:** v0.1 0 and MAIN 0. Dev: 7 items.
  - st-qa-travel-se-011: Thai tipping.
  - rivalset trv-01 (Kyoto temples), trv2-01 (Luang Prabang alms), trv2-10 (Mongolia ger), trv2-14 (Stone Town dress).
  - longsession ls06-t11 (Japan tipping) and ls06-t14 (hot-spring etiquette, Japan context).
- **Where they go:** places 0/7.
  - The CUSTOMS guard (geo.ts:118-184) and the absence of a food-place word keep them off the places path.
  - The traces confirm the normal research/chat path with packs (kept Tipping / Etiquette in Asia, Wikivoyage Kyoto / Luang Prabang / Mongolia / Stone Town / Japan). a competitor team's v1.8.3 bug class does not occur here.
- **Wrong path found (not customs, same family):** 3 of the 6 places hits on the 526 questions are misroutes. Each answers "The offline places pack is not installed" with 0 model tokens. The existing cut 7 / dt512 / LITEPACKS traces confirm all 3.
  - **rivalset trv2-03** "What should I eat in Oaxaca, and which nearby ... sites": "nearby" fires NEAR_DEVICE, so the named city is dropped and the query goes to near:device. This is a competitor team's v1.8.4 class. Opus scored it 0 in RIVALSET, where it was logged as an "instant tier excerpt".
  - **rivalset trv2-16** "I'm going to Hokkaido in winter ... what should I eat": "eat" plus the gazetteer candidate "winter" (a place name) makes it a places query.
  - **MAIN st-qa-cooking-se-002** "preserve vegetables in oil at home ... food poisoning": already known as ROUTING-R1 fix P (places-health-veto), 0 U gain.
  - The 3 correct places hits are food-001/002/006.
- **Candidate rule (post-freeze, not tested):** in a multi-clause question with a "things to do / sites / day trips" clause, the food clause is not a places request. Also, "nearby" next to a named place should not override that place. Replay cost: 0 LLM on these 526.

## 5. T12.1 (W25): OSM vegan tags inside our tiles vs worldwide
Distinct OSM refs with diet:vegan in the tiles (source 0 = OSM; no ref is duplicated across tiles), against taginfo worldwide (2026-10-20): yes 48,318, only 3,926, limited 1,336 (53,580 in all).

| tile set | tiles | OSM POIs | vegan yes / only / limited | yes+only+limited | share of worldwide |
|---|---|---|---|---|---|
| hosted world (HF boar-packs @44c3375c) | 8,374 | 3,384,898 | 46,717 / 3,829 / 1,294 | **51,840** | **96.8 %** (yes 96.7, only 97.5, limited 96.9) |
| kit-vgps2 (shipped kit, 9 tiles) | 9 | 110,558 | 2,575 / 252 / 17 | 2,844 | 5.3 % |
| kit-vexact (Berlin, Lisbon, Tokyo x2) | 4 | 92,608 | 2,254 / 187 / 15 | 2,456 | 4.6 % |

- The 3.2 % gap fits edits made between our extract date (OSM 09-25..27) and taginfo (10-20). It does not look like a filter loss.
- **Research-page line:** "The places path carries 51,840 OSM objects tagged vegan yes/only/limited, about 97 % of all such tags in OpenStreetMap (taginfo, 2026-10-20). Its ceiling is OSM's tagging, not our build. About 1 in 25 OSM restaurants carries a vegetarian/vegan tag, so an unlisted place is not evidence of no vegan option. A phone holds only the tiles for its area (the shipped kit: 9 tiles, 2,844 tagged places)."
- Caveat (TILE-PATH): no phone app can run a current-city query today, so this is a data ceiling, not a shipped capability.
