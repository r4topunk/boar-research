# LOOP-LOG fixture for lanes-tests.sh T-L3 (NOW = 2026-10-16 08:00, last 24 h = 10-15 08:00 .. 10-16 08:00)
2026-10-14 09:00 T1 main PASS old: before the 24 h window | mini=idle mac=idle | H/O=+9/+9 | next=none
2026-10-15 10:00 T2 main PASS armA: first result for A | mini=job1 mac=idle | H/O=+3/+1 | next=armA@11:00
2026-10-15 11:00 T3 main FAIL armB: B is closed because the gate failed on the slice | mini=idle mac=job2 | H/O=+2/+0 | next=armC@12:00
2026-10-15 12:00 T4 main META weekly: planned the week and the judge calls against the ledger for Monday | mini=idle mac=idle | H/O=+0/+0 | next=none
2026-10-15 13:00 T5 main PASS armA: second result for A | mini=idle mac=idle | H/O=+1/+4 | next=none
