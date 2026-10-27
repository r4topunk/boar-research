# Premise guard (EN): pre-registered L1 (Compass 2026-10-03, before any probe answer exists)
Delta: `premise-guard-delta-vs-cut2.patch` (on cut 2 7931b9a8). The guard is a pure post-generation step in the uncited-knowledge branch, so the L1 = cut 2 4B answers (s42, s43) to `probes.jsonl` (20 false-premise + 20 true-premise questions, written by Compass) replayed through `premiseGuard` offline. Changed answers are hand-read by Compass.

L0 (done): over 2,267 non-blind 4B traces (746 uncited knowledge answers), the guard acts only on vit-hum-004 (Gríma: decline) and vit-hum-002 (Mencius "did not directly attack": clause or sentence removed); every action removes a false premise denial.

KEEP iff all of these hold, in both seeds:
- **B1:** V-exact vit-hum-004 on cut 2 is declined.
- **B2:** On true-premise probes, the guard never changes an answer that affirms the premise. Acting on a false denial is a success.
- **B3:** On false-premise probes, the guard withholds or cuts a CORRECT correction on ≤ 1 item per seed.
- **B4:** No other change in the L0.

Otherwise KILL. There is no judged run: the changed V-exact and v0.1 items are only 002 and 004, and a decline replaces a false answer.
