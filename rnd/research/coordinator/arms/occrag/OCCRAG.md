# OCCRAG (hybrid OCC-RAG-1.7B / Qwen3-1.7B, K0 + K1, 2026-10-20): stage 1 NO-GO on both pack sets, stage 2 not run

TL;DR: OCC-RAG-1.7B answers only the items where the engine kept a source; Qwen3-1.7B answers everything else and takes over whenever OCC abstains or
breaks format. It changes very few answers: K0 has 3/37 changed and 2 fixed (6 needed), K1 has 7/37 changed and 3 fixed. No sentinel got worse.
OCC accepts only 3/15 (K0) and 7/25 (K1) of the source-present items it is offered. The rest are UNANSWERABLE (7 and 15) or malformed/looping traces (5 and 3).
Each OCC answer costs a median of about 330 generated tokens, against about 46 for the control. On the mini the OCC items take 2.1x the control's wall time.
The arm ends here.

| Item | Value |
|---|---|
| Model | occ-ai/OCC-RAG-1.7B-GGUF @ 57938bfa, OCC-RAG-1.7B-Q4_K_M.gguf, 1,107,405,952 B, sha256 `5ff807a93050972b39518ab09325e4f70d517cc8bdd3fe2924d4c36006412a51` (= HF LFS oid). Mini: <runner>/shared-models/lite/ (SHA256SUMS + DOWNLOAD.log appended; 38 GiB free after) |
| Licence | MIT on both HF cards (occ-ai/OCC-RAG-1.7B, -GGUF); base Qwen3-1.7B-Base Apache-2.0 |
| Candidate | occrag.patch sha256 `75b0ec82...` (be/adapter-litedecline.ts only; engine source untouched) |
| Criterion | OCCRAG-criterion.md sha256 `67a32346...`, committed bc7e228e before any judged candidate generation (the hybrid design from the coordinator update was applied before the freeze) |
| Runs | occrag-K0-screen-s42, occrag-K1-screen-s42 (mini, gen slot lock, 37 items each); Haiku calls 6 + 14 = **20**; 0 Opus, 0 paid |

