# GATELAT: can a reordered or trimmed GATE17 prompt keep the RU gate and cut its phone cost to <= 4 s?

TL;DR: **NONE qualifies** (criterion sha256 `94e86e40...` committed c90223a7 before any run).
- The cache trick works mechanically. With the LoRA loaded as an activated LoRA (aLoRA), the context-first prompt reuses the answer's KV, so only 151 tokens are new: **1.8 s projected on a Pixel 8a** (mini 1.3 s), versus 9.3 s for V0.
- But the gate stops working. In V1 the AUC falls from 0.934 to 0.66 (0.72 even with the LoRA on every token), and P(FAIL) never reaches 0.919 on any item (max 0.71). Decision agreement with V0 is therefore 54 %. The fine-tune only works in its trained card format.
- Trimming the context to the cited chunks (V2) meets the latency bar (3.9 s), but its AUC is 0.67. It refuses 18 of the 37 SUPPORTED answers, against 1 for V0.
- Next lever, if latency matters: a gate trained in the context-first / aLoRA format, or shipping V0 and accepting the cost. A prompt-only change is not enough.

## Results (124 RU gated answers, 37 SUPPORTED / 87 UNSUPPORTED, Haiku labels reused; bootstrap B 2000 seed 11)

| variant | AUC (CI) | AUC unwarned 56 | agree V0 @0.919 | flagged @0.919 | tokens p50 total / non-cached (unw) | mini wall p50 / p90 | Pixel 8a extra p50 / p90 (85 tok/s) | qualifies |
|---|---|---|---|---|---|---|---|---|
| V0 card order (RU) | 0.934 (0.883-0.974) | 0.898 | 100 % | 57 | 788 / 788 | 5.36 / 7.41 s | 9.27 / 12.24 s | ref (cost fails) |
| V1h context-first, aLoRA, cached | 0.660 (0.543-0.772) | 0.559 | 54 % | 0 | 1,080 / **151** | 1.29 / 1.37 s | **1.78 / 1.78 s** | NO (AUC, agree) |
| V1f context-first, LoRA on all tokens (diagnostic) | 0.723 (0.628-0.809) | 0.587 | 54 % | 0 | 1,080 / 1,080 | 7.42 / 9.93 s | 12.71 / 15.67 s | not eligible |
| V2 trimmed, card order | 0.671 (0.554-0.783) | 0.767 | 74 % | 79 | 332 / 332 | 2.51 / 3.67 s | 3.91 / 6.73 s | NO (AUC, agree) |
| V3h V1 + V2, aLoRA, cached | 0.673 (0.559-0.781) | 0.586 | 54 % | 0 | 624 / 360 | 2.46 / 3.81 s | 4.24 / 6.81 s | NO (all three) |

- **Rule:** AUC >= 0.90 AND agreement >= 95 % AND Pixel p50 <= 4 s on the unwarned 56.
- **Nearest miss on cost:** V1h (1.8 s), which fails on quality.
- **Nearest miss on quality:** V2 on cited items (AUC 0.767 vs V0 0.898 on the same 56). Where nothing is cited, top-2 trimming gives AUC 0.507 (V0 0.946).

## Why
- **V1 (reorder).** The LoRA was fine-tuned on one exact layout: rubric, then QUESTION/CONTEXT/RESPONSE in one user turn. As a follow-up turn after the conversation, it leans to PASS.
  - Median P(FAIL) is 0.08 on supported answers and 0.12 on unsupported ones in V1h, and 0.13 / 0.18 in V1f.
  - The ranking is weak and the 0.919 threshold is never crossed.
  - The aLoRA mode costs a further 0.06 AUC on top of the reorder. Context tokens computed without the adapter are not what this LoRA was trained on.
- **V2 (trim).** The support labels were made against the full context. When an answer takes a claim from an uncited chunk, the trimmed context drops its support, so the gate FAILs supported answers: 18 of 37 flagged, against 1 for V0.
  - Warned answers carry no citations, so top-2 trimming is close to random on them.

## Checks
- The rendered answer prompt matches the trace's promptTokens on 124/124 items, and answer prompt + answer is a token prefix of V1 on 124/124.
- The aLoRA invocation (`<|im_start|>user\nYou are a groundedness guardrail`, 10 tokens) was found on 124/124 items.
- Server-measured non-cached prompt_n equals the token-sequence computation (V1h: 0 difference on all items; V3h: -2...0).
- On the plain-LoRA server, V0 prompts were not re-run. RU's outputs are the reference.
- PASS/FAIL tokens were in the top 50 on every call.

## Setup
- **Gate:** the same as RU (Qwen3-1.7B-Q4_K_M b139949c + gate17-lora-f16 d022352e).
  - Runtime: llama-server b11010, CPU -t 4 -c 8192, --reasoning off, -np 1, on the mini, slot gen1/gen2. Each server was stopped after its pass.
  - **aLoRA copy:** identical tensors (392) plus `adapter.alora.invocation_tokens` (uint32), made by `tools/mk_alora.py` and deleted after the run. llama.cpp then evaluates the pre-invocation tokens with base weights, which equals the answer model's KV, so the cache hit is valid.
- **Hybrid sequence, per item:** prefill (answer prompt + answer) with cache on, then the gate request, then the same for V3.
- **Trimmed context:** the chunks the answer cites ([n]) with their original numbers. When nothing is cited, the first two chunks. 56 items were cited and 68 were not; the median is 2 of 4 chunks.
- Budget: 0 judge, 0 Haiku, 0 Opus, 0 paid. Mini: plain pass 22:16-22:37 (248 calls), aLoRA pass 23:05-23:20 (124 x 4 requests).

## Deviations
- **Run 1:** the plain pass completed, then `mk_alora.py` failed because the mini's stdlib Python lacks yaml and tqdm. I stubbed both; they are unused for a KV copy.
- **Run 2:** the aLoRA GGUF was rejected because its array was written as INT32. I fixed it to UINT32 and resumed with `RESUME=1` (tok and plain kept).
- No decision run was repeated, and inputs, prompts and rule are unchanged.

## Caveats
- The projection assumes 85 tok/s is flat across context position and that the LoRA costs nothing extra on the phone. It also assumes llama.rn keeps the answer KV and supports aLoRA; neither was verified, and both are moot since nothing qualifies.
- The cached prefix uses the re-tokenized answer text. The phone holds sampled tokens, and warned answers had their citations stripped after generation.
- AUC is against single-family Haiku support labels (5 tie-breaks). One gate pass per variant, deterministic at temperature 0.

## Files
- `GATELAT-criterion.md` (+ `.sha256`)
- `tools/`: build_inputs, mini_gatelat, mk_alora, run.sh, analyze
- `gate/`: inputs, tok, plain, hyb (.jsonl)
- `analysis.json`
- `runs/`: run logs, server logs, mk_alora log
