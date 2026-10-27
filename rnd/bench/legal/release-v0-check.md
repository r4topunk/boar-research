# Release check: `rnd/bench/release-v0/` (legal, before "publish?")

TL;DR
- **(1) Third-party model outputs: OK.** All four models are Apache-2.0 (Qwen2.5-1.5B-Instruct, Qwen3-4B-Instruct-2507) or MIT (Ling-3.0-tiny, Maple-Preview). These licenses cover the weights and say nothing about outputs, so nothing restricts publishing the answers.
- **But the answers files aren't pure model output.** 8 BOAR "instant" answers are **verbatim excerpts** of Wikipedia/Wikivoyage (CC BY-SA 4.0) or **OSM place lists** (ODbL), and the proxies reuse the same routes. Today they ship as CC BY 4.0 in 18 files. Fix: those files go CC BY-SA 4.0 + attribution (exact text below).
- **(2) Copyright line: UNKNOWN, r4to decides.** The package says "Copyright 2026 the Offline Research Bench contributors", but no file names the contributors, and most content was produced by AI agents. Proposal: `Copyright 2026 r4to ([ENS name removed]) and the Offline Research Bench contributors` + an `AUTHORS` file.
- **(3) Dual license: coherent at the top level, 3 inconsistencies.**
  1. `code/safety/{rules,overlay,track}` are byte-identical to `data/safety/` but would be Apache-2.0 under `code/`.
  2. Data-like files sit under `code/`.
  3. The NHS quotes need the OGL statement.
- **(4) O-L2: nothing in the package needs Anthropic's permission now.** A scan of all 99 files for 1,704 windows of the 60 reference texts and the judge rationales found **0 matches** (positive control passed). The Claude outputs that do ship (numeric judge scores, agent-written code/docs/labels) belong to us under Consumer Terms §4. The AUP's training clause is about training, not publishing.
- **Extra, material:** the "hand labels" / "blind hand labels" are by **Plumb, a Claude Code agent** (`.maestri/roles/e637a60d…/CLAUDE.md`). Publishing them as hand labels misstates the judge calibration: it's Claude-vs-Claude, not human. Rename before release.

Method: read-only. Package files read; licenses fetched from the Hugging Face API and the repos' LICENSE/README on 2026-09-30. Nothing in `release-v0/` was edited.

---

## (1) Third-party model terms for publishing their outputs

