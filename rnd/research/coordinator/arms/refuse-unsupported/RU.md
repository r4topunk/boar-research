# RU (REFUSE-UNSUPPORTED): GATE17 groundedness gate as a default-mode refusal trigger on the 1.7B K3 line

TL;DR: **PASS by the frozen rule at t = 0.919** (criterion sha256 `af16f29c9c5e3fa32cdd7d87eae8cf8acd6f02988339ae855f52ea4463d4f0df`,
committed 554d88ab before any gate run or label). The t = 0.5 row also passes.
- CE-unwarned (confident errors a user sees in default mode) falls from 10 to 4 of 177 items (-60 %, paired CI of the rate difference -0.062 to -0.011).
- 0 of 15 supported-correct answers are refused (Wilson 95 % CI 0 to 20 %).
- U on the answered items rises 0.526 to 0.556 (+0.030, CI +0.005 to +0.057).

**The price:**
- Coverage falls from 0.435 to 0.328: the gate refuses 19 of 56 gated answers.
- 5 of those refusals are judge-correct memory answers that the chunks do not support. They are not "false refusals" under the frozen definition, but the user loses them: correct answers shown go from 37 to 32.
- Latency: a second prefill of about 790 tokens. That is about 5.1 s on the mini and a projected **about 9.3 s (p50) / 12.2 s (p90) on a Pixel 8a**, roughly doubling the measured 9.4 s TTFT.

**Small counts:** the decision rests on 10 vs 4 CE-unwarned items and 15 supported-correct answers. One seed, single Haiku-low judge, single-family labeller.

## Setup (as frozen)
- **Answers.** The LITEPACKS K3 MacBook traces and their existing Haiku 5.5-low judge.v1-low judgments. No answer was generated or re-judged for scoring.
- **Contexts.** The mini regenerated the K3 system with `--dump-prompts` (tools/gen_dump.sh, 177 items, about 12 min, slot gen1).
  - Retrieval.kept matches on 177/177 and answer prompt tokens match on 177/177, so the dumped Context blocks are the ones the MacBook 1.7B saw.
  - **Mismatch (as asked):** the mini answer text is byte-identical to the LITEPACKS K3 answer on only 55/177 items. This is the known M4 vs M1 sampling divergence at temperature 0.7 (LP-SCREENS parity). The mini texts were therefore not used.
  - 0 kept-list mismatches, so the 10 % VOID clause does not apply.
