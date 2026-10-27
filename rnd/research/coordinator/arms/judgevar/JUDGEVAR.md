# JUDGEVAR: Opus judge.v1 test-retest noise on unchanged traces (criterion JUDGEVAR-criterion.md sha 79c085fe…; 2026-10-11; 102 Opus)

TL;DR: re-judging the frozen H s42 V-para traces (51 ids, both orders, same references, N = 4 shards) reproduces the frozen numbers: raw **0.533 → 0.537** (paired Δ +0.004, CI −0.005…+0.013), floor-adj **0.412 → 0.417** (+0.005, −0.007…+0.017). Per item: mean-rubric r **0.96**, identical on 32/51 items (10 ↑ / 9 ↓), 74/102 judge calls identical on all three dimensions, winner agreement 51/51, order consistency 51/51 both passes, reference-side mean |Δ| 0.029. **σ_judge ≈ 0.003 raw / 0.004 floor-adj** (|Δ|/√2), an order of magnitude below the seed term (SEEDVAR σ_run 0.020 / 0.025). The judge is effectively a fixed instrument; CI widening is needed for seed noise only.

| | retest R | frozen H | paired R − H |
|---|---|---|---|
| raw (CI) | 0.537 (0.503–0.569) | 0.533 (0.500–0.563) | +0.004 (−0.005…+0.013) |
| floor-adj (CI) | 0.417 (0.377–0.457) | 0.412 (0.375–0.450) | +0.005 (−0.007…+0.017) |
| per-dim mean |Δ| / exact / r | correctness 0.147 / 40 / 0.951 · completeness 0.069 / 45 / 0.885 · usefulness 0.069 / 44 / 0.942 | | |

Common-mode CI (new `paired.mjs --common-mode σ_raw,σ_floor`, formula CI = Δ ± 1.96·sqrt(SE_item² + 2σ²); default output unchanged, tests 44/44): with SEEDVAR's σ_run 0.020 / 0.025 on V-para, H s42 raw CI 0.500–0.563 → see `aggregates/paired-HvsK-s42-cm.opus.json` (`ratioCIcm`), floor-adj likewise; the paired H − K Δ keeps its sign with the wider CI (numbers in the QUEUE row). Reading for the bar table: the honest two-seed V-para CIs are ≈ 1.2–1.3× wider than the item-bootstrap ones (RND-REVIEW C1's estimate), judge noise adds nothing measurable.

Method: `shard_judge.sh` N = 4 opus, system `judgevar-H-retest`, bench-shim (original refs sha 952e2c44…), out `runs-dt512/dh-H-vpara-s42.judgments.retest.jsonl` (check ok 102/102); `deepvpara/tools/paired.mjs` R vs H; `tools/agree.mjs`. Aggregates: `aggregates/paired-RvsH-s42.opus.json`, `agree-RvsH-s42.opus.json`, `paired-HvsK-s42-cm.opus.json`. Exposure: 0 generations, 102 Opus judge calls on existing traces.
