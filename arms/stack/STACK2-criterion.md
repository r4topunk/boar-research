# STACK-2: the quality number for the surviving pack stack (keep rule X3 + quota) under "all packs installed" — a measurement after STACK's step-0 FAIL on the chunk bar (frozen 2026-10-13 16:3x, coordinator)

## Tags
Tags: none

## Question
STACK step 0 (GATE.md, criterion sha 56ed7ccf…): under all 9 packs + kit, X = packGround "perpack" + packRoute "quota" raises fact article kept **46 → 72** (bar 56; S single-pack 68) and fact chunk kept **31 → 36** (bar 39: FAIL by 3), removes P's lost kit contexts (1 + 3 → 0 + 0), gold kept not lower, p50 ×0.98. The chunk bar assumed the two settings add on chunks; they conflict on simplewiki/factbook items (the own pack needs > 2 slots under the quota), and the keep rule alone also lands at 36. Verdict by the letter: FAIL at step 0 — stands. This criterion is a **measurement**: the product note for the many-packs setup needs the quality Δ with a CI, and it is measurable at 0 paid calls (RULE 24). Arm **X** as prepared (tree runner-local/be-0cfd4a77-cut7-stack, patch stack.vs-cut7.patch sha 0049d3c3…, requests runs/st-<pack>-cut7-stack-s42.requests.jsonl), control **P** = CROWDQ's peers run, reference **S** = single pack.

## Fixed inputs
As STACK §Fixed inputs (same tree, requests, judge, bench dirs); v0.1 public 60 OFF/ON on the stack tree for the quality no-harm.

## Power
expected_delta: +0.02 raw X − P on the 180 (source: STACK step 0 — article kept +26 (SE 14 → 32, topic 32 → 40), chunk kept +5; ST2's conversion +18 chunks/+32 articles → +0.017; CROWDQ's crowding cost −0.016 is the most the quota can give back)
n: 180
seeds: 1 (deterministic)
mde: ≈ 0.03 raw paired at n 180
slice: n/a
l1_futility: n/a
reopen: STACK FAIL at step 0 on the chunk bar (36 vs 39) with the article bar passed by +16 and kit harm removed — the step-0 reach gate was mis-specified for two settings that conflict on chunks; the quality measurement itself was never run (R49 if this closes)
split: paired Δ by pack family (SE vs topic), declared; expected gain in SE (article kept 14 → 32)
NOTE: expected_delta < mde → the likely outcome is "not decided at MDE 0.03"; the deliverable is the Δ with its CI for the product note, plus the v0.1 no-harm number. No further stack arms on the 180 after this.

## Stages and rules
1a. Generation X on the 180 (MacBook, nohup, resumable); smoke; precheck ≥ 20 % changed vs P (step 0 says 160/180); Haiku 5.5-low N=4 both orders (360); paired Δ X − P pooled / SE / topic / per pack, X − S; same_answer field; URL-match reach from the traces (expect article kept ≈ 41 × 72/46 ≈ 64 ± 6).
1b. v0.1 public 60 OFF/ON on the stack tree (kit only), Haiku N=4 both orders (240); rule: CI high of (ON − OFF) ≥ −0.03 → no harm.
2. Verdict: LEVER (CI low > 0, Δ ≥ +0.03) → recommended default for many-packs installs + re-score the cards; SMALL (CI low > 0, Δ < 0.03) → optional setting, product note; NO / not decided → pack stack closed with the numbers; near-miss (Δ ≥ +0.015 with CI through 0) → Opus N=4 on X and P (720) for the report's number. A v0.1 harm (CI high < −0.03) overrides any positive verdict.

## Stop rules and budget
0 paid API. MacBook only. Never two 4B generation jobs at once. Disk ≥ 8 GiB. Haiku 600 (+ 720 Opus on a near-miss).

## Outputs and exposure
arms/stack/{STACK.md, aggregates/stack.json, runs/}; public items only (no new blind exposure). QUEUE rows per stage.
