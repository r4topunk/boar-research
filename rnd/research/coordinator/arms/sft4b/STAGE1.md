# SFT4B stage 1: environment only, arm closed at stage 0 (2026-10-13 21:04–22:3x, mini only; criterion 5853b8ea… + addenda 1 1730f4f9… / 2)

## Status: CLOSED AT STAGE 0 (coordinator 22:3x)
v3 data failed 2 of 5 gates: 562 kept < 1,000, and jev round-1 pass 38.3 % < 50 %. That is the criterion's stop rule ("the teacher is not faithful enough"). There was **no training** (step 6 never started) and no v2 fallback. Done: steps 1–5, plus the steps 7–10 tooling checked end to end on the smoke adapter. Step 11 was written but never run. Wall times: download 1.5 min, template gate < 1 min, smoke 19.9 min, P0 baseline + export + P1 + P0 scale-0 4 min, P2 tooling dry run ≈ 6 min. The mini was then cleaned (below).

## 1–3. Disk gate, download, config-only dir
- Gate: free 33 GiB − 5 = 28 ≥ 28 → PASS (35,122,960 KiB at 21:04).
- `mlx-community/Qwen3-4B-Instruct-2507-8bit` @ 0e42af58449718de7931ee04f28191fbe6c43a56 → `<runner>/shared-models/hf/Qwen3-4B-Instruct-2507-mlx8`. model.safetensors is **4,274,158,989 B, sha256 a6d98b6b22bd3928f0a9e38aea84c085e678bba1e03d028f21cbf6e0f6ed9f2c**; both match the pins. du 4.0 GiB. ~/.cache/huggingface grew by only 0.4 MB, so nothing was duplicated. Free went 33.5 → 29.5 GiB. DISK-LOG row added.
- `<runner>/kiln/sft4b/base-config` = Qwen/Qwen3-4B-Instruct-2507 @ cdbee75f… (config, generation_config, tokenizer*, vocab, merges; tokenizer_config sha a62ff0a2…).

## 4. Chat-template pin: PASS
- `chat_template.jinja` 40c21f34… is overwritten with Qwen's `chat_template` (string sha **64f85b19…**, matches the addendum). The mlx tokenizer_config carried no template.
- Gate on train.v2[0] (`tools/mini/s4_template.py`): no `<think>`. Prompt render + gen prompt is a byte prefix of the full render, and the token ids are a prefix too. The rendered target is `<|im_start|>assistant\n` + answer + `<|im_end|>\n`. The trailing `\n` is the template's turn separator. The trained (unmasked) tokens decode to answer + `<|im_end|>` + `\n`.

## 5. Smoke LoRA (50 it, 64 train / 16 hold-out v2, recipe + grad_checkpoint): PASS
- rc 0. **Peak memory footprint 10.63 GB** (`time -l`; < 11 GB, so no fallback and the 8-bit base is kept). Max RSS 2.44 GB. Trainable parameters 33.03 M (0.821 %).
- Speed: **13–14 tok/s** (mlx-lm counter); wall **1,194 s for 50 it ≈ 21.5 s/it** with GPU utilisation 97 %. Projection for 600 it with 7 evals on the full hold-out: **≈ 3.6–4 h**, against the 1–2.5 h estimate in PIPELINE-OPTIONS.
- Loss: val 2.090 (it 1, base) → 0.395 (it 25) → 0.457 (it 50). Train 0.99 → 0.058 (64 examples, 3 passes, so this is memorisation; diagnostic only).
- **Disk risk:** macOS swap grew during the smoke (swapfiles on the same container). Free fell 29.4 → **27.44 GiB minimum**, 0.44 GiB above the 27 GiB watchdog; free was 28.3 GiB afterwards. A ~4 h run plus 0.5 GiB of checkpoints can trip the watchdog. If it does, the run is resumable from the last 200-step checkpoint (`s6_train.sh <ckpt> <remaining>`).

## 7–8. Export path (checked on the smoke adapter, not the final one)
- `tools/mlx2peft.py`: 504 tensors = 252 pairs, r 16, alpha 320, 7 modules. `convert_lora_to_gguf.py --base base-config --outtype f16` runs end to end on Qwen3 with a config-only base. Output 66,094,848 B (smoke sha 9575f631…, discarded later).
- **P1 on the smoke adapter: PASS.** 9 tensors (q, k, down × layers 0/17/35, a superset of the 6). **Max relative difference 4.2e-4** (gate ≤ 2e-3); Frobenius about 3.0e-4. No transpose, naming or alpha errors.

