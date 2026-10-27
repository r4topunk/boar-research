import sys, re
src = "<workspace>/rnd/research/coordinator/CLAIM-DRAFT.md"
t = open(src, encoding="utf-8").read()
E = []
def e(old, new): E.append((old, new))

# 1-5 header / version
e("Draft v3.8 (2026-10-10 midday;",
  "Draft v3.9 — reviewed 2026-10-13 (independent Opus reviewer, side-session session): adjudicates CLAIM-REDTEAM-2026-10-13 (exposure and authorship wording, verdict reuse, device-implication gaps, seed-noise CIs, the pre-registered raw rule stated in section 1; see CLAIM-REVIEW-v3.9.md) — Draft v3.8 (2026-10-10 midday;")
e("Not published; pending independent review.", "Not published.")
e("S36, unreviewed)", "S36; reviewed with v3.6)")
e("independently reviewed through v3.8", "independently reviewed through v3.9")
e("## Changelog v3.5 → v3.5.1 (2026-10-09; two sentences, not yet independently reviewed)",
  "## Changelog v3.5 → v3.5.1 (2026-10-09; two sentences, reviewed with v3.6)")
# 6-7 V-para + v0.2 headline wording
e("(V-para, written by our team, 51 judged questions plus 7 venue questions; blind to the engine builders when these claim runs were made, spent since by deep-tier and venue arms, see section 5)",
  "(V-para: 58 questions written by a Claude Opus agent, 51 judged plus 7 venue questions, so the writer and the judge are one model family; blind to the engine builders when these claim runs were made, although a runner script once printed the set's grading fields (no questions, answers or references) before them; spent since by deep-tier and venue arms, see section 5)")
e("- **Held-out result (bench v0.2, 110 new questions, written blind):**",
  "- **Formerly held-out result (bench v0.2, 110 questions written blind by two Claude-family subagents; development data since 2026-10-06):**")
e("The v0.2 set has since been exposed (plaintext in a private repository's history, 4 runs) and is treated as development data;",
  "The v0.2 set is exposed (questions and references in plaintext in a private repository's history since 2026-10-02, before the claim runs; at least 12 full generation runs and 10 full Opus judge passes to date, team ledger [S47]) and is treated as development data;")
# 8 new headline bullet
e("- **Three scales, always shown together:**",
  "- **Pre-registered raw rule vs our stricter target (new in v3.9; context, not a claim number):** the analysis plan judges the bar on the raw ratio over bench v0.2, met when the 95% CI lies above 0.50; our bar table applies the same rule to V-para. The 4B claim build does not meet it (V-para raw CI high 0.445; v0.2 CI contains 0.50). The deep tier, which is not in the claim build and has never run on a phone, meets it on the desktop proxy on development-style data: with 512-token thinking, V-para raw 0.553 (0.513–0.592 with seed noise, two seeds) and v0.2 raw 0.608 (0.569–0.647, one seed); with 1024-token thinking, on two seeds on both sets (CI low ends 0.502 and 0.578 with seed noise). Because a system that declines everything already scores raw about 0.31, we lead with the floor-removed target (CI low at or above 0.50 on V-para, two seeds), which nothing reaches: the best deep tier scores 0.436 (0.387–0.486 with seed noise). The win rate is 0 on every set and seed. No unexposed set exists; a final number needs v0.3. [S1] [S2] [S46]\n- **Three scales, always shown together:**")
# 9-10 device parity
e("against 0.558 and 0.560 on the desktop: device quality equals desktop within noise.",
  "against 0.558 and 0.560 on the desktop (judge.v1-med; one phone, one run): on these items the phone score is not distinguishable from the desktop's.")
# 11 cut 6 verdict reuse
e("210 of 220 held-out item-seed answers byte-identical).",
  "210 of 220 held-out item-seed answers byte-identical; the judge verdicts of byte-identical answers were copied from the cut 3 run and only the 10 changed item-seeds were judged fresh (V-para: 96 of 102 copied), so the narrow Δ reflects that reuse and is not an independent re-judging).")
# 12 stale airplane-mode sentence
e("No phone run in airplane mode has happened yet. See rows 4 and 5.",
  "Cut 6's no-network APK has since run 73/73 questions on the 8 GB A15 in airplane mode (device status above); no traffic capture exists. See rows 4 and 5.")
