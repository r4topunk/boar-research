B=<runner>/spikes/llama-b11010/build-cpu/bin
echo BEFORE; uptime; sysctl vm.swapusage; vm_stat | grep -E "Pageouts|Swapouts|Swapins"; ps -axo %cpu=,comm= | sort -rn | head -3
for m in gemma-4-E4B-it-qat-Q4_0 Qwen3-4B-Instruct-2507-Q4_K_M gemma-4-E4B-it-qat-Q4_0 Qwen3-4B-Instruct-2507-Q4_K_M; do $B/llama-bench -m <runner>/shared-models/$m.gguf -p 0 -n 64 -t 4 -r 3 2>&1 | grep -E "tg64"; done
echo AFTER; uptime; sysctl vm.swapusage; vm_stat | grep -E "Pageouts|Swapouts|Swapins"
