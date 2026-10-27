# X2B-OFF-MAIN criterion addendum 1 (frozen 2026-10-21, before any Opus call or seed-43 generation)

Base: X2B-OFF-MAIN-criterion.md (sha256 0415e6eb..., commit 1c315378); seed-42 result in X2B-OFF-MAIN.md (CEu 7 -> 10, rule 3 "X2b stays on" by one item).
Purpose (coordinator, 2026-10-21): settle the borderline CE clause with (1) an Opus re-label of the CEu-flip items and (2) a second seed.
Decision rule unchanged: "safe for kit-only installs" iff pooled dU >= -0.02 AND CI low >= -0.05 AND pooled CEu(OFF) - CEu(ON) <= 2; "better" iff additionally dU > 0 with CI low > 0; otherwise X2b stays on.

## Step 1: Opus on the 9 seed-42 CEu-flip items
Items (CEu label differs ON vs OFF at seed 42, Haiku): lan-rsn-001, lan-cmp-002, lan-cmp-004, st-qa-cooking-se-016, st-qa-money-se-007, st-qa-money-se-009 (CEu new under OFF); vit-cry-006, vit-cry-007, lan-cmp-005 (CEu gone under OFF).
Judge: Opus (judge.mjs default opus, judge.v1), N = 4 shards, both orders (deepthink/tools/shard_judge.sh ... opus), on the OFF s42 traces (18 calls).
ON side: reuse Opus rows on byte-identical ON text where they exist. None exist (the MAIN Opus passes, MIN3CITE-OPUS and GEMMA-OPUS-MAIN, are K0; 0 Opus rows carry the lpctl-K1-main-s42 traces sha 847313ee...), so ON is judged too on the lpctl-K1-main-s42 traces (18 calls). **Deviation from the 18-call request, declared here: Opus cap 36.**
Recompute: CEu(seed 42) with Opus labels (corr from Opus, labels.py otherwise) on these 9 items for both arms and Haiku labels on the other 68; U_d and dU reported both ways (Haiku-only and Opus-on-9 mix). Step 1 alone does not decide; it feeds the pooled CE clause only through its seed-42 half (see Pooling).

## Step 2: seed 43, ON and OFF, same 77 ids
No K1 seed-43 MAIN control exists (divergence-map conditions: q17-K0-s43 only; null-s43 K1 covers screen2 only), so both are generated fresh on the mini:
- ON43 = null-cal/null-s43.patch (sha256 428d9f36..., sampler seed 43), run name x2bon43.
- OFF43 = x2b-off-s43.patch = x2b-off.patch + null-s43.patch concatenated (sha256 3f53aebf836055461dc1991456352f5d14c4e0f328a96e758df0986339aa81ac), run name x2boff43.
Run (cwd arms): OUT_BASE=$PWD/x2b-retest/main GEN_ONLY=1 bash x2b-retest/tools/run_pool_x2b.sh <x2bon43|x2boff43> K1 x2b-retest/main-live77.ids x2b-retest/<null-s43 patch|x2b-off-s43.patch>.
Judge: Haiku 5.5-low judge.v1-low N 4 both orders, via the same runner with JUDGE_ALLOW lists from tools/judge43_plan.py. Judgment reuse = byte-identical (itemId, answer text) from any of: ON s42 control (null-cal/control/pool-K1.json), OFF s42 (main/x2boffmain aggregate), null-s43 K1 (null-cal/arms/null-s43 aggregate), and ON43/OFF43 of each other (identical text judged once). **Cap 160 Haiku calls.** If more are needed: items in main-live77.ids order, each item's ON43 and OFF43 together, until the cap; unjudged items leave the seed-43 paired stats and are listed.

## Pooling (decides)
Two-seed pooled over item-seed pairs: dU = U_d(OFF, both seeds) - U_d(ON, both seeds), with sums over the 2 x 77 item-seed rows (ratio of sums). CI: item bootstrap (resample the 77 ids, keep both seeds of each id together), B 2000 seed 11, 95 % percentile.
CEu pooled = CEu(OFF s42) + CEu(OFF s43) - CEu(ON s42) - CEu(ON s43), labels Haiku except the 9 step-1 items at seed 42 (Opus labels on both arms). The clause "+<= 2 pooled" is read on this two-seed sum as written by the coordinator. Also reported: the Haiku-only pooled CEu and per-seed numbers.
Also reported: prompt tokens and retrieval wall per seed, R per seed.

## Sanity
77/77 rows and 0 errors per new run; OFF43 0 headpass:add codes; ON43 >= 1 headpass:add code; ON43 text differs from ON s42 on most live items (a seed-43 run identical to s42 would mean the patch did not apply -> invalid).

## Budget
calls_cap: Haiku 160 / Opus 36
opus_clause: step 1 only, 9 items, both arms, dev set (MAIN 97, ruler dev).
