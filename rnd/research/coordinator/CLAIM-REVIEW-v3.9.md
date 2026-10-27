# CLAIM-REVIEW v3.9 — red-team adjudication by the independent Opus reviewer (2026-10-13 22:5x, a parallel session)

**Verdict: ACCEPT WITH EDITS — 41 edits, applied by script (`CLAIM-REVIEW-v3.9-edits.py`, each OLD string matched exactly once in apply order) to CLAIM-DRAFT.md → v3.9.** Input: CLAIM-REDTEAM-2026-10-13.md (§2 nine overclaiming items, §4 eleven mismatches, §5 device gaps) + three reviewer-found items (R1–R3). Checks after applying: "AI-reviewed, not clinically reviewed" 8 lines (unchanged); venue wording "with device location and the user's area tile" ×3 (unchanged); leak grep: one pre-existing path only. No blind/veil read; no new measurement.

**Headline decision: YES.** Section 1 now states that the deep tier (not in the claim build, desktop only, development-style data) meets the pre-registered RAW rule and does not meet the floor-removed target; the 4B claim build meets neither; win rate 0 everywhere; no unexposed set. Premise correction: analysis-plan l.17 defines the raw bar on v0.2 only — its extension to V-para is BAR-TABLE l.7's, and the text says so.

## Verdict table
| Item | Verdict | Reason |
|---|---|---|
| Header "pending independent review" | ACCEPT WITH EDITS | v3.8 was reviewed; v3.9 header added (edits 1, 2, 4) |
| v3.5.1 → v3.8 version note | ACCEPT WITH EDITS | v3.5.1 covered by the v3.6 review; v3.8 missing from the review log (3, 5, 40) |
| §2.1 v0.2 "written blind" | ACCEPT WITH EDITS | "Formerly held-out", Claude-family writers, ledger dates (EXPOSURES bench-v02) |
| §2.2 "one disclosed exception" | ACCEPT WITH EDITS | A05, 3 adjudicated items, git plaintext (edit 14) |
| §2.3 V-para "written by our team" | ACCEPT WITH EDITS | Opus writer + grading-field print; reference author not recorded, so not claimed |
| §2.4 cut 6 verdict reuse | ACCEPT WITH EDITS | v0.2-specific 210/220 and V-para 96/102 (CLAIM-RESULTS-cut6 l.20–29), not 323/334 |
| §2.5 "device = desktop" | ACCEPT WITH EDITS | judge.v1-med, one phone, one run (QUEUE l.711) (10, 26) |
| §2.6 "first above 0.50" | ACCEPT WITH EDITS | Selection disclosed with "many"; "~20" has no source in BAR-TABLE or an arm file |
| §2.7 seed-noise CIs | ACCEPT WITH EDITS | BAR-TABLE l.131: CI_cm for H, T, TV and H v0.2 (28–33) |
| §2.8 row 7 "Partly met" | ACCEPT WITH EDITS | Kept "Partly met", qualified; "Attempted" is not a key value |
| §2.9 metric switch undeclared | ACCEPT WITH EDITS | Added to Departures (15) |
| §4.1 CLAUDE.md 0.519 | REJECT | Not claim text; the draft already uses two-seed numbers. Fix CLAUDE.md:22 |
| §4.2 CLAUDE.md order | REJECT | Not claim text |
| §4.3 +0.063 vs +0.054 | REJECT | The claim never cites pack numbers |
| §4.4 bar definition differs | ACCEPT WITH EDITS | Aligned with BAR-TABLE §0: win rate reported, not gated (9, 15, 30) |
| §4.5 BAR-TABLE.sha256 stale | REJECT (claim text) | Coordinator appended the current hash 0b1e9714… to BAR-TABLE.sha256 (done 22:5x) |
| §4.6 "4 runs" | ACCEPT WITH EDITS | "At least 12 gen / 10 Opus passes"; EXPOSURES status rows stale since 10-10 |
| §4.7 "Nothing is published" | ACCEPT WITH EDITS | Claim kit packs are public (REPRO-PLAN l.19); handle left out |
| §4.8 phone time 2–3 min | ACCEPT WITH EDITS | DEEP-RESEARCH D-3: 1.9–2.8 min cool + hot figure (35, 37) |
| §4.9 judge.v1-med | ACCEPT WITH EDITS | Exception stated; κ 1.000 (QUEUE l.543) (13) |
| §4.10 0.552 / 0.299 | ACCEPT (H) / REJECT (K) | H → 0.553 (BAR-TABLE l.39); K 0.299 is the labelled cut 3 run |
| §4.11 77 vs 74 MB | ACCEPT WITH EDITS | Same bytes, MB vs MiB (17, 18) |
| §5.1 bmoe has no budget setting | ACCEPT WITH EDITS | deep/RESUME.md D6 (34) |
| §5.2 parity without thinking | ACCEPT | DEEPPAR-L1 covered the deep tier without thinking (36) |
| §5.3 no BOAR phone run | ACCEPT | Folded into 37 |
| §5.4 benchmark app vs user app | ACCEPT WITH EDITS | Row 12 keeps "Partly met" with an explicit sentence |
| §5.5 venues never on a phone | ACCEPT | §5 l.167 already said it; row 15 now does (24) |
| R1 "No 12 GB device" | ACCEPT WITH EDITS | Outdated: a teammate's 12 GB phone is connected, package shared (QUEUE 10-13) |
| R2 "No phone run in airplane mode" | ACCEPT WITH EDITS | Contradicted rows 4 and 21 (cut 6 ran in airplane mode) (12) |
| R3 row 14 | ACCEPT WITH EDITS | Raw-rule sentence matches the headline (23) |
| Competitor placeholder (RIVALSET) | REJECT | No competitor-comparison section exists; nothing added |

