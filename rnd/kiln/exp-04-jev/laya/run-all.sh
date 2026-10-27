#!/usr/bin/env bash
# exp-04 LAYA arm, one heavy-queue job on the Mac mini (CPU, 4 threads). Offline after the pinned download.
set -euo pipefail
D=<runner>/kiln/exp-04-jev/laya; cd $D; mkdir -p preds onnx logs
export HF_HOME=$D/hf HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4
SNAP=$D/hf/hub/models--convaiinnovations--laya-multilingual/snapshots/e4e9ddf21a7b1903b7acffd8814ad4307bf63a67
T() { /usr/bin/time -l -o "logs/$1.time.txt" "${@:2}"; }
for s in tune test; do T fp32-$s .venv/bin/python run_laya.py --prompts v2.json --rows rows-$s.jsonl --out preds/laya-fp32-$s.jsonl --threads 4 --max-len 2048 > logs/fp32-$s.log 2>&1; done
T export .venv/bin/python export_onnx.py --model "$SNAP" --output onnx/laya-ml.onnx --quantize > logs/export.log 2>&1
ls -la onnx >> logs/export.log
for v in "onnx-fp32:onnx/laya-ml.onnx" "onnx-int8:onnx/laya-ml.int8.onnx"; do n=${v%%:*}; p=${v#*:}
  for s in test tune; do T $n-$s .venv/bin/python run_laya.py --prompts v2.json --rows rows-$s.jsonl --out preds/laya-$n-$s.jsonl --backend onnx --onnx "$p" --threads 4 --max-len 2048 > logs/$n-$s.log 2>&1; done; done
shasum -a 256 onnx/* > logs/onnx.sha256; du -h onnx/* >> logs/onnx.sha256
echo DONE
