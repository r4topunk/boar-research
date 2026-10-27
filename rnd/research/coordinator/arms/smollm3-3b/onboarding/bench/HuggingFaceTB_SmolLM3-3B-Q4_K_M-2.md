| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| smollm3 3B Q4_K - Medium       |   1.78 GiB |     3.08 B | BLAS       |       4 |           pp512 |         93.66 ± 0.81 |
| smollm3 3B Q4_K - Medium       |   1.78 GiB |     3.08 B | BLAS       |       4 |           tg128 |         32.47 ± 1.37 |

build: 4bc272f (1)
