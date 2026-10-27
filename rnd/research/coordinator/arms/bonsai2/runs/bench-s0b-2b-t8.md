| model                          |       size |     params | backend    | threads | dev          |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | ------------ | --------------: | -------------------: |
| qwen35 2B PTQ1_0 - 1.75 bpw ternary (group 128) | 398.81 MiB |     1.88 B | MTL,BLAS   |       8 | none         |           pp512 |        317.37 ± 8.77 |
| qwen35 2B PTQ1_0 - 1.75 bpw ternary (group 128) | 398.81 MiB |     1.88 B | MTL,BLAS   |       8 | none         |            tg64 |         59.19 ± 2.59 |

build: e3de71522 (10777)
