# Audit: does BOAR's "quality ratio ≥ 0.50" operationalize the bounty post's bar?

Date: 2026-10-06 · Auditor: Opus subagent (read-only) · Scope: boar-eval harness, bench v0.1/v0.2 manifests (no blind/ content opened), reports, rnd/research MANDATE/BOUNTY-BOARD/QUEUE/coordinator claim files.

Path shorthands: `E/` = `<workspace>/boar-eval/`, `R/` = `<workspace>/rnd/research/`, `B31` = `<workspace>/BOUNTY_31.md`.

TL;DR
- The "ratio" is **Σ absolute rubric scores (1–5, three criteria) of BOAR ÷ Σ the same for an Opus+web reference**, with scores taken in a pairwise prompt. It is not a preference rate. Because the rubric floor is 1, a system that always declines already scores **0.306**.
- On a human-meaningful scale the headline 0.513 corresponds to about **0.39 (floor removed)**, **0.30 (above always-decline)**, **39 % of answers judged correct**, and **4 % win-or-tie**. That is below Haiku from memory (0.653). There is no human calibration.
- The score leaves out **speed** (phone p50 is 69–112 s, 2–2.7 tok/s decode) and the post author's literal venue test. On the post author-style blind questions the ratio is **0.413**, not 0.51.
- Noise: a typical lever needs about **70–180 items × 2 seeds per arm** to detect +0.03. L1 (24 items) cannot detect it, and L2 (57) only barely. Of the dev gains, **+0.054 on dev became +0.007 on held-out**.
- Held-out hygiene has a concrete hole: the **v0.2 plaintext is in git history on origin/main** (commit d8154b6).

---

## 1. How the ratio is computed

**Verdict.** This is neither a pairwise preference nor a ratio of independently given scores. It is a **ratio of summed absolute rubric means, elicited in a pairwise frame**.
- Per item, an Opus judge sees BOAR and the frozen Opus+web reference side by side. It scores each answer 1–5 on correctness, completeness and usefulness, in both A/B orders. The two orders are averaged.
- Aggregate: ratio = ΣS_boar / ΣS_ref over judged, non-venue items, with a percentile-bootstrap CI.
- "0.50" is a threshold on that raw number, set by r4to's decision. The win/tie/loss preference is computed but is not the bar.

**Reference (frontier + web)**
- Recipe: `claude -p --model opus` with tools WebSearch + WebFetch, a clean env ([usage detail removed]), sequential calls with a 5 s gap and 1 retry (`E/bench/v0.1/refs/gen_refs.mjs:1-5,20-24,30`).
- System prompt `reference.v1` (sha d5144343…), from `<workspace>/wt/eval/eval/prompts/reference.v1.md:1-9`. It asks the model to search and verify, keep the answer **under 250 words**, lead with the direct answer, and end with a "Sources:" block.
- Generated once and frozen. The text is gitignored; only per-item sha256s are committed:
  - v0.1: 33 answers reused from v0 (2026-09-30) plus 27 new (2026-10-02), all `claude-opus-5-5` (`E/bench/v0.1/DATASET_CARD.md:85-90`, `E/bench/v0.1/refs/MANIFEST.json`).
  - v0.2: 110/110 answers, `"frozen": true` (`E/bench/v0.2/refs/MANIFEST.json`).
- The judge refuses to run on a refs or questions sha mismatch (`E/harness/judge.mjs:56-62`).

**Judge prompt and scale**
- System prompt (`E/scorers/vendor/eval-lib/judge-core.mjs:64-75`): impartial; "Do NOT reward length, formatting, confidence or tone"; penalize factual errors; a correct "I am not sure" beats a confident wrong answer; correct false premises; tie when equal.
- Rubric (`judge-core.mjs:40-44`): correctness (a wrong claim caps it at 2, an uncorrected false premise at 1), completeness and usefulness, each an integer **1–5** (schema minimum 1, `judge-core.mjs:46-51`).
- User prompt (`judge-core.mjs:77-81`, `judge.mjs:85,93`): the question, the item's author-note bullets ("key points of a good answer", written by Claude item writers), then Answer A and Answer B.
- Blinding strips think tags, the Sources block, links and bold text (`judge-core.mjs:5-20`, `judge.mjs:92`).
- Both orders always run (`judge.mjs:77,86-87`). The output is a JSON schema with scores_A, scores_B, winner and rationale (`judge-core.mjs:52-62`).

