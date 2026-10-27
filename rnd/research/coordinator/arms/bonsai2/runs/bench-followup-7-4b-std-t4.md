## 7-4b-std-t4: <runner>/spikes/llama-b11010/build-cpu/bin/llama-bench -m <runner>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf -t 4 -ngl 0
| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| qwen3 4B Q4_K - Medium         |   2.32 GiB |     4.02 B | BLAS       |       4 |           pp512 |         88.47 ± 2.36 |
| qwen3 4B Q4_K - Medium         |   2.32 GiB |     4.02 B | BLAS       |       4 |            tg64 |         27.31 ± 0.15 |

build: 4bc272f (1)
