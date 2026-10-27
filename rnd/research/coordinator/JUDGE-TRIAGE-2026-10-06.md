# Judge triage protocol (decided 2026-10-06 by r4to: "ficamos com o sonnet")

Calibration on the DEEPREAD answers (deep35 R450, v0.1 EN 57 items, both orders, same prompt judge.v1, same refs), Opus 5.5 judge.v1 as reference:
| judge | same winner | r (BOAR score) | κ correct ≥ 4 | ratio (Opus 0.634) | median s/call | 114 calls |
|---|---|---|---|---|---|---|
| Sonnet 5.5, effort low (`judge.v1-sonnet-low`) | 54/57 (95%) | 0.93 | 0.68 | 0.597 (−0.04 systematic) | 3.1 | 11 min |
| Sonnet 5.5, effort medium (`judge.v1-sonnet-med`) | 55/57 (96%) | 0.945 | 0.62 | 0.601 (−0.03) | 3.3 | 12 min |
| Haiku 4.5 (stopped at 46/114; 23 paired items) | 23/23 | 0.90 | 0.59 | 0.600 | 21.1 | slower: structured-output retries |
| Opus 5.5 judge.v1 | — | — | — | 0.634 | 5.1 (13 incl. gap) | ~25 min |

Rules:
1. **Direction tests (L1):** Sonnet-low, both orders, on the 20-item signal slice (items the 4B gets ≤ 3/5 on v0.1; list frozen in arms/signal20.ids) or on changed items only. Paired comparisons only; the −0.04 offset cancels. ≈ 40 calls, ≈ 4 min.
2. **Confirmation (L2):** Opus judge.v1(-med) on the full 57, 2 seeds, only for a winner at L1. Never mix versions in one number.
3. **Claim numbers:** Opus only, as before.
4. judge.mjs flags: `--judge-model sonnet --effort low --gap-ms 1000`; version tag is automatic (`judge.v1-low` by the script's naming → record as sonnet-low in the system name).
5. Haiku: not used (slower and unverified).
