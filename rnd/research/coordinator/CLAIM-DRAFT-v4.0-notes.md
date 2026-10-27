# CLAIM-DRAFT v4.0 — evidence trail (2026-10-15, drafting agent; 0 judge calls, 0 paid API; blind/ and rnd/veil/ not opened)

TL;DR: v4.0 adds a post-facing §0 (873 words counted from "**BOAR:" to the end of "Limits") plus Appendix A, and updates the evidence body (§1, §4, §6, §7, UNKNOWN, Sources S51–S54). Every number below is copied from the files cited, not recomputed. Paths are relative to `rnd/research/coordinator/` unless stated otherwise.

## 1. Number → source (file:line)

| Number in v4.0 | Source |
|---|---|
| 4B V-para floor-adj 0.261 (0.224–0.299), raw 0.413 (0.384–0.445), 2 seeds, Opus | CLAIM-RESULTS-cut3.md:57, :61 (BAR-TABLE.md:35 gives the cut 6 re-run as 0.261 (0.224–0.300); v4.0 keeps the cut 3 figure that v3.9 used) |
| 4B V-para W/T/L 0/0/51 on both seeds | BAR-TABLE.md:35 |
| 4B v0.2 floor-adj 0.389 (0.347–0.435), raw 0.513 (0.479–0.550) | CLAIM-RESULTS-cut3.md:24 (cut 6 two-seed: 0.388 (0.346–0.434) / 0.512 (0.478–0.549), BAR-TABLE.md:53) |
| 4B v0.2 W/T/L 0/0/110 · 0/1/109 (cut 6) | BAR-TABLE.md:53 |
| Cut 7 = cut 6 on both sets (replay); cut 3 → cut 6 verdict reuse | CLAIM-DRAFT §1 lineage bullet [S18][S19]; CLAIM-RESULTS-cut6.md l.20–29 |
| Raw floor ≈ 0.31 (D = 0.306) | BAR-TABLE.md:14 (analysis plan §4.2) |
| Deep, no thinking V-para 0.329 (0.294–0.362), raw 0.467 (0.439–0.494), 0/0/51 ×2, p50 33.3/30.9 s | BAR-TABLE.md:37 |
| Deep, no thinking v0.2 0.457 (0.417–0.500), raw 0.568 (0.536–0.602), 0/0/110 ×2, p50 34.4/33.6 s | BAR-TABLE.md:55 |
| Deep + 512 V-para 0.436 (0.401–0.472), raw 0.553 (0.524–0.581), 0/0/51 ×2, p50 78.9/79.4 s | BAR-TABLE.md:39 |
| Deep + 512 V-para seed-noise CIs 0.387–0.486 / 0.513–0.592 | BAR-TABLE.md:126 |
| Deep + 512 v0.2 0.508 (0.467–0.550), raw 0.608 (0.575–0.641), 0/1/109, 1 seed, p50 82.4 s | BAR-TABLE.md:57 |
| Deep + 512 v0.2 seed-noise CIs 0.463–0.553 / 0.569–0.647 | BAR-TABLE.md:128 |
| Deep + 1024 V-para 0.422 (0.385–0.459), raw 0.542 (0.513–0.571), seed noise 0.371–0.473 / 0.502–0.582, p50 142.9/146.0 s | BAR-TABLE.md:38, :127 |
| Deep + 1024 v0.2 0.514 (0.475–0.554), raw 0.612 (0.581–0.644), 0/1/109 · 0/2/108, seed noise 0.472–0.556 / 0.578–0.647, p50 132.6/136.8 s | BAR-TABLE.md:56, :129 |
| Haiku no-web V-para raw 0.588 (0.559–0.615), floor-adj 0.48 (no CI) | BAR-TABLE.md:44 |
| 4B desktop p50 10.1 s (V-para claim run), 6.3/6.1 s (v0.2, same backend) | BAR-TABLE.md:35, :53 |
| Bar readings: raw rule met on both sets only by T and H; D meets it on v0.2 only (0.536); 4B CI high 0.445 / v0.2 straddles; floor-adj target met by none; win rate 0 everywhere | BAR-TABLE.md:70–73, :80 (bottom line); raw rule defined on v0.2 in the analysis plan, extension to V-para is BAR-TABLE.md:7 (CLAIM-REVIEW-v3.9 premise correction) |
| Correctness-only floor-adj 0.427 (4B) / 0.660 (deep + 512), V-para; gap in completeness and usefulness | BAR-TABLE.md:88–89, :95 |
| "miss knowledge the packs do not hold" | BAR-TABLE.md:142 (59 % absent knowledge; scoped by the 2026-10-12 correction, :145–146) |
| POCO X6 Pro: MT6897, 10.7 GiB, Android 16, airplane mode, Wi-Fi/BT off, no INTERNET permission | arms/device-x6/DEVICE-X6.md:7 |
| 72/72, 0 crashes; fast tier p50 30.7 s / p90 48.4 s / max 53.0 s; TTFT p50 18.5 s; decode 5.5 tok/s; all answers p50 24.7 s / p90 41.4 s; wall 29 min 14 s | DEVICE-X6.md:14–18 |
| PSS peak 5.88 GB at load, then ≤ 4.23 GB; thermal_status 0; battery 34.5 → 41.7 °C (charging) | DEVICE-X6.md:19–20 |
| Phone 0.529 (0.481–0.575) vs desktop 0.529 (0.484–0.575); above-min 0.403 / 0.402; W/T/L 2/1/54 vs 1/2/54; paired −0.000 (−0.026…+0.028); Haiku 5.5-low; one run | DEVICE-X6.md:3, :29–34 |
| A15 cut 6: 73/73, airplane mode, model answers p50 49 s / p90 77 s / max 111 s, instant p50 8.5 s, PSS max 4.41 GiB, thermal 0; 0.561 (0.507–0.617) vs 0.558/0.560, judge.v1-med | CLAIM-DRAFT §1 device bullet (v3.9 text) [S28]; QUEUE.md:711; κ 1.000 judge.v1-med vs judge.v1 QUEUE.md:543 |
| Longer sessions: turns 2–5 ratio 1.397 (1.187–1.673), W/T/L 19/17/4 | arms/longsession/LONGSESSION.md:19 |
| Self-contained turns 2–5 1.205 (1.010–1.467) | LONGSESSION.md:22 |
| Turns 6–15 1.136 (0.993–1.320), W/T/L 10/18/2; self-contained 1.017 (0.950–1.095) | LONGSESSION.md:66, :79, :81 |
| Per-turn p50 turn 1 9.1 s; turns 2–5 5.1–10.6 s (standalone 2.5–7.1 s); turns 6–15 12.5–22.4 s | LONGSESSION.md:14–18, :77–78 |
| Desktop p50 11 s at turn 1 → 22 s at turns 14–15 vs ≈ 8 s standalone (post text) | LONGSESSION.md:66 (Addendum TL;DR) |
| Prompt peak 1,658 tokens (turn 14); crosses 4,096 at ≈ turn 50 | LONGSESSION.md:66, :78, :108 |
| App window: last 6 messages + ≤ 150-token summary from turn 8; ≈ 360–420 history tokens at turn 15 (estimated); app policy not run | LONGSESSION.md:33, :101–107 |
| 3/50 history-specific defects (card replay 2, detector 1); 0 in turns 6–15; error propagation in 2 sessions (ls04, ls02) | LONGSESSION.md §4–§5, A3 |
| 80 agent-written dev questions, one seed (42), Haiku judge.v1-low, reference = BOAR standalone answers | LONGSESSION.md:5–9 and Addendum l.68–71 |
| PR-1: retrieval 60/60, desktop generation 59/60, tests 1,378/1,378, wiring commit droppable, no Android build or device run | arms/pr1/PR-DESCRIPTION.md:58–59, :94, :122, :132 |
| PR-2 (packs/X2b, catalogue) after 2026-10-20; v0.3 out this week | CLOSING-SPRINT-2026-10-14.md:15 (Q3), :17 (Q5) |
| Kit 3.03 GB; facts table 4,233 entities; no Play Services code; no INTERNET in the no-network APKs | CLAIM-DRAFT §3 (S11, S18), evidence keys E1, E5 |
| 0 unsafe-rule hits on 10 danger questions | CLAIM-RESULTS-cut3.md safety table (cut3 s42/s43 0/0) |
| Two public repos, CONTRIBUTING invites held-out items (hashes first) | CLOSING-SPRINT §1 Q11; release/CONTRIBUTING.md:3, :12–14 |

