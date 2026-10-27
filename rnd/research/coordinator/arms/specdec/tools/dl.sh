# SPECDEC: download Qwen3-0.6B GGUF from the official Qwen HF org (run on the mini via: <on the mini> bash -s < dl.sh)
set -eu
D=<runner>/kiln/specdec; mkdir -p $D; cd $D
curl -sfL "https://huggingface.co/api/models/Qwen/Qwen3-0.6B-GGUF/tree/main" -o tree.json
python3 -c "
import json
for f in json.load(open('tree.json')): print(f['path'], f.get('size'), (f.get('lfs') or {}).get('oid'))"
set -eu
cd <runner>/kiln/specdec
nice -n 19 curl -sfL "https://huggingface.co/Qwen/Qwen3-0.6B-GGUF/resolve/main/Qwen3-0.6B-Q8_0.gguf" -o Qwen3-0.6B-Q8_0.gguf
ls -l Qwen3-0.6B-Q8_0.gguf; shasum -a 256 Qwen3-0.6B-Q8_0.gguf
shasum -a 256 <runner>/shared-models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf <runner>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf; ls -l <runner>/shared-models/*.gguf; df -g ~ | tail -1
