| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| gemma4 E2B Q4_K - Medium       |   2.88 GiB |     4.65 B | BLAS       |       4 |           pp512 |       116.01 ± 10.12 |
| gemma4 E2B Q4_K - Medium       |   2.88 GiB |     4.65 B | BLAS       |       4 |           tg128 |         18.93 ± 2.65 |

build: 4bc272f (1)