**Per item**
- `mapVerdict` maps the positional scores back to boar/ref (`judge-core.mjs:84-89`).
- `combineOrders` averages the scores of the two orders; if the two winners disagree, the winner becomes "tie" (`judge-core.mjs:94-98`).
- `meanScore` = mean of the three criteria (`judge-core.mjs:91`).

**Aggregate**
- `ratio = Σ meanScore(boar) / Σ meanScore(ref)` (`judge-core.mjs:128`), with a 2,000-resample seeded percentile bootstrap (`judge-core.mjs:111-121,138`).
- Excluded from the ratio:
  - venue-list items (`judge.mjs:70`);
  - errored traces (`judge.mjs:66`);
  - items judged in only one order (`E/scorers/bridge.mjs:34-37`).
- Bar verdict: MEETS only if the CI lower bound is ≥ 0.50 (`E/scorers/score.py:87-94`).
- v0.2 claim definition: raw ratio with a stratified two-level (items × runs) bootstrap, seeds 42/43(/44) (`E/bench/v0.2/plan/analysis-plan.md:16-20`).
- Companion metrics: Σ(S−1)/Σ(R−1), and (raw − 0.306)/(1 − 0.306) (`analysis-plan.md:22-25`; `E/scorers/stats.py:226-235`).
- The "RACE equivalent" ratio/(1+ratio), which maps 0.50 to 0.333, is cosmetic (`score.py:83-84,106`).

**What one item looks like (Android 4B, v0.1)**
- BOAR rubric 3.12 / 2.24 / 2.31 vs reference 4.81 / 4.94 / 4.96 gives ratio 0.521.
- On the same run: win/tie/loss is **2 % / 2 % / 96 %**, and 39 % of answers have correctness ≥ 4 (`E/reports/night-2026-10-01/and-qwen.md:13,30-34`).

---

## 2. Does it faithfully operationalize the bounty post's bar?

**Verdict: partially; the error leans optimistic.**
- It measures answer substance on mostly short, Wikipedia-friendly questions, as judged by a Claude model.
- It leaves out speed, his literal venue test and his "difficult questions" emphasis.
- Its scale has a 0.306 floor, so "0.50" does not read as "half as good".
- On the post author-style blind items the same engine scores 0.413.

