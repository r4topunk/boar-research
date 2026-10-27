| model                          |       size |     params | backend    | threads | dev          |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | ------------ | --------------: | -------------------: |
| qwen35 2B PTQ1_0 - 1.75 bpw ternary (group 128) | 398.81 MiB |     1.88 B | MTL,BLAS   |       4 | none         |           pp512 |       390.22 ± 10.91 |
| qwen35 2B PTQ1_0 - 1.75 bpw ternary (group 128) | 398.81 MiB |     1.88 B | MTL,BLAS   |       4 | none         |            tg64 |         48.55 ± 0.01 |

build: e3de71522 (10777)
