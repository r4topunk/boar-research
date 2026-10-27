# The ruler, judge-eye design: predicting what a judge experiences on a phone

## 1. Purpose statement

The ruler predicts whether a person holding a phone in airplane mode would agree with this statement: "this app is a useful, fully offline research tool that's >50% as good as internet + frontier models". That sentence is the bar quoted in `BOUNTY_31.md` ("Winner"), which mirrors https://poidh.xyz/mainnet/bounty/31. The ruler gives:
- a primary quality number with its CI
- a confident-error gate
- on-phone speed bands
- pass/fail offline and install checks

Every threshold is labelled either **bounty text** or **our choice**.

## 2. What the bounty and the post author say, quoted

| Source | Exact text |
|---|---|
| `BOUNTY_31.md` | "a casual info lookup and research tool that runs entirely offline on Android and is >50% as good as internet search + frontier AI models" |
| `BOUNTY_31.md` | "handle useful research questions beyond simple factual recall, including explanation, comparison, synthesis, and reasoning" |
| `BOUNTY_31.md` | "respond at speeds that feel usable for real lookups on a phone" |
| `BOUNTY_31.md` | "People travel with their phones into offline situations all the time" |
| `BOUNTY_31.md` | "include ones a 1B model would fail on"; "get the app running locally within a few minutes without substantial debugging" |
| `BOUNTY_31.md` | "If the post author publicly confirms that a submitted build meets that bar, that submission wins"; otherwise contributors "select a winner they believe best satisfies the requirements and spirit" |
| https://x.com/VitalikButerin/status/2100695863026954698 | "the goal is not even just CROPS, it's utility"; "10 TPS with 1B models that break if you try to use them for anything interesting" |
| https://x.com/VitalikButerin/status/2103762130554204651 | "still much slower and less effective at difficult questions than the models that can run on a laptop"; "my eval is "Tell me the best vegan restaurants in [city I am currently in]""; "look up any facts about the world that you care about" |
| https://x.com/VitalikButerin/status/2106537633056969024 | "comfortably running at 20-30 TPS, but it would only really start to feel fast at 100+" |
| https://vitalik.eth.limo/general/2026/04/02/secure_llms.html | "anything slower than 50 tok/sec feels too annoying to be worth it"; "I fed both outputs into an LLM to ask which is better"; "the walking distance from Paris to Rome and back is 2768 km, not 312.5 km" |

The X posts were read on 2026-10-19 through the api.fxtwitter.com mirror, because x.com returns 402. Before publishing, re-read them on x.com from a logged-in browser.

## 3. Judge-experience model (the thing we predict)

The model has five parts. Each one is our assumption, inferred from the quotes above; none is stated by the post author.

1. **A sitting.** A judge installs the app and asks about 10–15 questions in one go. A typical sitting has a few facts, a few "why/how/compare" questions, one or two travel or current-city questions, and one or two "interesting" questions meant to break a 1B model.
2. **The comparison point** is what the judge already uses: an LLM with web. V2 also names "models that can run on a laptop".
3. **Memory is asymmetric.** One confident wrong answer (the Paris–Rome kind) lowers trust more than one "I don't know offline". Blandness also counts against the app: the blog calls Local Deep Research "pretty bland and not very high-quality".
4. **Speed is felt per answer:** time until something useful appears, then time to the end. His tolerance quotes are for laptops. A phone threshold has to be our choice and must be labelled that way.
5. **The verdict is holistic and pass/fail** ("meets that bar"). Under the contributor path it is a ranking among entries.

So the ruler scores answers as **outcomes a user would act on**, aggregates them per simulated sitting, and keeps speed as a separate axis.

## 4. Mapping: bounty clause → what we measure → how

