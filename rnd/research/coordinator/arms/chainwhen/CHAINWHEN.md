# CHAINWHEN (2026-10-19/20): one chained 4B G3 source-pick call before the answer, judged

Criterion `CHAINWHEN-criterion.md`, sha256 `adba95cb20f0…` (verified with `shasum -a 256` before generation, unchanged). Public pack self-tests only (the 150 RELGATE contexts, cut 7 + X2b engine prompts); no blind/ or veil/ reads; 0 paid calls; 0 web.
Generation: Qwen3-4B-Instruct-2507 Q4_K_M, llama-server b11010 CPU on the mini (:8191, flags = prompt3m/serve.sh), prompt D4 exactly as PACKREAD, app sampler 0.7/40/0.95/0.05, seed 42, max_tokens 1024. 236 generations (150 OFF + 86 ON), 0 empty, 0 truncated, p50 28 s, 21:59 → 23:52; server stopped after the run.
Judge: Haiku 5.5-low (judge.v1-low), N = 4 shards, both orders, uncapped, refs = bench/selftest/<pack> via the new slice `boar-eval/bench/slices/chainwhen-v1` (150 ids). 472 calls, 472 ok (300 OFF + 172 ON).

## TL;DR

| readout | n | Q OFF | Q ON | Δ ON − OFF (paired 95 % CI) |
|---|---|---|---|---|
| **triggered (decision set)** | 86 | 0.566 | 0.585 | **+0.019 (−0.006 … +0.044)** |
| pick > 1 (source moved to [1]) | 68 | 0.594 | 0.619 | +0.026 (−0.000 … +0.050) |
| · fact elsewhere (G3 helped place it) | 34 | 0.645 | 0.681 | +0.036 (−0.003 … +0.078) |
| · no fact in context | 27 | 0.516 | 0.533 | +0.017 (−0.018 … +0.054) |
| · fact already at [1] (harm check) | 7 | 0.642 | 0.652 | +0.009 (−0.086 … +0.104) |
| pick = 0 ("may not contain the answer" note) | 18 | 0.464 | 0.456 | −0.008 (−0.063 … +0.047) |
| overall (all 150; ON = OFF on untriggered) | 150 | 0.608 | 0.619 | +0.011 (−0.003 … +0.025) |

**Verdict (frozen rule): NO.** Δ +0.019 misses the +0.02 bar by 0.001 and the paired CI low (−0.006) is not > 0. The no-harm clauses hold (untriggered identical by construction; pick>1 ∧ fact@1 Δ +0.009 ≥ −0.05, n 7).
Reading: the pick>1 reorder points in the right direction (+0.026, and +0.036 where the fact really sat further back), but the effect is within noise at this n. The pick = 0 note does nothing useful (Δ −0.008; mean correctness 2.22 → 2.03). The chain step does not pay on self-tests at this n. This does not test V-para-style casual questions.

## Trigger counts (150 items)
| branch | n | contexts by gold state |
|---|---|---|
| pick > 1 (ON ≠ OFF) | 68 | fact elsewhere 34 · no fact 27 · fact@1 7 |
| pick = 0 (ON ≠ OFF) | 18 | no fact 13 · fact elsewhere 3 · fact@1 2 |
| pick = 1 (ON = OFF) | 20 | fact@1 10 · fact elsewhere 7 · no fact 3 |
| skipped: health pack | 36 | — |
| skipped: n_src ≤ 2 | 8 | — |

Trigger rate 86/150 = 0.57; G3 is eligible to run on 106/150 (all non-skipped items).
Of the 68 pick>1 items, the picked source holds a gold quote in 31: Δ +0.027 (−0.015 … +0.072).
Per pack (triggered only): ethereum +0.060 (+0.006 … +0.119, n 16), outdoors +0.034 (n 9), factbook +0.028 (n 13), travel +0.014 (n 16), bitcoin −0.002 (n 18), simplewiki −0.011 (n 14). None is pre-registered, so read them as descriptive only.