## 2. Unsourced numbers
None in §0 or Appendix A. Two values rest on prose rather than an aggregate file: the Haiku anchor floor-adj 0.48 (no CI; BAR-TABLE.md:44 says so) and the A15 figures (QUEUE.md:711 plus the run directory). The "≈ 360–420 history tokens" figure is LONGSESSION's own estimate (0.259 tokens/char), labelled as estimated.

## 3. Choices the reviewer should check
- **POCO judge.** DEVICE-X6 used Haiku 5.5-low, not Opus; the text says so and calls it not comparable in level with the Opus rows or the A15 figure (judge.v1-med Opus).
- **"72/72".** DEVICE-X6 runs the 73-question set as 72 items + a warm-up; the post says 72/72.
- **Cut 3 vs cut 6 numbers.** Post and Appendix keep the cut 3 claim numbers (as v3.9) with cut 6 W/T/L; differences ≤ 0.001.
- **Bar sentence.** "Pre-registered rule … on v0.2; we also apply it to V-para" follows the v3.9 premise correction; deep without thinking meets the raw rule on v0.2 alone (Appendix A1 note).
- **Row 8 status** changed from "Not met on the phone" to "Not shown (judgement call; measured on two phones)": "usable speed" has no frozen threshold.
- **Excluded on purpose:** native-app comparison (DEVICE-X6 B rows), RIVALSET and any competitor number, X2b's +[competitor score removed] (dev self-tests; PR-2 material), venue results (would need the "with device location and the user's area tile" wording; kept only in §4/§5).
- **Hygiene edits to pre-existing text:** S28's run directory contained a person's name; S38 carried a third-party GitHub handle; row 15 and S34/S47 named the bounty issuer. All neutralised.
- §0 health caveat present; "AI-reviewed, not clinically reviewed" occurs 10 times in the file (v3.9: 8).

## UNKNOWN
Whether the PR-1 branch tip will change before submission (numbers cite tip 8b117738). Whether the shared public rubric (expected from the bounty's contributors) wants a different scale order. Repo URLs (placeholders).
