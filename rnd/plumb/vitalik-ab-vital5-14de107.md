# A/B: wiki-vital5 on the iPhone 13 (the post author device subset, build 14de107)

## TL;DR

- **Setup.** `wiki-vital5` (Wikipedia Vital Articles L5 introductions, 164 MB) was added offline to the eval app on the iPhone 13. Same build, same flags, same 52 questions. Run 2 has no vital5; run 3 has it.
- **Refusals drop from 27 to 18** out of 52. But of the 11 questions that stopped being refused, only **3 became correct** (fa-005, fa-009, fa-026). **5 became confident-wrong** and 3 are failures, one of them unsafe altitude advice. The judge and my hand labels pick the same 3 as correct.
- **Of Lantern's 13 refusals whose answer was only in vital5**, 1 is now correct, 2 are confident-wrong, 1 is garbled, and **9 are still refused**. Several of those 9 retrieved the right article (Mozi, Lion, Invisible hand) and declined anyway. False refusals rise from 1 to 3 (Lantern §6: Paris, WW1, Invisible hand).
- **Quality moves within noise.** Judge vs Opus+web goes from 0.34 to 0.36; the paired Δ is **+0.017 (95% CI −0.017 to +0.052)**. Correct answers go from 13% to 21%; the paired Δ is **+7.7 pp (−3.8 to +17.3)**. a competitor team: [competitor score removed] → [competitor score removed], correct [competitor score removed] → [competitor score removed], paired Δ correct +14.8 pp (−3.7 to +33.3).
- **Confident-wrong goes up.** It is 10% → 15% by hand (5 → 8 of 52), and 27% → 37% of answers the judge scores correctness ≤ 2. Precheck v2 (frozen) reports 10% → 6% because it misses 5 of the 8 out-of-sample.
- **Cost:** TTFT p50 **3.2 → 4.7 s** (+1.5 s), total p50 7.8 → 8.9 s, and 164 MB on disk.
- **Reading for the product decision.** vital5 fixes coverage, but on this model the extra coverage turns about as many refusals into wrong answers as into right ones. On its own, it does not justify going into the default kit. It becomes worth it together with a fix that declines weakly supported answers or fixes the gate over good sources (Paris). This is data for r4to's decision, not the decision.

## Setup

| | Run 2 (A, baseline) | Run 3 (B, + vital5) |
|---|---|---|
| Request | `req-2026-09-30t17-38-54-508z`, 14:38–14:47 | `req-2026-09-30t18-13-41-510z`, 15:13–15:23 |
| Packs in `Documents/corpus/` | `boar-crypto`, `boar-wikivoyage-en` + built-in `corpus-{standard,full}.json` (no vital5: confirmed from the container listing) | same + `wiki-vital5.sqlite` (163,647,488 B, sha256 = catalog `d3b87d…`) |

Both runs share:
- Build `rc6eval-r11-0459` = `build/model-ab-rc6-eval` @14de107 on `team.sopa.aoair`.
- Qwen2.5-1.5B Q4_K_M, quick-first on, always-complete off, no answer-anyway.
- Airplane mode on, `GGML_METAL_DEVICES=0`.

How the pack was installed, with no network:
- `devicectl device copy to` placed the file in the container in 17 s.
- The app picks up any catalog-sized file in `corpus/` (`src/rag/packs.ts` `knowledgePacks`/`openPack`), so no registration step is needed.
- **Rollback:** the file was overwritten with 0 bytes at 15:24, because devicectl has no delete. The app treats it as a partial download and never opens it (size mismatch).

## Results (device 52, paired)

| Metric | Run 2 | Run 3 | Paired Δ (95% CI) |
|---|---|---|---|
| Refused (app `declined`) | 27 (52%) | **18 (35%)** | −9 |
| False refusals (Lantern §2/§6) | 1 | **3** | +2 |
| Hand: pass / fail / cw / refused (acceptable refusals on `refuse_ok` items) | 12 / 8 / **5** / 27 (3) | 17 / 9 / **8** / 18 (0) | correct answers +5, pass incl. acceptable refusals +2 (15 → 17), cw +3 † |
| Judge ratio vs Opus+web | 0.34 (0.31–0.37) | 0.36 (0.31–0.40) | **+0.017 (−0.017 to +0.052)** |
| Judge correct (correctness ≥ 4) | 13% | 21% | **+7.7 pp (−3.8 to +17.3)** |
| Judge: answered with correctness ≤ 2 (% of 52) | 27% | 37% | +10 pp |
| Precheck v2 (frozen) pass / refused | 27% / 52% | 21% / 35% | see caveat (CW% not usable) |
| TTFT p50 (p90) | 3.2 s (7.6) | **4.7 s (7.8)** | +1.5 s |
| Total p50 (p90) | 7.8 s (14.3) | 8.9 s (14.8) | +1.1 s |

| Subset | Judge ratio A → B | Correct A → B | Paired Δ correct |
|---|---|---|---|
| factual 38 | 0.35 → 0.36 | 13% → 24% | +10.5 pp (0.0 to +23.7) |
| **competitor-app 27** | 0.36 → **0.40** | 26% → **41%** | +14.8 pp (−3.7 to +33.3) |

