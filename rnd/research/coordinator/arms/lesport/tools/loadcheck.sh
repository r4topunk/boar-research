#!/bin/bash
# usage: loadcheck.sh <tag> <extra args...>
tag=$1; shift
R=$HOME/boar/kiln/lesport-raw; mkdir -p $R
export PATH=/opt/homebrew/bin:$PATH
F=$HOME/boar/spikes/llama-omni/src/build-cpu/bin/llama-completion
P=$(cat $HOME/boar/kiln/deepspeed/prompts/00-lan-exp-001.rendered.txt)
/usr/bin/time -l perl -e 'alarm 150; exec @ARGV' $F -m $HOME/boar/shared-models/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf "$@" -p "$P" -n 8 -c 4096 -t 4 --temp 0 -no-cnv > $R/$tag.out 2> $R/$tag.err
echo rc=$?
grep -i -E "error|moe|expert|fail|abort|unsupported|arch" $R/$tag.err | head -20
tail -14 $R/$tag.err
