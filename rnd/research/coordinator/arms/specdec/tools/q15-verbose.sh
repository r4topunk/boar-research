# SPECDEC: why is Qwen2.5-1.5B refused as draft? start the server once with -lv 4 (SPC_DBG lines), kill that pid after 15 s. Run on the mini inside heavy.
cd <runner>/kiln/specdec
<runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m <runner>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf -md <runner>/shared-models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf --spec-type draft-simple -ngl 0 -np 1 -c 512 -lv 4 --host 127.0.0.1 --port 8188 > res_c/q15-verbose.log 2>&1 &
P=$!; sleep 15; kill $P; wait $P 2>/dev/null; echo stopped
