## 4-9b-kleidi-t8: <runner>/spikes/llama-prism-kleidi/x/llama-prism-b10777-e3de715/llama-bench -m <runner>/shared-models/bonsai2/Ternary-Bonsai-2-9B-PTQ1_0.gguf -t 8 -ngl 0 -dev none
| model                          |       size |     params | backend    | threads | dev          |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | ------------ | --------------: | -------------------: |
| qwen35 9B PTQ1_0 - 1.75 bpw ternary (group 128) |   1.85 GiB |     8.95 B | MTL,BLAS   |       8 | none         |           pp512 |         80.64 ± 1.20 |
| qwen35 9B PTQ1_0 - 1.75 bpw ternary (group 128) |   1.85 GiB |     8.95 B | MTL,BLAS   |       8 | none         |            tg64 |         13.05 ± 1.48 |

build: e3de71522 (10777)
