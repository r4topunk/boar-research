## 10-4b-kleidi-t8: <runner>/spikes/llama-prism-kleidi/x/llama-prism-b10777-e3de715/llama-bench -m <runner>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf -t 8 -ngl 0 -dev none
| model                          |       size |     params | backend    | threads | dev          |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | ------------ | --------------: | -------------------: |
| qwen3 4B Q4_K - Medium         |   2.32 GiB |     4.02 B | MTL,BLAS   |       8 | none         |           pp512 |        134.05 ± 0.04 |
| qwen3 4B Q4_K - Medium         |   2.32 GiB |     4.02 B | MTL,BLAS   |       8 | none         |            tg64 |         31.11 ± 0.07 |

build: e3de71522 (10777)
