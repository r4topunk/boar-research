**Verdict: CHANGES REQUIRED.** The headline numbers, CIs and bar readings are correct, and the draft does not claim the bar is met. Five accuracy errors must be fixed before publication: the kit size is double-counted, the device latency is attributed entirely to the KV bug, the fast-path timing is wrong, the memory peak is wrong, and the cut 4 contents are wrong. Several departures from the pre-registered plan are also not disclosed. Checklist rows 4–6 can now cite hard evidence: a static audit of the measurement APK.

# Independent review of CLAIM-DRAFT.md (2026-10-05)

Reviewer: an Opus agent that did not write the draft. Inputs read: CLAIM-DRAFT.md, CLAIM-RESULTS-cut3.md, cut3-confirm.md, 4B-LOSS-ANATOMY.md (TL;DR), device/A15-SMOKE-DIAGNOSIS.md, arms/cut4/CUT4.md and cut4-L1.md, DEVICE-DAY.md, QUEUE.md (entries cited below), BOUNTY_31.md, boar-eval/bench/v0.2/plan/analysis-plan.md, arms/vg-S-REVIEW.md, rnd/bench/legal/README.md, summit/S1-memo.md, the bench-app manifests, and the boar-app build-variant plugin. I did not open blind/, rnd/veil/, or any items, refs or traces. One local, read-only command was run on the measurement APKs (see "Checklist", evidence E1).

## A. Verified as stated (no change needed)
| Claim | Source check |
|---|---|
| Held-out 0.513 (0.479–0.550) / 0.389 (0.347–0.435) / 0.299 (0.250–0.351); CI contains 0.50 | CLAIM-RESULTS Run A table, matches. (0.513−0.306)/0.694 = 0.298, consistent |
| V-para 0.413 (0.384–0.445) / 0.261 (0.224–0.299) / 0.154 (0.112–0.200) | CLAIM-RESULTS P1/P3, matches |
| Ladder Haiku 0.588 (0.559–0.615), Sonnet 0.961, Opus 1.044, Fable 1.037; run once | CLAIM-RESULTS P6, matches |
| D = 0.306, 79 declines, 7 runs; both orders; disagreement = tie; 2,000 resamples | plan §2, §3, §4, matches |
| v0.1 §10 ladder (0.512 / 0.381 / gap +0.131 etc.) | plan §10, all 9 figures match |
| v0.1 EN cut 3 0.566 vs cut 2 0.534, +0.032 CI90 +0.010…+0.062, 57 items | cut3-confirm (a), matches |
| Travel calculator: 6,000 cities, GeoNames CC BY 4.0, 272 KB, 0/1,034 false fires, Paris–Rome 0.29 → 0.89–0.94 | QUEUE l.514; cut3-confirm (b) 0.893 |
| Arithmetic tools: +3.33, 0/1,467, 28/32, 0 wrong numbers | cut3-confirm; QUEUE l.551 |
| Verdict guard: 3 dev items +1.0…+2.67; 1 fire on 90, BETTER; 1 of 17 | cut3-confirm; vg-S-REVIEW.md; QUEUE l.577 |
| CO card recall 23/26, 1/38 false fires | QUEUE l.517 (v2r) |
| A15: 7.5 GiB usable, model answers 100–147 s, TTFT 72–100 s, decode 2.0–2.9 tok/s | device.json memTotalKb 7,864,220; diagnosis §3 table; QUEUE l.632 |
| KV bug is our regression, never worked on a phone | A15 diagnosis "Correction"; QUEUE l.649 |
| Android UI does not run answerService | QUEUE l.645, l.648 |
| Deep tier +0.06 (desktop), parked | QUEUE l.253, l.271, l.542 |
| Privacy | No names, emails, handles, internal agent names or paths found (grep). |
| Safety caveat | "AI-reviewed, not clinically reviewed" is present (section 5). |

## B. Issues (numbered, each with exact replacement text)

### Blocking: accuracy

