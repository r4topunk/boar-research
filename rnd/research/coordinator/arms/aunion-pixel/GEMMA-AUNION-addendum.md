# GEMMA-AUNION addendum to AUNION-PIXEL-criterion.md (frozen 2026-10-21, before the run)

Run: gemmaa73-a = gemma73-a request with requestId changed (models gemma-4-e2b-it-q4km, final-3-bench 73; sha 2d0f887f...). Same phone, installed APK (gemma2, thinkingOff shim; checked after the run by counting thinking markers in answers), A-union kit already installed (6 packs + gazetteer, shas verified 03:3x). Thermal gate before the run (status 0, battery <= 34.0 C). Measures and script as in the main criterion (summarize_aunion.py, same sha). 0 judge calls.

Baseline: gemma73-a (same phone, same APK, claim kit only, 02:07-02:20; started at battery 33.0 C, thermal max 1).

Rule: PASS if PSS peak < 5.0 GB AND 0 LMK kills; else FAIL. If PSS crosses 4.8 GB mid-run the run is let finish (a kill is the data point) and the crossing is noted with its time. Reported vs gemma73-a: answer p50/p90, TTFT p50, retrieval p50, promptN p50/max, prefill/decode tok/s, pack hits by source, battery/thermal (gemma73-a hit thermal 1 mid-run, so speed deltas carry that caveat).