# 13 judge.v1-med exception
e("Every claim number in this draft is Opus `judge.v1`. [S22]",
  "Every claim number in this draft is Opus `judge.v1`, except the phone-vs-desktop comparison in section 1 (judge.v1-med: the same Opus prompt at medium effort, which matched judge.v1 with κ 1.000 in a calibration re-judge). [S22] [S49]")
# 14 v0.2 exposure list
e("The 110 v0.2 questions are held-out: no engine change was tuned on their scores, with one disclosed exception (below).",
  "The 110 v0.2 questions were the held-out set: no engine change was tuned on their scores except one disclosed item (below). Other known exposures: one item seen by a researcher on 2026-10-03, 3 hand-adjudicated items, and the questions and references in plaintext in a private repository's history since 2026-10-02, before the claim runs; the set has been development data since 2026-10-06 (team ledger [S47]).")
# 15 departures: metric change
e("- **Pre-registration timing.** Hashes were committed to a private repository",
  "- **Headline metric (changed after the results).** The plan judges the bar on the raw ratio (plan §3). After the cut 3 and cut 6 claim results, an internal audit (2026-10-06) moved the headline to the floor-removed ratio plus win rate, a stricter scale; the raw reading stays beside it in every table, and section 1 says where the pre-registered rule is met (deep tier, development-style data) and where it is not (4B claim build). [S2] [S27] [S46]\n- **Pre-registration timing.** Hashes were committed to a private repository")
# 16 cut 6 lineage row
e("Claim re-run on held-out v0.2 and V-para (seeds 42, 43): raw 0.512",
  "Claim re-run on held-out v0.2 and V-para (seeds 42, 43; judge verdicts copied from cut 3 for byte-identical answers): raw 0.512")
# 17-18 row 3 APK and S8
e("plus the measurement app (BOAR Bench APK) 77 MB.",
  "plus the measurement app (BOAR Bench APK) 77 MB (77,086,168 bytes, 74 MiB).")
e("(device-day entry: APK 74 MB,", "(device-day entry: APK 74 MiB,")
# 19-20 row 7
e("| 7 | Useful research questions beyond recall (explain, compare, synthesise, reason) | **Partly met** |",
  "| 7 | Useful research questions beyond recall (explain, compare, synthesise, reason) | **Partly met (answers often thin or wrong)** |")
e("\"Above half\" is not shown on either set.",
  "\"Above half\" is not shown on either set. On V-para the 4B claim build's correctness is 2 of 5 or lower on 49 % of items, and its usefulness reaches 3 of 5 on 2.9 % of items (v0.2: 34.5 %). [S27] [S46]")
# 21 row 9
e("| 9 | Public GitHub repo with the functional version | **Not yet** | The work is in private repos. Nothing is published. [S0] |",
  "| 9 | Public GitHub repo with the functional version | **Not yet** | The code is in private repos; no public code repository exists. The claim kit's two knowledge packs (crypto, English Wikivoyage) and further packs used in no claim number are public on the project's Hugging Face dataset (boar-packs). [S0] [S48] |")
# 22 row 12
e("The bounty requires a stranger to install from a public repo in minutes; that path does not exist yet (rows 9 and 10).",
  "The phone runs used the debuggable measurement app (BOAR Bench), not an installable user app, and neither Android chat app calls the measured engine path (Android UI note below). The bounty requires a stranger to install from a public repo in minutes; that path does not exist yet (rows 9 and 10).")
# 23 row 14
e("Held-out v0.2 is exposed; a final number needs v0.3. [S1] [S18] [S25]",
  "Held-out v0.2 is exposed; a final number needs v0.3. The deep tier (not in the claim build, desktop only) meets the pre-registered raw rule on development-style data but not the floor-removed target (section 1). [S1] [S18] [S25] [S46]")
# 24 row 15
e("Tile download UX in the app and cities without a catalog tile: untested.",
  "Tile download UX in the app and cities without a catalog tile: untested. The location path has not been tested on a phone (section 5).")
# 25 section 5 V-para counts
e("later deep-tier arms on V-para are logged the same way)",
  "later deep-tier arms on V-para are logged the same way; at least 19 full generation runs, 12 twenty-item slices and 16 full Opus judge passes to date [S47])")