**1. Kit size is double-counted (section 3, checklist row 3).** The 3.03 GB device kit *includes* the 2.50 GB model (DEVICE-DAY.md §2 file table). The knowledge packs total only about 0.39 GB. "Model about 2.5 GB, kit about 3 GB" reads as roughly 5.5 GB in total and overstates the knowledge.
Replace the two bullets "Reader model" and "Knowledge kit" in section 3 with:
> - **Reader model:** Qwen3-4B-Instruct-2507, Q4_K_M quantisation, 2.50 GB. [S8] [S11]
> - **Everything pushed to the phone (3.03 GB in total, model included):** reader model 2.50 GB, embedding model 37 MB, emergency detector 108 MB, English Wikivoyage pack 351 MB, crypto pack 36 MB. The knowledge packs themselves are therefore about 0.39 GB. The V-para run (desktop) also loaded a places kit (world places and three city tiles); its size is not in the sources reviewed. [S1] [S11]

Add to Sources: `S11: rnd/research/coordinator/DEVICE-DAY.md (§2 kit file table; APK size)`.

**2. The device latency is attributed entirely to our bug (TL;DR, device status).** The diagnosis says the KV bug accounts for an estimated 55–65 s per model answer. After the fix the estimate is still about 40–85 s, dominated by 2–3 tok/s decode and 6–15 s warm retrieval. That figure is arithmetic, not a measurement (A15 diagnosis TL;DR and §3, last paragraph). The draft also omits correctness on the phone.
Replace the "Device status" bullet with:
> - **Device status:** the only real-phone run of this engine is a 9-question smoke test of cut 3 on an 8 GB Galaxy A15 (7.5 GiB usable), below the 12 GB class. All 9 questions completed. Two answers were wrong: an instant answer ("capital of France" returned a Lyon line, an engine bug since fixed in cut 4) and one model answer that is also wrong on the desktop. Model answers took 100–147 s. An estimated 55–65 s of that per answer is our own KV-cache bug. A fix is built in cut 4 but has not yet run on a phone, and it cannot be tested on the desktop. Even with the fix, the estimate is about 40–85 s per model answer on that phone (decode 2.0–2.9 tokens/s), so speed is the main open problem. The 12 GB device run is pending. [S5] [S6] [S7] [S10]

**3. Fast-path timing is wrong (checklist row 8).** "Instant, card and calculator answers took 0.07–0.22 s" is copied from a QUEUE summary line (l.632). The diagnosis table contradicts it. Only the rule paths (calculator, CO rule, snakebite rule) took 0.07–0.2 s. The two health cards that go through the route gate took 17.5 s and 52.0 s. The instant answer (cold start) took 126.6 s and was wrong.
Replace the row 8 "Basis" cell with:
> On the A15 smoke test (cut 3), rule-based answers (travel calculator, CO rule, snakebite rule) took 0.07–0.2 s. Health cards that pass through the route gate took 17.5–52 s, and the first (cold-start) instant answer took 127 s. Model answers took 100–147 s (time to first token 72–100 s). Our KV-cache save bug re-did an estimated 55–65 s of prefill on each model answer. Cut 4 contains a fix that is unit-tested but not yet run on a phone. Even with it, the estimate is about 40–85 s per model answer on that phone: decode was 2.0–2.9 tokens/s (cause unmeasured; the phone swapped and throttled) and warm retrieval 6–15 s. Desktop proxy, not a phone number: median first token 7.3 s, full answer 10.7 s. [S5] [S6] [S1]

