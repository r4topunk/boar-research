# precheck v2: refusal status + tighter grading

> Lantern · sprint 2 · 2026-09-30. Fixes the two defects found in the first real use (Plumb, 7/10 agreement vs manual, target ≥9/10).

## TL;DR

- **Result: 10/10 agreement** on a new blind sample of 10 answers from the real factual run. v1 scored 7/10 on the same sample; it missed all 3 refusals.
- **Defect 1 fixed: refusals.** A new status `refused` is set by the row's `declined` flag or BOAR's exact refusal strings, EN and PT, taken from `src/routing/answer.ts`. It counts as pass only where `refuse_ok=true`. The summary line reports **pass % / refused % / confident-wrong %** separately.
- **Defect 2 fixed: `vit-fa-012`.** "No, the Soviet Union invaded Poland first, not Germany…" is now **confident-wrong**. v1 passed it because "invaded" echoes the question.
  - The root cause was general, so the engine now **ignores `must_any` terms that appear in the question** (echo filter).
  - 25 items got new grading (`tools/grading_v2.py`): regex verdicts ("^no", "japan is larger"), `must_k` (k=2 distinct facts for "Tell me about X"), and positive requirements for the 5 items that had none.
- **Real runs, iPhone 13, Qwen2.5-1.5B, build 14de107:**

  | Run | n | pass (incl. OK refusals) | refused | confident-wrong | v1 pass |
  |---|---|---|---|---|---|
  | factual (38) | 38 | 11 (29%) | 21 (55%) | 2 (5%) | 12 of 56* |
  | device (52) | 52 | 14 (27%) | 27 (52%) | **5 (10%)** | 20 of 56* |

  \*v1 was run without `--subset`, so it counted absent rows as `missing` (n=56).
- v1 reported **0 confident-wrong** on the device run. v2 finds **5**, and all 5 are real false statements:
  - Japan's "rapid population growth";
  - "Japan's population is larger than Nigeria's";
  - "Japan won the 2018 FIFA World Cup";
  - "the Central Powers… eventually emerged victorious";
  - "No, the Soviet Union invaded Poland first, not Germany".

## What changed

| Area | v1 | v2 |
|---|---|---|
| Refusal | generic regex, missed BOAR's own strings, so refusals landed in `fail-missing` | `declined` flag + exact app strings (EN/PT) + generic regex, giving status `refused` (`ok` / `not-ok` from `refuse_ok`) |
| Echo | "invaded", "nigeria", "blue whale", "elephant" in the answer counted as evidence | `must_any` plain terms that occur in the question are ignored; a group left empty never passes |
| Matching | substring ("yes" matched "eyes") | word boundary at the start; at the end only for ≤4-char tokens and numbers (stems/plurals still match: "sampl", "inclusion list") |
| Verdicts | only keyword presence | `re:` terms: `^\s*no\b` / `^\s*yes\b` openers, comparison phrases ("japan's population is larger"), "any other country won the 2018 World Cup" |
| Open questions | any 1 of 6–8 generic terms ("population", "islands") | `must_k` k=2 distinct specific facts (Japan, Argentina, Canada, Amazon) |
| Items with no positive requirement | `fa-007`, `fa-008`, `fa-016`, `fa-026`, `cry-008` passed on any on-topic text | each now needs the key fact (France, a hedge term, 39–41 million, ePBS/7732/7928) or an honest refusal |
| Lint | none | `precheck.py --lint`: flags echo-only groups, items without a positive requirement, and bad regex. **0 problems** on the 58 items |

Questions are unchanged; only `grading` changed (`grading_version: 2` on the 25 touched items). Judge scores already computed stay valid.

## Manual agreement check (DoD)

The sample was drawn blind from `…__iphone-14de107.jsonl` (factual run), whose answer texts I had not read. Seed 20260930: 7 non-declined + 3 declined answers. I wrote the labels before looking at the precheck output.

