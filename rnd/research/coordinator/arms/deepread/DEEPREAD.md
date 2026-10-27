# DEEPREAD: deep35 as a reader with gold passages (R450), v0.1 EN 57, judge.v1

**TL;DR: INCONCLUSIVE.** deep35 R450 = **0.634** (CI 0.590–0.683), inside the 0.606 ≤ x < 0.660 band. The paired gain over the 4B on the same contexts is **+0.029** (CI −0.004…+0.063), half of the engine-level +0.06. By the frozen rule, deep35 reads like the 4B: its +0.06 is knowledge. The hybrid tier is still worth it for knowledge, packs are not.

Criterion: `DEEPREAD-criterion.md`, sha256 `07d830dc29b39743…` (checked before the run, unchanged). Kiln, 2026-10-06 17:22–18:31. Dev only (v0.1 public). No blind/, no V-para. One seed, one run, no restart.

## Verdict (frozen rule, applied by the letter)
| rule | value | result |
|---|---|---|
| ≥ 0.660 → GO | 0.6345 | no |
| 0.606 ≤ x < 0.660 → INCONCLUSIVE | 0.6345 | **yes** |
| < 0.606 → NO | — | no |

**INCONCLUSIVE.** Per the criterion: "reads like the 4B; the +0.06 is knowledge only; hybrid still worth it for knowledge, packs are not."

## Results (judge-core `summarize()` on combined orders; floor-adjusted = Σ(S−1)/Σ(S_ref−1))
| system | ratio (95% CI) | win / tie / loss | rubric C / Cm / U | floor-adj (CI) | position consistency |
|---|---|---|---|---|---|
| **deep35 R450** | **0.634 (0.590–0.683)** | 1.8% / 5.3% / 93.0% | 3.89 / 2.66 / 2.78 | 0.541 (0.479–0.597) | 96.5% |
| 4B R450 (Anvil, 2026-10-03) | 0.606 (0.558–0.658) | 1.8% / 3.5% / 94.7% | 3.58 / 2.58 / 2.76 | 0.505 (0.440–0.567) | 98.2% |

(C / Cm / U = correctness / completeness / usefulness. Ref rubric is the same for both: 4.83 / 4.93 / 4.96.) I reran the 4B number with the same script and got 0.6057, which matches the README.

**Paired, n = 57, same contexts, items resampled jointly (2000 boots):**
- Δratio **+0.029** (CI −0.004…+0.063).
- Δfloor-adj +0.036 (CI −0.004…+0.080).
- Per item: deep better on 26, worse on 18, equal on 13. Mean S is 3.11 vs 2.97.
- Most of the gain is correctness (+0.32). Completeness and usefulness barely move.
- Weak answers (S ≤ 2) fall from 11 to 5, but strong answers (S ≥ 4) stay flat at 12 vs 13. deep35 cuts bad reads more than it adds good ones.

**Converted** (deep ≥ 4 and 4B ≤ 2): 1 item.
| id | 4B S | deep S | winner 4B → deep |
|---|---|---|---|
| lan-cmp-003 | 1.83 | 4.67 | ref → tie |

**Regressed** (4B ≥ 4 and deep ≤ 2): **0 items.**

Largest moves, for reference:
- Up: lan-exp-002, vit-hum-006, trv-004 (+1.33 each); vit-trv-004 (+1.17); dng-005 (+1.0).
- Down: lan-cmp-004 (−1.0); vit-hum-004 and vit-cry-002 (−0.83 each).

The full per-item table is in `analysis.json` → `perItem`.

## Speed and memory (Mac mini CPU, 4 threads, llama-server; desktop numbers, not phone numbers)
| metric | value |
|---|---|
| decode tok/s | median **9.43**; aggregate 9.70 |
| prefill tok/s | median **18.6**; aggregate 18.5 |
| prompt / output tokens (median) | 765 / 72 |
| ttft (= prefill) median / total median per item | 41.1 s / 48.7 s; 46 min wall for 57 items |
| llama-server RSS | idle after load 6,583 MB; **peak 8,435 MB** (`ps` RSS every 250 ms) |
| model load (to /health 200) | 14.8 s, page cache warm |
| hidden reasoning tokens / empty answers / errors | 0 / 0 / 0. All 57 finished with `stop`; no `<think>` leaked. |

