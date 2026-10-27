# Plumb: exact commands for the the bounty post's eval (vitalik-lantern)

TL;DR: worktree `wt/eval-vitalik` (branch `eval/vitalik-lantern` from `feat/eval-inapp-benchmark` @4ecdc68, plus `eval/` from `feat/eval-frontier` @0a024db and the Lantern dataset). Device: iPhone 13, bundle `team.sopa.aoair`, installed build `rc6eval-r11-0459` (= `build/model-ab-rc6-eval` @14de107, `EXPO_PUBLIC_DEVICE_EVAL=1`, the R11 build, 0.47 on v2). No install needed.

## Preconditions (device)
- Coordinator gave the go (D5). The phone is unlocked, **out of airplane mode** (packs download, ~2 min), and nobody else is driving it.
- Nothing is installed. `eval-iphone.mjs` relaunches `team.sopa.aoair` with `--terminate-existing`, which puts the eval app in the foreground.

## 1. Factual subset (38, ~8 min)
```bash
cd <workspace>/wt/eval-vitalik
SHA=14de107
node scripts/eval-iphone.mjs \
  --questions eval/dataset/questions.vitalik-lantern.jsonl \
  --only "$(python3 -c 'import json;print(",".join(json.load(open("eval/dataset/subset.factual.vitalik-lantern.json"))["ids"]))')" \
  --install-assets boar-crypto,boar-wikivoyage-en \
  --quick-first on --always-complete off \
  --dataset vitalik-lantern \
  --out eval-results/iphone/vitalik-factual \
  --runs-file eval/results/runs/vitalik-lantern/qwen2.5-1.5b-instruct-q4km__iphone-$SHA.jsonl
```

## 2. Device subset (52, ~10 min): only if step 1 runs clean
Same command with `subset.device`, `--out eval-results/iphone/vitalik-device` and `--runs-file …__iphone-$SHA-device.jsonl`. The 38 factual ids are asked again, which gives a free repeatability check.

## 3. Desktop ([usage detail removed], `claude -p`)
```bash
cd <workspace>/wt/eval-vitalik/eval
node scripts/gen-references.mjs --dataset vitalik-lantern --ids <52 device ids>   # resumable
node scripts/judge.mjs  --dataset vitalik-lantern --system qwen2.5-1.5b-instruct-q4km__iphone-$SHA --subset factual
node scripts/report.mjs --dataset vitalik-lantern --subset factual --name vitalik-lantern-factual-$SHA --systems qwen2.5-1.5b-instruct-q4km__iphone-$SHA
python3 <workspace>/rnd/lantern/tools/precheck.py results/runs/vitalik-lantern/qwen2.5-1.5b-instruct-q4km__iphone-$SHA.jsonl \
  --questions dataset/questions.vitalik-lantern.jsonl --subset dataset/subset.factual.vitalik-lantern.json
```
