# GATE17: does a 1.7B groundedness gate flag BOAR's confident errors? (source-present answers, n 57, diagnostic)

TL;DR: **NO.** The gate `aaryand/qwen3-1.7b-context-adherence-guardrail` works as its card says (card examples reproduced 3/3), but on BOAR's
answers it does not separate confident errors (CE) from the rest: pooled AUC 0.496 (CI 0.340-0.648) for CE vs non-CE and 0.413 (0.179-0.663)
for judge-wrong vs judge-correct. At its own threshold (0.5) it FAILs 42 of 57 answers: 23/29 CE, and also 6/9 judge-correct ones.
With the false-alarm budget at 10 % (0 of 9 correct answers), it flags 3 answers, 2 of them CE (recall 0.07).
Why: BOAR's kept chunks rarely contain the answer (off-topic Wikivoyage pages, a "quadratic sieve" chunk for quadratic funding), so correct
answers are memory answers and "unsupported", the same as wrong ones. Strict grounding measures context support, which here does not track
correctness. When the context does support the answer and the answer is still wrong (vit-cry-006), the gate passes it (P(FAIL) 0.002).
No refuse-when-unsupported arm follows: on these contexts it would refuse about 3/4 of source-present answers, including most correct ones.
Cost: two prompt-dump regenerations (97 + 37 items, about 4 + 3 min) and one 57-call gate pass (3 min) on the mini. 0 judge calls, 0 Opus, 0 paid.

- Criterion: `GATE17-criterion.md`, sha256 `84cb4fa0dc59069090641885cca638a91ff31212ad479344a1323dfcc7505d3c`. Committed with the tools and the
  card smoke before the gate ran on any BOAR item (rnd 70a0e63f).
- Licence: card front matter and Hub API tag `apache-2.0` (rev daa91b0d0d7e). The card names the dataset `aaryand/context-adherence-guardrail-10k`.
  Base Qwen/Qwen3-1.7B is Apache-2.0.
- Adapter: PEFT LoRA r16/alpha 32, all linear layers (adapter_model.safetensors sha256 `8ed04f95...`). It was converted with llama.cpp b11010
  `convert_lora_to_gguf.py --outtype f16 --base <Qwen3-1.7B rev 70d244cc config + tokenizer only>`, which gave 392 tensors in
  `gate17-lora-f16.gguf` (sha256 `d022352e161774747abb1975fa0c7cdcf567a9fa30f39bd95839415917a96c09`, 34.9 MB, on the mini under <runner>/kiln/gate17/).
  The base was not merged and no base weights were downloaded.
  It runs as `llama-server -m Qwen3-1.7B-Q4_K_M.gguf (b139949c) --lora gate17-lora-f16.gguf -c 8192 -t 4 --reasoning off`, using
  `tools/run_gate.sh` (slot lock gen1/gen2, own port, server stopped after the pass, detector :8094 untouched).
- Prompt: the card's exact RUBRIC + QUESTION/CONTEXT/RESPONSE block, rendered with the Qwen3 template and thinking off (`tools/build_items.py`).
  Requests go to /completion with n_predict 1, temperature 0 and n_probs 50. P(FAIL) = pF / (pP + pF) for token ids PASS 49792 and FAIL 36973.
  Both tokens were in the top 50 on every call.
