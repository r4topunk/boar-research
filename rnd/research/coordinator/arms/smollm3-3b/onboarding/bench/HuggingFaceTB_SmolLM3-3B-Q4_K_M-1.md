| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| smollm3 3B Q4_K - Medium       |   1.78 GiB |     3.08 B | BLAS       |       4 |           pp512 |         94.29 ± 1.21 |
| smollm3 3B Q4_K - Medium       |   1.78 GiB |     3.08 B | BLAS       |       4 |           tg128 |         32.88 ± 0.26 |

build: 4bc272f (1)
