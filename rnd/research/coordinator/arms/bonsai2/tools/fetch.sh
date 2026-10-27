#!/bin/bash
# BONSAI2 S0: fetch PrismML llama.cpp fork (pinned release) + Ternary-Bonsai-2-9B PTQ1_0 on the mini.
S=<runner>/spikes/llama-prism/FETCH.status
echo "start $(date '+%F %T')" > $S
cd <runner>/spikes/llama-prism
T=llama-prism-b10777-e3de715-bin-macos-arm64.tar.gz
curl -sSL -o $T "https://github.com/PrismML-Eng/llama.cpp/releases/download/prism-b10777-e3de715/$T"; echo "bin_rc=$?" >> $S
shasum -a 256 $T >> $S
mkdir -p bin && tar -xzf $T -C bin --strip-components=1; echo "untar_rc=$?" >> $S
cd <runner>/shared-models/bonsai2
F=Ternary-Bonsai-2-9B-PTQ1_0.gguf
echo "dl9 start $(date '+%T')" >> $S
curl -sSL -A "Mozilla/5.0" -o $F.part "https://huggingface.co/prism-ml/Ternary-Bonsai-2-9B-gguf/resolve/5b2abb02362efbed46bbe204014b02837778b2c2/$F"; echo "dl9_rc=$?" >> $S
mv $F.part $F; stat -f %z $F >> $S; shasum -a 256 $F | tee -a SHA256SUMS >> $S
echo "end $(date '+%F %T')" >> $S; df -g ~ | tail -1 >> $S
