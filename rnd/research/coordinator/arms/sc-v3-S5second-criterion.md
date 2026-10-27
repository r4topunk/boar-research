# SC v3 trigger — S5″ criterion (frozen 2026-10-04, before set #4 exists; DEV)

S5′ (set #3) FAILED: recall water 21/25, snakebite 21/25 (pass); false fires 5/50 vs bar 2 (categories: explicit no-bite,
pet victim, backcountry stream filtering, boil-advisory history, treatment-plant how-it-works). Set #3 is burned for SC.

v3 guards (general, not item-specific): explicit no-bite negation; non-human victim (pet/livestock without a human victim
cue); water card only for a present need (a person or how-to/can-I/is-it/imperative ask) and never history, how-it-works /
utility process, or backcountry/backpacking trips; a creek/stream/river alone is no longer an emergency context.

Trigger under test, frozen at commit db7406c9 (worktree wt/cut3-dev, branch coord/cut3-dev), sha256:
- src/routing/waterSafety.ts      032c8ab2480501367c4702aba4c579c2d6fc160e402eb567ca9ab10bf0b92575
- src/routing/firstAidCards.ts    93ee13f15e54f1c4a052be60cfbafe33f9374fafcfc32006e3e35f47c1afe836
- src/routing/conditionCards.ts   5c4b5334560e1b00df42cac0bc2d034065d39650e1723ea80a9b81675b4509bc
(Card text lives in safetyCardText.ts; text-only edits do not change these three hashes.)

Set #4: written blind into arms/sc-fresh4/*.jsonl, fields id, text, expect_card ∈ {water, snakebite, none}. Never read by the
engineer. Scored ONCE with tools/sc-fresh4.mts (refuses to run on a hash mismatch); no tuning after. This is the last round.

Bars (identical to S5′): water recall ≥ 80 %; snakebite fast-path recall ≥ 80 %; false fires ≤ 1 per 25 expect_card = none
items (a water/snakebite card on an item that doesn't expect it, swaps included). Card order = engine fast path (snakebite,
CO hazard, water).

Dev checks at freeze (sc-v3-dev-result.txt): water FF 0/1,703; dev paraphrases 22/22, 0/18 FF; emergency-dev water fires 0/180;
snakebite 0 positives lost vs cut 2 on 6,847 messages, new fires / condition changes identical to v2 (all real bites).
Burned for this trigger: dev paraphrases, S5 set, set #3 (via its 5 category descriptions).
