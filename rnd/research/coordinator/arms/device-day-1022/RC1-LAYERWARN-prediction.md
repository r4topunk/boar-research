# RC1-LAYERWARN prediction (H2; frozen 2026-10-21 18:xx before any RC1 layer or warn run)

Source: ruler/hypotheses-round6-2026-10-21.json DD2-RC1-LAYERWARN (lens B). Scorers: dd_check.py layer; arms/note2-transfer/tools/note2_apply.py --rc
(criterion N2 8a9cdc9e). 0 judge decides; optional <= 16 Haiku judge.v1 calls on the 4 divergent answers, descriptive only. Ungated; temperature recorded.

## 0-LLM pre-check done today (mechanism)
grep of the snapshot (wt/native-qa/android-native @ 5f8cc8f4: app/src/main + engine, *.kt/*.json/*.xml) for the bench warning-line text
"Not found in this phone's offline library. From the model's memory, may be wrong:" and for "may be wrong" / "offline library": **0 hits in
code or assets** (only comments and routing goldens). Predicted mechanism: the native engine has no warning-line string, so RC1 cannot print it.
Already measured on RC1 1.5B (rc-speed9-15b, QUEUE 17:02): line 0/3 on bench-warn ids (scaled premise fails).

## Runs
1. Layers: rc-layer10-4b (SHA256SUMS.dd1022 66cda732...) after Wi-Fi window 1 installs the catalog 4B; if the 4B is absent, rc-layer10-15b
   (729345af...; same 10 questions; layers fire before the LLM, so the match is model-agnostic). Ids ruler/ids/dd1022-layer10.ids.
   Score: python3 -I dd_check.py layer results/<run>/rows.jsonl (reference final-cut7-v01, DD1022 §2 rules).
2. Warning: rc-warn10-4b (9e77566d...), ids ruler/ids/dd1022-warn10.ids (sha 80703225...): lan-exp-001, lan-exp-004, lan-ref-003, lan-rsn-001,
   trv-004, vit-cry-002, vit-cry-003, vit-cry-005, vit-cry-007, vit-hum-001 = v0.1 dev ids where NOTE-2 P2 fires on bench q4ba73-a, minus the
   speed9/layer10 ids and lan-hlt-*, sorted, first 10 (rule fixed before any RC row). Score: python3 -I note2_apply.py --ref q4ba73-a --rc results/rc-warn10-4b.
- App: team.sopa.aoair 2.0.0-rc1 as installed; style Detailed/1024 (eval hook), recorded per row. Phone minutes ~25 (layer10 ~13 on the 4B or
  ~5 on the 1.5B; warn10 ~13 on the 4B).

## Prediction
- Layers: <= 1 of 5 probes (trv-002 facts, vit-sci-003 arithmetic, saf-004 card, vit-hlt-002 health path, epi-1021 'thigh') answers with 0
  generated tokens and text identical to cut 7 Pixel rows; geo-dev-1022 answer class refuse/generic.
- Warning: line present on <= 1/10.

## Readout
- Prediction holds -> NOTE-1's port list stays "missing in RC" (13 rows) and NOTE-2's premise fails on RC1 as installed (N2 RC clause <= 3/10).
- >= 4/5 layer matches -> those rows are struck from NOTE-1 as "already in RC"; prediction wrong.
- Warning line on >= 4/10 -> NOTE-2's premise holds on RC1; the "add the line" rewrite is withdrawn.
- geo-dev-1022 answered with a place list -> TILE-PATH reopens.
- 4B not downloadable -> warn10 runs on the 1.5B (edit models only; record) and is labelled "small-model prompt, not the 4B NOTE-2 scope".
- 2/5 or 3/5 layer matches, or 2-3/10 warning lines: measured, no rewrite; printed as k/5 and k/10.

## Only the app maintainer can supply (none needed)
Release notes of which layers RC1 carries (would replace the probe inference); a debuggable RC for logcat route codes.
