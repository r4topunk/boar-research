## 2-9b-prism-t10: <runner>/spikes/llama-prism/bin/llama-bench -m <runner>/shared-models/bonsai2/Ternary-Bonsai-2-9B-PTQ1_0.gguf -t 10 -ngl 0 -dev none
| model                          |       size |     params | backend    | threads | dev          |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | ------------ | --------------: | -------------------: |
| qwen35 9B PTQ1_0 - 1.75 bpw ternary (group 128) |   1.85 GiB |     8.95 B | MTL,BLAS   |      10 | none         |           pp512 |         79.87 ± 1.20 |
| qwen35 9B PTQ1_0 - 1.75 bpw ternary (group 128) |   1.85 GiB |     8.95 B | MTL,BLAS   |      10 | none         |            tg64 |         13.40 ± 0.52 |

build: e3de71522 (10777)
