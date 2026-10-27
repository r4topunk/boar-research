# SFT4B (H10): can a small LoRA teach the 4B reader to use the kept pack passage, measured on the 180 pack-matched self-tests with a quote-verified teacher? (frozen 2026-10-13 20:0x, coordinator)

## Tags
Tags: none

## Question
The pack line's measured bound is the reader: retrieval-side levers moved reach a lot and quality little (ST2 +0.017; STACK +0.005), MedlinePlus passages are kept on 12/20 items with Δ ≈ 0, and the 35B reader is +0.054 over the 4B on the same passages (SELFTEST-DEEP). Arm **X = the claim 4B (Qwen3-4B-Instruct-2507) + a LoRA trained on extraction-style grounded QA built from the 11 published packs' own text**, served through the same engine and prompt as the claim build (merged weights → Q4_K_M GGUF, new adapter model id). Control **C = the claim 4B** (SELFTEST-SCORES with-pack traces/judgments, one pack installed). Reference: deep tier with pack (SELFTEST-DEEP).

## Fixed inputs
- Eval: the 180 public self-test items, one pack installed, claim settings (as SELFTEST-SCORES); no-harm: v0.1 public 60 (kit only), OFF = claim 4B traces (generate on the same tree/day), ON = LoRA model.
- Training data (stage 0): examples built ONLY from pack articles disjoint from every self-test item's source article and from the same-title stems (hash list `data/excluded-articles.json`, checked by `tools/disjoint_check.py`; the 100-item hold-out is disjoint too). Format = the engine's exact prompt (system + kept passages as the engine renders them + question) → target answer ≤ 60 words that states the fact and cites the passage the way the claim build does. Writer: Haiku 5.5 (no cap) from 1–2 chunks of a disjoint article; **filter: jev `quote_supports` ≥ 0.9 between the target answer and the passage (the quote-verified teacher the CLOSED R12 reopen line names), plus jev `answers_question` ≥ 0.8**; target 1,200 kept examples (≈ 110 per pack), hold-out 100 (never trained on).
- Training: mlx-lm LoRA on the mini (Qwen/Qwen3-4B-Instruct-2507 bf16 from HF, Apache-2.0; rank 16, all linear layers, lr 1e-5, 2 epochs, max seq 2,048; one declared recipe, no sweep); merge → convert_hf_to_gguf → Q4_K_M; adapter model id `qwen3-4b-instruct-2507-sft4b-q4km`.
- Judge: Haiku 5.5-low N=4 both orders (360 on the 180 + 240 on v0.1 OFF/ON); Opus N=4 on a near-miss (720).

## Power
expected_delta: +0.04 raw X − C on the 180 (source: RAFT / in-domain RAG fine-tuning literature +5–10 points on 7B readers; SELFTEST-DEEP: a reader that uses the same passages scores +0.054; P1: in-pack reading losses; the 4B's ≈ 50-word answers use the passage weakly (SELFTEST-SCORES medlineplus))
n: 180
seeds: 1 (deterministic generation; training seed fixed 42)
mde: ≈ 0.03 raw paired at n 180
slice: n/a
l1_futility: n/a
reopen: CLOSED R12 (fine-tune DATA line): that line failed on teacher faithfulness for long grounded answers (unsupported claims 6–16/20); this arm uses short extraction targets filtered per example by jev quote_supports ≥ 0.9 (the row's reopen condition) and a pack-matched eval with power (n 180, deterministic) instead of 20-example reviews
split: paired Δ by pack family (SE vs topic), declared; secondary descriptive: items where the fact article is kept vs not (reader effect should sit where the passage is present)

## Stages and rules
0. **Stage 0 (data + environment; jev ≤ [usage detail removed], Haiku writer calls uncapped but counted):** disjointness check passes (0 overlaps, 0 same-stem titles); ≥ 1,000 examples kept after the jev filters (report the filter pass rate; if < 50 % pass, stop: the teacher is not faithful enough, report); hold-out 100 built; mlx-lm installed on the mini, weights downloaded (sha + size in QUEUE), 50-step smoke LoRA runs without error; GGUF export path tested on the base model (base → Q4_K_M must reproduce the claim model's answers on 10 self-test items: identical or judged-equivalent, else stop: export is not parity).
1. Train (nohup, resumable checkpoints), merge, quantize; hold-out loss reported; smoke: 20 self-test items with the SFT model, 0 errors, answers ≤ cap, citations present.
2. Generate X on the 180 (MacBook) and v0.1 ON/OFF; precheck n/a (same prompts; the model differs); Haiku N=4 both orders; paired Δ X − C pooled / family / fact-kept split; same_answer field vs C (expected low; descriptive).
3. Verdict: LEVER (CI low > 0, Δ ≥ +0.03) → maintainer note + device plan question (a new 2.5 GB model file); SMALL; NO; not decided; near-miss → Opus 720. **v0.1 no-harm: CI high of (ON − OFF) ≥ −0.03 required; else NO regardless.** A LEVER also needs the hold-out answers to pass the same jev quote_supports filter at ≥ 0.9 on ≥ 80 % (no learned hallucination).

## Stop rules and budget

## Outputs and exposure
arms/sft4b/{STAGE0.md, SFT4B.md, tools/, data/ (examples, hold-out, excluded list; public pack text only), aggregates/, runs/}; model files under shared-models/ (mini + MacBook) with sha; QUEUE rows per stage (download, training start/end, verdict). No blind exposure (public items only).
