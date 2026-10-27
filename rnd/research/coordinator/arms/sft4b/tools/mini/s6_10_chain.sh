#!/bin/bash
# SFT4B stage 1 steps 6-10 chain (mini), sequential, stops at the first FAIL. Run under nohup AFTER the coordinator's "v3 ready".
# usage: bash s6_10_chain.sh <train.jsonl sha256> <valid.jsonl sha256>   (files already copied to $K/train/data/{train,valid}.jsonl)
# -> $K/chain.status ; training $K/train/{log,status,df.log}; export $K/export/{status,p1.json}; parity $K/parity/final-*
set -u
K=<runner>/kiln/sft4b; S=$K/chain.status; cd "$K"
echo "start $(date '+%F %T')" > "$S"
[ "$(shasum -a 256 train/data/train.jsonl | cut -d' ' -f1)" = "$1" ] && [ "$(shasum -a 256 train/data/valid.jsonl | cut -d' ' -f1)" = "$2" ] || { echo "FAIL data sha" >> "$S"; exit 1; }
f=$(df -k ~ | tail -1 | awk '{print $4}'); echo "free_KiB=$f" >> "$S"; [ "$f" -ge $((27*1048576 + 600*1024)) ] || { echo "FAIL free < 27 GiB + 0.6 GiB checkpoints" >> "$S"; exit 1; }
bash s6_train.sh; grep -q '^DONE' train/status || { echo "FAIL-INFRA training ($(tail -2 train/status | tr '\n' ' '))" >> "$S"; exit 1; }
echo "trained $(date '+%F %T')" >> "$S"
bash s78_export.sh "$K/train/adapter" "$K/export"; grep -q '^P1 PASS' export/status || { echo "FAIL-INFRA export/P1" >> "$S"; exit 1; }
rm -f train/adapter/0000200_adapters.safetensors train/adapter/0000400_adapters.safetensors; rm -rf export/peft   # step 9 (pipeline-created only)
echo "cleanup done; free_KiB=$(df -k ~ | tail -1 | awk '{print $4}')" >> "$S"
G=$K/export/qwen3-4b-instruct-2507-sft4b-lora-f16.gguf
bash p_server.sh final-p0-nolora 10; bash p_server.sh final-p0-scale0 10 --lora-scaled "$G:0"
.venv/bin/python p_compare.py p0 parity/final-p0-nolora.jsonl parity/final-p0-scale0.jsonl > parity/final-p0.json; r0=$?
.venv/bin/python p_compare.py p0 parity/p0-base-a.jsonl parity/final-p0-nolora.jsonl > parity/final-p0-vs-baseline.json
[ $r0 = 0 ] || { echo "FAIL-INFRA P0" >> "$S"; exit 1; }
echo "P0 PASS" >> "$S"
bash p2_chain.sh final "$K/train/adapter" "$G"; grep -q 'rc=0' parity/final-p2.status && echo "P2 PASS" >> "$S" || { echo "FAIL-INFRA P2 (or undecided: exact agreement low -> Haiku fallback deferred)" >> "$S"; exit 1; }
echo "DONE $(date '+%F %T')" >> "$S"
