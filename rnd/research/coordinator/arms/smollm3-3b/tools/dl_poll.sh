#!/bin/bash
# SMOLLM3-3B onboarding: download the bartowski Q4_K_M to the mini only when free disk after the download stays >= 25 GiB and no other
# GGUF download is in flight (checked right before the download). Polls every 10 min, up to 90 min. Prints DL_OK / DL_TIMEOUT / DL_FAIL.
SIZE=1915305792; N=HuggingFaceTB_SmolLM3-3B-Q4_K_M.gguf; F=<runner>/shared-models/lite/$N.part
URL=https://huggingface.co/bartowski/HuggingFaceTB_SmolLM3-3B-GGUF/resolve/86b3536ed1ca0dcb4716745642db4e6804bf3d32/$N
for i in $(seq 0 9); do
  r=$(<on the mini> bash -s <<EOS
free=\$(df -k ~ | awk 'NR==2{print \$4*1024}'); have=\$(stat -f %z $F 2>/dev/null || echo 0); other=\$(pgrep -f 'curl.*gguf|hf download|huggingface-cli' | wc -l | tr -d ' '); echo \$free \$have \$other
EOS
)
  set -- $r; [ $# = 3 ] || { echo "bad probe: $r"; sleep 600; continue; }
  after=$(( $1 - (SIZE - $2) )); echo "$(date +%T) free=$1 have=$2 other_dl=$3 after=$after need=$((25*1024*1024*1024))"
  if [ "$3" = 0 ] && [ $after -ge $((25*1024*1024*1024)) ]; then
    <on the mini> bash -s <<EOS && { echo DL_OK; exit 0; }
set -e; cd <runner>/shared-models/lite; curl -sSL --fail -C - -o $N.part $URL; mv $N.part $N; shasum -a 256 $N; df -k ~ | tail -1
EOS
    echo DL_FAIL; exit 1
  fi
  [ $i -lt 9 ] && sleep 600
done
echo DL_TIMEOUT
