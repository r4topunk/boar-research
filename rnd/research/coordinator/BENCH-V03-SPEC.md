# Bench v0.3: claim set written outside the Claude family (spec, coordinator draft 2026-10-07)

Inputs read: bench/v0.2 DATASET_CARD, HELD-OUT, questions.schema.json, plan/ (README, item-spec, analysis-plan, script headers, addenda), refs/ (gen_refs.mjs, build_manifest.py headers), validate.py, similarity.py, assemble.py; PIPELINE-AUDIT-2026-10-06 §1 and §4; CLAIM-RUNS-cut6; CLAIM-RESULTS-cut6 (aggregates); QUEUE L703, L770. Nothing under blind/ or rnd/veil/ was read. Companion files: `bench-v03/writer-prompts.md` (10 paste-ready blocks) and `bench-v03/refs-prompt.md`.

**Coordinator review (2026-10-07 09:5x):** accepted as the working spec. Already decided since the draft: the claim build is **cut 7** (= cut 6 + FACTS r6; traces differ from cut 6 only on FACTS fires, so the §8 "control = cut 6" run reduces to judging fired items, likely 0 calls). D1–D3 and the hours budget in §8 are r4to's call. The worked examples in writer-prompts.md were written from memory and their URLs were not re-opened: they are format examples, never bench items.

## 1. TL;DR
- **Why:** v0.2 is burnt. Its plaintext is in boar-eval history (`d8154b6`), it has had 4 runs, and all of its question writers, rewriters and reference answers came from Claude models, the same family as the Opus judge. No final claim number can come from it.
- **Who writes what:** r4to writes 110 items with one non-Claude model in its web UI (no API, no automation). The same model with web search writes the references from the reference.v1 prompt, unchanged. The coordinator runs the gates and the freeze. Kiln runs **one** claim run.
- **When:** writing 10-08…10-17, references 10-18…10-19, gates and freeze 10-20, claim run by 10-24, buffer to 10-31.
- **What it fixes:** questions, gold answers, rubrics and references are no longer written by the judge's family, and the plaintext stays out of git. The 10 strata of v0.2 are kept.
- **What it does not fix:** judge-family bias, because Opus `judge.v1` still scores (only the O3 cross-family judge fixes that). It also has one writer's style, and references from a different family move the denominator: v0.3 ratios are not 1:1 comparable with v0.2. The control and anchor runs in §8 measure that.

## 2. Composition (same strata as v0.2 so cut-level numbers stay stratum-comparable)
| category | n | wave 1 | special |
|---|---|---|---|
| explanation | 21 | 11 | |
| reasoning | 21 | 11 | real-world facts, no pure puzzles |
| comparison | 13 | 7 | |
| crypto | 13 | 7 | no price items, no client-default facts |
| honesty-refusal | 12 | 7 | 4 false premise (refuse_ok false), 4 unknowable + 4 time-pinned (refuse_ok true), type named in the rubric |
| health | 8 | 4 | danger false; NHS/CDC/WHO/NIH sources |
| danger | 10 | 6 | danger true; conduct from Ready.gov/NHS/CDC/NWS; 2 context-dependent; ≥ 4 first-aid + ≥ 4 hazard |
| synthesis | 6 | 3 | |
| travel-practical / travel-local | 4 / 2 | 2 / 2 | strata.py merges them into "travel" (6) |
- English only. Every item is graded by precheck. refuse_ok = 8 (v0.2: 9). danger: true = 10.
- Rules from `plan/item-spec.draft.md` (sha `e1c0943c…`), unchanged: the rubric is written for the judge with 1–2 "Penalize:" bullets; honesty items name their type and a "Decline rule:"; phrasing is ⅓ first-person, ⅓ direct question, ⅓ imperative.
- New for v0.3 (against convergence): ≥ 40 % of items centred outside Europe and North America, at most 2 per country, and each item hinges on ≥ 1 concrete checkable fact.
- **Schema delta** (`bench/v0.3/questions.schema.json` = v0.2 schema plus three changes). Validated on 10-07 against the 20 worked examples: all pass the schema and their own precheck.
```json
"id":     {"anyOf": [ …v0.2 patterns…, {"pattern": "^v03-[a-z-]+-[0-9]{2}$"}]},
"origin": {"enum":  [ …v0.2 values…, "v0.3-ext"]},
"allOf":  [ …, {"if": {"properties": {"origin": {"const": "v0.3-ext"}}, "required": ["origin"]},
               "then": {"required": ["answer"], "properties": {"license": {"const": "CC-BY-4.0"}}}}]
```
- `safety_rules` is not written by the writer. The coordinator maps it in `assemble.py` to rules **v0.7** (current, addendum 04), with the v0.2 rule: a rule is assigned only when its conduct is the item's conduct and the gold passes it, otherwise `[]`. The v0.7 forbid rules target v0.2 danger topics, which v0.3 avoids, so expect most v0.3 danger items to be judge-only for safety. The card must say so.
- Ids: `v03-<category>-NN`. Ids 01…w1 are wave 1, so a 60-item fallback is a fixed id range, declared now.

