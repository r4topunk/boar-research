## 8-4b-std-t10: <runner>/spikes/llama-b11010/build-cpu/bin/llama-bench -m <runner>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf -t 10 -ngl 0
| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| qwen3 4B Q4_K - Medium         |   2.32 GiB |     4.02 B | BLAS       |      10 |           pp512 |        127.41 ± 1.97 |
| qwen3 4B Q4_K - Medium         |   2.32 GiB |     4.02 B | BLAS       |      10 |            tg64 |         27.02 ± 1.51 |

build: 4bc272f (1)
