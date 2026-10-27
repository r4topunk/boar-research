# SC (safety-fact cards: water safety + snakebite completion) — L0 criterion (frozen before any run; DEV only)

Source: 4B-LOSS-ANATOMY.md, "Arm draft 2: SC". Deterministic, no generation, no judge.

## Under test (engine)
- `isWaterSafetyQuestion(q)` + the water-safety card (fast path next to the CO hazard card, EN only, label
  `Safety facts (CDC)`, reason code `answer:safety-fact-water`). Text in `src/routing/safetyCardText.ts` only.
- The EN snakebite card text (same file); trigger (`isSnakebiteFirstAid`, conditionCards `snakebite`) unchanged.

## Sets (read-only)
- v0.1 EN public (60): dng-005 must fire.
- Paraphrases by a fresh subagent: arms/probes/water-safety.probes.jsonl (22 pos / 18 hard neg). The engineer read them
  before writing the trigger, so they are DEV (optimistic). A second fresh subagent writes
  arms/probes/water-safety.heldout.jsonl AFTER the trigger is frozen (sha256 recorded in CUT3DEV.md); scored once.
- False-fire pools: Sonar aligned-en (1010) + terse-live EN (213) + Compass emergency-dev EN (105) = 1,328; the CO-hazard
  L0 sets and lookalikes (compass/exp/co-hazard/lookalike.{dev,heldout,heldout3}.jsonl); Compass chat-slice v0/v1/v2 EN;
  v0.1 EN minus dng-005.
- Wrong-card: Compass emergency-dev, all items with emergency = 1 (Sonar's 180-emergency set as used in exp-37).

## PASS bars
- S1. The water card fires on dng-005 and on ≥ 10 dev paraphrases (boil advisory, hurricane, outage, well water).
- S2. 0 false fires on the 1,328 EN dev messages, on the CO lookalike sets, on chat-slice EN and on v0.1 EN minus dng-005;
  ≤ 1 false fire on the 18 dev hard negatives.
- S3. 0 new wrong-card on the emergency-dev emergencies: no emergency message that the water card takes away from
  another card or route (any water-card fire there is listed and must be a drinking-water question).
- S4. Snakebite trigger set unchanged: `isSnakebiteFirstAid` and conditionCards are byte-identical in logic; the card fires
  on the same messages of all pools above before/after (diff = 0).
- S5. Held-out (scored once): recall ≥ 80 % on positives, false fires ≤ 1 on negatives.
- S6. Reviewer verdict APPROVE on arms/sc-cards-REVIEW.md (independent Opus reviewer, coordinator-run). Pending until then.

Verdict = PASS on S1–S5; S6 pending.
