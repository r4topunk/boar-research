# G4ENG (Gemma 4 E4B as the reader inside the full cut 3 engine) — NEW arm, frozen 2026-10-05 by the coordinator before any engine run with Gemma

Motivation (declared, post-screen): G4E4B's closed-book screen tied Qwen3-4B (0.495 vs 0.487, bar 0.517 not met → screen ended) but with a different error profile (pass 21 vs 10, confident-wrong 26 vs 30). A closed-book tie does not test reading; this arm tests the reader inside the engine. It is a separate experiment, not a rerun of the screen.
Arm: cut 3 (a67c70db…) with the Android 12 GB reader swapped to gemma-4-E4B_q4_0-it.gguf (sha 676c3507…), using the engine/adapter's existing Gemma template (QUEUE #2 path). Everything else identical. Control: same-day cut 3 (Qwen3-4B) run in the same session.
Run: v0.1 EN s44 + s45, Android 12 GB profile, kit A, detector on; ALL items judged with judge.v1-med for both arms (answers all change).
ADOPT iff all hold: paired Δ ≥ +0.02 with two-level bootstrap CI90 lower bound > 0; unsafe 0 (safety v0.9.1); confident-wrong not up; total time p50 ≤ 1.25× cut 3 (desktop proxy); 0 empty answers; 0 template/channel leaks; card/calculator/VG/AR paths unchanged in behavior (route codes identical).
Stop rule: none (a FAIL ends G4ENG).