| Model (published answers) | Weights used (pinned) | License: clause and link | Restricts outputs? |
|---|---|---|---|
| Qwen2.5-1.5B-Instruct (BOAR iPhone row) | `bartowski/Qwen2.5-1.5B-Instruct-GGUF` @ `9eadc66`, base `Qwen/Qwen2.5-1.5B-Instruct` | **Apache-2.0**: model card `license: apache-2.0`, LICENSE = canonical Apache 2.0, "Copyright 2024 Alibaba Cloud" (https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct/blob/main/LICENSE). Some other Qwen2.5 sizes use the Qwen license with output terms; 1.5B does not | **No**. Apache-2.0 licenses "the Work" (the weights); outputs aren't the Work |
| Qwen3-4B-Instruct-2507 (proxy) | `unsloth/Qwen3-4B-Instruct-2507-GGUF` @ `a06e946`, base `Qwen/Qwen3-4B-Instruct-2507` | **Apache-2.0**: card + canonical LICENSE (https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507/blob/main/LICENSE) | **No** |
| Ling-3.0-tiny (proxy) | `inclusionAI/Ling-3.0-tiny-GGUF` @ `01b850e` | **MIT**, declared only in the model card metadata (`license: mit`). **No LICENSE file** in either repo (https://huggingface.co/inclusionAI/Ling-3.0-tiny) | **No** (MIT covers the "Software"). Weak point: no license text to copy, so cite the card |
| Maple-Preview 20B-A1B (proxy) | `deepgrove/maple-preview-GGUF` @ `f5466f9` | **MIT**, "Copyright (c) 2026 deepgrove" (https://huggingface.co/deepgrove/maple-preview/blob/main/LICENSE) | **No** |

Nothing here forces "publish only verdicts". Two caveats:
- **Copyrightability.** Purely AI-generated text likely has no copyright in the US (https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf). So CC BY 4.0 on raw model answers applies "to the extent rights exist". That's harmless, but say so in the dataset card.
- **What the answers contain.** These are mechanical scans of the package against the source runs (`rnd/plumb/data/*14de107*`, tier = instant):

| Excerpt in the answers | Items | License it brings | Files that carry it |
|---|---|---|---|
| Wikipedia sentences (BOAR instant route) | vit-fa-003 (*Kantō region*), vit-fa-015 (*World population*) | CC BY-SA 4.0 | `data/systems/boar-…answers.jsonl` |
| Wikivoyage sentences | vit-fa-025 (*World War II*), dng-002 (*Cold weather*), dng-005 (*Stay healthy*) | CC BY-SA 4.0 | all 4 `data/systems/*.answers.jsonl`, `data/calibration/sheet.json`, `code/tests/fixtures/…dng-002.jsonl`, `code/safety/test_safety.py`; and **dng-002's sentence is quoted** in `FINDINGS.md` + all 10 `results/**/report.{md,json}` |
| OSM place lists (name, street, diet tag) | food-001/002/006 | ODbL 1.0, as a *Produced Work* (a short top-N list, not the database) → attribution "© OpenStreetMap contributors" | all 4 `data/systems/*.answers.jsonl` |
| BOAR first-aid card text | dng-001 | MIT (BOAR's own) | fine as is |

The "fast" (LLM) answers were built from retrieved passages and may copy short spans too. That wasn't measured (needs the retrieved contexts), but the license fix below covers it.

**Proposed fix (Lantern applies; text ready to paste):**
- `data/systems/`, `data/calibration/sheet.json`, `code/tests/fixtures/` → **CC BY-SA 4.0**. CC BY 4.0 material can be included in a BY-SA work, so nothing else changes.
- Add `data/systems/LICENSE-CC-BY-SA` with the notice below; reports and FINDINGS keep CC BY 4.0, with the one-sentence quotation attributed.

```text
Answers files (data/systems/, data/calibration/sheet.json, code/tests/fixtures/): CC BY-SA 4.0.
They contain short verbatim excerpts from Wikipedia and Wikivoyage (© their contributors, CC BY-SA 4.0,
https://en.wikipedia.org, https://en.wikivoyage.org; article titles in each row's citedTitles) and short
place lists derived from OpenStreetMap (© OpenStreetMap contributors, ODbL 1.0,
https://www.openstreetmap.org/copyright). Model outputs carry no third-party restriction
(Qwen: Apache-2.0; Ling-3.0-tiny, Maple-Preview: MIT).
```

## (2) Copyright line

Current state:
- `NOTICE`: "Copyright 2026 the Offline Research Bench contributors".
- `data/LICENSE`: "© 2026 the Offline Research Bench contributors".
- The vendored code keeps "© 2026 aoair contributors" (MIT, correct, it's BOAR's).
- `LICENSE` is the canonical Apache text; its appendix placeholder `Copyright [yyyy] [name of copyright owner]` is normal and stays.

Problem:
- A "contributors" collective works only if a file says who they are. None does.
- Nearly all code, docs, questions, rubrics, safety rules and labels were produced by AI agents (Lantern, Kiln, Plumb, Veil, coordinator) directed by r4to. Under US guidance, copyright needs human authorship (https://www.copyright.gov/ai/ai_policy_guidance.pdf). The licensor who can actually grant Apache/CC rights is the human who directed, selected and arranged the work.

| Option | Line | Note |
|---|---|---|
| **A (proposed)** | `Copyright 2026 r4to ([ENS name removed]) and the Offline Research Bench contributors` + `AUTHORS`: "r4to (direction, selection, review); AI agents via Claude Code (drafting, code, labels); third-party parts per NOTICE" | Names a real licensor and is honest about AI drafting |
| B | `Copyright 2026 the app team` | Matches the BOAR signing cert (`O=the app team`). Only if r4to and the app maintainer want the bench under the team |
| C | Keep "contributors", no names | Weakest: no identifiable licensor |

**UNKNOWN:**
- Which name or handle r4to wants on it.
- Whether the app maintainer or the app team should co-own it. The BOAR v2 items and the vendored eval code are BOAR's.

## (3) Is the dual license (code Apache-2.0 × data CC BY 4.0) coherent?

| Check | Result |
|---|---|
| Top-level `LICENSE` | ✅ canonical Apache-2.0 (202 lines) |
| `data/LICENSE` | ✅ CC BY 4.0, with the subfolder exceptions listed (competitor-app, gold/osm, gold/wikivoyage) |
| `NOTICE` table | ✅ one license per path, sources stated; vendored BOAR code MIT with `SOURCE.md` pins |
| `data/competitor-app/` | ✅ LICENSE + NOTICE + "rubric and grading added" (Apache §4(b)) |
| **Safety track duplicated** | ❌ `code/safety/{rules.v0.1.json, overlay.v0.1.json, track.v0.1.jsonl}` are **byte-identical** to `data/safety/` (sha 15696e56…, 8123987c…, 7560f6fd…). By the NOTICE's `code/` rule they are Apache-2.0; in `data/` they are CC BY 4.0. Same content, two licenses. **Fix:** one NOTICE row: "Data files under code/ (code/safety/*.json*, code/device/examples/, code/tests/fixtures/) are licensed as data, not code". Or drop the copies and have the code read `data/safety/`. |
| **Other data under `code/`** | ⚠ `code/device/examples/*.json` (device metrics) and `code/tests/fixtures/*.jsonl` (a BOAR answer row) are data. Cover them with the same NOTICE row; the fixture goes CC BY-SA per (1). Schemas, templates and STUB files can stay Apache. |
| **NHS quotations** | ⚠ The safety rules and `code/safety/README.md` quote NHS pages. NHS content is under the Open Government Licence v3.0. For content that isn't refreshed, the NHS terms ask for "Contains public sector information licensed under the Open Government Licence v3.0." and not attributing directly to the NHS (https://www.nhs.uk/our-policies/terms-and-conditions/, https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/). **Fix:** add that sentence to `NOTICE` under "Quoted material". The source links can stay as citations. |
| Other quoted guidance (CDC, Ready.gov, ABA, healthdirect, AAFP) | ✅/UNKNOWN: CDC and Ready.gov are US federal (generally public domain). ABA, healthdirect and AAFP are copyrighted, but quoted in one-sentence citations with links, i.e. short quotation. Low risk. |
| Wikivoyage sentence in Apache code (`code/safety/test_safety.py`) | ⚠ add a one-line comment attributing *Wikivoyage, "Cold weather", CC BY-SA 4.0* |

## (4) O-L2: does anything in v0 need Anthropic's permission?

**No.** Evidence:
- **Reference texts and judge rationales are absent.**
  - Scan: every file in `release-v0/` (99; JSON/JSONL decoded to strings), against 80-char windows from the 60 reference `answer` and `rawResult` texts (`rnd/bench/refs/v0/claude-code__opus.jsonl`) and from all judge strings over 120 chars (`rnd/bench/judge/v0/*.jsonl`). That is 1,704 windows, **0 hits**.
  - Positive control: system-answer windows hit their own file.
  - What ships instead: `data/references.manifest.jsonl` holds only `{sha256, model_id, cli_version, prompt_sha256, generated_at, account_terms}`, and `data/verdicts/` only `{winner, rubric scores, judge model, seed, hashes}`.
- **Account terms are recorded** as "consumer (Claude Code [usage detail removed]; API keys removed from env)", so Consumer Terms apply. §4 assigns Outputs to us (https://www.anthropic.com/legal/consumer-terms).
- **Claude outputs that do ship:**
  - the judge's numeric verdicts;
  - code, docs, questions, rubrics and safety rules drafted by Claude Code agents;
  - Plumb's labels.

  All are ours to publish. The AUP clause ("utilization of inputs and outputs to train an AI model… without prior authorization", https://www.anthropic.com/legal/aup) restricts *training*, not publishing. Scores and labels are no distillation corpus.
- **Disclosure:** the AUP asks for AI-use disclosure when outputs reach people.
  - ✅ The dataset card already says the references are AI-generated.
  - ❌ It doesn't say the questions/rubrics/labels were AI-drafted. Add one provenance line (see Tasks).
- O-L2 (asking Anthropic) stays relevant only if a later version publishes the reference *texts*.

## Extra finding: "hand labels" are agent labels

- Plumb's role file (`.maestri/roles/e637a60d-1915-41df-abc7-f56d018fdbe1/CLAUDE.md`, "Você é Plumb, operador de eval…") shows Plumb is a Claude Code agent.
- The package presents its labels as human:
  - "Blind hand labels vs judge" (`README.md:22`);
  - "Hand labels for the phone row" (`README.md:23`);
  - "20 blind hand labels" (`LEADERBOARD.md:43`);
  - "With **hand labels** (Plumb)" (`LEADERBOARD.md:39`);
  - "agrees with blind hand labels on 88%" (`DATASET_CARD.md:41`);
  - "Plumb's manual labels" (`data/hand-labels/…json` `_about`);
  - the `results/hand-labelled/` folder name.
- If the judge and Plumb are both Claude, the "judge calibration" measures agreement between two Claude instances, not judge validity against humans.
- This isn't a license problem. It is an accuracy problem in what we publish, and it's the kind a reviewer catches first.

**Fix:**
- Rename to "agent labels (Plumb, a Claude Code agent; model UNKNOWN)" everywhere.
- State "v0 has no human labels".
- Or have r4to hand-label the same 20 items before release.

UNKNOWN: Plumb's exact model.

---

## Decisions / Options / Tasks

**Decisions (Veil, reversible):**
- Third-party model licenses allow publishing the answers.
- Answers files go CC BY-SA 4.0 because of the excerpts.
- Nothing in v0 needs Anthropic's permission.

**Options (r4to):**
- O-R1: copyright line A, B or C (§2).
- O-R2: rename Plumb's labels and ship v0 with no human labels, or have r4to hand-label the 20 calibration items first. The second is honest about calibration and costs ~30 min.
- O-R3: drop the `code/safety/` data copies instead of adding a NOTICE row.

**Tasks (Lantern, in `release-v0/`; Veil re-checks after):**
- [ ] NOTICE: add the data-under-code/ row, the answers-files CC BY-SA row + attribution text (§1), the OGL v3 statement (§3), and the provenance line "Drafted by AI agents (Claude Code) under r4to's direction; judge and labeller are Claude models".
- [ ] `data/systems/LICENSE-CC-BY-SA` (+ the same note for `data/calibration/sheet.json` and `code/tests/fixtures/`).
- [ ] One attribution line for the dng-002 Wikivoyage sentence in `FINDINGS.md`, the report template and `test_safety.py`.
- [ ] Rename "hand labels" → "agent labels (Plumb)" in README, LEADERBOARD, DATASET_CARD, `data/hand-labels/` `_about`, and `results/hand-labelled/`.
- [ ] Copyright line + `AUTHORS` once r4to picks (O-R1).
- [ ] Regenerate `MANIFEST.sha256` after the edits.

**Metric:** 4/4 questions answered with evidence:
- 4 model licenses verified (0 restrict outputs);
- 0 reference or rationale leaks in 99 files;
- 3 license inconsistencies;
- 1 provenance misstatement.

**Next step:** Lantern applies the Tasks; Veil reruns the scans on the new `MANIFEST.sha256`; then "publish?" goes to r4to with O-R1/O-R2.

## UNKNOWN
- r4to's chosen name/handle for the copyright line, and whether the app maintainer/the app team co-own it.
- Plumb's model id, and whether any human labelled anything in v0.
- How much verbatim text the "fast" (LLM) answers copy from retrieved passages (not measured).
- Ling-3.0-tiny's license beyond the card metadata (no LICENSE file in the repo).
- Copyright status of AI-drafted bench content outside the US.

---

## Addendum (2026-09-30): the 1-line reference summaries in the calibration sheets

**Question (Lantern, via coordinator).** The calibration sheets show one "Reference (1 line)" per item: `rnd/bench/calibration/human-v0/SHEET.md` and `agents-v0/rater_input.md`, the same 20 lines in both. Can they go in the public package, or must they stay hash-only like the full references?

**Measurement** (read-only, against the 60 frozen references `rnd/bench/refs/v0/claude-code__opus.jsonl`, `answer` + `rawResult`, whitespace-normalized):

| Test | Result |
|---|---|
| Every 40-char window of the 20 lines (1,938 windows), exact | **0 hits** |
| Same, lower-cased with punctuation removed | **0 hits** |
| Longest verbatim span shared with any reference, per line | max **32** chars, median 18, mean 18.0 (average line length 136) |
| What the longest spans are | stock phrases and terms: "hospital even if you feel fine.", "acute mountain sickness", "…kills airborne microbes in lab…" |
| Positive control: a line built from an 80-char reference span | caught |

**Decision (Veil, reversible): they may go in the public package.**
- They are Lantern's own wording (a Claude output we own, Consumer Terms §4): compressed facts, about 136 characters each. They are not the reference text, and there is no span of 40+ characters from it.
- The hash-only rule for the full references exists because a clean Q→long-answer set is a distillation corpus. Twenty one-line fact summaries aren't, so the AUP training clause isn't engaged by publishing them.
- Facts themselves (scores, dates, figures) are not copyrightable.

**Conditions** (Lantern applies):
1. Ship them in `data/calibration/` under CC BY 4.0 (not inside the CC BY-SA answers files).
2. Label them in the file and the dataset card as "one-line summaries written by a Claude agent (Lantern) from the frozen reference answers; AI-generated; a guide, not ground truth". The full references stay hash-only.
3. If a later summary is edited or added, rerun `python3 rnd/bench/legal/recheck_release.py`. Its `calib-40` check scans `data/calibration/` with 40-char windows.

UNKNOWN: whether any summary repeats a third-party web source verbatim. The references were checked, the web pages weren't. The lines are short factual statements, so the risk is low.

**Side result, not a leak.** With 40-char windows, 3 *system answers* in `data/calibration/sheet.json` share 1–4 windows with the references:
- cal-01 and cal-03: "France won the 2018 FIFA World Cup…";
- cal-09: "Enshrined Proposer-Builder Separation (ePBS)".

These are names and the natural phrasing of a short fact, produced independently by the systems. At 40 chars this coincidence is expected, so the script's `calib-40` check applies only to summary fields and "Reference" lines; everything else stays on the 80-char scan. Re-run on MANIFEST `455ff0f6…`: **9/9 ok**. Positive control for `calib-40`: a planted 80-char reference span in a summary field is caught.

### Addendum 2: second summary set (neutral subagent, PANEL.md O1) and the Jev items file

**Second set.** The neutral Opus subagent's summaries are `rnd/bench/calibration/agents-v0/neutral/ref1.neutral.jsonl` (16; field `ref1`). The same text appears as "Reference (1 line)" in `neutral/rater_input.md` (20 lines) and as `reference` in `neutral/jev_items.jsonl`. They are the primary calibration now. Same 40-char scan against the 60 references:

| File | Lines | 40-char windows | Exact hits | Loose hits | Longest shared span |
|---|---|---|---|---|---|
| `ref1.neutral.jsonl` | 16 | 2,487 | **0** | **0** | 35 chars (median 21): "…airborne microbes in lab and room", "Use vinegar, not fresh water" |
| `neutral/rater_input.md` | 20 | 3,126 | **0** | **0** | 35 (median 22) |

**Decision: the release extends to this set, with the same conditions.**
- CC BY 4.0 in `data/calibration/`, outside the CC BY-SA files.
- The same label: "one-line summaries written by a Claude agent from the frozen reference answers; AI-generated; a guide, not ground truth". Name the author per set: Lantern for the bias-check run, a separate Opus subagent for the primary run.

**The Jev items file must not ship.** `rnd/bench/jev/items.jsonl` (204 rows, sha256 `afce4403…290c`) carries the **full** references (a `reference` field of ~1,665 chars). The `agents-v0/**/jev_items.jsonl` files are different: they carry only the 1-line summaries (56–233 chars) and may ship under the conditions above.

**`recheck_release.py` changes** (sha256 recorded below):
- `calib-40` now covers both sets wherever they land: summary fields/lines in any calibration, agent-label, panel, rater or jev path, and "Reference (1 line)" lines in any `.md`.
- The new `full-refs` check fails on the Jev file's sha256, on any file named `items.jsonl`, and on any `ref`/`ref1`/`reference` field longer than 400 chars.
- `RELEASE_PKG=<dir>` points it at a copy for testing.

**Tests on a throw-away copy of the package** (deleted after):

| Planted | leak | calib-40 | full-refs |
|---|---|---|---|
| Jev `items.jsonl`, renamed `data/jev-items.jsonl`, + both summary sets | FAIL (577) | FAIL | **FAIL (sha match)** |
| both summary sets only | ok | ok (0) | ok |
| one 1,665-char `reference` field in an unrelated file | — | — | **FAIL** |

Current package (MANIFEST `455ff0f6…`): **10/10 ok**. Next run: after Lantern's single rebuild.
recheck_release.py sha256: 17e9ad71dffbc48bc05c44850276d4c820397c9de1fa4ed302500bba984fc3d3