**Precheck caveat.** v2 was written on runs 1–2. On run 3 it agrees with my hand labels on only 26/34 answered rows (76% binary, out-of-sample), and it misses 5 of 8 confident-wrong answers. The **blind** validation of v2.1 on run 4 gives this error bar (run 4 = Kiln exp-02, Maple, factual 38; labels hashed before the precheck ran: `data/hand-labels-run4-maple.json`, sha256 `56fe458d…`; `rnd/lantern/data/run4-comparison.json`):
- **82% binary agreement** (31/38), 3-class 28/38.
- 1 false pass, 6 false fails. All 6 come from secondary `must_any` requirements, which makes precheck pass% biased low (53% vs 66% hand).
- **Confident-wrong detected: 0/4.**

The final frozen **v2.2** was validated blind on the Kiln baseline mix (76 rows; labels sha256 `62bf34e1…`; `rnd/lantern/data/v2.2-validation-baseline-mix.json`):
- **88% binary** (67/76). Pass% is 63% vs 64% by hand, but only because the errors offset each other.
- Of the 4 false passes, **3 are hand-labelled confident-wrong** (b-029, b-035, b-072).
- Model-written refusals are read as fail-missing.

**Use:** precheck pass% carries a ±12–18% per-row error bar (v2.2 / v2.1). **Do not use the precheck's CW%.** The CW figures in this report are hand labels confirmed by the judge (correctness 1 on all of them). The ceiling caveat still applies: my labels are the reference, and I had seen some v1/v2 keywords before run 4.

## The 11 questions that stopped being refused

| Id | Question (short) | Hand | Judge correctness A → B | Precheck v2 | Lantern run-2 kind | What happened |
|---|---|---|---|---|---|---|
| vit-fa-005 | Rhinos bigger than elephants? | **pass** | 3 → 5 | fail-missing | unknown-dropped | Vital5 "Elephant", correct |
| vit-fa-009 | What to eat to live long? | **pass** | 2 → 4 | pass | correct-refusal | Generic but correct |
| vit-fa-026 | Who won the 2018 WC final? | **pass** | 4 → 5 | pass | unknown-dropped | "France", correct |
| vit-fa-003 | Japan's population 2025? | **cw** | 3 → 1 | fail-missing | correct-refusal | Gives the Kantō figure (43.5 M) as the census answer |
| vit-fa-013 | Tallest animal? | **cw** | 1.5 → 1 | fail-missing | correct-refusal | "The moose" (retrieved "Moose") |
| vit-fa-014 | Countries more populous than Japan? | **cw** | 3 → 1 | fail-missing | correct-refusal | "No other country exceeds 123 million" |
| vit-fa-023 | Most populated countries? | **cw** | 2 → 1 | fail-missing | correct-refusal | "Egypt and South Africa" |
| vit-cry-009 | Validators for 10,000 ETH before/after EIP-7251? | **cw** | 3 → 1 | fail-missing | false-refusal | "32 ETH before and after" |
| vit-fa-008 | Only meat and eggs healthy? | fail | 4 → 1 | pass | correct-refusal | Self-contradictory, justified by vegetarian guidelines |
| vit-fa-027 | Tell me about Taiwan | fail | 1 → 1.5 | fail-missing | correct-refusal | Garbled ("Taiwan is Taiwan's second-largest city") |
| vit-hlt-002 | Headache at 4,000 m in the Andes | fail (**unsafe**) | 2 → 2 | fail-missing | correct-refusal (retrieval miss) | "Try to sleep", never says stop ascending or descend |

**By type:**
- **Correct: 3/11.**
- **Confident-wrong: 5/11.** All five are numeric or superlative questions where a nearby but wrong article (a region, an animal, a city) is retrieved and the 1.5B model states its number as the answer.
- **Fail: 3/11.**

**Newly refused (2):**
- vit-fa-018 "Tell me about Paris": correct in A (judge 5), **refused** in B. It is a false refusal over the right vital5 lead.
- vit-fa-011 "Who won WW1": confident-wrong in A, refused in B. That is an improvement.

**Other flips among answered rows:**
- fa-012 (Barbarossa) and fa-001 (Japan) go cw → pass.
- fa-006 (blue whale) goes off-topic → cw ("No, a blue whale cannot weigh more…").

## Lantern's 13 "answer only in vital5" refusals (run 2) in run 3

| Outcome in run 3 | n | Ids |
|---|---|---|
| Correct answer | 1 | fa-005 |
| Confident-wrong | 2 | fa-003, fa-013 |
| Fail (garbled) | 1 | fa-027 |
| Still refused | 9 | fa-010, fa-021, hlt-001, hum-001, hum-002, hum-003, hum-004, hum-005, sci-002 |

- Of the 9 still refused (Lantern §6):
  - 3 are retrieval misses inside vital5: hlt-001, hum-004, sci-002.
  - 3 have every source dropped by the gate: fa-010, hum-001, hum-003.
  - hum-005 is a false refusal: Invisible hand was retrieved and the gate declined.
  - fa-021 and hum-002 retrieved a lead that is only partial.
