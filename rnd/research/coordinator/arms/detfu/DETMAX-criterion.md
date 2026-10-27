# DETMAX criterion (frozen 2026-10-06, after DETFU, before any code)

DETFU (rnd 583fec1): split-turn emergencies are fine (S1/S2 0/60 lost: the detector window includes earlier user turns), but history DILUTES the score: S3 "Hi, quick question." + probe dropped ed-en-049 from 0.554 to 0.049 (route lost); ed-en-016 and dng-005 fell below 0.2 and survived only via the lexical floor.
Arm = cut 5 + one rule: when the conversation has earlier user turns, score the detector on (a) the current window as today AND (b) the current user turn alone; fire if either ≥ the existing threshold. Single-turn behaviour unchanged by construction. No threshold, model or lexical-list change.
Gates:
G1 build: patch vs 0cfd4a77 applies to a fresh archive, tsc clean, tests pass, new tests for the max rule.
G2 v0.1 EN s44 text/tier/passages/reasons identical 60/60 vs same-day cut 5.
G3 S3 (DETFU's set) 0/60 mismatches; plus held-out prefixes frozen here, never used before: P ∈ {"Thanks for the help earlier.", "Different topic now.", "Ok so I have another question."} + probe → 0 mismatches vs standalone (60 probes × 3).
G4 false fire: on the 192 dev chat messages, emergency/danger routes added by the arm vs cut 5 ≤ 2, each listed; any added route must also fire when that turn is sent standalone (by construction — verify).
G5 cost: extra detector calls only on turns with history (count); desktop detector time per extra call reported.
Dev only; never blind/, rnd/veil/, health-fresh*, chat-v3. Builder may read this file (no hidden set beyond P, which cannot be tuned since the rule has no free parameter).
