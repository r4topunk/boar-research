# RC1-LABS-BASELINE criterion (frozen 2026-10-23 before any tool run, generation or judge call of this arm; never edited afterwards)

## Question
Our RC1 baseline (N-D: 1.5B Detailed, KB-only, 51 CV5 dev ids; Haiku raw 0.312 / floor-adj U 0.129; Opus U 0.14 on the phone run)
was measured through the eval hook WITHOUT the app maintainer's Labs tools. The v2.0.0-rc1 release (tag commit 46be7377) ships Labs on
with calc, cohazard, distance, facts, polyglot and pulse onByDefault = true (guard OFF). What is the RC1 baseline with those tools on?

## Arms (51 CV5 v0.1 dev ids = cv5-51.ids)
- N-D (existing, NATIVE-PARITY step 3): runs/s3-gen.jsonl arm N-D, Haiku rows judgments/native-N-D-v01-s42.judgments.jsonl. Not regenerated.
- N-DL (new): N-D + the tool slot exactly as DeviceEvalRunner.answerRow at the tag: AnswerTools.run(query, emptyList()) over the
  default-on labs' answerTools in LabHooks order = LabRegistry.active (plugin.properties order, then id) stable-sorted by
  LabTools.slotRank: cohazard (0), polyglot (1), then calc (65), distance (66), facts (67); pulse (order 10) has no answerTool
  (LabPlugin default null). First non-null result wins; a throwing tool is skipped (LabTools.first).
  - ToolResult.Instant => the tool text IS the answer (no generation, no check slot; guard is off anyway).
  - No tool (null) => AnswerTools.systemPrompt(base, null) == base, so the pipeline prompt is the N-D prompt: the item inherits the
    N-D answer and its N-D Haiku rows. All five tools return Instant only (code read); a Context result, if any appears, makes the
    item "changed" and it is generated as N-D with the context appended (MacBook llama-server b11010 CPU, 1.5B Q4_K_M sha 1adf0b11,
    tools/s3_gen.py, seed 42) and judged.
- Tool code: compiled from the tag's engine/src/main/java (LabTools, CalcShortcut, Arithmetic, NumGuard, TravelDistance, Facts,
  CoHazard, LanguageGate, QueryContext ...) in a separate desktop harness (tools/harness-labs, never the 5f8cc8f4 snapshot). Data:
  facts table res/raw/lab_facts_facts_v1.json (build r10, sha256 307753ff...), city table res/raw/lab_distance_world_cities_v1.json.
  Lab wrappers re-written 1:1 in the harness (they only add Android resource loading/Compose UI). Stubs, stated in the report:
  polyglot's PhoneLanguageDetector (Android TextClassifier) returns null (as on a device with no detector / main thread) and the
  UI language is English; pulse has no tool so needs none.
- Determinism check: 3 non-fired items regenerated on the MacBook from the harness N-D prompt; prompt identity vs work/s3-prompts.jsonl
  is the pass condition; answer-text identity is reported (mini vs MacBook CPU may differ; that is hardware, not pipeline).

## Judge (changed items only)
Haiku 5.5-low judge.v1-low, N 4 shards, both orders (deepthink/tools/shard_judge.sh), bench boar-eval/bench/v0.1, system
native-parity-N-DL-v01-haiku55-low. Unchanged items inherit N-D rows. Calls = 2 x changed (cap 204). No Opus, no paid API.

## Metrics (estimator = arms/device-x6/tools/agg_device.py as vo_agg.py; 51 ids, paired item bootstrap B 2000 seed 11)
- PRIMARY: paired U (floor-adj, above_min) delta N-DL - N-D with 95 % CI; raw delta alongside.
- Items answered by a tool (count, which tool, receipt code), and per tool item whether right (Haiku correctness mean of orders >= 4 =
  right, <= 1.5 = confident error; also a hand read against the bench reference, reported separately).
- Confident errors per 100 (LITEPACKS rule as in VITAL-ONOFF: non-declined answer with correctness mean <= 1.5; tool answers count as
  non-declined). Health items = lan-hlt / vit-hlt ids.
- B1-SPLICE comparison (arms/rc1-pixel/LAYER-SPLICE.md, +0.106 Opus projection from our 8 facts answers): of the 8 ids lan-cmp-001,
  lan-exp-006, lan-ref-001, lan-ref-004, lan-ref-005, lan-rsn-002, lan-rsn-007, trv-002, how many his facts tool answers, with which
  template, whether right, and whether its text equals our layer text.

## Pre-registered predictions (from the task brief)
- A tool fires on 6-10 of 51.
- U rises by +0.03 to +0.10.
- 0 health items worse (no health item with lower s in N-DL than N-D).

## Reading (descriptive; nothing adopted)
The new RC1 baseline = the N-DL row. Report hit/miss for each prediction. Validity: every changed id judged in both orders, else INVALID.
One seed (non-fired items carry the step-3 generation), Haiku (compresses gaps), dev ids, desktop harness: stated next to every number.

## Budget
calls_cap: Haiku 204 / Opus 0