- **Default mode (both arms).** These are refused: warned answers (the engine's "not found in the library" line), LLM answers with no kept source, and engine declines.
  - These are shown: deterministic layers (Wikidata facts, calculator, first-aid cards; 21 shown) and unwarned LLM answers with kept chunks (56, all gated).
- **System R.** R refuses a gated answer when the gate's P(FAIL) >= t.
- **Gate run.** The gate ran on all 124 source-present answers (56 unwarned + 68 warned) using the GATE17 build: Q4_K_M + f16 LoRA on the mini, n_probs 50. Both tokens were in the top 50 on every call.
- **Support labels.** GATE17S label.mjs, unchanged, on all 124 answers: A/B agreement 119/124, 5 tie-breaks. Result: 37 SUPPORTED (22 unwarned, 15 warned), 87 UNSUPPORTED.

## Results (pooled 177 decides; bootstrap B 2000 seed 11)

| | t = 0.919 (decides) | t = 0.5 (secondary) |
|---|---|---|
| (a) CE-unwarned C -> R (rate) | 10 (0.056) -> 4 (0.023), -60 %, diff CI -0.062...-0.011 | 10 -> 3 (0.017), -70 %, CI -0.073...-0.011 |
| (b) false refusals (supported, corr >= 4) | 0/15 = 0 % (Wilson 0-20 %) | 0/15 (0-20 %) |
| (c) U on answered C -> R | 0.526 -> 0.556 (+0.030, CI +0.005...+0.057) | 0.526 -> 0.563 (+0.037, CI +0.012...+0.069) |
| (d) coverage C -> R | 0.435 -> 0.328 | 0.435 -> 0.311 |
| refused by the gate (of 56) | 19: 6 CE, 5 corr >= 4 (all UNSUPPORTED), 8 in between | 22: 7 CE, 5 corr >= 4 |
| verdict | **PASS** | PASS |

Per set at t = 0.919:

| set | CE-unwarned C -> R | false refusals | U on answered C -> R | coverage C -> R |
|---|---|---|---|---|
| MAIN 97 | 5 -> 2 (CI -0.072...0.0) | 0/5 | 0.518 -> 0.563 (+0.045, CI +0.012...+0.088) | 0.392 -> 0.309 |
| CAND 80 | 5 -> 2 (CI -0.088...0.0) | 0/10 | 0.534 -> 0.547 (+0.013, CI -0.020...+0.049) | 0.487 -> 0.350 |

Neither subset reaches CI high < 0 on its own; only the pooled set does.

**Gate vs support, out of sample on K3 (not in the rule):**
- AUC is 0.934 on all 124 answers and 0.898 on the 56 unwarned ones (GATE17S, on K0/K1: 0.965).
- Only one supported answer scores >= 0.919: st-boar-simplewiki-en-005, which is warned and refused in both arms anyway.
- Among judge-correct gated answers, 18 are supported and 10 are unsupported (memory-correct). The gate refuses every unwarned memory-correct one.

## Examples
**Caught confident errors** (shown by C, refused by R):
- vit-sci-002 (P 0.991, corr 1.0): "Japan is less densely populated than Germany..."
- lan-cmp-003 (P 0.998, corr 1.0): "countries larger than India ... Papua New Guinea, Indonesia, and Thailand", cited [5].
- st-boar-factbook-017 (P 0.998, corr 1.0): Pakistan mother tongues "Urdu (54%)... Afghani".
- vit-hum-004 (P 0.947, corr 1.5): "Gríma kills Saruman in Isegard...".
- st-boar-factbook-004 (P 0.996): the Bhutan capital legend.
- st-boar-factbook-009 (P 0.995): Bahrain's economy.

**CE-unwarned still shown by R (4):**
- vit-cry-007 "d/acc is a digital-to-analog converter [1]" (P 0.005; Haiku UNSUPPORTED, so the gate misses it).
- st-qa-money-se-001 (P 0.501, just under 0.919; caught at 0.5).
- st-boar-factbook-011 Western Sahara "controlled by the SADR" (P 0.047).
- st-boar-factbook-018: a Wikidata facts-table answer (deterministic layer, never gated).

**False refusals (supported and correct, refused):** none at either threshold.

**Correct but unsupported, refused (the real cost; 5, all CAND):**
- st-boar-factbook-007 Paraguay (corr 4.5, P 0.996)
- factbook-008 Mauritius (4.0)
- factbook-013 Trinidad and Tobago (4.0, P 0.999)
- medlineplus-en-018 PSA test (4.0)
- medlineplus-en-020 vaccines (4.5)

The answers cite chunks, but Haiku judges that at least one key claim is not in them.

**Supported but wrong, passed:** vit-cry-006, quadratic funding (supported, corr 2.0, P 0.002). This is the same misread GATE17 found. No supported answer is a CE (corr <= 1.5) here.

**Warned answers the gate would pass** (supported, corr >= 4, P < 0.919): lan-exp-004 Kyoto, st-boar-medlineplus-en-002 endocarditis, -008 high blood sugar. Three answers are a candidate "un-warn when the gate passes" variant; this was not measured.

## Latency (mini M4 CPU -t 4, LoRA without CPU_REPACK, cache_prompt off)

| | n | gate prompt tokens p50 / p90 / max | answer prompt tokens p50 | mini prefill p50 / p90 | mini wall p50 / p90 | Pixel 8a projected prefill p50 / p90 (85 tok/s) |
|---|---|---|---|---|---|---|
| unwarned gated (the product path) | 56 | 788 / 1,040 / 1,248 | 887 | 5.10 s / 7.40 s | 5.36 s / 7.41 s | **9.3 s / 12.2 s** |
| all gated | 124 | 786 / 993 / 1,283 | 876 | 5.10 s / 6.88 s | 5.27 s / 7.14 s | 9.3 s / 11.7 s |

- Mini prefill rate: 150 tok/s.
- The projection assumes the LoRA costs nothing extra on the phone and that there is no prefix reuse. The gate prompt starts with the rubric, so it shares no prefix with the answer prompt.
- The gate's decode is 1 token.
- **Possible mitigation (unmeasured):** reorder the gate prompt so it starts with the answer prompt's context and the KV cache can be reused. This changes the card prompt and would need a new smoke.

## Budget and deviations
- Haiku calls: 253 support labels (cap 500); 0 judge calls; 0 Opus; 0 paid.
- Mini work: 1 generation job (177 items) and 1 gate pass (124 calls, 21:57-22:08), each with its own server, stopped after.
- **Deviation (stated in the criterion):** the mini answers differ from the LITEPACKS K3 answers on 122/177 items. The brief's "must match" is unmet, so the MacBook answers were gated against the mini-dumped contexts, which match exactly (kept lists and prompt token counts 177/177).
- **Interpretation (stated in the criterion):** in control C, "no source kept" means the engine's warning line, following REREAD. Warned answers with weak kept chunks are refused in both arms.
- The 5 refused memory-correct answers fall outside clause (b) by its definition ("supported-correct"). A product read should weigh them: correct answers shown go from 37 to 32 while CE shown goes from 10 to 4.

## Files
- `RU-criterion.md` (+ `.sha256`)
- `tools/`: mkreq, gen_dump + mini_gen_dump, build_items, run_gate, analyze; gate17 mini_gate.py and gate17-support label.mjs are used unchanged
- `traces/ru-K3-dump-s42.{traces,prompts}.jsonl`
- `gate/{items.json, ru.inputs.jsonl, boar.outputs.jsonl}`
- `labels/labels.jsonl`
- `analysis.json`
- `runs/logs/`
