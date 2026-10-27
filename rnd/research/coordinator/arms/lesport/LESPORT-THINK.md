# LESPORT-THINK: does the LES fork run Qwen3.6-35B in thinking mode with the 512 budget respected? Verdict: **SEEN** (mechanism only, no quality claim)
Runner Kiln, 2026-10-16 (mini M4, CPU, 0 judge/LLM/API calls, ~25 min wall). Same GGUF (sha 96b9c0af…), fork `llama-omni` 0b74404c, `--moe-experts experts --moe-slot-bank 1280 --no-mmap -t 4 -c 4096`, `LLAMA_MOE_LOOKAHEAD_PREFETCH=1`, sampler 0.7/40/0.95/0.05 seed 42. 10 DEEPPAR prompts (`deepspeed/prompts`, items 00-09).

**Rendering recipe (thinking ON):** the 10 no-think strings end in `<|im_start|>assistant\n<think>\n\n</think>\n\n`; I replaced that tail with `<think>\n`. Verified: llama-server b11010 `/apply-template` (default, no kwarg = what DEEPTHINK sent via /v1/chat) on the parsed system+user messages is byte-identical to the replaced string on 10/10 (`apply_template_match`). DEEPTHINK itself used /v1/chat/completions with `thinking_budget_tokens` + the app message (`server.ts`), so no template kwarg.

**How the budget is enforced (engine):** server-side sampler (`thinking_budget_tokens` + message "\nI have thought enough; answering now.\n", max tokens = nPredict + budget), not an app-side cut. The fork carries the same `common/reasoning-budget.cpp` and exposes `--reasoning-budget N` / `--reasoning-budget-message`, but **only `llama-cli` (jinja chat path) wires it**. `llama-completion` (the L1 binary) accepts the flag and ignores it: smoke on item 00, `-n 1024 --reasoning-budget 512` -> 1023 tokens, no `</think>`, no answer (`out/smokeB-00.*`). So the thinking probe ran through `llama-cli --jinja -st --simple-io --reasoning on --reasoning-format none --reasoning-budget 512 --reasoning-budget-message <app text> -n 712 -sys <system> -p <user>` (712 = nPredict 200 + 512), one process per item. Caveat: cli renders the template itself from the split messages; its prompt tokens are not checked token-by-token against the string (prefill uses the server-tokenized count of the replaced string, 597-677 tokens).

| config | think block 10/10 | median reasoning tok (max) | closed by budget | answer non-empty | median answer tok | median decode tok/s | prefill s | RSS GiB (footprint) |
|---|---|---|---|---|---|---|---|---|
| LES fork, llama-cli, budget 512, -n 712 | 10/10 | 516 (516) | 10/10 forced | 10/10 | 72.5 | 16.3 (16.1-16.6) | 17.5 (16.8-18.7) | 2.94 (2.91) |
| server-think control: llama-server b11010 CPU, no budget, max_tokens 1024 | 10/10 open | >=1024 on 7/10 (714, 654, 829 closed by themselves) | n/a | 3/10 (7/10 hit 1024 mid-think) | 94/42/46 on the 3 | 22.6 (22.5-22.8) | 14.3 | n/a (earlier controls ≈ 7.9) |

Reasoning tokens = re-tokenized text before the forced message (512 + ≤4 from retokenization). Per item in `items.csv` (configs `les-think`, `server-think`; footprint is the fork's GiB).

**Reading**
- Thinking works on the fork: 10/10 produce a reasoning block (output starts "Here's a thinking process:", the `<think>` is in the prompt), the end tag is forced at 512 on 10/10 (message visible, then the answer), 10/10 non-empty answers, 35-113 tokens (DT512 answers 91-95).
- The budget would bind on 10/10 here (natural reasoning is 654-1024+ tokens; unbudgeted 7/10 do not finish in 1024). DT512 saw 82-90 % hits on V-para, so this slice is on the heavy side.
- Cost at 512: ≈ 56 s per item wall incl. model load (≈ 17.5 prefill + 31.4 reasoning + 4.4 answer decode + load), RSS 2.9 GiB, vs 7.9 GiB for the server control. The server's 22.6 tok/s here is warm mmap, not the 9.4 of L1's control; it is not like for like with the fork's one-process-per-item run.
- Not claimed: quality of fork-thinking answers (no judge), parity with DT512 numbers, phone speed.
- Implication for a device plan: the engine must embed the `reasoning-budget` sampler on the chat path (cli does; `llama-completion` does not). If the app drives `llama-completion`-style raw prompts, it needs an app-side cut at 512 tokens (force `</think>` + message) instead.

Files: `raw/think/out/` (cliB-NN.raw/err, ctl.results.jsonl, fork-analysis.json, smokeB-00.* = the completion no-budget smoke), `tools/run_cli.py`, `run_think.py`, `ctl.py`, `analyze_think.py`. Mini: `<runner>/kiln/lesport-think/`. Not committed. Disk free 40 GiB, no engine left running.
