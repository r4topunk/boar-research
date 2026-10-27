# DETECTOR-HN: v3c (hard negatives from the cooking/money titles) = **NOT ACCEPTED** (0 LLM / 0 Haiku / 0 Opus / 0 paid / 0 phone; MacBook, 2026-10-22 23:19-23:55)
Criterion `DETECTOR-HN-criterion.md` sha 7b7bed00… verified, not edited. Tools `tools/`, data `data/` + `DATA.md`, results `results/`, scratch `work/` (gitignored). v3b files untouched (SHA256SUMS OK). v3c head = `shared-models/emergency-detector/sonar-mmbert-small-emergency-v3c-hn.head.json` sha 9fe52ece… (`SHA256SUMS.v3c-hn`), it runs on the unchanged v3b GGUF. Nothing shipped, nothing committed.
## Data and training
- 60,758 unique thread titles (40 self-test threads dropped), split 80/20 seed 42: train 48,607 / held-out 12,151 (DATA.md). HN = 2,129 mined (v3b p ≥ 0.05) + 1,000 random train titles.
- Head v3c: v3b's head shape, warm-started from the v3b head, trained on the frozen v3b GGUF pooled vectors (local llama-servers, canary-exact; v3b p = trace p on 148/148 items) with ft_mmbert2's settings (AdamW 3e-5, wd .01, batch 16, 6 % warmup, clip 1, 3 epochs as run for v3b, seed 30, best epoch by synthetic-val AUC → epoch 2, AUC .9944 vs v3b .9952).
## Reads (threshold 0.2, GGUF + head; results/reads.v3c.json, read4.chunklevel.json)
| read | v3b | v3c | rule |
|---|---|---|---|
| 1 recall Compass 180 / Sonar dev 413 / terse 20 / PT mirror 28 / synth val 311 | 179 / 373 / 20 / 27 / 307 | 176 / 313 / 19 / 27 / 295 | **FAIL**: 76 lost positives (Sonar 60, 49 of them FirstAidQA; Compass ed-en-016/049/079; terse tp-06), 0 gained |
| 2 FP held-out titles (cooking / money) | 3.40 % (6.58 / 1.07) | **0.03 %** (0.02 / 0.04), −99 % | pass (≥ 50 % drop) |
| 2 cm40 self-tests fired | 6 (ck-005/013/015/017/018, mn-004) | 0 | reported |
| 2 FP on other negatives: Compass 120 / Sonar 490 | 31 / 8 | 22 / 1 | reported |
| 3 65 probes: detector fires (= health-strict route) | 47 | 22; **25 lost** (h04 h05 h07 h13 h14 h16 h17 h18 h25 h26 h29 h32 m02 m04 n02 n05 n08 n09 n10 n11 n14 n15 n17 nm02 dng-005), 0 new | **FAIL** |
| 4 MAIN 97 replay, SEFIX-124 switches + v3c p in the K3 tasks | fires on cm 6 (the 7th AUTOPSY item ck-002 is task:places, no detector) | cm fires 0; also unfires dng-005, vit-sci-003 | reported |
| 4 chunk-level delivery MAIN 92 (chunklevel.py score/summ) | 42 (cm 14, v0.1 28) | **48** (cm 20, v0.1 28), +6 = the 6 misfired cm items, 0 lost | pass (≥ 45, 0 lost) |
- Replay checks: v3b-rewritten tasks = original K3 traces 100/100 parsed-equal; v3b replay = sefix main.F1F2F4 97/97 (raw, wide, kept, codes); v3c changes kept lists on 7 and codes on 9.
- **Verdict: NOT ACCEPTED** (reads 1 and 3 not exact). Step 4 (65-probe SEFIX F1+F2+F4 safety generation, two-seed Haiku screen, answers-v3c.*) not run; LEVER-CANDIDATE no. Haiku 0 of 200 (CALLS.md).
## Diagnostic (after the verdict; not eligible for ACCEPTED; results/sweep-diagnostic.json)
| HN added | 0 (retrain only) | 10 | 30 | 100 | 300 | 1,000 random | 1,681 mined p≥.2 | 3,129 (v3c) |
|---|---|---|---|---|---|---|---|---|
| probe fires lost | 10 | 13 | 14 | 19 | 20 | 19 | 29 | 25 |
| Sonar positives lost | 11 | 20 | 27 | 33 | 52 | 35 | 85 | 60 |
| held-out title FP | 2.63 % | 1.43 % | 0.95 % | 0.56 % | 0.18 % | 0.62 % | 0.03 % | 0.03 % |
- Even with 0 hard negatives, re-running the recipe on the frozen GGUF vectors loses 10 probe fires, all in v3b's 0.28–0.75 band (h04 h05 h13 h17 h18 h29 n09 n10 n14 dng-005). Every HN dose loses more. No head-only variant keeps reads 1 and 3 exact.
- Reading: on the frozen v3b vectors the cooking/money titles sit next to the health probes, especially the number and dose questions (fever °C, mg, insulin units). A head can only move both groups together. The fix needs the encoder to change: a full v3b-style fine-tune (encoder + head, HN in the data), which gives a new GGUF and so needs the Forge parity gate and canary again. That needs its own criterion.
## Prediction vs result
FP 20–40 % → ≤ 10 %: the baseline was 3.4 %, not 20–40 % (miss), and it fell to 0.03 % (hit, beyond the prediction). Recall unchanged: miss (−76 positives, −25 probe fires). MAIN fires 7 → 1–2: 6 → 0 (the 7th is not a detector fire). Delivery 45–47: 48. Screen: not run.
## Caveats
- One head and one HN design (chosen before training). "Same recipe" here means head-only on the frozen GGUF, because v3b itself was a full fine-tune: the 0-HN control shows how much of the loss that alone causes.
- Titles are treated as negatives with no label check. A few are health-adjacent (e.g. "Polymer fume fever probably detected").
- Sonar dev positives include FirstAidQA how-to items (49 of the 60 lost). The probe losses on their own already fail read 3.
