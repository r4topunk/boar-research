# RC1-PRESS prediction (H4; frozen 2026-10-21 18:xx before any RC1 pressure cycle; DD1022 §5 kill event unchanged)

Source: ruler/hypotheses-round6-2026-10-21.json DD2-RC1-PRESS-MLOCK (lens B). Scorer: dd_check.py press. 0 judge.

## Runs (last of the day)
- Default-load arm (eval hook, EngineTweaks() default = MMAP; DeviceEvalRunner.kt l.190, snapshot 5f8cc8f4): per cycle Wi-Fi ON ->
  bash bg_set.sh press-4b-cN -> airplane ON -> thermal_gate.py press-4b-cN 340 (<= 34.0 C) -> python3 rc_eval.py run rc-press-4b-cN
  (c1 e4b22f35..., c2 c69c9a47..., c3 0e8387fa...; ids ruler/ids/dd1022-press-c1..c3.ids, 3 x 3). wiki-vital5 stays installed (H5).
  Sample adb shell dumpsys meminfo team.sopa.aoair every 5 s: TOTAL PSS, Private Dirty, Private Clean, Native Heap, .gguf mmap row, SwapPss.
- Preset arm (manual, only with r4to's explicit OK on the day; first item to cut): Settings -> "Run Boar Run" (MMAP_MLOCK), background apps
  re-opened, the 3 press-c1 questions typed in the chat UI, same meminfo sampling + logcat grep for mlock, then back to Auto. The eval hook
  cannot reach the preset. Force-stop the background apps at the end.
- Phone minutes: ~27 (3 cycles x 9 incl. cool) + ~10 preset = ~37.

## Prediction
Default arm: 3/3 cycles survive, TOTAL PSS peak <= 4.5 GB, 0 LMK lines naming team.sopa.aoair. Preset cycle: PSS within +/-0.2 GB of the
default cycle and 0 kills, because Android refuses the lock (0 MB locked, as on the X6 10-15).

## Readout (kill event = DD1022 §5: LMK/lmkd line naming the package, process gone >= 3 consecutive 10 s polls, or fewer rows than questions)
- 0/3 killed and PSS peak <= 4.5 GB -> prediction holds; gates table "the 4B (catalog download) fits 8 GB with background apps, 3/3, Pixel 8a".
- 0/3 killed, PSS 4.5-5.0 GB -> DD1022 §5 still passes (<= 5.0 GB); this prediction's PSS clause is printed as missed.
- >= 1/3 killed -> R4 8 GB row carries "killed in k/3 cold loads with background apps"; the 1.7B cannot be the fallback (not in RC1), so
  NOTE-1's amendment asks for the 1.7B entry on memory grounds (r4to OK).
- Preset cycle kills, or its PSS > default + 0.3 GB -> NOTE-1 adds "Run Boar Run unsafe on 8 GB". Preset not run -> NOT RUN, no claim.
- Cycles not started stay NOT RUN; 1 cycle is not a verdict.
- No 4B in RC1 -> the 3 cycles run on the 1.5B (requests edited to qwen2.5-1.5b-instruct-q4km, labelled "out-of-box install, only model
  installed"); the preset arm is dropped.

## Only the app maintainer can supply (none needed)
The NOTE-1 1.7B entry (revives rc-press-17b-c1..c3); an eval-hook load-mode field (would make the preset arm scriptable).
