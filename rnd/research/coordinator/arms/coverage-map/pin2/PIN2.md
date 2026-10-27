# PIN2: rescue the named article from the compressor's relative floor only, at its own rank, within the budget (0 LLM, MacBook replays, 2026-10-23)
Criterion ../PIN2-criterion.md sha256 `d026c9bbba68c209f56860c20a0acdb5d28d62182c0e1181903cddeeba7508c4` (frozen before any replay, not edited). 0 LLM, 0 judge, 0 Opus, 0 paid, 0 phone.
Patch ../../retrieve-sweep/patches/PIN2.patch sha256 `d6c0533c511e0a432919e4dd4c2ecd572b1e6ed7e1ca96e1deb8fabadf2790b7` (diff -ruN rs-SEFIX/src rs-PIN2/src; `patch -p1 --dry-run` clean on rs-SEFIX). Tree kiln-local/rs-PIN2 = cp -Rc rs-SEFIX + patch, one default-off switch RS_PIN2.

**TL;DR. NO by the frozen gate, on the context clause only.** PIN2 does what KEEPPIN's PIN did on the targets (Kyoto back on b15: 2 of 4 MISSES; MAIN 43 = +1, cooking-004) with none of its collateral: 0 reorders, 0 kept chunks lost anywhere, 1 other topic with a changed set (b18 +1 Cheetah chunk), 0 health losses, 0 evictions. It fails on context: the 27-topic p50 is 1.111x (b15 187 -> 431 and b18 127 -> 169 both cross the median; total tokens +3.3 %), and the frozen "no item above its work budget" check, measured on keptFull, flags 54 MAIN items (53 already over in base, because keptFull includes the head-pass appends outside compressContext; 1 new: vit-hum-002 631 -> 768 vs 700). The compressor itself never exceeds its budget (0 items, both sets).

## What PIN2 changes vs KEEPPIN PIN
- Rescue only chunks whose title the question names (KEEPPIN's titleNamedBy) AND that are under the 0.5 relative floor; chunks above the floor are untouched.
- No placement first: rescued sentences compete at their own score; kept order keeps the existing sort, so rescued chunks sit at their own rank (last in every fired item).
- Budget cap: a rescued chunk that got no sentence may evict the lowest-ranked non-pinned chunks to fit title + opening (+ best); never fired (evicted 0, both sets). Rescued chunks are exempt from onSubject in the non-health keep step (fired once: b15); health-strict untouched.

## Commands
```
cd <workspace>/rnd/research/coordinator/arms/coverage-map/pin2
tools/run_t27.sh off; tools/run_t27.sh PIN2 RS_PIN2=1
tools/run_main.sh off; tools/run_main.sh PIN2 RS_PIN2=1
python3 -I tools/score.py pin2.json
```
Recipes = keeppin/tools (MAIN: sefix/tools/run_main.sh recipe, SEFIX-124 env; 27: topics27/misses/run.sh recipe). Base = sefix/replays/main.F1F2F4.jsonl and topics27/replay/misses.A1.jsonl. Wall: MAIN 150-160 s per arm, 27 topics 4-6 s.
**Identity (switch off): MAIN 97/97 and 27/27 on raw ids, kept ids and reason codes.**

## Table
| metric | base SEFIX-124 | PIN2 | gate |
|---|---|---|---|
| MAIN chunk-level /92 (cm, v0.1) | 42 (14, 28) | 43 (15, 28); gained cooking-004, lost none | >= 44 (or MISSES) |
| MISSES recovered /4 | 1 (b13) | **2** (b13, b15 Kyoto x2 chunks) | >= 2: PASS |
| other 23 topics, kept SET changed | - | **1** (b18 +Cheetah 22516) | <= 2: PASS |
| other 23 topics, pure reorders / body-only | - | 0 / 0 | reported |
| MAIN kept SET changed / reorders / body-only | - | 5 / 0 / 0 (all additions, 0 losses) | reported |
| health losses (MAIN 11 items, 27: 7) | - | 0 / 0 | 0: PASS |
| ctx p50 MAIN | 653 | 657 (1.006x); max item 1.314x trv-004 | <= 1.10: PASS |
| ctx p50 27 topics | 324 | 360 (**1.111x**); max item 2.305x b15 | <= 1.10: **FAIL** |
| items above budget (keptFull) MAIN / 27 | (53 / 0 by the same measure) | **54** / 0 | 0: **FAIL** |
| compressor tokensAfter above budget | 0 / 0 | 0 / 0 | (diagnostic) |
| total ctx tokens MAIN / 27 | 56,812 / 8,701 | 57,333 (+0.9 %) / 8,987 (+3.3 %) | (diagnostic) |
| **verdict** | | **NO** (context clause) | |

## Per-item changes (all additions, nothing lost)
- 27: b15 +Kyoto 19425 + 19426 (187 -> 431 tokens, keep-step exemption fired); b18 +Cheetah 22516 (127 -> 169).
- MAIN: vit-hum-002 +Mozi (631 -> 768, budget 700); vit-cry-008 +ethereum.org: Glamsterdam (620 -> 702, budget 450 for the compressor, the excess is head-pass appends present in base too); lan-exp-005 +Sahara (481 -> 547); trv-004 +Lisbon Airport x2 (717 -> 942); cooking-004 +Appropedia: Tallow + the cooking Q&A 12990 (778 -> 789; the fact gained).

## Reading (post hoc, not the verdict)
- PIN2 isolates the effect: KEEPPIN's 5 "changes" on b5 b9 b11 b14 b17 were the pins-first ordering; with rank order kept they vanish. The set changes are the same as PIN's (b15, b18).
- The 27-topic p50 failure is the same 1.111x as KEEPPIN and is a median-rank artefact of 2 of 27 items crossing the middle (324 -> 360 are adjacent order statistics); KEEPPIN's context failure was therefore not caused by the ordering. The real cost is b15's two Kyoto chunks (+244 tokens) on one item.
- The "no item above its work budget" clause was written on keptFull, which also counts the head-pass / dense appends (their own budget, outside compressContext); base already fails it on 53/97. As written it cannot be passed by any arm on this recipe. The compressor budget is respected by construction.
- Any re-gate (e.g. total tokens or compressor tokensAfter instead of p50 and keptFull) needs a new criterion frozen before reuse and an independent ruling that it is not tuned to this result; not done here.

## Next
NO, so no Haiku screen. If the coordinator re-gates under a new criterion and PIN2 passes, the answer screen would be: Haiku 5.5-low, judge.v1 N 4 both orders, divergence-first on the 7 changed items only (27: b15 b18 Detailed s42 + s43; MAIN: vit-hum-002 vit-cry-008 lan-exp-005 trv-004 st-qa-cooking-se-004) vs the SEFIX-124 rows, cache by (id, sha256 text); rule changed-item dU >= +0.02 with CI low > -0.01 and CE-unwarned not up. Not run.

## Caveats
Dev items, bench engine (not the native Kotlin pipeline), lexical detector, deterministic replay (item counts). "Recovered" = expected title kept, not answer quality. b19 (instant table) and b20 (bm25 pool) are out of reach for any pin.
Files: PIN2.md, pin2.json, tools/{run_main.sh,run_t27.sh,score.py}, replays/ (gitignored).
