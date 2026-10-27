# X2B-OFF-MAIN criterion addendum 2 (frozen 2026-10-21, format only)

Addendum 1 (sha256 af0235a6..., commit 031cf1b9) declares the Opus step under "## Budget" (opus_clause), but _lib/preflight.py reads opus_clause from a "## Precheck" block, so the preflight refused (opus_on_dev) before any call.
This file restates addendum 1's Opus clause and caps in the blocks the preflight reads. No rule, set, cap or decision changes. Used as PREFLIGHT_CRITERION for step 1 only.

## Precheck
opus_clause: addendum 1 step 1 only: Opus judge.v1 on the 9 seed-42 CEu-flip items (dev MAIN), ON and OFF, 36 calls, to settle a borderline Haiku CE clause.

## Budget
calls_cap: Haiku 160 / Opus 36
opus_clause: addendum 1 step 1 only (9 items, both arms).
