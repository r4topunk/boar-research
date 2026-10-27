| time | what | Haiku calls | running total |
|---|---|---|---|
| 23:19-23:55 | data dump, embeddings (local llama-servers), head training, reads 1-4, MAIN 97 replays (MacBook), 0 LLM | 0 | 0 |
Total 0 of 200: v3c NOT ACCEPTED (reads 1 and 3 fail), so the 65-probe safety generation and the Haiku screen were not run.
| 00:12-00:45 (10-23) | DETECTOR-FT: v3d-ft fine-tune (mini MPS), embeddings (mini b11010 servers), reads, parity gate, canary, MAIN 97 replay (MacBook), 0 LLM | 0 | 0 |
Total DETECTOR-FT 0 of 200: v3d-ft NOT ACCEPTED (recall, probe routing, parity fail), so the 65-probe safety generation and the Haiku screen were not run.
| 00:47-01:20 (10-23) | DETECTOR-FT2: 4 fine-tune runs (mini MPS), HF screen of 12 checkpoints, one GGUF export + reads (mini b11010 servers via tunnel), 0 LLM | 0 | 0 |
Total DETECTOR-FT2 0 of 200: no checkpoint met the recall constraint, so the safety generation and the Haiku screen were not run.
