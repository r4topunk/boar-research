# Claim readiness for poidh #31 (coordinator audit, 2026-10-10)

TL;DR: the evidence side is complete for the 4B claim build (cut 7) except a v0.3 number. The submission side is not started: no public repo with cut 7, no installable APK that runs the measured engine, no demo post, and the claim vehicle (update #124 or a new claim) is undecided. Deadline 2026-10-31 (`BOUNTY_31.md`). Read-only audit; nothing under blind/ or rnd/veil/ was read; v0.3 item files were not opened.

## 1. Checklist: bounty need → BOAR state → gap (owner, size)
| # | Need (source) | BOAR has | Gap | Owner | Size |
|---|---|---|---|---|---|
| a1 | poidh claim: screenshot + link to post + link to repo (`BOUNTY_31.md` Proof) | nothing posted (`CLAIM-DRAFT.md` l.5 "Nothing here has been posted") | screenshot of cut 7 answering offline; poidh form | r4to | S |
| a2 | public demo on X or Farcaster: offline, several queries incl. ones a 1B fails, repo link, approach (`BOUNTY_31.md`) | draft text only (`CLAIM-DRAFT.md` §1, row 13 "Not yet") | video/post on a phone in airplane mode; query list chosen from dev items | r4to (post), coordinator (query list, text) | M |
| a3 | what competitors attached (`CLAIMS_31.md`) | — | a competitor team #125: repo + X post + signed APK release + HF corpus link; Boar #124: repo + X post + approach text; a competitor team #115: Farcaster + GitHub + offline-phone screenshot. Signed APK + corpus link is the highest bar seen | — | — |
| a4 | claim vehicle | Boar is already claim #124 (the app maintainer, 1.5B description); "materially different from the version reviewed" can disqualify (`QUEUE.md` l.255) | update #124 vs a new claim: UNKNOWN; needs the app maintainer and possibly the issuer | r4to + maintainer | S |
| b1 | claim build identified | cut 7 = commit 6d0b93b1 on local branch `coord/cut7` (`wt/cut7`), tree 7c96e59e, 4B only (`CLAUDE.md`) | none | — | — |
| b2 | app on real Android hardware, installable in minutes (`BOUNTY_31.md` Real-device) | upstream APK v1.0.0 = Qwen2.5-1.5B, Sep 26 (`boar-app/README.md` l.141–150); BOAR Bench APK = debuggable, no chat UI, package team.sopa.boarbench (`DEVICE-DAY.md` l.9; `bench-app/README.md`) | no APK of cut 7 with a chat UI exists | maintainer (build) + coordinator (engine handoff) | L |
| b3 | the UI runs the measured engine | Android ChatScreen uses legacy runAdaptiveChat, 0 imports of answerService (`QUEUE.md` l.472; `CLAIM-DRAFT.md` §4 note) | wire `src/ui-android` to answerService | maintainer | L |
| b4 | signed release | release workflow with keystore secret on the upstream repo (`boar-app/docs/RELEASING.md` l.4, l.28) | who holds the key: UNKNOWN (maintainer by the doc) | maintainer | S |
| b5 | public GitHub repo with the functional version + all code (`BOUNTY_31.md`) | engine base 0cfd4a77 public; cut 6/7 patches and claim runner local only (`REPRO-PLAN.md` TL;DR, §1); packs public on HF `r4topunk/boar-packs` (`REPRO-PLAN.md` §1) | publish cut 7 source + harness snapshot (REPRO-PLAN Option C), REPRODUCE.md (L6) | coordinator (prep), r4to (OK, O1) | M |
| b6 | fork rule | fork r4topunk/boar-app is PUBLIC (`CLAUDE.md`); `coord/*` incl. cut 7 not on origin (`git branch -r --contains 6d0b93b1` = empty); origin already carries `spike/moe-deep`, `wip/*` | never push `coord/*`, arm patches, deep-tier (depth.ts, DEEP_THINKING_BUDGET) or bench hooks to origin; engine changes stay local (memory: no engine PRs upstream) — conflicts with b5, see Decisions | r4to | S |
| c1 | which numbers go public | floor-adjusted + win-rate first, raw second, three scales shown together (`CLAIM-DRAFT.md` §1): V-para 0.261 (0.224–0.299) win 0/51; v0.2 0.389 (0.347–0.435) win 0/110; raw 0.413 / 0.513 [S1] | none; bar "not shown" (row 14) | — | — |
| c2 | held-out status | v0.2 burnt → dev; V-para held-out for 4B claim runs only, dev-style after 10-06; only es-fresh2 clean (`EXPOSURES.md` TL;DR) | a final number needs v0.3 | — | — |
| c3 | v0.3 (non-Claude items) | spec + infra ready; schedule items 10-08…10-17, refs 10-18…19, freeze 10-20, claim run ≤ 10-24 (`BENCH-V03-SPEC.md` §1, §7) | 0 items: no `boar-eval/bench/v0.3/work/` (ls 10-10); pilot due 10-08 not logged; 60-item fallback exists (§7) | r4to | L |
| c4 | independent-review trail | CLAIM-REVIEW.md, -v3.5…-v3.8 (all ACCEPT WITH EDITS, applied; `QUEUE.md` v3.7/v3.8 entries); safety caveat "AI-reviewed, not clinically reviewed" (§5) | review of the final public text (post + README) once written | coordinator | S |
| c5 | device evidence | cut 6 on 8 GB A15: 73/73, p50 49 s, PSS max 4.41 GiB, airplane mode (`CLAIM-DRAFT.md` §1 [S28]) | cut 7 on any phone; a ≥ 11 GB phone; GrapheneOS / no Play Services; dynamic network capture (§7) | r4to (relay to tester) | M |
| c6 | speed "usable" | row 8 "Not met on the phone" (`CLAIM-DRAFT.md` §4) | wording in the post; no lever open on the 4B side (`HANDOFF-2026-10-10.md` 15:28) | coordinator | S |
| d1 | deep tier reported separately | "Reported separately if ever used; not in this claim" (`CLAIM-DRAFT.md` §6); V-para 0.436, v0.2 0.508, win 0 (`HANDOFF-2026-10-10.md` §2) | stays out of the claim build | — | — |
| d2 | deep-tier device feasibility | runbook with frozen gates (decode ≥ 4 tok/s, RSS ≤ 9 GB, 3/3) for an 11 GB POCO tester (`deep/ADB-PROBE-RUNBOOK.md`; `HANDOFF-2026-10-10.md` §5); maintainer note not sent (`handoff/DEEP-TIER-2026-10-10.md` l.2) | relay runbook; app bmoe module (D2) and app-side thinking cap (D6) not built | r4to (relay, OK to send note), maintainer (D2) | M (probe) / L (app) |
| e1 | document models/datasets + licences (`BOUNTY_31.md`) | Qwen3-4B, Qwen3.6-35B Apache-2.0 (`rnd/kiln/MODELS.md` l.15, l.18; REPRO-PLAN L6); bge MIT, Wikipedia/Wikivoyage CC BY-SA, GeoNames CC BY 4.0 (REPRO-PLAN L6); boar-app MIT "aoair contributors" (`boar-app/LICENSE`) | public BOM not written (row 11 "Partly met") | coordinator | S |
| e2 | emergency detector redistribution | v3b gguf + head local only; mmBERT base licence UNKNOWN (`REPRO-PLAN.md` §1, L8) | check licence or ship as optional | coordinator | S |
| e3 | reference answers in the repo | Opus+web refs gitignored; "publishing text needs a licence/ToS decision" (`REPRO-PLAN.md` §1) | publish hashes only, or decide | r4to | S |
| e4 | crypto/places pack sources | crypto pack public on HF; per-source licences listed for candidate packs (`KNOWLEDGE-PACK-SIZING.md` l.76–82); claim crypto pack per-source licence not in files read | UNKNOWN for the shipped crypto pack; places kit size not recorded (`CLAIM-DRAFT.md` §3) | coordinator | S |

## 2. Decisions (needed; none taken here)
- D-A (r4to + maintainer): claim vehicle — update #124 or submit a new claim; ask the issuer only through r4to (`QUEUE.md` l.255).
- D-B (r4to): where cut 7 source goes public — fresh repo snapshot (REPRO-PLAN Option C) vs a tagged branch on the public fork vs upstream; must be reconciled with "engine changes stay local / no engine PRs upstream".
- D-C (r4to): v0.3 at 110 items, 60-item fallback, or no v0.3 (claim then says "no unexposed set").
- D-D (r4to): send `handoff/DEEP-TIER-2026-10-10.md` and the runbook relay, or not.

## 3. Options
- O1: ship the claim as BOAR Bench + desktop numbers + cut 6 A15 run, with the UI wiring left to the app maintainer (no installable chat app → fails "running locally within a few minutes" reading).
- O2: maintainer wires answerService and ships a signed v1.2 APK with cut 7 (closes b2–b4; depends on maintainer time).
- O3: attach the deep tier as a separately labelled "12 GB option" only if the tester probe passes its frozen gates.

## 4. Tasks (proposed order; dates are targets, not commitments)
| By | Task | Owner | Size |
|---|---|---|---|
| 10-13 | D-A, D-B, D-C taken; v0.3 wave-2 go/no-go (`BENCH-V03-SPEC.md` §7) | r4to | S |
| 10-14 | engine handoff for answerService wiring + cut 7 patch delivered locally to the app maintainer (after D-B) | coordinator | M |
| 10-17 | v0.3 items (110 or 60) | r4to | L |
| 10-20 | v0.3 refs, gates, freeze | r4to + coordinator | M |
| 10-21 | APK with cut 7 + answerService, signed | maintainer | L |
| 10-22 | public BOM / REPRODUCE.md / licence table; repo snapshot staged locally, scrubbed of blind/, veil/, v0.2 plaintext | coordinator | M |
| 10-24 | v0.3 claim run on cut 7 (one run) | coordinator (Kiln) | M |
| 10-25 | cut 7 APK on a phone (tester), airplane mode, ideally ≥ 11 GB, no Play Services | r4to (relay) | M |
| 10-26 | final claim text + independent Opus review of post and README | coordinator | S |
| 10-28 | repo public (r4to OK), demo video + post on X/Farcaster | r4to | M |
| 10-29 | poidh submission (screenshot + post + repo) | r4to | S |
| 10-31 | deadline; buffer 10-30 | — | — |

## UNKNOWN
- Whether #124 can be updated in place or a second claim is allowed (`QUEUE.md` l.255).
- Who holds the release keystore and whether the app maintainer will build cut 7 into the app.
- v0.3 progress: no items found in `boar-eval/bench/v0.3/`; items may live elsewhere (not searched).
- mmBERT base licence; per-source licence of the shipped crypto pack; ToS for publishing Opus reference text.
- Whether the community tester (POCO, 11 GB) will run anything; GrapheneOS behaviour; dynamic network behaviour.
- `CLAIM-DRAFT.md` l.3/l.5 still say "pending independent review" while l.1 records v3.8 as reviewed: header wording to fix before any public use.