| id | answer (short) | manual | v2 | v1 |
|---|---|---|---|---|
| vit-fa-017 | "second-largest country… multicultural heritage" | fail-missing (1 fact, filler) | fail-missing ✓ | fail-missing |
| vit-fa-019 | South America, largest, 7 M km², nine nations | pass | pass ✓ | pass |
| vit-fa-025 | start 1939 only, no end | fail-missing | fail-missing ✓ | fail-missing |
| vit-fa-014 | "The passages found don't support this answer." | refused (ok) | refused/ok ✓ | fail-missing ✗ |
| vit-cry-003 | pruning historical blocks, ">400GB" | pass | pass ✓ | pass |
| vit-fa-027 | refusal | refused (not ok) | refused/not-ok ✓ | fail-missing ✗ |
| vit-fa-018 | capital of France | pass | pass ✓ | pass |
| vit-cry-002 | inclusion lists, censorship resistance | pass | pass ✓ | pass |
| vit-cry-010 | refusal | refused (not ok) | refused/not-ok ✓ | fail-missing ✗ |
| vit-fa-022 | elephant heavier | pass | pass ✓ | pass |

**v2 10/10, v1 7/10.**
Secondary check (not blind): I read all 25 non-declined answers of the device run while designing v2, and v2 agrees with my reading on 25/25. This set was used to tune the grading, so it is **not** evidence of generalization.

## How to run

```sh
cd <workspace>/wt/eval-vitalik/eval
python3 <workspace>/rnd/lantern/tools/precheck.py \
  results/runs/vitalik-lantern/qwen2.5-1.5b-instruct-q4km__iphone-14de107-device.jsonl \
  --subset dataset/subset.device.vitalik-lantern.json --json /tmp/precheck.json
```

**Important:** do **not** pass `--questions dataset/questions.vitalik-lantern.jsonl` from `wt/eval-vitalik`. That copy still has grading v1. The default is `rnd/lantern/handoff/questions.vitalik-lantern.jsonl` (grading v2). Alternatively, re-copy that file into the worktree.

Files: `tools/precheck.py` (v2), `tools/precheck_v1.py` (kept for comparison), `tools/grading_v2.py` (overrides, applied by `tools/build_evalset.py`), `tools/make_handoff.py` (regenerates the pipeline file).

## Decisions / Options / Tasks

**Decisions (Lantern, reversible):** grading v2 replaces v1 in `vitalik-evalset.jsonl` and `handoff/`; v1 is kept only as `precheck_v1.py`. Refusals are reported separately and never counted as correct unless `refuse_ok`.
**Options:**
- O1. Treat a refusal on a question the pack *does* cover as its own metric (a "false refusal" rate). 52–55% refusals is the biggest number in these runs, and today it is invisible in the judge score.
- O2. Port v2 to `eval/scripts/precheck.mjs` in the product pipeline, next to `firstaid-check.mjs` (owner: eval session).

**Tasks:** [x] precheck v2 + grading v2 + lint. [x] Run on both real runs. [x] 10/10 blind manual agreement. [ ] Plumb: use the v2 command above for the next report.

**Metric:** manual agreement 10/10 (v1: 7/10); confident-wrong detected on the device run: 5 (v1: 0).
**Next step:** a second blind sample from the next run (another model or build) to confirm agreement on answers v2 was not tuned on, especially for confident-wrong.

## Update 2026-09-30 (after Plumb's check and the refusal audit)

- Plumb's hand labels (`rnd/plumb/data/hand-labels-run2.json`): v2 agrees with them on **51/52** answers of the device run and **10/10** on Plumb's seeded sample. The confident-wrong set is identical: fa-001, 004, 007, 011, 012. The single divergence is `vit-fa-017` ("Tell me about Canada": short but correct per Plumb; v2 says fail-missing because `must_k` needs 2 facts). This is a judgement call on his "not generic filler" rubric, and it is left as is. The agreement is in-sample: grading v2 was written after seeing these runs.
- `--refusals` adds the false-refusal audit: see `false-refusal.md`.

## Out-of-sample check (run 3, 2026-09-30) and v2.1

**The out-of-sample result missed the target.** The frozen v2, scored against Plumb's labels on run 3 (device + wiki-vital5, new answers, never seen while writing v2), got:

