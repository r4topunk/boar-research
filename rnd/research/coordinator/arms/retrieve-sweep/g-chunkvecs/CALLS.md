# Arm G stage 2: call ledger (cap: Haiku 400, Opus 0, paid 0, phone 0)
| time | what | Haiku calls | running total |
|---|---|---|---|
| 00:49-01:00 | generation 2 x 216 items on the mini (local llama-server, no API) | 0 | 0 |
| 01:1x | judge pass 1: CTL + ARM answers of the 84 changed-context items whose answers differ, forms F0 F1 F2 F3 F5 F6 F7 (84 ids x 2 orders x 2 arms), Haiku 5.5-low N 4 | 336 | 336 |
| 01:2x | judge pass 2: the 16 F4 items of the same set (16 x 2 x 2), same judge | 64 | 400 (cap 400; Opus 0, paid 0, phone 0; 0 retries). Not judged: 11 F8 answer-differing items (cap), 18 changed-context items with identical answer text (dU 0 by construction) |
