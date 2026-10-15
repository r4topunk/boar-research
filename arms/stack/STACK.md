# STACK-2: quality of the pack stack (keep rule X3 + quota 2/6), all 9 packs + kit, 180 public self-test items: **not decided at MDE 0.03**. v0.1 shows no harm (2026-10-13 17:1x)

Criteria: STACK sha 56ed7ccf… (step 0 **FAIL** on the chunk bar, stands; GATE.md) → STACK-2 measurement sha e875d463… (frozen, unedited). Cut 7 + stack.vs-cut7.patch (sha 0049d3c3…) on runner-local/be-0cfd4a77-cut7-stack, 4B claim build, seed 42, deterministic. X = {packGround: "perpack", packRoute: "quota"}; P = CROWDQ's all-9 peers run (same cut 7, settings absent); S = single pack. 0 paid calls, 0 Opus. **Haiku 5.5-low: 588 calls**: 360 on the 180 and 228 on v0.1 (2 × 57 × 2). N = 4 shards per run, every shard exited 0, no reruns, all fail-closed checks and floor_metrics --strict passed.

## TL;DR
- **Pooled Δ X − P raw +0.005 (−0.009…+0.021)**; above_min +0.007 (−0.011…+0.026). Items better/worse/same 73/63/44. P 0.476 → X 0.481 (S 0.493). Win-rate 0/180 in both.
- **SE (declared split) +0.018 (−0.000…+0.038)**, above_min +0.022 (−0.001…+0.047). **Topic −0.010 (−0.032…+0.011)**. The gain sits where step 0 put it (SE article kept 14 → 32), but its CI touches 0.
- **X − S pooled −0.011 (−0.027…+0.005)**: X recovers about a third of CROWDQ's crowding cost (P − S −0.016). SE X − S −0.015, topic −0.007.
- **Verdict (STACK-2 §2): not decided at MDE 0.03.** CI low ≤ 0, so neither LEVER nor SMALL. Δ +0.005 < 0.015, so not a near-miss and no Opus pass. The pack stack closes with these numbers (R49). Product note: X is safe to offer as an option for many-pack installs. It mainly helps SE-style packs and does not reach single-pack quality. It is not a recommended default.
- **v0.1 no-harm (kit only, 57 judged): ON − OFF raw −0.009 (−0.027…+0.007)**, above_min −0.011 (−0.033…+0.011). CI high ≥ −0.03 → **no harm**. OFF 0.529, ON 0.520; kept lists changed on 14/60.

## Step-0 gate (replay, wt/groundst; from GATE.md)
| gate | rule | P → X | verdict |
|---|---|---|---|
| G1 fact article kept | ≥ 56 | 46 → 72 | pass |
| G1 fact chunk kept | ≥ 39 | 31 → 36 | FAIL |
| G2 lost kit context v0.1 / v0.2 | X adds none | 1 → 0 / 3 → 0 | pass |
| G2 gold kept v0.1 / v0.2 resolvable | ≥ 12 / ≥ 3 | 22 / 3 (kit-only X 12 / 5) | pass |
| G3 retrieval + keep p50 | ≤ 1.3 × P | ×0.98 | pass |

## Reach, precheck and determinism (generation traces, URL match as crowdq reach.py)
- Fact article kept: S 59 → **P 41 → X 58** (forecast 64 ± 6: low edge of the band). SE 29 → 24 → 36; topic 30 → 17 → 22.
- Own-pack kept slots P 118 → X 143. Kept slots P 282 → X 452. Empty kept P 54 → X 25. `packground:kept-*` codes on 114/180 items. 11 installed packs on 180/180 traces; 0 errors.
- Kept shares under X (all 452 kept slots): simplewiki 27 % (CROWDQ P 36 %), wikivoyage kit 18 %, qa-travel-se 14 %, qa-ethereum-se 11 %. Foreign slots: simplewiki 66 → 91, wikivoyage 42 → 79. The added slots are mostly foreign: X fills the context rather than targeting the item's own pack.
- Precheck: 125/180 (69 %) items changed vs P (kept title/section list or promptTokens); ≥ 20 %, passed before judging.
- same_answer X vs P: kept_unchanged_prompt_same 55/55 (all items same 55/180). v0.1 ON vs OFF: 46/46 and 46/60.
- v0.1 OFF identity vs the kit-only replay with the traces' gate decisions: 53/60. The 7 others are tree differences, not stack effects: 6 are cut 7 FACTS r6 answers that skip retrieval (the dt512 replay tree has no FACTS), and dng-002 is the mmbert health-strict path. ON matches 52/60 (the same 7 + lan-ref-001, also a FACTS item).

## Per pack (Haiku raw P → X, Δ X − P (CI), better/worse/same, X − S; fact article kept S/P/X; own kept P → X)
| pack | P | X | Δ X − P | b/w/s | X − S | fact S/P/X | own kept |
|---|---|---|---|---|---|---|---|
| qa-travel-se | 0.439 | 0.457 | +0.018 (−0.035…+0.080) | 10/5/5 | +0.034 | 6/5/12 | 11→21 |
| qa-ethereum-se | 0.454 | 0.480 | +0.026 (−0.024…+0.081) | 8/8/4 | −0.036 | 7/7/9 | 26→26 |
| qa-bitcoin-se | 0.428 | 0.437 | +0.009 (−0.017…+0.031) | 7/3/10 | −0.032 | 2/2/3 | 15→23 |
| qa-health-se | 0.501 | 0.511 | +0.010 (−0.015…+0.038) | 7/8/5 | −0.014 | 5/4/6 | 7→12 |
| qa-outdoors-se | 0.463 | 0.489 | +0.026 (−0.013…+0.068) | 9/6/5 | −0.029 | 9/6/6 | 13→14 |
| boar-firstaid-en | 0.465 | 0.456 | −0.009 (−0.035…+0.017) | 9/7/4 | −0.016 | 2/1/2 | 5→6 |
| boar-medlineplus-en | 0.517 | 0.526 | +0.010 (−0.025…+0.045) | 10/8/2 | +0.018 | 11/3/6 | 4→8 |
| boar-factbook | 0.454 | 0.421 | −0.033 (−0.091…+0.021) | 7/10/3 | −0.017 | 5/1/1 | 1→2 |
| boar-simplewiki-en | 0.561 | 0.551 | −0.010 (−0.052…+0.038) | 6/8/6 | −0.015 | 12/12/13 | 36→31 |

## Caveats
1. Dev data with public, agent-written gold. Haiku is the L1 judge and compresses gaps, so these are not claim numbers. One deterministic seed: same_answer 55/55 where kept lists and prompts are unchanged.
2. The P and S Haiku rows were judged in earlier sessions with the same judge model, settings and bench bytes; only the system label differs.
3. Per-pack CIs at n = 20 are wide. Factbook's −0.033 matches step 0: under the quota its own pack loses slots.
4. The v0.1 run skips the 3 venue-list items (food-001/002/006), which judge.mjs never grades: 57 judged.
5. Disk dipped to 7.1 GiB at 16:32 for reasons outside this arm (the runner guard stopped simplewiki; resumed at 8.0 GiB after deleting my scratch trees). No data was lost. No new blind exposure in STACK-2.

Files: tools/{mkreq.py, run_stack.sh, chain.sh, judge_stack.sh, stack_agg.py}; runs/st-<pack>-cut7-stack-s42.* and v01-cut7-stack-{off,on}-s42.* (requests, traces, judgments, ids, shards, logs), runs/v01-kit.tasksfrom-{off,on}.jsonl, chain.log, judge.log; aggregates/{stack.json, *.floor_metrics.txt}.
