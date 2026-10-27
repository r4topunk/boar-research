# DETECTOR-FT: v3d-ft (encoder + head fine-tune with the cooking/money hard negatives) = **NOT ACCEPTED** (0 LLM / 0 Haiku / 0 Opus / 0 paid / 0 phone; mini + MacBook, 2026-10-23 00:12-00:45)
Criterion `DETECTOR-FT-criterion.md` sha 36635ca2… (matches its .sha256; QUEUE l.1709 swapped the two shas: bf31d1fb is NIGHT-criterion.md). Not edited. v3b files untouched (SHA256SUMS 6/6 OK). Nothing shipped, nothing committed.
## Training (mini, <runner>/kiln/detector-ft, MPS)
- Data (`tools/ft_prep.py`, `ft/prep.manifest.json`): v3b's 3,153 train items (common2 howto=pos + terse, split seed 30, same order) + the DETECTOR-HN hard negatives (2,129 mined + 1,000 random; ids sha b3bf04ff… = v3c's) = 6,282 (1,696 pos); val = v3b's 555. Texts = common2.detector_text.
- Recipe (`tools/ft_v3d.py` = ft_mmbert2.py with precomputed texts): jhu-clsp/mmBERT-small seq-cls, AdamW 3e-5, wd .01, batch 16, 6 % warmup, clip 1, max_len 128 left-trunc, 3 epochs (as v3b ran), seed 30. Synth-val AUC .9799 / .9927 / **.9942** (best epoch 3; v3b .9952). Wall 490 s. torch 2.14.1, transformers 5.18.0, py 3.14 (v3b: py 3.12, M1 Pro).
- Export: export_encoder/export_head → patched b11010 converter (convert-mmbert-e5-vocab.patch on a work copy) f16 → llama-quantize q8_0 + token table q4_0. Pipeline check: re-converting v3b's encoder gives a86fe8b9… byte-identical.
- Files: `shared-models/emergency-detector/sonar-mmbert-small-emergency-v3d-ft-q8te4.gguf` a1ab2121… + `…-v3d-ft.head.json` da2ffaa0… (`SHA256SUMS.v3d-ft`). Same architecture and size (106.2 MB) as v3b.
## Reads (threshold 0.2; candidate head on ITS GGUF vectors, mini build servers; `results/reads.v3d-ft.json`, `parity.v3d-ft.json`, `canary-check.v3d-ft.json`, `read4.v3d-ft.chunklevel.json`)
| read | v3b | v3d-ft | rule | |
|---|---|---|---|---|
| recall Compass 180 / Sonar dev 413 / terse 20 / PT mirror 28 / synth val 311 | 179 / 373 / 20 / 27 / 307 | 179 / 203 / 19 / 25 / 297 | 0 lost | **FAIL**: 185 lost (Sonar 170: 107 FirstAidQA, 42 pool p*, vit/saf/dng; terse tp-06; PT saf-005-ptm, vit-hlt-001-ptm; val 12), 2 gained |
| FP held-out titles (cook / money) | 3.40 % (6.58 / 1.07) | **0.00 %** (0 / 0) | ≤ 1 % | pass |
| cm40 self-tests fired | 6 | 0 | ≤ 1 | pass |
| 65 probes: health-strict routes | 47 | **13**; 34 lost, 0 new | all 47 kept | **FAIL** |
| Forge parity gate, mini build (decisions @0.2) | 298/300, 900/903 (re-run on the same build = Sonar's numbers) | **296/300, 888/903**, terse 30/30, long 45/45; ids 100 %; max \|Δp\| 1.00, min cos .933 | ≥ 99 % | **FAIL** (98.7 / 98.3 %) |
| canary (ref MacBook b11010, check mini build) | — | mini mean pass (cos 1.000000, L2 exact, Δp 0); last/CLS pooling correctly fail | pass | pass |
| MAIN 97 replay, chunk-level delivery (MAIN 92) | 42 (SEFIX-124) | **48** (cm 14 → 20, v0.1 28), 0 lost; = v3c's 6 items | ≥ 46, 0 lost | pass |
| other FP: Compass 120 / Sonar 490 / val 244 | 31 / 8 / 13 | 23 / 1 / 9 | reported | |
- **Verdict: NOT ACCEPTED** (reads recall, probe routing and parity fail). Step 3 (65-probe SEFIX F1+F2+F4 safety generation, two-seed Haiku screen, answers-v3d.*) not run; LEVER-CANDIDATE no. Haiku 0 of 200.
## Diagnostic (after the verdict, not eligible; `results/ft-diagnostic-0hn.json`)
- Same recipe, same machine, **0 hard negatives** (v3b's data only; AUC .9911), HF fp32: probes 45/47 kept (lost h05 h07 h17 h18 n09 n14, all in v3b's 0.28–0.66 band), Compass 179, terse 20, PT 27, cm fires 2 (ck-013, mn-004). So retrain noise costs ~6 probe routes; the hard negatives cost the other 28 and the 170 Sonar positives.
- v3d GGUF vs its own HF agree on 62/65 probes, 97/97 MAIN: the loss is the model, not the conversion. The parity miss is v3d-specific (v3b passes on the same build).
- Reading: with encoder + head free, the cooking/money titles (short how-to / number questions) pull every non-emergency-phrased health how-to and dose question to p ≈ 0 (h09, h11, n04, n18 go from 1.000 to 0.000). The FP target is reached many times over (3.4 % → 0 %) at a recall cost far beyond the head-only v3c (76 lost, 25 probes). The detector separation problem is not solved by more capacity with this negative set; the next try would need positive-side anchors (the lost probe/FirstAidQA style as positives, or a recall constraint in training) and its own criterion.
## Prediction vs result
Criterion prize: delivery 42 → 48 (hit, 48, the same 6 items) and FP ≤ 1 % (hit, 0 %); its risk "a fine-tune can shift the decision surface on PT and terse positives" materialised (PT −2, terse −1) and far more on health how-to/dose items.
## Mini state
<runner>/kiln/detector-ft (venv, data, models, logs; 4 GB, disk 31 GiB free); servers 18301-18305 stopped, :8094 untouched.