| Gap | Evidence | Direction |
|---|---|---|
| **Speed is not in the score.** The seven axes are "never averaged" (`E/README.md`; `E/docs/ADR-001-engine-eval-harness.md:64-74`), so quality ignores latency. | The bounty requires usable speed (`B31:28`). the post author: "anything slower than 50 tok/sec feels too annoying"; he called the apps "much slower and less effective at difficult questions" (`<workspace>/rnd/lantern/vitalik-thesis.md:9,16,28,38`). Measured on a phone (A15, 8 GB): p50 total **112 s** (`R/QUEUE.md:698`), decode **2.0–2.7 tok/s** (`R/QUEUE.md:695`), calibrated warm p50 ≈ 69 s (`R/QUEUE.md:661`); claim draft says "Not met on the phone" (`R/coordinator/CLAIM-DRAFT.md:142`). | strongly optimistic |
| **Item mix vs "beyond simple factual recall… synthesis".** | The bounty asks for questions "beyond simple factual recall, including explanation, comparison, synthesis, and reasoning" (`B31:27`). v0.1: synthesis 3/60; many "explanation/reasoning" items are lookups (Berlin Wall years, 2016 Olympics host, Kenya capital and independence, Kilimanjaro height: `E/bench/v0.1/questions.public.jsonl`; mix in `E/bench/v0.1/DATASET_CARD.md:62`). v0.2: synthesis 6/110, crypto 13, honesty 12, danger 10 (`E/bench/v0.2/DATASET_CARD.md:14`). Writers, rewriters and the reference are all Claude, and the writers converged on "canonical" topics (`E/bench/v0.2/DATASET_CARD.md:34,95`). | optimistic (easy, Wikipedia-covered items favour RAG) |
| **Population sensitivity is larger than the CI.** | v0.2 held-out 0.513 (0.479–0.550) vs V-para (blind, the post author-style) **0.413 (0.384–0.445)**; reasoning 0.348, synthesis 0.397 (`R/coordinator/CLAIM-RESULTS-cut3.md:24,57,68`). A 0.10 population shift is about 3× the CI half-width. | optimistic |
| **His literal eval is outside the ratio.** | Venue-list items are not judged (`E/harness/judge.mjs:70`; `analysis-plan.md:7`). V-para venues **0/7** (`CLAIM-RESULTS-cut3.md:63,71`). | optimistic |
| **Reference ≈ "frontier model", not "internet + frontier".** | Opus *without* web scores **1.029 (1.007–1.053)** against Opus+web, and the judge "cannot tell them apart" (`E/reports/anchors-2026-10-02/ladder.md:16,36`). The judge has no web either, the Sources block is stripped, and answers are capped at 250 words. Browsing, maps, lists, reviews and freshness are not represented. | ambiguous: the bar is easier than real web search on freshness and local questions, harder on depth |
| **Judge family bias.** | Opus judges answers measured against an Opus reference, on items written by Claude (`ladder.md:73`). The second judge, Fable, is the same family (κ 0.894, `R/QUEUE.md:249`). The cross-family GPT pilot was held and never run (`R/QUEUE.md:199`; `CLAIM-DRAFT.md:155`). | unknown sign; anchors likely inflated relative to BOAR |
| **Length bias.** | The prompt forbids rewarding length (`judge-core.mjs:68`). The length-controlled check gives a **negative** slope (−0.34 per log-word) (`R/QUEUE.md:141`). BOAR answers are about 51 words vs about 250 for the reference, and BOAR loses mainly on completeness and usefulness (`ladder.md:69`). | no positive length bias found; the "thin answer" penalty looks substantive |
| **Refusal floor.** | An always-decline system scores 0.306 (declines get about 1.48/5) (`ladder.md:23`; `analysis-plan.md:24`). On honesty items a decline scores about 2.1 (`E/bench/v0.2/plan/item-spec.draft.md:14`). | **about 61 % of the 0.50 bar is free** |
| **Does 0.50 mean "50 % as good"?** | Headline 0.513 → floor-removed 0.389, above-decline 0.299 (`CLAIM-RESULTS-cut3.md:24`). Correct (≥ 4) 39 %; win+tie 4 % (`and-qwen.md:30-34`). Haiku without web = 0.653, and the bar sits below it (`ladder.md:18,68`). No human labels: "NO human review" (`R/QUEUE.md:454`); the planned 40-pair check has not been done (`CLAIM-DRAFT.md:78`). | optimistic by about 0.1 on any human-interpretable scale |

---

## 3. Noise and power

**Verdict.**
- Run-to-run noise is about ±0.01–0.03 on the ratio, and the MDE formula in `stats.py` **understates** real paired variance by 1.3–2×, because it ignores item × arm heterogeneity.
- L1 (24 items) cannot resolve ±0.03. L2 (57 items × 2 seeds) resolves it only for levers that change few answers.
- Dev gains clearly over-transfer: +0.054 on dev became +0.007 on held-out. Several adoptions used **CI90**, not CI95.

**Measured noise**
- 1.5B, two identical-config seeds (`E/reports/night-2026-10-01/stability.md`):
  - ratios 0.374 / 0.384, Δ +0.010 (−0.030…+0.049);
  - σ²_run 0.252 (`:11`);
  - MDE 0.052 at 1 run/arm, 0.038 at 2 runs × 57 items (`:12,76-81`).
  - The ADR records Δ 0.031 between identical runs (`E/docs/ADR-001-engine-eval-harness.md:30`).
- Judge share of the noise: 2–9 % by proxy only. A direct re-judge of the same traces has **never** been done (`stability.md:13-14,89-93`). Verdict reuse alone moves the ratio by 0.0065 on identical texts (`R/QUEUE.md:676`), and per-item re-noise reaches about 0.05 (`R/QUEUE.md:574`).
- 4B ship era: printed MDE 0.018 at 2v2 × 110 (`CLAIM-RESULTS-cut3.md:35`), which implies σ²_run ≈ 0.11 = (0.018/2.8 × 4.85)² × 110.
- Observed paired CI half-widths at n = 110, 2v2:
  - cut 3 vs ship: ±0.0166 (SE ≈ 0.0085);
  - cut 3 vs E3: ±0.027 (SE ≈ 0.0138) (`CLAIM-RESULTS-cut3.md:35,37`).
  - The formula SE (`E/scorers/stats.py:177-183`) is 0.0064–0.0068. The real SE is **1.3× to 2.0×** larger.
