## 9-4b-std-t8-fa1: <runner>/spikes/llama-b11010/build-cpu/bin/llama-bench -m <runner>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf -t 8 -ngl 0 -fa 1
| model                          |       size |     params | backend    | threads |  fa |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --: | --------------: | -------------------: |
| qwen3 4B Q4_K - Medium         |   2.32 GiB |     4.02 B | BLAS       |       8 |   1 |           pp512 |        120.50 ± 6.43 |
| qwen3 4B Q4_K - Medium         |   2.32 GiB |     4.02 B | BLAS       |       8 |   1 |            tg64 |         36.68 ± 0.32 |

build: 4bc272f (1)