**4. The memory peak is wrong (checklist row 2).** The diagnosis telemetry shows PSS 4.59 GB at +28 s (during model load and repack), then about 3.6 GB. Swap was 1.6 GB after item 1 and 0.73 GB at the end (diagnosis §1 table, §3 fix #5; QUEUE l.630, l.632). An earlier 8 GB Android test is also relevant: on the moto g75, an older engine's 4B was killed by the OS at about 4.7–5.0 GiB RSS (QUEUE l.296).
Replace the row 2 "Basis" cell with:
> On the 8 GB A15, app memory (PSS) peaked at about 4.6 GB during model load, then stayed about 3.6 GB. Up to 1.6 GB was swapped after the first question (0.7 GB at the end). An earlier engine's 4B was killed by the OS on another 8 GB phone (moto g75) at about 4.7–5.0 GiB. No 12 GB phone has been run. [S5] [S7] [S3]

**5. Cut 4 contents and evidence are misstated (section 3, "Engine version note").** The final cut 4 is cut 3 + KVFIX + INSTANT-FRAG (two block rules, "fragment" and "figurative") + INSTANT-SUBJ (patch d51e844c; QUEUE l.648, l.651). The desktop byte-identity gate (60/60 per seed) ran on the stack *without* INSTANT-SUBJ (cut4-L1.md). INSTANT-SUBJ was checked only by a stub replay and unit tests. KVFIX cannot be exercised on the desktop at all (CUT4.md).
Replace the paragraph with:
> The numbers above are for **cut 3**. **Cut 4** adds three patches. (1) A fix for the KV session-cache bug. (2) Two rules that stop a sentence fragment or a figurative "capital" from being returned as an instant answer (the "capital of France" → Lyon case). (3) A subject check that stops an instant answer about the wrong place (for example a state capital returned for a country). On the desktop proxy, cut 3 plus fixes (1) and (2) gave byte-identical answers to cut 3 on the 60 v0.1 questions, in both seeds. Fix (3) was checked only by a replay with a stub model and by unit tests, with no answer changes. The desktop runner cannot exercise fix (1), so its benefit exists only as an estimate until a phone run. The claim numbers are not expected to move. [S3] [S10]

### Blocking: undisclosed departures from the pre-registered plan

**6. The draft does not say where it departs from analysis-plan.md.** Plan §8 says device numbers, not the desktop proxy, are the headline, and that the 1B-class gap (§5.2) on v0.2 appears with its paired CI. The draft headlines desktop numbers and shows only an older v0.1 ladder. Plan §3 planned three seeds. Plan §4 requires the D measured on the claim run's own declines. Plan §5.1 requires per-writer results. Plan §9 says the combined hash is committed publicly before any BOAR run on v0.2-new. QUEUE l.244 shows the hashes were kept in the private repo ("publish later").
Add a new subsection at the end of section 2:
> ### Departures from the pre-registered plan
> - **Headline source.** The plan says device numbers lead. No 12 GB device run exists yet, so this draft leads with desktop-proxy numbers, labelled as such.
> - **1B-class gap on the held-out set: not run.** The plan requires it with a paired CI. The only size ladder shown is from the development set on an earlier engine.
> - **Seeds.** The plan planned three runs (seeds 42, 43, 44). Two were run (42, 43), which is the plan's stated minimum.
> - **Not yet reported:** the always-decline level measured on the claim run's own declines; per-writer held-out results; the cross-family judge; the 40-pair human label check.
> - **Pre-registration timing.** Hashes were committed to a private repository before the held-out runs. They have not been published, so an outside reader cannot yet verify the timing. The plan said to publish the combined hash before the first run.

**7. The reference and the judge are the same model family, and the draft does not say so.** Plan §2: references are "Opus 5.5 + web", and the judge is claude-opus-5-5. A skeptical reader will ask about self-preference.
In section 2 "Judge and reference", replace the first bullet with:
> - Each BOAR answer is compared pairwise with a reference answer written by a frontier model (Claude Opus 5.5) with web search (`reference.v1`, generated once and frozen). The judge is the same model family. [S2]

In section 5, replace the "Single judge family" bullet's first sentence with: "**Single model family.** The reference answers and all judging come from Opus models."

**8. The held-out rule is overstated, and the safety level is not independent (sections 2 and 3).** "No engine decision was taken on them" conflicts with the disclosed CO card, which was motivated by v0.2 item A02 (QUEUE l.508, l.515). The 0/10 danger result includes A02.
In section 2, replace the "Dev and held-out are separate" bullet's last sentence with:
> The 110 v0.2 questions are held-out: no engine change was tuned on their scores, with one disclosed exception (below).

In the Safety cards row, replace "0 unsafe-rule hits on the 10 held-out danger questions, both seeds" with:
> 0 unsafe-rule hits on the 10 held-out danger questions, both seeds. One of the 10 (generator indoors) had failed in an earlier run and motivated the CO card, so it is not independent evidence.

In the CO hazard card row, replace the last sentence with:
> The earlier engine gave an unsafe answer on the held-out generator-indoors item. Cut 3 did not, but the card was built after that failure was seen, so this item is excluded from any improvement claim.

### Required: framing and clarity

**9. "Held-out lookalike set" is ambiguous with bench v0.2.** These are separate blind probe sets ("held-out lookalike set #3", QUEUE l.515). In the CO row, replace "Held-out lookalike set:" with "On a separate blind lookalike set (not bench v0.2):". In the Arithmetic row, replace "held-out lookalikes 28/32 right" with "on a separate held-out probe set (not bench v0.2), 28/32 right".

**10. Row 7 mixes V-para category scores into a held-out sentence.** Reasoning 0.348 is a V-para figure from 7 items (CLAIM-RESULTS, "Per category"). No held-out per-category figures exist in the sources.
Replace the row 7 "Basis" cell with:
> Held-out ratio 0.513 (0.479–0.550) on a mix of explanation, reasoning, comparison, synthesis, crypto, travel, health, danger and honesty questions. On the separate V-para set (0.413), the weakest categories were reasoning 0.348 (7 items) and travel 0.36 (8 items). "Above half" is not shown on either set. [S1]

**11. The venue caveat overclaims "a user with a real location fix would not".** The evidence is 6/6 venue checks (3 with GPS) on the desktop proxy (cut3-confirm (b)). The BOAR Bench APK declares no location permission (evidence E1), so the location path has never run on a phone.
Replace the last sentence of the "V-para venues" caveat with:
> A user who types coordinates would get the same gap. When a GPS fix was passed in, the separate V-exact set's venue checks passed 6 of 6 on the desktop proxy. The location path has not been tested on a phone.

**12. "The benchmark ran offline" (row 4) has no source.** The desktop runs ran on a networked machine, and the judge needs the network. See the corrected row 4 below.

**13. APK size "74–80 MB" has no source for 80.** The three BOAR Bench APKs are 77,086,168–77,091,288 bytes (DEVICE-DAY.md; CUT4.md; `ls -l`), and the "74 MB" figure is the same file in MiB. In row 3, write "measurement app (BOAR Bench APK) 77 MB".

**14. The computed-verdict and retrieval levers are summarised imprecisely (section 3, "Levers that failed").** CV and CVO failed their gates on *new* wrong answers (3, and 2). CVS and CVH changed verdicts but lowered the judged score (QUEUE l.596, l.601, l.603, l.618). The rv2 fall has a CI that crosses 0 (QUEUE l.525).
Replace the two bullets with:
> - Larger Wikipedia packs and a new retrieval path: the right sentence reached the model more often (7 → 18 of 56 dev questions), but the judged score did not rise (−0.021, 90% CI −0.054…+0.009). Killed.
> - Computed-verdict arms (four variants): verdict accuracy rose on fresh verdict sets, but two variants introduced new wrong answers and two lowered the judged score slightly. Closed.

**15. The "the post author-style" label invites the reading that he wrote or endorsed the set.** In the TL;DR, replace "**the post author-style blind set (V-para, 51 judged questions):**" with:
> **Blind set in the style of the bounty's example questions (V-para, written by our team, 51 judged questions plus 7 venue questions):**

and add to the end of that bullet: "The 7 venue questions scored 0 of 7 (see section 5)."

**16. The TL;DR label "Fixed on this claim" is unclear.** Replace "**Fixed on this claim:**" with "**Scope of this claim:**".

**17. The frontier ladder table omits BOAR's CI and the difference in runs.** Replace the BOAR row with `| BOAR cut 3 (4B) | 0.413 (0.384–0.445) |`. Replace the note after the table with: "The ladder models ran once each on the 51 items; BOAR's figure pools two runs. BOAR is below a small hosted model (Haiku) without web. This is the gap to close. [S1]"

**18. The held-out gain is missing its CI (section 5, "Dev items in the 167-item view").** Replace "(+0.011 over the previous stack)" with "(+0.011 over the previous stack, 95% CI −0.004…+0.029)".

**19. "A few items per seed" overstates the noise.** Replace the "Run-to-run noise" bullet with: "**Run-to-run noise.** In byte-identity checks, about one answer per seed changes between runs with identical inputs. [S3] [S10]"

**20. "Bench v0.1 (public)" is ambiguous.** No source shows that v0.1 has been published. Replace with "Bench v0.1 (60 items, the planned public split)".

**21. The safety caveat should travel with the card claims.** Add to the end of the Safety cards row and the CO hazard card row: "Card texts are AI-reviewed, not clinically reviewed."

## C. Corrected checklist rows (replace rows 1, 2, 3, 4, 5, 6, 8, 12)

Evidence keys:
- **E1, static network audit of the measurement APK (this review).** I ran `PATH=~/Library/Android/sdk/build-tools/36.0.0:$PATH python3 boar-app/scripts/audit-apk.py <apk> --out <dir>` (upstream offline-proof tool v0.2.0, stdlib + aapt2, sha256 5985e33f…d4ed) on all three BOAR Bench APKs: cut 3 `a02b55e6…` (the one run on the A15), cut 4 `80925f6a…`, and final cut 4 `22e22f2c…`. Results, identical for all three:
  - Verdict **NETWORK-CAPABLE**. The APK declares `android.permission.INTERNET` and includes OkHttp, React Native networking, WebSocket and DownloadManager classes. The tool lists 19 hosts to review (for example download.geonames.org, archive.org).
  - **Google Play Services / Firebase: none found. Tracker SDKs: none found.** Remote code loading: none.
  - The APK is debuggable and signed with the public Expo debug key. No location permission is declared.
  - Cross-check: `aapt2 dump permissions` agrees, and `bench-app/android/app/src/main/AndroidManifest.xml` declares INTERNET.
  - Reports were written to the session scratchpad only, not to the repo; anyone can reproduce them with the command above.
- **E2, the upstream app has an offline build variant and a prior offline proof.** `boar-app/plugins/withBuildVariant.js` builds an "offline" variant that strips INTERNET and the network-state permissions. `rnd/bench/legal/README.md` §4 records the audit verdict for a "BOAR offline `1928502d`" build as ✅ offline by construction (no INTERNET, no GMS or tracker classes; debug-signed). That build does **not** contain the measured engine (the Android UI uses the legacy path; QUEUE l.645). The underlying reports are in the quarantined rnd/veil/ and were not read.
- **E3, network state of the A15 run.** `device/a15-smoke-2026-10-05/device.json` and `bench.json` record no airplane-mode or network state. Earlier device runs of the older 1.5B engine were in airplane mode: `boar-eval/reports/devices-2026-10-02/android-g75.md` and `ios-q15.md`.
- **E4, GrapheneOS.** No device has been tried. `rnd/research/summit/S1-memo.md` says nobody on the team has tested one.

| # | Requirement | Status | Basis |
|---|---|---|---|
| 1 | Runs on Android and GrapheneOS-compatible hardware | **Partly met** | Cut 3 ran on one Android phone (Galaxy A15, 8 GB, 9-question smoke test, 9/9 completed). No GrapheneOS device has been tried. A static scan of the measurement APK finds no Google Play Services or Firebase code (E1). [S5] [S6] E1 E4 |
| 2 | Within 12 GB RAM | **Partly met** | Use the text from issue 4. |
| 3 | Total size at most 50 GB | **Met** | Device kit 3.03 GB in total (model 2.50 GB, detector and embedding 0.15 GB, knowledge packs 0.39 GB), plus the 77 MB measurement app. The V-para places kit size is not recorded but does not change the conclusion. [S11] [S10] |
| 4 | Works completely offline | **Not yet verified** | The engine is designed to run from local files. No run of the measured engine has a recorded offline state: the A15 smoke test did not log airplane mode (E3), and the desktop runs used a networked machine. Earlier phone runs of the older 1.5B engine were in airplane mode (E3). The measurement APK can open network connections (E1). [S5] E1 E3 |
| 5 | No API calls or network requests in use | **Not yet** | A static audit of the measurement APK (BOAR Bench, cut 3 and cut 4) gives **NETWORK-CAPABLE**: it declares INTERNET and lists 19 hosts to review (E1). No dynamic capture exists. The upstream app has a no-INTERNET build variant, and an earlier upstream offline build passed this audit (E2), but that build does not contain the measured engine. Closing this row needs the engine in the offline variant, plus the static audit and a per-app traffic count during a run. (The judge calls are in the evaluation harness, not the app.) E1 E2 |
| 6 | No Google Play Services for core function | **Partly met (static only)** | No Google Play Services, Firebase or tracker classes in any of the three measurement APKs (E1). Never run on a device without Play Services (the A15 is a stock Samsung phone, and no GrapheneOS device has been tried). E1 E4 |
| 8 | Speed that feels usable | **Not met on the phone** | Use the text from issue 3. |
| 12 | Real-device requirement | **Partly met** | One 8 GB phone smoke test of cut 3 (9/9 completed, 2 wrong answers, model answers 100–147 s). Cut 4 has not run on a phone, and the 12 GB run is pending. The bounty requires a stranger to install from a public repo in minutes; that path does not exist yet (rows 9 and 10). [S5] |

Rows 7 (see issue 10), 9, 10, 11, 13 and 14 stand as drafted.

The UNKNOWN list in the draft should drop "Whether any core path needs Google Play Services" and instead read: "Whether any core path needs Google Play Services at run time. A static scan finds no Play Services code, but it has never run on a device without them."

## D. Sentences a skeptical reviewer would attack (after the fixes above)
- "About half" (TL;DR) is fair only because the CI, the V-para failure and the Haiku gap sit next to it. Keep all three in the same paragraph wherever the 0.513 is quoted, including the demo post.
- The ratio is relative to a same-family reference and judge (issue 7). Until the cross-family judge runs, expect "the judge likes its own style" as the first objection. The plan's rule (take the lower ratio if they differ by more than 0.05) should be quoted wherever the headline appears.
- The deep-tier row ("+0.06 on the desktop") should add "and failed the memory limit (peak 10.0–10.3 GiB)" (QUEUE l.253). Otherwise it reads as an unused upgrade.

## UNKNOWN
- Size of the places kit used in the V-para run.
- Whether the measurement APK actually sends anything during a run. Only static capability is known (E1); no traffic count exists.
- Whether the "74 MB" in DEVICE-DAY.md is MiB (77,086,168 B = 73.5 MiB). I assumed it is.
- Whether bench v0.1 has been published anywhere (issue 20).

# Review v3.2 (independent Opus, 2026-10-07 18:53)
Target: CLAIM-DRAFT.md v3.2 (269 lines) + CLAIM-DRAFT-v3.2-changes.md. Read only; 0 runs, 0 model/judge calls; blind/ and rnd/veil/ not read.
**Verified as stated:** three-scale table and V-para scales (CLAIM-RESULTS-cut3 l.24, l.61); cut 6 row (CLAIM-RESULTS-cut6 l.36, l.73, l.47); 0.397 and 0/0/110 (s42), V-para 0/51, Haiku floor 0.48 (PIPELINE-AUDIT l.13–15); CUT7 build, gates, fire counts (CUT7 l.10–30); VENUEGPS-2 7/7, 10/10, +3.65 MB, 5–192 ms (l.2–24); JUDGE2 49/57, 50/57, +0.110/+0.112, κ 0.32/0.55, +0.026 vs +0.029 (l.18–37); MOESCREEN 0.603/0.613/0.596/0.487, +0.108; DEEPROUTE +0.057, ×7.1, R2 26 %/+0.033/58 %/×2.4, 84 %; BENCH-V03 timeline (l.10, §7); Haiku/PARJUDGE 54/57, ≈14×, 55/57, +0.007; FTDATA 16→11→6/20. Bar wording ("not shown above", CI contains 0.50) at l.12 and l.156; deep tier "no device result" at l.185; "AI-reviewed, not clinically reviewed" at l.98, 101, 166, 204.

| id | sev | draft line | issue | required edit |
|---|---|---|---|---|
| B1 | BLOCKER | 21, 143, 144, 146, 147, 150, 154, 195–197, 240, 252 | Device record is stale. QUEUE l.711: cut 6 (bench.json engine tree b0f53fe0, patch 824e0b35) ran **73/73 v0.1 on the A15**, device.json `airplaneModeOn: true`, `networkPermissionAbsent: true`; fast p50 49 s / p90 77 s / max 111 s; instant p50 8.5 s; PSS max 4.41 GiB; thermal 0; phone 0.561 (0.507–0.617) vs desktop 0.558/0.560 on the same 57 (judge.v1-med). QUEUE l.695: cut 5 rate sweep ran (airplane, 9/9; decode 2.0–2.7 tok/s; thread ranking within noise; q8 KV unmeasured). The draft says "the only real-phone run … is a 9-question smoke test of cut 3", "cut 4 and cut 5 have not run on a phone", "no run of the measured engine has a recorded offline state", "sweep built but not run", E5 "none has been run on a phone". | Replace l.21 with: "**Device status (8 GB phone only; no 12 GB phone run):** cut 6 (the claim build minus the facts tier) ran the 73 v0.1 questions on an 8 GB Galaxy A15 with airplane mode on and the network permission absent: 73/73 completed; model answers p50 49 s, p90 77 s, max 111 s; instant answers p50 8.5 s; app memory (PSS) max 4.41 GiB; thermal status 0. On the 57 judged items the phone scored 0.561 (0.507–0.617) against 0.558 and 0.560 on the desktop: device quality equals desktop within noise. These are development items the engine was tuned on, so this is not evidence for the bar. A cut 5 rate sweep on the same phone measured decode at 2.0–2.7 tokens/s. The earlier 9-question cut 3 smoke test (model answers 100–147 s) predates the KV-cache fix. Cut 7's facts tier has not run on a phone. [S28]" Add S28 = `rnd/research/QUEUE.md` l.695, l.711; `boar-eval/runs/device-tester-a15/final-cut6-v01/` (device.json, bench.json). Update rows 1, 2, 12 with the cut 6 run; row 4 → "**Partly met (one 8 GB phone run)** … cut 6 no-network APK, airplane mode on, network permission absent (device.json); no traffic capture"; row 5: add "the cut 6 no-network APK (cca28caf…) ran on the phone"; row 8 status → "**Not met on the phone (cut 6 measured on an 8 GB phone)**", lead with the measured 49/77/111 s, then drop the 69/89 s projection or label it superseded; E5 last sentence → "The cut 6 no-network APK ran 73/73 on the A15 (S28)." §7: delete l.195–197 as open items, add "cut 7 on a phone" and "ABBA rerun of the cut 5 speed A/B (QUEUE l.699, order confound)". Never quote the dev-set CI lower bound 0.507 as "above 0.50". |
| M1 | MAJOR | 131, 132, 135, 193, 253 | Cut 6 is cut 5 + DETMAX, not "cut 4 plus deterministic-module extensions". DETMAX.md l.3 "Arm = cut 5 + one rule … branch coord/detmax from coord/cut5lite"; QUEUE l.694 "cut 6 = cut 5 + DETMAX"; `git merge-base --is-ancestor` in wt/cut7: 07f65d69 (CUT5-SPEED 2, .nosrc KV prefix) and 7173c9af (CUT5-SPEED 3, gate skip) are ancestors of 6d0b93b1. The patch file name `detmax-on-cut4` is misleading. | l.132 → "**Cut 6** \| Cut 5 plus DETMAX (with history, the emergency detector scores the window and the current turn alone and takes the max). Claim re-run …". l.131 append "Included in cut 6 and cut 7." l.135 last sentence → "Cut 5's two phone-latency changes are in cut 6 and cut 7 (commit ancestry), so the cut 6 held-out re-run (0.512) already includes them." Delete the l.193 "Record whether …" sentence and the second sentence of l.253. |
| M2 | MAJOR | 120, 185 | "peak memory 10.0–10.3 GiB against an 8 GiB limit": QUEUE l.267 says the ≤ 8 GiB was our own per-process estimate, not a bounty rule, and 10.0–10.3 GiB is macOS peak footprint (max RSS 4.0–8.7 GiB). Engine-path deep numbers use the old main 0cfd4a77 4B as base (DEEPROUTE l.8), not cut 7. | l.120 → "Quality +0.060 (CI +0.021…+0.101) on the desktop (old main engine); desktop peak footprint 10.0–10.3 GiB (max RSS 4.0–8.7 GiB) against our own ≤ 8 GiB per-process estimate for 8 GB phones. Parked; not part of this claim." l.185: "Peak memory 10.0–10.3 GiB needs a 12 GB phone" → "Desktop-only: phone memory and speed are unmeasured; the desktop footprint (10.0–10.3 GiB) points to a 12 GB phone, and none is available." Name the base of +0.060 (QUEUE l.271) vs +0.057 (DEEPROUTE l.3) or use one. |
| M3 | MAJOR | 164, 183 | "So the judge family moves the ratio level by about 0.11" generalises one local, Q2-quantised model on v0.1 dev (2 systems) to a family; l.183 "+0.11 level shift" can read as a correction. | l.164 → "One non-Claude judge (Gemma 4 26B-A4B, Q2 quantised, run locally) scored the ratio 0.11 higher than Opus on v0.1 for both systems tested. That quantifies how much the level depends on the judge; it is not a correction to the headline, and Gemma is not a substitute headline judge." l.183 → "A local Gemma judge scored v0.1 0.11 higher than Opus with the same ranking (quantification, not a correction)." |
| m1 | MINOR | 163 | Open point (a); see resolution below. | After "…'location unavailable'." insert: "The items carry no location field; the engine routed all 7 as 'near the device' and does not turn a place or coordinates typed in the question into a location fix, so a user who types a place instead of sharing location gets no venues." |
| m2 | MINOR | 100, 163 | Location-only 0/7 is seed 42 only (VENUEGPS l.4); "0/7 without either" is ambiguous. | l.100 "(0/7 without either)" → "(0/7 with no location, both seeds; 0/7 with location but no tile, seed 42 only)"; l.163 "gave 0 of 7" → "gave 0 of 7 (seed 42; seed 43 not run)". |
| m3 | MINOR | 11 | OSM caveat only by pointer. | "…returned venues on 7 of 7, both seeds" → "…returned ≥ 3 OSM-gold venues on 7 of 7 (10 per item), both seeds; engine venues and gold both come from OSM diet tags". |
| m4 | MINOR | 12, 22 | 96.7 % and 323/334 pool v0.1 dev item-seeds (CLAIM-RESULTS-cut6 l.21–25); s42 v0.2 alone is 105/110. | l.12 "(seed 42, 96.7 % …)" → "(seed 42; 105 of 110 answers byte-identical to cut 3)"; l.22 "323 of 334 judged item-seed answers" → "210 of 220 held-out item-seed answers". |
| m5 | MINOR | 182 | Future result stated as fact; v0.3 keeps the Opus judge (BENCH-V03 l.12). | "Gives the first final number from an unexposed set." → "Planned to give the first number from an unexposed set; the judge stays Opus, so judge-family bias remains." |
| m6 | MINOR | 192 | Personal handle in a text meant for publication (CLAUDE.md Rules). | "r4to writes" → "the project owner writes". |
| m7 | MINOR | 149, 17 | Row 7 leads with raw only (v3.1 D1); table still says "Held-out" for an exposed set. | Row 7 → "Floor removed 0.389, raw 0.513 (0.479–0.550) on …"; l.17 label → "v0.2, formerly held-out (exposed) (110)". |
| m8 | MINOR | 99, 167 | Facts tier excludes Portuguese/Spanish, health, card emergencies, detector fires (CUT7 l.36), not "non-English"; bar is 75 % partial / 85 % pass (FACTS-r6-SET4 l.5). l.167 "weak answer" has no number. | l.99 "non-English" → "Portuguese or Spanish"; "below its 75 % bar" → "below its 75 % partial bar (pass 85 %)". l.167 "still gets a weak answer" → "gets no card, only the model answer". |

**Verdict: ACCEPT WITH EDITS.** Headline numbers, bar wording, venue condition, deep-tier label and the safety caveat check out against sources. B1 and M1–M3 are mandatory before the draft counts as reviewed; B1 changes rows 1, 2, 4, 5, 8, 12, §7 and E5, so the writer should send those rows back for a spot check.
**Open point (a), venue cause:** state both, as one statement. The sources agree on the mechanism: no location fix reached the engine (VENUEGPS l.8 no-location 7/7; CLAIM-RESULTS-cut6 l.89 "the engine gets no GPS fix"). They disagree only on what the question text holds: cut 3/cut 6 results say "coordinates in the question text" (citing RUN-MAPPING "located by their text"), while VENUEGPS found no location field, took the coordinates from the gold files' `user_location`, and saw route `near:device`. Neither runner read question text (script-only), so the draft should not claim either way. Use the m1 sentence; the coordinator should annotate CLAIM-RESULTS-cut3 l.71 and -cut6 l.89 with a pointer to VENUEGPS.
**Open point (b), cut 5 in cut 7:** RESOLVED, YES (M1 evidence: DETMAX.md l.3, QUEUE l.694, git ancestry). The UNKNOWN goes away, and so does "whether held-out moves on cut 5": cut 6 = cut 5 + DETMAX was measured at 0.512 (Δ −0.001 vs cut 3).
**Notes outside the draft:** (1) CLAIM-RESULTS-cut6 l.11 reports gate counts "same as cut 3" (109/110) although cut 5 skips the gate on 32 of 54 v0.1 calls (CUT5LITE): this is UNKNOWN; answers are unaffected (CUT5LITE G2 120/120). (2) CLAIM-RUNS-cut6 l.3 cites the cut 3 partial phone 0.482, which QUEUE l.711 marks invalid (wrong refs, WRONGREFS-*); the draft must not cite it. (3) The CLAUDE.md state block ("JUDGE2 partial … full run pending"; no A15 cut 6 result) and REPRO-PLAN l.26 ("cut 6 never on a phone") are stale.
