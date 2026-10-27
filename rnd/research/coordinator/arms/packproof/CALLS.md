# PACKPROOF call ledger (cap Haiku 400, Opus 0, paid 0, phone 0; criterion 37f74d6f)
| time | what | Haiku calls | running total |
|---|---|---|---|
| 12:23-12:27 | MacBook identity check, 5 sefix124 items (generation only; kept 5/5 identical to the mini) | 0 | 0 |
| 12:44 | coordinator parallelism note: OFF arm (8 groups, 180 gens) + a 5-item host identity check moved to the mini (tools/run_mini_off.sh, job pp-off-s42, kiln slot lock, same recipe, same GGUF sha b139949c); ON arm stays on the MacBook. MacBook OFF dirs hold placeholder STATUS files so the MacBook driver skips them | 0 | 0 |
| 12:51-13:2x | A labels, ON on-k13 140 units (ONLY_A=1; a first non-A start was killed after 27 rows, up to 4 in-flight calls may be unlogged) | 140 | 140 |
| 12:56-13:14 | mini OFF arm ran (slot gen1): ident 5/5 kept identical to the mini sefix124 traces, 8 OFF groups 180/180 rows, 0 errors | 0 | 140 |
| 14:10 | coordinator session restart killed the MacBook driver (ethereum ON at 6/20) and the label process at 309 rows; MacBook scratch tree/wrapper/detector script lost. Ethereum ON group re-run whole on the mini (tools/run_mini_eth.sh, job pp-on-eth-s42, 14:13-14:15, 20/20); the 6 MacBook rows kept aside in gen/x-macbook-partial-on-eth, unused | 0 | 309 |
| 14:1x | A labels: remaining 7 OFF units + 20 ethereum ON units | 27 | 336 |
| 14:1x | B rechecks (borderline, passages reversed): 59, stopped at the 395 guard; C calls 0 (3 skipped at cap), so 11 A/B disagreements keep A (flagged ab_disagree_noC) | 59 | 395 |
Total logged 395 of 400; 0 errored rows. Up to 8 in-flight calls killed by the two process stops (12:51 restart to ONLY_A, 14:10 session restart) may be unlogged. Opus 0, paid 0, phone 0.
