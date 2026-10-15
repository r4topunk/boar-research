# BOAR research record

TL;DR: BOAR is an offline Android research assistant: a small local language model (Qwen3-4B) answers from knowledge packs stored on the phone (Wikipedia, Wikivoyage, Stack Exchange, health and crypto references), with no network. This repo is the measured record behind it: frozen pass/fail criteria, arm reports, aggregates, closed negative results and pack cards. It does not contain any held-out item text.

The bench (questions, frozen references, judge, scorers) lives in its own repo: https://github.com/r4topunk/boar-bench.

## Where BOAR stands against the bar

The target (poidh bounty #31): "more than 50 % as good as internet plus a frontier AI", on a phone with at most 12 GB RAM, English only. We measure it as a ratio of judge rubric scores: BOAR's answer vs a frozen reference written by a frontier model with web search, on the same question.

### The three scales

| scale | definition | why it is reported |
|---|---|---|
| **raw ratio** | Σ mean-rubric(BOAR) / Σ mean-rubric(reference); mean-rubric = mean of correctness, completeness and usefulness (1–5), averaged over both A/B orders | the formal rule of the analysis plan; flattered by the rubric floor (a useless answer still scores 1/5, so raw ≈ 0.2–0.3 for nothing) |
| **floor-adjusted** | Σ(S − 1) / Σ(R − 1): the same ratio with the rubric minimum removed | the primary research target; it answers "how much of the reference's value above nothing does BOAR deliver" |
| **win / tie / loss** | per item, the judge's combined winner over both orders (order disagreement = tie) | the plainest reading; never gated |

95 % CIs are item bootstraps (2,000 resamples). Definitions with code pointers: `reports/BAR-TABLE.md` §0.

### Honest numbers (Opus judge, two seeds unless noted)

| configuration | set | raw | floor-adjusted | win / tie / loss | desktop p50 |
|---|---|---|---|---|---|
| 4B claim build (cut 6 = cut 7 on these sets) | V-para (51) | 0.413 (0.384–0.445) | **0.261** (0.224–0.300) | 0 / 0 / 51 | ≈ 6–10 s |
| 4B claim build | v0.2 (110, dev) | 0.512 (0.478–0.549) | 0.388 (0.346–0.434) | 0 / 0–1 / 109–110 | ≈ 6 s |
| deep tier (Qwen3.6-35B-A3B, no thinking) | V-para (dev-style) | 0.467 (0.439–0.494) | 0.329 (0.294–0.362) | 0 / 0 / 51 | ≈ 32 s |
| deep tier + thinking 512 | V-para (dev-style) | 0.553 (0.524–0.581) | **0.436** (0.401–0.472) | 0 / 0 / 51 | ≈ 79 s |
| deep tier + thinking 512 (1 seed) | v0.2 (dev) | 0.608 (0.575–0.641) | 0.508 (0.467–0.550) | 0 / 1 / 109 | ≈ 82 s |
| Claude Haiku 5.5, no web (anchor) | V-para (dev-style) | 0.588 (0.559–0.615) | 0.48 (CI unknown) | not recorded | — |

### The ladder (V-para, floor-adjusted, bar 0.50)

```
4B claim build        0.26  |█████▏              |
deep tier             0.33  |██████▌             |
deep + thinking 1024  0.42  |████████▍           |
deep + thinking 512   0.44  |████████▋           |   (same quality as 1024 at 0.55× the time)
bar                   0.50  |██████████          |
```

Reading: on development data (desktop only, no phone run for the deep tier, and the v0.2 leg is one seed), the deep tier with thinking clears the formal raw rule (CI low > 0.50), which asks for both sets; the primary floor-adjusted target is not met (best 0.436 on V-para, CI high 0.472), and the win rate against the reference is 0 everywhere. The deep tier needs a 12 GB-class phone; the 4B claim build runs on 8 GB.

### Dev vs held-out

- **V-para** was held-out for the two 4B claim runs (cut 3 and cut 6, 2026-10-05/06). Everything measured on it after 2026-10-06 (the deep tier and its variants) is development-style evidence.
- **v0.2** is burnt (its plaintext reached a builder-visible place) and is treated as dev data.
- A final number needs **bench v0.3**, written outside the Claude model family; only its hashes will be public before scoring.
- Status of every set: `reports/SET-STATUS.md`. No item text from any held-out or burnt set appears in this repo; ids, categories and aggregates do.

### On a phone

- Cut 7 (the frozen claim build) on a 12 GB-class phone (POCO X6 Pro, MediaTek MT6897, 10.7 GiB usable RAM, Android 16, airplane mode): 72/72 answered, fast-tier p50 31 s, app PSS ≤ 4.2 GB after model load, no thermal throttling. Quality on the 57 public v0.1 items (Haiku L1 judge): **phone 0.529 = desktop 0.529** (paired −0.000, CI −0.026…+0.028). `arms/device-x6/DEVICE-X6.md`.
- Cut 6 on an 8 GB Galaxy A15: 73/73, phone 0.561 vs desktop 0.558/0.560 on the same 57 items.
- The deep tier has not yet run on a phone; desktop numbers transfer to the on-device engine (bmoe) with a sampling caveat (judged-equivalent on identical contexts).

## How to read an arm

An *arm* is one experiment. Read it in this order:
1. `arms/<arm>/<ARM>-criterion.md`: the pass/fail rule, frozen (sha256) **before** any run that decides something.
2. `arms/<arm>/<ARM>.md`: the report and the verdict against that criterion.
3. `arms/<arm>/aggregates/`: the numbers the report quotes; `tools/` holds the scripts that produced them (paths parametrised: `$BOAR_WS`, `$RUNNER_ROOT`, `$RUNNER_HOST`, `$HELDOUT_DIR`).
4. `*.patch`: the engine diff against a public upstream boar-app commit (`0cfd4a77` for cut 6/7).

Arms shipped here: `facts` (the Wikidata fact table in cut 7), `detfu` (cut 6's detector and follow-ups), `headpass-st`, `oracle-st`, `stack`, `packs` (the knowledge-pack line), `device-x6` (phone run), `longsession` (multi-turn drift), `pr1` (rebase and chat wiring of cut 7 onto upstream).

Hashes and the release scrub: files were scrubbed for this release (local paths → variables, agent and session names → roles, maintainer handle → "the maintainer", held-out paths → `$HELDOUT_DIR`). Where a scrubbed file is pinned by a `.sha256`, the hash refers to the private original: 13 criterion files pinned by `.sha256` (plus `arms/device-x6/DEVICE-X6-criterion.md`, whose sha is quoted in its report and which also carries a redaction note), `reports/BAR-TABLE.md`, and `arms/detfu/detmax-on-cut4.vs-0cfd4a77.patch` (private sha `3f355999…`, public sha `d20b88d6…`; only comment text on added lines changed). All other engine patches are byte-identical to the private ones. Hashes of files that are not released (recall sets, pack sidecars) are kept as provenance.

## Negative results are a feature

`reports/CLOSED.md` is a registry of 76 closed lever families: what was tried, how it was measured, how well powered the test was (minimum detectable effect), and what would reopen it. Examples: bigger closed-book models (one plateau ≈ 0.60 for 25–35B MoE), fine-tuning data quality, best-of-2 and self-verification, thinking budgets beyond 512, corpus size for the deep tier. Publishing them saves the next team the same runs; a "not detected at MDE x" row says exactly how small an effect could still hide there. Rule changes to the method are logged in `reports/RULE-CHANGES.md`.

## How the judge works, and its limits

- **Pairwise, both orders.** For each item the judge sees the question, BOAR's answer and the frozen reference, as A/B and again as B/A, and returns rubric scores (correctness, completeness, usefulness, 1–5) and a winner. Order disagreement counts as a tie. Prompt and schema: `judge.v1` (in the bench repo).
- **Models.** Claim and decision numbers use Claude Opus via the Claude Code CLI (`claude -p`). Triage (L1) uses Claude Haiku 5.5 at low effort, sharded 4 ways; Haiku compresses gaps, so a Haiku "no difference" is weaker than an Opus one (`method/L1-PROTOCOL.md`).
- **Limits.** The judge is closed, paid and not bit-reproducible. The references on v0.1 and the judge are the same model family, and so are the writers of v0.2 and V-para; v0.3 is being written outside it. A local open judge (Gemma 4 26B) picked the same winner on 49–50 of 57 items but with κ 0.32/0.55 and a +0.11 lenient bias: usable for ranking, not for the number. Sample sizes are small (CI half-width ≈ 0.03–0.06); one-seed deep-tier deltas below ≈ 0.03 on V-para are seed noise.

## Repo map

Citations in reports to files that are not in this repo (QUEUE, handoffs, pack catalogue, arms not listed above) refer to the maintainers' private record; the arms shipped here are the ones listed under "How to read an arm".


| path | what |
|---|---|
| `reports/` | BAR-TABLE (every configuration vs the bar), CLOSED (negative-results registry), RULE-CHANGES, REPORT-PACKS-2026-10-13 (the pack stack), DEEP-RESEARCH-2026-10-12 (literature notes + verified premises), SET-STATUS |
| `method/` | L1-PROTOCOL (judge triage), CRITERION-TEMPLATE, METHOD (short protocol summary) |
| `arms/` | one folder per shipped arm (criterion, report, aggregates, tools, patches) |
| `packs/` | knowledge-pack cards (the packs themselves are published as a dataset: r4topunk/boar-packs) and the self-test README |
| `BOM.md` | models, packs, datasets, licences and revisions |

## Reproduction

Engine = public boar-app commit `0cfd4a77` + the arm's patch. Bench = https://github.com/r4topunk/boar-bench (v0.1 questions, frozen references, judge, scorers). Models and packs: `BOM.md`. What cannot be reproduced from this repo: the held-out sets (private by design), bit-identical judge outputs (closed model), and the cut 6 runner profile that uses the emergency detector (not released; see `BOM.md`).

## Licences

Code and scripts: Apache-2.0 (`LICENSE`). Text, reports, aggregates and cards: CC BY 4.0 (`LICENSE-DOCS`). Engine patches: MIT, like upstream boar-app (`LICENSE-MIT`). Third-party derived parts (Wikipedia and Wikivoyage: CC BY-SA 4.0; Stack Exchange: CC BY-SA 2.5/3.0/4.0 per post; GeoNames: CC BY 4.0; Wikidata: CC0): see `NOTICE` and the per-directory `NOTICE.md` files.

Author: BOAR R&D. AI-reviewed, not clinically reviewed: nothing here is medical advice.
