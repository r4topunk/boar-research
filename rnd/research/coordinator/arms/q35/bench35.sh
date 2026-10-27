B=<runner>/spikes/llama-b11010/build-cpu/bin
uptime
for m in Qwen3.5-4B-Q4_K_M Qwen3-4B-Instruct-2507-Q4_K_M; do for r in 1 2; do $B/llama-bench -m <runner>/shared-models/$m.gguf -p 0 -n 64 -t 4 -r 3 2>&1 | grep -E "tg64|model"; done; done
uptime