## 3. Writer procedure for r4to (copy-paste; details and blocks in `bench-v03/writer-prompts.md`)
1. **Setup, once (20 min).** Pick the model (§9 D1). Turn memory and chat-history reference OFF, the training opt-out ON and web search ON. Create the folder `<private held-out dir>`. It is outside every git repo; researchers never read blind/.
2. **Never show the model any BOAR material:** no packs, v0.1/v0.2 items, traces, failure lists, QUEUE or research cards, and not the word "BOAR". The paste blocks are the only input. The do-not-use list in them holds topic names only (2–6 words each), taken from the public v0.2 card, the v0.1 public set and the safety track.
3. **One fresh chat per category** (10 chats). In the block, replace `{{PROVENANCE}}` with `writer-human+<model name exactly as in the picker> 2026-10-DD` (the writing day), then paste it.
4. **Topics first.** The model proposes 2N topics (topic | region | phrasing | key fact | URL). r4to picks N: strike anything canonical or textbook-famous, check the region quota and the phrasing mix, and avoid repeating a topic used in another category.
5. **Items.** Send `Picks: …` and get JSONL in batches of ≤ 7 (wave 1 ids first). Paste each batch into `blind/bench-v03/work/<category>.jsonl`. Also keep the `V-STYLE IDS:` line in `work/vstyle.ids` if D3 = fold.
6. **Fact-check every item by hand (≈ 4 of the 8 min per item).** Open each `reference_sources` URL. Confirm the gold's key fact and every number in the rubric on the page, and confirm each "Penalize:" bullet names something actually wrong. If a fact is not on a cited page, ask the model for a better source or drop the topic. The URL in `reference_sources` is the record.
7. **Pilot on 10-08:** travel-local (2) and travel-practical (4) first. The coordinator runs a format-only validate the same day (ids, counts, precheck errors; no topic review) and r4to records his real minutes per item. That figure replaces the 8-min estimate in §8.
8. **At the end (15 min):** read all question lines once, side by side, for same-topic pairs across categories.
- **Claude never edits item text.** Gate failures go back to r4to as `id + reason`. He fixes them in the same chat (`In <id>, the page <URL> says … Fix …`), or by hand. This covers fact fixes too; on v0.2 the coordinator made two fact fixes itself.
- **Convergence guard** (the v0.2 failure: 36 same-topic pairs out of 55 among two Claude writers, then 7 of 37 again among the rewriters). The do-not-use list names every v0.2 collision topic from the card: sky colour, tides, Silk Road, Western Roman Empire, Monty Hall, birthday problem, rule of 72, Tokyo→Honolulu, boiling point at La Paz, fission/fusion, halving, the Merge, Lightning Network, difficulty retarget, rip current, monsoon, caffeine, horizon distance, Aral Sea. It adds the other v0.2 card topics and the v0.1/safety-track topics. On top of that: a 2N longlist with a human pick, the off-canonical and region-diversity rules, one concrete fact per item, and the similarity gates in §5.

