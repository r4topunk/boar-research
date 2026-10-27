| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| qwen3 4B Q4_K - Medium         |   2.32 GiB |     4.02 B | BLAS       |       8 |           pp512 |        126.16 ± 0.49 |
| qwen3 4B Q4_K - Medium         |   2.32 GiB |     4.02 B | BLAS       |       8 |            tg64 |         32.72 ± 2.25 |

build: 4bc272f (1)
