# V-0 result (protocol 0eb7cc82…, labels 3584ede6…, run 19:5x 2026-10-02): FAIL
- Flags on positives **3/9** (need ≥ 7): vit-sci-002 ×3 (explicit "Japan is actually more densely populated"). Missed: lan-ref-003 ×3 ("No… before 1970" vs "1969"), lan-cmp-003 ×3 ("No country is bigger" vs "seventh-largest").
- False flags **0/21**; parse failures 0/30.
- Latency (M1, Metal, fresh context, ~120–200 prompt tokens): 0.30–1.0 s per check.
- Reading: the 4B catches a contradiction only when a later sentence states the opposite outright. It misses ones that need one inference step (a date comparison, an ordinal implying a count). Precision is perfect, but recall covers the easy third only.
- Not tried (would be tuning on the 9): other wordings, reasoning before the YES/NO. A "reason, then answer" check turn belongs to Anvil's test-time-compute lane, and would cost more tokens on the phone.
