# FOTAPOL onboarding: fotapol/qwen3-1.7b-financial-rag-lora-v4 on the BOAR Qwen3-1.7B (2026-10-20/21)

TL;DR: licence OK (Apache-2.0), adapter sha matches the card, base weights match our unsloth Q4_K_M, the LoRA converts and loads with llama-server `--lora`, thinking stays off, and the 5-item smoke through the real engine has 0 failures. Answers are shorter (26 vs 34 tokens), `[n]` citations kept on 3/4 shown answers (plain 4/5), 1 of 5 answers lost its citation and was released behind the warning line. No `[Source n]` tags leaked. The LoRA did not slow generation in the smoke, but the plain run was more contended. Cleared for the GATE v2 screens.

## Checks
| Check | Result |
|---|---|
| Licence | Card front matter `license: apache-2.0` and Hub API tag `license:apache-2.0` (HF rev `d1af458b0bde4c74ccf87e3042ac8bb2390a8c65`). Base Qwen/Qwen3-1.7B is Apache-2.0. Card: "pet-project research artifact, not a financial-advice system". Training data: FinQA / DocFinQA + a synthetic lookup set (dataset_manifest.json). |
| Adapter | PEFT LoRA r16 / alpha 32 / dropout 0.05, all 7 linear projections, peft 0.20.0, not DoRA/rsLoRA. `adapter_model.safetensors` sha256 `6a89a40cb988567ee09e1ed049b19f09456ec84975738da9edec27613627b2e2` (= the card's value), 34,917,504 B; adapter_config.json sha256 `02e7bf4d...`. Downloaded to mini `<runner>/kiln/fotapol/adapter/` from the pinned revision, generic UA. |
| Conversion | llama.cpp b11010 `convert_lora_to_gguf.py --outtype f16 --base <runner>/kiln/gate17/base` (Qwen3-1.7B rev 70d244cc config + tokenizer only, reused from gate17; no base weights downloaded), in a throwaway `uv run --no-project --python 3.12 --with torch safetensors numpy transformers sentencepiece protobuf` env (cache 1.4 GB, deleted after). Output `<runner>/kiln/fotapol/fotapol-v4-lora-f16.gguf`, 392 tensors, 34,892,064 B, sha256 `a04b72ac33670121a9c300a4e9c5da6836fa0a501f07ee1b390586f768dcfe45`. Log: mini `<runner>/kiln/fotapol/convert.log`. |
| Base revision | Adapter expects Qwen/Qwen3-1.7B @ `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e` (adapter_config `revision`, training_metadata). Our Q4_K_M is unsloth/Qwen3-1.7B-GGUF @ `d7f544ee` (2025-06-08, sha256 b139949c). The Qwen repo commit history shows the weights uploaded once (`8d4744f9`, 2025-04-28); every later commit (README, tokenizer_config `0ecc6541` 2025-05-19, LICENSE `70d244cc` 2025-07-26) leaves the weights untouched. So the adapter's base weights = the weights unsloth quantized. Not identical: our base is Q4_K_M, the adapter was trained on 4-bit NF4 QLoRA and is applied in f16 on Q4_K_M (same situation as gate17). |
| Template / thinking | Adapter's chat_template.jinja = the stock Qwen3 template; trained with `enable_thinking: false`. BOAR already runs `--reasoning off` + enable_thinking false; the env keeps `--reasoning off` and only adds `--lora`. Smoke traces: reasoningTokens 0. |
| Trained prompt vs BOAR | Trained with its own system message ("financial document QA ... cite them as [Source N] ... If the context does not fully support an answer, respond exactly: I cannot answer this question from the supplied context."). BOAR's prompt and `[n]` numbering stay unchanged (deployability variant (a)); the card's format is not used. The trained refusal string matches labels.py MODEL_DECLINE ("i cannot answer"), so if it appears it is counted as a decline. |
| Sampling | Card: greedy. BOAR keeps its sampler (T 0.7, top_k 40, seed 42) so only the adapter changes. |
| Load | Env file `fotapol.env` (quoted, arms/greedy lesson) sets `BOAR_SERVER_EXTRA_ARGS="--reasoning off --lora <abs path>"`; adapter-litedecline.ts splits it on whitespace into llama-server args; recorded in every trace as `runtime.versions.server.extra_args`. |

## Smoke (5 K0 screen items: 3 problems lan-cmp-004, lan-cmp-005, lan-exp-007 + 2 sentinels lan-ref-002, st-boar-medlineplus-en-013; LoRA then plain, same mini session, tools/smoke.sh -> tools/gen_only.sh)
| | LoRA | plain (same session) | plain (mini control traces) |
|---|---|---|---|
| rows / errors | 5 / 0 | 5 / 0 | 5 / 0 |
| declines / warned | 0 / 1 | 0 / 0 | 0 / 0 |
| `[n]` cited (shown) | 3/4 | 4/5 | 4/5 |
| `[Source n]` tags | 0 | 0 | 0 |
| output tokens mean | 26 | 34 | 34 |
| wall sum / p50 | 13.3 s / 2.8 s | 17.8 s / 4.0 s | 12.2 s / 2.86 s |
| prefill p50 | 2,125 ms | 2,497 ms | 1,805 ms |
| decode tok/s p50 | 52.1 | 39.2 | 55.9 |
The two smoke runs shared the mini with another generation job (loadAvg 2.5-5.5), so speed is load-dominated. Against the uncontended control the LoRA's prefill is about 18 % slower (the f16 LoRA leaves the CPU_REPACK fast path, as in gate17) and decode is about 7 % slower. The plain smoke reproduced 4/5 control texts byte-for-byte (lan-exp-007 differs), so the control is not fully deterministic across runs.
Examples (LoRA): lan-cmp-004 "The adult male moose weighs more on average than an adult male American bison. [1]" (plain adds weights). lan-exp-007 lost its `[1]` and was released behind the warning line (counts as a default-mode refusal; watch for false refusals). st-boar-medlineplus-en-013: atrial fibrillation / ECG, uncited in both arms.
Files: smoke/smoke5.ids, smoke/{fotapol-smoke,plain-smoke}/ (traces, status), smoke/extra_metrics.json (tools/extra_metrics.py).