- `_draw_runs` resamples 2 runs with replacement (`stats.py:103-107`), which halves the represented run variance. With k = 2, the two-level CIs are slightly too narrow.

**Sample size to detect +0.03** (80 % power, two-sided α 0.05, Z = 2.8, paired; n = σ²·(2/k)·(Z/(Δ·R̄))²)

| Variance source | k = 1 run/arm | k = 2 | k = 4 |
|---|---|---|---|
| σ² 0.252, R̄ 4.89 (1.5B, temp 0.7) | 184 items | 92 | 46 |
| σ² 0.107, R̄ 4.85 (4B ship, formula) | 79 | 40 | 20 |
| Empirical, cut 3 vs ship (few answers change) | — | **≈ 69** | — |
| Empirical, cut 3 vs E3 (many answers change) | — | **≈ 181** | — |

**Funnel power**
- L1 = 24 items (`R/BOUNTY-BOARD.md:32`): formula MDE at 2 seeds/arm is 0.039–0.059. With the heterogeneity factor it is about **0.05–0.12**, so it cannot see ±0.03.
- L2 = v0.1 EN, 57 items: formula 0.025–0.037, realistic **0.033–0.07**.
- Adoption rules used CI90: cut3-vgar Δ +0.029, CI90 [+0.007, +0.058] (`R/QUEUE.md:567`); cut 3 confirm Δ +0.032, CI90 [+0.010, +0.062] (`R/QUEUE.md:574`). At 95 % these become about [−0.001, +0.059] and [+0.001, +0.063], which is borderline.
- android-g75 calls a Δ whose CI excludes 0 "noise" because |Δ| < MDE (`E/reports/devices-2026-10-02/android-g75.md:7-8`). MDE is a design quantity, not a post-hoc significance test.

**Winner's curse**
- Dev v0.1: main 4B 0.512 → cut 3 0.566, **+0.054** (`E/bench/v0.2/plan/analysis-plan.md:70`; `R/QUEUE.md:574`).
- Held-out: E3 0.506 → cut 3 0.513, **+0.007** (+0.011 vs ship, CI contains 0) (`CLAIM-RESULTS-cut3.md:24,28,35-37`).
- So about 85 % of the dev gain did not transfer.
- Caveat: the dev numbers mix judge.v1 (s42/s43) and judge.v1-med (s44/s45).

---

## 4. Judge: model, versions, calibration, drift

**Verdict.**
- One judge, `claude-opus-5-5` via `claude -p`, no tools, structured output. Its prompt and code are pinned: judge-core sha 521f7ad3 equals the frozen plan copy (verified by shasum).
- Two version labels exist (v1, v1-med), and the medium-effort setting apparently did not take effect.
- Calibration is same-family only (Fable). There is no cross-family judge, no human calibration of the ratio and no direct test-retest. Comparability over time rests on an unpinned alias and CLI.

**Configuration and versions**
- Model: `--judge-model opus` alias by default (`E/harness/judge.mjs:31`); the resolved id is recorded per row (`judge.mjs:101`).
- Tally over every `E/runs/**/*.judgments*.jsonl`:
  - claude-opus-5-5 judge.v1: 9,098 rows (CLI 2.1.287/288/289);
  - claude-opus-5-5 judge.v1-med: 2,636 rows (CLI 2.1.289);
  - claude-fable-5-1 judge.v1: 456 rows.
  - The model id was constant; the CLI version drifted.
- Version labels: `--effort` produces `judge.v1-<level>`, "never compare it with judge.v1 numbers" (`judge.mjs:22-24`). In practice, v1-med vs v1 on one run gave same winner 100 %, κ 1.000, ratio 0.545 vs 0.545 (`R/QUEUE.md:541`). Output tokens did not change, so the effort flag apparently had no effect (`R/QUEUE.md:543`). The label "v1-med" is unreliable as a description.
- The claim plan fixes judge.v1 (`analysis-plan.md:13`). Claim runs used v1 (`CLAIM-RESULTS-cut3.md:12`). Dev numbers since 10-04 are v1-med, so dev vs held-out comparisons cross labels; this is benign given κ 1.0.