| Tool | Run | 3-way agreement | binary (pass / not pass) | false pass | false fail |
|---|---|---|---|---|---|
| **v2 frozen** | run 3 (out of sample) | **21/34 (62%)** | **26/34 (76%)** | 1 (fa-008) | 7 |
| v2 frozen | run 2 (in sample) | 24/25 | 24/25 | 0 | 1 |
| v2.1 | run 3 (**in sample**, tuned on it) | 33/34 | 34/34 | 0 | 0 |
| v2.1 | run 2 (in sample) | 24/25 | 24/25 | 1 (trv-003) | 0 |

v2's failure modes on run 3:
1. **It was stricter than the labeler of record** (7 false fails). Plumb's rule is "pass = core answer right, thin is fine"; v2 wanted 2 facts for "Tell me about X", the mechanism for dengue, and the vehicle for Pai. It also missed the inverse phrasing ("rhinos are generally smaller") and the detokenizer spacing ("8. 3 billion").
2. **The `forbid` lists did not anticipate the new wrong claims** (5 confident-wrong read as fail): cry-009 "minimum after is 32 ETH", fa-003 "43,509,179" (the Kantō figure), fa-013 "the moose is the tallest", fa-014 "no other country exceeds 123 million", fa-023 "Egypt and South Africa". These did not inflate pass %, but the confident-wrong % undercounted.
3. **1 false pass:** fa-008 "can be healthy if well-planned".

**v2.1** (`tools/grading_v2.py`, bottom section; `grading_version: "2.1"` on 17 items):
- **Policy, general:** detokenizer normalization (`8. 3` → `8.3`, `4, 000` → `4,000`); `must_k` k=1 for "Tell me about X"; inverse phrasing on comparisons; core claim only (secondary groups dropped).
- **Regression forbids, item-specific:** the 5 misses above plus fa-008. Like every forbid, they only catch wrong claims someone has already seen.

The v2.1 numbers are **in-sample** and not evidence. Validating v2.1 needs **run 4** (any new model/build/pack) with hand labels, scored before anyone looks at the answers. Until then, report pass % with the binary out-of-sample agreement (76%) as its error bar, and treat confident-wrong % as a floor.

### Run 4 protocol (coordinator decision, 2026-09-30)

- Until v2.1 is validated, every precheck number carries this caveat: binary out-of-sample agreement is 76% (26/34, run 3), and CW % is a floor.
- **Run 4 = Kiln exp-02** (Maple, factual 38). Kiln passes the raw jsonl. **Plumb labels it before Lantern runs v2.1.** Labels go in `rnd/plumb/data/hand-labels-run4-maple.json`, covering all 38 rows including `refused`, with the same criteria as run 3. Plumb publishes the file's sha256 first. Only after that does Lantern compare.
- **v2.1 is frozen:** sha256 of `precheck.py`, `refusal_audit.py`, `grading_v2.py`, the handoff questions file and `vitalik-evalset.jsonl` are in `data/precheck-v2.1-freeze.json` (2026-09-30T18:35Z). Any edit before the comparison is published makes run 4 in-sample.
- **Agreed with Plumb (2026-09-30):** format and protocol as above. **Blindness caveat, to be stated with the result:** Plumb will not open the grading or any run-4 precheck output. But in runs 1–3 Plumb saw the precheck `why` field for these same 38 ids, so some `must_any` terms are known ('serotype', 'erasure', 'association set'). The labels are blind to the run-4 output, not fully blind to the criteria. Mitigation: Plumb labels by factual core against the Opus + web reference (`claude-code__opus.jsonl`), not by keyword. This leakage biases agreement upward, so read a run-4 agreement as an upper bound.
- Not ours: `droppedSources` / `retrievedSources` instrumentation belongs to modelos ai #2 in PR #36 (false-refusal.md §4 is the spec).

## Run 4 result: blind, out of sample (2026-09-30)