| Clause (quoted) | Measured | How | Gate or reported |
|---|---|---|---|
| ">50% as good as internet + frontier models" | Utility ratio U (§6) | Absolute outcome labels vs a frozen frontier+web reference, two judge families | Primary |
| "useful … research tool"; "it's utility" | Useful-answer rate | Share of answers labelled USEFUL | Reported |
| "beyond simple factual recall, including explanation, comparison, synthesis, and reasoning" | U per stratum | Strata in §5, each at least 10 % | Reported, plus a gate that no required stratum has U < 0.30 (our choice) |
| V2 vegan eval, "People travel…" | Current-city venue score | Device location injected, OSM gold plus human check | Reported separately, never hidden |
| "1B models that break…" / "include ones a 1B model would fail on" | 1B baseline arm | The same items run on a 1B model (Llama-3.2-1B or Gemma-3-1B) | Separability check plus a demo list |
| "respond at speeds that feel usable … on a phone" | TTFT, time-to-complete, decode tok/s, p50/p90 | Native app on a real phone, airplane mode | Reported in bands (§8) |
| "work completely offline" / "no … network requests" | Bytes on the network | PCAPdroid capture during the run; manifest has no INTERNET permission | Gate: 0 bytes |
| "not require Google Play Services" | gms dependency | `aapt dump`, run on a phone without gms (GrapheneOS if available) | Gate |
| "maximum 12GB RAM environment" / "no more than 50GB total" | Device RAM, installed bytes | Device spec sheet; `du` of the app plus assets | Gate |
| "running locally within a few minutes" | Setup time | A third party follows the README; time measured with and without the asset download | Reported (setup, not answer latency) |
| "materially different from the version reviewed" | Build identity | APK sha256 and git tag recorded in every result row | Gate |

## 5. Item set: "Sitting Set" (SS-1)

**Size.** 72 judged items in 6 sittings of 12, plus 8 current-city venue items. A fallback of 48 judged + 6 venue is allowed if writing runs late. With n = 72 the CI half-width is about ±0.07, enough to call "clearly above or below 0.5" (methods survey §11).

**Strata and weights** (our choice, each derived from a quote):

| Stratum | Weight | Anchor |
|---|---|---|
| Fact lookup (single and multi-fact) | 15 % | V2 "look up any facts about the world" |
| Explanation | 15 % | req. "explanation" |
| Comparison | 12 % | req. "comparison" |
| Synthesis (needs 2+ sources) | 12 % | req. "synthesis" |
| Reasoning, incl. travel arithmetic (Paris–Rome type) | 14 % | req. "reasoning"; blog example |
| Travel and on-the-road practical (transit, border, phrases, first aid, money) | 20 % | "People travel with their phones…" |
| Honesty: false premise / unanswerable offline | 6 % | judge rule "a correct 'I am not sure' beats a confident wrong answer" |
| Hard "interesting" tag (overlaps the strata; ≥ 30 % of items) | — | "break if you try to use them for anything interesting"; V2 "difficult questions" |
| Current-city venues (separate score) | 8 items | V2 eval |

Crypto, health and danger are **no longer strata**. They can appear as topics inside the strata above. The 10 danger items move to a **safety guardrail slice** that sits outside the ratio and is gated on zero harmful confident errors. Freshness ("now") items: 4 items are tagged `fresh` and reported apart. That makes the internet's real advantage visible instead of designing it out (flaw A5).

**Who writes.**
- Items, key facts and per-item rubric bullets come from **r4to (human)**, assisted by **one non-Claude model in a web UI**. No Claude anywhere in writing.
- Each item has 3–6 **key facts**, each with a source URL checked by hand. It also has 0–2 **must-not** points (dangerous or false claims, HealthBench-style).
- Items are not filtered on the failures of any system.
- The 11 V-exact verbatim queries stay as a **public calibration slice**: shown to judges, scored, and reported separately.
- The sha256 of the item file is frozen before any run. Plaintext is published after the headline run.

If the human-written set cannot be finished by 10-22, the ruler is published with **V-para + v0.2 as a labelled dev run** ("Claude-written, exposed"), and SS-1 is filled in for the contributors' review. We do not hide the substitution.

**Language:** English only. This is our scope choice; the bounty says nothing about language. It is stated in the README.

## 6. References and judging

**Reference ("internet + frontier models"):**
- **R-A:** Claude Opus 5.5 + WebSearch/WebFetch, the existing `reference.v1`, with the 250-word cap raised to 400. This is the rivals' convention (#125, #134, #137), so numbers stay comparable.
- **R-B:** a non-Claude frontier model with web, same prompt, run in a web UI. Its family must differ from the judge used for the headline.
- Both are frozen and dated, and stored with their URLs. Where a reference contradicts the key facts, it is **flagged**, and both sides are graded against the key facts.
- Optional O3 arm: a laptop model (Qwen3.6-35B on the desktop, no web). This mirrors V2's comparison.

**Absolute outcome label per answer** (the primary unit):

| Label | Meaning | Score |
|---|---|---|
| USEFUL | A casual user could act on it. Key facts right, no must-not hit | +1 |
| PARTIAL | Right direction but missing what was needed, or bland | +0.5 |
| ABSTAIN | Honest "can't answer offline", or empty/off-topic but harmless | 0 |
| CONFIDENT-WRONG | States a false key fact or a must-not without hedging | −1 (Kalai-style t = 0.5, our choice) |

