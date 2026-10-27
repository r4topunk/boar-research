# DECODE-GROUND (2026-10-21 20:5x): grounding the 1.7B at decoding time — select evidence under a grammar, amplify it with context-aware decoding, fall back to closed-book

Status: CONCEPT + BUILD (stage 0/1). Owner: coordinator (main). Criterion: `DG-criterion.md` (to be frozen after the smoke, before any judged run).

## TL;DR
Every lever tried on the 1.7B + packs so far lived **before** the model (routing, keep, reach, chunk order, pack sets, prompt wording, thinking, sampling) or **around** it (model swaps, LoRA gates). None touched the only place where the knowledge pack and the model's prior actually meet: **the next-token distribution**. DECODE-GROUND moves the pack into the decoder in three composable steps, all runtime-only on llama.cpp b11010 (no llama.cpp or llama.rn change; harness/adapter code only):

1. **SELECT** — the model itself picks the evidence. A GBNF grammar built per question lists the sentences of the *raw* retrieval candidates (top-N before the keep step) plus one `NO_EVIDENCE` alternative; the 1.7B emits one choice (≈ 10 tokens). Selection is a recognition task, which small models do far better than open generation, and the menu includes chunks the keep step dropped (RAG-FUNNEL S3, 17/97).
2. **AMPLIFY** — context-aware decoding (CAD, Shi et al. 2023, arXiv 2305.14739): at each token, p ∝ p(y | selected evidence, q)^(1+α) / p(y | q)^α. Two llama-server slots (same model, `cache_prompt`), top-k logprobs from both, greedy on the combined score. This directly attacks the measured reading wall (−0.070 at identical contexts; GATE17-SUPPORT: 84 % of source-present answers unsupported; RAG-FUNNEL S4, 17/97). A cheaper sibling, **COPY-BIAS**, adds `logit_bias` +b to the content tokens of the selected evidence (one pass, device-portable in principle; llama.rn rc.4 crashes on logit_bias, the native JNI does not).
3. **FALLBACK** — `NO_EVIDENCE` → the plain closed-book prompt (no sources block). This removes the crowding loss (−0.019 single→multi pack; off-topic appends in 25–57 % of K1 prompts per MODEL-USAGE P0 RET-F1/CTX-F1) and shortens the prompt (time win) on exactly the items where packs cannot help.

## Why this is the right box to think outside of
| measured wall (where) | what fixes it in the funnel | DECODE-GROUND step |
|---|---|---|
| fact retrieved but dropped at keep: S3 17/97 (CB17) | the keep heuristic | SELECT over raw candidates |
| fact kept, answer still wrong: S4 17/97; 84 % unsupported (GATE17) | the reader | AMPLIFY (CAD / copy-bias) |
| off-topic sources hurt: crowding −0.019; RET-F1 57 % | the gate | FALLBACK on NO_EVIDENCE |
| fact in no installed pack: S1 45/97 | coverage (NOTE-5 catalog) | **not addressed** — ceiling |

Honest ceiling: on MAIN 97 only ≈ 34 items (S3 + S4) are reachable, and 63/97 K0 answers are byte-identical to closed-book because nothing was kept. An aggregate ΔU of +0.02…+0.05 would already be the largest 1.7B+packs lever measured; the mechanism question is read on the fact-in-an-installed-pack subset (frozen ids before the run).

## Arms (Qwen3-1.7B Q4_K_M, K1 pack set, mini, seed 42, -t 4, default repack, same host as MINI-BASELINE)
| arm | SELECT | decode | fallback | extra cost (expected) |
|---|---|---|---|---|
| B = MINI-BASELINE K1 (exists) | keep step | plain | — | — |
| S | grammar over raw top-N sentences | plain, context = selected sentence(s) + their chunk | closed-book on NO_EVIDENCE | +≈10 tokens; shorter prompt on fallback |
| C1 | keep step (as B) | CAD α 1.0 on the kept context | — | 2 decode passes per token (research ceiling probe) |
| SC | grammar | CAD α 1.0 on the selected evidence | closed-book | 2 passes when evidence selected |
| SB | grammar | copy-bias b 2.0 on selected evidence tokens | closed-book | ≈ 0 (shippable candidate) |
Smoke first (5 items × arm): token-id round trip, grammar acceptance, no repetition loops, timings. α/b fixed before the freeze from the smoke only (no judge).

## Measurement (draft; frozen in DG-criterion.md)
- Screen = **GATE v2** (arms/null-cal/GATE-V2.md, tools/screen_gate_v2.py), K1 params: net ≥ 9, false refusals ≤ 4, U_cov Δ ≥ −0.071; divergence-first: only answers that differ from B are judged; Haiku 5.5-low N 4 both orders. Judge order: S → SB → SC → C1 (stop a branch when its cheaper parent is NO-GO and its own net ≤ parent's).
- Secondary (reported, no rule): ΔU vs B on the fact-in-pack subset (RAG-FUNNEL S2–S5 ids) and on S1; CE-unwarned counts; mean output tokens and totalMs vs B; NO_EVIDENCE rate and its agreement with the RAG-FUNNEL S1 label.
- Confirm: an arm that is GO on K1 and whose Haiku ΔU ≥ +0.02 on MAIN 97 runs the CV5 51 under Opus judge.v1 paired against the CB17/K0 Opus rows (≤ 110 Opus). Claim-grade only then.
- Caps: Haiku ≤ 700, Opus ≤ 110, paid 0, phone 0 min. Kill: any arm with > 5 % empty/loop answers or mean totalMs > 4× B is stopped before judging.

## Device path (for the notes, not for this arm)
S + SB cost ≈ nothing at decode and are expressible in the app maintainer's JNI loop (grammar sampler + logit bias exist in llama.cpp's sampler API). CAD needs two contexts per token (≈ 2× decode) and is a research probe for "how much of the gap is reading"; if C1/SC pay and SB does not, the follow-up is a one-pass approximation (CAD on the first k tokens, or selected-evidence prefix caching).

## Literature priors (verified titles; numbers are the papers', on other models and tasks)
- CAD: +7–15 points on knowledge-conflict / summarization faithfulness for 7–13B models, larger for smaller models (arXiv 2305.14739).
- Grammar-constrained selection: selection ≫ generation for small models (recognition vs recall); our own LITE17 Q (free-text quote-then-answer) was +0.002, so the gain must come from the grammar and the raw-candidate menu, not from quoting per se — that is the risk.
- Context-token logit bias: no clean prior; treat SB as the cheap approximation of CAD, read against C1.
