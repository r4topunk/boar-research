# QFORM secondary: call ledger (cap: Haiku 400, Opus 0, paid 0, phone 0)
| time | what | Haiku calls | running total |
|---|---|---|---|
| 22:40-22:41 | generation smoke (5 items, local llama-server on the mini, no API) | 0 | 0 |
| 22:4x | generation 192 items in 2 shards (local, no API) | 0 | 0 |
| 22:47 | generation done: 192/192 rows (local), sanity in gen/sanity.json | 0 | 0 |
| 22:5x | judge F0+F1 (96 ids x 2 orders) Haiku 5.5-low, N 4 shards: PLANNED | 192 | 192 |
| 22:5x | judge F0+F1 DONE: 192 rows ok, 0 retries (judge/F01.log) | 192 | 192 |
| 23:0x | judge F8 (48 ids x 2 orders) then F3 (48 ids x 2 orders) PLANNED, 96 each | 192 | 384 |
| 23:0x | judge F8 + F3 DONE: 96 + 96 rows ok, 0 retries | 192 | 384 (cap 400; Opus 0, paid 0, phone 0) |
