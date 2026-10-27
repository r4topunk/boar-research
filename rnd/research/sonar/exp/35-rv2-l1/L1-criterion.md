# L1: retrieval v2 ("CLEAN min") vs the current ship kit, 2 seeds (Sonar, frozen 2026-10-03 night, before any rv2 run)

TL;DR:
- **rv2** changes how English non-health questions get their context:
  - article candidates = the Wikipedia articles the question names (share ≥ 0.25) + the BM25 top 4, at most 8;
  - each gives its lead chunk + its best chunk for the question;
  - the other sources keep their retrieved passages;
  - everything is cut into ~45–60-word windows, ranked by bge-small cosine to the question, floored at 0.5, and filled to 240 words;
  - this replaces compression + the term-coverage topic gates.
- Health, history, PT and multipass keep the classic path; the crypto-source guard stays.
- **L0** (fast replay, real engine, stub LLM; sonar/exp/34-gold-hit): gold sentence in context on v0.1 EN rises **7/56 → 18/56** (+11 / −0) against bounty1 + the same kit.
  - Health/card items: identical contexts (5/5).
  - Unit tests: 670 pass + 3 new. The 1 failing test (`wikiPack.destination`) fails identically on bounty1.
- **Decides:** whether rv2 + top100k goes into the EN ship candidate (then L2/L3).

## Frozen inputs
| What | Value |
|---|---|
| Arm A (control = current ship engine) | 0cfd4a77 + `bounty1-engine.patch` 2994a90b… (sonar/exp/31), kit A (boar-crypto ae9fbd2c…, boar-wikivoyage-en ff8595e3…). s42 = exp-33's `bigpack-A-s42` (reused); **s43 new** |
| Arm R (rv2) | 0cfd4a77 + `rv2-engine.patch` **dc9c6d9131ddfe36cf61bcf28d0b834aa9cc5911d1c14cd6ab204a9b370e1ceb** (= bounty1 + rv2; delta `rv2-on-bounty1.patch` 224c3867…; rebuilds byte-for-byte from `git archive 0cfd4a77 src`). Kit A + `boar-wiki-en-top100k` 9123b372…. **s42 and s43** |
| Runner, detector, places | as exp-33: health11-runner e4882a95…, detector env as in the health11 confirm, `--places` kit-vexact, `--event-source-text` |
| Items | exp-33's request set: V-exact 11 + v0.1 public EN 57 (65 requests) |
| Judge | judge.v1 (opus, both orders), refs as exp-33 |

## Metrics and decision (R vs A, pooled over s42 + s43)
1. **v0.1 EN:** paired ratio Δ (R − A), per-item mean over the 2 seeds, bootstrap 90% CI by item.
2. **Safety:** unsafe items (v0.8.7), summed over seeds.
3. **V-exact knowledge items** (vx-001, vx-002, vit-hum-001, vit-hum-004): judged score per item, mean of seeds.
4. **Retrieval time:** desktop p50 ratio R/A, reported. Phone estimate (Forge): +1.0–1.3 s at 2 threads.
5. **L0 on the real run traces:** gold sentence in context (goldhit.py), reported.

**GO (rv2 into the EN ship candidate → L2):** all of
- Δ ≥ +0.02 and the CI90 lower bound > 0;
- unsafe R ≤ A;
- no V-exact knowledge item worse by ≥ 1 judge point.

**KILL:** Δ ≤ 0, or the CI90 upper bound < +0.02.

**Otherwise:** one more seed pair (s44, both arms), then the same rule on 3 seeds.

## Expectation (stated before the run)
- **Gain:** +0.02 to +0.05 on v0.1 EN. Anvil's Q450 (gold articles + question-chosen passages) is +0.07 over the engine, and rv2 reaches 18 of Q450's 50 gold-sentence items at L0.
- **Risk:** without the term-coverage gates, an off-topic window above cosine 0.5 can reach the prompt. The safety and judge numbers catch that.
- **Neutral:** venue, travel-calculator and health items (classic path).

## Note (2026-10-03 night, after freezing; criterion unchanged): rv2 transfers to Forge's cut 2
- **cut2-rv2** (shipcut2-rv2.vs-0cfd4a77.patch 645a68ea…; = cut 1b + co-exposure2.1 + rv2-on-bounty1 224c3867) on the fast replay, kit A + top100k:
  - placed contexts identical to the tested rv2 tree on **64/65**; gold sentence 18/56 = rv2's.
- **cut2-norv2** vs bounty1: identical on 64/65; gold sentence 7/56.
- The single difference in both pairs is vit-trv-004 (Paris–Rome), from Forge's travel-calc component, not rv2.
- So this L1's verdict on rv2 applies to the cut2-rv2 variant.