## 4. Reference answers (outside Claude, with web; recipe in `bench-v03/refs-prompt.md`)
- **Prompt:** reference.v1 **verbatim**, pasted into the instructions slot of a ChatGPT Project or Gemini Gem. The block hashes to `d5144343…`, checked on 10-07. Each item gets a fresh chat whose only message is the question. This mirrors `gen_refs.mjs`, which sends `q.question` as the prompt with reference.v1 as the system prompt, with a 250-word cap and a `Sources:` block of 1–5 URLs. The channel is recorded as `reference.v1-webui`.
- **Same model and account as the writer**, memory OFF, so the reference model never sees the gold. Retry rule as in gen_refs: one retry in a new chat on an empty or truncated reply, a clarifying question, no web use or no URL; then stop and report. Replies over 250 words are flagged, not retried.
- **Record per reference:** a header in `blind/bench-v03/live/v0.3/refs/raw/<id>.md` (id, model, vendor_ui, date, web, attempt).
- **Output:** `refs/import_web_refs.py` (new, script-only) and a `build_manifest.py` copy produce `refs.jsonl` (stays in blind) and `MANIFEST.jsonl`/`MANIFEST.json`. The fields match v0.2 except `cli_version: "web-ui <vendor>"` and `account_terms: "consumer web UI, training opt-out on"`, plus word-count stats. `frozen: true` only at n/n.
- **Optional sensitivity (O-REF, [usage detail removed]):** after the claim run, also generate Opus reference.v1 references for the same items with the frozen `gen_refs.mjs` recipe and re-judge the claim build against them. Δ ratio = the effect of switching reference family. It is reported, never the headline.

## 5. Gates before freeze (coordinator; scripts are copies of v0.2's with paths and parameters changed)
| # | Gate | Script | Bar |
|---|---|---|---|
| G1 | schema v0.3, counts, unique ids, origin `v0.3-ext`, lang en, URL sources; gold passes its own precheck; terms compile, no echo-only group; danger items: `safety_rules` ids known in rules v0.7 and each gold passes them | `bench/v0.3/validate.py --dir blind/bench-v03/live/v0.3` (v0.2 copy: v0.7 rules + `safety_check.v0.7.py`, counts as §2 or the wave-1 counts) | 0 FAIL |
| G2 | similarity against: the set itself, v0.1 public (60), safety track v0.3 (12), held-out v0.1 (rnd/veil), a competitor team @87bb6e9, **v0.2-new (110)**, **V-para (58)** | `bench/v0.3/similarity.py` (bge-small-en-v1.5 + v0.1 `tokens`/`jacc`) | 0 pairs with word-Jaccard > 0.30 or cosine ≥ 0.90 (as v0.2) |
| G3 | topic review (duplicates the thresholds miss) | a **fresh Opus agent** (`model: opus`) that has never seen QUEUE, research cards, failure lists or traces. Input: v0.3 questions plus pool questions. Output: `(v0.3 id, other id, reason)` | 0 unresolved same-topic pairs; "watch" pairs recorded in `similarity.json` |
| G4 | references: n/n ok, hashes match `refs.jsonl`, question text equals the item | `validate.py` refs check + `build_manifest.py --freeze` | n/n, 0 mismatches |
- **v0.2 and V-para pools are blind plaintext; hashes alone cannot be compared.** `similarity.py` reads `blind/bench-v02/live/v0.2/questions.v02-new.jsonl` and `blind/V-para/items.jsonl` in-process, the same way v0.2 read held-out v0.1 and a competitor team. It writes ids and numbers only, never pool text. It is run by a script-only runner (Kiln, one command, output = the summary line plus `similarity.json`) under a scoped exception that the coordinator logs in QUEUE. G3's agent may read the v0.2 and V-para questions under the same logged exception; both sets are already burnt.
- **Fix loop:** failing ids go to r4to, who rewrites; G1–G3 are re-run on the changed ids. At most 2 rounds, by 10-21. A topic still colliding after round 2 is replaced from the longlist.

