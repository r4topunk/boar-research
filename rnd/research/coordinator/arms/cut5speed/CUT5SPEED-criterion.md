# CUT5-SPEED criterion (frozen 2026-10-06, before any run)

Motivation: coordinator/device/A15-LATENCY-BUDGET.md (warm A15 p50 68.7 s; projected 54.4 s with the 3 changes below).

Arm = cut 4 final (coord/instsubj, patch d51e844c…) + three latency-only changes:
1. Forge retrieval perf arms (forge/SHIP-SPEED.md, forge/arms/ship/forge-ship.patch): native zstd / vector cache / sqlBatch, whatever applies cleanly to cut 4. Plus per-stage retrieval timing in the trace (`retrievalStages`) so the phone can measure it.
2. Second KV prefix: the static no-source system message gets its own session key + save/restore (token-identical prompt).
3. Route-gate skip when ruleTaskType ∈ {lookup, research, compare}, no detector fire, no history, not about BOAR. Otherwise the gate runs as today.

No prompt text, retrieval result, model, sampling or answer-length change is allowed.

## Gates (all must pass to ADOPT as cut 5 = device-day candidate)
G1 Build: patch applies to a fresh `git archive 0cfd4a77`; tsc clean; all unit tests pass; new tests cover (2) key derivation + mkdir and (3) skip/no-skip decisions.
G2 Identity: v0.1 EN s44 + s45 on the Mac mini (node backend, same config as cut4-L1), arm vs same-day cut 4 control: answer text identical on ≥ 119/120 items, tier identical 120/120, retrieved passage ids identical 120/120. Any text difference must be explained as run-to-run noise by a control-vs-control rerun of that item. No judge calls.
G3 Speed (desktop, descriptive + gate): retrieval wall time (sum over items, node backend) arm ≤ 0.8 × control. Report per-stage ms.
G4 Gate-skip safety (deterministic, dev only, no blind): on the v0.1 EN items + the dev chat/small-talk probes available outside blind/ and rnd/veil/, list every message where the gate would be skipped; skip must never fire on small talk, greetings, thanks, questions about BOAR, or emergency/detector-fired messages (0 violations).
Stop rule: if G2 fails for a non-noise reason, drop the offending component and re-run once with the rest; report which component was dropped.
