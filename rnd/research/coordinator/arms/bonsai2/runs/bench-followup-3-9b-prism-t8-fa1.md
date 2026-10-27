## 3-9b-prism-t8-fa1: <runner>/spikes/llama-prism/bin/llama-bench -m <runner>/shared-models/bonsai2/Ternary-Bonsai-2-9B-PTQ1_0.gguf -t 8 -ngl 0 -dev none -fa 1
| model                          |       size |     params | backend    | threads |  fa | dev          |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --: | ------------ | --------------: | -------------------: |
| qwen35 9B PTQ1_0 - 1.75 bpw ternary (group 128) |   1.85 GiB |     8.95 B | MTL,BLAS   |       8 |   1 | none         |           pp512 |         81.20 ± 0.41 |
| qwen35 9B PTQ1_0 - 1.75 bpw ternary (group 128) |   1.85 GiB |     8.95 B | MTL,BLAS   |       8 |   1 | none         |            tg64 |         15.78 ± 0.23 |

build: e3de71522 (10777)