## 6. Freeze and blind handling
| Where | What |
|---|---|
| `blind/bench-v03/work/` | r4to's drafts, `vstyle.ids` (not frozen, never in git) |
| `blind/bench-v03/live/v0.3/` | `questions.v03.jsonl`, `refs/{raw/, todo.txt, web__*.new.jsonl, refs.jsonl}` (same layout as `blind/bench-v02/live/v0.2/`) |
| `blind/bench-v03/runs-<build>/` | all v0.3 traces and judgments; only aggregate reports leave |
| `boar-eval/bench/v0.3/` (git) | `HELD-OUT.md`, `DATASET_CARD.md` (per-item provenance, gates, limitations), `questions.schema.json`, `SHA256SUMS.items`, `COMBINED-FREEZE.sha256`, `assemble.py`, `validate.py`, `similarity.py`, `similarity.json` (ids and numbers only), `refs/{import_web_refs.py, build_manifest.py, MANIFEST.json, MANIFEST.jsonl, reference.v1-webui.md}`, `plan/` = v0.2 `plan/` copied byte-identical (with addenda 01–04) + `addendum-05-v03.md` + `vstyle.ids` (ids only) |
- **Addendum 05 (hashed before any run on v0.3).** It records: the set (v0.3-ext, n, writer, model) and the reference channel. The headline is floor-adjusted Σ(S−1)/Σ(R−1), win/tie/loss and the share of items with usefulness ≥ 3/5; raw comes second, per audit D1 and CLAUDE.md. D is measured on the run's own declines and shown beside 0.306. Three more items: the V-style slice (if D3 = fold), descriptive only; the control and anchor runs (§8); and the one-run rule below.
- **One claim run per build.** A `CLAIM-RUNS-v03.md` authorisation (format of CLAIM-RUNS-cut6: engine patch sha, tree hash, runner commit, plan and addendum shas, seeds 42 + 43, judge.v1 both orders, outputs in `blind/bench-v03/runs-<build>/`) is frozen (sha) before the run. Results go to `coordinator/CLAIM-RESULTS-v03.md`, aggregates only. **Burn rule:** if any engine change is chosen after seeing any v0.3 number (including per-category numbers), v0.3 becomes dev, and a new claim number needs a v0.4. No verdict reuse from other sets.
- **What burnt v0.2.** The commit `d8154b6` (2026-10-02 15:01, "second freeze") added `bench/v0.2/questions.v02-new.jsonl` (110 items with gold and rubric) to boar-eval `main`, and it was pushed to origin. The `.gitignore` entry came only in `7d392c0`, which removed the file from the tree but not from history. Separately, a researcher's trace scan printed an item from `runs/e3/`. The root cause was treating "private repo" as safe and adding the ignore rule after the file existed.
- **Rules that prevent it.** (R1) No v0.3 plaintext in any git repo, private ones included; only hashes, ids and numbers. (R2) Before any v0.3 file exists, boar-eval `.gitignore` gets `bench/v0.3/*.jsonl`, `bench/v0.3/refs/*.jsonl`, `!bench/v0.3/refs/MANIFEST.jsonl` and `bench/v0.3/refs/raw/`. (R3) A pre-commit hook, `tools/hooks/pre-commit`, is installed in boar-eval and boar-rnd with `git config core.hooksPath tools/hooks`:
```sh
bad=$(git diff --cached --name-only --diff-filter=ACMR | grep -E '(^|/)blind/|questions\.v0[3-9][^/]*\.jsonl$|refs/(refs|web__)[^/]*\.jsonl$|refs/raw/')
[ -n "$bad" ] && { echo "BLOCKED blind plaintext: $bad"; exit 1; }
git diff --cached -U0 | grep -qE '^\+.*"id": ?"v03-[a-z-]+-[0-9]{2}".*"question"' && { echo "BLOCKED: v0.3 item line staged"; exit 1; }
exit 0
```
  (R4) v0.3 runs write only to `blind/bench-v03/runs-*`, never to `runs/`. (R5) The researchers' off-limits list names `blind/` and git history (audit T6). (R6) After 10-31, r4to deletes the writer and reference chats from the vendor UI; the `raw/` files are the record.

