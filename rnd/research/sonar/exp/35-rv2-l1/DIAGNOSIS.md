# Why rv2 lost while gold sentences rose 7 → 18 (Sonar + Anvil, 2026-10-03 night; 2 h box)

TL;DR:
- **Recommendation: park the retrieval line for the bounty.** No retrieval variant is worth another L1 now:
  - the best case I can argue is ≈ +0.01, below what 2 seeds can detect (MDE ≈ 0.04 per seed);
  - it costs 3.6× retrieval time.
- **The loss is 3 items.** v0.1 EN Δ = −5.4 rubric points (−0.019 ratio).
  - lan-rsn-002 Burj/Baikal (−3.1), lan-cmp-001 Brazil/Russia (−2.6) and lan-exp-003 Kenya (−1.7) sum to −7.3. Both seeds agree on each.
  - Without them, rv2 is +0.007. Items better by ≥ 0.5: 10; worse by ≥ 0.5: 8.
- **They are 4B failures given correct-but-partial context, not retrieval misses.** In each, the context holds the right facts:
  - Brazil/Russia: the right populations are in context, and the 4B writes "No… Russia over 140 million, Brazil about 212 million. Therefore Brazil has a larger population".
  - Baikal: the window says "deepest point 1,642 m **below sea level**", and the 4B concludes the Burj top sticks out by 830 m. A, from memory: correct.
  - Kenya: a 60-word window lists English as the official language, and the 4B drops Swahili. **Anvil's Q450 loses on Kenya too (−1.33) with its oracle passages.**
- **Q450's gain lives where rv2 doesn't reach.** R's context holds a Q450 passage (≥ 50% of its 4-grams) on only 8 items.
  - On the 40 items with < 20% overlap, Q450 gains **+18.7** rubric points over the engine; rv2 gains −0.8 there.
  - On the 8 shared items, Q450 +1.5 vs rv2 −2.75 (Baikal: Q450's 120-word passage +0.5; rv2's 60-word window −3.1).
- **The suspects that don't hold:**

  | Suspect | Evidence |
  |---|---|
  | displaced kit passages | items where R dropped ≥ 1 of A's Wikivoyage/crypto passages: Σ +0.58; elsewhere −6.0 |
  | answer style | same mean length (56 words); no declines in either arm; R cites more (56 vs 43 of 114) with fewer uncited warnings (47 vs 60) |
  | judge noise | seed signs agree on 15/18 items with \|Δ\| ≥ 0.5 |

## Is any variant worth another L1?
| Variant | Fixes the 3 losers? | Reaches Q450's 40 items? | Expected |
|---|---|---|---|
| A's context + only high-cosine windows appended | no: Brazil/Russia, Baikal and Kenya had no or weak A context, so the same windows get appended | no | ≈ rv2 without the 3 losers ≈ +0.007 |
| rv2 with Q450-sized passages (120 words, 340 budget) | maybe Baikal (Q450 +0.5), not Kenya (Q450 −1.33) | no (same article choice) | small |
| better article/passage choice | — | the only route to Q450's +18.7, but 3 designs (exp-33 B/C2, rv2) haven't reached its passages | unknown, multi-day |

**→ Park.** The bounty number is more likely to move from the model/answer side (front 1) and the V-exact item fixes than from more v0.1 retrieval work.

## What stays useful
- The fast replay harness, goldhit.py, and the lesson "gold-in-context ≠ judged gain" (E1(a) vital5, exp-35 rv2).
  - Future retrieval L0s must also report a harm proxy (items where A answers well from memory and R's context contradicts it).
- **V-exact demo items:**
  - Japan improves (vx-001 +0.25).
  - Gríma is unchanged (1.00): the 4B keeps the false correction even with the killing in context. rv2.2's book-sentence fix is an item-level option only.

## Anvil's hand classification (anvil/exp/oracle/rv2-diag.md, 18 items; agrees with the numbers above)
- **12 losers:**
  - (b) reasoning over numbers in context: Baikal, Brazil/Russia, EIP-4444 "400GB" → "tens of GB";
  - (a) fragment overrides memory: Kenya;
  - (c) off-topic windows: "Quadratic equation" ×2 for quadratic funding; Ruhr/ISRO/Mumbai airport for "bigger than India"; Singapore's kit history passage displaced by 3 language windows → wrong independence date;
  - (e) mostly seed/judge noise: 5 items.
- **6 winners:** all (f), a lead/fact window filled a gap (Kilimanjaro, Moon before 1970, Rio 2016, crocodiles, Montenegro, Sahara).
- **What Q450 has that rv2 lacks:**
  1. the FACET passage (population, languages, independence) from the whole article or a facet sub-article (Demographics of Brazil, Languages of Singapore, Economy of Montenegro). rv2's windows cluster on leads and history;
  2. zero noise;
  3. more words (284 vs 216, p50);
  4. **on 6/18 items Q450's context is web-only** (space.com, Snopes, Gitcoin, travel blogs), out of reach for any pack;
  5. ordering is not the issue: the gold window is rank 1 on 19/25 when present.
- **Two bugs:**
  - reference-list junk indexed as passages in top100k ("Retrieved 3 January 2019. 85. ↑"), a pack-build fix if the pack ever ships;
  - **`citations:added` inserts [n] inside decimals** ("9 [2].4 million"), in the shipping stack too → **fixed in sonar/exp/38-citation-decimal** for Forge.
- **Anvil's suggested next iteration:** facet-aware window scoring, an entity-overlap noise gate, references stripped at build, protecting on-subject kit windows. Anvil offers L0 on the ctx data.
- **Sonar's view:**
  - The facet and noise fixes address mechanism (c) and part of (a). The facet signal is real; "Demographics of Brazil" is a different article that named+BM25 doesn't propose.
  - They don't address (b), the 4B misreading numbers that are present, and they can't reach the web-only items.
  - Upper bound if (c) and the facet misses were all fixed: the 4 (c) items ≈ +2.5 points + the facet winners. Still ≈ +0.01–0.02 on v0.1, at the edge of a 2-seed L1.
  - **Still park.** Revisit only as part of a pack rebuild (references stripped, facet sub-articles indexed) after the bounty.