- The judge sees: the question, the key facts, the must-not list, and one answer, blinded and length-normalised. Citations are **kept** (only the system name is stripped), because a grounded citation is part of offline trust. This is a change from judge.v1.
- The judge prompt also asks for the existing 1–5 correctness/completeness/usefulness scores, so we keep continuity with the old raw and floor-adjusted numbers.

**Judges:**
- **J1:** Claude Opus via `claude -p`, pinned model id rather than the `opus` alias.
- **J2:** an OpenAI frontier model via Codex, the same as XFAM.
- Each answer is labelled by both. **The headline is the lower U of the two** (`analysis-plan.md` rule). Agreement is reported as κ and Spearman.

**Pairwise check (secondary):** judge.v1 in both orders against R-A, kept as is. Its job is to show the same ranking, and it is the method the post author uses himself ("ask which is better").

**Human spot check:**
- 40 items drawn at random, stratified, before seeing results.
- r4to and the app maintainer label each one blind with the same 4 labels.
- Prediction-powered inference (Angelopoulos 2023, arXiv 2301.09633) corrects U.
- κ between humans and each judge is reported per stratum.
- This replaces the never-run 40-pair check (flaw 19).

## 7. Primary metric and thresholds

**U (utility ratio)** = Σ score(app) / Σ score(ref) over judged items. The reference is the better of R-A and R-B per item, which is the conservative choice. Stratum weights from §5 apply.

ABSTAIN = 0 sets the scale origin at "useless". So U is floor-adjusted by construction (interpretation I2/I4), and a 1B model that "breaks" scores near 0 or below.

**CI:** a paired, stratified bootstrap over items × 2 generation seeds × 2 judges, 2,000 resamples. The sha256 of this section is frozen before the run.

| Verdict | Rule (our choice) |
|---|---|
| **Meets bar** | Lower-judge U CI low > 0.50, **and** all offline/RAM/storage/gms gates pass, **and** CE gate passes, **and** the safety slice has 0 harmful errors |
| **Point above bar** | Lower-judge U point > 0.50, CI straddles |
| **Below bar** | Otherwise |

**Confident-error gate (judge-eye):** CE rate(app) ≤ CE rate(ref) + 5 pp, and ≤ 10 % absolute. Both limits are our choice.

**Clean-sitting rate (secondary, the experience predictor):**
- Draw 10,000 simulated 12-item sittings by stratum weight.
- A sitting is "clean" if it has 0 CONFIDENT-WRONG answers and at least 6 USEFUL ones.
- Report P(clean) for the app, the reference, and the 1B model.
- Example of how to read it: "In 7 of 10 sittings a judge would see no confident error."

**Other secondary numbers, always shown:**
- W/T/L and win+tie rate vs R-A. These are not the bar, because a 50 % win-rate means parity, not "half as good".
- raw and floor-adjusted judge.v1 ratios, for continuity with claim v4.x and the rivals
- U per stratum
- the current-city venue score: precision of named venues that exist and are vegan-tagged, judged by OSM plus a human check, because OSM-only gold is circular (flaw 12)
- the 1B gap, U(app) − U(1B), with separability: 1B, app and reference CIs must not overlap
- `fresh` items

**Reporting format:** a single card. The headline line reads "U = x (CI) under the stricter judge [family]". It is followed by the gates, the latency bands, clean-sitting, and W/T/L. The judge family is named next to every ratio. The card states "AI-judged; 40-item human check; the post author has not endorsed this ruler."

## 8. Speed (separate axis, never folded into U)

- The **native submitted app** runs on a ≤12 GB phone (POCO X6 Pro, plus Pixel 8a 8 GB if available), in airplane mode, for all items × 1 seed, fast tier and deep tier.
- Measured per answer:
  - TTFT
  - **time to first useful sentence** (the first 30 tokens)
  - time to complete
  - decode tok/s
  - peak PSS
- Reported as p50/p90.

**Bands:**

| Band | Anchor |
|---|---|
| decode ≤ 10 tok/s: "the post author's failed baseline" | "10 TPS with 1B models" |
| 20–30 tok/s: "too slow for comfort" | V3 |
| 50 tok/s: "laptop minimum" | blog |
| 100+ tok/s: "feels fast" | V3 |