**Calibration**
- Second judge: Fable (same family), κ(correct) 0.894, r 0.939, ratio within 0.004–0.010 (`R/QUEUE.md:249`).
- Cross-family judge: GPT-5.5 pilot (~[usage detail removed]) **held** (`R/QUEUE.md:199`); the plan's rule "if the difference is > 0.05, the lower ratio is the headline" has not been exercised (`analysis-plan.md:39-44`).
- Human labels: only early hand labels used to calibrate truthfulness thresholds (precheck 88 % agreement; correctness ≥ 4 = pass) (`E/scorers/score.py:28,120`). **Nothing calibrates the ratio against humans.** r4to decided "NO human review" (`R/QUEUE.md:454`), and the plan's 40-pair human check is pending (`analysis-plan.md:45-49`; `CLAIM-DRAFT.md:78`).

**Drift and comparability risks**
- The `opus` alias and the CLI version are unpinned (`E/reports/anchors-2026-10-02/ladder.md:78`).
- Reusing verdicts from mixed judge instances makes ratios irreproducible at about 0.007 (`R/QUEUE.md:676`).
- No direct judge test-retest exists (`stability.md:14`).
- The references are a fixed snapshot (2026-09-30 and 2026-10-02), so there is no drift there. They age, however: v0.2 flags drift-prone facts (`E/bench/v0.2/DATASET_CARD.md:97`).

---

## 5. Held-out hygiene

**Verdict.** The procedure is good on paper: pre-registered plan with hashes, plaintext in `blind/`, aggregate-only results, exposures disclosed. It has **one concrete leak and several soft ones**:
- the v0.2 plaintext remains reachable in git history (and on origin);
- the committed dataset card and the safety rules reveal held-out topics, and the safety rules were written by a researcher;
- a held-out failure was fixed with a targeted product change;
- the held-out set has been reused at least 4 times.

**How it is protected**
- v0.1 held-out (30 items): hashes and counts only (`E/bench/v0.1/heldout.manifest.json`).
- v0.2: plaintext moved to `blind/bench-v02/live/v0.2/` on 2026-10-03 after a researcher's trace scan printed an item (`E/bench/v0.2/HELD-OUT.md:3-7`; `R/QUEUE.md:373`). Paths are gitignored (`E/.gitignore`). `SHA256SUMS.items` and `COMBINED-FREEZE.sha256` stay in the repo. The refs MANIFEST.jsonl and spend.jsonl contain hashes, ids and token counts only (checked: no field over 64 chars).
- Plan rules: "No arm decision is ever taken on v0.2-new"; researchers get aggregates only (`analysis-plan.md:8,63-66`).

**How exposures are logged**
- As free-text QUEUE entries: `R/QUEUE.md:335` (vit-h1 items), `:373` (v0.2 A05), `:486` (V-para grading dicts), `:637` (lookup set), `:701` (cut 6 = "second held-out exposure").
- Agent scripts skip v0.2 by id prefix (`R/sonar/exp/30-learned-detector/build_dev_pool.py:1,15`; `R/sonar/exp/29-instant-offtopic/scan.mts:10`).
- There is no structured ledger (item × agent × date) in the readable tree. One may exist in blind/; not checked.

**Contamination risks found**

1. **v0.2 plaintext in git history.**
   - `bench/v0.2/questions.v02-new.jsonl` (110 items with gold answers and rubrics) was committed in `d8154b6` and only deleted in `7d392c0` (`git log --all -- bench/v0.2/questions.v02-new.jsonl`).
   - The blob is reachable (`git cat-file -e` ok; **not opened** in this audit), and `d8154b6` is on `remotes/origin/main`.
   - MANDATE tells researchers to "Read the boar-eval repo … freely" (`R/MANDATE.md:74`). Its blind rule names only `rnd/veil/` (`R/MANDATE.md:104`).
   - Refs text was never committed (no history for `refs.jsonl`).
2. **Topic leak in a committed card.** `E/bench/v0.2/DATASET_CARD.md` lists:
   - the conduct of all 9 rule-less danger items (`:65-75`): rip current, generator in a garage, choking, floodwater, tsunami, rabies PEP, heat exhaustion, lightning, tornado in a mobile home;
   - collided "canonical" topics, about half of which survive in the set (`:34,38`);
   - fact-fixed items: Mont Blanc 2025 survey, a billion seconds (`:40-41,103`).
