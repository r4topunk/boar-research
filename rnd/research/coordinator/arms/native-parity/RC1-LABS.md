# RC1-LABS-BASELINE (2026-10-23): the RC1 baseline with the app maintainer's default-on Labs tools

TL;DR: **With Labs on (his rc1 release default), his facts tool answers 8 of 51 dev questions, all right, and nothing else fires. New RC1 baseline (Haiku): raw 0.366 / U 0.196, up from 0.312 / 0.129 without Labs; paired U +0.067 (+0.025…+0.117), raw +0.054 (+0.020…+0.094), 8 better / 0 worse.** The 8 are exactly the B1-SPLICE ids, and 7 of the 8 texts are byte-identical to our engine's layer answers (his table is our r10 build), so the B1 Opus projection (U 0.143 → 0.248, +0.106) now describes his shipped app rather than a counterfactual. One seed, Haiku, dev ids, desktop harness.

## Criterion
RC1-LABS-criterion.md, sha256 2708edc75f71e359984c1a59e5c78f10eca2805ebcc7ecfcfda91da9ae99b083, frozen (read-only) before any tool run, generation or judge call.

## What each default-on lab does (tag v2.0.0-rc1, commit 46be7377; all wrap engine/routing/LabTools)
| lab (order, slot rank) | answerTool | what it answers | harness |
|---|---|---|---|
| cohazard (69, rank 0) | Instant | planning questions about a fuel-burning device in an enclosed space → fixed CO safety answer (CDC/CPSC/NHS); EN, plus PT/ES drafts | compiled as is |
| polyglot (64, rank 1) | Instant | a full question in a language other than EN/PT/ES → "Sorry, BOAR doesn't speak X yet. Ask in English." (LanguageGate) | **stub**: Android TextClassifier detector = null (only non-Latin scripts are caught, as on a device without the detector); UI language English |
| calc (65) | Instant | arithmetic in the question (CalcShortcut/Arithmetic, our PR #85 port), NumGuard health lexicon keeps it off health | compiled as is |
| distance (66) | Instant | city-to-city trip distance (GeoNames table, sha 5517b2e7…) × route factor; EN only, not health | compiled as is |
| facts (67) | Instant | one property of a place/landmark/event/award in the Wikidata table (population, area, height, dates, host, winner, plugs/voltage), or a computed verdict for two; EN only, not health/seed | compiled as is; table lab_facts_facts_v1.json **build r10**, snapshot 2026-10-06, 4,233 entities, sha256 307753ff… |
| pulse (10) | none | a device-stats screen (CPU/RAM/thermal); LabPlugin.answerTool default null | not needed |
Slot order (LabHooks: LabRegistry.active sorted by slotRank): cohazard > polyglot > calc > distance > facts. Guard (the check slot) is off by default and not run. All five tools return ToolResult.Instant only, so a non-firing item's prompt is unchanged (AnswerTools.systemPrompt(base, null) == base).

## Commands
- `bash tools/run_labs.sh` (MacBook, 0 LLM, ~1 min): git archive of the tag's engine/src/main/java + the two raw tables into work/labs/tag, builds tools/harness-labs (Rc1Labs.kt, the five wrappers re-written 1:1), writes runs/rc1-labs-tools.jsonl (per item: winning lab, receipt, text, per-lab results). No lab threw.
- Determinism check: snapshot harness (tools/harness, 5f8cc8f4) rebuilt the N-D prompt for vit-hum-001/002/003 → **3/3 byte-identical** to work/s3-prompts.jsonl. Regenerated on the MacBook llama-server b11010 (1.5B Q4_K_M sha 1adf0b11, -t 2 -np 1, tools/s3_gen.py seed 42): texts differ from the mini's after 8-165 characters (CPU/kernel nondeterminism across machines, not pipeline; VITAL-ONOFF already showed mini-on-mini byte identity). Non-fired items therefore inherit the mini N-D answers and rows.
- Judge: `bash tools/labs_judge.sh` → traces/native-N-DL-v01-s42.traces.jsonl (gitignored), runs/labs-changed.ids (8), preflight OK, Haiku 5.5-low judge.v1-low N 4 both orders → judgments/native-N-DL-v01-s42.judgments.jsonl (16 rows ok). **Haiku calls 16 (cap 204), Opus 0, paid 0.**
- Aggregate: `python3 -I tools/labs_agg.py` → aggregates/rc1-labs.json.

## Tool items (all facts; correctness = Haiku mean of both orders; hand read vs bench v0.1 reference)
| id | receipt | N-D corr → N-DL corr | s N-D → N-DL | right (Haiku / hand) | text = our layer |
|---|---|---|---|---|---|
| lan-cmp-001 | facts-population | 1.0 → 4.0 | 1.33 → 3.17 | yes / yes (Brazil 214.2 M vs Russia 146.1 M) | yes |
| lan-rsn-002 | facts-depth | 1.0 → 5.0 | 1.33 → 3.67 | yes / yes (814 m below) | yes |
| lan-ref-001 | facts-winner | 1.0 → 4.0 | 1.00 → 2.83 | yes / yes (Ishiguro) | yes |
| lan-ref-004 | facts-area | 2.0 → 4.5 | 2.00 → 3.50 | yes / yes (103,004 km²) | yes |
| lan-exp-006 | facts-height | 2.0 → 4.0 | 2.00 → 2.67 | yes / yes (5,895 m, dormant volcano; terse on "what is it") | yes |
| lan-rsn-007 | facts-dates | 2.0 → 4.5 | 2.50 → 3.33 | yes / yes (1961 / 1989) | yes |
| lan-ref-005 | facts-host | 2.0 → 5.0 | 2.00 → 3.33 | yes / yes (Rio) | yes |
| trv-002 | facts-electricity | 1.0 → 4.0 | 1.00 → 3.33 | yes / yes (C + N, 127/220 V, 60 Hz) | no: his r10 text adds "60 Hz" |
calc, distance, cohazard and polyglot fired on 0/51 (the CV5 set has no arithmetic, trip-distance, CO or foreign-language item).

## N-D vs N-DL (51 CV5 ids; Haiku 5.5-low judge.v1-low; one seed)
| | N-D (RC1 measured, Labs off) | N-DL (RC1 as shipped, Labs on) |
|---|---|---|
| items answered by a tool | 0 | 8 (facts 8) |
| raw (CI) | 0.312 (0.288–0.339) | 0.366 (0.321–0.415) |
| U floor-adj (CI) | 0.129 (0.098–0.163) | **0.196 (0.141–0.256)** |
| win/tie/loss vs reference | 0/0/51 | 1/0/50 |
| confident errors per 100 (LITEPACKS rule) | 66.7 (34) | 58.8 (30) |
- Paired N-DL − N-D, all 51: **U +0.067 (+0.025…+0.117)**, raw +0.054 (+0.020…+0.094), better/worse 8/0. On the 8 changed items only: U +0.451 (+0.317…+0.578).
- CE: 4 items leave CE (lan-cmp-001, lan-rsn-002, lan-ref-001, trv-002), none enters. Health items: 0 worse (no tool touched them).

## B1-SPLICE comparison (arms/rc1-pixel/LAYER-SPLICE.md)
- His facts tool answers **8/8** of the B1 ids, **8/8 right**, and **7/8 texts byte-identical** to our cut-7 layer answers (trv-002 differs only by the r10 "60 Hz" addition). B1 was a projection with Opus (U 0.143 → 0.248, +0.106); this is the measured version with Haiku (+0.067). The gap is the judge (Haiku compresses gaps), not the routing: same ids, same texts.
- Consequence: the "port our deterministic layers" ask for the facts table is already shipped in rc1 (Labs on by default); our RC1 numbers measured through the eval hook without request.labs understated his app by the whole B1 effect.

## Predictions vs outcome
- Tool fires on 6-10 of 51: **hit** (8).
- U rises by +0.03 to +0.10: **hit** (+0.067).
- 0 health items worse: **hit** (0).

## New baseline sentence (NOTE-1 input)
"Measured with your Labs defaults on (as a user gets rc1), your app scores U 0.196 (raw 0.366, Haiku, 51 dev questions) instead of the 0.129 we reported with Labs off: Boar Facts answers 8 of the 51, all correctly, with the same text as our engine's facts layer on 7 of them. With the Opus judge that is the B1 figure, about 0.25 instead of 0.14. The verdict guard is off by default, so it played no part."

## UX page row "tabela de fatos"
| feature | status in rc1 | measured |
|---|---|---|
| tabela de fatos (Boar Facts, r10 table, Wikidata CC0) | shipped, Labs on by default, Instant answer (no model) | answers 8/51 dev questions, 8/8 right; U +0.067 Haiku (Opus projection +0.106); 4 fewer confident errors |

## Caveats
- Desktop harness: the tool decisions are the tag's engine code compiled on the JVM; the five lab wrappers are re-written (they only load res/raw and draw UI). Pipeline rows are step 3's (snapshot 5f8cc8f4, parity-checked against the RC1 Pixel); the tag's engine also changed RagPure/Retriever/AnswerPipeline, which this arm does not re-measure.
- Stub: polyglot's Android language detector is null (only other alphabets get the reply); irrelevant here (all 51 questions are English) but it would under-fire on Latin-script foreign questions. Pulse has no tool.
- One seed (non-fired items carry the step-3 mini generation), Haiku 5.5-low (compresses gaps), dev ids (CV5 51 of v0.1), n 8 changed. Empty history (eval rows pass emptyList()), so follow-up behaviour is not covered.
