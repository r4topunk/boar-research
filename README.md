# BOAR research record: the full open record (v1.1)

TL;DR: BOAR is an offline Android research assistant: a small local language model answers from knowledge packs stored on the phone, with no network. It was built for poidh bounty #31 ("more than 50 % as good as internet plus a frontier AI", at most 12 GB RAM, English only), inspired by a post by Vitalik Buterin. This repository is the **whole research record behind it, as a clean snapshot without git history**: every decision, frozen pass/fail criterion, arm report, aggregate, trace, pack builder and negative result that is safe to publish. The benchmark (questions, frozen references, judge, scorers) is the sibling repository `boar-bench`. Author: r4to, independent researcher.

Live article: https://r4topunk.github.io/boar-research/

## Status (final)

- **Research closed by the author on 2026-10-23; record v1.0 published 2026-10-26; v1.1 on 2026-10-27: the held-out sets are retired and public** (see below and `CHANGELOG.md`). History is not exported: this is one snapshot of the working tree, not a git history (see `CHANGELOG.md`).
- **Final standing, as of 2026-10-25:** on a Pixel 8a in airplane mode, the submitted app (LabRat, formerly BoarLite) won **0 of 71** head-to-heads under the Claude Opus judge and **0 of 71** under OpenAI gpt-5.6-sol (via the Codex CLI). Ruler U-total (71 headline items, health weight 0.5): Claude **0.165** (0.127-0.205; seeds 42, 43), gpt-5.6-sol **0.242** (0.194-0.296; seeds 42, 43). The lower family, 0.165, is **below the 0.50 bar**. Median answer 13.9 s, first word 9.8 s, 11.8 tokens/s, peak memory 3.87 GB, no network traffic. Source rows: `data/status.json`; the report is `rnd/research/coordinator/arms/device-final/DEVICE-FINAL.md`, judged against its frozen rule `DEVICE-FINAL-criterion.md` (sha256 in `DEVICE-FINAL-criterion.sha256`). Since v1.1 the bench v0.4 items, references and writer record are public in `boar-bench` (`bench/v0.4/`); the hash commitments in `bench/v0.4/SHA256SUMS` were published before and verify byte for byte, so the number can be checked and re-run (the judge is a paid closed model, the device run needs the phone).
- The bar was **not reached** on any set measured. The record exists to show how that was measured, what was tried, and what each lever was worth.

## Honest numbers (earlier 4B build and deep tier; Claude Opus judge, two seeds unless noted)

| configuration | set | raw | floor-adjusted | win / tie / loss | desktop p50 |
|---|---|---|---|---|---|
| 4B claim build (cut 6 = cut 7 on these sets) | V-para (51) | 0.413 (0.384-0.445) | **0.261** (0.224-0.300) | 0 / 0 / 51 | about 6-10 s |
| 4B claim build | v0.2 (110, burnt, dev) | 0.512 (0.478-0.549) | 0.388 (0.346-0.434) | 0 / 0-1 / 109-110 | about 6 s |
| deep tier (Qwen3.6-35B-A3B, no thinking) | V-para (dev-style) | 0.467 (0.439-0.494) | 0.329 (0.294-0.362) | 0 / 0 / 51 | about 32 s |
| deep tier + thinking 512 | V-para (dev-style) | 0.553 (0.524-0.581) | **0.436** (0.401-0.472) | 0 / 0 / 51 | about 79 s |
| deep tier + thinking 512 (1 seed) | v0.2 (dev) | 0.608 (0.575-0.641) | 0.508 (0.467-0.550) | 0 / 1 / 109 | about 82 s |
| Claude Haiku 5.5, no web (anchor) | V-para (dev-style) | 0.588 (0.559-0.615) | 0.48 (CI unknown) | not recorded | n/a |

Three scales are always reported together. **Raw ratio** = sum of the judge's mean rubric score for BOAR / sum for the frozen reference (mean of correctness, completeness, usefulness, 1-5, over both A/B orders); it is flattered by the rubric floor (a useless answer still scores 1/5). **Floor-adjusted** = the same ratio with the rubric minimum removed from both sides. **Win / tie / loss** = per item, the judge's combined winner over both orders. 95 % CIs are item bootstraps (2,000 resamples). Definitions with code pointers: `rnd/research/coordinator/BAR-TABLE.md`.