# 26 section 6 parity row
e("on the same 57 development items, so device quality equals desktop within noise.",
  "on the same 57 development items (judge.v1-med), so on one 8 GB phone the phone score is not distinguishable from the desktop's.")
# 27 12 GB footprint
e("points to a 12 GB phone, and none is available.",
  "points to a 12 GB phone, and no 12 GB phone has run it yet.")
# 28-31 deep-tier CIs with seed noise
e("floor removed 0.422 (0.385–0.459), pairwise wins 0 of 51 on both seeds; raw 0.542 (0.513–0.571)",
  "floor removed 0.422 (0.385–0.459; 0.371–0.473 with seed noise), pairwise wins 0 of 51 on both seeds; raw 0.542 (0.513–0.571; 0.502–0.582 with seed noise)")
e("floor removed 0.514 (0.475–0.554), pairwise wins 0 of 110 on both seeds; raw 0.612 (0.581–0.644)",
  "floor removed 0.514 (0.475–0.554; 0.472–0.556 with seed noise), pairwise wins 0 of 110 on both seeds; raw 0.612 (0.581–0.644; 0.578–0.647 with seed noise)")
# 32 selection + bar reading
e("This is the first configuration whose point estimate is above 0.50 floor removed on any set, but its CI straddles 0.50 (low end 0.475) and its win rate is 0 of 110, so the bar reading (floor-removed CI low above 0.50 and win rate above 0) is not met; v0.2 is development data, so this is not claim evidence.",
  "This was the first configuration whose point estimate is above 0.50 floor removed on any set, but it is the best of many deep-tier configurations tried on these exposed sets (team ledger), so selection inflates it; its CI straddles 0.50 (low end 0.475; 0.472 with seed noise) and its win rate is 0 of 110, so our floor-removed target (CI low at or above 0.50; win rate reported, not gated) is not met. It does meet the plan's raw rule on this set (raw CI low 0.581). v0.2 is development data, so this is not claim evidence. [S46]")
e("floor removed 0.436 (0.401–0.472) vs 0.422 at 1024",
  "floor removed 0.436 (0.401–0.472; 0.387–0.486 with run-to-run seed noise added, the interval the claim cites for deep-tier rows [S46]) vs 0.422 at 1024")
e("raw 0.552 (0.524–0.581)", "raw 0.553 (0.524–0.581; 0.513–0.592 with seed noise)")
e("the 512-work budget scores raw 0.608 (0.575–0.641), floor removed 0.508 (0.467–0.550)",
  "the 512-work budget scores raw 0.608 (0.575–0.641; 0.569–0.647 with seed noise), floor removed 0.508 (0.467–0.550; 0.463–0.553 with seed noise)")
# 36-37 bmoe gaps
e("the device plan stays one deep answer with thinking 512, with no best-of-2 or verifier pass [S43].",
  "the device plan stays one deep answer with thinking 512, with no best-of-2 or verifier pass [S43]; the planned device engine (bmoe v0.28.0) has no thinking-budget setting, so the 512 cap needs an app-side limit that is not built yet [S50].")
e("our arithmetic gives roughly 2–3 min per 512-token thinking answer and 3.5–5 min per 1024-token one on that phone",
  "our arithmetic gives roughly 1.9–2.8 min per 512-token thinking answer on a cool phone (about 3 min at their slower in-app decode rate; their third back-to-back request decoded 22 % slower) and 3.4–5.0 min per 1024-token one on that phone [S45]")
e("The desktop deep-tier numbers may therefore be quoted for a bmoe-based device plan only with that caveat [S30].",
  "The desktop deep-tier numbers may therefore be quoted for a bmoe-based device plan only with that caveat [S30]; that parity test covered the deep tier without thinking, so the thinking tiers' transfer to bmoe is untested.")
# 40-41 section 7
e("applying that competitor's public 12 GB phone rates gives roughly 2–3 min per such answer (our arithmetic, their rates) [S38]; our own phone measurement is still pending.",
  "applying that competitor's public 12 GB phone rates gives roughly 1.9–2.8 min per such answer on a cool phone (our arithmetic, their rates) [S38] [S45]; no BOAR deep-tier run on any phone exists yet.")
e("No 12 GB device is available.",
  "A teammate's 12 GB phone is now connected through a relay and a cut 7 test package has been shared; no result has returned yet. [S3]")