- Smoke (the card's own example + 2 variants): Nobel claim P(FAIL) 0.998 (card: FAIL 0.9...), grounded 0.002, decline 0.011.

## Items
- The mini controls lpctl-K0-main-s42 (97) and lpctl-K1-screen-s42 (37) were regenerated unchanged with `--dump-prompts` (`tools/gen_dump.sh`)
  to get the exact context the 1.7B saw. **97/97 and 37/37 answer texts are byte-identical** to the controls, so the existing Haiku 5.5-low labels
  apply unchanged. No K1 MAIN control exists, so K0 MAIN + K1 screen were used, as instructed.
- In scope: 57 rows (K0 MAIN 32, K1 screen 25, 0 duplicates dropped). They hold 29 CE, 35 judge-wrong (corr <= 2) and 9 judge-correct (corr >= 4).
  Each row had one generate. Context = the prompt's `Context:` block verbatim (max 3,816 chars). The warning line was stripped on 33 rows.
- Out of scope, no kept source: K0 MAIN 64, K1 screen 12. One kept-source item had no LLM generate, so no context prompt:
  `dng-005` (the deterministic flood-guidance layer). The full lists are in `gate/items.json` -> report.
- Inputs `gate/boar.inputs.jsonl` sha256 `d92eaf81...`; outputs `gate/boar.outputs.jsonl` `11d4f923...`; analysis `analysis.json` (`tools/analyze.py`).

## Results (bootstrap B 2000 seed 11)
| Set | n | CE | wrong / correct | AUC CE vs non-CE (CI) | AUC wrong vs correct (CI) |
|---|---|---|---|---|---|
| **Pooled (primary)** | 57 | 29 | 35 / 9 | **0.496** (0.340-0.648) | 0.413 (0.179-0.663) |
| K0 MAIN only | 32 | 12 | 17 / 7 | 0.558 (0.348-0.768) | 0.370 (0.114-0.636) |
| K1 screen only | 25 | 17 | 18 / 2 | 0.360 (0.105-0.640) | 0.472 (0.0-1.0) |
| Warned (memory answers, citations removed) | 33 | 21 | 24 / 2 | 0.381 (0.179-0.591) | 0.125 (0.0-0.269) |
| Unwarned | 24 | 8 | 11 / 7 | 0.430 (0.182-0.695) | 0.260 (0.043-0.542) |

Median P(FAIL): CE 0.983, judge-correct 0.990, other 0.965. The judge-correct answers are slightly *more* likely to be flagged.

### Flag table (pooled)
| Threshold | Flagged | CE caught | Wrong caught | False alarms (corr >= 4) |
|---|---|---|---|---|
| **t\* = 0.9989 (FA <= 10 %, i.e. 0 of 9)** | 3/57 | **2/29 (0.07)** | 2/35 | 0/9 |
| 0.5 (the gate's verdict) | 42/57 | 23/29 (0.79) | 26/35 | 6/9 (0.67) |

## Verdict (frozen rule)
**NO.** AUC 0.496 < 0.70, CI low 0.340 < 0.60, and CE recall at t\* 0.07 < 1/3. All three clauses fail.

## Latency (mini M4 CPU, -t 4, Q4_K_M + f16 LoRA, cache_prompt off)
Gate prompt tokens: p50 530, p90 859, max 1,037. Prefill: p50 2.40 s, p90 5.22 s per call (195 tok/s; the LoRA cannot use the CPU_REPACK
buffer, so it falls back to plain CPU matmuls). Decode is 1 token, about 0 ms. On a phone this would be a second prefill of roughly the answer's own size.

## Examples
Caught CE (highest P(FAIL)):
- `K0main:vit-trv-003` (0.9994, corr 1.0): Chiang Mai -> Pai road. Context = a Chiang Mai grocery list. Answer: "about 50 km east... well-maintained".
- `K1screen:vit-hum-005` (0.9994, corr 1.0): the invisible hand. The context has the Smith quote; the answer adds "appears approximately 20 times" (it appears once).
- `K1screen:st-qa-cooking-se-020` (0.9976, corr 1.5): ice-cream custard. Context = Nowy Targ ice-cream parlours. Answer: "warm the dairy to make it more pliable".

False alarms (judge-correct, highest P(FAIL)):
- `K1screen:lan-cmp-003` (0.9987, corr 5.0): "countries bigger than India". Context = Wikivoyage India sightseeing. Answer lists Russia, Canada, Brazil, Australia: correct and unsupported.
- `K0main:lan-hlt-003` (0.9976, corr 4.0): mosquito diseases / HIV. Context = Wikivoyage China vaccinations. Answer: "dengue and West Nile, not HIV".
- `K0main:lan-cmp-003` (0.9973, corr 4.0): the same India question on K0, with a different correct memory answer.

Missed CE, grounded but wrong: `vit-cry-006` quadratic funding (P(FAIL) 0.002 on K0 and 0.002 on K1). The kept ethereum.org chunk mentions
collusion and public transactions, so the answer is "supported", but the judge marks it wrong (corr 1.0 / 1.5).

## Deviations / notes
- The base is Qwen3-1.7B Q4_K_M plus an f16 LoRA. The card uses bf16 + PEFT. The 3/3 smoke matches the card, but its numbers are not re-measured here.
- The K1 screen set is CE-enriched (27 problems + 10 sentinels). It is pooled as the criterion says. K0 MAIN alone gives the same reading
  (AUC 0.558, CI 0.348-0.768, recall at t\* 1/12).
- The labels come from one Haiku judge run (about 5 % CE noise per item, SCREENS.md). That noise cannot explain AUC ~0.5.
- The K1 dump waited about 3.5 min for the mini's 2-server guard while the smoke server was up. Nothing else on the mini was started or stopped.
- `gate/items.json` does not store the question text: the rnd pre-commit hook blocks pretty-printed JSON with blind-style ids next to `question`.
  The question is still in each prompt. After the run, `build_items.py` was changed to drop that field. A rebuild gives byte-identical
  gate inputs, and the analysis re-run gives the same result.
