| model                          |       size |     params | backend    | threads | dev          |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | ------------ | --------------: | -------------------: |
| qwen35 4B PTQ1_0 - 1.75 bpw ternary (group 128) | 895.04 MiB |     4.21 B | MTL,BLAS   |       8 | none         |           pp512 |        130.15 ± 0.12 |
| qwen35 4B PTQ1_0 - 1.75 bpw ternary (group 128) | 895.04 MiB |     4.21 B | MTL,BLAS   |       8 | none         |            tg64 |         27.40 ± 0.16 |

build: e3de71522 (10777)
