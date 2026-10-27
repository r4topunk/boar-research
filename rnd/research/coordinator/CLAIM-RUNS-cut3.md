# Claim runs on cut 3 — coordinator authorisation (r4to approved 2026-10-05), frozen before any run

Engine: cut 3 = arms/cut3-final-candidate.vs-0cfd4a77.patch (sha256 a67c70dbd194da82f46704bff1bb29e24b610808112c402348dc2c5e70bd35c9). No code change of any kind during the claim runs.

## Run A — bench v0.2 held-out L3 (spends the held-out once for cut 3)
- Plan: boar-eval bench/v0.2/plan/ (analysis-plan.md 697b4327…, floor_metrics.py, paired_gap.py, strata.py; combined fe100e91…), addenda 01–04 (coverage, safety v0.5→v0.7 overlay, …) exactly as used for the ship L3 (blind/bench-v02/runs-ship).
- Config identical to runs-ship: Android 12 GB profile, 4B, kit as runs-ship, detector on, seeds s42 + s43, all EN items (ship-all.en.ids). Judge judge.v1 (NO --effort flag), both orders — same judge version as runs-ship and E3, so cut 3 is paired against them.
- Report: raw ratio (headline) + floor-removed + above-always-decline, stratified CI per the plan; EN-only primary, full view beside; paired Δ vs runs-ship (cut 2-era ship stack) and vs E3; safety per the plan (unsafe adjudication left to the coordinator, keys + counts only).
## Run B — V-para (blind/V-para, 58 items; bars compass/exp/bounty-eval/VPARA-BARS.md; mapping RUN-MAPPING.md)
- Config (b) ship places kit = primary; (a) bare ship config beside. Seeds and judge exactly as VPARA-BARS.md specifies; judge.v1 for the 51 judged items against refs/refs.jsonl; venue scorer for the 7 venue items per RUN-MAPPING.md.
- Report P1–P5 + ladder per VPARA-BARS.md, via compass/exp/bounty-eval/claim_report.py where it applies.
## Blind rules (both runs)
- Script-only access to blind/: the runner never prints question text, answers, refs, grading fields or gold contents into its context; only ids, counts, hashes, aggregate numbers. Exposure of anything else = stop and report.
- Outputs go under blind/bench-v02/runs-cut3/ and blind/V-para/runs-cut3/. Nothing from blind/ is copied into rnd/ or boar-eval except the aggregate report.
- No tuning, no re-runs except for a technical failure (logged with reason).
