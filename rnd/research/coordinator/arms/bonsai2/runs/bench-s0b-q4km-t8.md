| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| qwen3 4B Q4_K - Medium         |   2.32 GiB |     4.02 B | BLAS       |       8 |           pp512 |        114.61 ± 7.14 |
| qwen3 4B Q4_K - Medium         |   2.32 GiB |     4.02 B | BLAS       |       8 |            tg64 |         32.25 ± 0.28 |

build: 4bc272f (1)
