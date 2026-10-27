## 1-9b-prism-t4: <runner>/spikes/llama-prism/bin/llama-bench -m <runner>/shared-models/bonsai2/Ternary-Bonsai-2-9B-PTQ1_0.gguf -t 4 -ngl 0 -dev none
| model                          |       size |     params | backend    | threads | dev          |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | ------------ | --------------: | -------------------: |
| qwen35 9B PTQ1_0 - 1.75 bpw ternary (group 128) |   1.85 GiB |     8.95 B | MTL,BLAS   |       4 | none         |           pp512 |         87.03 ± 0.38 |
| qwen35 9B PTQ1_0 - 1.75 bpw ternary (group 128) |   1.85 GiB |     8.95 B | MTL,BLAS   |       4 | none         |            tg64 |         11.96 ± 0.13 |

build: e3de71522 (10777)
