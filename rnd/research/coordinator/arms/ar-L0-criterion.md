# AR (arithmetic tools + health-detector numeric guard) — L0 criterion (frozen before any run; DEV only)

Source: 4B-LOSS-ANATOMY.md, "Arm draft 3: AR". Deterministic, no generation, no judge.

## Functions under test (engine `src/routing/arithmetic.ts`)
- `arithmeticAnswer(question)`: (1) rate × quantity -> time ("N units at R units per second/minute/hour", one or two
  phases), (2) ceil-division ("how many X of size S for T"). Constants only from the question. EN only; never on
  PT/ES, never when the message has a symptom/injury/medication term.
- Numeric guard: when the learned detector fires on a message that `arithmeticAnswer` answers, the calculator answers
  (reason code `detector:numeric-guard`) instead of the health route.
- The staking-validator variant with constants from a pinned passage (vit-cry-009) is in the draft; it fires only if the
  constants are in the retrieved context.

## Sets (read-only)
- v0.1 EN public questions (60): boar-eval/bench/v0.1/questions.public.jsonl
- Probes written by a fresh subagent before the code existed: arms/probes/arithmetic.probes.jsonl (30 pos, 15 neg).
  NOTE: the engineer read these before writing the patterns, so they are DEV (optimistic).
- Held-out probes: a second fresh subagent writes arms/probes/arithmetic.heldout.jsonl AFTER the code is frozen
  (sha256 of arithmetic.ts recorded in CUT3DEV.md before scoring); scored once, no tuning after.
- Non-arithmetic EN dev messages: Sonar aligned-en (1010) + terse-live EN (213) + Compass emergency-dev EN (105) +
  Compass chat-slice v0/v1/v2 EN items (never *-blind) + v0.1 EN public except vit-sci-003 / vit-cry-009.
- Detector guard recall: Compass emergency-dev v1, all 300 items (rnd/research/compass/exp/emergency-dev/dev.jsonl).

## PASS bars
- A1. vit-sci-003 is answered by the calculator with 1,300/30 ≈ 43.3 s + 400/10 = 40 s ≈ 83.3 s.
- A2. vit-cry-009: 312 (16 ETH left over) or 313 before, and 5 after. (Draft bar; fires only with the constants in context.)
- A3. ≥ 30 positive unit problems (unit tests + dev probes) give the exact expected number; 0 fires with a wrong number.
- A4. 0 fires on the non-arithmetic EN dev messages (≥ 1,000) and on the 15 dev-probe negatives.
- A5. Numeric guard on emergency-dev (300): 0 items where the guard would apply (0 recall loss); false fires cannot go up
  (the guard only removes health routes).
- A6. Held-out probes (scored once): 0 wrong numbers; false fires ≤ 1 on its negatives; recall reported.

Verdict = PASS if A1, A3, A4, A5, A6 hold. A2 is reported separately (constant availability, see CUT3DEV.md).
