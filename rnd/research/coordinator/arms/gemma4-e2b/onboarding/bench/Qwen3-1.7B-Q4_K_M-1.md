| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| qwen3 1.7B Q4_K - Medium       |   1.03 GiB |     1.72 B | BLAS       |       4 |           pp512 |        120.89 ± 1.91 |
| qwen3 1.7B Q4_K - Medium       |   1.03 GiB |     1.72 B | BLAS       |       4 |           tg128 |         30.29 ± 0.66 |

build: 4bc272f (1)