## Results at a glance (what each lever was worth)

| lever | verdict | where |
|---|---|---|
| deep tier (Qwen3.6-35B-A3B) + thinking budget 512 | largest measured lever: V-para floor-adjusted 0.26 -> 0.44 (Claude Opus), still below 0.50, win-rate 0 | `BAR-TABLE.md`, `arms/dt512/` |
| knowledge packs + head pass (X2b) | small gains on pack-matched dev self-tests; limit is delivery of the fact to the model | `REPORT-PACKS-2026-10-13.md`, `arms/headpass-st/` |
| completeness instruction in the prompt | NO: hurt correctness | `CLOSED.md` row 8, `arms/complete/` |
| fine-tune data (grounded-reading SFT) | closed before training: data failed the faithfulness review | `CLOSED.md` row 12 |
| Gemma 4 26B-A4B + thinking instead of Qwen | NO: faster, slightly worse | `CLOSED.md` row 19, `arms/gemmathink/` |
| vendor sampling presets | NO | `CLOSED.md` row 26, `arms/deepsamp/` |
| best-of-2, self-selection, verifier pass | NO: coin flip | `CLOSED.md` row 27, `arms/deepbo2/` |
| per-item routing 4B vs deep | chance-level out of sample | `CLOSED.md` row 28, `arms/deeproute/` |

All paths are under `rnd/research/coordinator/`. `CLOSED.md` holds every closed family with its minimum detectable effect and what would reopen it.

Dev vs held-out: **since 2026-10-27 no set is held out: all of them are retired and public dev data** (v1.1; `rnd/heldout/README.md`). V-para was held-out for the two 4B claim runs (2026-10-05/06) and everything measured on it afterwards is development-style evidence; v0.2 was burnt (its plaintext reached a builder-visible place); the v0.4 ruler was the claim set until the project was submitted. A final number for a later system needs a new set written after this date. The status of every set, and what each spend was, stays in `rnd/research/coordinator/EXPOSURES.md`.

## Map of the folders