# 42 sources
e("## Evidence keys (used in the checklist)",
  "- S45: `rnd/research/coordinator/DEEP-RESEARCH-2026-10-12.md` D-3 and `deepresearch-2026-10-12/verify/engine_speed.md` (per-answer phone time from the competitor's measured rates: 512 budget 1.9–2.8 min cool, in-app upper end ≈ 3 min, 1024 budget 3.4–5.0 min; third back-to-back request −22 % decode)\n- S46: `rnd/research/coordinator/BAR-TABLE.md` §0 (targets), §1a/§1b/§1c (rows and readings), §2 (usefulness and correctness shares), addendum 2026-10-11 (CIs with seed noise)\n- S47: `rnd/research/coordinator/EXPOSURES.md` status rows bench-v02 and V-para (writers, run and judge-pass counts, A05, hand-adjudicated items, grading-field print, git plaintext d8154b6)\n- S48: `rnd/research/coordinator/REPRO-PLAN.md` l.19 (claim kit packs public on the dataset); `rnd/research/QUEUE.md` pack publication rows (2026-10-13)\n- S49: `rnd/research/QUEUE.md` l.543 (judge.v1-med vs judge.v1, κ 1.000) and l.711 (A15 comparison judged with judge.v1-med)\n- S50: `deep/RESUME.md` addendum 2026-10-09 D6 (bmoe v0.28.0 exposes only `--no-think`; budget needs an app-side cap)\n## Evidence keys (used in the checklist)")
# 43 review log
e("- v3.7 reviewed (independent Opus, 2026-10-09 night): ACCEPT WITH EDITS, 0 blockers, 1 major + 6 minor + 1 nit applied; see `CLAIM-REVIEW-v3.7.md`.",
  "- v3.7 reviewed (independent Opus, 2026-10-09 night): ACCEPT WITH EDITS, 0 blockers, 1 major + 6 minor + 1 nit applied; see `CLAIM-REVIEW-v3.7.md`.\n- v3.8 reviewed (independent Opus, 2026-10-10): ACCEPT WITH EDITS, 0 blockers, 1 major + 6 minor + 1 nit applied; see `CLAIM-REVIEW-v3.8.md`.\n- v3.9 reviewed (independent Opus, 2026-10-13, side-session session): red-team adjudication (CLAIM-REDTEAM-2026-10-13) applied as an edit list; see `CLAIM-REVIEW-v3.9.md`.")
# 44 changelog
e("## Changelog v3.7 → v3.8",
  "## Changelog v3.8 → v3.9 (2026-10-13; red-team adjudication by the independent Opus reviewer; no new measurement)\n- §1: v0.2 relabelled formerly held-out (writers, exposure dates, run counts); V-para authorship and the grading-field print disclosed; cut 6 verdict reuse disclosed; phone parity reworded (judge.v1-med, one phone); stale airplane-mode sentence corrected; new bullet: the pre-registered raw rule is met by the deep tier (desktop, development-style) and not by the 4B claim build; floor-removed target not met; win rate 0.\n- §2: judge.v1-med exception; v0.2 exposure list; headline-metric change listed under departures. §3: cut 6 row notes verdict reuse.\n- §4: row 3 APK bytes; row 7 qualified with correctness and usefulness shares; row 9 public packs; row 12 measurement app vs user app; row 14 raw-rule sentence; row 15 location path not on a phone. §5: V-para run counts.\n- §6: seed-noise CIs for the deep-tier rows in BAR-TABLE's addendum (T, H, TV, H on v0.2); H raw 0.553; v0.2 1024 sentence: selection and raw rule; bar reading aligned with BAR-TABLE (win rate reported, not gated); bmoe has no thinking-budget setting; bmoe parity untested with thinking; phone time 1.9–2.8 min cool (DEEP-RESEARCH D-3); 12 GB phone wording. §7: 12 GB phone line; phone time.\n- Sources S45–S50; header, title line and review log.\n\n## Changelog v3.7 → v3.8")

out = t
for i, (o, n) in enumerate(E, 1):
    c = out.count(o)
    if c != 1:
        print("FAIL", i, c, o[:80]); sys.exit(1)
    out = out.replace(o, n)
open(sys.argv[1], "w", encoding="utf-8").write(out)
print("edits", len(E), "ok")