## Phone cost
These figures come from the RELGATE extrapolation and were not measured here. The G3 turn costs +0.57 s per item when prefix-KV reuse works on device, and about +18 s when it does not (KVFIX not in the build). G3 must run on every eligible item to learn the pick, so 106/150 items pay. That is a mean of +0.40 s per question with KV reuse and +12.7 s without it.

## Renumbering (pick > 1)
The sources are in the system message (the "Context:" block), not the user turn. They are split with the regex from relgate/tools/build_sets.py `split_context`, with an exact round-trip assert on every item. The picked source moves to [1] and the others keep their order and are renumbered. Two examples (source headers only; bodies byte-identical):
- st-boar-factbook-001, pick 3. Before: [1] Wikivoyage: Kyrgyzstan | [2] Wikivoyage: Kyrgyzstan | [3] Kyrgyzstan (Key facts) | [4] Kyrgyzstan (Geography). After: [1] Kyrgyzstan (Key facts) | [2] Wikivoyage: Kyrgyzstan | [3] Wikivoyage: Kyrgyzstan | [4] Kyrgyzstan (Geography).
- st-boar-factbook-002, pick 3. Before: [1] Wikivoyage: Malta Island | [2] Wikivoyage: Malta Island | [3] Malta (Key facts) | [4] Malta (Background). After: [1] Malta (Key facts) | [2] Wikivoyage: Malta Island | [3] Wikivoyage: Malta Island | [4] Malta (Background).

## Checks
- All 150 relgate prompts are byte-identical to the headpass-st gen-x2b source prompts. The OFF prompts are byte-identical to the PACKREAD M4-D4 prompts on the 54 shared ids.
- The G3 pick is the argmax over digits 0..n_src from relgate/runs/m4.jsonl. It agrees with exploratory-g3rows.json on 150/150.
- There were 0 empty answers, 0 length stops and 0 generation errors.

## Caveats
- One seed and a Haiku L1 judge. The decision Δ sits on the bar, so a rerun could land on either side. An Opus confirmation was not triggered because the verdict is NO.
- The OFF answers are not text-identical to the PACKREAD M4-D4 answers (0/54), even though the prompts, seed and server flags match. llama-server sampling under cache_prompt is not reproducible across sessions. ON and OFF were generated in the same session, interleaved per item.
- Gold labels (quote presence) understate positives (see the RELGATE audit), so the state splits are approximate.
- The pick = 0 subset is small (n 18) and most of it is no-fact items. Its CI is wide.
- Self-test questions are pack-matched and specific. V-para-style casual questions were not tested.

## Deviations
1. The brief says to renumber the sources "in the user turn". In the X2b engine prompt they live in the system message, so renumbering was applied there. This does not conflict with the criterion, which does not say where the sources sit. The pick = 0 note was appended to the user turn as the criterion says (one newline after the style reminder).
2. The bench slice `boar-eval/bench/slices/chainwhen-v1` (150 ids, refs copied verbatim from bench/selftest/<pack>) was created for the judge. It was committed to the local boar-eval repo (fb253f7) and not pushed.
3. A 1-id judge probe (2 Haiku calls) was run on partial traces to check auth before the full pass. It went to /tmp and is not part of the data.

## Files
- `tools/build.py` (prompts, plan, slice), `tools/prompts_lib.py` (copy of kiln/prompt3m), `tools/gen.py` + `tools/run_mini.sh` (mini), `tools/to_traces.py`, `tools/agg.py`
- `data/prompts.jsonl`, `data/plan.json` (per-item branch/pick/state), `data/ids-150.ids`, `data/ids-on.ids`, `data/renumber-examples.json`
- `answers/answers-M4.jsonl`, `answers/gen-M4.log`; `traces/chainwhen-{OFF,ON}.traces.jsonl`; `judgments/chainwhen-{OFF,ON}.judgments.jsonl` (+ shards, logs); `aggregates/chainwhen.json`
