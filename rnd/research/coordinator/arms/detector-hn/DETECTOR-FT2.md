# DETECTOR-FT2: recall-constrained fine-tune with a small hard-negative dose = **NO ACCEPTED CHECKPOINT** (every dose rejected at the recall constraint; 0 LLM / 0 Haiku / 0 Opus / 0 paid / 0 phone; mini MPS + MacBook, 2026-10-23)
Criterion `DETECTOR-FT2-criterion.md` sha 34301679… (matches .sha256, not edited). v3b/v3c/v3d untouched (SHA256SUMS, .v3c-hn, .v3d-ft all OK). Nothing shipped, nothing committed.
## Training (mini <runner>/kiln/detector-ft, `tools/ft_v3e.py` = ft_v3d.py + every epoch saved + optional positive CE weight; v3b recipe otherwise)
- Data (`tools/ft2_prep.py`, `ft2/prep.manifest.json`): v3b's 3,153 train items + the top-D of the 2,129 mined titles by v3b p (ties by index); val = v3b's 555. D150 = 128 cooking + 22 money, all at v3b p = 1.000; D300 p ≥ .9997; D600 p ≥ .9922. Positive-weight variant: CE weight [1, 3] at D300.
- 4 runs × 3 epochs, seed 30, ≈ 250 s each; synth-val AUC e1/e2/e3: D150 .984/.994/.995, D300 .992/.996/.996, D600 .986/.995/.997, D300-pw3 .984/.993/.994 (v3b .9952). Train AUC is not the problem.
## Recall constraint first (all 12 checkpoints; HF fp32 screen `tools/hf2score.py` + `tools/ft2_screen.py` vs v3b's GGUF fires @0.2; the only near-miss re-read on its own GGUF)
| ckpt | Compass/terse/PT lost (of 179/20/27) | Sonar dev kept /373 | probe routes /47 | cm40 fires | Compass neg FP (v3b 31) | recall |
|---|---|---|---|---|---|---|
| D150 e1 (HF) | 1 (ed-en-016) | 370 (99.2 %) | 38 | 0 | 69 | fail |
| **D150 e1 (GGUF)** | **1** (ed-en-016; count 179 = 179 with ed-en-073 gained) | 370 kept, 395 total (99.2 %) | **40** (lost h05 h06 h07 h14 m04 n09 dng-005; 9 new) | 0 | 74 | **fail** |
| D150 e2 / e3 | 2 PT / 1 PT | 315 / 319 (84–86 %) | 23 / 28 | 0 / 0 | 27 / 27 | fail |
| D300 e1 / e2 / e3 | 1 / 8 / 1 | 338 / 284 / 301 (76–91 %) | 32 / 20 / 25 | 0 | 37 / 20 / 27 | fail |
| D600 e1 / e2 / e3 | 0 / 1 terse / 0 | 318 / 330 / 318 (85–88 %) | 26 / 19 / 19 | 0 | 54 / 27 / 27 | fail |
| D300-pw3 e1 / e2 / e3 | 0 / 12 / 2 | 354 / 279 / 296 (75–95 %) | 42 / 17 / 20 | 0 | 63 / 15 / 26 | fail |
- 0/12 checkpoints meet the recall constraint → D150, D300, D600 and the ×3 variant are all **REJECTED** at step 1. Every checkpoint also fails the 47/47 route read (best 42, D300-pw3 e1, which loses 19 Sonar positives).
- D150 e1 GGUF extra reads (reported, not needed for the verdict): held-out title FP 3.40 → 0.83 % (cooking 6.58 → 1.30, money 1.07 → 0.48); cm40 6 → 0 fires; but FP on health negatives up (Compass 31 → 74, Sonar 8 → 44, val 13 → 65): epoch 1 has not separated cooking from health, it has moved the boundary to "health-sounding vs not", so health non-emergencies fire more and some emergencies (h06 1.000 → .186, h14, m04) drop. `results/reads.v3e-D150.e1.json`, GGUF 7a9c88ef… + head 40879646… (`ft2/v3e-D150.e1.head.json`; GGUF left on the mini only).
- Not run (dose rejected): parity gate, canary, MAIN 97 replay, the 65-probe SEFIX F1+F2+F4 safety check, the Haiku screen, answers-v3e.*. LEVER-CANDIDATE: no.
## Prediction vs result
- Predicted: D150 keeps recall, cm fires 6 → 3; D300 knife edge (fires 1–2, Sonar −1…−3 %); D600 fails recall; 40 % chance of an ACCEPTED checkpoint.
- Result: the cm side was easier than predicted (0 fires at every dose and epoch, even D150 e1) and the recall side far harder: even 150 negatives cost 54–58 Sonar positives by epoch 2–3 and 7–24 probe routes at every checkpoint. D150 is not "keeps recall"; no knife edge exists in this dose range. The mined titles at v3b p ≈ 1 ("What to do when curdling occurs?", "slow cooker isn't done") are phrased exactly like first-aid how-to questions, so any dose of them teaches the encoder to drop how-to-phrased health questions (FirstAidQA faq*, Sonar p*), the same failure DETECTOR-FT saw at 3,129.
- Reading: the dose was not the only cause. Note the no-negative rerun already loses 2–6 probe routes to retrain noise, so 47/47 needs a recall anchor in training (the 47 probe-style / FirstAidQA-style positives as extra positives, or a loss that pins v3b's positive scores), not a smaller negative set. SEFIX-124 stays the safe set.
## Mini state
Disk 31 GiB free; checkpoints deleted except the D150 e1 GGUF (106 MB) + head; servers 18301–18304 stopped, tunnel closed, :8094 / Docker / ollama untouched.
