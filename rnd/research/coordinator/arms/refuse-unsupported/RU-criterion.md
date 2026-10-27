# RU (REFUSE-UNSUPPORTED) criterion (frozen 2026-10-20 before any gate run or support label on these items)

## Question
In the default product mode (decision 2026-10-20 evening, QUEUE l.1443: refuse by default when no source supports the answer, show-anyway on
request), does adding the GATE17 groundedness gate after the Qwen3-1.7B answer (LITEPACKS system, pack set K3, compact declines released)
cut the confident errors a user sees without refusing too many supported correct answers or lowering the quality of what is still shown?

## Systems (same answers; only the refusal decision differs)
- Answers: the LITEPACKS K3 traces (MacBook, seed 42; arms/litepacks/traces/lp-K3-{v01,cm,st}-s42) and their existing Haiku 5.5-low judge.v1-low
  judgments (K3 reuses K0 judgment rows where the text is byte-identical, as litepacks/tools/agg.py). No answer is re-judged.
- Context the 1.7B saw: regenerated on the Mac mini with `--dump-prompts` (tools/gen_dump.sh + tools/mini_gen_dump.sh, base tree
  be-0cfd4a77-cut7-litepacks, K3 requests unchanged except runId). The mini and MacBook decode differently at temperature 0.7 (LP-SCREENS
  parity: text identical on about 30 % of items) but retrieval is identical, so the context block of the mini's last generate prompt is used only
  where the mini retrieval.kept list (title, section, source) equals the MacBook one. The mini answer texts are NOT used; their identity rate with
  the LITEPACKS K3 answers is reported (the mismatch the brief asks to report). VOID if more than 10 % of the source-present LLM answers have a
  kept-list mismatch.
- **Control C (default mode, no gate):** an answer is shown iff it is not a decline (arms/reread-2026-10-20/reread.py `is_decline`: trace declined,
  engine refusal / notice strings, short model abstentions, empty body) AND it does not start with the warning line ("Not found in this phone's
  offline library. From the model's memory, may be wrong:", i.e. the engine found no supporting source) AND (it is a deterministic layer answer,
  timing.outputTokens == 0, e.g. Wikidata facts tables, calculator, first-aid cards; OR retrieval.kept is non-empty). So warned answers and LLM
  answers with no kept source are refused in both arms (product rule).
  Interpretation note: the brief's "refuse only when no source kept" is read as the engine's own no-source signal (the warning line), as in
  REREAD; warned answers have kept chunks but the engine judged them weak.
- **System R:** C, plus: every source-present answer (LLM answer, not a decline, kept non-empty, mini kept identical, Context block present) gets
  the gate; if P(FAIL) >= t, R refuses it (replaced by the engine no-source refusal text, a decline).
- Gate = GATE17 exactly: aaryand/qwen3-1.7b-context-adherence-guardrail LoRA (gate17-lora-f16.gguf d022352e) on Qwen3-1.7B-Q4_K_M (b139949c),
  llama-server b11010 CPU -t 4 -c 8192 --reasoning off on the mini (tools/run_gate.sh: slot lock gen1/gen2, own port, stopped after);
  prompt = arms/gate17/tools/build_items.py `render(question, context, response)` (card RUBRIC, Qwen3 template, thinking off), response = answer
  minus the warning line; /completion n_predict 1, temperature 0, n_probs 50 (arms/gate17/tools/mini_gate.py, unchanged);
  P(FAIL) = pF / (pP + pF). The gate runs on warned source-present answers too (diagnostic; they are refused in both arms anyway).
- **Thresholds:** t = 0.919 (GATE17S t*, primary, decides); t = 0.5 (the gate's own verdict, secondary row, does not decide).

## Items
177 = MAIN 97 (arms/lp-screens/main-97.ids: v0.1 57 judged + qa-cooking-se 20 + qa-money-se 20) + the 80 candidate-pack self-tests
(st-boar-simplewiki-en / factbook / medlineplus-en / firstaid-en, 20 each; K3 holds all four packs = pack-matched). Pooled set decides;
MAIN and CAND reported separately. Dev sets only (no bench/v0.4, blind/, rnd/veil).

## Support labels (Haiku 5.5-low; exact GATE17S procedure)
arms/gate17-support/tools/label.mjs unchanged (system + user prompt exact as GATE17S-criterion.md; call A chunks in order, call B chunks reversed and
renumbered, call C on disagreement, majority; failed call retried once). Inputs: question, the dumped Context block, the response (warning line removed).
Order: first every unwarned source-present answer (needed by the rule), then the warned ones (diagnostic) while the cap allows.
calls_cap: Haiku 500 (support labels only; 0 judge calls); Opus 0; paid APIs 0. If unwarned labelling alone would exceed the cap, stop and report.

## Metrics (tools/analyze.py, committed with this file; bootstrap = item rows, B 2000, seed 11, 2.5 / 97.5 percentiles)
Per arm over the n items of a set:
- (a) CE-unwarned rate = #(shown AND judge correctness <= 1.5) / n. Relative drop = 1 - CE_R / CE_C. Paired bootstrap CI of rate_R - rate_C.
- (b) False refusals = #(shown by C, gated, Haiku-SUPPORTED, correctness >= 4, refused by R) / #(shown by C, gated, SUPPORTED, correctness >= 4); Wilson 95 % CI.
  Deterministic-layer answers are never gated and carry no support label (not in the denominator).
- (c) U on answered items = sum s / sum s_ref over shown items (s = mean of the 3 judge dims over both orders); R - C with paired bootstrap CI.
- (d) Coverage = shown / n.
Also reported (not in the rule): gate AUC vs the support labels on this population (GATE17S out of sample), supported / unsupported x correct
cross-tabs, warned answers that are SUPPORTED and correct and pass the gate (what a gate-based un-warning would rescue), refusals by the gate split
into CE / correct; latency: gate prompt tokens per gated answer (p50/p90/max, all gated and unwarned-only), mini prompt ms and wall per gate call,
projected Pixel 8a prefill = gate prompt tokens / 85 tok/s (the phone's measured 1.7B prefill rate, arms/litelat; assumes the LoRA costs no extra
on the phone and no prefix reuse with the answer prompt, the rubric comes first).

## Decision rule (pooled 177, t = 0.919)
PASS iff ALL of
1. CE-unwarned relative drop >= 50 % AND paired CI high of (rate_R - rate_C) < 0;
2. false refusals <= 15 % (point estimate; Wilson CI reported); if fewer than 5 supported-correct answers exist the clause is unassessable and the
   verdict is INCONCLUSIVE;
3. U_R on answered items >= U_C on answered items - 0.02 (point estimate).
Otherwise FAIL. The t = 0.5 row is computed the same way and reported, never decides.

## Known limits (stated before the run)
One seed; answers from the MacBook paired with mini-dumped contexts (identical retrieval assumed from kept-list equality); single Haiku-low judge
for correctness and a single-family Haiku labeller for support; the 80 self-tests are pack-written (an upper bound for on-topic use); t = 0.919 was
chosen on GATE17S's 57 rows (K0/K1 contexts), so this run is its first out-of-sample use on K3.