## Format adaptation (adapter only)
- **Routing.** A generation with at least 1 engine context chunk goes to OCC-RAG, served by a second llama-server b11010 with `--special`.
  OCC sees the native format: the question as the only user turn (the engine's style reminder removed), the engine's chunks passed as `chat_template_kwargs.documents` in engine order (source id N = engine [N]), no system prompt, greedy decoding.
- **OCC output.** The engine sees only the answer section, with `<|source_id|>N` rewritten as `[N]`. An uncited ANSWERABLE answer gets the ids cited in the reasoning section appended as `[a][b]`.
- **Fallback to Qwen3-1.7B.** Qwen gets the original request, byte-identical to the control, in any of these cases:
  - OCC returns UNANSWERABLE, or an answer that is empty or "Not enough information";
  - the trace is malformed (no answer section, or a status that is not exactly ANSWERABLE or UNANSWERABLE);
  - a section opens twice while streaming (loop guard; the stream is stopped).
- **No source kept, or a prompt-form call.** Qwen3-1.7B, unchanged.
- **Trace cap.** OCC has no budget control. The adapter allows 512 trace tokens on top of the engine's 512. At the cap, a forced close lets the model write the status (up to 8 tokens) and then the answer (up to 64 tokens).
- **Smokes (not judged; smoke/).** 0 generation_failed. Fallback and no-source answers were byte-identical to the control on 4/4 items, so the mini is deterministic and control judgments are reused.
- **Why the smokes changed the design:**
  - At the engine's T 0.7 the section order scrambled, so OCC calls use greedy.
  - With no sources the model looped to the cap, which is why the coordinator chose the hybrid design.

## Gates (verbatim, tools/screen_gate.py)
```
screen K0: problems 27 (CE in mini control 23) | fixed 2 (need >= 6) | still CE 21 | sentinels worse 0/10 (max 1) | changed answers 3/37 -> NO-GO
  fixed vit-cry-003 1.5 -> 3.0
  fixed vit-cry-006 1.0 -> 2.0
screen K1: problems 27 (CE in mini control 21) | fixed 3 (need >= 6) | still CE 18 | sentinels worse 0/10 (max 1) | changed answers 7/37 -> NO-GO
  fixed vit-cry-002 1.0 -> 2.0
  fixed vit-cry-006 1.5 -> 2.0
  fixed vit-hum-005 1.0 -> 2.0
```
Screen deltas vs the mini control (n 37):
- K0: U +0.006 (0.000…+0.015), CE −0.054 (−0.135…0.000).
- K1: U +0.001 (−0.006…+0.009), CE −0.081 (−0.189…0.000).
- Both: decline 0, refusal-like 0.

## Routes, false-UNANSWERABLE, tokens, latency (tools/latency.py → latency/*.json)
| | K0 screen | K1 screen |
|---|---|---|
| Items with an answer generation / no generation (facts, places) | 29 / 8 | 28 / 9 |
| qwen-nosource (no source kept) | 14 | 3 |
| OCC-eligible (≥ 1 source) | 15 | 25 |
| answered by OCC | 3 | 7 |
| UNANSWERABLE → Qwen (false-UNANSWERABLE candidates) | 7 (47 %) | 15 (60 %) |
| malformed / looped → Qwen | 5 / 0 | 2 / 1 |
| OCC generated tokens per answer (trace + answer): median / p90 / max | 337 / 406 / 1352 | 329 / 432 / 609 |
| Control output tokens, median | 46 | 45 |
| Forced closes | 2 | 0 |
| Mini wall per answer, median, all 37: cand / ctl | 2.06 s / 2.77 s (0.74x)* | 9.50 s / 4.91 s (1.93x) |
| Mini wall, median on the OCC-eligible items: cand / ctl | 8.80 s / 4.17 s (2.1x) | 11.04 s / 5.47 s (2.0x) |
| Answer length, median words: cand / ctl | 40 / 41 | 40 / 42 |

\*The K0 control screen ran alongside the K1 control job (SCREENS.md), so its all-item median is inflated. The OCC-eligible rows are the comparison that matters.

- **Phone cost.** About 330 tokens per OCC answer means roughly 21–28 s of decode at 12–16 tok/s, against about 3–4 s now. The 1.5x latency clause would have failed on K1 and on the OCC items of both sets.
- **The false-UNANSWERABLE rate is the main finding.** On K1, OCC refused 15 of the 25 items where sources were kept. These include lan-cmp-003 (Qwen with the same context scores 5.0) and 4 items at 3.0. A standalone OCC (no fallback) would have turned those into refusals.
- **Format breaks on the Q4_K_M.** On 8 of the 40 OCC calls the model invented status tokens ("ANSWER_SOURCE", "HAS_ANSWER") or never wrote a status. Whether Q8_0 behaves better was not tested (UNKNOWN).

## Verdict
NO-GO on K0 and K1 (fixed 2 and 3, against 6 needed). Stage 2 was not run.
The changes are real but small:
- When OCC answers, it sometimes swaps a confident memory answer for a short grounded span, which moved 2–3 items from correctness 1.0–1.5 to 2.0–3.0.
- It abstains or breaks format on 72–80 % of the source-present items it is offered.
- It costs about 7x the output tokens.
- Most screen problems never reach OCC anyway: on K0, 14 items have no kept source.

## Examples (K1 screen; control → candidate, verbatim)
1. vit-cry-003, correctness 2.0 → 3.0 (OCC answered). Control: "Not found in this phone's offline library. From the model's memory, may be wrong:\nEIP-4444 reduces disk usage by pruning historical data, saving node operators significant space. The exact amount save…" Candidate: "It saves 400GB of disk space. [1]". Grounded and cited, but a bare span that drops the "what changes" half.
2. lan-cmp-003, false UNANSWERABLE. OCC said UNANSWERABLE on a context where Qwen answers "India is the seventh-largest country in the world by land area [5]. Several countries are larger than India by area, including Russia, Canada, Brazil, and Australia." (correctness 5.0). The fallback kept that answer.
3. lan-rsn-003, still a confident error (OCC answered). Candidate: "The pronghorn, for much longer than the cheetah[2][3]". The question was "Which land animal runs fastest, and for how long can it keep up its top speed?", and OCC answers the wrong animal confidently, with citations.

## Deviations
- The hybrid design follows the coordinator's update, received mid-arm and applied before the criterion was frozen. The brief's original drop-in OCC-only design was smoked but never judged.
- Two llama-servers per job. mini_gen.sh's "≤ 2 non-detector servers" start guard therefore makes other jobs wait while an OCCRAG job runs.
- run_arm.sh does not copy the adapter sidecar (`traces.occ.jsonl`), so it was fetched by hand from the mini job dir into sidecar/.
- The status check is exact: a lowercase "unanswerable" (1 K0 row) counted as malformed. It falls back to Qwen either way.
- Files: occrag.patch, OCCRAG-criterion.md, tools/{smoke.sh, latency.py, verdict.py}, traces/, judgments/, aggregates/ (incl. gate.txt/json), sidecar/, latency/, smoke/.
