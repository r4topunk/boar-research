#!/bin/bash
# DEEPFULL: on the mini, delete the Gemma 4 GGUF (GEMMATHINK ended NO), re-download the Qwen3.6-35B GGUF, verify sha. Sizes/sha/free only.
set -u; H=MINI_HOST
ssh -T -n $H 'bash -c "
M=<runner>/shared-models; Q=\$M/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf; G=\$M/gemma-4-26B-A4B-it-UD-Q2_K_XL.gguf
if pgrep -fl \"llama-server.*(Qwen3.6-35B|gemma-4-26B)\" >/dev/null; then echo REFUSE-server-running; exit 1; fi
echo free_before \$(df -g ~ | awk \"NR==2{print \\\$4}\") GiB
[ -f \$G ] && { rm -f \$G; echo \"deleted Gemma 4 26B GGUF \$(date +%F\\ %H:%M)\"; }
echo free_mid \$(df -g ~ | awk \"NR==2{print \\\$4}\") GiB
[ -f \$Q ] || /usr/bin/curl -sSL --retry 3 -A \"curl/8\" -o \$Q https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF/resolve/a483e9e6cb/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf
ls -l \$Q | awk \"{print \\\$5}\"; shasum -a 256 \$Q | cut -c1-16; echo free_after \$(df -g ~ | awk \"NR==2{print \\\$4}\") GiB; sysctl -n vm.swapusage; date +%F\\ %H:%M"'
