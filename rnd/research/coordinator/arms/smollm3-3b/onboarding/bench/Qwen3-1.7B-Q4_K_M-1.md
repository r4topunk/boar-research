| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| qwen3 1.7B Q4_K - Medium       |   1.03 GiB |     1.72 B | BLAS       |       4 |           pp512 |        175.92 ± 3.09 |
| qwen3 1.7B Q4_K - Medium       |   1.03 GiB |     1.72 B | BLAS       |       4 |           tg128 |         56.35 ± 4.55 |

build: 4bc272f (1)
