# OCCRAG criterion (frozen 2026-10-20 before any judged candidate generation; HYBRID design per the coordinator update of 2026-10-20)

## Question
On the LITEPACKS system (Qwen3-1.7B, compact declines released behind the warning line), does OCC-RAG-1.7B answering the items where the engine kept
at least one source for the model cut confident errors (K0) and read the packs better (K1)?

## Candidate (arms/occrag/occrag.patch, sha256 in occrag.patch.sha256; be/adapter-litedecline.ts only, no engine source change)
- Model: occ-ai/OCC-RAG-1.7B-GGUF @ 57938bfad9737724b4e5a0b7942bea4dd4c942fb, file OCC-RAG-1.7B-Q4_K_M.gguf, 1,107,405,952 B,
  sha256 5ff807a93050972b39518ab09325e4f70d517cc8bdd3fe2924d4c36006412a51 (= HF LFS oid), MIT (model cards of occ-ai/OCC-RAG-1.7B and -GGUF).
  On the mini at <runner>/shared-models/lite/; a second llama-server b11010 (same flags + --special) next to the Qwen3-1.7B one.
- Hybrid routing per answer generation (adapter wrapper):
  - >= 1 engine context chunk in the request -> OCC-RAG, native format: one user turn = the question (engine style reminder removed), the chunks as
    chat_template_kwargs.documents in engine order (source id N = engine [N]), no system prompt, greedy (temperature 0, top_k 1; vendor default),
    output cap = engine nPredict 512 + 512 trace tokens, forced close at the cap (status <= 8 tokens, answer <= 64 tokens, greedy).
    Output to the engine = the answer section only, <|source_id|>N -> [N]; an uncited ANSWERABLE answer gets the ids cited in the reasoning section
    appended as [a][b].
  - Fallback to Qwen3-1.7B with the original request (byte-identical to the control path) when the OCC status is UNANSWERABLE or the answer is empty /
    "Not enough information" (route occ-abstain-fallback-qwen), the trace is malformed (no answer section or a status other than ANSWERABLE/UNANSWERABLE;
    occ-malformed-fallback-qwen), or a section opens twice while streaming (occ-looped-fallback-qwen; stream stopped).
  - 0 chunks (no source kept: the memory answer under the warning line) or a prompt-form call -> Qwen3-1.7B unchanged (qwen-nosource / qwen-prompt).
- Unchanged: retrieval, routing, packs, prompts of the Qwen path, sampling of the Qwen path, warning line, decline/release rules (answer.ts 0d1ac07d).
- Control = the MINI controls of arms/lp-screens/control (lpctl-K0-screen-s42, lpctl-K1-screen-s42, lpctl-K0-main-s42).

## Sets (dev only)
- Stage 1 = arms/lp-screens/screen-K0.ids then screen-K1.ids (27 problems + 10 sentinels each).
- Stage 2 = arms/lp-screens/main-97.ids (MAIN n 97) on a pack set that passes stage 1 and the latency clause.

## Judge
Haiku 5.5-low judge.v1-low, N = 4 shards, both orders, via arms/lp-screens/tools/run_arm.sh (answers identical to the control reuse control judgments).
0 Opus, 0 paid APIs.

## Budget
calls_cap: Haiku 1200

## Decision rule (stated before running)
- Stage 1 (per pack set): the gate printed by arms/lp-screens/tools/screen_gate.py: GO iff fixed >= 6 AND sentinels worse <= 1
  (worse = correctness drop >= 1.0, newly declined / refusal-like, or newly CE). Reported with it (tools/latency.py): route counts per screen
  (OCC answered / each fallback / Qwen no-source), the false-UNANSWERABLE count (occ-abstain-fallback-qwen rows), OCC tokens per answer
  (trace + answer + forced close: median, p90, max), answer length (words) and mini wall time per answer vs the control.
- Stage 2 runs only for a screen that is GO AND whose median mini wall time per answer (timing.totalMs over the 37 screen items) is <= 1.5x the
  control's. MAIN n 97 on that pack set; verdict by tools/verdict.py (paired item bootstrap B 2000 seed 11), both pack sets vs the mini K0 MAIN control:
  - K0 PASS iff CE rate change <= -0.05 with paired CI high < 0 AND decline + refusal-like rate change <= +0.03 AND U change >= -0.01.
  - K1 PASS iff U change >= +0.03 with CI low > 0 AND CE rate change <= +0.02.
  Otherwise NO.
- Known bias, report only: agg_run.py's refusal-like pattern does not match "Not enough information"; in this hybrid design OCC abstentions fall back
  to Qwen, so the phrase reaches the engine only through a Qwen answer. Judge-noise caveat per SCREENS.md (~5 % CE flips on re-judged answers).
  No re-run to rescue a NO.
