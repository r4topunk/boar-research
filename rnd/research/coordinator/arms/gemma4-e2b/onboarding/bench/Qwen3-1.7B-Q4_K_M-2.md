| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| qwen3 1.7B Q4_K - Medium       |   1.03 GiB |     1.72 B | BLAS       |       4 |           pp512 |        117.10 ± 0.78 |
| qwen3 1.7B Q4_K - Medium       |   1.03 GiB |     1.72 B | BLAS       |       4 |           tg128 |         28.27 ± 2.91 |

build: 4bc272f (1)
