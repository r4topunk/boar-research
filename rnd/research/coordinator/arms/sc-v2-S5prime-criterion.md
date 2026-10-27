# SC v2 trigger — S5′ criterion (frozen 2026-10-04, before set #3 exists; DEV)

Trigger under test, frozen at commit 02406703 (worktree wt/cut3-dev, branch coord/cut3-dev), sha256:
- src/routing/waterSafety.ts      18444303431d3a098484152b3dad892a90d57741207a87267779e54514db3b2a
- src/routing/firstAidCards.ts    2682556f30b716b7baa1e2437b62eb83a1a050b832a6401846eaeed7f027b1f4
- src/routing/conditionCards.ts   5c4b5334560e1b00df42cac0bc2d034065d39650e1723ea80a9b81675b4509bc
(card text safetyCardText.ts 3f351db3… unchanged; it awaits the reviewer.)

Set #3: written by a separate blind writer into arms/sc-fresh3/*.jsonl, fields id, text, expect_card ∈ {water, snakebite, none}.
The engineer never reads it. Scored ONCE with tools/sc-fresh3.mts (it refuses to run if any trigger sha256 differs); no tuning after.

Card prediction = the engine's fast-path order: snakebite card, then CO hazard (EN), then water card (EN); else none.

PASS (S5′) iff all hold:
- water recall ≥ 80 % on expect_card = water;
- snakebite recall ≥ 80 % on expect_card = snakebite (fast-path card);
- false fires ≤ 1 per 25 expect_card = none items (a water/snakebite card on an item that doesn't expect it, swaps included).

Disclosures: the S5 set (probes/water-safety.heldout.jsonl) and the dev paraphrases were used to tune v2 and are burned for this
trigger (v2 on S5: 25/25, 0/25 FF — not evidence). Dev checks kept: 0/1,703 water false fires, 0 wrong cards, 0 lost snakebite
positives (fast path or condition) on 6,847 messages; every new snakebite fire / condition change is a real snakebite
(sc-v2-dev-result.txt).