3. **A researcher wrote the held-out safety mappings.** Compass authored safety v0.6/v0.7 with explicit mappings to v0.2 danger items (`R/QUEUE.md:269,272`). Compass then built the CO-hazard card (`R/QUEUE.md:515`) after the held-out item A02 (generator) failed in the ship run (`R/QUEUE.md:508`).
   - Disclosed: "A02 is excluded from any improvement claim" (`CLAIM-RESULTS-cut3.md:50`).
   - But A02 is still inside the 0.513 headline.
4. **Held-out reuse.** E3, runs-ship, cut 3 and (released) cut 6 were all evaluated on the same 110 items (`CLAIM-RESULTS-cut3.md:24-28`; `R/QUEUE.md:701`). The deltas are below the MDE, so the selection effect is small. Still, "which cut to claim" is a forking path.
5. **Single-family items, reference and judge** (`E/bench/v0.2/DATASET_CARD.md:95`). This is not leakage, but it correlates the held-out set with the dev set's style.

---

## 6. Desktop-node adapter vs the real phone

**Verdict.**
- On the desktop, the engine logic is real: the same `createAnswerer`, packs and GGUF files (sha-checked). Runtime, sampler, RAM, KV cache, GPS and the UI path are simulated or absent.
- Quality has matched the device within noise on the cases checked: iPhone 1.5B; Android 1.5B at −0.029; A15 4B on 25 items at 0.482 vs 0.478/0.493.
- The big gaps are **latency, which is out of score anyway**, and **the shipping Android UI not running the measured engine path**.

| Dimension | Desktop-node | Phone | Could change score? |
|---|---|---|---|
| Engine code | Real `createAnswerer`, zero engine edits (`E/adapters/desktop-node/README.md:3`) | Same `answerService` in BOAR Bench; **the shipping Android UI uses the legacy `runAdaptiveChat` → executor.ts, not answerService** (`R/QUEUE.md:645-648`) | **Yes**: the measured engine is not what a user of the Android app runs until ui-android is wired |
| Model and quant | Same GGUF, sha-checked: Qwen3-4B-Instruct-2507 Q4_K_M (`runner/adapter.ts:139-148`) | llama.rn 0.13.0-rc.4; repack differs per platform (`R/QUEUE.md:418`) | Small |
| Runtime and sampler | node-llama-cpp 3.21.1 sampler and chat template; temp 0.7, top_k 40, top_p 0.95, min_p 0.05, seed (`runner/adapter.ts:311-319`); "Not comparable across backends at temperature > 0" (`README.md:63,75`) | llama.rn sampler chain | Text differs, ratio within noise so far: A15 0.482 vs desktop 0.478/0.493 on 25 items (`R/QUEUE.md:698`); moto g75 1.5B −0.029 (−0.056…−0.003) (`android-g75.md:7`) |
| Context length | `contextSize max(2048, nCtx ?? 4096)` (`runner/adapter.ts:311`); server backend `-c 4096` (`:390`) | Engine default (`LE.defaultContextSize`, `runner/adapter.ts:726`) | Low |
| RAM | Simulated only for engine decisions, `BOAR_EVAL_RAM_BYTES` (`runner/adapter.ts:133`; `README.md:75`) | Real LMK: the 4B was **killed while loading** on an 8 GB moto g75 (`android-g75.md:5`); A15 PSS 3.65 GB with swap | Yes, as availability: an answer that never arrives, or a fallback model |
| KV prefix reuse | None; the shim no-ops `saveSession`, so evals never saw the KV save bug (`README.md:75`; `R/QUEUE.md:634`) | Bug cost 55–65 s per question | Latency only |
| Route gate and detector | Absent from the committed adapter until 2026-10-06. Claim runs used the mini-only "be-ship" runner. `--backend server` runs (kvq8, speedpack) are gate-less (`E/adapters/desktop-node/RUNNERS.md:3,18,28-29,63,67`) | Gate on | Fidelity checked later: 0/60 text changes (`R/QUEUE.md:668`) |
| Retrieval | Same engine retrieval and k; node:sqlite shim; no native zstd/bridge cost (`README.md:29`; CUT5-SPEED in `R/QUEUE.md:663`) | expo-sqlite, native zstd | Ranking same; timing differs a lot |
| GPS / places | Only via `--places`; no device location. V-para venue items → `location:unavailable` (`CLAIM-RESULTS-cut3.md:71`) | Real GPS fix | **Yes** for the bounty post's literal test (untested end to end) |
| Multipass, thinking | `alwaysComplete` multipass not wired; thinking budget emulated (`README.md:65,75`) | Native | Low for the 4B default |
| Timeouts and errors | `--timeout-ms 120000`. Errored traces are **skipped, not scored 0** (`judge.mjs:66`) | A15 had 0 timeouts, p90 149 s | Could inflate device ratios if phone timeouts occur |
| Latency | Desktop TTFT p50 7.3 s, total 10.7 s (`CLAIM-RESULTS-cut3.md:68`) | A15 total p50 112 s; decode 2–2.7 tok/s (`R/QUEUE.md:695,698`) | Not in the score (see §2) |
| Hardware class | Mac mini CPU | Only 8 GB phones tested (A15, moto g75); **no 12 GB device** (`CLAIM-DRAFT.md:19,23`) | Unknown |

