# v1-fresh status: DEV since 2026-10-03 00:13 -03
TL;DR: v1 was spent as the confirm set for B5 (FAIL: acc 51/57 vs bar 52; missed 1/23 and safety 0/7 pass). Kiln and Compass have seen its item-level errors, so **v1 is development data now**, like v0. It may be used for tuning and read by anyone (the coordinator decides when to open it to Anvil). It can never be a confirm set again. The next confirm set is `../v2-fresh/` (frozen, Anvil-blind).
- Frozen files are unchanged (FROZEN.sha256 still verifies). The B5 and main runs are in `runs/`.
- Safety read of the 7 safety replies (B5 run): `runs/b5gate/safety-read.md`.
