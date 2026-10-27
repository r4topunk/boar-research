#!/bin/bash
# GEMMATHINK: on the mini, delete the Qwen3.6-35B GGUF (disk rule), download the Gemma 4 26B-A4B GGUF, verify sha. Prints sizes/sha/free only.
# Usage: getmodel.sh   (refuses if a MoE llama-server is running)
set -u; H=MINI_HOST
ssh -T -n $H 'bash -c "
M=<runner>/shared-models; Q=\$M/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf; G=\$M/gemma-4-26B-A4B-it-UD-Q2_K_XL.gguf
if pgrep -fl \"llama-server.*(Qwen3.6-35B|gemma-4-26B)\" >/dev/null; then echo REFUSE-server-running; exit 1; fi
echo free_before \$(df -g ~ | awk \"NR==2{print \\\$4}\") GiB
[ -f \$Q ] && { rm -f \$Q; echo \"deleted Qwen3.6-35B GGUF \$(date +%F\\ %H:%M)\"; }
echo free_mid \$(df -g ~ | awk \"NR==2{print \\\$4}\") GiB
[ -f \$G ] || /usr/bin/curl -sSL --retry 3 -A \"curl/8\" -o \$G https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF/resolve/main/gemma-4-26B-A4B-it-UD-Q2_K_XL.gguf
ls -l \$G | awk \"{print \\\$5}\"; shasum -a 256 \$G | cut -c1-16; echo free_after \$(df -g ~ | awk \"NR==2{print \\\$4}\") GiB; sysctl -n vm.swapusage"'
