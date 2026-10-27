# v2-fresh status: DEV since 2026-10-03 (after the B6 confirm run)
TL;DR: v2 was spent as the confirm set for B6. **B6 PASSED**: acc 55/57 (bar ≥ 52), missed-search 0/23, safety items missed 0/7 (Kiln; rescored by Compass with the frozen scorer: identical). Kiln and Compass have seen its item-level errors, so **v2 is now development data**, like v0 and v1, and can never be a confirm set again. A next confirm would need a v3-fresh set.
- Frozen files are unchanged (FROZEN.sha256 verifies). Runs are in `runs/{b6gate,main}/`.
- Safety read of the 7 safety replies: `runs/b6gate/safety-read.md`.
- Dev use so far: chat-slice v2-039 drove a heatstroke trigger term ('no suda' / 'não está suando'; first-aid-cards/triggers.proposed.mjs).