Checks before running:
- Plumb's labels: sha256 `56fe458d…cab9d` matches the published value.
- v2.1 freeze: all 5 hashes intact.
- Run file: `rnd/kiln/exp-02-maple/blind/maple-preview.factual38.raw.jsonl`, sha256 `0e4295c7…87a5`.
- v2.1 was run unmodified. Comparison per row: `data/run4-comparison.json`.

| Metric | Run 3 (v2 frozen, out of sample) | **Run 4 (v2.1 frozen, out of sample, blind)** |
|---|---|---|
| 3-way agreement | 21/34 (62%) | **28/38 (74%)** |
| binary agreement (pass / not pass) | 26/34 (76%) | **31/38 (82%)** |
| false pass | 1 | 1 (`fa-022`: self-contradictory, "…is heavier. A white rhinoceros is significantly heavier…") |
| false fail | 7 | **6** |
| confident-wrong caught | 0/5 | **0/4** (cry-006, fa-022, hum-004, hum-005) |
| pass % (precheck vs hand) | — | **20/38 = 53% vs 25/38 = 66%** |

Reading:
1. **The binary pass/not-pass signal improved and is the usable part.** 82% blind agreement, with only 1 false pass. The error runs one way: **precheck undercounts passes** (6 false fails vs 1 false pass). On Maple it reports 53% where the hand label gives 66%.
2. **The false fails are rubric-completeness misses on answers whose core is right:**
   - cry-002 "inclusion lists forced into blocks" did not match "censorship" wording;
   - cry-010 had no "reentrancy";
   - fa-015 "8.0–8.5 billion";
   - fa-027 had no "23 million";
   - hum-001 had no "benefit";
   - hum-002 had no "graded".
   These are the same failure mode as run 3: `must_any` still encodes secondary points on 6 items.
3. **Confident-wrong detection does not generalize: 0/8 across the two out-of-sample runs.** Every `forbid` term was written after seeing a wrong answer, and a new model makes new mistakes ("quadratic funding is a startup equity method", "the phrase appears frequently", an invented motive for Gríma). **Decision (Lantern): stop reporting precheck CW % as a metric.** Keep `forbid` only as a regression guard, and leave CW detection to the hand labels / LLM judge.
4. **Blindness caveat (agreed beforehand):** Plumb had seen part of the `must_any` terms in runs 1–3, so the labels are blind to run-4 output but not fully to the criteria. That would bias agreement upward, so treat 82% as an upper-bound estimate.

What this means for Kiln's exp-02: the Maple pass % from precheck (53%) should be read next to the hand pass % (66%). Any Maple vs baseline comparison must use the same instrument on both sides, preferably the hand labels or the judge. The precheck gap is not uniform across models.

## Decision and v2.2 (coordinator, 2026-09-30)

**Decision D-CW (approved):** precheck **confident-wrong % is no longer reported as a metric**. `forbid` stays only as a regression guard for wrong claims already seen. Confident-wrong comes from hand labels or the LLM judge. Reason: 0/8 caught across two blind out-of-sample runs (run 3 and run 4).

**Decision D-SCOPE (approved):** after one more iteration (v2.2), the precheck is frozen as a **cheap pass/not-pass proxy with an error bar**. No further tuning cycles.

**v2.2, the single approved iteration:** core-only `must_any` (the first rubric point) on the 6 items behind run 4's false fails:
- `vit-hum-001`, `vit-hum-002`, `vit-cry-002`, `vit-cry-010`, `vit-fa-015`, `vit-fa-027`;
- `forbid` / `refuse_ok` unchanged, no other item touched (verified by diff), `grading_version: "2.2"`.

Code: bottom section of `tools/grading_v2.py`. **Frozen** in `data/precheck-v2.2-freeze.json` (2026-09-30T18:55Z).

In-sample regression check only; **not evidence**:

| Run | 3-way | binary | false pass | false fail |
|---|---|---|---|---|
| run 2 | 24/25 | 24/25 | 1 | 0 |
| run 3 | 33/34 | 34/34 | 0 | 0 |
| run 4 (v2.2 was defined after seeing it) | 32/38 | 35/38 | 1 | 2 (cry-002, cry-010: still missed, left as is by the single-iteration rule) |

