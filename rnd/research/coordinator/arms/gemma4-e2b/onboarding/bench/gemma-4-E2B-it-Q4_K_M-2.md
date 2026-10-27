| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| gemma4 E2B Q4_K - Medium       |   2.88 GiB |     4.65 B | BLAS       |       4 |           pp512 |         83.47 ± 1.04 |
| gemma4 E2B Q4_K - Medium       |   2.88 GiB |     4.65 B | BLAS       |       4 |           tg128 |         17.18 ± 0.20 |

build: 4bc272f (1)
