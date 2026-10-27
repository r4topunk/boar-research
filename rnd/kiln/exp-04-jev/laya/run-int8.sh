#!/usr/bin/env bash
# INT8 (ONNX) vs torch fp32, both max_len 1024 and one question per call; then the diagnostic plain-text variant (torch).
set -uo pipefail
D=<runner>/kiln/exp-04-jev/laya; cd $D; export HF_HOME=$D/hf HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4
/usr/bin/time -l -o logs/int8-1024-test.time.txt .venv/bin/python run_laya.py --prompts v2.json --rows rows-test.jsonl --out preds/laya-int8-1024-test.jsonl --backend onnx --onnx onnx/laya-ml.int8.onnx --split --threads 4 --max-len 1024 > logs/int8-1024-test.log 2>&1
/usr/bin/time -l -o logs/fp32-1024-test.time.txt .venv/bin/python run_laya.py --prompts v2.json --rows rows-test.jsonl --out preds/laya-fp32-1024-test.jsonl --split --threads 4 --max-len 1024 > logs/fp32-1024-test.log 2>&1
for s in tune test; do .venv/bin/python run_laya.py --prompts laya-b.json --plain --rows rows-$s.jsonl --out preds/laya-b-fp32-$s.jsonl --threads 4 --max-len 2048 > logs/laya-b-$s.log 2>&1; done
echo DONE
