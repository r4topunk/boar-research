| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| qwen3 1.7B Q4_K - Medium       |   1.03 GiB |     1.72 B | BLAS       |       4 |           pp512 |        178.53 ± 1.05 |
| qwen3 1.7B Q4_K - Medium       |   1.03 GiB |     1.72 B | BLAS       |       4 |           tg128 |         53.68 ± 2.96 |

build: 4bc272f (1)