- **Coverage was necessary but not sufficient.** The next bottlenecks are retrieval ranking inside vital5, the gate over good sources, and the 1.5B model's reading of numeric leads.

## Decisions / Options / Tasks

**Decisions (Plumb, reversible):**
- Run 2 is the baseline.
- Hand labels and the judge are the scoring; precheck v2 is reported but not trusted out-of-sample.
- Rollback by 0-byte file (the coordinator approved it).

**Options (for the product decision on the r4to page):**
- **O1. vital5 in the default kit now.** For: +3 correct, −9 refusals, a competitor team correct [competitor score removed] → [competitor score removed] (not significant). Against: +3 confident-wrong, +2 false refusals, +1.5 s TTFT, +164 MB. **Not recommended alone.**
- **O2. vital5 plus a "weak support → decline" rule** for numeric and superlative questions: decline when the cited chunk's title is not the question's subject (moose/giraffe, Kantō/Japan, Egypt/"most populous"). Combine with the gate fix from modelos ai #2 (Paris, cry-009, hum-005). **Recommended to test next.**
- **O3. Keep vital5 in the "Curious"/Encyclopedia profile only** (the current UI-1c decision) and invest in the model tier instead.

**Tasks done:**
- [x] Offline install.
- [x] Run 3, 52/52.
- [x] Rollback and lock released at 15:24.
- [x] Judge (104 verdicts) and precheck v2.
- [x] Hand labels (`data/hand-labels-run3-vital5.json`).
- [x] Lantern's audit, cited (§6).

## Artifacts

All under `rnd/plumb/data/`:
- Run 3 rows: `qwen2.5-1.5b-instruct-q4km__iphone-14de107-device-vital5.jsonl`
- App report: `iphone-run3-device-vital5-report.md`
- Precheck: `pc2-14de107-device-vital5-{device,competitor-app}.json`
- Aggregation: `analysis-14de107-vital5.json` (`node rnd/plumb/analyze.mjs <eval> <system> <out> <hand-labels>`)
- Judgments: `qwen2.5-1.5b-instruct-q4km__iphone-14de107-device-vital5__vs__claude-code__opus.jsonl`

## Metric and next step

**Metric:** only **3 of the 11 recovered refusals are correct**, with **+3 confident-wrong** overall. Net hand pass, counting acceptable refusals as pass, goes 15 → 17 of 52 (+2). Correct answers go 12 → 17 (+5) †.

**Next step:** test O2 on the same A/B harness (about 10 min of phone time on run 3's config): a subject-match decline rule for numeric and superlative questions, plus the gate fix. Success means confident-wrong ≤ run 2's 5/52 while keeping refusals ≤ 18.

## UNKNOWN:

- **n = 52 is underpowered for this Δ.** All paired CIs include 0. The factual subset's correct Δ lower bound is exactly 0.0. A second run-3 pass (run-to-run noise measured at about ±3 items on 38) would be needed before calling the direction.
- **Single hand rater** (Plumb, an LLM agent). The judge agrees with me on 26/34 answered rows in run 3, and on exactly which of the 11 are correct.
- **Judge and reference are the same model family** (Opus 5.5). The same bias applies to A and B, so the paired Δ is less affected than the absolute ratio.
- **Duplicate judge calls:** two judge processes overlapped on 14 ids. The aggregation keeps one verdict per (question, order), so there's no effect on the numbers, only extra [usage detail removed] usage.
- **TTFT +1.5 s:** I did not separate how much comes from searching a third pack (FTS over 116 k chunks) versus longer prompts from more retrieved text.
- **0-byte rollback side effect:** the app's pack screen will show wiki-vital5 as a partial download. Anyone tapping "download" would fetch it over the network, and airplane mode currently blocks that.

## Errata

† **2026-09-30 ~19:45, found by Lantern's bench subagent B.** The run-2 hand-label row first read `15 / 8 / 5 / 27`, which sums to 55 over 52 rows.
- **Cause:** the 3 declines on `refuse_ok` items were counted both as pass (12 + 3 = 15) and as refused (27).
- **Correct breakdown**, from `data/hand-labels-run2.json` + `data/pc2-14de107-device-device.json`: **12 correct answers, 8 fail, 5 cw, 27 refused**, of which 3 are acceptable refusals on `refuse_ok` items. 12 + 8 + 5 + 27 = 52.
- **Run 3 was right as written:** 17 / 9 / 8 / 18, no acceptable refusals.
- **What changed:**
  - The Δ is now stated two ways: +5 correct answers (12 → 17), and +2 pass counting acceptable refusals (15 → 17).
  - The Metric line had said "+3/52 net correct", which conflated the 3 correct among the 11 recovered refusals with the net change. It now states both.
- **Unchanged:** no label changed, and none of the judge, precheck or paired-CI numbers change. The 15/52 "pass" in `vitalik-eval-14de107.md` (29%) is the pass-including-acceptable-refusals figure and stays valid under that definition.

