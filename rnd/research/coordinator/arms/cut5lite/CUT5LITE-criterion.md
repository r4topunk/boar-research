# CUT5-LITE criterion (frozen 2026-10-06, after CUT5-SPEED; post-hoc arm, declared as such)

Why: CUT5-SPEED (ab05007f…, report CUT5SPEED.md, rnd 8300247) failed G3 because desktop node cannot see the phone costs the Forge perf arms remove (bridge, native zstd); the stack was 1.07× slower on desktop. The other two components passed G1/G2/G4 and do not depend on the perf arms. The perf arms move to a device-only A/B (kill switch EXPO_PUBLIC_BOAR_PERF=none) and are NOT in this arm.

Arm = coord/instsubj (cut 4 final, d51e844c…) + only the CUT5-SPEED commits c66fb4f5 (second KV prefix `.nosrc`) and 3658379f (route-gate skip with the tightened guards), cherry-picked; no other change.

Gates (all must pass → cut 5 = device-day candidate):
G1 patch vs 0cfd4a77 applies to a fresh archive; tsc clean; all unit tests pass.
G2 Mac mini, v0.1 EN s44+s45, node backend, same-day cut 4 control: answer text, tier and retrieved passages identical 120/120 (a text diff only allowed if a control-vs-control rerun shows the same item drifting). No judge.
G4 the CUT5-SPEED deterministic gate-skip check re-run on the same 464 dev messages: 0 violations.
G5 retrieval wall time arm/control ≤ 1.03 (no slowdown).
No retuning of the skip guards in this arm.