- The phone wall-clock bands are **our choice**: first useful sentence ≤ 10 s good, ≤ 30 s tolerable, > 60 s fails a casual lookup.
- **Speed-qualified U** (sensitivity only) counts an answer only if it completed within 60 s on the phone. This shows judges what the fast tier alone delivers, and stops a deep tier at about 2 min from carrying the headline unnoticed.

## 9. Offline and install protocol (gates)

1. Run `aapt dump permissions`: no INTERNET permission and no gms.
2. Run the full item set with PCAPdroid capturing all traffic: 0 bytes.
3. Record `du` of the APK plus assets (≤ 50 GB) and the device RAM spec (≤ 12 GB).
4. A fresh-install stopwatch run by someone outside the team, following the README only. Report minutes, excluding and including the download. Any manual debugging step is logged.
5. The APK sha256 and git tag in the result card must match the claimed build.

GrapheneOS: we own no device. The ruler states this and runs on a gms-free profile. It is listed as UNKNOWN until a contributor runs it.

## 10. What stays, what changes

| Stays | Changes |
|---|---|
| Pairwise judge.v1, both orders, kept as secondary | Primary is absolute 4-outcome U with key facts, not the raw 1–5 ratio |
| `reference.v1` prompt | Cap raised to 400 words; second reference R-B from a non-Claude model |
| Provenance rows, stale-row refusal, bootstrap code | Two judge families, lower one is the headline; model ids pinned |
| V-exact as the calibration slice; V-para/v0.2 as dev | New human-written SS-1 with key facts; Claude removed from item writing |
| Floor-adjusted and raw for continuity | Crypto/health/danger stop being strata; danger becomes a safety gate; travel and venue are first-class |
| Win-rate reported | Win-rate is never the bar; clean-sitting and CE rate added |
| Latency as its own axis | Measured on the **native app** on a phone, not the TS engine on the desktop (flaws 28–29) |
| — | Citations visible to the judge; `fresh` slice added; human spot check with PPI correction |

## 11. Cost and time (deadline 2026-10-23)

| Day | Work | Cost |
|---|---|---|
| 10-19/20 | Freeze ruler spec + analysis-plan sha; update the judge prompt (outcome labels, citations kept); r4to writes SS-1 (about 6 h human time at about 5 min/item including key facts) | 0 API |
| 10-21 | References R-A (72+8 × `claude -p`, about 1.5 h) and R-B (web UI, batched by r4to, about 2 h); 1B arm and app on the desktop, 2 seeds | [usage detail removed] only |
| 10-21/22 | Phone runs, native app, airplane mode + PCAPdroid: 80 items × 2 tiers, about 3–4 h | 0 |
| 10-22 | Judging: about 80 items × (app ×2 seeds + 1B + R-A + R-B) ≈ 400 answers × 2 families ≈ 800 absolute calls, plus 160 pairwise; Opus sharded N = 4 ≈ 2 h; Codex ≈ 2 h | [usage detail removed]; no paid API |
| 10-22 | Human spot check, 40 items × 2 labellers, about 1.5 h each | human time |
| 10-23 | Card, README, independent Opus wording review, publish only with r4to's OK | — |

## 12. Risks

1. **The human-written set slips**, as v0.3 was dropped on 10-18. Fallback: publish the ruler and run it on dev sets, clearly labelled.
2. **Our thresholds look self-serving.** Mitigations: the stricter-judge rule, the conservative better-of-two reference, the CE penalty applied identically to both sides, and pre-registered shas.
3. **The Codex judge depends on r4to's access.** If unavailable, Gemma 26B runs as J2 for triage only, and the card states "single family".
4. **Venue gold is circular.** Mitigation: human verification of named venues on a sample.
5. **Our result fails our own ruler** (likely, given V-para ≈ 0.26–0.44). We publish anyway. The ruler's value to judges depends on it not bending.
6. **GrapheneOS is untested** and the native app is −0.089 vs the engine. Both are disclosed on the card.

## UNKNOWN
- the post author's in-thread replies, and which apps he tested.
- Whether "a few minutes" excludes the download.
- Whether UI/UX counts: comment 1230 on the poidh page is unanswered.
- Deadline: the bounty says "by October 31st, 2026"; the 10-20 (CLAUDE.md), 10-23 (this task) and 10-25 (memory) dates are internal only.
- Whether Codex use counts as "paid API" under r4to's rule.
- The phone wall-clock bands and the −1 CE weight are our choices with no public anchor. Ask contributors for comment before the run.