---

## Top 5 risks that a measured 0.50 does NOT mean the bounty post's bar is met (ranked)

| # | Risk | Why it matters (evidence) | Cheapest check that reduces it |
|---|---|---|---|
| 1 | **Speed is outside the score, and the phone is far too slow.** | He rejects slow tools (50 tok/s floor, "much slower"). The phone measures 2–2.7 tok/s decode and 69–112 s per answer (`R/QUEUE.md:661,695,698`; `vitalik-thesis.md:16,38`). A 0.51 answer that takes 90 s is not "usable". | Zero new runs: recompute the A15 25-item ratio with any answer over a frozen latency cap (e.g. 30 s) scored at the decline floor, and report "ratio within 30 s" next to the headline. |
| 2 | **What gets shipped is not what was measured.** | Android UI → legacy executor, not answerService (`R/QUEUE.md:645-648`). No 12 GB device run. Desktop shims hid the KV bug (`R/QUEUE.md:634`). GPS path untested (`CLAIM-RESULTS-cut3.md:71`). | A static check (`git grep answerService` in the submission's ui-android), plus one smoke run of 9 items through the *installed app UI* on the 12 GB phone when it arrives, with the BOAR Bench comparison on the same items. |
| 3 | **The question population is easier than his.** | v0.2 0.513 vs V-para (the post author-style) 0.413. Synthesis is 5 % of items. His venue test is excluded and scores 0/7. He judges on "difficult questions" (`CLAIM-RESULTS-cut3.md:57,63`; `B31:27`). | Headline V-para next to v0.2, at equal size (no new runs). Then about 30 "hard" items written by a human or non-Claude writer (multi-hop synthesis or comparison), run once on the frozen cut. |
| 4 | **The scale's meaning is uncalibrated, and the judge is single-family.** | 0.513 raw = 0.389 floor-removed = 0.299 above-decline = 39 % correct = 4 % win+tie. It sits below Haiku from memory. Claude judges against a Claude reference. No humans (`CLAIM-RESULTS-cut3.md:24`; `and-qwen.md:30-34`; `ladder.md:18,73`; `R/QUEUE.md:454`). | The pre-registered 40-pair blind human label check (`analysis-plan.md:45-49`, about 1 h for r4to), adding one binary question: "is BOAR's answer at least half as useful?". Also the cross-family re-judge of one run: GPT-5.5 at about [usage detail removed] which needs r4to's OK for paid APIs, or a local open-weights judge on the mini. |
| 5 | **Held-out integrity and dev overfitting.** | Plaintext in git history on origin (`d8154b6`). Topics and conduct in the committed card. A researcher mapped the safety rules, and A02 got a targeted fix. Dev +0.054 became held-out +0.007. Adoptions at CI90 (`R/QUEUE.md:269,508,515,567,574`; `CLAIM-RESULTS-cut3.md:35-37`). | (a) Coordinator-only, aggregate recompute of the cut 3/cut 6 held-out ratio *excluding* items whose topic is named in `E/bench/v0.2/DATASET_CARD.md` or mapped by Compass (no runs). (b) Purge the blob from history in the private repo (`git filter-repo` + force push; r4to's call, irreversible). (c) For the final claim, a small fresh blind set by a non-Claude/human writer. |

UNKNOWN:
- Whether any agent ever ran `git show d8154b6:…`. No access log exists.
- The size of the cross-family judge effect (never run).
- The phone ratio on a 12 GB device and through the shipping UI.
- Whether an exposure ledger exists inside `blind/` (not opened, by rule).
