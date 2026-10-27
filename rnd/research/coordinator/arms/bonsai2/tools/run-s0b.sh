#!/bin/bash
# BONSAI2-B S0: fetch Ternary-Bonsai-2 4B + 2B PTQ1_0 (no mmproj), verify sha vs HF LFS oid,
# llama-bench (4B -t8; 2B -t8 and -t4; 4B Q4_K_M control -t8 re-check), server smoke (5 v0.1 items, thinking off).
W=<runner>/kiln/bonsai2; S=$W/S0B.status; cd $W; echo "start $(date '+%F %T')" > $S; uptime >> $S
D=<runner>/shared-models/bonsai2; mkdir -p $D
PRISM=<runner>/spikes/llama-prism/bin
STDB=<runner>/spikes/llama-b11010/build-cpu/bin
dl() { # name rev sha
  local F=Ternary-Bonsai-2-$1-PTQ1_0.gguf
  curl -sSL -A "Mozilla/5.0" -o $D/$F.part "https://huggingface.co/prism-ml/Ternary-Bonsai-2-$1-gguf/resolve/$2/$F"; echo "dl_$1_rc=$?" >> $S
  local got=$(shasum -a 256 $D/$F.part | cut -d' ' -f1)
  if [ "$got" = "$3" ]; then mv $D/$F.part $D/$F; echo "$got  $F" >> $D/SHA256SUMS; echo "sha_$1 OK $(stat -f %z $D/$F)" >> $S
  else echo "sha_$1 MISMATCH $got" >> $S; rm -f $D/$F.part; fi
}
dl 4B 8d6557168168f91ea6697a4a49ed2ef622b53adb 56711263ec9a9ffeaa74a3a0e58dece8127cf9268404746c721113ca76994d60
dl 2B 683f7be2629342a50987627b40881e54761a2430 36061ad406df8a4903a6db005be350c50fabfaf717f9ef0acf4b76adcd9929fa
df -k ~ | tail -1 >> $S
B4=$D/Ternary-Bonsai-2-4B-PTQ1_0.gguf; B2=$D/Ternary-Bonsai-2-2B-PTQ1_0.gguf; Q4=<runner>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf
$PRISM/llama-bench -m $B4 -t 8 -ngl 0 -dev none -p 512 -n 64 -r 2 -o md > bench-s0b-4b-t8.md 2>bench-s0b-4b-t8.err; echo "b4_rc=$?" >> $S
$PRISM/llama-bench -m $B2 -t 8 -ngl 0 -dev none -p 512 -n 64 -r 2 -o md > bench-s0b-2b-t8.md 2>bench-s0b-2b-t8.err; echo "b2t8_rc=$?" >> $S
$PRISM/llama-bench -m $B2 -t 4 -ngl 0 -dev none -p 512 -n 64 -r 2 -o md > bench-s0b-2b-t4.md 2>bench-s0b-2b-t4.err; echo "b2t4_rc=$?" >> $S
$STDB/llama-bench -m $Q4 -t 8 -ngl 0 -p 512 -n 64 -r 2 -o md > bench-s0b-q4km-t8.md 2>bench-s0b-q4km-t8.err; echo "q4_rc=$?" >> $S
NT='{"chat_template_kwargs":{"enable_thinking":false},"temperature":0.7,"top_p":0.8,"top_k":20,"min_p":0,"presence_penalty":1.5}'
python3 smoke.py bonsai2-4b-ptq1 $PRISM/llama-server $B4 s0-items.json s0b-bonsai2-4b.jsonl "$NT" --device none -ngl 0 --no-op-offload >> $S 2>&1
python3 smoke.py bonsai2-2b-ptq1 $PRISM/llama-server $B2 s0-items.json s0b-bonsai2-2b.jsonl "$NT" --device none -ngl 0 --no-op-offload >> $S 2>&1
uptime >> $S; df -k ~ | tail -1 >> $S
echo "end $(date '+%F %T')" >> $S
