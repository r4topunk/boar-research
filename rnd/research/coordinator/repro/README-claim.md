# BOAR: offline research assistant for Android (poidh bounty #31 claim, cut 7)

> **Public-release path map (v1.1.2).** This file was written for the first single-package release. Read `boar-eval/...` as `boar-bench/...` (sibling repository) and `engine/...` and `tools/...` as this folder (`rnd/research/coordinator/repro/`); other workspace-relative paths resolve in `boar-research` or `boar-bench` unless `docs/EXCLUDED.md` lists them as withheld. Full table: [REPRODUCE.md](REPRODUCE.md), section "v1.1 layout".

DRAFT, not published. Numbers are copied from the claim draft v3.8, section 1 (now [METHODS.md](METHODS.md)); nothing here is new evidence.

## What it is and how it works
BOAR answers English research questions on an Android phone with no network. The claim build is **cut 7** (engine commit 6d0b93b1, content tree 7c96e59e…). The download is 3.03 GB in total, model included ([BOM.md](BOM.md)).
- **Answer model:** Qwen3-4B-Instruct-2507 (Q4_K_M, 2.50 GB). It answers with citations from passages retrieved from small curated packs (English Wikivoyage, a crypto/Ethereum pack; packs about 0.39 GB).
- **Instant tiers (code answers, no model call):** a facts table built from Wikidata (CC0) for single-fact and two-entity numeric questions; a travel calculator (distance, round trip, time at a stated pace; labelled "an estimate, not a mapped route"); safety and health cards (AI-reviewed, not clinically reviewed) behind a learned emergency detector that routes emergencies before the model; a venue path that lists nearby places **with device location and the user's area tile** (OpenStreetMap tags).

## Results: three scales, always shown together
Judge: Claude Opus (`judge.v1`), pairwise against a reference answer written by Claude Opus 5.5 with web search, both A/B orders, two seeds, stratified bootstrap 95 % CIs.
- **Raw judge ratio vs the frontier reference:** sum of BOAR scores / sum of reference scores (1–5 rubric). A system that declines every question already scores raw 0.306, so raw 0.50 does not mean "half as good".
- **Floor-adjusted ratio:** the same ratio with the judge's minimum score subtracted from both sides.
- **Win-rate:** pairwise wins of the BOAR answer over the reference answer.

| Set | Status | Raw ratio (95 % CI) | Floor-adjusted (95 % CI) | Win-rate |
|---|---|---|---|---|
| V-para: 51 bounty-style judged items (+7 venue items) | held-out for the 4B claim runs (cut 3, cut 6); development-style for everything measured after 2026-10-06 | 0.413 (0.384–0.445) | 0.261 (0.224–0.299) | 0 of 51 |
| bench v0.2: 110 items written by Claude-family writers | dev (exposed after the claim runs) | 0.513 (0.479–0.550) | 0.389 (0.347–0.435) | 0 of 110 (cut 6 re-run, seed 42; 0/0/110) |

**Bar not shown above.** The bounty bar is ">50 % as good as internet + frontier AI". The raw ratio is the formal rule of our 2026-10-02 analysis plan; on it, V-para is 0.413 (below 0.50) and v0.2 is 0.513 with a CI that contains 0.50. Floor-adjusted is 0.261 and 0.389, and the win-rate is 0 on both sets. We do not claim the bar is met on any scale. Context: a Claude Haiku with no web scores raw 0.588 (floor-adjusted 0.48) on the V-para items.

Cut 7 = cut 6 + the facts tier. The facts tier fires on 0 of 110 v0.2 and 0 of 58 V-para questions, so cut 7's answers on those sets equal cut 6's (engine replay identical); numbers were measured on cut 3 and re-run on cut 6 (v0.2 raw 0.513 on cut 3, 0.512 on cut 6; V-para raw 0.413 on both).

The 7 V-para venue items: 0 of 7 in the claim run (no device location passed); 7 of 7 with device location and the user's area tile, both seeds (desktop, development-style). Engine venues and gold both come from OSM diet tags, so this shows the path works, not that the venues are good.

## Device runs
| Build | Phone | Result |
|---|---|---|
| cut 6 | 8 GB Galaxy A15 | 73/73 v0.1 items, model answers p50 49 s, p90 77 s, PSS max 4.41 GiB, airplane mode, no network permission |
| cut 7 | none | no phone run yet; BOAR Bench cut 7 no-network APK built (debug-signed, not hosted), sha256 6eb8cb45…, engine tree 7c96e59e… identical to the desktop claim tree |

Speed (cut 6, 8 GB A15): model answers p50 49 s, p90 77 s; instant answers p50 8.5 s. On the 57 judged v0.1 items the phone's raw ratio was 0.561 (0.507–0.617) against 0.558 and 0.560 on the desktop (raw only; floor-adjusted and win-rate not computed for this comparison); those are development items, not evidence for the bar.

## What is different
- **Facts tier:** instant answers from a fixed Wikidata (CC0) table, each ending with its source line.
- **Venues:** "best vegan restaurants" style questions are answered **with device location and the user's area tile** (one tile 0.2–1.1 MB).
- **Safety cards:** fixed first-aid and hazard text from official sources, shown before the model. AI-reviewed, not clinically reviewed.
- **No-network APK by construction:** the no-network builds of the measurement app (BOAR Bench, cut 4 to cut 7) have no INTERNET permission; static audit NO-NETWORK-BY-CONSTRUCTION, no Google Play Services or Firebase classes.
- **Exposure ledger:** every generation run and judge pass on a held-out set is logged in a team-internal ledger (not in this package; the status of each set is in [REPRODUCE.md](REPRODUCE.md) section 6).

## Limits
- **Speed on the phone: not met as usable.** Cut 6, 8 GB A15: model answers p50 49 s, p90 77 s.
- **No unexposed English set.** v0.2 is dev data; V-para is held-out only for the 4B claim runs. A final number would need a new set written outside the Claude family.
- **The judge is a closed model** (Claude Opus), the same family as the reference writer and the v0.2 writers. No human label check yet.
- **Win-rate 0 everywhere:** no BOAR answer beat the reference on either set.
- **Deep tier:** a 35B-class research configuration is measured separately on the desktop; it is not in this claim.
- **No installable chat app yet.** The Android chat UI does not yet run the measured engine path; only the measurement app (no chat UI, driven over adb) does. No public repo or phone install steps yet.
- Claim numbers are desktop-proxy runs. Cut 7 has not run on a phone; no 12 GB phone and no GrapheneOS device have been tried.
- Safety and health cards: AI-reviewed, not clinically reviewed. Safety checks are small (10 held-out danger questions, 0 unsafe-rule hits).

## More
- [REPRODUCE.md](REPRODUCE.md): rebuild cut 7 from a public commit plus one patch; run the public dev bench v0.1.
- [BOM.md](BOM.md): every model, pack, tile and APK with bytes, sha256, licence and URL.
- [METHODS.md](METHODS.md): the full claim draft v3.8 (judge, frozen plan, lineage, requirements, caveats).
- Exposure ledger: team-internal, not published; per-set status in [REPRODUCE.md](REPRODUCE.md) section 6.