| path | what it is |
|---|---|
| `rnd/research/QUEUE.md` | the single decision and result queue: every verdict, in order (start here to follow the story); see also `docs/TIMELINE.md` |
| `rnd/research/coordinator/` | the coordinator's record: reports (`BAR-TABLE.md`, `CLOSED.md`, `RULE-CHANGES.md`, `REPORT-PACKS-2026-10-13.md`, `DEEP-RESEARCH-2026-10-12.md`), claim drafts and their reviews, plans, the exposure ledger, `repro/`, `ruler/` (bench v0.4 work), and **`arms/`: one folder per experiment** |
| `rnd/research/coordinator/arms/<arm>/` | an experiment: `<ARM>-criterion.md` (frozen rule) + `.sha256`, `<ARM>.md` (report), `aggregates/` (numbers), `tools/` (scripts), `*.patch` (engine diffs), run summaries; the raw `.jsonl` traces are in the Hugging Face dataset [r4topunk/boar-traces](https://huggingface.co/datasets/r4topunk/boar-traces) at the same path (see `TRACES.md`) |
| `rnd/research/{sonar,anvil,compass,forge,summit}/` | the lanes' own notes, cards, radars and experiments (retrieval and health, models and latency, evaluation and safety, native performance and the deep tier, strategy memos) |
| `rnd/research/packs/` | knowledge-pack cards (the packs themselves are a Hugging Face dataset, see `BOM.md`) |
| `rnd/kiln/` | the runner lane: experiment folders `exp-01` ... `exp-10`, pack builders, disk log |
| `rnd/bench/`, `rnd/lantern/`, `rnd/plumb/` | early benchmark v0 build, landscape notes and the iPhone plumbing (September to early October) |
| `rnd/archive/`, `rnd/harness/` | small archive notes and harness stubs |
| `data/` | the publication content base: facts, timeline, decisions, experiments and glossary as JSON (public rows only), with `SCHEMA.md` |
| `docs/` | `TIMELINE.md`, `HOW-THE-LAB-WORKED.md`, `REDACTION.md`, `EXCLUDED.md`, `REDACTION-HASHES.tsv` |
| `DATA-CARD.md`, `BOM.md`, `NOTICE`, `CHANGELOG.md`, `CITATION.cff`, `LICENSE-MIT`, `LICENSE-DOCS` | data cards, bill of materials, licences and attribution |

The path `rnd/` keeps the layout of the original working tree, so references inside the documents (for example `rnd/research/coordinator/arms/headpass-st/`) resolve as written. Sibling repository: https://github.com/r4topunk/boar-bench (bench v0.1 public questions, frozen references, judge, scorers).

## How to read the record

1. `docs/HOW-THE-LAB-WORKED.md` (5 minutes): the coordinator, the lanes, the loop, frozen criteria, independent reviews. The lane names (Sonar, Anvil, Compass, Forge, Kiln, Summit, Lantern, Plumb, Veil) are the names of the agent lanes that did the work; they are explained there once.
2. `rnd/research/coordinator/BAR-TABLE.md`: every configuration against the bar, with the scale definitions.
3. `rnd/research/coordinator/CLOSED.md`: the registry of closed lever families, each with how well powered the test was (minimum detectable effect) and what would reopen it. `RULE-CHANGES.md` logs every change to the method.
4. An arm, in this order: `<ARM>-criterion.md` (written and hashed **before** any deciding run), then `<ARM>.md` (verdict against it), then `aggregates/`, then `tools/`.
5. `docs/TIMELINE.md` and `rnd/research/QUEUE.md` for the chronology; `data/` for the same story as structured rows.

## How to reproduce the key results (step by step)

What can be reproduced: the engine builds (public base commit plus one patch), the public dev bench v0.1 end to end on a plain Mac, and every aggregate from stored traces. What cannot: bit-identical judge outputs (a closed, paid model), and anything that needs the phone. The full guide is `rnd/research/coordinator/repro/REPRODUCE.md`; the commands below are its core. The engine base is commit `0cfd4a77` of the app maintainer's open-source `boar-app` (MIT). The author's public fork https://github.com/r4topunk/boar-app contains that commit (on its branch `pr/cut7-engine`), so no contact is needed. Elsewhere in the record the upstream repository appears as `UPSTREAM_REPO/boar-app` (its owner is not named, by policy).

**R1. Rebuild the claim engine and check its hash** (no model, no judge, a few minutes):
```bash
git clone https://github.com/r4topunk/boar-app "$HOME/boar-app"     # public fork; contains the base commit
git -C "$HOME/boar-app" cat-file -t 0cfd4a77badd01297af8dc9a3a10924f8a895105     # expect: commit
cd rnd/research/coordinator/repro
shasum -a 256 -c cut7.vs-0cfd4a77.patch.sha256
./verify-trees.sh "$HOME/boar-app" /tmp/boar-vt .     # prints both hashes per tree; every tree must say OK (adds git worktrees inside your clone)
```
Expected: cut 7 git tree `17d42f2027bdd3b95f2956655d5e49b9924db1a1`, content hash `7c96e59e001b6273baa4f8dcaa7c696c1aa8f356321914b29e38fe58a900cf79`. (The two patches used here, `cut7.vs-0cfd4a77.patch` and `deep-dt512.vs-0cfd4a77.patch`, are byte-identical to the private originals and their `.sha256` files pass. Other engine patches in the arm folders may carry redacted comment text; for those the released sha256 is in the `.sha256` file next to the patch and the original sha256 is in `docs/REDACTION-HASHES.tsv`.)

**R2. Run bench v0.1 end to end on the desktop** (needs Node >= 22.5, pnpm, an Apple-silicon Mac with 16 GB, about 10 GB of disk, and the sibling `boar-bench` repository; the judge step needs a logged-in `claude` CLI and is paid):
```bash
cd rnd/research/coordinator/repro
./fetch-assets.sh --check              # models + 2 packs, size and sha256 checked (dry run); drop --check to download (about 2.9 GB)
# then follow REPRODUCE.md sections 4 and 5: requests -> engine tree (0cfd4a77 + cut 7 patch) -> run.sh -> judge.mjs -> floor_metrics.py
# (REPRODUCE.md writes paths for its original package layout engine/, tools/, boar-eval/: here the engine files and tools sit together
#  in repro/, and boar-eval is the boar-bench repository)
```
You will get your own references and your own judge numbers, so the ratio moves; what should hold is the order of magnitude (raw about 0.5-0.6 on the 57 judged items) and near-zero declines on non-medical questions.

**R3. Re-compute a recorded arm from its stored traces and judgments (no model, no judge, seconds).** First fetch the traces from the dataset (`TRACES.md`): `hf download r4topunk/boar-traces --repo-type dataset --include "rnd/research/coordinator/arms/headpass-st/**" "rnd/research/coordinator/arms/packs/**" "rnd/research/coordinator/arms/packs-l2/**" "rnd/research/coordinator/arms/oracle-st/**" --local-dir .`. It needs the full repository: `agg_hp.py` also reads three sibling arms (`arms/packs-l2/tools/l2_agg.py`, `arms/packs/selftest-runs/`, `arms/oracle-st/tools/oracle-facts.json`); with only the headpass-st folder it drops the 9 packs with a WARN and writes a different `agg.json`. Every arm's `aggregates/` came from a script in its own `tools/` applied to the stored `runs/` or `gen/` files. Example, the head-pass experiment (verified for this release: the recomputed `agg.json` is identical to the shipped one):
```bash
cd rnd/research/coordinator/arms/headpass-st
cp aggregates/agg.json /tmp/agg.shipped.json                  # the script rewrites aggregates/agg.json in place
ROOT="$(cd ../../../../.. && pwd)"                            # the directory that contains this repository's rnd/ folder
sed "s#<workspace>#$ROOT#g" tools/agg_hp.py > /tmp/agg_hp.py  # old scripts carry the placeholder <workspace> for the original workspace
python3 -I /tmp/agg_hp.py                                     # prints the per-pack and pooled tables quoted in HEADPASS-ST.md
diff <(python3 -m json.tool --sort-keys /tmp/agg.shipped.json) <(python3 -m json.tool --sort-keys aggregates/agg.json) && echo IDENTICAL
```
Frozen criteria: `python3 tools/verify-criteria.py` checks every `*criterion*.sha256` (whole file or through `END FROZEN`); the few that do not verify, and why, are listed in `docs/PIN-EXCEPTIONS.md`. Scripts in other arms use the same placeholder (`<workspace>`, sometimes `<runner>` or `<home>` for machine-specific roots): substitute it the same way and read the script header for its inputs.

## What was excluded, and why

Details and counts: `docs/EXCLUDED.md`. In short (v1.1: the held-out and burnt sets are **no longer excluded**, they are in `rnd/heldout/` and `boar-bench`): the **app maintainer's data** (his questions, traces, correspondence and the scores of runs on his devices; arms built on them were removed whole), **private relays** (chat drafts, session handoffs), **competitor** scores and competitor-derived question sets (every file carrying 3 or more of a competitor team's 27 public test questions was removed; a few engine patches and traces keep 1-2 generic questions such as "tell me about japan"), **third-party raw web snapshots** (site tokens and copyright), **paid-gateway and spend ledgers**, **credentials**, **model weights and other large binaries** (none over 20 MB shipped; listed in `BOM.md` with source URLs and sha256). Redaction rules (names to roles, paths and hosts neutral, usage and spend lines removed) are in `docs/REDACTION.md`.

Questions, errata and reuse: see `CONTRIBUTING.md`.

## Licences and attribution

Code and scripts: MIT (`LICENSE-MIT`). Text, reports, aggregates and cards: CC BY 4.0 (`LICENSE-DOCS`). Engine patches: MIT, like the upstream app they modify. Third-party derived data (Wikipedia and Wikivoyage CC BY-SA 4.0, OpenStreetMap ODbL, Wikidata CC0, Stack Exchange CC BY-SA per post, MedlinePlus public domain, and others) keeps its source licence: see `NOTICE` and `DATA-CARD.md`.

**Health content is AI-reviewed, not clinically reviewed.** Nothing here is medical advice.

Cite as in `CITATION.cff`.