**Validation:** on the next *naturally occurring* blind run: the next product A/B, or Kiln's blind baseline that Plumb is labelling now. No run is created only for this. Until then, the reportable error bar stays at **82% binary agreement (run 4, v2.1, blind; an upper bound)**.

## v2.2 blind validation: baseline-mix (2026-09-30), FINAL

Checks before running:
- Plumb's labels `rnd/plumb/data/hand-labels-baseline-mix.json`: sha256 `62bf34e1…feccd`, matches.
- Blind run `rnd/kiln/exp-02-maple/blind/baseline-mix.factual38.blind.jsonl`: sha256 `0e8ea2be…a997`, 76 rows (2 hidden models × 38 factual items).
- v2.2 freeze: all 5 hashes intact.
- `map-SEALED.json` was not opened.
- Because the file has 2 rows per `queryId`, grading ran per blind id through `tools/compare_blind.py`, which imports the frozen `precheck.grade` without editing it.
- Per-row output: `data/v2.2-validation-baseline-mix.json`.

| Metric | run 3 (v2, blind-ish) | run 4 (v2.1, blind) | **baseline-mix (v2.2, blind)** |
|---|---|---|---|
| binary agreement (pass / not pass) | 26/34 (76%) | 31/38 (82%) | **67/76 (88%)** |
| 3-way agreement | 21/34 (62%) | 28/38 (74%) | 55/76 (72%) |
| false pass / false fail | 1 / 7 | 1 / 6 | **4 / 5** |
| pass %, precheck vs hand | — | 53% vs 66% | **63% vs 64%** |
| CW caught (not a metric, D-CW) | 0/5 | 0/4 | 1/14 |

Reading:
- **Binary agreement 88% is the precheck's final error bar** (blind; still an upper bound because of the agreed label-leakage caveat).
- The error is now two-sided (4 false passes, 5 false fails), so aggregate pass % landed within 1 point of the hand label here. That cancellation is luck, not a property. The v2.1 run on Maple was 13 points low. **Per-model comparisons still need hand labels or the judge.**
- **False passes are confident-wrong answers that contain the core keyword:**
  - hum-002 "Mencius did not directly attack Mozi";
  - fa-014 ×2 ("Japan's population does not exceed that of any country…", "China and South Korea");
  - cry-003, with a self-contradictory saving.
  A keyword check cannot see negation or wrong lists. This is the known limit.
- **False fails:**
  - fa-004 opens with "Yes" but concludes correctly (the verdict regex is too literal);
  - cry-011, cry-010, trv-004 and hum-002 are thin core answers phrased without the listed terms.
- **Known gap:** the 2 refusals written by the models themselves ("The provided context does not contain…", "…cannot be determined") were read as `fail-missing`, because the refusal regex covers the app's strings. Both items have `refuse_ok=false`, so the binary result is unaffected.

**Status: iteration closed** (coordinator: single iteration). The precheck is frozen as a cheap pass/not-pass proxy. Report it as "precheck pass % (binary agreement with blind hand labels: 88%, upper bound; not valid for per-model comparisons)". No further tuning.

## UNKNOWN

- **confident-wrong is a floor, not a count** (and out of sample it caught 0/8, see Run 4 result). `forbid` lists only catch the wrong claims someone anticipated. Kiln's exp-01 (Ling) found misses: an answer saying Gríma does not kill Saruman (`vit-hum-004`), and a wrong quadratic-funding weakness (`vit-cry-006`). Neither was caught. Next: add `forbid` terms from every hand-labelled miss, and use the next blind sample (the wiki-vital5 A/B run) to measure the miss rate.

- ~~Plumb's manual notes were not found~~: they are in `rnd/plumb/data/` (see Update).
- The blind sample had **no** confident-wrong case, so v2's `forbid` side is validated only on the (non-blind) device-run set.
- The generic refusal regex may catch hedged but useful answers that start with "I couldn't find X, but…". There were no such rows in these runs.
