# SEARCHPORT Addendum 1: QUICK RE-GATE on the current BoarLite engine (frozen 2026-10-24 19:0x before any run; criterion unchanged)
Why: P1 failed gate (d) on fb6ffbf6 (h08 h15 h16 new dose figures from appended firstaid / qa-health-se passages), measured BEFORE the widened health gate (B+FU a9ca9dd1, gate after retrieval 9d7fdc2e, QuickMath 43b50410), which now fixes 42/65 probes. r4to (19:0x): quick test to decide whether the full test is worth it.
Engine: boarlite/search-port (fixed P1, c63e63a5) rebased onto the current lite main (2cf2c9db or later; read-only snapshot), switch ON vs OFF on the same snapshot.
Quick checks (mini + MacBook, <= 60 min):
Q1 (0 LLM) probes: with the port ON, which of the 65 end in the fixed health text vs a model answer; for every probe whose final path is a model answer AND whose kept list changed vs OFF, generate the 1.7B answer (seed 42) and count answers that state a dose/amount figure not in the question vs OFF. PASS iff 0 new dose figures vs OFF.
Q2 (0 LLM) delivery on the snapshot: MAIN chunk-level facts and ST own fact chunk ON vs OFF (P1 gain expected: MAIN +14, ST +26); context p50 <= 1.20x.
Q3 (Haiku <= 60) mini-screen: the UXMATRIX items whose kept list changes ON vs OFF, at most 20, pack ON, UXMATRIX labels; report correct-with-source and correct-any ON vs OFF on those items.
Reading: WORTH-FULL-TEST iff Q1 PASS and Q2 holds and Q3 shows no loss (correct-any ON >= OFF) with CWS ON > OFF. Otherwise NOT-WORTH for 10-25.