## 10. Parity tooling (mini, `build-cpu` llama-server b11010, claim Q4_K_M, port 8097; :8094 untouched)
- 20 parity prompts: `parity/parity-prompts.jsonl` (sha b611ea6d…). These are the v2 hold-out examples, round-robin over the 11 packs, engine-rendered, public pack text. P0 uses the first 10.
- **P0 determinism baseline:** no LoRA, two fresh server runs, 10 prompts, greedy: **10/10 byte-identical** (text + tokens).
- **P0 identity (smoke adapter):** `--lora-scaled <smoke lora>:0` vs no LoRA: **10/10 byte-identical**. `/lora-adapters` shows scale 0.
- **P2 tooling dry run (smoke adapter, not the gate):** G1 ≠ G0 20/20. Same-sign effect: median Δlength +9 words (MLX) vs +3 words (GGUF), and Δcitations +1.35 in both. Exact agreement M0/G0 4/20 → M1/G1 7/20; first-divergence median 17.5 → 27.5 words. Server `/apply-template` = HF `apply_chat_template` on 20/20. Runtime LoRA cost on CPU: 25.5 → 24.0 tok/s (−6 %).

## 11. MacBook plumbing (written, NOT run; MacBook untouched)
- `tools/adapter-lora.patch` applies to kiln-local/be-0cfd4a77-cut7/be/adapter.ts (6298e5d3…; dry run applies). It adds `--lora ${BOAR_SERVER_LORA}` to the server args, and `lora.file`, `lora.sha256` and `model.variant` = `qwen3-4b-instruct-2507-q4km-sft4b` to `versions`. Patched adapter.ts sha256 **45574c77cf4e748d…**.
- `tools/run_selftest_sft4b.sh` = run_selftest.sh pointed at the side tree `kiln-local/be-0cfd4a77-cut7-sft4b` (ARM cut7-sft4b, adapter sha 45574c77), checking the LoRA sha via `BOAR_LORA_SHA`.

## Run notes / decisions
- Data decision (coordinator): v2 was first named as the stage-1 set (train.v2 1,000, sha a7b7b1b5…; holdout.v2 84, sha e49e52c9…; 16 hold-out articles never produced a passing target and were not replaced). jev round-1 pass was 56.1 % on checked answers (49.7 % counting length drops). Padding risk: the 35-word floor pulls in a third, tangential sentence. Superseded at 21:1x by v3 (distractor-rich, addendum 2); v2 was used only for the smoke.
- 600 it at batch 4 = 2.4 epochs on 1,000 examples (the base criterion's "2 epochs" assumed 1,200). The epoch count for v3 follows its size.

## Cleanup (closed line, 22:3x)
- Deleted: `<runner>/shared-models/hf/Qwen3-4B-Instruct-2507-mlx8` (4.0 GiB) and the empty `hf/` dir; the smoke adapters and smoke GGUF LoRA; the smoke data copies; `kiln/sft4b/train/` (v2 data copies); `kiln/sft4b/base-config/`.
- Kept: the venv, the tools, stage-0 data, and small logs/parity outputs (`kiln/sft4b` 973 MB).
- Free went 28,813,108 → 33,226,344 KiB (27.5 → **31.7 GiB**; `df -g` 27 → 31). :8094 is healthy. DISK-LOG row added.

## Reuse if the line reopens
Re-download (s1_download.sh), then s4_template.py on the new train[0], then `s6_10_chain.sh <sha train> <sha valid>` (train → export → P1 → cleanup → P0 → P2). For stage 2, use adapter-lora.patch and run_selftest_sft4b.sh. Multi-passage contexts will make training slower than the smoke's 21.5 s/it.

## Not verified
- Training itself: loss curve, wall time, and swap/disk over a ~4 h run (free also drifted to 27.5 GiB from other activity by 22:1x).
- P1/P2 on a trained adapter, and the GGUF LoRA sha. The smoke adapter overfit 64 examples, so its pass only shows that the tooling works.
- Transfer to the imatrix Q4_K_M at full training strength. The side-tree patch and runner were never applied or run.