The 4B R450 run did not record tok/s (node-llama-cpp, `timing` nulls). On the MacBook its wall time was about 9–15 s per item.

## Settings, and deviations from the 4B R450 run
| | 4B R450 (Anvil) | deep35 R450 (this run) |
|---|---|---|
| contexts | `anvil/exp/oracle/ctx-R450.jsonl` | **same file, reused** (sha256 `ad73972b…`) |
| prompt | gen_oracle.mts | same logic, ported to `build_msgs.mjs` |
| sampler | 0.7 / 40 / 0.95 / 0.05, seed 42, max 512 tokens | same |
| context size | 4096 | `-c 4096` |
| thinking | n/a (Instruct-2507) | off: `chat_template_kwargs.enable_thinking=false`, `--reasoning-format deepseek`; 0 hidden tokens |
| model | Qwen3-4B-Instruct-2507 Q4_K_M | Qwen3.6-35B-A3B UD-Q2_K_XL, sha `96b9c0af…` (verified on the mini) |
| **backend** | **node-llama-cpp 3.21.1, CPU x4, MacBook** | **llama-server b11010 build (`--version`: 0.4.1-dev, commit 4bc272f), CPU, Mac mini, heavy lock** |
| server flags | — | `-t 4 -tb 4 -c 4096 -ngl 0 -np 1 --jinja --no-webui --cache-ram 0 --reasoning-format deepseek`, `cache_prompt:false` (same as desktop-node `--backend server`) |
| judge | judge.v1 (Opus), both orders, bench/v0.1 refs `bd235bb9811f`, questions `568b3ececd8a`, seed 7, gap 5000 ms | same; `--system oracle-R450-deep35` |

**Context identity:**
- I reused the stored contexts file. Its mtime (10-03 16:43) is before the 4B run started (16:54).
- For all 57 items, the passages in it match the 4B traces' `retrieval.kept`: same titles, same sims, same order, 0 mismatches.
- The question text matches too.
- So both readers saw the same contexts.

**Backend deviation:**
- The 4B ran on node-llama-cpp; this run uses llama-server, so the sampler chains differ.
- At temperature 0.7, that part of Δ is not separable from the model. This is the documented "not comparable across backends at temp > 0" caveat.
- With one seed, the paired CI already spans 0.
- Each backend applied its own chat template (node-llama-cpp's Qwen wrapper vs the GGUF jinja template).

## Caveats
- Dev, 1 seed. The README's noise floor is about 0.05. The 0.634 sits 0.026 below the GO bar, and its CI reaches 0.683.
- R450 is an upper bound: the passages were picked using the reference answer.
- No engine post-processing on either side, same as the oracle table.

## Judge spend
- 114 calls, 0 rate limits, 0 errors. All 114 rows are judge.v1 / claude-opus-5-5.

## Files (all in this folder)
- `requests.jsonl` (sha256 `f9c0b3ed…`): the 57 chat requests.
- `build_msgs.mjs`: prompt builder plus the 4B context check.
- `gen_server.py`: llama-server client with the RSS sampler.
- `gen-run.log`, `deep35-R450.traces.server.log`: logs. Mini copy: `<runner>/kiln/deepread/`.
- `deep35-R450.traces.jsonl`, `deep35-R450.judgments.jsonl`, `judge-deep35-R450.log`: traces, judgments, judge log.
- `analyze.mjs` → `analysis.json`: summarize, floor-adjusted ratio, paired bootstrap, per-item table, speed.
- 4B comparator: `rnd/research/anvil/exp/oracle/runs/qwen3-4b-R450.{traces,judgments}.jsonl`.
