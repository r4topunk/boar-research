# RC1-VITAL5 prediction (H5; frozen 2026-10-21 18:xx before the pack is downloaded)

Source: ruler/hypotheses-round6-2026-10-21.json DD2-RC1-VITAL5 (lens B). 0 judge, 0 LLM readout.

## Run
- Wi-Fi window 2 (after H3 and H2): RC1 Knowledge -> BOAR Knowledge -> Wikipedia Vital Articles -> Download (snapshot catalog: wiki-vital5,
  sqlite-pack, 163,647,488 B, sha256 d3b87d56...; the RC1 screen shows 156 MB = MiB). Record on-device size/sha, then airplane ON.
- thermal_gate.py rc-vital9-15b 310; python3 rc_eval.py run rc-vital9-15b (SHA256SUMS.dd1022 bf155205...; same warmup + 9 questions as
  rc-speed9-15b, model qwen2.5-1.5b-instruct-q4km, Detailed/1024 by the eval hook). Leave the pack installed for H4.
- Diff against results/rc-speed9-15b (paired on queryId): retrievalUsed, retrievalMs, contextTokensBefore/After, retrievedTitles, key-string
  regex from arms/rc1-pixel/aggregates/parity.json; logcat must show "knowledge base + 1 packs".
- Phone minutes ~12 (3 download in the window + 6 run + cool-down).

## Prediction (n = 9, warmup excluded)
retrievalUsed >= 4/9 (vs 1/9 with 0 packs), retrievalMs p50 <= 0.6 s, key string present on >= 7/9 (vs 6/9).

## Readout
- **PACKS-BIND** (prediction holds): >= 4/9 with logcat "+ 1 packs" -> RC1's 1/9 came from missing packs, not the 0.7 gate; backs NOTE-5
  with a measurement on his binary.
- **GATE-BINDS** (kill): <= 2/9 with logcat confirming 1 pack -> the gate/routing binds; NOTE-5 adds a gate line and RC1-PARITY's "0 packs"
  explanation is marked incomplete.
- 3/9: measured, no verdict.
- Pack not in RC1's catalog, download fails, or logcat shows 0 packs -> NOT RUNNABLE; NOTE-5 keeps the bench-only argument.
- Caveat fixed now: wiki-vital5 is his pack, not ours; n = 9 reasoning/comparison ids (mde not met): the readout is a direction, not a size.

## Only the app maintainer can supply (none needed)
NOTE-5 catalog entries for our boar-packs (revives any boar-packs run on RC); a .sqlite picker or a debuggable RC (revives rc-aunion10).