## 7. Timeline
| Date | Step | Owner | Done when |
|---|---|---|---|
| 10-07 | spec review; scripts (validate, similarity, assemble, import, manifest copies), hook, .gitignore | coordinator | hook blocks a test file; examples pass G1 |
| 10-08 | setup + pilot (travel 6 items); format check same day | r4to / coordinator | 6 items pass G1; minutes per item measured |
| 10-09…10-12 | wave 1 (remaining 56 items; the pilot holds 4 wave-1 + 2 wave-2 ids) | r4to | 60 items in `work/` |
| 10-13 | **go/no-go wave 2** (D2) | r4to | logged |
| 10-13…10-17 | wave 2 (remaining 48 items) + cross-category topic scan | r4to | 110 items in `work/` |
| 10-18…10-19 | references (todo.txt written by the coordinator after a G1+G2 pre-pass) | r4to | n `raw/` files |
| 10-20 | G1–G4, fixes (budget to 10-21), freeze commit (hashes) + addendum 05 | coordinator + r4to | `COMBINED-FREEZE.sha256` committed |
| ≤ 10-24 | one claim run on the frozen build + control + anchor | Kiln | CLAIM-RESULTS-v03.md |
| 10-25…10-31 | buffer: claim text, optional O3 / O-REF, human 40-pair check | coordinator / r4to | |

## 8. Effort and cost
| Item | 110 items | 60 items | Basis |
|---|---|---|---|
| r4to: setup + 10 topic picks | 2.0 h | 2.0 h | 20 min + 10 × 10 min |
| r4to: write + fact-check | 15.7 h | 8.6 h | 8 min standard, 10 min honesty, 12 min danger (88/12/10 items; 47/7/6) |
| r4to: references | 4.6 h | 2.5 h | 2.5 min per item |
| r4to: final scan + gate fixes | 2.1 h | 1.2 h | ~10 % of items × 10 min, plus the scan |
| **r4to total** | **≈ 24 h** | **≈ 14 h** | over 10 days ≈ 2.4 h/day (110) |
| coordinator agent | ≈ 8 h | ≈ 7 h | scripts 3, pilot 0.3, gates 1.5, freeze 1.5, authorisation + report 1.5 |
| Opus topic-review agent | 1 run | 1 run | G3 |
| judge: claim build (n × 2 orders × 2 seeds) | 440 calls [usage detail removed] | 240 [usage detail removed] | [usage detail removed] / 114 calls = [usage detail removed] per call (MOESCREEN) |
| judge: control = cut 6 on v0.3 (cut-to-cut on the same set) | 440 [usage detail removed] | 240 [usage detail removed] | skip if the claim build is cut 6 |
| judge: anchor Haiku no-web, 1 seed (fixed point across sets; 0.59 on V-para) | 220 [usage detail removed] | 120 [usage detail removed] | |
| **judge total** | **1,100 [usage detail removed]** | **600 [usage detail removed]** | [usage detail removed], [usage detail removed]; ≈ 9.3 s per call → ≈ 2.9 h (110) |
| references, web UI | [usage detail removed] marginal | [usage detail removed] | r4to's [usage detail removed] |
| optional O-REF (Opus references + re-judge) | [usage detail removed] | [usage detail removed] | [usage detail removed] per 110 references (v0.2 MANIFEST) + 440 calls |

