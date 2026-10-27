#!/bin/bash
# CHATFAIL S1: llama-server b11010 for one model on port 8191 (usage: chatfail-server.sh m4|m1). Flags = the desktop-node adapter's server backend.
case "$1" in m4) M=$HOME/boar/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf;; m1) M=$HOME/boar/shared-models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf;; *) exit 2;; esac
exec $HOME/boar/spikes/llama-b11010/build-cpu/bin/llama-server -m "$M" -t 4 -tb 4 -c 4096 -ngl 0 -np 1 --jinja --no-webui --cache-ram 0 --host 127.0.0.1 --port 8191
