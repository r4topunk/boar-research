| model                          |       size |     params | backend    | threads | dev          |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | ------------ | --------------: | -------------------: |
| qwen35 9B PTQ1_0 - 1.75 bpw ternary (group 128) |   1.85 GiB |     8.95 B | MTL,BLAS   |       8 | none         |           pp512 |         78.57 ± 0.45 |
| qwen35 9B PTQ1_0 - 1.75 bpw ternary (group 128) |   1.85 GiB |     8.95 B | MTL,BLAS   |       8 | none         |            tg64 |         15.94 ± 0.43 |

build: e3de71522 (10777)