## Consistency check (numbers new or changed in v3.9; untouched numbers were traced by the red-team and earlier reviews)
0.445 (K V-para raw CI high): BAR-TABLE.md:35 · v0.2 K CI contains 0.50: BAR-TABLE.md:53, :70 · 0.553 and CI_cm 0.513–0.592: BAR-TABLE.md:39, :126 · 0.608 and 0.569–0.647 (H v0.2 raw, 1 seed): :57, :128 · 0.502 (T V-para raw CI_cm low), 0.371–0.473 / 0.502–0.582: :127 · 0.578 (TV v0.2 raw CI_cm low), 0.472–0.556, 0.578–0.647: :129 · 0.436 and 0.387–0.486: :39, :126 · 0.463–0.553: :128 · 0.581 (TV v0.2 raw CI low): :56, :72 · win rate 0 on every row and seed: :80 · ≈ 0.31 always-decline raw (D = 0.306): :14; analysis plan §4.2 · "met when the CI lies above 0.50": boar-eval/bench/v0.2/plan/analysis-plan.md:17, :58; V-para extension BAR-TABLE.md:7 · 49 % correctness ≤ 2: PIPELINE-AUDIT-2026-10-06.md:14 · usefulness ≥ 3: 2.9 % / 34.5 %: BAR-TABLE.md:93 · 210/220, 10 fresh, 96/102: CLAIM-RESULTS-cut6.md l.22–28 · ≥ 12 gen / 10 Opus (v0.2); 19 full / 12 slices / 16 Opus (V-para): EXPOSURES.md l.14–15 · 2026-10-02 (d8154b6), 10-03 (A05), 10-06 (burnt): EXPOSURES ledger rows · 3 hand-adjudicated items: EXPOSURES bench-v02 notes · 58 / 51 / 7 V-para, Opus writer: EXPOSURES V-para row · κ 1.000: QUEUE.md:543; A15 judged judge.v1-med: QUEUE.md:711 · 73/73 airplane mode: QUEUE.md:711 · 77,086,168 B / 74 MiB: DEVICE-DAY.md:8 · 1.9–2.8 min, ≈ 3 min in-app, 3.4–5.0 min, −22 %: deepresearch-2026-10-12/verify/engine_speed.md:80–82; DEEP-RESEARCH-2026-10-12.md:29, :143 · bmoe v0.28.0 `--no-think` only: deep/RESUME.md:59–61 · 12 GB teammate phone, package shared: QUEUE tail 10-13 · reused unchanged: 0.558 / 0.560, 0.422, 0.514, 0.475, 0.512, 512 / 1024 (S28, S33, S35, S37, S41). New evidence keys S45–S50 added to the draft.

## UNKNOWN
Exact current run and judge-pass counts per set (EXPOSURES status rows predate QUANTCEIL, VITALADD stage 3, DEEPHEDGE, DEEPROUTE-V02 → "at least"; coordinator to update the rows). Which model wrote the V-para references (EXPOSURES open question). Seed-noise CIs for D, Q, G never computed (BAR-TABLE addendum covers H, T, TV, H v0.2). Pooled 3-seed H CI missing (dt512/aggregates/L2-H-3seed.opus.json is 0 bytes, PIPELINE-AUDIT F2) → edit 9 cites the two-seed CI. No hot-phone number of our own. No PIPELINE-AUDIT-2026-10-13 defect touches a claim number. RIVALSET and ORACLE-ST still running: no claim text added. Update to claim #124 vs new claim: does not affect the text.
