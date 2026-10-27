# MOESCREEN: Qwen3.5-35B-A3B UD-Q2_K_XL closed-book, v0.1 EN 57, judge.v1 (Kiln, 2026-10-07 00:11–03:55)
**TL;DR: NO.** Ratio **0.603** (CI 0.548–0.659). Paired Δ vs the 4B closed-book (0.487) is **+0.116** (CI +0.073…+0.161; bar +0.05 met). Paired Δ vs deep35 closed-book (0.596, Addendum 1 run) is **+0.007** (CI −0.028…+0.044; bar +0.03 not met). Qwen3.5 knows about what Qwen3.6 knows.
Criterion `MOESCREEN-criterion.md`: sha256 `a3667f51…` before the runs; Addendum 1 (deep35 closed-book comparator) is `386e983c…`. Dev only (v0.1 public). No blind/, v0.2, V-para. 1 seed, no rescue, no detector port.
## Comparators (ORACLE TABLE = `anvil/exp/oracle/README.md`)
- **4B closed-book row** (0.487): `anvil/exp/outofkit/runs/srv-qwen3-4b.{traces,judgments}.jsonl`, judge.v1 (Opus 5.5, no effort flag), refs `bd235bb9811f`, questions `568b3ececd8a`, seed 7. Reproduced 0.487 (10/30/17) with `ratio.py`.
- **deep35 closed-book row:** absent from the table (deep35 was only measured via the engine 0.565 and R450 0.634), so it was run per Addendum 1. Same protocol and runner, `Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf` sha `96b9c0af…` (kept on the mini). Outputs `moescreen-deep35-v01-s42.*`, traces sha `658131e9…`; 114 judge calls, [usage detail removed].
## Settings and deviations
- Model: unsloth `Qwen3.5-35B-A3B-UD-Q2_K_XL.gguf`, 12,156,754,560 B, sha256 `855b8d11…` (= HF lfs oid). Server: llama-server b11010 (`0.4.1-dev`, 4bc272f), same binary as DEEPREAD, under `<runner>/bin/run-heavy`.
- **Deviation:** the criterion's fallback said "DEEPREAD R450 minus the context". I used the **4B closed-book row's protocol** instead, so the only paired comparison stays clean: anchor.v1 system prompt (sha `ea2f484e`), bare question, max_tokens 450, 0.7/40/0.95/0.05, seed 42, `enable_thinking=false`, `-t 4 -c 4096 -np 1 --jinja --no-webui`. R450-minus-context would have changed the prompt, the "2-3 sentences" suffix and max 512 vs the 4B row.
- Runner `moescreen-anchors.py` (sha `ed1decad…`) = server-anchors.py plus instrumentation only (random port, ps RSS every 250 ms, prefill tok/s, finish_reason, reasoning chars).
## Gates (frozen)
| gate | bar | result |
|---|---|---|
| free disk after download | ≥ 25 GiB | 26.3 GiB (27,558,924 KiB) PASS |
| model loads (qwen35moe on b11010) | loads | yes, /health in 14.1 s PASS |
| smoke decode, 3 items | ≥ 5 tok/s | 10.94 / 11.45 / 11.35 PASS |
| thinking/hidden tokens | 0 | 0 `<think>`, 0 reasoning_content (smoke and all 57) PASS |
| non-empty answers | 3/3 | 3/3 (57/57 in the full run) PASS |
| peak RSS | ≤ 13 GB | 8,225 MB smoke; 8,084 MB full run PASS |

## Speed (Mac mini M4 CPU x4; desktop numbers, contended)
- The mini was **not idle**: `smbd` at 750–890 % CPU throughout (not ours, left alone), load 11–14, swap 2.9 of 4 GB used. These speeds reflect the contention and do not rank the model.
- Decode fell from 10.5 to 3.4 tok/s over the run: median **4.66**, aggregate 5.09. Prefill median 5.75, aggregate 6.11 (DEEPREAD: 18.6).
- Per item median 77.7 s, 76 min wall for 57. Tokens in / out median 142 / 276; 2 answers hit the 450 cap (vit-cry-001, vit-cry-009).
- RSS 6,361 MB idle, peak 8,084 MB; it fell to about 4.8 GB late in the run (page-cache eviction of the mmap'd file).

## Quality (judge-core summarize, both orders combined; `analysis-q35-vs-4b.json`)
| system | ratio (95% CI) | floor-adj (CI) | win / tie / loss | pass / cw / fail | C / Cm / U |
|---|---|---|---|---|---|
| **Qwen3.5-35B-A3B closed** | **0.603 (0.548–0.659)** | 0.501 (0.431–0.568) | 1.8 / 1.8 / 96.5 % | 17 / 25 / 15 | 2.79 / 3.17 / 2.90 |
| Qwen3-4B closed (ORACLE row) | 0.487 (0.433–0.541) | 0.357 (0.286–0.421) | 0 / 0 / 100 % | 10 / 30 / 17 | 2.44 / 2.45 / 2.32 |
| deep35 Qwen3.6-35B-A3B closed (Add. 1) | 0.596 (0.540–0.648) | 0.492 (0.424–0.562) | 0 / 3.5 / 96.5 % | 15 / 27 / 15 | 2.72 / 3.18 / 2.87 |

**Paired vs 4B, n = 57** (2000 joint boots): Δratio **+0.116** (CI +0.073…+0.161); Δfloor-adj **+0.145** (+0.090…+0.203); better 40 / worse 7 / equal 10; converted 1 (lan-cmp-002), regressed 0. Median length 202 vs 177 words.
**Paired vs deep35 closed** (`analysis-q35-vs-deep35.json`): Δratio **+0.007** (CI −0.028…+0.044); Δfloor-adj +0.009 (−0.032…+0.057); better 20 / worse 23 / equal 14; converted 0, regressed 0. deep35 vs 4B: +0.108 (+0.069…+0.149).
Non-paired references: Haiku no-web 0.653; Qwen3.5-9B closed 0.488; deep35 engine 0.565.

## Verdict (frozen rule)
GO needs Δ vs deep35 closed-book ≥ +0.03 (**+0.007, not met**) AND Δ vs 4B ≥ +0.05 (**+0.116, met**). **Verdict: NO**: Qwen3.5-35B-A3B does not become the deep-tier candidate. Most of the +0.116 over the 4B is MoE-35B-class knowledge that deep35 already has.

## Judge
114/114 calls, judge.v1 / claude-opus-5-5, refs bd235bb9, seed 7, `--gap-ms 1000`; 0 errors, 0 rate limits, 17.7 min, [usage detail removed] ([usage detail removed]).

## Files
- `boar-eval/runs/kiln/moescreen/moescreen-q35-v01-s42.{traces.jsonl (sha c38babfb…),judgments.jsonl,log,server.log}`, `judge-moescreen-q35.log`, `smoke-q35.*`.
- Here: `moescreen-anchors.py`, `analyze.mjs` (DEEPREAD's, relabelled), `analysis-q35-vs-4b.json`. GGUF deleted from the mini at 01:58 (MODELS.md, DISK-LOG.md).

## UNKNOWN
- deep35 closed-book ran on the same contended mini (decode median 7.28 tok/s, peak RSS 9,893 MB, 53 min). Speed is not comparable across the three runs.
- Speed on an idle mini or a phone (contended: 3.4–11 tok/s). Seed noise: 1 seed, noise floor about 0.05, Δ CI lower bound +0.073.
