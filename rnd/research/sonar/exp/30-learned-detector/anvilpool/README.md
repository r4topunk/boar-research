# v3b on Anvil's emergency-gate pool (599, non-blind; anvil/exp/emergency-gate/pool.json), 2026-10-03
HF v3b, the shipped input builder, thr 0.2; engine = det OR (broad regex AND p ≥ 0.01) OR isCardEmergency OR isHealthFollowUp. Gate rows: arm/l0-b6e.jsonl (set=pool).

| on 599 | EMERGENCY recall (185) | NOT false fires (391) | hard-neg (40) | HEALTH_INFO fired (23) |
|---|---|---|---|---|
| lexical health9 | 121 | 10 | 10 | 4 |
| B6E gate alone | 179 | 1 | 0 | 0 |
| B6E arm (gate|card|fu) | 180 | 1 | 0 | 0 |
| v3b engine (det|regex&p>=.01|card|fu) | 182 | 2 | 0 | 1 |
| union | 184 | 3 | 0 | 1 |

- v3b misses: dng-005-ptm (flood tap water, PT), vit-loc1-016 (minimised monkey bite), vit-loc1-028 (typhoon evacuation with conflicting advice). 
- **Correction (Anvil, 2026-10-03):** the first version of this table read the gate's `em` probability as a boolean (any p > 0 = fire): 185/18/7. Wrong. The gate decision is the boolean `emergency` (em ≥ 0.5). Corrected above.
- Caveat: the pool overlaps Sonar dev sources (night, v0.1, chat-v0), which were used to pick v3b's threshold but not to train it. The **B6E prompt was NOT tuned on this pool**: it was hash-registered (anvil prompts/PREREG.sha256, 10:47) before any score on it. The pool is in-sample only for Anvil's label spec.