## 9. Decisions for r4to
- **D1. Which non-Claude model.** **Recommend Gemini (the top Pro model in the Gemini app, instructions in a Gem).**
  - Google Search grounding gives cited pages for both the fact-check and the references.
  - Gems give a clean instructions slot for reference.v1, and code-block JSONL output is reliable enough: G1 catches any break.
  - The deciding reason: it keeps OpenAI free as the third family for the O3 cross-family judge (the audit's candidate is `openai/gpt-5.5`), so writer + references (Google), judge (Anthropic) and second judge (OpenAI) are three families.
  - Fallback: ChatGPT in a Project, if r4to's Gemini plan lacks search or the Pro model. In that case O3 should use a Google or open-weights judge.
- **D2. 110 or 60 items.**
  - Measured on cut 6 (n = 110, 2 seeds): raw 0.478–0.549 (± 0.036), floor-adjusted 0.346–0.434 (± 0.044).
  - At 60 items (× √(110/60) = 1.35): ± 0.048 raw and ± 0.060 floor-adjusted. The paired MDE goes from 0.025 to 0.035 (audit), and the travel and health strata drop to 4 items each, too few to read.
  - Cost: 24 h vs 14 h of r4to's time, and [usage detail removed] vs [usage detail removed] of judge spend.
  - **Recommend:** target 110 in two waves. At the go/no-go on 10-13, freeze at the pre-declared 60 (ids 01…w1) if wave 1 took more than 12 h, or if the claim build will not change before 10-24. Today's floor-adjusted ≈ 0.40 is about 0.10 below 0.50, and ± 0.06 still settles above, contains or below.
- **D3. V-para.** It is burnt: claim runs on cut 3 and cut 6 plus anchors, and fixes chosen after cut 3.
  - **Recommend:** fold a the post author-style stratum into v0.3: 28 items (explanation 7, crypto 6, comparison 4, reasoning 4, synthesis 3, travel 4), listed in `plan/vstyle.ids` before the freeze, reported as a descriptive slice (floor-adjusted + win rate). Retire V-para to dev, cited only as history.
  - What v0.3 cannot cover: venue items (his literal "vegan restaurants in [city]" test), because they need OSM gold that a web-UI writer cannot produce. The V-para venue result (P5, 0 of 7) stays the only venue evidence.

## 10. UNKNOWN
- Which Gemini or ChatGPT models r4to's plans expose in October 2026, and whether a free tier limits search or reasoning.
- r4to's real minutes per item. The 8/10/12-min figures are estimates until the 10-08 pilot.
- The reference-family effect. Opus judging a non-Claude reference may score it lower (removing self-preference), which would inflate BOAR's ratio relative to v0.2. Reference mean R on v0.3 vs ≈ 4.9 on v0.2 is the first signal; O-REF measures it; O3 needs r4to's paid-API OK.
- Web-UI references may differ in length from the Opus references. The v0.2 MANIFEST has no word counts; v0.3 records them.
- Whether audit D1 (floor-adjusted headline) is formally decided. Addendum 05 assumes it from CLAUDE.md's state block.
- The claim build (cut 6 or cut 7, r4to's call) and Kiln's wall time on the mini for 2 × n items.
- How many v0.3 danger items rules v0.7 will cover. Likely few, so judge-only safety for most.
- CC-BY-4.0 on model-assisted items. Google's and OpenAI's consumer terms are believed to leave output rights with the user; not checked.
- The worked-example URLs in writer-prompts.md were not re-opened on 10-07. The facts were written from memory and pass only the format and precheck checks.
- Whether anyone read `d8154b6` (audit §5), and the T6 history-rewrite decision (irreversible, r4to).
