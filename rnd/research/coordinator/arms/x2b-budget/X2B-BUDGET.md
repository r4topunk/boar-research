# X2B-BUDGET — verdict NO (gate clauses 3 and 4 fail) — 2026-10-23 18:1x

Criterion X2B-BUDGET-criterion.md (sha in X2B-BUDGET-criterion.sha256, frozen before any replay, unchanged). 0 LLM, 0 judge, 0 paid, MacBook only; tree kiln-local/rs-X2B (rs-SEFIX + X2B-BUDGET.patch, switch RS_X2B_BUDGET). Replays were finished by the 10-23 agent before the 17:4x restart; scoring (tools/score.py -> x2b-budget.json) and this report by the night session.

## Identity
B600 vs retbench base: MAIN kept ids 97/97, ST 180/180, MAIN 42, ST fact chunk 77, TOPICS 24 (P1 holds). Probes vs F3-SAFETY OFF traces (hosts differ): title+source 42/65, title 63/65 (reported only; arm changes are counted vs the B600 probe replay).

## Table
| arm | MAIN facts | ST fact | ST own kept | H40 | class E | TOPICS | MAIN ctx p50 (x) / max | probes changed (dose/number) | health losses | gate |
|---|---|---|---|---|---|---|---|---|---|---|
| B600 | 42 | 77 | 100 | 13 | 0/5 | 24 | 732 (1.00) / 1223 | 0 (0) | 0 | base |
| B900 | 47 (+5) | 88 (+11) | 121 | 18 | 5/5 | 24 | 856 (1.169) / 1387 | 12 (9) | 0 | FAIL (3, 4) |
| B1200 | 47 (+5) | 90 (+13) | 122 | 18 | 5/5 | 24 | 862 (1.178) / 1470 | 12 (9) | 0 | FAIL (3, 4) |
| BINF (ref) | 47 | 90 | 122 | 18 | 5/5 | 24 | 862 (1.178) / 1470 | 12 (9) | 0 | not a candidate |

MAIN gains (B900): st-qa-cooking-se-004, -020, st-qa-money-se-014, -016, vit-cry-010; 0 lost. ST gains: factbook-001, -014, the 5 class-E items, ethereum-015, outdoors-017, travel-008, -020; 0 lost.

## Why it fails
- Clause 3: context p50 1.169x (B900) and 1.178x (B1200) vs the 1.15x guard (max + 1024 stays far under 4096).
- Clause 4: 12 probe kept sets change, 9 of them dose/number (h02 h15 h19 h21 h23 h24 h26 h27 n06). Every change is an ADDED appended chunk (0 dropped), several off-point for a health-strict turn: "Eating Matches to repel insects?" (h19), "Boy" (h23), "How often is X times a day?" and a washing-water SE answer (h02), "Will there be problems bringing an ointment" (n06). P4 (probes do not change) is wrong: the budget acts on chunks the health filter already let through, and a looser budget lets more of the SE-lead / dense tail in.
- 900 already reaches the BINF ceiling on MAIN (+5): the gain is the 4-chunk cap, not the budget size.

## Reading
The lever is real on delivery (+5 MAIN, +11 ST, all five class-E misses recovered, 0 health losses) but by the letter it is NO, and it does not join ENGINE-RC. A follow-up (not tonight: NIGHT-2026-10-24 forbids new research arms) would be a budget raise only on non-health turns (health-strict turns keep 600), which would leave the probes untouched by construction and must still pass the 1.15x context guard (non-health ctx growth would need its own check). Stage 2 not run, Haiku 0.
