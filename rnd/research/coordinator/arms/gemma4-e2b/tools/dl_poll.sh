#!/bin/bash
# GEMMA4-E2B onboarding: resume the Q4_K_M download on the mini only when free disk after the download stays >= 25 GiB and no other
# download into shared-models is in flight. Polls every 10 min, up to 90 min. Prints DL_OK / DL_TIMEOUT. (The mini login shell is fish: bash -s.)
SIZE=3106738272; F=<runner>/shared-models/lite/gemma-4-E2B-it-Q4_K_M.gguf.part
URL=https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF/resolve/0314792d7f1f7e229411f620751375812bb9faf2/gemma-4-E2B-it-Q4_K_M.gguf
for i in $(seq 0 9); do
  r=$(<on the mini> bash -s <<EOS
free=\$(df -k ~ | awk 'NR==2{print \$4*1024}'); have=\$(stat -f %z $F 2>/dev/null || echo 0); other=\$(pgrep -f 'curl.*gguf' | wc -l | tr -d ' '); echo \$free \$have \$other
EOS
)
  set -- $r; [ $# = 3 ] || { echo "bad probe: $r"; sleep 600; continue; }
  after=$(( $1 - (SIZE - $2) )); echo "$(date +%T) free=$1 have=$2 other_dl=$3 after=$after need=$((25*1024*1024*1024))"
  if [ "$3" = 0 ] && [ $after -ge $((25*1024*1024*1024)) ]; then
    <on the mini> bash -s <<EOS && { echo DL_OK; exit 0; }
set -e; cd <runner>/shared-models/lite; curl -sSL --fail -C - -o gemma-4-E2B-it-Q4_K_M.gguf.part $URL; mv gemma-4-E2B-it-Q4_K_M.gguf.part gemma-4-E2B-it-Q4_K_M.gguf; shasum -a 256 gemma-4-E2B-it-Q4_K_M.gguf; df -k ~ | tail -1
EOS
    echo DL_FAIL; exit 1
  fi
  [ $i -lt 9 ] && sleep 600
done
echo DL_TIMEOUT
